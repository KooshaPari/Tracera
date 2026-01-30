# Graph Data Caching Strategies Implementation Plan

## Executive Summary

This document outlines a comprehensive caching strategy enhancement for the Trace application's graph data layer. The current implementation has basic caching, but lacks advanced features like adaptive TTL, memory pressure handling, and granular invalidation patterns.

**Current State:**
- Frontend: React Query with fixed stale time settings
- Backend: In-memory GraphCache with basic TTL + Redis adapter
- Issues: Coarse-grained cache invalidation, no memory management, fixed TTL values

**Proposed Improvements:**
- Adaptive TTL based on data access patterns
- LRU cache with memory pressure management
- Granular cache invalidation with hierarchical invalidation
- Cache prewarming strategies
- Advanced monitoring and metrics

---

## Part 1: Frontend Caching Enhancement

### 1.1 Enhanced Query Configuration with Adaptive TTL

**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/lib/queryConfig.ts`

**Current Implementation:**
```typescript
export const QUERY_CONFIGS = {
  static: { staleTime: 10 * 60 * 1000, gcTime: 30 * 60 * 1000 },
  dynamic: { staleTime: 30 * 1000, gcTime: 5 * 60 * 1000 },
  graph: { staleTime: 5 * 60 * 1000, gcTime: 15 * 60 * 1000 },
  realtime: { staleTime: 0, gcTime: 1 * 60 * 1000 },
  session: { staleTime: 5 * 60 * 1000, gcTime: 60 * 60 * 1000 },
}
```

**Proposed Enhancements:**

1. **Adaptive TTL Calculator** - Adjusts cache duration based on:
   - Data size (large graphs need shorter TTL)
   - Update frequency (frequently updated data gets shorter TTL)
   - Time of day (less aggressive caching during peak hours)

2. **Query Size Categories** - Different strategies for:
   - Small graphs (< 100 nodes): Longer TTL
   - Medium graphs (100-1000 nodes): Standard TTL
   - Large graphs (> 1000 nodes): Shorter TTL

3. **Context-Aware Settings** - Settings vary by context:
   - Read-heavy operations (static graphs): Longer TTL
   - Write-heavy operations (editable items): Shorter TTL
   - Real-time collaboration: Very short TTL

**Implementation Details:**
- Create `lib/adaptiveCacheConfig.ts` with adaptive TTL calculation
- TTL ranges: 30s (hot data) to 30m (static data)
- Metrics tracking for cache effectiveness

### 1.2 In-Memory Cache Layer with LRU Eviction

**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/lib/graphCache.ts`

**Purpose:** Local memory cache for expensive computations (layouts, transforms, aggregations)

**Key Features:**

1. **LRU Cache Implementation**
   - Max size: Configurable (default 100 entries)
   - Auto-evict least recently used entries
   - Memory pressure aware (evict on ~80% capacity)

2. **Cache Entry Metadata**
   - Hit/miss counts
   - Last access time
   - Computation time saved
   - Memory usage estimate

3. **Cache Key Strategy**
   - Stable hashing of query params and dependencies
   - Prevents collisions across different graph types
   - Supports partial matches for pattern invalidation

**Methods:**

```
- set(key, value, options?)  // Store with optional TTL
- get(key)                   // Retrieve if valid
- has(key)                   // Check existence
- delete(key)                // Remove entry
- clear()                    // Clear all entries
- stats()                    // Get cache statistics
- prewarm(entries)           // Bulk load for prewarming
- invalidatePattern(pattern) // Granular pattern-based invalidation
```

### 1.3 Graph Cache Store with Hierarchical Invalidation

**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/stores/graphCacheStore.ts`

**Purpose:** Zustand store managing cached graph state with intelligent invalidation

**Store Structure:**

```typescript
interface GraphCacheStore {
  // Cached data
  layoutPositions: Map<string, LayoutData>
  groupings: Map<string, GroupingData>
  searchResults: Map<string, SearchResult[]>

  // Metadata
  cacheStats: CacheStatistics
  invalidationPatterns: InvalidationPattern[]

