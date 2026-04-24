/**
 * Lightweight graph cache utilities used across web graph modules.
 */

import { useGraphCacheOperations } from '@/stores/graph-cache-operations';

export interface GraphCacheNode {
  id: string;
  data: Record<string, unknown>;
}

export type GraphCacheValue = unknown;

export interface GraphCacheEntry {
  nodes: GraphCacheNode[];
  timestamp: number;
}

export type GraphCachePressure = 'comfortable' | 'caution' | 'critical';

export interface GraphCacheStats {
  totalEntries: number;
  maxEntries: number;
  totalMemory: number;
  maxMemory: number;
  totalHits: number;
  totalMisses: number;
  hitRatio: number;
  memoryUsagePercent: number;
  totalInvalidations: number;
  entriesBySize: {
    tiny: number;
    small: number;
    medium: number;
    large: number;
    oversized: number;
  };
  oldestEntry: string | null;
  newestEntry: string | null;
}

const CATEGORY_THRESHOLDS = {
  tiny: 256,
  small: 1024,
  medium: 32_768,
  large: 1_048_576,
};

interface CacheItem<T> {
  key: string;
  value: T;
  size: number;
  createdAt: number;
  lastAccessedAt: number;
}

interface CacheStoreConfig {
  maxEntries: number;
  maxMemory: number;
}

class BaseLRUCache<T> {
  private readonly store = new Map<string, CacheItem<T>>();
  private readonly config: CacheStoreConfig;
  private totalMemory = 0;
  private hits = 0;
  private misses = 0;
  private invalidations = 0;

  constructor(config: Partial<CacheStoreConfig> = {}) {
    this.config = {
      maxEntries: config.maxEntries ?? 100,
      maxMemory: config.maxMemory ?? 10 * 1024 * 1024,
    };
  }

  private estimateSize(value: T): number {
    if (value === undefined) {
      return 4;
    }

    if (value === null) {
      return 4;
    }

    if (typeof value === 'string') {
      return value.length * 2;
    }

    try {
      return JSON.stringify(value)?.length ?? 16;
    } catch {
      return 128;
    }
  }

  private computeMemoryRatio(): number {
    if (this.config.maxMemory <= 0) {
      return 0;
    }

    return (this.totalMemory / this.config.maxMemory) * 100;
  }

  private computeSizeCategory(size: number): keyof GraphCacheStats['entriesBySize'] {
    if (size <= CATEGORY_THRESHOLDS.tiny) {
      return 'tiny';
    }

    if (size <= CATEGORY_THRESHOLDS.small) {
      return 'small';
    }

    if (size <= CATEGORY_THRESHOLDS.medium) {
      return 'medium';
    }

    if (size <= CATEGORY_THRESHOLDS.large) {
      return 'large';
    }

    return 'oversized';
  }

  private pruneIfNeeded(): void {
    const keys = [...this.store.keys()];
    while (this.store.size > this.config.maxEntries || this.totalMemory > this.config.maxMemory) {
      const oldestKey = keys.shift();
      if (oldestKey === undefined) {
        break;
      }

      const oldest = this.store.get(oldestKey);
      if (!oldest) {
        this.store.delete(oldestKey);
        continue;
      }

      this.totalMemory -= oldest.size;
      this.store.delete(oldestKey);
      this.invalidations += 1;
    }
  }

  private patternToRegex(pattern: string): RegExp {
    const escaped = pattern.replace(/[.+?^${}()|[\]\\]/g, '\\$&');
    const withWildcard = escaped.replace(/\*/g, '.*');
    return new RegExp(`^${withWildcard}$`);
  }

  set(key: string, value: T): void {
    const now = Date.now();
    const existing = this.store.get(key);
    const size = this.estimateSize(value);

    if (existing) {
      this.totalMemory -= existing.size;
    }

    const item: CacheItem<T> = {
      key,
      value,
      size,
      createdAt: existing?.createdAt ?? now,
      lastAccessedAt: now,
    };

    this.store.delete(key);
    this.store.set(key, item);
    this.totalMemory += size;

    this.pruneIfNeeded();
  }

  get(key: string): T | null {
    const item = this.store.get(key);
    if (!item) {
      this.misses += 1;
      return null;
    }

    this.hits += 1;
    item.lastAccessedAt = Date.now();
    this.store.delete(key);
    this.store.set(key, item);
    return item.value;
  }

  has(key: string): boolean {
    return this.store.has(key);
  }

  delete(key: string): boolean {
    const existing = this.store.get(key);
    if (!existing) {
      return false;
    }

    this.totalMemory -= existing.size;
    this.store.delete(key);
    this.invalidations += 1;
    return true;
  }

  clear(): void {
    this.store.clear();
    this.totalMemory = 0;
  }

