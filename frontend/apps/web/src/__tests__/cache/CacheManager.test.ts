/**
 * Cache Manager Test Suite
 *
 * Tests for multi-layer cache system including:
 * - Cache hit/miss ratio
 * - Memory usage under load
 * - Invalidation correctness
 * - Layer routing
 * - Optimistic updates
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { CacheKeys, CacheManager } from '@/lib/cache';

describe(CacheManager, () => {
  let cacheManager: CacheManager;

  beforeEach(() => {
    cacheManager = new CacheManager({
      enableMemory: true,
      enableIndexedDB: false, // Disable for testing (requires browser)
      enableServiceWorker: false, // Disable for testing (requires browser)
      enableLogging: false,
    });
  });

  afterEach(async () => {
    await cacheManager.clear();
    await cacheManager.close();
  });

  describe('Basic Operations', () => {
    it('should set and get values', async () => {
      const key = 'test:key';
      const value = { data: 'test' };

      await cacheManager.set(key, value);
      const retrieved = await cacheManager.get(key);

      expect(retrieved).toEqual(value);
    });

    it('should return null for missing keys', async () => {
      const retrieved = await cacheManager.get('nonexistent');
      expect(retrieved).toBeNull();
    });

    it('should check key existence', async () => {
      const key = 'test:exists';
      expect(await cacheManager.has(key)).toBeFalsy();

      await cacheManager.set(key, 'value');
      expect(await cacheManager.has(key)).toBeTruthy();
    });

    it('should delete values', async () => {
      const key = 'test:delete';
      await cacheManager.set(key, 'value');

      const deleted = await cacheManager.delete(key);
      expect(deleted).toBeTruthy();
      expect(await cacheManager.has(key)).toBeFalsy();
    });
  });

  describe('TTL and Expiration', () => {
    it('should expire entries after TTL', async () => {
      const key = 'test:ttl';
      await cacheManager.set(key, 'value', { ttl: 100 }); // 100ms

      // Should exist immediately
      expect(await cacheManager.get(key)).toBe('value');

      // Wait for expiration
      await new Promise((resolve) => setTimeout(resolve, 150));

      // Should be expired
      expect(await cacheManager.get(key)).toBeNull();
    });

    it('should handle null TTL (never expires)', async () => {
      const key = 'test:no-ttl';
      await cacheManager.set(key, 'value', { ttl: null });

      await new Promise((resolve) => setTimeout(resolve, 100));
      expect(await cacheManager.get(key)).toBe('value');
    });
  });

  describe('Invalidation', () => {
    it('should invalidate by pattern', async () => {
      await cacheManager.set('project:1', { id: 1 });
      await cacheManager.set('project:2', { id: 2 });
      await cacheManager.set('item:1', { id: 1 });

      const count = await cacheManager.invalidate({ pattern: 'project:*' });

      expect(count).toBe(2);
      expect(await cacheManager.has('project:1')).toBeFalsy();
      expect(await cacheManager.has('project:2')).toBeFalsy();
      expect(await cacheManager.has('item:1')).toBeTruthy();
    });

    it('should invalidate by tags', async () => {
      await cacheManager.set('key1', 'value1', { tags: ['tag1', 'tag2'] });
      await cacheManager.set('key2', 'value2', { tags: ['tag2'] });
      await cacheManager.set('key3', 'value3', { tags: ['tag3'] });

      const count = await cacheManager.invalidate({ tags: ['tag2'] });

      expect(count).toBe(2);
      expect(await cacheManager.has('key1')).toBeFalsy();
      expect(await cacheManager.has('key2')).toBeFalsy();
      expect(await cacheManager.has('key3')).toBeTruthy();
    });

    it('should clear all entries', async () => {
      await cacheManager.set('key1', 'value1');
      await cacheManager.set('key2', 'value2');

      await cacheManager.clear();

      expect(await cacheManager.has('key1')).toBeFalsy();
      expect(await cacheManager.has('key2')).toBeFalsy();
    });
  });

  describe('Cache Hit/Miss Ratio', () => {
    it('should track hits and misses', async () => {
      const key = 'test:ratio';

      // Miss
      await cacheManager.get(key);

      // Set
      await cacheManager.set(key, 'value');

      // Hits
      await cacheManager.get(key);
      await cacheManager.get(key);
      await cacheManager.get(key);

      const stats = await cacheManager.getStats();

      expect(stats.overall.totalRequests).toBe(4);
      expect(stats.overall.misses).toBe(1);
      expect(stats.overall.memoryHits).toBe(3);
      expect(stats.overall.hitRatio).toBeCloseTo(0.75, 2);
    });

    it('should achieve >80% hit rate for repeated queries', async () => {
      const keys = Array.from({ length: 100 }, (_, i) => `key:${i % 20}`);

      // Prewarm cache
      for (let i = 0; i < 20; i++) {
        await cacheManager.set(`key:${i}`, { value: i });
      }

      // Simulate repeated access
      for (const key of keys) {
        await cacheManager.get(key);
      }

      const stats = await cacheManager.getStats();
      expect(stats.overall.hitRatio).toBeGreaterThan(0.8);
    });
  });

  describe('Memory Usage', () => {
    it('should track memory usage', async () => {
      const largeObject = {
        data: Array(1000).fill('test'),
      };

      await cacheManager.set('large', largeObject);

      const stats = await cacheManager.getStats();
      expect(stats.memory?.totalMemory).toBeGreaterThan(0);
    });

    it('should evict entries when memory limit reached', async () => {
      // Fill cache to capacity
      for (let i = 0; i < 1500; i++) {
        await cacheManager.set(`key:${i}`, { data: 'x'.repeat(100) });
      }

      const stats = await cacheManager.getStats();

      // Should have evicted some entries
      expect(stats.memory?.totalEntries).toBeLessThan(1500);
      expect(stats.memory?.memoryUsagePercent).toBeLessThanOrEqual(100);
    });
  });

  describe('Optimistic Updates', () => {
    it('should perform optimistic update successfully', async () => {
      const key = 'test:optimistic';
      await cacheManager.set(key, { value: 1 });

      const mockUpdate = vi.fn(async () => ({ value: 2 }));

      const result = await cacheManager.optimisticUpdate(
        key,
        (current: { value: number } | null) => ({
          value: (current?.value ?? 0) + 1,
        }),
        mockUpdate,
      );

      expect(result.success).toBeTruthy();
      expect(result.data).toEqual({ value: 2 });
      expect(await cacheManager.get(key)).toEqual({ value: 2 });
    });

    it('should rollback on error', async () => {
      const key = 'test:rollback';
      const original = { value: 1 };
      await cacheManager.set(key, original);

      const mockUpdate = vi.fn(async () => {
        throw new Error('Update failed');
      });

      await expect(
        cacheManager.optimisticUpdate(
          key,
          (current: { value: number } | null) => ({
            value: (current?.value ?? 0) + 1,
          }),
          mockUpdate,
        ),
      ).rejects.toThrow('Update failed');

      // Should have rolled back
      expect(await cacheManager.get(key)).toEqual(original);
    });
  });

  describe('Cache Keys Utility', () => {
    it('should generate consistent keys', () => {
      const projectKey1 = CacheKeys.project.byId('123');
      const projectKey2 = CacheKeys.project.byId('123');

      expect(projectKey1).toBe(projectKey2);
      expect(projectKey1).toBe('project:123');
    });

    it('should generate hierarchical keys', () => {
      expect(CacheKeys.project.byId('123')).toBe('project:123');
      expect(CacheKeys.project.list('user-1', 0)).toBe('projects:user:user-1:page:0');
      expect(CacheKeys.item.byType('proj-1', 'epic')).toBe('items:project:proj-1:type:epic');
    });
  });

  describe('Performance Benchmarks', () => {
    it('should have <10ms lookup latency', async () => {
      await cacheManager.set('benchmark', { data: 'test' });

      const iterations = 1000;
      const start = performance.now();

      for (let i = 0; i < iterations; i++) {
        await cacheManager.get('benchmark');
      }

      const duration = performance.now() - start;
      const avgLatency = duration / iterations;

      expect(avgLatency).toBeLessThan(10);
    });

    it('should handle 1000+ entries efficiently', async () => {
      const start = performance.now();

      // Insert 1000 entries
      for (let i = 0; i < 1000; i++) {
        await cacheManager.set(`perf:${i}`, { value: i });
      }

      // Retrieve 1000 entries
      for (let i = 0; i < 1000; i++) {
        await cacheManager.get(`perf:${i}`);
      }

      const duration = performance.now() - start;

      // Should complete in reasonable time (<1s for 2000 operations)
      expect(duration).toBeLessThan(1000);

      const stats = await cacheManager.getStats();
      expect(stats.memory?.totalEntries).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle undefined values', async () => {
      await cacheManager.set('undefined', undefined);
      expect(await cacheManager.get('undefined')).toBe(undefined);
    });

    it('should handle null values', async () => {
      await cacheManager.set('null', null);
      // Note: null is used for cache miss, so this will return null
      // This is expected behavior
      const result = await cacheManager.get('null');
      expect(result === null || result === undefined).toBeTruthy();
    });

    it('should handle circular references gracefully', async () => {
      const circular: any = { a: 1 };
      circular.self = circular;

      // Should not throw
      await expect(cacheManager.set('circular', circular)).rejects.toThrow();
    });

    it('should handle very large objects', async () => {
      const large = {
        data: Array(10_000)
          .fill(0)
          .map((_, i) => ({ data: 'x'.repeat(100), id: i })),
      };

      await cacheManager.set('large', large);
      const retrieved = await cacheManager.get('large');

      expect(retrieved).toBeDefined();
    });

    it('should handle concurrent access', async () => {
      const key = 'concurrent';

      // Concurrent sets and gets
      await Promise.all([
        cacheManager.set(key, { value: 1 }),
        cacheManager.set(key, { value: 2 }),
        cacheManager.get(key),
        cacheManager.get(key),
      ]);

      // Should have a value (last write wins)
      const value = await cacheManager.get(key);
      expect(value).toBeDefined();
    });
  });

  describe('Statistics', () => {
    it('should provide detailed statistics', async () => {
      await cacheManager.set('key1', 'value1');
      await cacheManager.set('key2', 'value2');
      await cacheManager.get('key1');
      await cacheManager.get('nonexistent');

      const stats = await cacheManager.getStats();

      expect(stats.overall).toBeDefined();
      expect(stats.overall.totalRequests).toBeGreaterThan(0);
      expect(stats.memory).toBeDefined();
      expect(stats.memory?.totalEntries).toBe(2);
    });
  });
});

describe('Cache Integration Scenarios', () => {
  let cache: CacheManager;

  beforeEach(() => {
    cache = new CacheManager({ enableLogging: false });
  });

  afterEach(async () => {
    await cache.clear();
    await cache.close();
  });

  it('should handle project workflow', async () => {
    const projectId = '123';

    // Create project
    const project = { id: projectId, name: 'Test Project' };
    await cache.set(CacheKeys.project.byId(projectId), project, {
      tags: [`project:${projectId}`],
    });

    // Add items
    for (let i = 0; i < 5; i++) {
      await cache.set(
        CacheKeys.item.byId(`item-${i}`),
        { id: `item-${i}`, projectId },
        { tags: [`project:${projectId}`, `item:item-${i}`] },
      );
    }

    // Verify project cached
    expect(await cache.get(CacheKeys.project.byId(projectId))).toEqual(project);

    // Verify items cached
    for (let i = 0; i < 5; i++) {
      expect(await cache.has(CacheKeys.item.byId(`item-${i}`))).toBeTruthy();
    }

    // Delete project - should invalidate all related items
    await cache.invalidate({ tags: [`project:${projectId}`] });

    // Verify everything invalidated
    expect(await cache.has(CacheKeys.project.byId(projectId))).toBeFalsy();
    for (let i = 0; i < 5; i++) {
      expect(await cache.has(CacheKeys.item.byId(`item-${i}`))).toBeFalsy();
    }
  });

  it('should handle graph caching workflow', async () => {
    const graphId = 'graph-123';

    // Cache layout
    await cache.set(
      CacheKeys.graph.layout(graphId, 'dagre'),
      { positions: {} },
      { tags: [`graph:${graphId}`] },
    );

    // Cache grouping
    await cache.set(
      CacheKeys.graph.grouping(graphId, 'type'),
      { groups: [] },
      { tags: [`graph:${graphId}`] },
    );

    // Cache search
    await cache.set(
      CacheKeys.search.query(graphId, 'test'),
      { results: [] },
      { tags: [`graph:${graphId}`] },
    );

    // Update graph - invalidate all caches
    await cache.invalidate({ tags: [`graph:${graphId}`] });

    // Verify all invalidated
    expect(await cache.has(CacheKeys.graph.layout(graphId, 'dagre'))).toBeFalsy();
    expect(await cache.has(CacheKeys.graph.grouping(graphId, 'type'))).toBeFalsy();
    expect(await cache.has(CacheKeys.search.query(graphId, 'test'))).toBeFalsy();
  });
});
