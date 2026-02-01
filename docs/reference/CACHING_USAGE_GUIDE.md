# Graph Data Caching Usage Guide

## Quick Start

### For React Queries (Frontend)

```typescript
import { useQuery } from "@tanstack/react-query";
import { QUERY_CONFIGS, queryKeys } from "@/lib/queryConfig";

// Basic usage with predefined cache config
export function useGraphs(projectId: string) {
  return useQuery({
    queryKey: queryKeys.graph.full(projectId),
    queryFn: () => fetchGraphs(projectId),
    ...QUERY_CONFIGS.graph, // Use predefined cache settings
  });
}
```

### For In-Memory Cache (Layouts, Transforms)

```typescript
import { layoutCache, cacheKeys } from "@/lib/graphCache";

// Cache expensive layout computation
function computeLayout(graphId: string): LayoutData {
  const cacheKey = cacheKeys.layout(graphId, "force-directed");

  // Check cache first
  const cached = layoutCache.get(cacheKey);
  if (cached) return cached;

  // Compute if not cached
  const result = expensiveLayoutComputation(graphId);

  // Store in cache
  layoutCache.set(cacheKey, result);

  return result;
}
```

### For Graph Cache Store (State Management)

```typescript
import { useGraphCacheStore } from "@/stores/graphCacheStore";

// Get cached layout
const store = useGraphCacheStore();
const layout = store.getLayout("layout:graph1:force");

// Store computed data
store.setLayout("layout:graph1:force", computedLayout);

// Invalidate when item changes
store.invalidateByItem("item123");

// Get cache statistics
const stats = store.getStats();
console.log(`Cache hit ratio: ${stats.layouts.hitRate}`);
```

---

## Frontend Caching Patterns

### Pattern 1: Adaptive Cache Config

Use adaptive caching when data size and update frequency vary:

```typescript
import {
  calculateAdaptiveTTL,
  CacheMetrics,
  ADAPTIVE_CONFIGS,
} from "@/lib/adaptiveCacheConfig";

// Measure your data characteristics
const metrics: CacheMetrics = {
  dataSize: graphData.length * 1024, // Estimate in bytes
  updateFrequency: 5, // Updates per hour
  accessFrequency: 50, // Accesses per hour
  timestamp: Date.now(),
};

// Get adaptive configuration
const adaptiveConfig = ADAPTIVE_CONFIGS.graphAdaptive(metrics);

// Use in query
const { data } = useQuery({
  queryKey: ["graph", projectId],
  queryFn: () => fetchGraph(projectId),
  ...adaptiveConfig,
});
```

### Pattern 2: Layout Caching

Cache computed graph layouts to avoid expensive recalculations:

```typescript
import { layoutCache, cacheKeys } from "@/lib/graphCache";

export function useGraphLayout(graphId: string, algorithm: string) {
  const cacheKey = cacheKeys.layout(graphId, algorithm);

  return useQuery({
    queryKey: ["layout", graphId, algorithm],
    queryFn: async () => {
      // Check in-memory cache first
      const cached = layoutCache.get(cacheKey);
      if (cached) return cached;

      // Compute layout
      const positions = await computeLayout(graphId, algorithm);

      // Cache result
      layoutCache.set(cacheKey, {
        positions,
        bounds: calculateBounds(positions),
        graphId,
        algorithm,
        timestamp: Date.now(),
      });

      return positions;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
}
```

### Pattern 3: Search Result Caching

Cache search results with automatic invalidation:

```typescript
import { searchCache, cacheKeys } from "@/lib/graphCache";
import { useGraphCacheStore } from "@/stores/graphCacheStore";

export function useGraphSearch(graphId: string, query: string) {
  const cacheStore = useGraphCacheStore();
  const cacheKey = cacheKeys.search(graphId, query);

  return useQuery({
    queryKey: ["search", graphId, query],
    queryFn: async () => {
      // Check cache
      let cached = searchCache.get(cacheKey);
      if (cached) return cached;

      // Search
      const results = await searchGraph(graphId, query);

      // Cache with metadata
      const searchResult = {
        query,
        results,
        timestamp: Date.now(),
      };

      searchCache.set(cacheKey, searchResult);
      cacheStore.setSearchResult(cacheKey, results);

      return results;
    },
    staleTime: 30 * 1000, // 30 seconds
  });
}
```

### Pattern 4: Hierarchical Invalidation

Automatically invalidate related caches when data changes:

```typescript
import { useGraphCacheStore } from "@/stores/graphCacheStore";
import { useMutation, useQueryClient } from "@tanstack/react-query";

export function useUpdateItem(itemId: string) {
  const queryClient = useQueryClient();
  const cacheStore = useGraphCacheStore();

  return useMutation({
    mutationFn: (data: ItemUpdate) => updateItem(itemId, data),
    onSuccess: () => {
      // Invalidate caches hierarchically
      cacheStore.invalidateByItem(itemId, true); // Cascading

      // Also invalidate React Query caches
      queryClient.invalidateQueries({
        queryKey: ["items", itemId],
      });

      // Invalidate graph caches
      queryClient.invalidateQueries({
        queryKey: ["graph"],
      });
    },
  });
}
```