  // Operations
  setLayout(key, data)
  setGrouping(key, data)
  setSearchResult(key, data)
  invalidateByItem(itemId)        // Cascading invalidation
  invalidateByProject(projectId)  // Project-level invalidation
  invalidateByPattern(pattern)    // Pattern-based invalidation
  getStats()
}
```

**Invalidation Hierarchy:**
- Item change → Invalidate: ancestors, descendants, paths, impact
- Link change → Invalidate: affected graphs, transitive closure
- Project change → Invalidate: all cached data for project

---

## Part 2: Backend Caching Enhancement

### 2.1 Advanced GraphCache with Memory Management

**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/graph/cache.go`

**Current Issues:**
- No memory limit management
- Coarse-grained invalidation (clears entire cache)
- No TTL decay or adaptive behavior

**Enhancements:**

1. **LRU Eviction Strategy**
   - Max memory limit (configurable, default 256MB)
   - Tracks entry size for accurate memory accounting
   - Evicts LRU entries when limit approached

2. **Granular Cache Keys**
   ```
   Format: {prefix}:{params_hash}:{version}
   Examples:
   - descendants:itemId:maxDepth:v1
   - ancestors:itemId:maxDepth:v1
   - path:sourceId:targetId:v1
   - transitive_closure:projectId:v1
   - full_graph:projectId:v1
   ```

3. **Cache Versioning**
   - Version incremented on invalidation
   - Allows safe concurrent access
   - Supports gradual cache decay

4. **Adaptive TTL**
   ```
   Base TTL + Adjustment:
   - Hot items (recent access): +50% to TTL
   - Cold items (stale): -50% to TTL
   - Large graphs: -30% (memory pressure)
   - Small graphs: +30% (low overhead)
   ```

### 2.2 Hierarchical Invalidation Patterns

**New Methods:**

```go
// Invalidate all caches related to an item
InvalidateItem(itemID string)

// Invalidate item and cascade to related items
InvalidateItemCascading(itemID string) error

// Invalidate by pattern (e.g., "descendants:*")
InvalidatePattern(pattern string) error

// Get invalidation impact analysis
GetInvalidationImpact(itemID string) ImpactAnalysis

// Selective invalidation with filtering
InvalidateWithFilter(predicate func(CacheEntry) bool) error
```

### 2.3 Cache Invalidation Coordinator Service

**New File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/services/cache_invalidator.go`

**Responsibilities:**
- Centralized cache invalidation logic
- Tracks dependencies between cached items
- Implements cascading invalidation rules
- Coordinates with transaction log

**Key Features:**

1. **Dependency Tracking**
   - Maintains dependency graph
   - Updates on item/link changes
   - Lazy evaluation for performance

2. **Batched Invalidation**
   - Groups related invalidations
   - Reduces Redis round-trips
   - Atomic invalidation transactions

3. **Change Log Integration**
   - Subscribes to change stream
   - Immediate invalidation on changes
   - Fallback to TTL-based expiration

---

## Part 3: Integration & Optimization Strategies

### 3.1 Cache Warming Strategies

**Scenario 1: User Session Start**
- Preload recent project graphs
- Preload user's default views
- Preload frequently accessed items

**Scenario 2: Large Graph Rendering**
- Progressive loading of layout cache
- Batch compute expensive calculations
- Stagger Redis reads to avoid stampede

**Scenario 3: Bulk Operations**
- Cache intermediate results
- Reuse subgraph computations
- Invalidate strategically at end

### 3.2 Memory Pressure Management

**Tier-Based Strategy:**

1. **Comfortable (< 70% memory):** Normal operation
2. **Caution (70-80%):**
   - Reduce TTL by 25%
   - Evict cold entries
   - Limit new entries

3. **Critical (> 80%):**
   - Aggressive LRU eviction
   - Halt non-essential caching
   - Emergency flush option

### 3.3 Performance Optimization Patterns

**Pattern 1: Result Pipelining**
```
Request → Cache Check → Compute → Store → Return
  ↓
  If cache hit, skip compute phase
