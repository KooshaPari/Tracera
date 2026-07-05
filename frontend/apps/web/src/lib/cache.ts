/**
 * Multi-Layer Cache System
 *
 * Unified caching interface with multiple backends:
 * - Memory (LRU) - Fast, in-memory caching
 * - IndexedDB - Large, persistent storage
 * - Service Worker - API response caching
 * - Redis (backend) - Distributed caching
 *
 * @example
 * ```typescript
 * import { getCacheManager, CacheKeys, TTL } from '@/lib/cache';
 *
 * const cache = getCacheManager();
 *
 * // Store data
 * await cache.set(
 *   CacheKeys.project.byId('123'),
 *   projectData,
 *   { ttl: TTL.MEDIUM, tags: ['project:123'] }
 * );
 *
 * // Retrieve data
 * const project = await cache.get(CacheKeys.project.byId('123'));
 *
 * // Invalidate by pattern
 * await cache.invalidate({ pattern: 'project:*' });
 * ```
 */

import { TTL, CacheKeys } from './cache/CacheInterface';
// Core interfaces and types
import { getCacheManager } from './cache/CacheManager';

export type {
  ICache,
  IObservableCache,
  CacheEntry,
  CacheMetadata,
  CacheOptions,
  InvalidateOptions,
  CacheStatistics,
  CacheEvent,
  CacheEventType,
  CacheEventListener,
} from './cache/CacheInterface';

export {
  TTL,
  CacheKeys,
  CacheEventType as EventType,
  addJitter,
  isExpired,
  calculateExpiration,
  matchesPattern,
  estimateSize,
} from './cache/CacheInterface';

// Memory cache
export { MemoryCache, createMemoryCache } from './cache/MemoryCache';
export type { MemoryCacheConfig } from './cache/MemoryCache';

// IndexedDB cache
export { IndexedDBCache, createIndexedDBCache } from './cache/IndexedDBCache';
export type { IndexedDBCacheConfig } from './cache/IndexedDBCache';

// Service Worker cache
export { ServiceWorkerCache, createServiceWorkerCache } from './cache/ServiceWorkerCache';
export type { ServiceWorkerCacheConfig } from './cache/ServiceWorkerCache';

// Unified cache manager
export { CacheManager, getCacheManager, resetCacheManager, CacheLayer } from './cache/CacheManager';
export type { CacheManagerConfig } from './cache/CacheManager';

/**
 * Quick start examples
 */

/**
 * Initialize cache manager with default settings
 */
export function initializeCache() {
  return getCacheManager({
    enableMemory: true,
    enableIndexedDB: true,
    enableServiceWorker: true,
    defaultTTL: 5 * 60 * 1000, // 5 minutes
    enableLogging: process.env['NODE_ENV'] === 'development',
  });
}

/**
 * Cache a function result with automatic key generation
 */
export async function memoize<T>(
  fn: () => Promise<T>,
  key: string,
  options?: { ttl?: number; tags?: string[] },
): Promise<T> {
  const cache = getCacheManager();

  // Check cache
  const cached = await cache.get<T>(key);
  if (cached !== null) {
    return cached;
  }

  // Execute function
  const result = await fn();

  // Store in cache
  await cache.set(key, result, {
    ttl: options?.ttl,
    tags: options?.tags,
  });

  return result;
}

/**
 * Create a cached API function
 */
export function createCachedAPI<TArgs extends unknown[], TResult>(
  apiFn: (...args: TArgs) => Promise<TResult>,
  keyGenerator: (...args: TArgs) => string,
  options?: { ttl?: number; tags?: (...args: TArgs) => string[] },
) {
  return async (...args: TArgs): Promise<TResult> => {
    const key = keyGenerator(...args);
    const cache = getCacheManager();

    // Check cache
    const cached = await cache.get<TResult>(key);
    if (cached !== null) {
      return cached;
    }

    // Call API
    const result = await apiFn(...args);

    // Store in cache
    await cache.set(key, result, {
      ttl: options?.ttl,
      tags: options?.tags?.(...args),
    });

    return result;
  };
}

