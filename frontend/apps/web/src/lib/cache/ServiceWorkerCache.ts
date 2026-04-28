/**
 * Service Worker Cache Implementation
 *
 * Leverages browser Service Worker API for network request caching.
 * Best for: API responses, offline support, network-first strategies
 *
 * Features:
 * - Network request interception
 * - Offline support
 * - Cache-first/Network-first strategies
 * - Automatic cache version management
 * - Background sync support
 */

import { logger } from '@/lib/logger';

import type {
  IObservableCache,
  CacheOptions,
  InvalidateOptions,
  CacheStatistics,
  CacheEvent,
  CacheEventType,
  CacheEventListener,
} from './CacheInterface';

import { TTL, CacheEventType as EventType } from './CacheInterface';

/**
 * Service Worker cache configuration
 */
export interface ServiceWorkerCacheConfig {
  /** Cache name (default: 'trace-api-cache-v1') */
  cacheName?: string | undefined;
  /** Cache strategy (default: 'network-first') */
  strategy?: 'cache-first' | 'network-first' | 'stale-while-revalidate' | undefined;
  /** Default TTL (default: 5 minutes) */
  defaultTTL?: number | undefined;
  /** Maximum cache size in MB (default: 50) */
  maxCacheSizeMB?: number | undefined;
  /** Enable logging (default: false) */
  enableLogging?: boolean | undefined;
}

/**
 * Service Worker cache implementation
 */
export class ServiceWorkerCache implements IObservableCache {
  private readonly cacheName: string;
  private readonly strategy: string;
  private readonly defaultTTL: number;
  private readonly maxCacheSize: number;
  private readonly enableLogging: boolean;
  private totalHits: number = 0;
  private totalMisses: number = 0;
  private listeners = new Map<CacheEventType, Set<CacheEventListener>>();
  private registration: ServiceWorkerRegistration | null = null;

  constructor(config: ServiceWorkerCacheConfig = {}) {
    this.cacheName = config.cacheName ?? 'trace-api-cache-v1';
    this.strategy = config.strategy ?? 'network-first';
    this.defaultTTL = config.defaultTTL ?? TTL.SHORT;
    this.maxCacheSize = (config.maxCacheSizeMB ?? 50) * 1024 * 1024;
    this.enableLogging = config.enableLogging ?? false;

    // Register service worker if not already registered
    this.registerServiceWorker().catch((error) => {
      logger.error('[ServiceWorkerCache] Registration failed:', error);
    });
  }

  /**
   * Register service worker
   */
  private async registerServiceWorker(): Promise<void> {
    if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
      throw new Error('Service Worker not supported');
    }

