/**
 * Unified Cache Manager
 *
 * Orchestrates multiple cache backends with automatic fallback and intelligent routing.
 * Provides a single interface for all caching needs.
 *
 * Strategy:
 * - Small, frequently accessed data → Memory cache
 * - Large datasets → IndexedDB
 * - API responses → Service Worker
 * - Session data → All layers with sync
 */

import { logger } from '@/lib/logger';

import type {
  ICache,
  CacheOptions,
  InvalidateOptions,
  CacheStatistics,
  CacheEvent,
} from './CacheInterface';

import { TTL, CacheKeys, CacheEventType } from './CacheInterface';
import { IndexedDBCache, createIndexedDBCache } from './IndexedDBCache';
import { MemoryCache, createMemoryCache } from './MemoryCache';
import { ServiceWorkerCache, createServiceWorkerCache } from './ServiceWorkerCache';

/**
 * Cache layer priorities
 */
export enum CacheLayer {
  MEMORY = 'memory',
  INDEXEDDB = 'indexeddb',
  SERVICE_WORKER = 'service-worker',
}

/**
 * Cache manager configuration
 */
export interface CacheManagerConfig {
  /** Enable memory cache (default: true) */
  enableMemory?: boolean;
  /** Enable IndexedDB cache (default: true) */
  enableIndexedDB?: boolean;
  /** Enable Service Worker cache (default: true) */
  enableServiceWorker?: boolean;
  /** Default TTL (default: 5 minutes) */
  defaultTTL?: number;
  /** Enable logging (default: false) */
  enableLogging?: boolean;
  /** Memory cache size in MB (default: 50) */
  memoryCacheSizeMB?: number;
  /** IndexedDB max entries (default: 5000) */
  indexedDBMaxEntries?: number;
}

/**
 * Size threshold for cache routing
 */
const SIZE_THRESHOLDS = {
  MEMORY: 100 * 1024, // 100KB - use memory cache
  INDEXEDDB: 5 * 1024 * 1024, // 5MB - use IndexedDB
} as const;

/**
 * Unified cache manager
 */
export class CacheManager {
  public memoryCache: MemoryCache | null = null;
  public indexedDBCache: IndexedDBCache | null = null;
  public serviceWorkerCache: ServiceWorkerCache | null = null;
  private readonly config: Required<CacheManagerConfig>;
  private stats = {
    totalRequests: 0,
    memoryHits: 0,
    indexedDBHits: 0,
    serviceWorkerHits: 0,
    misses: 0,
  };

  constructor(config: CacheManagerConfig = {}) {
    this.config = {
      enableMemory: config.enableMemory ?? true,
      enableIndexedDB: config.enableIndexedDB ?? true,
      enableServiceWorker: config.enableServiceWorker ?? true,
      defaultTTL: config.defaultTTL ?? TTL.SHORT,
      enableLogging: config.enableLogging ?? false,
      memoryCacheSizeMB: config.memoryCacheSizeMB ?? 50,
      indexedDBMaxEntries: config.indexedDBMaxEntries ?? 5000,
    };

    this.initialize();
  }

  /**
   * Initialize cache backends
   */
  private initialize(): void {
    if (this.config.enableMemory) {
      this.memoryCache = createMemoryCache({
        maxMemory: this.config.memoryCacheSizeMB * 1024 * 1024,
        defaultTTL: this.config.defaultTTL,
        enableLogging: this.config.enableLogging,
        name: 'MemoryCache',
      });

      if (this.config.enableLogging) {
        logger.debug('[CacheManager] Memory cache initialized');
      }
    }

    if (this.config.enableIndexedDB && typeof window !== 'undefined') {
      try {
        this.indexedDBCache = createIndexedDBCache({
          maxEntries: this.config.indexedDBMaxEntries,
          defaultTTL: this.config.defaultTTL,
          enableLogging: this.config.enableLogging,
        });

        if (this.config.enableLogging) {
          logger.debug('[CacheManager] IndexedDB cache initialized');
        }
      } catch (error) {
        logger.warn('[CacheManager] IndexedDB cache initialization failed:', error);
      }
    }

    if (this.config.enableServiceWorker && typeof window !== 'undefined') {
      try {
        this.serviceWorkerCache = createServiceWorkerCache({
          defaultTTL: this.config.defaultTTL,
          enableLogging: this.config.enableLogging,
        });

        if (this.config.enableLogging) {
          logger.debug('[CacheManager] Service Worker cache initialized');
        }
      } catch (error) {
        logger.warn('[CacheManager] Service Worker cache initialization failed:', error);
      }
    }

    // Setup event listeners for synchronization
    this.setupEventListeners();
  }

