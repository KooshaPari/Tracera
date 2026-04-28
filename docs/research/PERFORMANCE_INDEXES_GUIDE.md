# Performance Indexes Guide

Migration: `045_add_performance_indexes.py`

## Overview

This migration adds 23 performance indexes across critical tables to optimize query patterns identified in the Trace application:

- **Links table**: Graph traversal and relationship queries
- **Items table**: Filtering, sorting, and full-text search
- **Change log**: Audit trail and tracking queries

## Index Strategy

### 1. Single-Column Indexes (Base Indexes)

Used for direct lookups and equality filters:

#### Links Table
| Index | Column | Purpose |
|-------|--------|---------|
| `ix_links_source_id` | `source_id` | Find all outgoing links from a node |
| `ix_links_target_id` | `target_id` | Find all incoming links to a node |
| `ix_links_type` | `type` | Filter links by relationship type |
| `ix_links_created_at` | `created_at` | Timeline-based queries |
| `ix_links_updated_at` | `updated_at` | Recent changes queries |

#### Items Table
| Index | Column | Purpose |
|-------|--------|---------|
| `ix_items_project_id` | `project_id` | Scope queries to project |
| `ix_items_parent_id` | `parent_id` | Hierarchy traversal (nullable optimized) |
| `ix_items_status` | `status` | Status-based filtering |
| `ix_items_owner` | `owner` | User ownership queries |
| `ix_items_type` | `type` | Item type filtering |
| `ix_items_priority` | `priority` | Priority-based sorting |
| `ix_items_created_at` | `created_at` | Time range queries |
| `ix_items_updated_at` | `updated_at` | Recent activity queries |

### 2. Composite Indexes (Covering Indexes)

Multi-column indexes for common query patterns:

#### Links Table
| Index | Columns | Purpose |
|-------|---------|---------|
| `ix_links_source_target` | `source_id, target_id` | Find specific link relationships |
| `ix_links_source_type` | `source_id, type` | Find outgoing links of type |
| `ix_links_type_created` | `type, created_at` | Timeline queries by type |

#### Items Table
| Index | Columns | Purpose |
|-------|---------|---------|
| `ix_items_project_status` | `project_id, status` | Filter items by project and status |
| `ix_items_project_owner` | `project_id, owner` | Find owner's items in project |
| `ix_items_project_updated` | `project_id, updated_at` | Recent items in project |
| `ix_items_parent_status` | `parent_id, status` | Tree traversal with status |
| `ix_items_project_status_priority` | `project_id, status, priority` | Dashboard queries |

### 3. Full-Text Search Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| `ix_items_search` | `name + description` | Full-text search (GIN) |

## Query Performance Impact

### Before Indexes

```sql
-- Find all links from a node (full table scan)
EXPLAIN ANALYZE SELECT * FROM links WHERE source_id = '123';
                           QUERY PLAN
Seq Scan on links (cost=0.00..10000.00 rows=50)
Filter: (source_id = '123')
```

### After Indexes

```sql
-- Same query with index (fast lookup)
EXPLAIN ANALYZE SELECT * FROM links WHERE source_id = '123';
                                  QUERY PLAN
Index Scan using ix_links_source_id on links (cost=0.29..2.15 rows=50)
Index Cond: (source_id = '123')
```

**Expected improvements**: 80-95% faster for indexed queries

## Common Query Patterns Optimized

### 1. Graph Traversal

```sql
-- Find neighbors of a node
SELECT * FROM links WHERE source_id = ? OR target_id = ?;
-- Uses: ix_links_source_id, ix_links_target_id

-- Find links of specific type
SELECT * FROM links WHERE source_id = ? AND type = 'depends_on';
-- Uses: ix_links_source_type
```

### 2. Item Filtering

```sql
-- Dashboard: show active items in project
SELECT * FROM items WHERE project_id = ? AND status = 'active';
-- Uses: ix_items_project_status

-- Kanban board: items by owner
SELECT * FROM items WHERE project_id = ? AND owner = ?;
-- Uses: ix_items_project_owner

-- Priority sorting
SELECT * FROM items WHERE project_id = ? AND status = ? ORDER BY priority;
-- Uses: ix_items_project_status_priority
```

### 3. Hierarchy Queries

```sql
-- Get children of an item
SELECT * FROM items WHERE parent_id = ? ORDER BY status;
-- Uses: ix_items_parent_id, ix_items_parent_status

-- Complete tree traversal (recursive)
WITH RECURSIVE tree AS (
  SELECT * FROM items WHERE id = ?
  UNION ALL
  SELECT i.* FROM items i
  JOIN tree t ON i.parent_id = t.id
)
-- Uses: ix_items_parent_id at each level
```

### 4. Search

```sql
-- Full-text search
SELECT * FROM items WHERE to_tsvector('english', name || ' ' || description)
                       @@ plainto_tsquery('english', 'search term');
-- Uses: ix_items_search (GIN index)
```

