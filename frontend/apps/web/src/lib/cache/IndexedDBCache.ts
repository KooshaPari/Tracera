/**
 * IndexedDB Cache Implementation
 *
 * Browser-based persistent cache using IndexedDB.
 * Best for: Large datasets (>5MB), offline support, persistent storage
 *
 * Features:
 * - Persistent storage (survives page reloads)
 * - Large capacity (typically >50MB)
 * - Automatic expiration cleanup
 * - Tag-based indexing
 * - Version migration support
 */

import { logger } from '@/lib/logger';

import type {
  IObservableCache,
  CacheEntry,
  CacheMetadata,
  CacheOptions,
  InvalidateOptions,
  CacheStatistics,
  CacheEvent,
  CacheEventType,
  CacheEventListener,
} from './CacheInterface';

import {
  TTL,
  isExpired,
  calculateExpiration,
  matchesPattern,
  estimateSize,
  CacheEventType as EventType,
} from './CacheInterface';

/**
 * IndexedDB cache configuration
 */
export interface IndexedDBCacheConfig {
  /** Database name (default: 'trace-cache') */
  dbName?: string | undefined;
  /** Store name (default: 'cache-entries') */
  storeName?: string | undefined;
  /** Database version (default: 1) */
  version?: number | undefined;
  /** Default TTL (default: 1 hour) */
  defaultTTL?: number | undefined;
  /** Maximum entries (default: 5000) */
  maxEntries?: number | undefined;
  /** Enable logging (default: false) */
  enableLogging?: boolean | undefined;
}

/**
 * IndexedDB cache implementation
 */
export class IndexedDBCache implements IObservableCache {
  private db: IDBDatabase | null = null;
  private readonly dbName: string;
  private readonly storeName: string;
  private readonly version: number;
  private readonly defaultTTL: number;
  private readonly maxEntries: number;
  private readonly enableLogging: boolean;
  private totalHits: number = 0;
  private totalMisses: number = 0;
  private listeners = new Map<CacheEventType, Set<CacheEventListener>>();
  private initPromise: Promise<void> | null = null;

  constructor(config: IndexedDBCacheConfig = {}) {
    this.dbName = config.dbName ?? 'trace-cache';
    this.storeName = config.storeName ?? 'cache-entries';
    this.version = config.version ?? 1;
    this.defaultTTL = config.defaultTTL ?? TTL.MEDIUM;
    this.maxEntries = config.maxEntries ?? 5000;
    this.enableLogging = config.enableLogging ?? false;

    // Initialize asynchronously
    this.initPromise = this.initialize();
  }

