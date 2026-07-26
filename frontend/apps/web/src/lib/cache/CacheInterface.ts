/**
 * Multi-Layer Cache Interface
 *
 * Provides a unified, pluggable caching system with support for multiple storage backends:
 * - Memory (LRU)
 * - IndexedDB (browser storage for large datasets)
 * - Service Worker (API response caching)
 * - Redis (server-side, via backend)
 *
 * All cache implementations follow this interface for consistency.
 */

/**
 * Cache entry metadata
 */
export interface CacheMetadata {
  /** Entry creation timestamp */
  createdAt: number;
  /** Last access timestamp */
  lastAccessAt: number;
  /** Expiration timestamp (null = never expires) */
  expiresAt: number | null;
  /** Number of times this entry was accessed */
  hitCount: number;
  /** Estimated size in bytes */
  size: number;
  /** Tags for group invalidation (e.g., ["project:123", "user:456"]) */
  tags: string[];
  /** Version for migration support */
  version: number;
}

/**
 * Cache entry with value and metadata
 */
export interface CacheEntry<T = unknown> {
  key: string;
  value: T;
  metadata: CacheMetadata;
}

/**
 * Cache statistics for monitoring
 */
export interface CacheStatistics {
  /** Total number of entries */
  totalEntries: number;
  /** Maximum entries allowed */
  maxEntries: number;
  /** Total cache hits */
  totalHits: number;
  /** Total cache misses */
  totalMisses: number;
  /** Hit ratio (0-1) */
  hitRatio: number;
  /** Total memory used (bytes) */
  totalMemory: number;
  /** Maximum memory allowed (bytes) */
  maxMemory: number;
  /** Memory usage percentage */
  memoryUsagePercent: number;
  /** Backend type identifier */
  backendType: string;
}

/**
 * TTL presets for convenience
 */
export const TTL = {
  /** 5 minutes - for frequently changing data */
  SHORT: 5 * 60 * 1000,
  /** 1 hour - for moderately stable data */
  MEDIUM: 60 * 60 * 1000,
  /** 24 hours - for stable data */
  LONG: 24 * 60 * 60 * 1000,
  /** 7 days - for rarely changing data */
  WEEK: 7 * 24 * 60 * 60 * 1000,
  /** Never expires */
  NEVER: null,
} as const;

/**
 * Cache options for get/set operations
 */
export interface CacheOptions {
  /** Time-to-live in milliseconds (null = never expires) */
  ttl?: number | null | undefined;
  /** Tags for group invalidation */
  tags?: string[] | undefined;
  /** Version for migration support */
  version?: number | undefined;
  /** Add jitter to TTL to prevent thundering herd (0-1, percentage of TTL) */
  jitter?: number | undefined;
}

/**
 * Cache invalidation options
 */
export interface InvalidateOptions {
  /** Invalidate by key pattern (glob-style, e.g., "user:*") */
  pattern?: string | undefined;
  /** Invalidate by tags (all entries with ANY of these tags) */
  tags?: string[] | undefined;
  /** Invalidate all entries */
  all?: boolean | undefined;
}

/**
 * Unified cache interface for all backends
 */
export interface ICache {
  /**
   * Retrieve a value from cache
   * @returns The cached value or null if not found/expired
   */
  get<T = unknown>(key: string): Promise<T | null>;

  /**
   * Store a value in cache
   */
  set<T = unknown>(key: string, value: T, options?: CacheOptions): Promise<void>;

  /**
   * Check if a key exists in cache (and is not expired)
   */
  has(key: string): Promise<boolean>;

  /**
   * Delete a specific entry
   */
  delete(key: string): Promise<boolean>;

  /**
   * Invalidate cache entries based on criteria
   */
  invalidate(options: InvalidateOptions): Promise<number>;

  /**
   * Clear all entries
   */
  clear(): Promise<void>;

  /**
   * Get cache statistics
   */
  getStats(): Promise<CacheStatistics>;

  /**
   * Get all keys (optionally filtered by pattern)
   */
  keys(pattern?: string): Promise<string[]>;

  /**
   * Bulk get operation
   */
  getMany<T = unknown>(keys: string[]): Promise<Map<string, T>>;

  /**
   * Bulk set operation
   */
  setMany<T = unknown>(
    entries: Array<{ key: string; value: T; options?: CacheOptions }>,
  ): Promise<void>;

  /**
   * Touch entry to update last access time and extend TTL
   */
  touch(key: string): Promise<boolean>;

