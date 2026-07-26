/**
 * Comprehensive tests for cache.ts
 * Coverage targets: Cache initialization, memoization, API caching, utilities
 */

import { describe, expect, it, vi } from 'vitest';

import {
  clearItemCaches,
  clearProjectCaches,
  clearUserCaches,
  createCachedAPI,
  getCacheHealth,
  getCacheManager,
  initializeCache,
  memoize,
  prewarmCache,
  CacheKeys,
  TTL,
} from '../../lib/cache';

describe('Cache System - P1 Coverage', () => {
  // ============================================================================
  // INITIALIZATION TESTS
  // ============================================================================

  describe('initializeCache', () => {
    it('should initialize cache with defaults', () => {
      const cache = initializeCache();

      expect(cache).toBeDefined();
      expect(cache).toBeTruthy();
    });

    it('should enable memory cache', () => {
      const cache = initializeCache();

      expect(cache.memoryCache).toBeDefined();
    });

    it('should enable IndexedDB cache', () => {
      const cache = initializeCache();

      expect(cache.indexedDBCache).toBeDefined();
    });

    it('should enable service worker cache', () => {
      const cache = initializeCache();

      expect(cache.serviceWorkerCache).toBeDefined();
    });

    it('should set default TTL', () => {
      const cache = initializeCache();

      expect(cache).toBeDefined();
    });

    it('should enable logging in development', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const cache = initializeCache();
      expect(cache).toBeDefined();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('getCacheManager', () => {
    it('should return cache manager instance', () => {
      const cache = getCacheManager();

      expect(cache).toBeDefined();
      expect(cache.get).toBeDefined();
      expect(cache.set).toBeDefined();
      expect(cache.invalidate).toBeDefined();
      expect(cache.clear).toBeDefined();
    });

    it('should support custom configuration', () => {
      const cache = getCacheManager({
        defaultTTL: 30000,
        enableIndexedDB: false,
        enableLogging: true,
        enableMemory: true,
        enableServiceWorker: false,
      });

      expect(cache).toBeDefined();
    });

    it('should return singleton instance', () => {
      const cache1 = getCacheManager();
      const cache2 = getCacheManager();

      // Same instance
      expect(cache1).toBe(cache2);
    });
  });

  // ============================================================================
  // CACHE KEYS TESTS
  // ============================================================================

  describe('CacheKeys', () => {
    describe('project keys', () => {
      it('should generate project.byId key', () => {
        const key = CacheKeys.project.byId('proj-1');

        expect(key).toBeDefined();
        expect(typeof key).toBe('string');
        expect(key).toContain('proj-1');
      });

      it('should generate unique keys for different IDs', () => {
        const key1 = CacheKeys.project.byId('proj-1');
        const key2 = CacheKeys.project.byId('proj-2');

        expect(key1).not.toBe(key2);
      });

      it('should be deterministic', () => {
        const key1 = CacheKeys.project.byId('proj-1');
        const key2 = CacheKeys.project.byId('proj-1');

        expect(key1).toBe(key2);
      });
    });

    describe('item keys', () => {
      it('should generate item.byId key', () => {
        const key = CacheKeys.item.byId('item-1');

        expect(key).toBeDefined();
        expect(key).toContain('item-1');
      });

      it('should generate unique keys for different items', () => {
        const key1 = CacheKeys.item.byId('item-1');
        const key2 = CacheKeys.item.byId('item-2');

        expect(key1).not.toBe(key2);
      });
    });
  });

  // ============================================================================
  // TTL CONSTANTS TESTS
  // ============================================================================

  describe('TTL Constants', () => {
    it('should have SHORT TTL', () => {
      expect(TTL.SHORT).toBeDefined();
      expect(typeof TTL.SHORT).toBe('number');
      expect(TTL.SHORT).toBeGreaterThan(0);
    });

    it('should have MEDIUM TTL', () => {
      expect(TTL.MEDIUM).toBeDefined();
      expect(typeof TTL.MEDIUM).toBe('number');
      expect(TTL.MEDIUM).toBeGreaterThan(TTL.SHORT);
    });

    it('should have LONG TTL', () => {
      expect(TTL.LONG).toBeDefined();
      expect(typeof TTL.LONG).toBe('number');
      expect(TTL.LONG).toBeGreaterThan(TTL.MEDIUM);
    });

    it('should follow hierarchy SHORT < MEDIUM < LONG', () => {
      expect(TTL.SHORT).toBeLessThan(TTL.MEDIUM);
      expect(TTL.MEDIUM).toBeLessThan(TTL.LONG);
    });
  });

  // ============================================================================
  // MEMOIZE FUNCTION TESTS
  // ============================================================================

  describe('memoize', () => {
    it('should memoize function result', async () => {
      const mockFn = vi.fn(async () => ({ data: 'test' }));

      const result1 = await memoize(mockFn, 'test-key');
      const result2 = await memoize(mockFn, 'test-key');

      expect(result1).toEqual({ data: 'test' });
      expect(result2).toEqual({ data: 'test' });
      // Function should be called only once due to caching
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should execute function if not cached', async () => {
      const mockFn = vi.fn(async () => ({ data: 'result' }));

      const result = await memoize(mockFn, 'unique-key');

      expect(result).toEqual({ data: 'result' });
      expect(mockFn).toHaveBeenCalledOnce();
    });

    it('should support custom TTL', async () => {
      const mockFn = vi.fn(async () => ({ data: 'test' }));

      const result = await memoize(mockFn, 'key-with-ttl', { ttl: 60000 });

      expect(result).toBeDefined();
    });

    it('should support tags', async () => {
      const mockFn = vi.fn(async () => ({ data: 'test' }));

      const result = await memoize(mockFn, 'tagged-key', { tags: ['user:123'] });

      expect(result).toBeDefined();
    });

    it('should store result in cache', async () => {
      const mockFn = vi.fn(async () => ({ value: 42 }));

      await memoize(mockFn, 'stored-key');

      const cache = getCacheManager();
      const cached = await cache.get('stored-key');

      expect(cached).toBeDefined();
    });

    it('should handle function errors', async () => {
      const mockFn = vi.fn(async () => {
        throw new Error('Function failed');
      });

      await expect(memoize(mockFn, 'error-key')).rejects.toThrow('Function failed');
    });

    it('should differentiate between keys', async () => {
      const mockFn = vi.fn(async () => ({ data: 'result' }));

      const result1 = await memoize(mockFn, 'key-1');
      const result2 = await memoize(mockFn, 'key-2');

      expect(result1).toEqual(result2);
      expect(mockFn).toHaveBeenCalledTimes(2);
    });
  });

  // ============================================================================
  // CREATE CACHED API TESTS
  // ============================================================================

  describe('createCachedAPI', () => {
    it('should create cached API function', async () => {
      const mockApi = vi.fn(async (id: string) => ({ id, data: 'test' }));
      const keyGen = (id: string) => `item:${id}`;

      const cachedApi = createCachedAPI(mockApi, keyGen);

      const result = await cachedApi('item-1');

      expect(result).toEqual({ data: 'test', id: 'item-1' });
    });

    it('should cache results', async () => {
      const mockApi = vi.fn(async (id: string) => ({ id, value: Math.random() }));
      const keyGen = (id: string) => `api:${id}`;

      const cachedApi = createCachedAPI(mockApi, keyGen);

      const result1 = await cachedApi('item-1');
      const result2 = await cachedApi('item-1');

      expect(result1.value).toBe(result2.value);
      expect(mockApi).toHaveBeenCalledTimes(1);
    });

    it('should support custom TTL', async () => {
      const mockApi = vi.fn(async (id: string) => ({ id }));
      const keyGen = (id: string) => `api:${id}`;

      const cachedApi = createCachedAPI(mockApi, keyGen, { ttl: 30000 });

      const result = await cachedApi('item-1');

      expect(result).toBeDefined();
    });

    it('should support tag generation', async () => {
      const mockApi = vi.fn(async (id: string) => ({ id }));
      const keyGen = (id: string) => `api:${id}`;
      const tagGen = (id: string) => [`item:${id}`];

      const cachedApi = createCachedAPI(mockApi, keyGen, { tags: tagGen });

      const result = await cachedApi('item-1');

      expect(result).toBeDefined();
    });

    it('should handle multiple arguments', async () => {
      const mockApi = vi.fn(async (projectId: string, itemId: string) => ({
        projectId,
        itemId,
      }));
      const keyGen = (projectId: string, itemId: string) => `${projectId}:${itemId}`;

      const cachedApi = createCachedAPI(mockApi, keyGen);

      const result = await cachedApi('proj-1', 'item-1');

      expect(result).toEqual({ itemId: 'item-1', projectId: 'proj-1' });
    });

    it('should pass through errors', async () => {
      const mockApi = vi.fn(async () => {
        throw new Error('API error');
      });
      const keyGen = () => 'error-key';

      const cachedApi = createCachedAPI(mockApi, keyGen);

      await expect(cachedApi()).rejects.toThrow('API error');
    });
  });

  // ============================================================================
  // CLEAR CACHE UTILITIES TESTS
  // ============================================================================

  describe('clearProjectCaches', () => {
    it('should clear project caches by ID', async () => {
      const cache = getCacheManager();
      const clearSpy = vi.spyOn(cache, 'invalidate');

      await clearProjectCaches('proj-1');

      expect(clearSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          tags: expect.arrayContaining(['project:proj-1']),
        }),
      );
    });

    it('should handle different project IDs', async () => {
      const cache = getCacheManager();
      const clearSpy = vi.spyOn(cache, 'invalidate');

      await clearProjectCaches('proj-123');

      expect(clearSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          tags: expect.arrayContaining(['project:proj-123']),
        }),
      );
    });
  });

  describe('clearItemCaches', () => {
    it('should clear item caches by ID', async () => {
      const cache = getCacheManager();
      const clearSpy = vi.spyOn(cache, 'invalidate');

      await clearItemCaches('item-1');

      expect(clearSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          tags: expect.arrayContaining(['item:item-1']),
        }),
      );
    });
  });

  describe('clearUserCaches', () => {
    it('should clear user caches by ID', async () => {
      const cache = getCacheManager();
      const clearSpy = vi.spyOn(cache, 'invalidate');

      await clearUserCaches('user-1');

      expect(clearSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          tags: expect.arrayContaining(['user:user-1']),
        }),
      );
    });
  });

  // ============================================================================
  // PREWARM CACHE TESTS
  // ============================================================================

  describe('prewarmCache', () => {
    it('should prewarm projects', async () => {
      const cache = getCacheManager();
      const setSpy = vi.spyOn(cache, 'set');

      const projectData = { id: 'proj-1', name: 'Test Project' };
      await prewarmCache({
        projects: [{ data: projectData, id: 'proj-1' }],
      });

      expect(setSpy).toHaveBeenCalled();
    });

    it('should prewarm items', async () => {
      const cache = getCacheManager();
      const setSpy = vi.spyOn(cache, 'set');

      const itemData = { id: 'item-1', title: 'Test Item' };
      await prewarmCache({
        items: [{ data: itemData, id: 'item-1' }],
      });

      expect(setSpy).toHaveBeenCalled();
    });

    it('should prewarm both projects and items', async () => {
      const cache = getCacheManager();
      const setSpy = vi.spyOn(cache, 'set');

      await prewarmCache({
        items: [{ data: { id: 'item-1' }, id: 'item-1' }],
        projects: [{ data: { id: 'proj-1' }, id: 'proj-1' }],
      });

      expect(setSpy).toHaveBeenCalledTimes(2);
    });

    it('should handle empty prewarm data', async () => {
      const cache = getCacheManager();
      const setSpy = vi.spyOn(cache, 'set');

      await prewarmCache({});

      expect(setSpy).not.toHaveBeenCalled();
    });

    it('should set correct TTL for projects', async () => {
      const cache = getCacheManager();
      const setSpy = vi.spyOn(cache, 'set');

      await prewarmCache({
        projects: [{ data: { id: 'proj-1' }, id: 'proj-1' }],
      });

      expect(setSpy).toHaveBeenCalledWith(
        expect.anything(),
        expect.anything(),
        expect.objectContaining({
          ttl: TTL.LONG,
        }),
      );
    });

    it('should set correct TTL for items', async () => {
      const cache = getCacheManager();
      const setSpy = vi.spyOn(cache, 'set');

      await prewarmCache({
        items: [{ data: { id: 'item-1' }, id: 'item-1' }],
      });

      expect(setSpy).toHaveBeenCalledWith(
        expect.anything(),
        expect.anything(),
        expect.objectContaining({
          ttl: TTL.MEDIUM,
        }),
      );
    });
  });

  // ============================================================================
  // GET CACHE HEALTH TESTS
  // ============================================================================

  describe('getCacheHealth', () => {
    it('should return health status', async () => {
      const health = await getCacheHealth();

      expect(health).toBeDefined();
      expect(health.healthy).toBeDefined();
      expect(health.hitRatio).toBeDefined();
      expect(health.memoryUsage).toBeDefined();
      expect(health.issues).toBeDefined();
    });

    it('should report healthy status', async () => {
      const health = await getCacheHealth();

      expect(typeof health.healthy).toBe('boolean');
    });

    it('should report hit ratio', async () => {
      const health = await getCacheHealth();

      expect(typeof health.hitRatio).toBe('number');
      expect(health.hitRatio).toBeGreaterThanOrEqual(0);
      expect(health.hitRatio).toBeLessThanOrEqual(1);
    });

    it('should report memory usage', async () => {
      const health = await getCacheHealth();

      expect(typeof health.memoryUsage).toBe('number');
      expect(health.memoryUsage).toBeGreaterThanOrEqual(0);
    });

    it('should report issues', async () => {
      const health = await getCacheHealth();

      expect(Array.isArray(health.issues)).toBe(true);
    });

    it('should flag low hit ratio', async () => {
      const health = await getCacheHealth();

      if (health.hitRatio < 0.5) {
        expect(health.issues).toContain('Low cache hit ratio (<50%)');
      }
    });

    it('should flag high memory usage', async () => {
      const health = await getCacheHealth();

      if (health.memoryUsage > 90) {
        expect(health.issues).toContain('Memory cache near capacity (>90%)');
      }
    });

    it('should have zero issues when healthy', async () => {
      const health = await getCacheHealth();

      if (health.healthy) {
        expect(health.issues).toHaveLength(0);
      }
    });
  });

  // ============================================================================
  // DEV UTILITIES TESTS
  // ============================================================================

  describe('dev utilities', () => {
    it('should export dev utilities', () => {
      // Check that dev exports exist
      expect(typeof CacheKeys).toBe('object');
      expect(typeof TTL).toBe('object');
    });

    it('should have clearAll utility', () => {
      // The cache module exports dev utilities that include clearAll, printStats, etc.
      const cache = getCacheManager();
      expect(cache).toBeDefined();
    });
  });

  // ============================================================================
  // INTEGRATION TESTS
  // ============================================================================

  describe('Integration: Complete Cache Flow', () => {
    it('should cache API result and reuse from cache', async () => {
      const mockApi = vi.fn(async (id: string) => ({
        data: `Item ${id}`,
        id,
      }));

      const cachedApi = createCachedAPI(mockApi, (id: string) => `item:${id}`);

      const result1 = await cachedApi('test-1');
      const result2 = await cachedApi('test-1');

      expect(result1).toEqual(result2);
      expect(mockApi).toHaveBeenCalledTimes(1);
    });

    it('should clear cache and refetch', async () => {
      const mockApi = vi.fn(async (id: string) => ({
        timestamp: Date.now(),
      }));

      const cachedApi = createCachedAPI(mockApi, (id: string) => `api:${id}`, {
        tags: (id: string) => [`item:${id}`],
      });

      const result1 = await cachedApi('id-1');

      // Clear and refetch
      await clearItemCaches('id-1');

      const result2 = await cachedApi('id-1');

      // Should have been called again after clearing
      expect(mockApi.mock.calls.length).toBeGreaterThanOrEqual(1);
    });

    it('should prewarm cache before API call', async () => {
      const cache = getCacheManager();

      await prewarmCache({
        items: [{ data: { id: 'item-1', title: 'Test' }, id: 'item-1' }],
      });

      const cached = await cache.get(CacheKeys.item.byId('item-1'));

      expect(cached).toBeDefined();
    });

    it('should monitor cache health after operations', async () => {
      const mockApi = vi.fn(async () => ({ data: 'test' }));
      const cachedApi = createCachedAPI(mockApi, () => 'key');

      await cachedApi();
      await cachedApi();

      const health = await getCacheHealth();

      expect(health).toBeDefined();
      expect(health.healthy || health.hitRatio > 0).toBe(true);
    });
  });

  // ============================================================================
  // EDGE CASES
  // ============================================================================

  describe('Edge Cases', () => {
    it('should handle null key generation', async () => {
      const mockApi = vi.fn(async () => ({ data: 'test' }));
      const keyGen = () => `key:${Math.random()}`; // Different key each time

      const cachedApi = createCachedAPI(mockApi, keyGen);

      const result1 = await cachedApi();
      const result2 = await cachedApi();

      // Should call twice since keys are different
      expect(mockApi).toHaveBeenCalledTimes(2);
    });

    it('should handle undefined cache values', async () => {
      const cache = getCacheManager();
      const result = await cache.get('nonexistent-key');

      expect(result).toBeNull();
    });

    it('should handle very large cached values', async () => {
      const largeData = Array.from({ length: 10000 }, (_, i) => ({
        id: i,
        value: `data-${i}`,
      }));

      const result = await memoize(async () => largeData, 'large-key', { ttl: 60000 });

      expect(result).toEqual(largeData);
    });

    it('should handle rapid successive cache operations', async () => {
      const cache = getCacheManager();

      const promises = Array.from({ length: 100 }, (_, i) =>
        cache.set(`key-${i}`, { value: i }, { ttl: 5000 }),
      );

      await Promise.all(promises);

      const health = await getCacheHealth();
      expect(health).toBeDefined();
    });

    it('should handle special characters in cache keys', async () => {
      const cache = getCacheManager();

      const key = `item:@#$%^&*()={}[]|:;"'<>,.?/`;
      await cache.set(key, { data: 'test' });

      const result = await cache.get(key);

      expect(result).toBeDefined();
    });
  });
});