  /**
   * Initialize IndexedDB
   */
  private async initialize(): Promise<void> {
    if (typeof window === 'undefined' || !window.indexedDB) {
      throw new Error('IndexedDB not available');
    }

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => {
        reject(new Error(`Failed to open IndexedDB: ${request.error}`));
      };

      request.onsuccess = () => {
        this.db = request.result;
        if (this.enableLogging) {
          logger.debug(`[IndexedDBCache] Initialized database: ${this.dbName}`);
        }
        // Clean up expired entries on startup
        this.cleanupExpired().catch((error) => {
          logger.error('[IndexedDBCache] Cleanup failed:', error);
        });
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create object store if it doesn't exist
        if (!db.objectStoreNames.contains(this.storeName)) {
          const store = db.createObjectStore(this.storeName, {
            keyPath: 'key',
          });

          // Create indexes for efficient queries
          store.createIndex('expiresAt', 'metadata.expiresAt', {
            unique: false,
          });
          store.createIndex('tags', 'metadata.tags', {
            unique: false,
            multiEntry: true,
          });
          store.createIndex('createdAt', 'metadata.createdAt', {
            unique: false,
          });

          if (this.enableLogging) {
            logger.debug(`[IndexedDBCache] Created object store: ${this.storeName}`);
          }
        }
      };
    });
  }

  /**
   * Ensure database is initialized
   */
  private async ensureInitialized(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise;
    }
    if (!this.db) {
      throw new Error('IndexedDB not initialized');
    }
  }

  /**
   * Get a value from cache
   */
  async get<T = unknown>(key: string): Promise<T | null> {
    await this.ensureInitialized();

    const transaction = this.db!.transaction([this.storeName], 'readonly');
    const store = transaction.objectStore(this.storeName);

    return new Promise((resolve) => {
      const request = store.get(key);

      request.onsuccess = () => {
        const entry = request.result as CacheEntry<T> | undefined;

        if (!entry) {
          this.totalMisses++;
          this.emit({
            type: EventType.MISS,
            backend: 'IndexedDBCache',
            key,
            timestamp: Date.now(),
          });
          resolve(null);
          return;
        }

        // Check expiration
        if (isExpired(entry.metadata.expiresAt)) {
          this.delete(key); // Clean up
          this.totalMisses++;
          this.emit({
            type: EventType.MISS,
            backend: 'IndexedDBCache',
            key,
            timestamp: Date.now(),
            metadata: { reason: 'expired' },
          });
          resolve(null);
          return;
        }

        // Update metadata
        entry.metadata.lastAccessAt = Date.now();
        entry.metadata.hitCount++;
        this.totalHits++;

        // Update entry in DB
        this.updateMetadata(key, entry.metadata).catch((error) => {
          logger.error('[IndexedDBCache] Failed to update metadata:', error);
        });

        this.emit({
          type: EventType.HIT,
          backend: 'IndexedDBCache',
          key,
          timestamp: Date.now(),
        });

        resolve(entry.value);
      };

      request.onerror = () => {
        logger.error(`[IndexedDBCache] Get failed for key=${key}:`, request.error);
        resolve(null);
      };
    });
  }

  /**
   * Set a value in cache
   */
  async set<T = unknown>(key: string, value: T, options: CacheOptions = {}): Promise<void> {
    await this.ensureInitialized();

    const ttl = options.ttl ?? this.defaultTTL;
    const size = estimateSize(value);

    // Check if we need to evict entries
    const count = await this.count();
    if (count >= this.maxEntries) {
      await this.evictOldest();
    }

    const metadata: CacheMetadata = {
      createdAt: Date.now(),
      lastAccessAt: Date.now(),
      expiresAt: calculateExpiration(ttl, options.jitter),
      hitCount: 0,
      size,
      tags: options.tags ?? [],
      version: options.version ?? 1,
    };

    const entry: CacheEntry<T> = { key, value, metadata };

    const transaction = this.db!.transaction([this.storeName], 'readwrite');
    const store = transaction.objectStore(this.storeName);

    return new Promise((resolve, reject) => {
      const request = store.put(entry);

      request.onsuccess = () => {
        this.emit({
          type: EventType.SET,
          backend: 'IndexedDBCache',
          key,
          timestamp: Date.now(),
          metadata: { size, ttl },
        });

        if (this.enableLogging) {
          logger.debug(`[IndexedDBCache] Set key=${key}, size=${size}`);
        }
        resolve();
      };

      request.onerror = () => {
        reject(new Error(`Failed to set key=${key}: ${request.error}`));
      };
    });
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
    await this.ensureInitialized();

    const transaction = this.db!.transaction([this.storeName], 'readwrite');
    const store = transaction.objectStore(this.storeName);

    return new Promise((resolve) => {
      const request = store.delete(key);

      request.onsuccess = () => {
        this.emit({
          type: EventType.DELETE,
          backend: 'IndexedDBCache',
          key,
          timestamp: Date.now(),
        });
        resolve(true);
      };

      request.onerror = () => {
        logger.error(`[IndexedDBCache] Delete failed for key=${key}:`, request.error);
        resolve(false);
      };
    });
  }

  /**
   * Invalidate cache entries
   */
  async invalidate(options: InvalidateOptions): Promise<number> {
    await this.ensureInitialized();

    if (options.all) {
      const count = await this.count();
      await this.clear();
      return count;
    }

    const keysToDelete: string[] = [];

    // Find keys by pattern or tags
    const transaction = this.db!.transaction([this.storeName], 'readonly');
    const store = transaction.objectStore(this.storeName);

    if (options.tags && options.tags.length > 0) {
      // Use tag index
      const index = store.index('tags');
      for (const tag of options.tags) {
        const request = index.getAll(tag);
        await new Promise<void>((resolve) => {
          request.onsuccess = () => {
            const entries = request.result as CacheEntry[];
            entries.forEach((entry) => {
              if (!keysToDelete.includes(entry.key)) {
                keysToDelete.push(entry.key);
              }
            });
            resolve();
          };
          request.onerror = () => resolve();
        });
      }
    }

    if (options.pattern) {
      // Get all keys and filter by pattern
      const allKeys = await this.keys();
      const matchedKeys = allKeys.filter((key) => matchesPattern(key, options.pattern!));
      matchedKeys.forEach((key) => {
        if (!keysToDelete.includes(key)) {
          keysToDelete.push(key);
        }
      });
    }

    // Delete matched keys
    for (const key of keysToDelete) {
      await this.delete(key);
    }

    this.emit({
      type: EventType.INVALIDATE,
      backend: 'IndexedDBCache',
      pattern: options.pattern,
      tags: options.tags,
      timestamp: Date.now(),
      metadata: { count: keysToDelete.length },
    });

    return keysToDelete.length;
  }

  /**
   * Clear all entries
   */
  async clear(): Promise<void> {
    await this.ensureInitialized();

    const transaction = this.db!.transaction([this.storeName], 'readwrite');
    const store = transaction.objectStore(this.storeName);

    return new Promise((resolve, reject) => {
      const request = store.clear();

      request.onsuccess = () => {
        this.emit({
          type: EventType.CLEAR,
          backend: 'IndexedDBCache',
          timestamp: Date.now(),
        });
        resolve();
      };

      request.onerror = () => {
        reject(new Error(`Failed to clear cache: ${request.error}`));
      };
    });
  }

  /**
   * Get cache statistics
   */
  async getStats(): Promise<CacheStatistics> {
    await this.ensureInitialized();

    const count = await this.count();
    const totalMemory = await this.calculateTotalSize();

    return {
      totalEntries: count,
      maxEntries: this.maxEntries,
      totalHits: this.totalHits,
      totalMisses: this.totalMisses,
      hitRatio:
        this.totalHits + this.totalMisses === 0
          ? 0
          : this.totalHits / (this.totalHits + this.totalMisses),
      totalMemory,
      maxMemory: 100 * 1024 * 1024, // 100MB typical limit
      memoryUsagePercent: Math.round((totalMemory / (100 * 1024 * 1024)) * 100),
      backendType: 'IndexedDBCache',
    };
  }

  /**
   * Get all keys
   */
  async keys(pattern?: string): Promise<string[]> {
    await this.ensureInitialized();

    const transaction = this.db!.transaction([this.storeName], 'readonly');
    const store = transaction.objectStore(this.storeName);

    return new Promise((resolve) => {
      const request = store.getAllKeys();

      request.onsuccess = () => {
        const allKeys = request.result as string[];
        if (!pattern) {
          resolve(allKeys);
        } else {
          resolve(allKeys.filter((key) => matchesPattern(key, pattern)));
        }
      };

      request.onerror = () => {
        logger.error('[IndexedDBCache] Failed to get keys:', request.error);
        resolve([]);
      };
    });
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
   * Touch entry
   */
  async touch(key: string): Promise<boolean> {
    const entry = await this.get(key);
    if (entry === null) return false;
    // get() already updates lastAccessAt
    return true;
  }

  /**
   * Close database connection
   */
  async close(): Promise<void> {
    if (this.db) {
      this.db.close();
      this.db = null;
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
          logger.error('[IndexedDBCache] Event listener error:', error);
        }
      });
    }
  }

  /**
   * Private: Update metadata
   */
  private async updateMetadata(key: string, metadata: CacheMetadata): Promise<void> {
    const transaction = this.db!.transaction([this.storeName], 'readwrite');
    const store = transaction.objectStore(this.storeName);

    return new Promise((resolve) => {
      const getRequest = store.get(key);
      getRequest.onsuccess = () => {
        const entry = getRequest.result as CacheEntry | undefined;
        if (entry) {
          entry.metadata = metadata;
          store.put(entry);
        }
        resolve();
      };
      getRequest.onerror = () => resolve();
    });
  }

  /**
   * Private: Count entries
   */
  private async count(): Promise<number> {
    const transaction = this.db!.transaction([this.storeName], 'readonly');
    const store = transaction.objectStore(this.storeName);

    return new Promise((resolve) => {
      const request = store.count();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => resolve(0);
    });
  }

  /**
   * Private: Calculate total size
   */
  private async calculateTotalSize(): Promise<number> {
    const transaction = this.db!.transaction([this.storeName], 'readonly');
    const store = transaction.objectStore(this.storeName);

    return new Promise((resolve) => {
      const request = store.getAll();
      request.onsuccess = () => {
        const entries = request.result as CacheEntry[];
        const total = entries.reduce((sum, entry) => sum + entry.metadata.size, 0);
        resolve(total);
      };
      request.onerror = () => resolve(0);
    });
  }

  /**
   * Private: Evict oldest entry
   */
  private async evictOldest(): Promise<void> {
    const transaction = this.db!.transaction([this.storeName], 'readwrite');
    const store = transaction.objectStore(this.storeName);
    const index = store.index('createdAt');

    return new Promise((resolve) => {
      const request = index.openCursor();
      request.onsuccess = () => {
        const cursor = request.result;
        if (cursor) {
          store.delete(cursor.primaryKey);
          this.emit({
            type: EventType.EVICTION,
            backend: 'IndexedDBCache',
            key: cursor.primaryKey as string,
            timestamp: Date.now(),
          });
        }
        resolve();
      };
      request.onerror = () => resolve();
    });
  }

  /**
   * Private: Clean up expired entries
   */
  private async cleanupExpired(): Promise<number> {
    await this.ensureInitialized();

    const transaction = this.db!.transaction([this.storeName], 'readwrite');
    const store = transaction.objectStore(this.storeName);
    const index = store.index('expiresAt');

    let count = 0;
    const now = Date.now();

    return new Promise((resolve) => {
      const request = index.openCursor();
      request.onsuccess = () => {
        const cursor = request.result;
        if (cursor) {
          const entry = cursor.value as CacheEntry;
          if (entry.metadata.expiresAt && entry.metadata.expiresAt <= now) {
            store.delete(cursor.primaryKey);
            count++;
          }
          cursor.continue();
        } else {
          if (this.enableLogging && count > 0) {
            logger.debug(`[IndexedDBCache] Cleaned up ${count} expired entries`);
          }
          resolve(count);
        }
      };
      request.onerror = () => resolve(count);
    });
  }
}

/**
 * Create IndexedDB cache instance
 */
export function createIndexedDBCache(config: IndexedDBCacheConfig = {}): IndexedDBCache {
  return new IndexedDBCache(config);
}
