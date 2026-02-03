/**
 * LRU Cache for Graph Data
 *
 * Provides in-memory caching of expensive graph computations (layouts, transforms, aggregations)
 * with automatic LRU eviction when capacity limits are reached.
 *
 * Features:
 * - Configurable max entries and max memory
 * - LRU eviction strategy
 * - Memory pressure awareness
 * - Cache statistics and monitoring
 * - Pattern-based invalidation
 * - Prewarming support
 */

import { logger } from "@/lib/logger";

const DEFAULT_MAX_ENTRIES = Number("100");
const DEFAULT_MAX_MEMORY_BYTES = Number("52428800");
const GROUPING_CACHE_MAX_ENTRIES = Number("50");
const GROUPING_CACHE_MAX_MEMORY_BYTES = Number("26214400");
const SEARCH_CACHE_MAX_ENTRIES = Number("100");
const SEARCH_CACHE_MAX_MEMORY_BYTES = Number("10485760");
const LAYOUT_CACHE_MAX_ENTRIES = Number("100");
const LAYOUT_CACHE_MAX_MEMORY_BYTES = Number("52428800");

const BYTE_SIZE_DEFAULT = Number("8");
const BYTES_PER_CHAR = Number("2");
const BYTES_PER_KILOBYTE = Number("1024");
const DEFAULT_ARRAY_OVERHEAD_BYTES = Number("24");
const DEFAULT_OBJECT_OVERHEAD_BYTES = Number("24");
const DEFAULT_INDEX_ENTRY_BYTES = Number("40");
const BOOLEAN_BYTES = Number("4");
const MILLISECONDS_PER_SECOND = Number("1000");
const MEMORY_PRESSURE_CAUTION = Number("0.7");
const MEMORY_PRESSURE_CRITICAL = Number("0.85");
const PERCENT_SCALE = Number("100");
const SIZE_SMALL_LIMIT = Number("10") * BYTES_PER_KILOBYTE;
const SIZE_MEDIUM_LIMIT = Number("100") * BYTES_PER_KILOBYTE;

/**
 * Cache entry metadata
 */
interface CacheEntryMetadata {
	/** Last access timestamp */
	lastAccessTime: number;
	/** Creation timestamp */
	createdTime: number;
	/** Number of cache hits */
	hitCount: number;
	/** Number of cache misses */
	missCount: number;
	/** Estimated size in bytes */
	estimatedSize: number;
}

/**
 * Cache entry
 */
interface CacheEntry<T> {
	value: T;
	metadata: CacheEntryMetadata;
}

type EntryAge = { age: number; key: string };

type EntryAgeSummary = {
	newestEntry: EntryAge | null;
	oldestEntry: EntryAge | null;
};

/**
 * Cache statistics
 */
export interface CacheStatistics {
	totalEntries: number;
	maxEntries: number;
	totalHits: number;
	totalMisses: number;
	hitRatio: number;
	totalMemory: number;
	maxMemory: number;
	memoryUsagePercent: number;
	oldestEntry: { key: string; age: number } | null;
	newestEntry: { key: string; age: number } | null;
	entriesBySize: {
		large: number; // 100 KB+
		medium: number; // 10-100 KB
		small: number; // 1-10 KB
		tiny: number; // < 1 KB
	};
}

/**
 * LRU Cache implementation
 */
class GraphCacheImpl<T = any> {
	private entries: Map<string, CacheEntry<T>> = new Map();
	private lruOrder: string[] = []; // Most recently used at end
	private readonly maxEntries: number;
	private readonly maxMemory: number;
	private totalMemory = 0;
	private totalHits = 0;
	private totalMisses = 0;

	constructor(
		maxEntries: number = DEFAULT_MAX_ENTRIES,
		maxMemory: number = DEFAULT_MAX_MEMORY_BYTES,
	) {
		// 50 MB default
		this.maxEntries = maxEntries;
		this.maxMemory = maxMemory;
	}

	/**
	 * Get a value from cache
	 */
	get(key: string): T | null {
		const entry = this.entries.get(key);

		if (!entry) {
			this.totalMisses += 1;
			return null;
		}

		// Update LRU order
		const index = this.lruOrder.indexOf(key);
		if (index > -1) {
			this.lruOrder.splice(index, 1);
		}
		this.lruOrder.push(key);

		// Update metadata
		entry.metadata.lastAccessTime = Date.now();
		entry.metadata.hitCount += 1;
		this.totalHits += 1;

		return entry.value;
	}