```

**Pattern 2: Dual-Write Consistency**
```
Update Item → Invalidate Redis + Local Cache → Synchronously
```

**Pattern 3: Lazy Invalidation**
```
Change Event → Mark stale → Lazy refresh on next access
```

### 3.4 Monitoring & Metrics

**Frontend Metrics:**
- Cache hit/miss ratio per query
- Average cache serving time
- Stale data refresh frequency
- Memory usage by cache type

**Backend Metrics:**
- Redis memory usage
- Cache entry count trends
- Eviction rate
- Invalidation patterns
- Query latency with/without cache

**Alerts:**
- Cache hit ratio < 30%
- Memory usage > 85%
- Invalidation storm (> 100 ops/min)
- Stale data serving > 5%

---

## Part 4: Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
1. Create `lib/graphCache.ts` with LRU implementation
2. Create `lib/adaptiveCacheConfig.ts`
3. Add metrics collection framework
4. Update `queryConfig.ts` with adaptive settings

**Deliverables:**
- Basic LRU cache working
- Frontend metrics dashboard
- Tests with 90%+ coverage

### Phase 2: Backend Enhancement (Week 2-3)
1. Enhance `cache.go` with memory management
2. Create `cache_invalidator.go` service
3. Implement hierarchical invalidation
4. Add backend metrics collection

**Deliverables:**
- Granular cache invalidation
- Memory-aware caching
- Backend metrics exposed via /metrics
- Integration tests

### Phase 3: Integration (Week 3-4)
1. Implement cache warming in repositories
2. Add prewarming hooks to common queries
3. Integrate metrics with monitoring
4. Performance tuning based on metrics

**Deliverables:**
- End-to-end caching working
- Cache warming reducing latency by 40%+
- Comprehensive monitoring
- Performance benchmarks

### Phase 4: Optimization (Week 4+)
1. Analyze metrics and optimize TTLs
2. Implement smart prewarming
3. Add compression for large entries
4. Implement cache clustering for distributed setup

**Deliverables:**
- 50%+ cache hit ratio
- 30-40% reduction in compute time
- Automated cache tuning
- Production-ready monitoring

---

## Part 5: Implementation Examples

### Example 1: Adaptive TTL Calculator

```typescript
// lib/adaptiveCacheConfig.ts
export interface CacheMetrics {
  dataSize: number
  updateFrequency: number // changes per hour
  accessFrequency: number // accesses per hour
  timestamp: number
}

export function calculateAdaptiveTTL(
  metrics: CacheMetrics,
  baseConfig: QueryConfig
): QueryConfig {
  let ttlMultiplier = 1.0

  // Size-based adjustment
  if (metrics.dataSize > 10000) {
    ttlMultiplier *= 0.7 // Large graphs: shorter TTL
  } else if (metrics.dataSize < 100) {
    ttlMultiplier *= 1.3 // Small graphs: longer TTL
  }

  // Update frequency adjustment
  if (metrics.updateFrequency > 10) {
    ttlMultiplier *= 0.6 // Frequently updated: shorter TTL
  } else if (metrics.updateFrequency < 1) {
    ttlMultiplier *= 1.5 // Rarely updated: longer TTL
  }

  return {
    ...baseConfig,
    staleTime: Math.max(
      30_000,
      Math.min(
        30 * 60 * 1000,
        baseConfig.staleTime * ttlMultiplier
      )
    ),
  }
}
```

### Example 2: Hierarchical Invalidation

```typescript
// stores/graphCacheStore.ts
invalidateByItem(itemId: string) {
  // Direct invalidations
  this.deleteLayout(`item:${itemId}`)
  this.deleteGrouping(`item:${itemId}`)

  // Cascade to related items
  const ancestors = this.getAncestors(itemId)
  const descendants = this.getDescendants(itemId)

  // Invalidate all related caches
  ancestors.forEach(aid => {
    this.invalidatePattern(`descendants:${aid}:*`)
  })

  descendants.forEach(did => {
    this.invalidatePattern(`ancestors:${did}:*`)
  })

  // Invalidate transitive closure
  this.deletePattern(`transitive_closure:*`)
}
```

### Example 3: LRU Cache with Memory Management

```go
// backend/internal/graph/lru_cache.go
type LRUCache struct {
  mu            sync.RWMutex
  entries       map[string]*CacheEntry
  maxMemory     int64
  currentMemory int64
  lruOrder      *list.List // doubly-linked list
  positions     map[string]*list.Element
}