/**
 * Utility: Clear all project-related caches
 */
export async function clearProjectCaches(projectId: string): Promise<void> {
  const cache = getCacheManager();
  await cache.invalidate({ tags: [`project:${projectId}`] });
}

/**
 * Utility: Clear all item-related caches
 */
export async function clearItemCaches(itemId: string): Promise<void> {
  const cache = getCacheManager();
  await cache.invalidate({ tags: [`item:${itemId}`] });
}

/**
 * Utility: Clear all user-related caches
 */
export async function clearUserCaches(userId: string): Promise<void> {
  const cache = getCacheManager();
  await cache.invalidate({ tags: [`user:${userId}`] });
}

/**
 * Utility: Prewarm cache with common data
 */
export async function prewarmCache(data: {
  projects?: Array<{ id: string; data: unknown }> | undefined;
  items?: Array<{ id: string; data: unknown }> | undefined;
}): Promise<void> {
  const cache = getCacheManager();

  if (data.projects) {
    for (const { id, data: projectData } of data.projects) {
      await cache.set(CacheKeys.project.byId(id), projectData, {
        ttl: TTL.LONG,
        tags: [`project:${id}`],
      });
    }
  }

  if (data.items) {
    for (const { id, data: itemData } of data.items) {
      await cache.set(CacheKeys.item.byId(id), itemData, {
        ttl: TTL.MEDIUM,
        tags: [`item:${id}`],
      });
    }
  }
}

/**
 * Utility: Get cache health status
 */
export async function getCacheHealth(): Promise<{
  healthy: boolean;
  hitRatio: number;
  memoryUsage: number;
  issues: string[];
}> {
  const cache = getCacheManager();
  const stats = await cache.getStats();

  const issues: string[] = [];

  if (stats.overall.hitRatio < 0.5) {
    issues.push('Low cache hit ratio (<50%)');
  }

  if (stats.memory && stats.memory.memoryUsagePercent > 90) {
    issues.push('Memory cache near capacity (>90%)');
  }

  if (stats.indexedDB && stats.indexedDB.memoryUsagePercent > 90) {
    issues.push('IndexedDB cache near capacity (>90%)');
  }

  return {
    healthy: issues.length === 0,
    hitRatio: stats.overall.hitRatio,
    memoryUsage: stats.memory?.memoryUsagePercent ?? stats.indexedDB?.memoryUsagePercent ?? 0,
    issues,
  };
}

/**
 * Development utilities
 */
export const dev = {
  /**
   * Clear all caches (use in development only)
   */
  async clearAll() {
    const cache = getCacheManager();
    await cache.clear();
    console.log('[Cache] All caches cleared');
  },

  /**
   * Print cache statistics
   */
  async printStats() {
    const cache = getCacheManager();
    const stats = await cache.getStats();
    console.table(stats);
  },

  /**
   * List all cached keys
   */
  async listKeys(pattern?: string) {
    const cache = getCacheManager();
    const memoryKeys = await cache.memoryCache?.keys(pattern);
    const indexedDBKeys = await cache.indexedDBCache?.keys(pattern);

    console.log('Memory Cache Keys:', memoryKeys);
    console.log('IndexedDB Cache Keys:', indexedDBKeys);
  },

  /**
   * Simulate cache load
   */
  async simulateLoad(count: number = 1000) {
    const cache = getCacheManager();
    console.log(`[Cache] Simulating ${count} cache operations...`);

    const start = performance.now();

    for (let i = 0; i < count; i++) {
      await cache.set(`test:${i}`, { value: i }, { ttl: TTL.SHORT });
    }

    for (let i = 0; i < count; i++) {
      await cache.get(`test:${i}`);
    }

    const duration = performance.now() - start;
    console.log(`[Cache] Completed in ${duration.toFixed(2)}ms`);
    console.log(`[Cache] Average: ${(duration / count).toFixed(3)}ms per operation`);

    // Cleanup
    await cache.invalidate({ pattern: 'test:*' });
  },
};
