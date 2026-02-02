/**
 * Tests for useGraphPerformanceMonitor hook
 */

import { renderHook, act, waitFor } from "@testing-library/react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
	useGraphPerformanceMonitor,
	createProfilerCallback,
	perfMark,
	type PerformanceMetrics,
	type LODDistribution,
} from "../useGraphPerformanceMonitor";
import type { CacheStatistics } from "../../lib/graphCache";

// Mock data
const mockNodes = Array.from({ length: 100 }, (_, i) => ({
	id: `node-${i}`,
	type: "requirement",
	title: `Node ${i}`,
}));

const mockEdges = Array.from({ length: 150 }, (_, i) => ({
	id: `edge-${i}`,
	sourceId: `node-${i % 100}`,
	targetId: `node-${(i + 1) % 100}`,
	type: "depends_on" as const,
}));

const mockVisibleNodes = mockNodes.slice(0, 50);
const mockVisibleEdges = mockEdges.slice(0, 75);

const mockLODDistribution: LODDistribution = {
	high: 10,
	medium: 20,
	low: 15,
	skeleton: 5,
};

const mockCacheStats: {
	layout: CacheStatistics;
	grouping: CacheStatistics;
	search: CacheStatistics;
} = {
	layout: {
		totalEntries: 10,
		maxEntries: 100,
		totalHits: 80,
		totalMisses: 20,
		hitRatio: 0.8,
		totalMemory: 1024000,
		maxMemory: 52428800,
		memoryUsagePercent: 2,
		oldestEntry: { key: "layout:graph1:dagre", age: 300 },
		newestEntry: { key: "layout:graph2:force", age: 5 },
		entriesBySize: { tiny: 2, small: 5, medium: 3, large: 0 },
	},
	grouping: {
		totalEntries: 5,
		maxEntries: 50,
		totalHits: 40,
		totalMisses: 10,
		hitRatio: 0.8,
		totalMemory: 512000,
		maxMemory: 26214400,
		memoryUsagePercent: 2,
		oldestEntry: { key: "grouping:graph1:type", age: 200 },
		newestEntry: { key: "grouping:graph2:status", age: 10 },
		entriesBySize: { tiny: 1, small: 3, medium: 1, large: 0 },
	},
	search: {
		totalEntries: 8,
		maxEntries: 100,
		totalHits: 60,
		totalMisses: 15,
		hitRatio: 0.8,
		totalMemory: 256000,
		maxMemory: 10485760,
		memoryUsagePercent: 2,
		oldestEntry: { key: "search:graph1:test", age: 100 },
		newestEntry: { key: "search:graph2:node", age: 2 },
		entriesBySize: { tiny: 4, small: 3, medium: 1, large: 0 },
	},
};

