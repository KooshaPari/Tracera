# Performance Indexes Quick Reference

Fast lookup guide for developers working with Trace database queries.

## Quick Stats

- **Migration**: `045_add_performance_indexes.py`
- **Indexes created**: 23 total
- **Expected improvement**: 80-95% faster queries
- **Storage overhead**: ~5-8 MB
- **Lock time**: None (concurrent creation)

## Index Listing by Table

### Links Table (8 indexes)

```
ix_links_source_id        → source_id
ix_links_target_id        → target_id
ix_links_type             → type
ix_links_created_at       → created_at
ix_links_updated_at       → updated_at
ix_links_source_target    → (source_id, target_id)
ix_links_source_type      → (source_id, type)
ix_links_type_created     → (type, created_at)
```

### Items Table (14 indexes)

```
ix_items_project_id             → project_id
ix_items_parent_id              → parent_id (excludes NULL)
ix_items_status                 → status
ix_items_owner                  → owner
ix_items_type                   → type
ix_items_priority               → priority
ix_items_created_at             → created_at
ix_items_updated_at             → updated_at
ix_items_project_status         → (project_id, status)
ix_items_project_owner          → (project_id, owner)
ix_items_project_updated        → (project_id, updated_at)
ix_items_parent_status          → (parent_id, status)
ix_items_project_status_priority → (project_id, status, priority)
ix_items_search                 → Full-text search (GIN)
```

### Change Log Table (1 index)

```
ix_change_log_record_table → (record_id, table_name)
```

## Which Index Will My Query Use?

### Links Queries

| Query | Indexes Used |
|-------|--------------|
| `WHERE source_id = ?` | `ix_links_source_id` |
| `WHERE target_id = ?` | `ix_links_target_id` |
| `WHERE source_id = ? AND target_id = ?` | `ix_links_source_target` |
| `WHERE source_id = ? AND type = ?` | `ix_links_source_type` |
| `WHERE type = ?` | `ix_links_type` |
| `WHERE created_at > ?` | `ix_links_created_at` |
| `WHERE type = ? ORDER BY created_at` | `ix_links_type_created` |

### Items Queries

| Query | Indexes Used |
|-------|--------------|
| `WHERE project_id = ?` | `ix_items_project_id` |
| `WHERE parent_id = ?` | `ix_items_parent_id` |
| `WHERE status = ?` | `ix_items_status` |
| `WHERE owner = ?` | `ix_items_owner` |
| `WHERE project_id = ? AND status = ?` | `ix_items_project_status` |
| `WHERE project_id = ? AND owner = ?` | `ix_items_project_owner` |
| `WHERE parent_id = ? AND status = ?` | `ix_items_parent_status` |
| `WHERE project_id = ? AND status = ? ORDER BY priority` | `ix_items_project_status_priority` |
| `WHERE project_id = ? ORDER BY updated_at` | `ix_items_project_updated` |
| `WHERE updated_at > ?` | `ix_items_updated_at` |

### Full-Text Search

```sql
WHERE to_tsvector('english', name || ' ' || description) @@ plainto_tsquery(?)
-- Uses: ix_items_search (GIN)
```

## Verify Index Usage

```bash
# Connect to database
psql -d trace_db

# Check if indexes exist
\di items
\di links

# See which indexes are actually being used
SELECT * FROM pg_stat_user_indexes WHERE tablename IN ('items', 'links');
```

## Common Mistakes to Avoid

### ❌ Bad: Query predicate order doesn't match index

```sql
-- Index: (project_id, status, priority)
-- This won't use the full composite index:
SELECT * FROM items WHERE status = ? AND project_id = ? ORDER BY priority;

-- ✓ Better: Match column order in WHERE clause
SELECT * FROM items WHERE project_id = ? AND status = ? ORDER BY priority;
```

### ❌ Bad: Using functions on indexed columns

```sql
-- Won't use index:
SELECT * FROM items WHERE LOWER(name) = 'test';

-- ✓ Better: Store lowercase in DB or use FTS index
SELECT * FROM items WHERE name = 'test';
```

### ❌ Bad: Searching with LIKE wildcards

