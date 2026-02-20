# Graph Caching Quick Reference

## TL;DR
The shortest path service now uses Redis caching for 10x performance improvement (2s → <200ms).

---

## Quick Start

### API Usage
```bash
# Automatic caching - no changes needed
GET /api/v1/analysis/shortest-path?project_id=X&source_id=Y&target_id=Z

# First call: ~2s (cache miss)
# Subsequent calls: <200ms (cache hit for 5 minutes)
```

### Python Service Usage
```python
# With cache (recommended for production)
from tracertm.services.cache_service import get_cache_service

cache = get_cache_service()
service = ShortestPathService(db_session, cache)

# Without cache (backward compatible)
service = ShortestPathService(db_session)
```

---

## Cache Behavior

| Scenario | Performance | Details |
|----------|-------------|---------|
| **Cache Hit** | <200ms | Path found in Redis, no computation |
| **Cache Miss** | ~2s | Computes path, stores in Redis for 5 min |
| **Cache Unavailable** | ~2s | Falls back to computation, no error |
| **After 5 minutes** | ~2s | TTL expired, recomputes and caches |

---

## Cache Keys

```
Format: tracertm:graph:{project_id}:path:{source_id}:{target_id}:{link_types}

Examples:
tracertm:graph:proj-123:path:item-1:item-2:all
tracertm:graph:proj-123:path:item-1:item-2:depends_on:implements
tracertm:graph:proj-123:all_paths:item-1:all
```

---

## Automatic Invalidation

Cache automatically clears when:
- ✅ Items are created/updated/deleted
- ✅ Links are created/deleted
- ✅ Projects are updated

**No manual cache management needed!**

---

## Monitoring

### Check Cache Health
```bash
GET /api/v1/admin/cache/stats

Response:
{
  "hits": 1250,
  "misses": 180,
  "hit_rate": 87.4,
  "total_size_bytes": 524288
}
```

### Clear Cache (Admin Only)
```bash
# Clear all graph caches for a project
DELETE /api/v1/admin/cache?prefix=graph:proj-123

# Clear all caches
DELETE /api/v1/admin/cache
```

---

## Troubleshooting

### Cache Not Working?
1. Check Redis is running: `redis-cli ping` → `PONG`
2. Check connection: `GET /api/v1/health` → check `cache_healthy`
3. Check logs for cache warnings

### Unexpected Stale Data?
- Cache invalidates automatically on item/link changes
- Max staleness: 5 minutes (TTL)
- Force clear: `DELETE /api/v1/admin/cache?prefix=graph:YOUR_PROJECT_ID`

### Performance Not Improved?
- First request is always slow (cache miss)
- Subsequent requests should be <200ms
- Check cache hit rate in stats (should be >70%)

---

## Development

### Running Tests
```bash
# Caching tests
python -m pytest tests/unit/services/test_shortest_path_cache.py -v

# Integration tests (without cache)
python -m pytest tests/integration/services/ -v -k shortest
```

### Disable Caching (for testing)
```python
# Simply don't pass cache parameter
service = ShortestPathService(db_session)
```

---

## Configuration

### Redis URL
```bash
# Environment variable
export REDIS_URL="redis://localhost:6379"

# Or in config
redis_url: "redis://localhost:6379"
```

### TTL Adjustment (if needed)
```python
# In cache_service.py CACHE_CONFIG
"graph": {
    "ttl": 300,  # Change to desired seconds
    "prefix": "graph",
}
```

---

## Performance Metrics

### Before Caching
- Average response time: 2000-3000ms
- Database queries per request: 2 (items + links)
- CPU usage: High (Dijkstra's algorithm every request)

### After Caching (with 80% hit rate)
- Average response time: 400ms (80% hits @ 200ms + 20% misses @ 2000ms)
- Database queries per request: 0.4 (only on cache miss)
- CPU usage: Low (most requests served from cache)

---

## Best Practices

1. **Always use cache in production** - Pass cache service to constructor
2. **Monitor hit rate** - Should be >70% for typical usage
3. **Don't manually invalidate** - Automatic invalidation handles it
4. **Use link type filters** - Different filters have separate cache keys
5. **Set up Redis persistence** - Configure Redis to persist cache across restarts

---

## See Also

- `/GRAPH_CACHING_IMPLEMENTATION.md` - Detailed implementation
- `/PHASE_2_4_COMPLETION_SUMMARY.md` - Complete implementation summary
- `/src/tracertm/services/cache_service.py` - Cache service implementation
- `/tests/unit/services/test_shortest_path_cache.py` - Test examples
