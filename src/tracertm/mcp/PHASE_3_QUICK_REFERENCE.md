# Phase 3 Quick Reference

## 🚀 Quick Start

### Import Optimized Utilities
```python
from tracertm.mcp.tools.base_async import (
    get_async_session,       # Pooled async sessions
    cached_query,            # Query caching
    invalidate_cache,        # Cache invalidation
    require_project,
    wrap_success
)
from tracertm.mcp.query_optimizer import QueryOptimizer
```

---

## 📊 Connection Pooling

### Get Async Session
```python
# Use connection pool
async with get_async_session() as session:
    result = await session.execute(query)
    data = result.scalars().all()
    # Auto-commit/rollback
```

### Check Pool Status
```python
from tracertm.mcp.database_manager import get_database_manager

db_manager = await get_database_manager()
status = await db_manager.get_pool_status()
# {"size": 10, "checked_out": 3, "overflow": 2, "checked_in": 7}
```

---

## 💾 Query Caching

### Cache Read Query
```python
async def _fetch_data():
    async with get_async_session() as session:
        result = await session.execute(query)
        return result.scalars().all()

# Cache for 5 minutes
data = await cached_query(
    "cache_key",
    _fetch_data,
    ttl=300,
    project_id=project_id
)
```

### Invalidate Cache
```python
# After write operations
invalidate_cache("item_")        # All item queries
invalidate_cache("project_list") # Specific cache
invalidate_cache()               # Clear all
```

### Cache Stats
```python
from tracertm.mcp.cache import get_query_cache

cache = get_query_cache()
stats = cache.get_stats()
# {"hit_rate": 0.85, "size": 234, "hits": 890, "misses": 120}
```

---

## 🔗 Eager Loading (Avoid N+1)

### Items with Links
```python
# ✅ Loads items + source_links + target_links in 1 query
items = await QueryOptimizer.get_items_with_links(
    session,
    project_id="proj-123",
    view="FEATURE",
    status="active",
    limit=50
)
```

### Links with Items
```python
# ✅ Loads links + source_item + target_item in 1 query
links = await QueryOptimizer.get_links_with_items(
    session,
    project_id="proj-123",
    link_type="implements",
    limit=50
)
```

### Item with Hierarchy
```python
# ✅ Loads item + parent + children in 1 query
item = await QueryOptimizer.get_item_with_hierarchy(
    session,
    item_id="item-123",
    project_id="proj-123"
)
```

### Batch Get Items
```python
# ✅ Loads multiple items in 1 query
items_dict = await QueryOptimizer.batch_get_items(
    session,
    item_ids=["id1", "id2", "id3"],
    project_id="proj-123"
)
# Returns: {"id1": <Item>, "id2": <Item>, "id3": <Item>}
```

---

## 📈 Performance Monitoring

### Database Metrics
```python
from tracertm.mcp.tools.items_phase3 import get_db_metrics_phase3

metrics = await get_db_metrics_phase3()
# Returns:
# {
#   "database": {"status": "healthy", "version": "..."},
#   "pool": {"size": 10, "checked_out": 3, ...},
#   "cache": {"hit_rate": 0.85, "size": 234, ...},
#   "queries": {"avg_duration_ms": 45.2, "slow_queries_count": 12}
# }
```

### Slow Queries
```python
db_manager = await get_database_manager()
health = await db_manager.health_check()
slow_queries = health["queries"]["recent_slow_queries"]

for sq in slow_queries:
    print(f"Query: {sq['query'][:100]}")
    print(f"Duration: {sq['duration_ms']}ms")
```

---

## 🛠️ Tool Conversion Pattern

### Before (Sync)
```python
from tracertm.mcp.tools.base import get_session

@mcp.tool()
def my_tool():
    with get_session() as session:
        items = session.query(Item).filter(...).all()
        return {"items": items}
```

### After (Async + Pooled + Cached)
```python
from tracertm.mcp.tools.base_async import get_async_session, cached_query

@mcp.tool()
async def my_tool():
    async def _fetch():
        async with get_async_session() as session:
            result = await session.execute(
                select(Item).where(...)
            )
            return result.scalars().all()

    items = await cached_query("my_tool", _fetch, ttl=300)
    return {"items": items}
```

---

## 📋 Common Patterns

### Create with Cache Invalidation
```python
@mcp.tool()
async def create_item(title: str, ...):
    async with get_async_session() as session:
        item = Item(...)
        session.add(item)
        await session.commit()

    # Invalidate caches
    invalidate_cache(f"item_query_{project_id}")
    invalidate_cache(f"item_view_{project_id}_{view}")

    return wrap_success(_item_to_dict(item), "create", ctx)
```

### Query with Eager Loading + Cache
```python
@mcp.tool()
async def query_items(include_links: bool = False, ...):
    async def _query():
        async with get_async_session() as session:
            if include_links:
                return await QueryOptimizer.get_items_with_links(
                    session, project_id, limit=50
                )
            else:
                result = await session.execute(
                    select(Item).where(...)
                )
                return result.scalars().all()

    items = await cached_query(
        f"item_query_{project_id}",
        _query,
        ttl=300,
        include_links=include_links
    )

    return wrap_success({"items": [_item_to_dict(i) for i in items]}, ...)
```

---

## 🎯 Performance Targets

| Optimization | Expected Gain |
|--------------|---------------|
| Connection pooling | 30-50% faster |
| Query caching (hit) | 99% faster |
| Eager loading | 80-90% fewer queries |
| **Combined** | **50%+ faster** |

---

## 🧪 Testing

### Run Benchmark
```bash
python -m tracertm.mcp.db_benchmark \
    "postgresql://user:pass@localhost/db" \
    "project-id-here"
```

### Run Tests
```bash
pytest tests/unit/mcp/test_database_manager.py -v
pytest tests/unit/mcp/test_cache.py -v
```

---

## 🗄️ Database Indexes

```sql
-- Required for optimal performance
CREATE INDEX idx_items_project_view ON items(project_id, view);
CREATE INDEX idx_items_status ON items(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_links_source ON links(source_item_id);
CREATE INDEX idx_links_target ON links(target_item_id);
```

---

## 🔍 Troubleshooting

### "Not connected" error
```python
from tracertm.mcp.database_manager import get_database_manager
db_manager = await get_database_manager()
await db_manager.initialize()
```

### Cache not invalidating
```python
# Be specific with cache keys
invalidate_cache(f"item_query_{project_id}")  # Good
invalidate_cache("item_")                      # Too broad
```

### Slow queries
```python
# 1. Check indexes exist
# 2. Use QueryOptimizer for relationships
# 3. Review slow query logs
health = await db_manager.health_check()
print(health["queries"]["recent_slow_queries"])
```

---

## 📚 See Also

- **Full Guide**: `PHASE_3_DATABASE_OPTIMIZATION.md`
- **Completion Summary**: `PHASE_3_COMPLETION_SUMMARY.md`
- **Example Tools**: `tools/items_phase3.py`
- **Benchmark**: `db_benchmark.py`