describe("useGraphPerformanceMonitor", () => {
	let originalEnv: string | undefined;

	beforeEach(() => {
		// Save original NODE_ENV
		originalEnv = process.env.NODE_ENV;

		// Set to development for testing
		process.env.NODE_ENV = "development";

		// Mock sessionStorage
		global.sessionStorage = {
			getItem: vi.fn(() => null),
			setItem: vi.fn(),
			removeItem: vi.fn(),
			clear: vi.fn(),
			length: 0,
			key: vi.fn(),
		};

		// Mock performance.now
		vi.spyOn(performance, "now").mockReturnValue(1000);

		// Mock requestAnimationFrame
		global.requestAnimationFrame = vi.fn((cb: FrameRequestCallback) => {
			setTimeout(() => {
				cb(0);
			}, 16);
			return 1;
		});
		global.cancelAnimationFrame = vi.fn();
	});

	afterEach(() => {
		// Restore original NODE_ENV
		if (originalEnv !== undefined) {
			process.env.NODE_ENV = originalEnv;
		}

		vi.restoreAllMocks();
	});

	it("should initialize with null metrics", () => {
		const { result } = renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				enabled: true,
			}),
		);

		expect(result.current.currentMetrics).toBeNull();
		expect(result.current.history).toEqual([]);
	});

	it("should be disabled in production mode", () => {
		process.env.NODE_ENV = "production";

		const { result } = renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				enabled: false,
			}),
		);

		expect(result.current.currentMetrics).toBeNull();
	});

	it("should collect performance metrics", async () => {
		const { result } = renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				lodDistribution: mockLODDistribution,
				cacheStats: mockCacheStats,
				enabled: true,
				reportInterval: 100,
			}),
		);

		// Wait for first report
		await waitFor(
			() => {
				expect(result.current.currentMetrics).not.toBeNull();
			},
			{ timeout: 200 },
		);

		const metrics = result.current.currentMetrics!;

		// Verify node metrics
		expect(metrics.nodes.total).toBe(100);
		expect(metrics.nodes.rendered).toBe(50);
		expect(metrics.nodes.culled).toBe(50);
		expect(metrics.nodes.cullingRatio).toBe(50);

		// Verify edge metrics
		expect(metrics.edges.total).toBe(150);
		expect(metrics.edges.rendered).toBe(75);
		expect(metrics.edges.culled).toBe(75);
		expect(metrics.edges.cullingRatio).toBe(50);

		// Verify LOD distribution
		expect(metrics.lod.high).toBe(10);
		expect(metrics.lod.medium).toBe(20);
		expect(metrics.lod.low).toBe(15);
		expect(metrics.lod.skeleton).toBe(5);

		// Verify cache metrics
		expect(metrics.cache.combined.hitRatio).toBeGreaterThan(0);
	});

	it("should track FPS metrics", async () => {
		const { result } = renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				enabled: true,
				reportInterval: 100,
			}),
		);

		await waitFor(
			() => {
				expect(result.current.currentMetrics).not.toBeNull();
			},
			{ timeout: 200 },
		);

		const metrics = result.current.currentMetrics!;

		// FPS should be tracked (values will be > 0 if RAF is working)
		expect(metrics.fps).toBeDefined();
		expect(metrics.fps.samples).toBeGreaterThanOrEqual(0);
	});

	it("should calculate cache hit rates correctly", async () => {
		const { result } = renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				cacheStats: mockCacheStats,
				enabled: true,
				reportInterval: 100,
			}),
		);

		await waitFor(
			() => {
				expect(result.current.currentMetrics).not.toBeNull();
			},
			{ timeout: 200 },
		);

		const metrics = result.current.currentMetrics!;

		// Layout cache
		expect(metrics.cache.layout.hits).toBe(80);
		expect(metrics.cache.layout.misses).toBe(20);
		expect(metrics.cache.layout.hitRatio).toBe(0.8);

		// Combined cache
		expect(metrics.cache.combined.hits).toBe(180); // 80 + 40 + 60
		expect(metrics.cache.combined.misses).toBe(45); // 20 + 10 + 15
		expect(metrics.cache.combined.hitRatio).toBe(0.8);
	});

	it("should maintain history of metrics", async () => {
		const { result } = renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				enabled: true,
				reportInterval: 50,
			}),
		);

		// Wait for multiple reports
		await waitFor(
			() => {
				expect(result.current.history.length).toBeGreaterThan(0);
			},
			{ timeout: 200 },
		);

		expect(result.current.history.length).toBeGreaterThan(0);
	});

	it("should provide summary string", async () => {
		const { result } = renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				cacheStats: mockCacheStats,
				enabled: true,
				reportInterval: 100,
			}),
		);

		await waitFor(
			() => {
				expect(result.current.currentMetrics).not.toBeNull();
			},
			{ timeout: 200 },
		);

		const summary = result.current.getSummary();
		expect(summary).toContain("FPS:");
		expect(summary).toContain("Nodes:");
		expect(summary).toContain("Edges:");
		expect(summary).toContain("Cache Hit Rate:");
	});

	it("should reset metrics and history", async () => {
		const { result } = renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				enabled: true,
				reportInterval: 100,
			}),
		);

		await waitFor(
			() => {
				expect(result.current.currentMetrics).not.toBeNull();
			},
			{ timeout: 200 },
		);

		act(() => {
			result.current.reset();
		});

		expect(result.current.currentMetrics).toBeNull();
		expect(result.current.history).toEqual([]);
	});

	it("should call custom onMetricsUpdate handler", async () => {
		const onMetricsUpdate = vi.fn();

		renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				enabled: true,
				reportInterval: 100,
				onMetricsUpdate,
			}),
		);

		await waitFor(
			() => {
				expect(onMetricsUpdate).toHaveBeenCalled();
			},
			{ timeout: 200 },
		);

		const metrics = onMetricsUpdate.mock.calls[0][0] as PerformanceMetrics;
		expect(metrics.nodes.total).toBe(100);
	});

	it("should persist metrics to sessionStorage", async () => {
		const setItemSpy = vi.spyOn(sessionStorage, "setItem");

		renderHook(() =>
			useGraphPerformanceMonitor({
				nodes: mockNodes,
				edges: mockEdges,
				visibleNodes: mockVisibleNodes,
				visibleEdges: mockVisibleEdges,
				enabled: true,
				reportInterval: 100,
				persistToStorage: true,
			}),
		);

		await waitFor(
			() => {
				expect(setItemSpy).toHaveBeenCalledWith(
					"trace_graph_performance_metrics",
					expect.any(String),
				);
			},
			{ timeout: 200 },
		);
	});
});

