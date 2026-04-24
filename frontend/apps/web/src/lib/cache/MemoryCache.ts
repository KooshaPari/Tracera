/**
 * Memory Cache Implementation (LRU)
 *
 * In-memory cache with LRU eviction strategy.
 * Best for: Frequently accessed, short-lived data (<5MB total)
 *
 * Features:
 * - Fast access (no serialization)
 * - Automatic LRU eviction
 * - Memory pressure awareness
 * - Tag-based invalidation
 * - Pattern matching support
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
 * Memory cache configuration
 */
export interface MemoryCacheConfig {
  /** Maximum number of entries (default: 1000) */
  maxEntries?: number | undefined;
  /** Maximum memory in bytes (default: 50MB) */
  maxMemory?: number | undefined;
  /** Default TTL for entries (default: 5 minutes) */
  defaultTTL?: number | undefined;
  /** Enable logging (default: false) */
  enableLogging?: boolean | undefined;
  /** Name for debugging (default: 'MemoryCache') */
  name?: string | undefined;
}

/**
 * In-memory LRU cache implementation
 */
export class MemoryCache implements IObservableCache {
  private entries = new Map<string, CacheEntry>();
  private lruOrder: string[] = []; // Most recently used at end
  private readonly maxEntries: number;
  private readonly maxMemory: number;
  private readonly defaultTTL: number;
  private readonly enableLogging: boolean;
  private readonly name: string;
  private totalMemory: number = 0;
  private totalHits: number = 0;
  private totalMisses: number = 0;
  private listeners = new Map<CacheEventType, Set<CacheEventListener>>();

  constructor(config: MemoryCacheConfig = {}) {
    this.maxEntries = config.maxEntries ?? 1000;
    this.maxMemory = config.maxMemory ?? 50 * 1024 * 1024; // 50MB
    this.defaultTTL = config.defaultTTL ?? TTL.SHORT;
    this.enableLogging = config.enableLogging ?? false;
    this.name = config.name ?? 'MemoryCache';

    if (this.enableLogging) {
      logger.debug(
        `[${this.name}] Initialized with maxEntries=${this.maxEntries}, maxMemory=${this.maxMemory}`,
      );
    }
  }

  /**
   * Get a value from cache
   */
  async get<T = unknown>(key: string): Promise<T | null> {
    const entry = this.entries.get(key);

    if (!entry) {
      this.totalMisses++;
      this.emit({
        type: EventType.MISS,
        backend: this.name,
        key,
        timestamp: Date.now(),
      });
      return null;
    }

    // Check expiration
    if (isExpired(entry.metadata.expiresAt)) {
      this.delete(key); // Clean up expired entry
      this.totalMisses++;
      this.emit({
        type: EventType.MISS,
        backend: this.name,
        key,
        timestamp: Date.now(),
        metadata: { reason: 'expired' },
      });
      return null;
    }

    // Update LRU order
    this.updateLRU(key);

    // Update metadata
    entry.metadata.lastAccessAt = Date.now();
    entry.metadata.hitCount++;
    this.totalHits++;

    this.emit({
      type: EventType.HIT,
      backend: this.name,
      key,
      timestamp: Date.now(),
    });

    return entry.value as T;
  }

  /**
   * Set a value in cache
   */
  async set<T = unknown>(key: string, value: T, options: CacheOptions = {}): Promise<void> {
    const ttl = options.ttl ?? this.defaultTTL;
    const size = estimateSize(value);

    // Remove old entry if exists
    if (this.entries.has(key)) {
      const oldEntry = this.entries.get(key)!;
      this.totalMemory -= oldEntry.metadata.size;
      this.removeLRU(key);
    }

    // Evict entries if necessary
    while (
      (this.totalMemory + size > this.maxMemory || this.entries.size >= this.maxEntries) &&
      this.entries.size > 0 &&
      !this.entries.has(key)
    ) {
      await this.evictLRU();
    }

    // Create metadata
    const metadata: CacheMetadata = {
      createdAt: Date.now(),
      lastAccessAt: Date.now(),
      expiresAt: calculateExpiration(ttl, options.jitter),
      hitCount: 0,
      size,
      tags: options.tags ?? [],
      version: options.version ?? 1,
    };

    // Store entry
    const entry: CacheEntry<T> = { key, value, metadata };
    this.entries.set(key, entry);
    this.lruOrder.push(key);
    this.totalMemory += size;

    this.emit({
      type: EventType.SET,
      backend: this.name,
      key,
      timestamp: Date.now(),
      metadata: { size, ttl },
    });

    if (this.enableLogging) {
      logger.debug(`[${this.name}] Set key=${key}, size=${size}, ttl=${ttl}`);
    }
  }

  /**
   * Check if key exists and is not expired
   */
  async has(key: string): Promise<boolean> {
    const entry = this.entries.get(key);
    if (!entry) return false;
    if (isExpired(entry.metadata.expiresAt)) {
      await this.delete(key);
      return false;
    }
    return true;
  }

