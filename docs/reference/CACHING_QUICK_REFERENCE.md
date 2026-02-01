# Caching Quick Reference

## File Locations

```
Frontend Implementation:
├── /frontend/apps/web/src/lib/adaptiveCacheConfig.ts (Adaptive TTL)
├── /frontend/apps/web/src/lib/graphCache.ts (LRU Cache)
├── /frontend/apps/web/src/stores/graphCacheStore.ts (State Management)
├── /frontend/apps/web/src/__tests__/lib/adaptiveCacheConfig.test.ts (Tests)
└── /frontend/apps/web/src/__tests__/lib/graphCache.test.ts (Tests)

Documentation:
├── /docs/CACHING_STRATEGIES_IMPLEMENTATION.md (Full Plan)
├── /docs/CACHING_USAGE_GUIDE.md (Examples & Patterns)
├── /docs/BACKEND_CACHING_ENHANCEMENTS.md (Backend Improvements)
├── /docs/CACHING_IMPLEMENTATION_SUMMARY.md (Overview)
└── /docs/CACHING_QUICK_REFERENCE.md (This File)
```

## Quick Examples

### Use Adaptive Cache Config

```typescript
import { ADAPTIVE_CONFIGS, CacheMetrics } from "@/lib/adaptiveCacheConfig";

const metrics: CacheMetrics = {
  dataSize: 500 * 1024,
  updateFrequency: 5,
  accessFrequency: 50,
  timestamp: Date.now(),
};

const config = ADAPTIVE_CONFIGS.graphAdaptive(metrics);

useQuery({
  queryKey: ["graph", projectId],
  queryFn: () => fetchGraph(projectId),
  ...config,
});
```

### Cache Layout Computation

```typescript
import { layoutCache, cacheKeys } from "@/lib/graphCache";

const key = cacheKeys.layout(graphId, "force-directed");
const cached = layoutCache.get(key);

if (!cached) {
  const computed = computeLayout();
  layoutCache.set(key, computed);
}
```

### Invalidate Caches

```typescript
import { useGraphCacheStore } from "@/stores/graphCacheStore";

const store = useGraphCacheStore();

// On item update
store.invalidateByItem(itemId, true); // Cascading

// On project update
store.invalidateByProject(projectId);

// Pattern-based
store.invalidateByPattern("layout:graph1:*");
```

### Get Cache Statistics

```typescript
import { useGraphCache } from "@/lib/graphCache";

const { getStats } = useGraphCache();
const stats = getStats();

console.log(`Layouts: ${stats.layout.totalEntries}`);
console.log(`Total hits: ${stats.total.totalHits}`);
console.log(`Memory: ${(stats.total.totalMemory / 1024 / 1024).toFixed(2)} MB`);
```

## Cache Tiers

| Tier | Type | TTL | Size | When to Use |
|------|------|-----|------|-----------|
| Static | Long-lived data | 10-30m | Large | Projects, schemas |
| Dynamic | Frequently changing | 30s-5m | Medium | Items, lists |
| Graph | Expensive computations | 5-15m | Large | Layouts, paths |
| Realtime | Always fresh | 0-5s | Small | Live updates |

## Key Generation

```typescript
cacheKeys.layout(graphId, algorithm)           // layout:graphId:algorithm
cacheKeys.grouping(graphId, strategy)         // grouping:graphId:strategy
cacheKeys.search(graphId, query)              // search:graphId:query
cacheKeys.pathfinding(sourceId, targetId)    // path:sourceId:targetId
cacheKeys.aggregation(type, params)           // agg:type:params
```

## Pattern Matching

```typescript
store.invalidateByPattern("layout:*")         // All layouts
store.invalidateByPattern("layout:graph1:*")  // Graph1 layouts
store.invalidateByPattern("*:force*")         // All force algorithms
store.invalidateByPattern("path:item1:*")     // Paths from item1
```

## Cache Capacity

| Cache | Max Entries | Max Memory | Use For |
|-------|------------|-----------|---------|
| Layout | 100 | 50 MB | Graph layouts |
| Grouping | 50 | 25 MB | Item groupings |
| Search | 100 | 10 MB | Search results |