### 5. Time-Based Queries

```sql
-- Recent activity
SELECT * FROM items WHERE updated_at > now() - interval '7 days';
-- Uses: ix_items_updated_at

-- Created this month
SELECT * FROM items WHERE created_at >= date_trunc('month', now());
-- Uses: ix_items_created_at
```

## Index Maintenance

### Monitoring Index Usage

```sql
-- Check index usage statistics
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE tablename IN ('items', 'links', 'change_log')
ORDER BY idx_scan DESC;
```

### Reindexing

```sql
-- If index becomes bloated (rare)
REINDEX INDEX CONCURRENTLY ix_items_project_status;

-- Analyze table for query planner
ANALYZE items;
```

### Unused Index Detection

```sql
-- Find unused indexes
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND tablename IN ('items', 'links', 'change_log')
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Storage Impact

Approximate index sizes (depends on data volume):

- **Single-column indexes**: 50-200 KB each
- **Composite indexes**: 100-300 KB each
- **Full-text search index**: 200-500 KB
- **Total**: ~5-8 MB for typical project volume

## Migration Procedure

### Forward Migration

```bash
# Apply the migration
alembic upgrade head

# Verify indexes were created
psql -d trace_db -c "\di items"
```

### Backward Migration (if needed)

```bash
# Rollback
alembic downgrade -1

# Verify indexes were dropped
psql -d trace_db -c "\di items"
```

## Testing

### Load Testing Script

```sql
-- Generate test data
INSERT INTO items (id, project_id, name, status, owner)
SELECT
  gen_random_uuid(),
  (ARRAY['proj-1', 'proj-2', 'proj-3'])[floor(random()*3)+1],
  'Item ' || generate_series(1, 10000),
  (ARRAY['todo', 'in_progress', 'done'])[floor(random()*3)+1],
  'user-' || floor(random()*100)
FROM generate_series(1, 10000);

-- Test query performance before/after analyze
EXPLAIN ANALYZE SELECT * FROM items WHERE project_id = 'proj-1' AND status = 'in_progress';

-- Analyze for planner
ANALYZE items;

-- Re-run explain to see improvement
EXPLAIN ANALYZE SELECT * FROM items WHERE project_id = 'proj-1' AND status = 'in_progress';
```

### Verification Query

```sql
-- Verify indexes exist
SELECT indexname, indexdef FROM pg_indexes
WHERE tablename IN ('items', 'links', 'change_log')
AND schemaname = 'public'
ORDER BY tablename, indexname;
```

## Performance Expectations

### Query Speed Improvements

| Query Type | Expected Improvement | Typical Time |
|-----------|---------------------|--------------|
| Single lookup | 95% faster | 1-5ms |
| Small result set | 90% faster | 5-20ms |
| Large result set | 70% faster | 50-200ms |
| Full-text search | 80% faster | 20-100ms |

### Index Creation Time

- Initial creation: ~5-15 seconds for populated tables
- Minimal lock time: Indexes created concurrently
- Impact: Negligible on running application

## Troubleshooting

### Index Not Being Used

```sql
-- Check index usage
SELECT * FROM pg_stat_user_indexes WHERE indexname = 'ix_items_project_status';

-- Force analyze to update planner statistics
ANALYZE items;

-- Check planner estimates
EXPLAIN SELECT * FROM items WHERE project_id = ? AND status = ?;
```

### Query Still Slow

```sql
-- Check table statistics
SELECT
  n_live_tup,
  n_dead_tup,
  last_vacuum,
  last_autovacuum
FROM pg_stat_user_tables
WHERE relname = 'items';

-- Run maintenance if needed
VACUUM ANALYZE items;
```

### Disk Space Issues

```sql
-- Check index sizes
SELECT
  tablename,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

## Index Selection Philosophy

This migration follows these principles:

1. **Critical Path First**: Indexes on most frequently accessed columns
2. **Composite Benefits**: Multi-column indexes for common query patterns
3. **Covering Indexes**: Avoid nested index lookups for common queries
4. **Full-Text Capability**: GIN index for text search without like patterns
5. **Minimal Overhead**: Balance between query speed and write performance

## Future Optimization Opportunities

Potential future indexes based on application growth:

```sql
-- Workflow-specific indexes (if workflow feature expands)
CREATE INDEX ix_items_project_workflow ON items(project_id, workflow_state);

-- Batch operations on large result sets
CREATE INDEX ix_items_bulk_update ON items(project_id, updated_at) INCLUDE (status, owner);

-- Cross-project analytics (if needed)
CREATE INDEX ix_items_owner_created ON items(owner, created_at);
```

## References

- [PostgreSQL Index Types](https://www.postgresql.org/docs/current/indexes-types.html)
- [Query Planning](https://www.postgresql.org/docs/current/using-explain.html)
- [Index Statistics](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [EXPLAIN ANALYZE](https://www.postgresql.org/docs/current/sql-explain.html)