  /**
   * Close/cleanup the cache (for backends with persistent connections)
   */
  close(): Promise<void>;
}

/**
 * Cache event types for observability
 */
export enum CacheEventType {
  HIT = 'cache:hit',
  MISS = 'cache:miss',
  SET = 'cache:set',
  DELETE = 'cache:delete',
  INVALIDATE = 'cache:invalidate',
  CLEAR = 'cache:clear',
  ERROR = 'cache:error',
  EVICTION = 'cache:eviction',
}

/**
 * Cache event payload
 */
export interface CacheEvent {
  type: CacheEventType;
  backend: string;
  key?: string | undefined;
  keys?: string[] | undefined;
  pattern?: string | undefined;
  tags?: string[] | undefined;
  timestamp: number;
  metadata?: Record<string, unknown> | undefined;
}

/**
 * Cache event listener
 */
export type CacheEventListener = (event: CacheEvent) => void;

/**
 * Observable cache interface (extends base cache with event system)
 */
export interface IObservableCache extends ICache {
  /**
   * Subscribe to cache events
   */
  on(eventType: CacheEventType, listener: CacheEventListener): () => void;

  /**
   * Emit a cache event
   */
  emit(event: CacheEvent): void;
}

/**
 * Cache key builder utilities
 */
export const CacheKeys = {
  /**
   * Project-related keys
   */
  project: {
    byId: (id: string) => `project:${id}`,
    list: (userId: string, page: number) => `projects:user:${userId}:page:${page}`,
    stats: (id: string) => `project:${id}:stats`,
  },

  /**
   * Item-related keys
   */
  item: {
    byId: (id: string) => `item:${id}`,
    list: (projectId: string, page: number) => `items:project:${projectId}:page:${page}`,
    byType: (projectId: string, type: string) => `items:project:${projectId}:type:${type}`,
  },

  /**
   * Graph-related keys
   */
  graph: {
    layout: (graphId: string, algorithm: string) => `graph:${graphId}:layout:${algorithm}`,
    grouping: (graphId: string, strategy: string) => `graph:${graphId}:grouping:${strategy}`,
    pathfinding: (graphId: string, from: string, to: string) =>
      `graph:${graphId}:path:${from}:${to}`,
  },

  /**
   * Search-related keys
   */
  search: {
    query: (projectId: string, query: string) => `search:${projectId}:${query}`,
    facets: (projectId: string) => `search:${projectId}:facets`,
  },

  /**
   * User-related keys
   */
  user: {
    byId: (id: string) => `user:${id}`,
    profile: (id: string) => `user:${id}:profile`,
    preferences: (id: string) => `user:${id}:preferences`,
  },

  /**
   * API response keys
   */
  api: {
    response: (method: string, path: string, queryHash: string) =>
      `api:${method}:${path}:${queryHash}`,
  },
} as const;

/**
 * Helper to add jitter to TTL (prevents thundering herd)
 */
export function addJitter(ttl: number, jitterPercent: number = 0.1): number {
  const jitter = Math.random() * ttl * jitterPercent;
  return Math.floor(ttl + jitter);
}

/**
 * Helper to check if entry is expired
 */
export function isExpired(expiresAt: number | null): boolean {
  if (expiresAt === null) return false;
  return Date.now() >= expiresAt;
}

/**
 * Helper to calculate expiration timestamp
 */
export function calculateExpiration(ttl: number | null, jitter?: number): number | null {
  if (ttl === null) return null;
  const finalTTL = jitter ? addJitter(ttl, jitter) : ttl;
  return Date.now() + finalTTL;
}

/**
 * Helper to match key against glob pattern
 */
export function matchesPattern(key: string, pattern: string): boolean {
  const regex = new RegExp(`^${pattern.replace(/\*/g, '.*').replace(/\?/g, '.')}$`);
  return regex.test(key);
}

/**
 * Helper to estimate object size in bytes
 */
export function estimateSize(obj: unknown): number {
  if (obj === null || obj === undefined) return 8;

  if (typeof obj === 'string') {
    return obj.length * 2; // UTF-16
  }

  if (typeof obj === 'number') return 8;
  if (typeof obj === 'boolean') return 4;

  if (Array.isArray(obj)) {
    return obj.reduce((sum, item) => sum + estimateSize(item), 24);
  }

  if (typeof obj === 'object') {
    let size = 24; // Base object size
    for (const key in obj) {
      size += key.length * 2; // Key size
      size += estimateSize((obj as Record<string, unknown>)[key]);
    }
    return size;
  }

  return 8; // Default
}