  /**
   * Get value from cache with automatic layer selection
   */
  async get<T = unknown>(
    key: string,
    options?: { preferredLayer?: CacheLayer },
  ): Promise<T | null> {
    this.stats.totalRequests++;

    // Try memory cache first (fastest)
    if (this.memoryCache) {
      const value = await this.memoryCache.get<T>(key);
      if (value !== null) {
        this.stats.memoryHits++;
        return value;
      }
    }

    // Try IndexedDB (large datasets)
    if (
      this.indexedDBCache &&
      (!options?.preferredLayer || options.preferredLayer === CacheLayer.INDEXEDDB)
    ) {
      const value = await this.indexedDBCache.get<T>(key);
      if (value !== null) {
        this.stats.indexedDBHits++;
        // Promote to memory cache if small enough
        this.promoteToMemory(key, value);
        return value;
      }
    }

    // Try Service Worker (API responses)
    if (this.serviceWorkerCache && key.startsWith('http')) {
      const value = await this.serviceWorkerCache.get<T>(key);
      if (value !== null) {
        this.stats.serviceWorkerHits++;
        return value;
      }
    }

    this.stats.misses++;
    return null;
  }

  /**
   * Set value in appropriate cache layers
   */
  async set<T = unknown>(key: string, value: T, options: CacheOptions = {}): Promise<void> {
    const size = this.estimateSize(value);
    const layers = this.selectLayers(key, size);

    // Store in all selected layers
    const promises: Promise<void>[] = [];

    if (layers.includes(CacheLayer.MEMORY) && this.memoryCache) {
      promises.push(this.memoryCache.set(key, value, options));
    }

    if (layers.includes(CacheLayer.INDEXEDDB) && this.indexedDBCache) {
      promises.push(this.indexedDBCache.set(key, value, options));
    }

    if (
      layers.includes(CacheLayer.SERVICE_WORKER) &&
      this.serviceWorkerCache &&
      key.startsWith('http')
    ) {
      promises.push(this.serviceWorkerCache.set(key, value, options));
    }

    await Promise.all(promises);

    if (this.config.enableLogging) {
      logger.debug(`[CacheManager] Set key=${key} in layers:`, layers);
    }
  }

  /**
   * Check if key exists in any layer
   */
  async has(key: string): Promise<boolean> {
    if (this.memoryCache && (await this.memoryCache.has(key))) return true;
    if (this.indexedDBCache && (await this.indexedDBCache.has(key))) return true;
    if (
      this.serviceWorkerCache &&
      key.startsWith('http') &&
      (await this.serviceWorkerCache.has(key))
    )
      return true;
    return false;
  }

  /**
   * Delete from all layers
   */
  async delete(key: string): Promise<boolean> {
    const results = await Promise.all([
      this.memoryCache?.delete(key) ?? Promise.resolve(false),
      this.indexedDBCache?.delete(key) ?? Promise.resolve(false),
      this.serviceWorkerCache?.delete(key) ?? Promise.resolve(false),
    ]);

    return results.some((result) => result);
  }

  /**
   * Invalidate across all layers
   */
  async invalidate(options: InvalidateOptions): Promise<number> {
    const results = await Promise.all([
      this.memoryCache?.invalidate(options) ?? Promise.resolve(0),
      this.indexedDBCache?.invalidate(options) ?? Promise.resolve(0),
      this.serviceWorkerCache?.invalidate(options) ?? Promise.resolve(0),
    ]);

    const total = results.reduce((sum, count) => sum + count, 0);

    if (this.config.enableLogging) {
      logger.debug(`[CacheManager] Invalidated ${total} entries`);
    }

    return total;
  }

  /**
   * Clear all layers
   */
  async clear(): Promise<void> {
    await Promise.all([
      this.memoryCache?.clear(),
      this.indexedDBCache?.clear(),
      this.serviceWorkerCache?.clear(),
    ]);

    if (this.config.enableLogging) {
      logger.debug('[CacheManager] All caches cleared');
    }
  }