---

## Backend Caching Patterns

### Pattern 1: Graph Cache in Repository

```go
// backend/internal/repositories/graph_repository.go

type GraphRepository struct {
  db    *sql.DB
  cache *graph.GraphCache
}

func (r *GraphRepository) GetAncestors(ctx context.Context, itemID string, maxDepth int) (*graph.GraphResult, error) {
  // Use cached version
  result, err := r.cache.GetAncestorsCached(ctx, itemID, maxDepth)
  if err == nil {
    return result, nil // Cache hit
  }

  // Cache miss, compute
  return r.computeAncestors(ctx, itemID, maxDepth)
}
```

### Pattern 2: Cache Invalidation on Update

```go
// backend/internal/services/item_service.go

type ItemService struct {
  repo      *repositories.ItemRepository
  graphCache *graph.GraphCache
}

func (s *ItemService) UpdateItem(ctx context.Context, item *models.Item) error {
  // Update in database
  if err := s.repo.Update(ctx, item); err != nil {
    return err
  }

  // Invalidate caches
  s.graphCache.InvalidateItem(item.ID)

  return nil
}
```

### Pattern 3: Redis-Backed Cache

```go
// backend/internal/services/graph_service.go

type GraphService struct {
  localCache *graph.GraphCache  // Fast local cache
  redisCache *cache.RedisCache  // Distributed cache
}

func (s *GraphService) GetGraph(ctx context.Context, projectID string) (*graph.GraphResult, error) {
  // Try local cache first
  if cached, ok := s.localCache.Get(key); ok {
    return cached.(*graph.GraphResult), nil
  }

  // Try Redis
  var result graph.GraphResult
  if err := s.redisCache.Get(ctx, key, &result); err == nil {
    s.localCache.Set(key, &result) // Warm local cache
    return &result, nil
  }

  // Compute
  result, err := s.computeGraph(ctx, projectID)
  if err != nil {
    return nil, err
  }

  // Store in both caches
  s.localCache.Set(key, &result)
  s.redisCache.Set(ctx, key, &result)

  return &result, nil
}
```

---

## Cache Invalidation Strategies

### Strategy 1: Item Change Cascade

When an item is updated:

1. Invalidate item's layout cache
2. Invalidate ancestor's descendant caches
3. Invalidate descendant's ancestor caches
4. Invalidate all path caches involving the item
5. Invalidate transitive closure for the project

```typescript
// stores/graphCacheStore.ts
store.invalidateByItem(itemId, true); // Cascading invalidation
```

### Strategy 2: Link Change Cascade

When a link is created/deleted:

1. Invalidate transitive closure
2. Invalidate ancestor/descendant caches for affected items
3. Invalidate all path caches between affected items

```typescript
store.invalidateByPattern("transitive_closure:*");
store.invalidateByPattern("path:*");
```

### Strategy 3: Project Change

When project is significantly modified:

1. Invalidate all project-specific caches
2. Keep user-specific caches

```typescript
store.invalidateByProject(projectId);
```

### Strategy 4: Pattern-Based Invalidation

For fine-grained control:

```typescript
// Invalidate layouts for specific graph
store.invalidateByPattern(`layout:${graphId}:*`);

// Invalidate all search results
store.invalidateByPattern("search:*");

// Invalidate paths involving item
store.invalidateByPattern(`path:${itemId}:*`);
store.invalidateByPattern(`path:*:${itemId}`);
```

---

## Monitoring & Debugging

### Cache Statistics

```typescript
import { useGraphCache } from "@/lib/graphCache";

function CacheMonitor() {
  const { getStats } = useGraphCache();
  const stats = getStats();

  return (
    <div>
      <p>Layout Cache: {stats.layout.totalEntries} entries</p>
      <p>Grouping Cache: {stats.grouping.totalEntries} entries</p>
      <p>Search Cache: {stats.search.totalEntries} entries</p>
      <p>Total Memory: {(stats.total.totalMemory / 1024 / 1024).toFixed(2)} MB</p>
      <p>Hit Ratio: {(stats.total.totalHits / (stats.total.totalHits + stats.total.totalMisses) * 100).toFixed(1)}%</p>
    </div>
  );
}
```

### Cache Store Statistics

```typescript
function CacheStoreMonitor() {
  const stats = useGraphCacheStore(store => store.getStats());

  return (
    <div>
      <p>Layouts: {stats.layouts.count}</p>
      <p>Groupings: {stats.groupings.count}</p>
      <p>Total Invalidations: {stats.totalInvalidations}</p>
    </div>
  );
}
```

### Debugging Cache Keys

```typescript
// View all cached keys matching pattern
const cache = useGraphCache();
const layoutKeys = cache.layoutCache.keysMatching("layout:graph1:*");
console.log("Cached layouts:", layoutKeys);
```

### Memory Pressure Alerts