	/**
	 * Set a value in cache
	 */
	set(key: string, value: T): void {
		const estimatedSize = this.estimateSize(value);

		// Remove old entry if exists
		if (this.entries.has(key)) {
			const oldSize = this.entries.get(key)!.metadata.estimatedSize;
			this.totalMemory -= oldSize;
			const index = this.lruOrder.indexOf(key);
			if (index > -1) {
				this.lruOrder.splice(index, 1);
			}
		}

		// Evict entries if necessary
		while (
			(this.totalMemory + estimatedSize > this.maxMemory ||
				this.entries.size >= this.maxEntries) &&
			this.entries.size > 0 &&
			!this.entries.has(key)
		) {
			this.evictLRU();
		}

		// Store entry
		this.entries.set(key, {
			value,
			metadata: {
				createdTime: Date.now(),
				estimatedSize,
				hitCount: 0,
				lastAccessTime: Date.now(),
				missCount: 0,
			},
		});

		this.lruOrder.push(key);
		this.totalMemory += estimatedSize;
	}

	/**
	 * Check if key exists in cache
	 */
	has(key: string): boolean {
		return this.entries.has(key);
	}

	/**
	 * Delete a specific entry
	 */
	delete(key: string): boolean {
		const entry = this.entries.get(key);
		if (!entry) return false;

		this.totalMemory -= entry.metadata.estimatedSize;
		this.entries.delete(key);

		const index = this.lruOrder.indexOf(key);
		if (index > -1) {
			this.lruOrder.splice(index, 1);
		}

		return true;
	}

	/**
	 * Clear all entries
	 */
	clear(): void {
		this.entries.clear();
		this.lruOrder = [];
		this.totalMemory = 0;
		this.totalHits = 0;
		this.totalMisses = 0;
	}

	/**
	 * Invalidate entries matching a pattern
	 * Pattern uses simple glob-like matching: "prefix:*" matches keys starting with "prefix:"
	 */
	invalidatePattern(pattern: string): number {
		const regex = new RegExp(
			`^${pattern.replace(/\*/g, ".*").replace(/\?/g, ".")}$`,
		);
		let count = 0;

		for (const key of this.entries.keys()) {
			if (regex.test(key)) {
				this.delete(key);
				count += 1;
			}
		}

		return count;
	}

	/**
	 * Bulk load entries (for prewarming)
	 */
	prewarm(entries: Array<[string, T]>): void {
		for (const [key, value] of entries) {
			this.set(key, value);
		}
	}

	/**
	 * Get all keys matching a pattern
	 */
	keysMatching(pattern: string): string[] {
		const regex = new RegExp(
			`^${pattern.replace(/\*/g, ".*").replace(/\?/g, ".")}$`,
		);
		return [...this.entries.keys()].filter((key) => regex.test(key));
	}

	/**
	 * Estimate object size in bytes (rough estimate)
	 */
	private estimateSize(obj: any): number {
		if (obj === null || obj === undefined) return BYTE_SIZE_DEFAULT;

		if (typeof obj === "string") {
			return obj.length * BYTES_PER_CHAR; // UTF-16 encoding
		}

		if (typeof obj === "number") {
			return BYTE_SIZE_DEFAULT;
		}

		if (typeof obj === "boolean") {
			return BOOLEAN_BYTES;
		}

		if (Array.isArray(obj)) {
			return obj.reduce(
				(sum, item) => sum + this.estimateSize(item),
				DEFAULT_ARRAY_OVERHEAD_BYTES,
			);
		}

		if (typeof obj === "object") {
			let size = DEFAULT_OBJECT_OVERHEAD_BYTES; // Base object size
			for (const key in obj) {
				size += key.length * BYTES_PER_CHAR; // Key size
				size += this.estimateSize(obj[key]);
			}
			return size;
		}

		return BYTE_SIZE_DEFAULT; // Default
	}

