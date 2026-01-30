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

import { create } from "zustand";

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
		tiny: number; // < 1 KB
		small: number; // 1-10 KB
		medium: number; // 10-100 KB
		large: number; // 100 KB+
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
	private totalMemory: number = 0;
	private totalHits: number = 0;
	private totalMisses: number = 0;

	constructor(maxEntries: number = 100, maxMemory: number = 52428800) {
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
			this.totalMisses++;
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
		entry.metadata.hitCount++;
		this.totalHits++;

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
				lastAccessTime: Date.now(),
				createdTime: Date.now(),
				hitCount: 0,
				missCount: 0,
				estimatedSize,
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
			"^" + pattern.replace(/\*/g, ".*").replace(/\?/g, ".") + "$",
		);
		let count = 0;

		for (const key of this.entries.keys()) {
			if (regex.test(key)) {
				this.delete(key);
				count++;
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
			"^" + pattern.replace(/\*/g, ".*").replace(/\?/g, ".") + "$",
		);
		return Array.from(this.entries.keys()).filter((key) => regex.test(key));
	}

	/**
	 * Estimate object size in bytes (rough estimate)
	 */
	private estimateSize(obj: any): number {
		if (obj === null || obj === undefined) return 8;

		if (typeof obj === "string") {
			return obj.length * 2; // UTF-16 encoding
		}

		if (typeof obj === "number") {
			return 8;
		}

		if (typeof obj === "boolean") {
			return 4;
		}

		if (Array.isArray(obj)) {
			return obj.reduce((sum, item) => sum + this.estimateSize(item), 24);
		}

		if (typeof obj === "object") {
			let size = 24; // Base object size
			for (const key in obj) {
				size += key.length * 2; // Key size
				size += this.estimateSize(obj[key]);
			}
			return size;
		}

		return 8; // Default
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
		const entries = Array.from(this.entries.entries());

		let oldestEntry: { key: string; age: number } | null = null;
		let newestEntry: { key: string; age: number } | null = null;

		if (entries.length > 0) {
			entries.sort(
				(a, b) => a[1].metadata.createdTime - b[1].metadata.createdTime,
			);
			oldestEntry = {
				key: entries[0][0],
				age: Math.round((now - entries[0][1].metadata.createdTime) / 1000),
			};
			newestEntry = {
				key: entries[entries.length - 1][0],
				age: Math.round(
					(now - entries[entries.length - 1][1].metadata.createdTime) / 1000,
				),
			};
		}

		// Categorize entries by size
		const entriesBySize = {
			tiny: 0,
			small: 0,
			medium: 0,
			large: 0,
		};

		for (const [, entry] of this.entries) {
			const size = entry.metadata.estimatedSize;
			if (size < 1024) entriesBySize.tiny++;
			else if (size < 10 * 1024) entriesBySize.small++;
			else if (size < 100 * 1024) entriesBySize.medium++;
			else entriesBySize.large++;
		}

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
				this.maxMemory === 0
					? 0
					: Math.round((this.totalMemory / this.maxMemory) * 100),
			oldestEntry,
			newestEntry,
			entriesBySize,
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
		if (percent < 0.7) return "comfortable";
		if (percent < 0.85) return "caution";
		return "critical";
	}
}

/**
 * Create a new graph cache instance
 */
export function createGraphCache<T = any>(
	maxEntries: number = 100,
	maxMemory: number = 52428800, // 50 MB
): GraphCacheImpl<T> {
	return new GraphCacheImpl(maxEntries, maxMemory);
}

/**
 * Global cache instance for layout computations
 */
export const layoutCache = createGraphCache<{
	positions: Record<string, { x: number; y: number }>;
	bounds: { minX: number; minY: number; maxX: number; maxY: number };
}>(100, 52428800); // 50 MB

/**
 * Global cache instance for grouping computations
 */
export const groupingCache = createGraphCache<{
	groupId: string;
	items: string[];
	bounds: { minX: number; minY: number; maxX: number; maxY: number };
}>(50, 26214400); // 25 MB

/**
 * Global cache instance for search results
 */
export const searchCache = createGraphCache<{
	query: string;
	results: Array<{ id: string; title: string; score: number }>;
	timestamp: number;
}>(100, 10485760); // 10 MB

/**
 * Hook to access graph cache with statistics
 */
export function useGraphCache() {
	const getLayoutStats = () => layoutCache.getStats();
	const getGroupingStats = () => groupingCache.getStats();
	const getSearchStats = () => searchCache.getStats();

	const getAllStats = () => ({
		layout: getLayoutStats(),
		grouping: getGroupingStats(),
		search: getSearchStats(),
		total: {
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
	});

	return {
		layoutCache,
		groupingCache,
		searchCache,
		getStats: getAllStats,
		getLayoutStats,
		getGroupingStats,
		getSearchStats,
	};
}

/**
 * Cache key generators
 */
export const cacheKeys = {
	layout: (graphId: string, algorithm: string) =>
		`layout:${graphId}:${algorithm}`,
	grouping: (graphId: string, strategy: string) =>
		`grouping:${graphId}:${strategy}`,
	search: (graphId: string, query: string) => `search:${graphId}:${query}`,
	pathfinding: (sourceId: string, targetId: string) =>
		`path:${sourceId}:${targetId}`,
	aggregation: (type: string, params: string) => `agg:${type}:${params}`,
};

/**
 * Precompute and warm cache with commonly accessed items
 */
export async function prewarmCache(graphId: string): Promise<void> {
	// This function is called when a graph is first loaded
	// Implement prewarming strategies based on your application's needs

	if (process.env.NODE_ENV === "development") {
		console.debug(
			"[GraphCache] Cache prewarming initiated for graph:",
			graphId,
		);
	}
}

/**
 * Clear all caches (use sparingly, typically on logout or major data changes)
 */
export function clearAllCaches(): void {
	layoutCache.clear();
	groupingCache.clear();
	searchCache.clear();

	if (process.env.NODE_ENV === "development") {
		console.debug("[GraphCache] All caches cleared");
	}
}
