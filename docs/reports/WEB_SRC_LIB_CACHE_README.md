# Multi-Layer Cache System

Comprehensive caching solution with multiple storage backends, intelligent routing, and automatic invalidation.

## Quick Start

```typescript
import { getCacheManager, CacheKeys, TTL } from '@/lib/cache';

const cache = getCacheManager();

// Set value
await cache.set(CacheKeys.project.byId('123'), projectData, {
  ttl: TTL.MEDIUM,
  tags: ['project:123'],
});

// Get value
const project = await cache.get(CacheKeys.project.byId('123'));

// Invalidate
await cache.invalidate({ pattern: 'project:*' });
```

## Architecture

```
┌─────────────────────────────────────────────┐
│           Cache Manager                      │
│    (Unified Interface & Routing)            │
├──────────┬─────────────┬──────────────────┤
│ Memory   │ IndexedDB   │ Service Worker   │
│ (LRU)    │ (Large)     │ (API Responses)  │
└──────────┴─────────────┴──────────────────┘
```

## Cache Layers

### Memory Cache

- **Best for**: Small, frequently accessed data (<100KB)
- **Speed**: Sub-millisecond
- **Capacity**: 50MB default
- **Persistence**: No

### IndexedDB Cache

- **Best for**: Large datasets (>100KB, <5MB)
- **Speed**: 1-5ms
- **Capacity**: 50-100MB
- **Persistence**: Yes

### Service Worker Cache

- **Best for**: API responses, offline support
- **Speed**: Network-dependent
- **Capacity**: 50-100MB
- **Persistence**: Yes

## TTL Presets

```typescript
TTL.SHORT; // 5 minutes
TTL.MEDIUM; // 1 hour
TTL.LONG; // 24 hours
TTL.WEEK; // 7 days
TTL.NEVER; // Never expires
```

## Key Generators

```typescript
CacheKeys.project.byId('123'); // 'project:123'
CacheKeys.project.list('user-1', 0); // 'projects:user:user-1:page:0'
CacheKeys.item.byId('456'); // 'item:456'
CacheKeys.item.list('project-123', 0); // 'items:project:project-123:page:0'
CacheKeys.graph.layout('graph-1', 'dagre'); // 'graph:graph-1:layout:dagre'
CacheKeys.search.query('project-123', 'test'); // 'search:project-123:test'
```

## Invalidation

### By Pattern

```typescript
// Wildcard matching
await cache.invalidate({ pattern: 'project:*' });
await cache.invalidate({ pattern: 'item:project:123:*' });
```

### By Tags

```typescript
// Set with tags
await cache.set(key, value, {
  tags: ['project:123', 'user:456'],
});

// Invalidate by tag
await cache.invalidate({ tags: ['project:123'] });
```

### Clear All

```typescript
await cache.clear();
```

## Optimistic Updates

```typescript
const { success, data, rollback } = await cache.optimisticUpdate(
  CacheKeys.item.byId(itemId),
  (current) => ({ ...current, title: 'New Title' }),
  async () => await api.updateItem(itemId, { title: 'New Title' }),
);

if (!success) {
  console.error('Update failed, rolled back');
}
```

## React Hook Example

```typescript
import { useEffect, useState } from 'react';
import { getCacheManager, CacheKeys, TTL } from '@/lib/cache';

function useProject(projectId: string) {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const cache = getCacheManager();

      // Try cache
      const cached = await cache.get(CacheKeys.project.byId(projectId));
      if (cached) {
        setProject(cached);
        setLoading(false);
        return;
      }

      // Fetch from API
      const data = await api.getProject(projectId);
      setProject(data);
      setLoading(false);

      // Store in cache
      await cache.set(CacheKeys.project.byId(projectId), data, {
        ttl: TTL.MEDIUM,
        tags: [`project:${projectId}`],
      });
    }

    load();
  }, [projectId]);

  return { project, loading };
}
```

## Monitoring

```typescript
// Get statistics
const stats = await cache.getStats();

console.log('Hit Ratio:', stats.overall.hitRatio);
console.log('Memory Usage:', stats.memory?.memoryUsagePercent);
console.log('Total Entries:', stats.memory?.totalEntries);
```

## Development Utilities

```typescript
import { dev } from '@/lib/cache';

// Clear all caches
await dev.clearAll();

// Print statistics
await dev.printStats();

// List cached keys
await dev.listKeys('project:*');

// Simulate load test
await dev.simulateLoad(1000);
```

## Performance Targets

- ✅ Cache hit rate: >80%
- ✅ Backend load reduction: >60%
- ✅ Lookup latency: <10ms
- ✅ Memory usage: <100MB per user

## API Reference

See [Caching Strategy Guide](../../../../../docs/guides/caching-strategy-guide.md) for complete documentation.

## Files

- `CacheInterface.ts` - Core types and interfaces
- `MemoryCache.ts` - In-memory LRU cache
- `IndexedDBCache.ts` - Browser persistent storage
- `ServiceWorkerCache.ts` - Network caching
- `CacheManager.ts` - Unified orchestrator
- `index.ts` - Public exports

## Testing

```bash
# Run cache tests
npm test -- cache

# With coverage
npm test -- cache --coverage
```

## Backend Integration

See `backend/internal/cache/` for Redis cache implementation and HTTP middleware.

---

For detailed documentation, see [Caching Strategy Guide](../../../../../docs/guides/caching-strategy-guide.md).