```sql
-- Won't use index efficiently:
SELECT * FROM items WHERE name LIKE '%search%';

-- ✓ Better: Use full-text search
SELECT * FROM items WHERE to_tsvector('english', name) @@ plainto_tsquery('search');
```

### ❌ Bad: OR conditions between different columns

```sql
-- May not use indexes efficiently:
SELECT * FROM items WHERE project_id = ? OR owner = ?;

-- ✓ Better: Use UNION or filter by project first
SELECT * FROM items WHERE project_id = ?
UNION
SELECT * FROM items WHERE owner = ? AND project_id NOT IN (?);
```

## Performance Checklist

When optimizing a slow query:

- [ ] Run `EXPLAIN ANALYZE` to see the query plan
- [ ] Check if indexes are being used (look for "Index Scan")
- [ ] If "Seq Scan" appears, check if there's a matching index
- [ ] Verify column order matches composite index definition
- [ ] Run `ANALYZE items;` to update statistics
- [ ] Check for index bloat: `SELECT idx_scan FROM pg_stat_user_indexes WHERE indexname = '...'`
- [ ] Use `LIMIT` when possible to avoid full result set processing

## Common Performance Queries

### Get items in project

```sql
SELECT * FROM items WHERE project_id = $1
ORDER BY updated_at DESC LIMIT 50;
-- Uses: ix_items_project_updated
```

### Dashboard: active items by priority

```sql
SELECT * FROM items
WHERE project_id = $1 AND status = 'active'
ORDER BY priority DESC;
-- Uses: ix_items_project_status_priority
```

### Item tree with hierarchy

```sql
WITH RECURSIVE tree AS (
  SELECT * FROM items WHERE id = $1
  UNION ALL
  SELECT i.* FROM items i
  JOIN tree t ON i.parent_id = t.id
)
SELECT * FROM tree;
-- Uses: ix_items_parent_id at each recursion level
```

### Find related items

```sql
SELECT target.* FROM items source
JOIN links ON source.id = links.source_id
JOIN items target ON links.target_id = target.id
WHERE source.project_id = $1;
-- Uses: ix_links_source_id, ix_links_target_id
```

## Testing Query Performance

### Before optimization

```sql
EXPLAIN ANALYZE SELECT * FROM items WHERE project_id = $1 AND status = $2;
```

Expected slow plan:
```
Seq Scan on items  (cost=0.00..1000.00 rows=100)
  Filter: (project_id = $1 AND status = $2)
```

### After index applied

```sql
ANALYZE items;  -- Update statistics
EXPLAIN ANALYZE SELECT * FROM items WHERE project_id = $1 AND status = $2;
```

Expected fast plan:
```
Index Scan using ix_items_project_status on items
  (cost=0.29..2.15 rows=100)
  Index Cond: (project_id = $1 AND status = $2)
```

## Troubleshooting

### Index not being used?

1. **Check statistics**: `ANALYZE items;`
2. **Verify index exists**: `\di items` in psql
3. **Check column order**: Composite indexes require specific column order
4. **Check data types**: Make sure query uses exact type (UUID vs string)

### Query still slow?

1. **Increase sample size**: `SET WORK_MEM TO '512MB'` (for large sorts)
2. **Check table bloat**: Many deleted rows? Run `VACUUM`
3. **Check multiple queries**: Index one issue at a time
4. **Profile with `pg_stat_statements`**: See which queries are slowest

### High CPU usage with indexes?

- Too many indexes = slower writes
- Drop unused indexes: `SELECT idx_scan FROM pg_stat_user_indexes`
- Balance read vs. write performance

## Performance Goals

✓ Single-item lookup: **< 5ms**
✓ Small filter (< 1000 items): **< 20ms**
✓ Large filter (< 10000 items): **< 100ms**
✓ Full-text search: **< 50ms**
✓ Recursive hierarchy (< 50 levels): **< 100ms**

## Migration Info

```bash
# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1

# Check status
alembic current
```

## Related Documentation

- Full guide: `/docs/PERFORMANCE_INDEXES_GUIDE.md`
- Test suite: `/tests/test_performance_indexes.sql`
- Migration: `/alembic/versions/045_add_performance_indexes.py`
