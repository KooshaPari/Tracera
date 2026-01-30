import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
	createGraphCache,
	layoutCache,
	groupingCache,
	searchCache,
	clearAllCaches,
	prewarmCache,
	useGraphCache,
	cacheKeys,
} from "@/lib/graphCache";

describe("Graph Cache - LRU Implementation", () => {
	describe("Cache Creation", () => {
		it("should create a new cache with default settings", () => {
			const cache = createGraphCache();
			const stats = cache.getStats();

			expect(stats.totalEntries).toBe(0);
			expect(stats.maxEntries).toBe(100);
			expect(stats.totalMemory).toBe(0);
		});

		it("should create a cache with custom settings", () => {
			const cache = createGraphCache(50, 10485760); // 50 entries, 10 MB
			const stats = cache.getStats();

			expect(stats.maxEntries).toBe(50);
			expect(stats.maxMemory).toBe(10485760);
		});
	});

	describe("Basic Operations", () => {
		let cache: ReturnType<typeof createGraphCache>;

		beforeEach(() => {
			cache = createGraphCache();
		});

		it("should set and get values", () => {
			const value = { data: "test" };
			cache.set("key1", value);

			const retrieved = cache.get("key1");
			expect(retrieved).toEqual(value);
		});

		it("should return null for non-existent keys", () => {
			const result = cache.get("non-existent");
			expect(result).toBeNull();
		});

		it("should check key existence", () => {
			cache.set("key1", { data: "test" });

			expect(cache.has("key1")).toBe(true);
			expect(cache.has("key2")).toBe(false);
		});

		it("should delete entries", () => {
			cache.set("key1", { data: "test" });
			expect(cache.has("key1")).toBe(true);

			const deleted = cache.delete("key1");
			expect(deleted).toBe(true);
			expect(cache.has("key1")).toBe(false);
		});

		it("should return false when deleting non-existent key", () => {
			const deleted = cache.delete("non-existent");
			expect(deleted).toBe(false);
		});

		it("should clear all entries", () => {
			cache.set("key1", { data: "test1" });
			cache.set("key2", { data: "test2" });
			expect(cache.getStats().totalEntries).toBe(2);

			cache.clear();
			expect(cache.getStats().totalEntries).toBe(0);
			expect(cache.get("key1")).toBeNull();
		});
	});

	describe("LRU Eviction", () => {
		it("should evict least recently used entries when max entries exceeded", () => {
			const cache = createGraphCache(3); // Max 3 entries

			cache.set("key1", { data: "value1" });
			cache.set("key2", { data: "value2" });
			cache.set("key3", { data: "value3" });

			// Add 4th entry - should evict key1 (least recently used)
			cache.set("key4", { data: "value4" });

			expect(cache.has("key1")).toBe(false);
			expect(cache.has("key4")).toBe(true);
		});

		it("should not evict recently accessed entries", () => {
			const cache = createGraphCache(3);

			cache.set("key1", { data: "value1" });
			cache.set("key2", { data: "value2" });
			cache.set("key3", { data: "value3" });

			// Access key1 to make it recently used
			cache.get("key1");

			// Add 4th entry - should evict key2
			cache.set("key4", { data: "value4" });

			expect(cache.has("key1")).toBe(true); // Recently accessed
			expect(cache.has("key2")).toBe(false); // Evicted
		});

		it("should respect memory limits", () => {
			const cache = createGraphCache(1000, 1024); // 1 KB limit

			const largeObject = {
				data: "x".repeat(500), // ~1KB
			};

			cache.set("key1", largeObject);
			expect(cache.getStats().totalEntries).toBe(1);

			// This should trigger eviction
			cache.set("key2", largeObject);
			expect(cache.getStats().totalEntries).toBeLessThanOrEqual(1);
		});
	});

	describe("Statistics", () => {
		let cache: ReturnType<typeof createGraphCache>;

		beforeEach(() => {
			cache = createGraphCache();
		});

		it("should track hit and miss counts", () => {
			cache.set("key1", { data: "test" });

			cache.get("key1"); // Hit
			cache.get("key1"); // Hit
			cache.get("key2"); // Miss

			const stats = cache.getStats();
			expect(stats.totalHits).toBe(2);
			expect(stats.totalMisses).toBe(1);
		});

		it("should calculate hit ratio correctly", () => {
			cache.set("key1", { data: "test" });

			cache.get("key1"); // Hit
			cache.get("key1"); // Hit
			cache.get("key2"); // Miss
			cache.get("key2"); // Miss

			const stats = cache.getStats();
			expect(stats.hitRatio).toBe(0.5); // 2 hits / 4 total
		});

		it("should report cache statistics", () => {
			cache.set("key1", { data: "test" });
			cache.set("key2", { data: "test" });

			const stats = cache.getStats();

			expect(stats.totalEntries).toBe(2);
			expect(stats.maxEntries).toBe(100);
			expect(stats.totalMemory).toBeGreaterThan(0);
			expect(stats.memoryUsagePercent).toBeGreaterThan(0);
			expect(stats.oldestEntry).not.toBeNull();
			expect(stats.newestEntry).not.toBeNull();
		});

		it("should categorize entries by size", () => {
			const tinyData = { data: "x" };
			const smallData = { data: "x".repeat(100) };

			cache.set("tiny", tinyData);
			cache.set("small", smallData);

			const stats = cache.getStats();
			expect(stats.entriesBySize.tiny).toBeGreaterThan(0);
		});

		it("should reset statistics", () => {
			cache.set("key1", { data: "test" });
			cache.get("key1");
			cache.get("key1");

			const statsBefore = cache.getStats();
			expect(statsBefore.totalHits).toBe(2);

			cache.resetStats();

			const statsAfter = cache.getStats();
			expect(statsAfter.totalHits).toBe(0);
			expect(statsAfter.totalMisses).toBe(0);
		});
	});

	describe("Pattern-Based Invalidation", () => {
		let cache: ReturnType<typeof createGraphCache>;

		beforeEach(() => {
			cache = createGraphCache();
		});

		it("should invalidate entries by prefix pattern", () => {
			cache.set("layout:graph1:force", { data: "test1" });
			cache.set("layout:graph1:circle", { data: "test2" });
			cache.set("grouping:graph1:strategy", { data: "test3" });

			const count = cache.invalidatePattern("layout:*");

			expect(count).toBe(2);
			expect(cache.has("layout:graph1:force")).toBe(false);
			expect(cache.has("grouping:graph1:strategy")).toBe(true);
		});

		it("should support wildcard patterns", () => {
			cache.set("layout:graph1", { data: "test1" });
			cache.set("layout:graph2", { data: "test2" });
			cache.set("search:graph1", { data: "test3" });

			const count = cache.invalidatePattern("layout:*");

			expect(count).toBe(2);
			expect(cache.has("search:graph1")).toBe(true);
		});

		it("should return count of invalidated entries", () => {
			cache.set("key1", { data: "test" });
			cache.set("key2", { data: "test" });
			cache.set("key3", { data: "test" });

			const count = cache.invalidatePattern("key*");

			expect(count).toBe(3);
		});

		it("should find keys matching pattern", () => {
			cache.set("layout:graph1:force", { data: "test1" });
			cache.set("layout:graph1:circle", { data: "test2" });
			cache.set("layout:graph2:force", { data: "test3" });

			const keys = cache.keysMatching("layout:graph1:*");

			expect(keys).toHaveLength(2);
			expect(keys).toContain("layout:graph1:force");
			expect(keys).toContain("layout:graph1:circle");
		});
	});

	describe("Prewarming", () => {
		let cache: ReturnType<typeof createGraphCache>;

		beforeEach(() => {
			cache = createGraphCache();
		});

		it("should bulk load entries", () => {
			const entries: Array<[string, any]> = [
				["key1", { data: "value1" }],
				["key2", { data: "value2" }],
				["key3", { data: "value3" }],
			];

			cache.prewarm(entries);

			expect(cache.getStats().totalEntries).toBe(3);
			expect(cache.get("key1")).toEqual({ data: "value1" });
			expect(cache.get("key2")).toEqual({ data: "value2" });
		});

		it("should handle empty prewarm array", () => {
			cache.prewarm([]);

			expect(cache.getStats().totalEntries).toBe(0);
		});
	});

	describe("Memory Pressure", () => {
		it("should report comfortable pressure when below 70%", () => {
			const cache = createGraphCache(100, 1024); // 1 KB limit
			cache.set("key1", { data: "x" });

			const pressure = cache.getMemoryPressure();
			expect(pressure).toBe("comfortable");
		});

		it("should report caution pressure between 70-85%", () => {
			const cache = createGraphCache(100, 100); // 100 bytes limit
			const largeObject = { data: "x".repeat(50) }; // ~50 bytes

			cache.set("key1", largeObject);
			cache.set("key2", largeObject);

			const pressure = cache.getMemoryPressure();
			expect(["caution", "critical"]).toContain(pressure);
		});

		it("should report critical pressure above 85%", () => {
			const cache = createGraphCache(100, 100);
			const largeObject = { data: "x".repeat(100) };

			cache.set("key1", largeObject);

			const pressure = cache.getMemoryPressure();
			expect(pressure).toBe("critical");
		});
	});

	describe("Global Cache Instances", () => {
		afterEach(() => {
			clearAllCaches();
		});

		it("should have layout cache instance", () => {
			layoutCache.set("test", {
				positions: {},
				bounds: { minX: 0, minY: 0, maxX: 100, maxY: 100 },
			});

			const stats = layoutCache.getStats();
			expect(stats.totalEntries).toBeGreaterThan(0);
		});

		it("should have grouping cache instance", () => {
			groupingCache.set("test", {
				groupId: "g1",
				items: ["item1"],
			});

			const stats = groupingCache.getStats();
			expect(stats.totalEntries).toBeGreaterThan(0);
		});

		it("should have search cache instance", () => {
			searchCache.set("test", {
				query: "test",
				results: [],
				timestamp: Date.now(),
			});

			const stats = searchCache.getStats();
			expect(stats.totalEntries).toBeGreaterThan(0);
		});
	});

	describe("Clear All Caches", () => {
		it("should clear all global caches", () => {
			layoutCache.set("key1", {
				positions: {},
				bounds: { minX: 0, minY: 0, maxX: 100, maxY: 100 },
			});
			groupingCache.set("key2", {
				groupId: "g1",
				items: ["item1"],
			});

			clearAllCaches();

			expect(layoutCache.getStats().totalEntries).toBe(0);
			expect(groupingCache.getStats().totalEntries).toBe(0);
		});
	});

	describe("Cache Key Generators", () => {
		it("should generate layout cache keys", () => {
			const key = cacheKeys.layout("graph1", "force-directed");
			expect(key).toBe("layout:graph1:force-directed");
		});

		it("should generate grouping cache keys", () => {
			const key = cacheKeys.grouping("graph1", "hierarchical");
			expect(key).toBe("grouping:graph1:hierarchical");
		});

		it("should generate search cache keys", () => {
			const key = cacheKeys.search("graph1", "query");
			expect(key).toBe("search:graph1:query");
		});

		it("should generate pathfinding cache keys", () => {
			const key = cacheKeys.pathfinding("node1", "node2");
			expect(key).toBe("path:node1:node2");
		});

		it("should generate aggregation cache keys", () => {
			const key = cacheKeys.aggregation("sum", "param1:value1");
			expect(key).toBe("agg:sum:param1:value1");
		});
	});

	describe("useGraphCache Hook", () => {
		beforeEach(() => {
			clearAllCaches();
		});

		it("should provide cache operations", () => {
			const cache = useGraphCache();

			expect(cache.layoutCache).toBeDefined();
			expect(cache.groupingCache).toBeDefined();
			expect(cache.searchCache).toBeDefined();
			expect(cache.getStats).toBeDefined();
		});

		it("should get statistics for all caches", () => {
			const cache = useGraphCache();

			layoutCache.set("key1", {
				positions: {},
				bounds: { minX: 0, minY: 0, maxX: 100, maxY: 100 },
			});

			const stats = cache.getStats();

			expect(stats.layout).toBeDefined();
			expect(stats.grouping).toBeDefined();
			expect(stats.search).toBeDefined();
			expect(stats.total).toBeDefined();
		});
	});

	describe("Edge Cases", () => {
		it("should handle null values", () => {
			const cache = createGraphCache();
			cache.set("nullKey", null);

			expect(cache.get("nullKey")).toBeNull();
		});

		it("should handle undefined values", () => {
			const cache = createGraphCache();
			cache.set("undefinedKey", undefined);

			expect(cache.get("undefinedKey")).toBeUndefined();
		});

		it("should handle circular references without infinite loops", () => {
			const cache = createGraphCache();
			const obj: any = { data: "test" };
			obj.self = obj;

			// Should not throw
			expect(() => {
				cache.set("circularKey", obj);
			}).not.toThrow();
		});

		it("should handle very long cache keys", () => {
			const cache = createGraphCache();
			const longKey = "key".repeat(100);

			cache.set(longKey, { data: "test" });

			expect(cache.get(longKey)).toEqual({ data: "test" });
		});
	});
});