  /**
   * Delete a specific entry
   */
  async delete(key: string): Promise<boolean> {
    const entry = this.entries.get(key);
    if (!entry) return false;

    this.totalMemory -= entry.metadata.size;
    this.entries.delete(key);
    this.removeLRU(key);

    this.emit({
      type: EventType.DELETE,
      backend: this.name,
      key,
      timestamp: Date.now(),
    });

    return true;
  }

  /**
   * Invalidate cache entries
   */
  async invalidate(options: InvalidateOptions): Promise<number> {
    let count = 0;
    const keysToDelete: string[] = [];

    if (options.all) {
      // Clear all entries
      count = this.entries.size;
      await this.clear();
      return count;
    }

    // Find keys to delete
    for (const [key, entry] of this.entries) {
      let shouldDelete = false;

      // Match by pattern
      if (options.pattern && matchesPattern(key, options.pattern)) {
        shouldDelete = true;
      }

      // Match by tags
      if (options.tags && options.tags.some((tag) => entry.metadata.tags.includes(tag))) {
        shouldDelete = true;
      }

      if (shouldDelete) {
        keysToDelete.push(key);
      }
    }

    // Delete matched keys
    for (const key of keysToDelete) {
      await this.delete(key);
      count++;
    }

    this.emit({
      type: EventType.INVALIDATE,
      backend: this.name,
      pattern: options.pattern,
      tags: options.tags,
      timestamp: Date.now(),
      metadata: { count },
    });

    if (this.enableLogging) {
      logger.debug(`[${this.name}] Invalidated ${count} entries`);
    }

    return count;
  }

  /**
   * Clear all entries
   */
  async clear(): Promise<void> {
    const count = this.entries.size;
    this.entries.clear();
    this.lruOrder = [];
    this.totalMemory = 0;

    this.emit({
      type: EventType.CLEAR,
      backend: this.name,
      timestamp: Date.now(),
      metadata: { count },
    });

    if (this.enableLogging) {
      logger.debug(`[${this.name}] Cleared ${count} entries`);
    }
  }

  /**
   * Get cache statistics
   */
  async getStats(): Promise<CacheStatistics> {
    return {
      totalEntries: this.entries.size,
      maxEntries: this.maxEntries,
      totalHits: this.totalHits,
      totalMisses: this.totalMisses,
      hitRatio:
        this.totalHits + this.totalMisses === 0
          ? 0
          : this.totalHits / (this.totalHits + this.totalMisses),
      totalMemory: this.totalMemory,
      maxMemory: this.maxMemory,
      memoryUsagePercent:
        this.maxMemory === 0 ? 0 : Math.round((this.totalMemory / this.maxMemory) * 100),
      backendType: this.name,
    };
  }

  /**
   * Get all keys (optionally filtered by pattern)
   */
  async keys(pattern?: string): Promise<string[]> {
    const allKeys = Array.from(this.entries.keys());
    if (!pattern) return allKeys;
    return allKeys.filter((key) => matchesPattern(key, pattern));
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
   * Touch entry to update last access time
   */
  async touch(key: string): Promise<boolean> {
    const entry = this.entries.get(key);
    if (!entry) return false;

    entry.metadata.lastAccessAt = Date.now();
    this.updateLRU(key);
    return true;
  }

  /**
   * Close/cleanup (no-op for memory cache)
   */
  async close(): Promise<void> {
    // No cleanup needed for memory cache
  }

  /**
   * Subscribe to cache events
   */
  on(eventType: CacheEventType, listener: CacheEventListener): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(listener);

    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        listeners.delete(listener);
      }
    };
  }

  /**
   * Emit a cache event
   */
  emit(event: CacheEvent): void {
    const listeners = this.listeners.get(event.type);
    if (listeners) {
      listeners.forEach((listener) => {
        try {
          listener(event);
        } catch (error) {
          logger.error(`[${this.name}] Error in event listener:`, error);
        }
      });
    }
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.totalHits = 0;
    this.totalMisses = 0;
  }

  /**
   * Get memory pressure status
   */
  getMemoryPressure(): 'comfortable' | 'caution' | 'critical' {
    const percent = this.totalMemory / this.maxMemory;
    if (percent < 0.7) return 'comfortable';
    if (percent < 0.85) return 'caution';
    return 'critical';
  }

  /**
   * Private: Update LRU order
   */
  private updateLRU(key: string): void {
    this.removeLRU(key);
    this.lruOrder.push(key);
  }

  /**
   * Private: Remove from LRU order
   */
  private removeLRU(key: string): void {
    const index = this.lruOrder.indexOf(key);
    if (index > -1) {
      this.lruOrder.splice(index, 1);
    }
  }

  /**
   * Private: Evict least recently used entry
   */
  private async evictLRU(): Promise<void> {
    const keyToEvict = this.lruOrder[0];
    if (!keyToEvict) return;

    await this.delete(keyToEvict);

    this.emit({
      type: EventType.EVICTION,
      backend: this.name,
      key: keyToEvict,
      timestamp: Date.now(),
    });

    if (this.enableLogging) {
      logger.debug(`[${this.name}] Evicted key=${keyToEvict}`);
    }
  }
}

/**
 * Create a memory cache instance
 */
export function createMemoryCache(config: MemoryCacheConfig = {}): MemoryCache {
  return new MemoryCache(config);
}
