import * as Vitest from 'vitest';

import {
  cacheKeys,
  clearAllCaches,
  createGraphCache,
  groupingCache,
  layoutCache,
  searchCache,
  useGraphCache,
} from '@/lib/graphCache';
Vitest.describe('Graph Cache - LRU Implementation', () => {
  Vitest.describe('Cache Creation', () => {
    Vitest.it('should create a new cache with default settings', () => {
      const cache = createGraphCache();
      const stats = cache.getStats();

      Vitest.expect(stats.totalEntries).toBe(0);
      Vitest.expect(stats.maxEntries).toBe(100);
      Vitest.expect(stats.totalMemory).toBe(0);
    });

    Vitest.it('should create a cache with custom settings', () => {
      const cache = createGraphCache(50, 10_485_760); // 50 entries, 10 MB
      const stats = cache.getStats();

      Vitest.expect(stats.maxEntries).toBe(50);
      Vitest.expect(stats.maxMemory).toBe(10_485_760);
    });
  });

  Vitest.describe('Basic Operations', () => {
    let cache: ReturnType<typeof createGraphCache>;

    Vitest.beforeEach(() => {
      cache = createGraphCache();
    });

    Vitest.it('should set and get values', () => {
      const value = { data: 'test' };
      cache.set('key1', value);

      const retrieved = cache.get('key1');
      Vitest.expect(retrieved).toEqual(value);
    });

    Vitest.it('should return null for non-existent keys', () => {
      const result = cache.get('non-existent');
      Vitest.expect(result).toBeNull();
    });

    Vitest.it('should check key existence', () => {
      cache.set('key1', { data: 'test' });

      Vitest.expect(cache.has('key1')).toBeTruthy();
      Vitest.expect(cache.has('key2')).toBeFalsy();
    });

    Vitest.it('should delete entries', () => {
      cache.set('key1', { data: 'test' });
      Vitest.expect(cache.has('key1')).toBeTruthy();

      const deleted = cache.delete('key1');
      Vitest.expect(deleted).toBeTruthy();
      Vitest.expect(cache.has('key1')).toBeFalsy();
    });

    Vitest.it('should return false when deleting non-existent key', () => {
      const deleted = cache.delete('non-existent');
      Vitest.expect(deleted).toBeFalsy();
    });

    Vitest.it('should clear all entries', () => {
      cache.set('key1', { data: 'test1' });
      cache.set('key2', { data: 'test2' });
      Vitest.expect(cache.getStats().totalEntries).toBe(2);

      cache.clear();
      Vitest.expect(cache.getStats().totalEntries).toBe(0);
      Vitest.expect(cache.get('key1')).toBeNull();
    });
  });

  Vitest.describe('LRU Eviction', () => {
    Vitest.it('should evict least recently used entries when max entries exceeded', () => {
      const cache = createGraphCache(3); // Max 3 entries

      cache.set('key1', { data: 'value1' });
      cache.set('key2', { data: 'value2' });
      cache.set('key3', { data: 'value3' });

      // Add 4th entry - should evict key1 (least recently used)
      cache.set('key4', { data: 'value4' });

      Vitest.expect(cache.has('key1')).toBeFalsy();
      Vitest.expect(cache.has('key4')).toBeTruthy();
    });

    Vitest.it('should not evict recently accessed entries', () => {
      const cache = createGraphCache(3);

      cache.set('key1', { data: 'value1' });
      cache.set('key2', { data: 'value2' });
      cache.set('key3', { data: 'value3' });

      // Access key1 to make it recently used
      cache.get('key1');

      // Add 4th entry - should evict key2
      cache.set('key4', { data: 'value4' });

      Vitest.expect(cache.has('key1')).toBeTruthy(); // Recently accessed
      Vitest.expect(cache.has('key2')).toBeFalsy(); // Evicted
    });

    Vitest.it('should respect memory limits', () => {
      const cache = createGraphCache(1000, 1024); // 1 KB limit

      const largeObject = {
        data: 'x'.repeat(500), // ~1KB
      };

      cache.set('key1', largeObject);
      Vitest.expect(cache.getStats().totalEntries).toBe(1);

      // This should trigger eviction
      cache.set('key2', largeObject);
      Vitest.expect(cache.getStats().totalEntries).toBeLessThanOrEqual(1);
    });
  });

  Vitest.describe('Statistics', () => {
    let cache: ReturnType<typeof createGraphCache>;

    Vitest.beforeEach(() => {
      cache = createGraphCache();
    });

    Vitest.it('should track hit and miss counts', () => {
      cache.set('key1', { data: 'test' });

      cache.get('key1'); // Hit
      cache.get('key1'); // Hit
      cache.get('key2'); // Miss

      const stats = cache.getStats();
      Vitest.expect(stats.totalHits).toBe(2);
      Vitest.expect(stats.totalMisses).toBe(1);
    });

    Vitest.it('should calculate hit ratio correctly', () => {
      cache.set('key1', { data: 'test' });

      cache.get('key1'); // Hit
      cache.get('key1'); // Hit
      cache.get('key2'); // Miss
      cache.get('key2'); // Miss

      const stats = cache.getStats();
      Vitest.expect(stats.hitRatio).toBe(0.5); // 2 hits / 4 total
    });

    Vitest.it('should report cache statistics', () => {
      cache.set('key1', { data: 'test' });
      cache.set('key2', { data: 'test' });

      const stats = cache.getStats();

      Vitest.expect(stats.totalEntries).toBe(2);
      Vitest.expect(stats.maxEntries).toBe(100);
      Vitest.expect(stats.totalMemory).toBeGreaterThan(0);
      Vitest.expect(stats.memoryUsagePercent).toBeGreaterThan(0);
      Vitest.expect(stats.oldestEntry).not.toBeNull();
      Vitest.expect(stats.newestEntry).not.toBeNull();
    });

    Vitest.it('should categorize entries by size', () => {
      const tinyData = { data: 'x' };
      const smallData = { data: 'x'.repeat(100) };

      cache.set('tiny', tinyData);
      cache.set('small', smallData);

      const stats = cache.getStats();
      Vitest.expect(stats.entriesBySize.tiny).toBeGreaterThan(0);
    });

    Vitest.it('should reset statistics', () => {
      cache.set('key1', { data: 'test' });
      cache.get('key1');
      cache.get('key1');

      const statsBefore = cache.getStats();
      Vitest.expect(statsBefore.totalHits).toBe(2);

      cache.resetStats();

      const statsAfter = cache.getStats();
      Vitest.expect(statsAfter.totalHits).toBe(0);
      Vitest.expect(statsAfter.totalMisses).toBe(0);
    });
  });

  Vitest.describe('Pattern-Based Invalidation', () => {
    let cache: ReturnType<typeof createGraphCache>;

    Vitest.beforeEach(() => {
      cache = createGraphCache();
    });

    Vitest.it('should invalidate entries by prefix pattern', () => {
      cache.set('layout:graph1:force', { data: 'test1' });
      cache.set('layout:graph1:circle', { data: 'test2' });
      cache.set('grouping:graph1:strategy', { data: 'test3' });

      const count = cache.invalidatePattern('layout:*');

      Vitest.expect(count).toBe(2);
      Vitest.expect(cache.has('layout:graph1:force')).toBeFalsy();
      Vitest.expect(cache.has('grouping:graph1:strategy')).toBeTruthy();
    });

    Vitest.it('should support wildcard patterns', () => {
      cache.set('layout:graph1', { data: 'test1' });
      cache.set('layout:graph2', { data: 'test2' });
      cache.set('search:graph1', { data: 'test3' });

      const count = cache.invalidatePattern('layout:*');

      Vitest.expect(count).toBe(2);
      Vitest.expect(cache.has('search:graph1')).toBeTruthy();
    });

    Vitest.it('should return count of invalidated entries', () => {
      cache.set('key1', { data: 'test' });
      cache.set('key2', { data: 'test' });
      cache.set('key3', { data: 'test' });

      const count = cache.invalidatePattern('key*');

      Vitest.expect(count).toBe(3);
    });

    Vitest.it('should find keys matching pattern', () => {
      cache.set('layout:graph1:force', { data: 'test1' });
      cache.set('layout:graph1:circle', { data: 'test2' });
      cache.set('layout:graph2:force', { data: 'test3' });

      const keys = cache.keysMatching('layout:graph1:*');

      Vitest.expect(keys).toHaveLength(2);
      Vitest.expect(keys).toContain('layout:graph1:force');
      Vitest.expect(keys).toContain('layout:graph1:circle');
    });
  });

  Vitest.describe('Prewarming', () => {
    let cache: ReturnType<typeof createGraphCache>;

    Vitest.beforeEach(() => {
      cache = createGraphCache();
    });

    Vitest.it('should bulk load entries', () => {
      const entries: [string, unknown][] = [
        ['key1', { data: 'value1' }],
        ['key2', { data: 'value2' }],
        ['key3', { data: 'value3' }],
      ];

      cache.prewarm(entries);

      Vitest.expect(cache.getStats().totalEntries).toBe(3);
      Vitest.expect(cache.get('key1')).toEqual({ data: 'value1' });
      Vitest.expect(cache.get('key2')).toEqual({ data: 'value2' });
    });

    Vitest.it('should handle empty prewarm array', () => {
      cache.prewarm([]);

      Vitest.expect(cache.getStats().totalEntries).toBe(0);
    });
  });

  Vitest.describe('Memory Pressure', () => {
    Vitest.it('should report comfortable pressure when below 70%', () => {
      const cache = createGraphCache(100, 1024); // 1 KB limit
      cache.set('key1', { data: 'x' });

      const pressure = cache.getMemoryPressure();
      Vitest.expect(pressure).toBe('comfortable');
    });

    Vitest.it('should report caution pressure between 70-85%', () => {
      const cache = createGraphCache(100, 100); // 100 bytes limit
      const largeObject = { data: 'x'.repeat(50) }; // ~50 bytes

      cache.set('key1', largeObject);
      cache.set('key2', largeObject);

      const pressure = cache.getMemoryPressure();
      Vitest.expect(['caution', 'critical']).toContain(pressure);
    });

    Vitest.it('should report critical pressure above 85%', () => {
      const cache = createGraphCache(100, 100);
      const largeObject = { data: 'x'.repeat(100) };

      cache.set('key1', largeObject);

      const pressure = cache.getMemoryPressure();
      Vitest.expect(pressure).toBe('critical');
    });
  });

  Vitest.describe('Global Cache Instances', () => {
    Vitest.afterEach(() => {
      clearAllCaches();
    });

    Vitest.it('should have layout cache instance', () => {
      layoutCache.set('test', {
        positions: {},
        bounds: { minX: 0, minY: 0, maxX: 100, maxY: 100 },
      });

      const stats = layoutCache.getStats();
      Vitest.expect(stats.totalEntries).toBeGreaterThan(0);
    });

    Vitest.it('should have grouping cache instance', () => {
      groupingCache.set('test', {
        groupId: 'g1',
        items: ['item1'],
      });

      const stats = groupingCache.getStats();
      Vitest.expect(stats.totalEntries).toBeGreaterThan(0);
    });

    Vitest.it('should have search cache instance', () => {
      searchCache.set('test', {
        query: 'test',
        results: [],
        timestamp: Date.now(),
      });

      const stats = searchCache.getStats();
      Vitest.expect(stats.totalEntries).toBeGreaterThan(0);
    });
  });

  Vitest.describe('Clear All Caches', () => {
    Vitest.it('should clear all global caches', () => {
      layoutCache.set('key1', {
        positions: {},
        bounds: { minX: 0, minY: 0, maxX: 100, maxY: 100 },
      });
      groupingCache.set('key2', {
        groupId: 'g1',
        items: ['item1'],
      });

      clearAllCaches();

      Vitest.expect(layoutCache.getStats().totalEntries).toBe(0);
      Vitest.expect(groupingCache.getStats().totalEntries).toBe(0);
    });
  });

  Vitest.describe('Cache Key Generators', () => {
    Vitest.it('should generate layout cache keys', () => {
      const key = cacheKeys.layout('graph1', 'force-directed');
      Vitest.expect(key).toBe('layout:graph1:force-directed');
    });

    Vitest.it('should generate grouping cache keys', () => {
      const key = cacheKeys.grouping('graph1', 'hierarchical');
      Vitest.expect(key).toBe('grouping:graph1:hierarchical');
    });

    Vitest.it('should generate search cache keys', () => {
      const key = cacheKeys.search('graph1', 'query');
      Vitest.expect(key).toBe('search:graph1:query');
    });

    Vitest.it('should generate pathfinding cache keys', () => {
      const key = cacheKeys.pathfinding('node1', 'node2');
      Vitest.expect(key).toBe('path:node1:node2');
    });

    Vitest.it('should generate aggregation cache keys', () => {
      const key = cacheKeys.aggregation('sum', 'param1:value1');
      Vitest.expect(key).toBe('agg:sum:param1:value1');
    });
  });

  Vitest.describe('useGraphCache Hook', () => {
    Vitest.beforeEach(() => {
      clearAllCaches();
    });

    Vitest.it('should provide cache operations', () => {
      const cache = useGraphCache();

      Vitest.expect(cache.layoutCache).toBeDefined();
      Vitest.expect(cache.groupingCache).toBeDefined();
      Vitest.expect(cache.searchCache).toBeDefined();
      Vitest.expect(cache.getStats).toBeDefined();
    });

    Vitest.it('should get statistics for all caches', () => {
      const cache = useGraphCache();

      layoutCache.set('key1', {
        positions: {},
        bounds: { minX: 0, minY: 0, maxX: 100, maxY: 100 },
      });

      const stats = cache.getStats();

      Vitest.expect(stats.layout).toBeDefined();
      Vitest.expect(stats.grouping).toBeDefined();
      Vitest.expect(stats.search).toBeDefined();
      Vitest.expect(stats.total).toBeDefined();
    });
  });

  Vitest.describe('Edge Cases', () => {
    Vitest.it('should handle null values', () => {
      const cache = createGraphCache();
      cache.set('nullKey', null);

      Vitest.expect(cache.get('nullKey')).toBeNull();
    });

    Vitest.it('should handle undefined values', () => {
      const cache = createGraphCache();
      cache.set('undefinedKey', undefined);

      Vitest.expect(cache.get('undefinedKey')).toBeUndefined();
    });

    Vitest.it('should handle circular references without infinite loops', () => {
      const cache = createGraphCache();
      const obj: { data: string } = { data: 'test' };
      obj.self = obj;

      // Should not throw
      Vitest.expect(() => {
        cache.set('circularKey', obj);
      }).not.toThrow();
    });

    Vitest.it('should handle very long cache keys', () => {
      const cache = createGraphCache();
      const longKey = 'key'.repeat(100);

      cache.set(longKey, { data: 'test' });

      Vitest.expect(cache.get(longKey)).toEqual({ data: 'test' });
    });
  });
});