	/**
	 * Evict the least recently used entry
	 */
	private evictLRU(): void {
		if (this.lruOrder.length === 0) return;

		const keyToEvict = this.lruOrder[0];
		this.delete(keyToEvict);
	}

	/**
	 * Get cache statistics
	 */
	getStats(): CacheStatistics {
		const now = Date.now();
		const entries = [...this.entries.entries()];
		const ageSummary = this.getEntryAgeSummary(entries, now);
		const entriesBySize = this.getEntriesBySize();
		const totalRequests = this.totalHits + this.totalMisses;
		const hitRatio = totalRequests === 0 ? 0 : this.totalHits / totalRequests;
		const memoryUsagePercent =
			this.maxMemory === 0
				? 0
				: Math.round((this.totalMemory / this.maxMemory) * PERCENT_SCALE);

		return {
			entriesBySize,
			hitRatio,
			maxEntries: this.maxEntries,
			maxMemory: this.maxMemory,
			memoryUsagePercent,
			newestEntry: ageSummary.newestEntry,
			oldestEntry: ageSummary.oldestEntry,
			totalEntries: this.entries.size,
			totalHits: this.totalHits,
			totalMemory: this.totalMemory,
			totalMisses: this.totalMisses,
		};
	}

	/**
	 * Reset statistics without clearing cache
	 */
	resetStats(): void {
		this.totalHits = 0;
		this.totalMisses = 0;
	}

	/**
	 * Get detailed entry information
	 */
	getEntryInfo(key: string): CacheEntryMetadata | null {
		return this.entries.get(key)?.metadata || null;
	}

	/**
	 * Get memory pressure status
	 */
	getMemoryPressure(): "comfortable" | "caution" | "critical" {
		const percent = this.totalMemory / this.maxMemory;
		if (percent < MEMORY_PRESSURE_CAUTION) return "comfortable";
		if (percent < MEMORY_PRESSURE_CRITICAL) return "caution";
		return "critical";
	}

	private getEntryAgeSummary(
		entries: Array<[string, CacheEntry<T>]>,
		now: number,
	): EntryAgeSummary {
		let oldestEntry: EntryAge | null = null;
		let newestEntry: EntryAge | null = null;

		if (entries.length === 0) {
			return { newestEntry, oldestEntry };
		}

		entries.sort(
			(a, b) => a[1].metadata.createdTime - b[1].metadata.createdTime,
		);
		oldestEntry = {
			age: Math.round(
				(now - entries[0][1].metadata.createdTime) /
					MILLISECONDS_PER_SECOND,
			),
			key: entries[0][0],
		};
		newestEntry = {
			age: Math.round(
				(now - entries[entries.length - 1][1].metadata.createdTime) /
					MILLISECONDS_PER_SECOND,
			),
			key: entries[entries.length - 1][0],
		};

		return { newestEntry, oldestEntry };
	}

	private getEntriesBySize(): CacheStatistics["entriesBySize"] {
		const entriesBySize = {
			large: 0,
			medium: 0,
			small: 0,
			tiny: 0,
		};

		for (const [, entry] of this.entries) {
			const size = entry.metadata.estimatedSize;
			if (size < BYTES_PER_KILOBYTE) {
				entriesBySize.tiny += 1;
			} else if (size < SIZE_SMALL_LIMIT) {
				entriesBySize.small += 1;
			} else if (size < SIZE_MEDIUM_LIMIT) {
				entriesBySize.medium += 1;
			} else {
				entriesBySize.large += 1;
			}
		}

		return entriesBySize;
	}
}

/**
 * Create a new graph cache instance
 */
export const createGraphCache = <T = any>(
	maxEntries: number = DEFAULT_MAX_ENTRIES,
	maxMemory: number = DEFAULT_MAX_MEMORY_BYTES, // 50 MB
): GraphCacheImpl<T> => new GraphCacheImpl(maxEntries, maxMemory);

/**
 * Global cache instance for layout computations
 */
export const layoutCache = createGraphCache<{
	positions: Record<string, { x: number; y: number }>;
	bounds: { minX: number; minY: number; maxX: number; maxY: number };
}>(LAYOUT_CACHE_MAX_ENTRIES, LAYOUT_CACHE_MAX_MEMORY_BYTES); // 50 MB