  getStats(): GraphCacheStats {
    const entriesBySize = {
      tiny: 0,
      small: 0,
      medium: 0,
      large: 0,
      oversized: 0,
    } as GraphCacheStats['entriesBySize'];

    for (const item of this.store.values()) {
      entriesBySize[this.computeSizeCategory(item.size)] += 1;
    }

    const totalRequests = this.hits + this.misses;
    const memoryUsagePercent = this.computeMemoryRatio();
    const hitRatio = totalRequests === 0 ? 0 : this.hits / totalRequests;

    const keys = [...this.store.keys()];

    return {
      totalEntries: this.store.size,
      maxEntries: this.config.maxEntries,
      totalMemory: this.totalMemory,
      maxMemory: this.config.maxMemory,
      totalHits: this.hits,
      totalMisses: this.misses,
      hitRatio,
      memoryUsagePercent,
      totalInvalidations: this.invalidations,
      entriesBySize,
      oldestEntry: keys[0] ?? null,
      newestEntry: keys[keys.length - 1] ?? null,
    };
  }

  prewarm(entries: [string, T][]): void {
    for (const [key, value] of entries) {
      this.set(key, value);
    }
  }

  invalidatePattern(pattern: string): number {
    const regex = this.patternToRegex(pattern);
    let count = 0;

    for (const key of [...this.store.keys()]) {
      if (regex.test(key)) {
        if (this.delete(key)) {
          count += 1;
        }
      }
    }

    return count;
  }

  keysMatching(pattern: string): string[] {
    const regex = this.patternToRegex(pattern);
    return [...this.store.keys()].filter((key) => regex.test(key));
  }

  getMemoryPressure(): GraphCachePressure {
    const ratio = this.computeMemoryRatio();

    if (ratio >= 85) {
      return 'critical';
    }

    if (ratio >= 70) {
      return 'caution';
    }

    return 'comfortable';
  }

  resetStats(): void {
    this.hits = 0;
    this.misses = 0;
    this.invalidations = 0;
  }
}

const cacheFactory = (maxEntries?: number, maxMemory?: number): BaseLRUCache<GraphCacheValue> =>
  new BaseLRUCache({
    ...(maxEntries !== undefined && { maxEntries }),
    ...(maxMemory !== undefined && { maxMemory }),
  });

export const graphCache = new Map<string, GraphCacheEntry>();
export const groupingCache = cacheFactory();
export const layoutCache = cacheFactory();
export const searchCache = cacheFactory();

export const cacheKeys = {
  layout: (graphId: string, layout: string): string => `layout:${graphId}:${layout}`,
  grouping: (graphId: string, strategy: string): string => `grouping:${graphId}:${strategy}`,
  search: (graphId: string, query: string): string => `search:${graphId}:${query}`,
  pathfinding: (source: string, target: string): string => `path:${source}:${target}`,
  aggregation: (name: string, query: string): string => `agg:${name}:${query}`,
};

export const createGraphCache = (
  maxEntries = 100,
  maxMemory = 10 * 1024 * 1024,
): BaseLRUCache<GraphCacheValue> =>
  cacheFactory(maxEntries, maxMemory);

export function clearAllCaches(): void {
  graphCache.clear();
  layoutCache.clear();
  groupingCache.clear();
  searchCache.clear();
}

export function useGraphCache() {
  const ops = useGraphCacheOperations();

  return {
    ...ops,
    layoutCache,
    groupingCache,
    searchCache,
    getStats: () => ({
      layout: layoutCache.getStats(),
      grouping: groupingCache.getStats(),
      search: searchCache.getStats(),
      total: {
        layout: layoutCache.getStats().totalEntries,
        grouping: groupingCache.getStats().totalEntries,
        search: searchCache.getStats().totalEntries,
        totalEntries:
          layoutCache.getStats().totalEntries +
          groupingCache.getStats().totalEntries +
          searchCache.getStats().totalEntries,
        totalMemory:
          layoutCache.getStats().totalMemory +
          groupingCache.getStats().totalMemory +
          searchCache.getStats().totalMemory,
        totalHits:
          layoutCache.getStats().totalHits +
          groupingCache.getStats().totalHits +
          searchCache.getStats().totalHits,
        totalMisses:
          layoutCache.getStats().totalMisses +
          groupingCache.getStats().totalMisses +
          searchCache.getStats().totalMisses,
      },
    }),
    layoutCacheKey: cacheKeys.layout,
    groupingCacheKey: cacheKeys.grouping,
    searchCacheKey: cacheKeys.search,
  };
}

export function getCacheKey(viewport: { x: number; y: number; zoom: number }): string {
  return `${viewport.x}:${viewport.y}:${viewport.zoom}`;
}

export function setCache(key: string, entry: GraphCacheEntry | GraphCacheNode[]): void {
  graphCache.set(key, Array.isArray(entry) ? { nodes: entry, timestamp: Date.now() } : entry);
}

export function getCache(key: string): GraphCacheEntry | undefined {
  return graphCache.get(key);
}

export function clearCache(): void {
  graphCache.clear();
}