func (c *LRUCache) Set(key string, value interface{}) error {
  c.mu.Lock()
  defer c.mu.Unlock()

  size := estimateSize(value)

  // Check memory pressure
  for c.currentMemory+size > c.maxMemory && len(c.entries) > 0 {
    c.evictLRU()
  }

  // Store entry
  c.entries[key] = &CacheEntry{
    Data:      value,
    ExpiresAt: time.Now().Add(c.ttl),
  }
  c.currentMemory += size

  // Update LRU order
  c.updateLRUOrder(key)

  return nil
}
```

---

## Part 6: Testing Strategy

### Unit Tests

**Frontend:**
- LRU cache eviction logic
- Adaptive TTL calculation
- Cache invalidation patterns
- Store state transitions

**Backend:**
- Memory pressure handling
- Cache invalidation cascades
- TTL decay logic
- Concurrent access safety

### Integration Tests

- Frontend query caching + React Query integration
- Backend Redis + in-memory fallback
- End-to-end cache invalidation workflows
- Cache warming effectiveness

### Performance Tests

- Benchmark cache operations (get/set/delete)
- Memory usage under load
- Invalidation cascade performance
- Hit ratio under realistic workloads

### Metrics Tests

- Counter increments on hits/misses
- Memory usage tracking accuracy
- Invalidation pattern matching

---

## Part 7: Monitoring & Observability

### Key Metrics

**Frontend:**
```
Cache:
  - react_query_hits_total
  - react_query_misses_total
  - react_query_hit_ratio
  - memory_cache_size_bytes
  - memory_cache_entries_count
```

**Backend:**
```
Graph Cache:
  - graph_cache_hits_total
  - graph_cache_misses_total
  - graph_cache_evictions_total
  - graph_cache_memory_bytes
  - graph_cache_invalidations_total
```

### Dashboards

1. **Cache Health Dashboard**
   - Hit ratio trends
   - Memory usage trends
   - Entry count by type
   - Eviction rates

2. **Performance Dashboard**
   - Query latency with/without cache
   - Compute time saved by caching
   - Total response time breakdown

3. **Invalidation Dashboard**
   - Invalidation frequency by type
   - Cascade depth analysis
   - Redis operation counts

---

## Part 8: Configuration Reference

### Frontend Configuration

```typescript
// .env
VITE_CACHE_MAX_ENTRIES=100
VITE_CACHE_TTL_STATIC=600000      // 10 minutes
VITE_CACHE_TTL_DYNAMIC=30000      // 30 seconds
VITE_CACHE_TTL_GRAPH=300000       // 5 minutes
VITE_ADAPTIVE_CACHE_ENABLED=true
```

### Backend Configuration

```go
// config/cache.go
type CacheConfig struct {
  Enabled           bool          // Enable caching
  MaxMemory         int64         // Max memory bytes (256MB default)
  DefaultTTL        time.Duration // Default TTL (5 min default)
  CleanupInterval   time.Duration // Cleanup run interval (1 min)
  EnableRedis       bool          // Enable Redis backing
  RedisURL          string        // Redis connection
  MetricsEnabled    bool          // Enable metrics collection
}
```

---

## Part 9: Migration Guide

### For Existing Queries

**Before:**
```typescript
useQuery({
  queryKey: ['graph', projectId],
  queryFn: () => fetchGraph(projectId),
  staleTime: 5 * 60 * 1000,
})
```

**After:**
```typescript
useQuery({
  queryKey: ['graph', projectId],
  queryFn: () => fetchGraph(projectId),
  ...QUERY_CONFIGS.graph,  // Uses adaptive settings
})
```

### For Cache Invalidation

**Before:**
```typescript
queryClient.invalidateQueries({ queryKey: ['graph'] })
```

**After:**
```typescript
graphCacheStore.invalidateByProject(projectId)
queryClient.invalidateQueries({
  queryKey: ['graph', projectId],
  exact: true
})
```

---

## Part 10: Success Criteria

### Performance Targets
- Cache hit ratio: > 50% (initially > 40%)
- Query latency reduction: 30-40% for cached queries
- Memory overhead: < 5% of heap

### Reliability Targets
- Cache consistency: 100% (no stale data bugs)
- Invalidation accuracy: 99.9%
- Cache availability: 99.95%

### Monitoring Targets
- Metrics collection overhead: < 1%
- Alert accuracy: > 95%
- MTTR for cache issues: < 5 min

---

## Conclusion

This comprehensive caching strategy provides a foundation for significant performance improvements through:

1. **Adaptive caching** that adjusts to data characteristics
2. **Granular invalidation** that maintains consistency
3. **Memory management** preventing runaway usage
4. **Comprehensive monitoring** enabling continuous optimization

By implementing these strategies incrementally, we can achieve 30-40% improvements in query latency while maintaining 100% data consistency.