/**
 * Global cache instance for grouping computations
 */
export const groupingCache = createGraphCache<{
	groupId: string;
	items: string[];
	bounds: { minX: number; minY: number; maxX: number; maxY: number };
}>(GROUPING_CACHE_MAX_ENTRIES, GROUPING_CACHE_MAX_MEMORY_BYTES); // 25 MB

/**
 * Global cache instance for search results
 */
export const searchCache = createGraphCache<{
	query: string;
	results: Array<{ id: string; title: string; score: number }>;
	timestamp: number;
}>(SEARCH_CACHE_MAX_ENTRIES, SEARCH_CACHE_MAX_MEMORY_BYTES); // 10 MB

type GraphCacheStatsSummary = {
	grouping: CacheStatistics;
	layout: CacheStatistics;
	search: CacheStatistics;
	total: {
		totalEntries: number;
		totalHits: number;
		totalMemory: number;
		totalMisses: number;
	};
};

type GraphCacheHook = {
	getGroupingStats: () => CacheStatistics;
	getLayoutStats: () => CacheStatistics;
	getSearchStats: () => CacheStatistics;
	getStats: () => GraphCacheStatsSummary;
	groupingCache: GraphCacheImpl<{ groupId: string; items: string[]; bounds: { minX: number; minY: number; maxX: number; maxY: number } }>;
	layoutCache: GraphCacheImpl<{ positions: Record<string, { x: number; y: number }>; bounds: { minX: number; minY: number; maxX: number; maxY: number } }>;
	searchCache: GraphCacheImpl<{ query: string; results: Array<{ id: string; title: string; score: number }>; timestamp: number }>;
};

/**
 * Hook to access graph cache with statistics
 */
export const useGraphCache = (): GraphCacheHook => {
	const getLayoutStats = (): CacheStatistics => layoutCache.getStats();
	const getGroupingStats = (): CacheStatistics => groupingCache.getStats();
	const getSearchStats = (): CacheStatistics => searchCache.getStats();

	const getAllStats = (): GraphCacheStatsSummary => ({
		grouping: getGroupingStats(),
		layout: getLayoutStats(),
		search: getSearchStats(),
		total: {
			totalEntries:
				layoutCache.getStats().totalEntries +
				groupingCache.getStats().totalEntries +
				searchCache.getStats().totalEntries,
			totalHits:
				layoutCache.getStats().totalHits +
				groupingCache.getStats().totalHits +
				searchCache.getStats().totalHits,
			totalMemory:
				layoutCache.getStats().totalMemory +
				groupingCache.getStats().totalMemory +
				searchCache.getStats().totalMemory,
			totalMisses:
				layoutCache.getStats().totalMisses +
				groupingCache.getStats().totalMisses +
				searchCache.getStats().totalMisses,
		},
	});

	return {
		getGroupingStats,
		getLayoutStats,
		getSearchStats,
		getStats: getAllStats,
		groupingCache,
		layoutCache,
		searchCache,
	};
};

/**
 * Cache key generators
 */
export const cacheKeys = {
	aggregation: (type: string, params: string) => `agg:${type}:${params}`,
	grouping: (graphId: string, strategy: string) =>
		`grouping:${graphId}:${strategy}`,
	layout: (graphId: string, algorithm: string) =>
		`layout:${graphId}:${algorithm}`,
	pathfinding: (sourceId: string, targetId: string) =>
		`path:${sourceId}:${targetId}`,
	search: (graphId: string, query: string) => `search:${graphId}:${query}`,
};

/**
 * Precompute and warm cache with commonly accessed items
 */
export const prewarmCache = async (graphId: string): Promise<void> => {
	// This function is called when a graph is first loaded
	// Implement prewarming strategies based on your application's needs

	if (process.env["NODE_ENV"] === "development") {
		logger.debug("[GraphCache] Cache prewarming initiated for graph:", graphId);
	}
};

/**
 * Clear all caches (use sparingly, typically on logout or major data changes)
 */
export const clearAllCaches = (): void => {
	layoutCache.clear();
	groupingCache.clear();
	searchCache.clear();

	if (process.env["NODE_ENV"] === "development") {
		logger.debug("[GraphCache] All caches cleared");
	}
};