    try {
      this.registration = await navigator.serviceWorker.register('/service-worker.js', {
        scope: '/',
      });

      if (this.enableLogging) {
        logger.debug('[ServiceWorkerCache] Service Worker registered');
      }

      // Listen for updates
      this.registration.addEventListener('updatefound', () => {
        if (this.enableLogging) {
          logger.debug('[ServiceWorkerCache] Update found');
        }
      });
    } catch (error) {
      logger.error('[ServiceWorkerCache] Registration failed:', error);
      throw error;
    }
  }

  /**
   * Get cache instance
   */
  private async getCacheInstance(): Promise<Cache> {
    if (typeof window === 'undefined' || !('caches' in window)) {
      throw new Error('Cache API not supported');
    }
    return await caches.open(this.cacheName);
  }

  /**
   * Get a value from cache
   */
  async get<T = unknown>(key: string): Promise<T | null> {
    try {
      const cache = await this.getCacheInstance();
      const response = await cache.match(key);

      if (!response) {
        this.totalMisses++;
        this.emit({
          type: EventType.MISS,
          backend: 'ServiceWorkerCache',
          key,
          timestamp: Date.now(),
        });
        return null;
      }

      // Check if expired
      const expiresHeader = response.headers.get('X-Cache-Expires');
      if (expiresHeader) {
        const expiresAt = parseInt(expiresHeader, 10);
        if (Date.now() >= expiresAt) {
          await this.delete(key);
          this.totalMisses++;
          this.emit({
            type: EventType.MISS,
            backend: 'ServiceWorkerCache',
            key,
            timestamp: Date.now(),
            metadata: { reason: 'expired' },
          });
          return null;
        }
      }

      this.totalHits++;
      this.emit({
        type: EventType.HIT,
        backend: 'ServiceWorkerCache',
        key,
        timestamp: Date.now(),
      });

      const data = await response.json();
      return data as T;
    } catch (error) {
      logger.error(`[ServiceWorkerCache] Get failed for key=${key}:`, error);
      return null;
    }
  }

  /**
   * Set a value in cache
   */
  async set<T = unknown>(key: string, value: T, options: CacheOptions = {}): Promise<void> {
    try {
      const cache = await this.getCacheInstance();
      const ttl = options.ttl ?? this.defaultTTL;

      // Create response with custom headers
      const headers = new Headers({
        'Content-Type': 'application/json',
        'X-Cache-Timestamp': Date.now().toString(),
      });

      if (ttl !== null) {
        headers.set('X-Cache-Expires', (Date.now() + ttl).toString());
      }

      if (options.tags && options.tags.length > 0) {
        headers.set('X-Cache-Tags', JSON.stringify(options.tags));
      }

      const response = new Response(JSON.stringify(value), {
        headers,
        status: 200,
      });

      await cache.put(key, response);

      this.emit({
        type: EventType.SET,
        backend: 'ServiceWorkerCache',
        key,
        timestamp: Date.now(),
        metadata: { ttl },
      });

      if (this.enableLogging) {
        logger.debug(`[ServiceWorkerCache] Set key=${key}`);
      }

      // Check cache size and evict if necessary
      await this.enforceMaxSize();
    } catch (error) {
      logger.error(`[ServiceWorkerCache] Set failed for key=${key}:`, error);
      throw error;
    }
  }

  /**
   * Check if key exists
   */
  async has(key: string): Promise<boolean> {
    const value = await this.get(key);
    return value !== null;
  }

  /**
   * Delete a specific entry
   */
  async delete(key: string): Promise<boolean> {
    try {
      const cache = await this.getCacheInstance();
      const result = await cache.delete(key);

      if (result) {
        this.emit({
          type: EventType.DELETE,
          backend: 'ServiceWorkerCache',
          key,
          timestamp: Date.now(),
        });
      }

      return result;
    } catch (error) {
      logger.error(`[ServiceWorkerCache] Delete failed for key=${key}:`, error);
      return false;
    }
  }

  /**
   * Invalidate cache entries
   */
  async invalidate(options: InvalidateOptions): Promise<number> {
    try {
      if (options.all) {
        const cache = await this.getCacheInstance();
        const keys = await cache.keys();
        for (const request of keys) {
          await cache.delete(request);
        }

        this.emit({
          type: EventType.CLEAR,
          backend: 'ServiceWorkerCache',
          timestamp: Date.now(),
        });

        return keys.length;
      }

      const cache = await this.getCacheInstance();
      const requests = await cache.keys();
      let count = 0;

      for (const request of requests) {
        const url = request.url;
        let shouldDelete = false;

        // Check pattern
        if (options.pattern) {
          const pattern = options.pattern.replace(/\*/g, '.*').replace(/\?/g, '.');
          const regex = new RegExp(pattern);
          if (regex.test(url)) {
            shouldDelete = true;
          }
        }

        // Check tags
        if (options.tags && options.tags.length > 0) {
          const response = await cache.match(request);
          if (response) {
            const tagsHeader = response.headers.get('X-Cache-Tags');
            if (tagsHeader) {
              const tags = JSON.parse(tagsHeader) as string[];
              if (options.tags.some((tag) => tags.includes(tag))) {
                shouldDelete = true;
              }
            }
          }
        }

        if (shouldDelete) {
          await cache.delete(request);
          count++;
        }
      }

      this.emit({
        type: EventType.INVALIDATE,
        backend: 'ServiceWorkerCache',
        pattern: options.pattern,
        tags: options.tags,
        timestamp: Date.now(),
        metadata: { count },
      });

      return count;
    } catch (error) {
      logger.error('[ServiceWorkerCache] Invalidate failed:', error);
      return 0;
    }
  }

  /**
   * Clear all entries
   */
  async clear(): Promise<void> {
    try {
      await caches.delete(this.cacheName);
      // Recreate cache
      await caches.open(this.cacheName);

      this.emit({
        type: EventType.CLEAR,
        backend: 'ServiceWorkerCache',
        timestamp: Date.now(),
      });

      if (this.enableLogging) {
        logger.debug('[ServiceWorkerCache] Cache cleared');
      }
    } catch (error) {
      logger.error('[ServiceWorkerCache] Clear failed:', error);
      throw error;
    }
  }

  /**
   * Get cache statistics
   */
  async getStats(): Promise<CacheStatistics> {
    try {
      const cache = await this.getCacheInstance();
      const keys = await cache.keys();
      const totalEntries = keys.length;

      // Estimate total size
      let totalMemory = 0;
      for (const request of keys.slice(0, 100)) {
        // Sample first 100
        const response = await cache.match(request);
        if (response) {
          const blob = await response.blob();
          totalMemory += blob.size;
        }
      }

      // Extrapolate from sample
      if (keys.length > 100) {
        totalMemory = Math.floor((totalMemory / 100) * keys.length);
      }

      return {
        totalEntries,
        maxEntries: Infinity, // No hard limit for Service Worker cache
        totalHits: this.totalHits,
        totalMisses: this.totalMisses,
        hitRatio:
          this.totalHits + this.totalMisses === 0
            ? 0
            : this.totalHits / (this.totalHits + this.totalMisses),
        totalMemory,
        maxMemory: this.maxCacheSize,
        memoryUsagePercent: Math.round((totalMemory / this.maxCacheSize) * 100),
        backendType: 'ServiceWorkerCache',
      };
    } catch (error) {
      logger.error('[ServiceWorkerCache] GetStats failed:', error);
      return {
        totalEntries: 0,
        maxEntries: Infinity,
        totalHits: this.totalHits,
        totalMisses: this.totalMisses,
        hitRatio: 0,
        totalMemory: 0,
        maxMemory: this.maxCacheSize,
        memoryUsagePercent: 0,
        backendType: 'ServiceWorkerCache',
      };
    }
  }

  /**
   * Get all keys
   */
  async keys(pattern?: string): Promise<string[]> {
    try {
      const cache = await this.getCacheInstance();
      const requests = await cache.keys();
      const urls = requests.map((req) => req.url);

      if (!pattern) return urls;

      const regex = new RegExp(`^${pattern.replace(/\*/g, '.*').replace(/\?/g, '.')}$`);
      return urls.filter((url) => regex.test(url));
    } catch (error) {
      logger.error('[ServiceWorkerCache] Keys failed:', error);
      return [];
    }
  }

  /**
   * Bulk get operation
   */
  async getMany<T = unknown>(keys: string[]): Promise<Map<string, T>> {
    const result = new Map<string, T>();
    for (const key of keys) {
      const value = await this.get<T>(key);
      if (value !== null) {
        result.set(key, value);
      }
    }
    return result;
  }

  /**
   * Bulk set operation
   */
  async setMany<T = unknown>(
    entries: Array<{ key: string; value: T; options?: CacheOptions }>,
  ): Promise<void> {
    for (const entry of entries) {
      await this.set(entry.key, entry.value, entry.options);
    }
  }

  /**
   * Touch entry (no-op for Service Worker cache)
   */
  async touch(_key: string): Promise<boolean> {
    // Service Worker cache doesn't support updating metadata without recreating entry
    return false;
  }

  /**
   * Close (unregister service worker)
   */
  async close(): Promise<void> {
    if (this.registration) {
      await this.registration.unregister();
      this.registration = null;
    }
  }

  /**
   * Subscribe to events
   */
  on(eventType: CacheEventType, listener: CacheEventListener): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(listener);

    return () => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        listeners.delete(listener);
      }
    };
  }

  /**
   * Emit event
   */
  emit(event: CacheEvent): void {
    const listeners = this.listeners.get(event.type);
    if (listeners) {
      listeners.forEach((listener) => {
        try {
          listener(event);
        } catch (error) {
          logger.error('[ServiceWorkerCache] Event listener error:', error);
        }
      });
    }
  }

  /**
   * Private: Enforce maximum cache size
   */
  private async enforceMaxSize(): Promise<void> {
    try {
      const stats = await this.getStats();
      if (stats.totalMemory <= this.maxCacheSize) return;

      // Evict oldest entries
      const cache = await this.getCacheInstance();
      const requests = await cache.keys();

      // Sort by timestamp (oldest first)
      const timestampedRequests = await Promise.all(
        requests.map(async (request) => {
          const response = await cache.match(request);
          const timestamp = response?.headers.get('X-Cache-Timestamp');
          return {
            request,
            timestamp: timestamp ? parseInt(timestamp, 10) : 0,
          };
        }),
      );

      timestampedRequests.sort((a, b) => a.timestamp - b.timestamp);

      // Delete 20% of oldest entries
      const deleteCount = Math.ceil(timestampedRequests.length * 0.2);
      for (let i = 0; i < deleteCount; i++) {
        const entry = timestampedRequests[i];
        if (!entry) continue;
        await cache.delete(entry.request);
        this.emit({
          type: EventType.EVICTION,
          backend: 'ServiceWorkerCache',
          key: entry.request.url,
          timestamp: Date.now(),
        });
      }

      if (this.enableLogging) {
        logger.debug(`[ServiceWorkerCache] Evicted ${deleteCount} entries due to size limit`);
      }
    } catch (error) {
      logger.error('[ServiceWorkerCache] EnforceMaxSize failed:', error);
    }
  }
}

/**
 * Create Service Worker cache instance
 */
export function createServiceWorkerCache(
  config: ServiceWorkerCacheConfig = {},
): ServiceWorkerCache {
  return new ServiceWorkerCache(config);
}