## Memory Pressure Levels

```typescript
cache.getMemoryPressure() // Returns:
// "comfortable" (<70%)
// "caution" (70-85%)
// "critical" (>85%)
```

## Invalidation Cascade

```
Item Update
  ├─ Item's ancestors: descendants cache
  ├─ Item's descendants: ancestors cache
  ├─ All paths involving item
  └─ Transitive closure

Link Creation/Deletion
  ├─ Transitive closure
  └─ All paths involving items

Project Change
  └─ All project-specific caches
```

## Testing Checklist

- [ ] Cache gets/sets work
- [ ] LRU eviction occurs at capacity
- [ ] Memory limits enforced
- [ ] Statistics tracked correctly
- [ ] Pattern matching works
- [ ] TTL expiration works
- [ ] Invalidation cascades
- [ ] Thread-safe operations

## Deployment Checklist

- [ ] Deploy cache utilities
- [ ] Update queries to use configs
- [ ] Implement cache invalidation
- [ ] Add monitoring
- [ ] Run performance tests
- [ ] Monitor hit ratios
- [ ] Tune TTL values
- [ ] Document for team

## Metrics to Monitor

```
Frontend:
- react_query_hit_ratio_percent
- memory_cache_memory_usage_bytes
- memory_cache_entries_count
- cache_invalidation_count_total

Backend:
- graph_cache_hit_ratio_percent
- graph_cache_memory_usage_bytes
- cache_invalidation_duration_ms
- cache_invalidation_count_total
```

## Common Commands

```typescript
// Get cache statistics
const stats = useGraphCache().getStats();

// Clear all caches
clearAllCaches();

// Prewarm cache
prewarmCache(graphId);

// Check memory pressure
cache.getMemoryPressure();

// Reset statistics
cache.resetStats();

// Find matching keys
cache.keysMatching("layout:*");
```

## Troubleshooting

**Cache hits too low?**
- Check TTL settings
- Verify cache key generation
- Monitor access patterns
- Consider prewarming

**Memory usage high?**
- Reduce max entries
- Reduce max memory
- Enable preload filtering
- Check for memory leaks

**Cache not invalidating?**
- Verify invalidation is called
- Check pattern matching
- Review cascading logic
- Monitor invalidation stats

**Performance not improving?**
- Measure before/after latency
- Check hit ratio
- Analyze hot paths
- Profile memory usage

## Integration Checklist

```
1. Frontend
   [ ] Add adaptiveCacheConfig.ts
   [ ] Add graphCache.ts
   [ ] Add graphCacheStore.ts
   [ ] Update useQuery calls
   [ ] Implement invalidation

2. Backend
   [ ] Add cache_invalidator.go
   [ ] Update services
   [ ] Add metrics endpoint
   [ ] Configure cache limits

3. Testing
   [ ] Unit tests pass
   [ ] Integration tests pass
   [ ] E2E tests pass
   [ ] Performance tests pass

4. Monitoring
   [ ] Metrics collected
   [ ] Alerts configured
   [ ] Dashboards created
   [ ] Logs analyzed

5. Documentation
   [ ] Usage guide updated
   [ ] API docs updated
   [ ] Runbook created
   [ ] Team trained
```

## Performance Targets

| Metric | Target | Alert |
|--------|--------|-------|
| Hit Ratio | >50% | <30% |
| Latency Improvement | 30-40% | <10% |
| Memory Overhead | <5% | >10% |
| Consistency | 100% | <99.9% |
| Availability | 99.95% | <99% |

## Resources

- Full docs: `/docs/CACHING_STRATEGIES_IMPLEMENTATION.md`
- Usage guide: `/docs/CACHING_USAGE_GUIDE.md`
- Backend enhancements: `/docs/BACKEND_CACHING_ENHANCEMENTS.md`
- Test examples: `/__tests__/lib/graphCache.test.ts`

## Support

For issues:
1. Check usage guide examples
2. Review test cases
3. Enable debug logging
4. Check cache statistics
5. Monitor metrics dashboard

---

**Version**: 1.0
**Status**: Ready for Implementation
**Expected Performance Gain**: 30-40% latency reduction