```typescript
function MemoryPressureMonitor() {
  const { layoutCache } = useGraphCache();
  const pressure = layoutCache.getMemoryPressure();

  if (pressure === "critical") {
    console.warn("Cache memory pressure critical!");
    // Could trigger cache cleanup
  }
}
```

---

## Performance Tuning

### Tuning Stale Time

```typescript
// Too short: Frequent refetches, lower cache effectiveness
staleTime: 10 * 1000 // 10 seconds - Too aggressive

// Good: Balances freshness and performance
staleTime: 5 * 60 * 1000 // 5 minutes - Good for most use cases

// Too long: Stale data, user confusion
staleTime: 60 * 60 * 1000 // 60 minutes - Too lenient
```

### Tuning GC Time

```typescript
// GC time should be longer than stale time
// Formula: gcTime = staleTime * 3 (rough guideline)

staleTime: 5 * 60 * 1000, // 5 minutes
gcTime: 15 * 60 * 1000, // 15 minutes (3x)
```

### Tuning LRU Capacity

```typescript
// Adjust based on available memory and typical data size
const layoutCache = createGraphCache(
  100, // Max 100 entries
  52428800 // 50 MB max
);
```

---

## Common Pitfalls

### Pitfall 1: Not Invalidating on Updates

**Wrong:**
```typescript
const result = await updateItem(data);
// Cache still has old data!
```

**Right:**
```typescript
const result = await updateItem(data);
graphCacheStore.invalidateByItem(data.id);
queryClient.invalidateQueries({ queryKey: ["items"] });
```

### Pitfall 2: Cascading Invalidations Too Aggressively

**Wrong:**
```typescript
// Invalidates entire project on single item change
store.invalidateByProject(projectId);
```

**Right:**
```typescript
// Only invalidate affected items
store.invalidateByItem(itemId, true); // Cascading to related items
```

### Pitfall 3: Memory Leaks from Unbounded Cache

**Wrong:**
```typescript
const cache = new Map(); // Grows indefinitely
cache.set(key, largeObject);
```

**Right:**
```typescript
const cache = createGraphCache(100, 52428800); // Bounded LRU
cache.set(key, largeObject); // Auto-evicts old entries
```

### Pitfall 4: Cache Key Collisions

**Wrong:**
```typescript
// Same key for different contexts
`layout:${graphId}:force` // Doesn't distinguish algorithms
```

**Right:**
```typescript
// Include all relevant parameters
cacheKeys.layout(graphId, algorithm)
// Results in: layout:graph1:force-directed
```

---

## Testing Cache Behavior

### Test Cache Hits

```typescript
it("should cache layout computations", async () => {
  const cache = createGraphCache();
  const cacheKey = cacheKeys.layout("g1", "force");

  const layout1 = cache.get(cacheKey) || {
    positions: {},
    bounds: { minX: 0, minY: 0, maxX: 100, maxY: 100 },
  };

  cache.set(cacheKey, layout1);
  const layout2 = cache.get(cacheKey);

  expect(layout2).toEqual(layout1);
  expect(cache.getStats().totalHits).toBe(1);
});
```

### Test Cache Invalidation

```typescript
it("should invalidate by pattern", () => {
  const store = useGraphCacheStore();

  store.setLayout("layout:g1:force", layoutData);
  store.setLayout("layout:g1:circle", layoutData);

  store.invalidateLayout("g1");

  expect(store.getLayout("layout:g1:force")).toBeNull();
  expect(store.getLayout("layout:g1:circle")).toBeNull();
});
```

### Test Memory Management

```typescript
it("should evict LRU entries under memory pressure", () => {
  const cache = createGraphCache(10, 1024); // 1 KB limit
  const largeObj = { data: "x".repeat(500) };

  cache.set("key1", largeObj);
  cache.set("key2", largeObj);
  cache.set("key3", largeObj);

  // key1 should be evicted
  expect(cache.has("key1")).toBe(false);
  expect(cache.has("key2")).toBe(true);
  expect(cache.has("key3")).toBe(true);
});
```

---

## FAQ

**Q: When should I use which cache layer?**

A:
- React Query: Network requests, API responses
- LRU Cache (layoutCache, etc.): Expensive computations, layouts
- Zustand Store: UI state, view configurations
- LocalStorage: User preferences, session data

**Q: How do I know cache is working?**

A: Check statistics:
- `cache.getStats().hitRatio > 0.3` is a good sign
- `layoutCache.getStats().totalHits > 0` means it's being used
- Monitor in React DevTools Profiler

**Q: What happens if cache gets corrupted?**

A: Call `clearAllCaches()` to reset. Data will be recomputed on next access.

**Q: Can I share cache between browser tabs?**

A: Not recommended for LRU cache. Use LocalStorage or Server-Side Session for cross-tab data.

**Q: How do I debug cache misses?**

A: Enable debug logging:
```typescript
if (process.env.NODE_ENV === "development") {
  console.debug("Cache miss for key:", key);
}
```

---

## Resources

- [React Query Documentation](https://tanstack.com/query/latest)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Cache Invalidation Strategies](https://www.mnot.net/cache_docs/)
- [LRU Cache Theory](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU))