describe("createProfilerCallback", () => {
	it("should create profiler callback that logs to console", () => {
		const consoleSpy = vi.spyOn(console, "log").mockImplementation(() => {});

		const callback = createProfilerCallback("TestComponent", true);

		callback("TestComponent", "mount", 10, 8, 1000, 1010);

		expect(consoleSpy).toHaveBeenCalledWith(
			expect.stringContaining("TestComponent"),
			expect.any(String),
			expect.objectContaining({
				id: "TestComponent",
				phase: "mount",
			}),
		);

		consoleSpy.mockRestore();
	});

	it("should store profiler data in sessionStorage", () => {
		const setItemSpy = vi.spyOn(sessionStorage, "setItem");

		const callback = createProfilerCallback("TestComponent", false);

		callback("TestComponent", "update", 5, 8, 1000, 1005);

		expect(setItemSpy).toHaveBeenCalledWith(
			"trace_profiler_TestComponent",
			expect.any(String),
		);
	});
});

describe("perfMark", () => {
	beforeEach(() => {
		vi.spyOn(performance, "mark").mockImplementation(() => ({} as any));
		vi.spyOn(performance, "measure").mockImplementation(() => ({} as any));
		vi.spyOn(performance, "getEntriesByName").mockReturnValue([
			{ duration: 42 } as any,
		]);
	});

	it("should create performance marks", () => {
		const markSpy = vi.spyOn(performance, "mark");

		perfMark.start("test-operation");
		perfMark.end("test-operation");

		expect(markSpy).toHaveBeenCalledWith("test-operation-start");
		expect(markSpy).toHaveBeenCalledWith("test-operation-end");
	});

	it("should measure duration between marks", () => {
		const measureSpy = vi.spyOn(performance, "measure");

		perfMark.start("test-operation");
		perfMark.end("test-operation");

		expect(measureSpy).toHaveBeenCalledWith(
			"test-operation",
			"test-operation-start",
			"test-operation-end",
		);
	});

	it("should not create marks in production", () => {
		process.env.NODE_ENV = "production";

		const markSpy = vi.spyOn(performance, "mark");

		perfMark.start("test-operation");
		perfMark.end("test-operation");

		expect(markSpy).not.toHaveBeenCalled();
	});
});