  /**
   * Get aggregated statistics
   */
  async getStats(): Promise<{
    overall: { totalRequests: number; memoryHits: number; indexedDBHits: number; serviceWorkerHits: number; misses: number; hitRatio: number };
    memory: CacheStatistics | null;
    indexedDB: CacheStatistics | null;
    serviceWorker: CacheStatistics | null;
  }> {
    const [memoryStats, indexedDBStats, serviceWorkerStats] = await Promise.all([
      this.memoryCache?.getStats() ?? Promise.resolve(null),
      this.indexedDBCache?.getStats() ?? Promise.resolve(null),
      this.serviceWorkerCache?.getStats() ?? Promise.resolve(null),
    ]);

    const totalHits =
      this.stats.memoryHits + this.stats.indexedDBHits + this.stats.serviceWorkerHits;
    const totalAttempts = totalHits + this.stats.misses;

    return {
      overall: {
        ...this.stats,
        hitRatio: totalAttempts === 0 ? 0 : totalHits / totalAttempts,
      },
      memory: memoryStats,
      indexedDB: indexedDBStats,
      serviceWorker: serviceWorkerStats,
    };
  }

  /**
   * Close all cache connections
   */
  async close(): Promise<void> {
    await Promise.all([
      this.memoryCache?.close(),
      this.indexedDBCache?.close(),
      this.serviceWorkerCache?.close(),
    ]);
  }

  /**
   * Optimistic update - update cache immediately, then update backend
   */
  async optimisticUpdate<T>(
    key: string,
    updater: (current: T | null) => T,
    backendUpdate: () => Promise<T>,
    options: CacheOptions = {},
  ): Promise<{ success: boolean; data: T; rollback: () => Promise<void> }> {
    // Get current value
    const current = await this.get<T>(key);

    // Calculate optimistic value
    const optimistic = updater(current);

    // Store rollback data
    const rollback = async () => {
      if (current !== null) {
        await this.set(key, current, options);
      } else {
        await this.delete(key);
      }
    };

    // Update cache optimistically
    await this.set(key, optimistic, options);

    try {
      // Update backend
      const updated = await backendUpdate();

      // Sync cache with backend result
      await this.set(key, updated, options);

      return { success: true, data: updated, rollback };
    } catch (error) {
      // Rollback on error
      await rollback();
      throw error;
    }
  }

  /**
   * Private: Select appropriate cache layers based on key and size
   */
  private selectLayers(key: string, size: number): CacheLayer[] {
    const layers: CacheLayer[] = [];

    // Always try memory for small items
    if (size <= SIZE_THRESHOLDS.MEMORY) {
      layers.push(CacheLayer.MEMORY);
    }

    // Use IndexedDB for larger items
    if (size <= SIZE_THRESHOLDS.INDEXEDDB) {
      layers.push(CacheLayer.INDEXEDDB);
    }

    // Use Service Worker for HTTP requests
    if (key.startsWith('http')) {
      layers.push(CacheLayer.SERVICE_WORKER);
    }

    return layers;
  }

  /**
   * Private: Promote value to memory cache
   */
  private async promoteToMemory<T>(key: string, value: T): Promise<void> {
    if (!this.memoryCache) return;

    const size = this.estimateSize(value);
    if (size <= SIZE_THRESHOLDS.MEMORY) {
      await this.memoryCache.set(key, value, { ttl: TTL.SHORT });
    }
  }

  /**
   * Private: Estimate object size
   */
  private estimateSize(obj: unknown): number {
    if (obj === null || obj === undefined) return 8;
    if (typeof obj === 'string') return obj.length * 2;
    if (typeof obj === 'number') return 8;
    if (typeof obj === 'boolean') return 4;

    // Rough estimate for objects
    try {
      return JSON.stringify(obj).length * 2;
    } catch (error) {
      return 1024; // Default 1KB
    }
  }

  /**
   * Private: Setup event listeners for cache synchronization
   */
  private setupEventListeners(): void {
    // Listen to memory cache events
    if (this.memoryCache) {
      this.memoryCache.on(CacheEventType.SET, (event: CacheEvent) => {
        // Could sync to other layers if needed
        if (this.config.enableLogging) {
          logger.debug('[CacheManager] Memory cache SET:', event.key);
        }
      });
    }

    // Listen to IndexedDB events
    if (this.indexedDBCache) {
      this.indexedDBCache.on(CacheEventType.SET, (event: CacheEvent) => {
        if (this.config.enableLogging) {
          logger.debug('[CacheManager] IndexedDB cache SET:', event.key);
        }
      });
    }
  }
}

/**
 * Global cache manager instance
 */
let globalCacheManager: CacheManager | null = null;

/**
 * Get or create global cache manager
 */
export function getCacheManager(config?: CacheManagerConfig): CacheManager {
  if (!globalCacheManager) {
    globalCacheManager = new CacheManager(config);
  }
  return globalCacheManager;
}

/**
 * Reset global cache manager (for testing)
 */
export function resetCacheManager(): void {
  if (globalCacheManager) {
    globalCacheManager.close();
    globalCacheManager = null;
  }
}

/**
 * Export key generators for convenience
 */
export { CacheKeys };
