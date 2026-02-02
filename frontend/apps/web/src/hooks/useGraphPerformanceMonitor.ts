/**
 * Graph Performance Monitor Hook
 *
 * Comprehensive performance monitoring for graph visualizations using:
 * - Performance API for accurate timing measurements
 * - React DevTools Profiler API for render performance
 * - Custom metrics tracking for optimization effectiveness
 *
 * Tracks:
 * - FPS during pan/zoom operations
 * - Node/Edge render counts vs totals (viewport culling effectiveness)
 * - LOD (Level of Detail) distribution
 * - Cache hit rates (layout, grouping, search)
 * - Viewport load times
 * - Memory usage and GC pressure
 *
 * Usage:
 * ```tsx
 * const monitor = useGraphPerformanceMonitor({
 *   nodes,
 *   edges,
 *   visibleNodes,
 *   visibleEdges,
 *   lodDistribution,
 *   cacheStats,
 *   enabled: process.env.NODE_ENV === 'development',
 * });
 *
 * // Metrics automatically logged to console and stored in sessionStorage
 * // Access current metrics: monitor.currentMetrics
 * // Force report: monitor.reportMetrics()
 * ```
 */

import { useCallback, useEffect, useRef, useState } from "react";
import type { CacheStatistics } from "@/lib/graphCache";
import { logger } from '@/lib/logger';

/** Performance metrics snapshot */
export interface PerformanceMetrics {
	/** Timestamp when metrics were captured */
	timestamp: number;

	/** Frames per second during interaction */
	fps: {
		current: number;
		average: number;
		min: number;
		max: number;
		samples: number;
	};

	/** Node rendering metrics */
	nodes: {
		total: number;
		rendered: number;
		culled: number;
		cullingRatio: number; // Percentage of nodes culled
	};

	/** Edge rendering metrics */
	edges: {
		total: number;
		rendered: number;
		culled: number;
		cullingRatio: number; // Percentage of edges culled
	};

	/** LOD (Level of Detail) distribution */
	lod: {
		high: number; // Full detail nodes
		medium: number; // Simplified nodes
		low: number; // Minimal nodes
		skeleton: number; // Loading/error skeletons
	};

	/** Cache performance metrics */
	cache: {
		layout: CacheHitRateMetrics;
		grouping: CacheHitRateMetrics;
		search: CacheHitRateMetrics;
		combined: CacheHitRateMetrics;
	};

	/** Viewport and rendering timing */
	timing: {
		viewportLoadMs: number; // Time to render current viewport
		layoutComputeMs: number; // Time to compute layout
		cullingMs: number; // Time spent on viewport culling
		renderMs: number; // Total render time
	};

	/** Memory metrics (if available) */
	memory?: {
		usedJSHeapSize: number; // Bytes
		totalJSHeapSize: number; // Bytes
		jsHeapSizeLimit: number; // Bytes
		heapUsagePercent: number;
	};

	/** Interaction metrics */
	interaction: {
		isPanning: boolean;
		isZooming: boolean;
		panDuration: number; // ms
		zoomDuration: number; // ms
		lastInteractionType: "pan" | "zoom" | "idle";
	};
}

/** Cache hit rate metrics */
interface CacheHitRateMetrics {
	hits: number;
	misses: number;
	hitRatio: number; // 0-1
	totalRequests: number;
}

/** LOD level distribution input */
export interface LODDistribution {
	high: number;
	medium: number;
	low: number;
	skeleton?: number;
}

/** Hook configuration */
export interface UseGraphPerformanceMonitorConfig {
	/** Total nodes in graph */
	nodes: any[];
	/** Total edges in graph */
	edges: any[];
	/** Currently visible/rendered nodes */
	visibleNodes: any[];
	/** Currently visible/rendered edges */
	visibleEdges: any[];
	/** LOD level distribution */
	lodDistribution?: LODDistribution;
	/** Cache statistics from graph caches */
	cacheStats?: {
		layout?: CacheStatistics;
		grouping?: CacheStatistics;
		search?: CacheStatistics;
	};
	/** Enable monitoring (default: true in dev, false in prod) */
	enabled?: boolean;
	/** Report interval in ms (default: 5000) */
	reportInterval?: number;
	/** Enable console logging (default: true in dev) */
	logToConsole?: boolean;
	/** Enable sessionStorage persistence (default: true in dev) */
	persistToStorage?: boolean;
	/** Custom metric handlers */
	onMetricsUpdate?: (metrics: PerformanceMetrics) => void;
}

/** Hook return value */
export interface GraphPerformanceMonitor {
	/** Current performance metrics */
	currentMetrics: PerformanceMetrics | null;
	/** Historical metrics (last N snapshots) */
	history: PerformanceMetrics[];
	/** Force immediate metric collection and report */
	reportMetrics: () => void;
	/** Clear history and reset counters */
	reset: () => void;
	/** Get metrics summary for display */
	getSummary: () => string;
}

/** FPS tracker using requestAnimationFrame */
class FPSTracker {
	private frames: number[] = [];
	private lastFrameTime: number = performance.now();
	private rafId: number | null = null;
	private isRunning: boolean = false;

	start(): void {
		if (this.isRunning) return;
		this.isRunning = true;
		this.tick();
	}

	stop(): void {
		this.isRunning = false;
		if (this.rafId !== null) {
			cancelAnimationFrame(this.rafId);
			this.rafId = null;
		}
	}

	private tick = (): void => {
		if (!this.isRunning) return;

		const now = performance.now();
		const delta = now - this.lastFrameTime;
		this.lastFrameTime = now;

		if (delta > 0) {
			const fps = 1000 / delta;
			this.frames.push(fps);

			// Keep only last 60 frames (1 second at 60fps)
			if (this.frames.length > 60) {
				this.frames.shift();
			}
		}

		this.rafId = requestAnimationFrame(this.tick);
	};

	getMetrics(): {
		current: number;
		average: number;
		min: number;
		max: number;
		samples: number;
	} {
		if (this.frames.length === 0) {
			return { current: 0, average: 0, min: 0, max: 0, samples: 0 };
		}

		const current = this.frames[this.frames.length - 1] || 0;
		const average =
			this.frames.reduce((sum, fps) => sum + fps, 0) / this.frames.length;
		const min = Math.min(...this.frames);
		const max = Math.max(...this.frames);

		return {
			current: Math.round(current),
			average: Math.round(average),
			min: Math.round(min),
			max: Math.round(max),
			samples: this.frames.length,
		};
	}

	reset(): void {
		this.frames = [];
		this.lastFrameTime = performance.now();
	}
}

/** Interaction tracker */
class InteractionTracker {
	private isPanning: boolean = false;
	private isZooming: boolean = false;
	private panStartTime: number = 0;
	private zoomStartTime: number = 0;
	private lastInteractionType: "pan" | "zoom" | "idle" = "idle";

	startPan(): void {
		if (!this.isPanning) {
			this.isPanning = true;
			this.panStartTime = performance.now();
			this.lastInteractionType = "pan";
		}
	}

	endPan(): void {
		this.isPanning = false;
	}

	startZoom(): void {
		if (!this.isZooming) {
			this.isZooming = true;
			this.zoomStartTime = performance.now();
			this.lastInteractionType = "zoom";
		}
	}

	endZoom(): void {
		this.isZooming = false;
	}

	getMetrics() {
		const now = performance.now();
		return {
			isPanning: this.isPanning,
			isZooming: this.isZooming,
			panDuration: this.isPanning ? now - this.panStartTime : 0,
			zoomDuration: this.isZooming ? now - this.zoomStartTime : 0,
			lastInteractionType: this.lastInteractionType,
		};
	}

	reset(): void {
		this.isPanning = false;
		this.isZooming = false;
		this.panStartTime = 0;
		this.zoomStartTime = 0;
		this.lastInteractionType = "idle";
	}
}

/** Storage key for persisted metrics */
const STORAGE_KEY = "trace_graph_performance_metrics";

/** Maximum history entries to keep */
const MAX_HISTORY_LENGTH = 50;

/**
 * Graph Performance Monitor Hook
 */
export function useGraphPerformanceMonitor({
	nodes,
	edges,
	visibleNodes,
	visibleEdges,
	lodDistribution,
	cacheStats,
	enabled = process.env.NODE_ENV === "development",
	reportInterval = 5000,
	logToConsole = process.env.NODE_ENV === "development",
	persistToStorage = process.env.NODE_ENV === "development",
	onMetricsUpdate,
}: UseGraphPerformanceMonitorConfig): GraphPerformanceMonitor {
	const [currentMetrics, setCurrentMetrics] =
		useState<PerformanceMetrics | null>(null);
	const [history, setHistory] = useState<PerformanceMetrics[]>([]);

	// Trackers
	const fpsTracker = useRef<FPSTracker>(new FPSTracker());
	const interactionTracker = useRef<InteractionTracker>(
		new InteractionTracker(),
	);

	// Timing markers
	const timingMarkers = useRef<{
		viewportLoadStart?: number;
		layoutComputeStart?: number;
		cullingStart?: number;
		renderStart?: number;
	}>({});

	/** Collect current performance metrics */
	const collectMetrics = useCallback((): PerformanceMetrics => {
		const now = performance.now();

		// FPS metrics
		const fps = fpsTracker.current.getMetrics();

		// Node/Edge culling metrics
		const nodeTotal = nodes.length;
		const nodeRendered = visibleNodes.length;
		const nodeCulled = nodeTotal - nodeRendered;
		const nodeCullingRatio =
			nodeTotal > 0 ? (nodeCulled / nodeTotal) * 100 : 0;

		const edgeTotal = edges.length;
		const edgeRendered = visibleEdges.length;
		const edgeCulled = edgeTotal - edgeRendered;
		const edgeCullingRatio =
			edgeTotal > 0 ? (edgeCulled / edgeTotal) * 100 : 0;

		// LOD distribution
		const lod = {
			high: lodDistribution?.high ?? 0,
			medium: lodDistribution?.medium ?? 0,
			low: lodDistribution?.low ?? 0,
			skeleton: lodDistribution?.skeleton ?? 0,
		};

		// Cache metrics
		const getCacheMetrics = (
			stats?: CacheStatistics,
		): CacheHitRateMetrics => {
			if (!stats) {
				return { hits: 0, misses: 0, hitRatio: 0, totalRequests: 0 };
			}
			return {
				hits: stats.totalHits,
				misses: stats.totalMisses,
				hitRatio: stats.hitRatio,
				totalRequests: stats.totalHits + stats.totalMisses,
			};
		};

		const layoutCache = getCacheMetrics(cacheStats?.layout);
		const groupingCache = getCacheMetrics(cacheStats?.grouping);
		const searchCache = getCacheMetrics(cacheStats?.search);
		const combinedCache: CacheHitRateMetrics = {
			hits: layoutCache.hits + groupingCache.hits + searchCache.hits,
			misses: layoutCache.misses + groupingCache.misses + searchCache.misses,
			hitRatio:
				layoutCache.totalRequests +
					groupingCache.totalRequests +
					searchCache.totalRequests >
				0
					? (layoutCache.hits + groupingCache.hits + searchCache.hits) /
						(layoutCache.totalRequests +
							groupingCache.totalRequests +
							searchCache.totalRequests)
					: 0,
			totalRequests:
				layoutCache.totalRequests +
				groupingCache.totalRequests +
				searchCache.totalRequests,
		};

		// Timing metrics (from Performance API marks)
		const timing = {
			viewportLoadMs: timingMarkers.current.viewportLoadStart
				? now - timingMarkers.current.viewportLoadStart
				: 0,
			layoutComputeMs: timingMarkers.current.layoutComputeStart
				? now - timingMarkers.current.layoutComputeStart
				: 0,
			cullingMs: timingMarkers.current.cullingStart
				? now - timingMarkers.current.cullingStart
				: 0,
			renderMs: timingMarkers.current.renderStart
				? now - timingMarkers.current.renderStart
				: 0,
		};

		// Memory metrics (if available)
		let memory: PerformanceMetrics["memory"];
		if (
			"memory" in performance &&
			typeof (performance as any).memory === "object"
		) {
			const mem = (performance as any).memory;
			memory = {
				usedJSHeapSize: mem.usedJSHeapSize,
				totalJSHeapSize: mem.totalJSHeapSize,
				jsHeapSizeLimit: mem.jsHeapSizeLimit,
				heapUsagePercent: (mem.usedJSHeapSize / mem.jsHeapSizeLimit) * 100,
			};
		}

		// Interaction metrics
		const interaction = interactionTracker.current.getMetrics();

		return {
			timestamp: now,
			fps,
			nodes: {
				total: nodeTotal,
				rendered: nodeRendered,
				culled: nodeCulled,
				cullingRatio: nodeCullingRatio,
			},
			edges: {
				total: edgeTotal,
				rendered: edgeRendered,
				culled: edgeCulled,
				cullingRatio: edgeCullingRatio,
			},
			lod,
			cache: {
				layout: layoutCache,
				grouping: groupingCache,
				search: searchCache,
				combined: combinedCache,
			},
			timing,
			memory,
			interaction,
		};
	}, [nodes, edges, visibleNodes, visibleEdges, lodDistribution, cacheStats]);

	/** Report metrics to console and storage */
	const reportMetrics = useCallback(() => {
		if (!enabled) return;

		const metrics = collectMetrics();
		setCurrentMetrics(metrics);

		// Update history
		setHistory((prev) => {
			const updated = [...prev, metrics];
			// Keep only last MAX_HISTORY_LENGTH entries
			return updated.slice(-MAX_HISTORY_LENGTH);
		});

		// Custom handler
		if (onMetricsUpdate) {
			onMetricsUpdate(metrics);
		}

		// Console logging
		if (logToConsole) {
			logger.group(
				`%c[Graph Performance] ${new Date(metrics.timestamp).toLocaleTimeString()}`,
				"color: #10b981; font-weight: bold",
			);

			logger.info(
				`%cFPS: ${metrics.fps.current} (avg: ${metrics.fps.average}, min: ${metrics.fps.min}, max: ${metrics.fps.max})`,
				metrics.fps.current >= 55
					? "color: #10b981"
					: metrics.fps.current >= 30
						? "color: #f59e0b"
						: "color: #ef4444",
			);

			logger.info(
				`Nodes: ${metrics.nodes.rendered}/${metrics.nodes.total} (${metrics.nodes.cullingRatio.toFixed(1)}% culled)`,
			);
			logger.info(
				`Edges: ${metrics.edges.rendered}/${metrics.edges.total} (${metrics.edges.cullingRatio.toFixed(1)}% culled)`,
			);

			logger.info(
				`LOD: High=${metrics.lod.high} Med=${metrics.lod.medium} Low=${metrics.lod.low} Skeleton=${metrics.lod.skeleton}`,
			);

			logger.info(
				`Cache Hit Rate: ${(metrics.cache.combined.hitRatio * 100).toFixed(1)}% (${metrics.cache.combined.hits}/${metrics.cache.combined.totalRequests})`,
			);

			if (metrics.timing.viewportLoadMs > 0) {
				logger.info(`Viewport Load: ${metrics.timing.viewportLoadMs.toFixed(1)}ms`);
			}

			if (metrics.memory) {
				const heapMB = (metrics.memory.usedJSHeapSize / 1024 / 1024).toFixed(1);
				const limitMB = (metrics.memory.jsHeapSizeLimit / 1024 / 1024).toFixed(
					1,
				);
				logger.info(
					`Memory: ${heapMB}MB / ${limitMB}MB (${metrics.memory.heapUsagePercent.toFixed(1)}%)`,
				);
			}

			if (metrics.interaction.isPanning || metrics.interaction.isZooming) {
				logger.info(
					`Interaction: ${metrics.interaction.lastInteractionType} (${metrics.interaction.isPanning ? `pan: ${metrics.interaction.panDuration.toFixed(0)}ms` : ""} ${metrics.interaction.isZooming ? `zoom: ${metrics.interaction.zoomDuration.toFixed(0)}ms` : ""})`,
				);
			}

			logger.groupEnd();
		}

		// Persist to sessionStorage
		if (persistToStorage) {
			try {
				const stored = sessionStorage.getItem(STORAGE_KEY);
				const history = stored ? JSON.parse(stored) : [];
				history.push(metrics);
				// Keep only last 100 entries in storage
				const trimmed = history.slice(-100);
				sessionStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
			} catch (error) {
				logger.warn("[Graph Performance] Failed to persist metrics:", error);
			}
		}
	}, [enabled, collectMetrics, logToConsole, persistToStorage, onMetricsUpdate]);

	/** Get human-readable summary */
	const getSummary = useCallback((): string => {
		if (!currentMetrics) return "No metrics available";

		const lines = [
			`FPS: ${currentMetrics.fps.current} (avg: ${currentMetrics.fps.average})`,
			`Nodes: ${currentMetrics.nodes.rendered}/${currentMetrics.nodes.total} rendered (${currentMetrics.nodes.cullingRatio.toFixed(1)}% culled)`,
			`Edges: ${currentMetrics.edges.rendered}/${currentMetrics.edges.total} rendered (${currentMetrics.edges.cullingRatio.toFixed(1)}% culled)`,
			`Cache Hit Rate: ${(currentMetrics.cache.combined.hitRatio * 100).toFixed(1)}%`,
		];

		if (currentMetrics.memory) {
			const heapMB = (
				currentMetrics.memory.usedJSHeapSize /
				1024 /
				1024
			).toFixed(1);
			lines.push(`Memory: ${heapMB}MB`);
		}

		return lines.join(" | ");
	}, [currentMetrics]);

	/** Reset all metrics and history */
	const reset = useCallback(() => {
		fpsTracker.current.reset();
		interactionTracker.current.reset();
		setCurrentMetrics(null);
		setHistory([]);
		timingMarkers.current = {};

		if (persistToStorage) {
			sessionStorage.removeItem(STORAGE_KEY);
		}
	}, [persistToStorage]);

	// Start FPS tracking
	useEffect(() => {
		if (!enabled) return;

		fpsTracker.current.start();

		return () => {
			fpsTracker.current.stop();
		};
	}, [enabled]);

	// Periodic metric reporting
	useEffect(() => {
		if (!enabled || reportInterval <= 0) return;

		const interval = setInterval(reportMetrics, reportInterval);

		return () => clearInterval(interval);
	}, [enabled, reportInterval, reportMetrics]);

	// Track pan/zoom interactions via React Flow events
	useEffect(() => {
		if (!enabled) return;

		// Listen for viewport changes to detect pan/zoom
		// const handleViewportChange = () => {
		// 	// Start interaction tracking (will be handled by viewport change listeners in FlowGraphViewInner)
		// 	timingMarkers.current.viewportLoadStart = performance.now();
		// };

		// Add event listeners if needed
		// Note: This is simplified - actual implementation would integrate with ReactFlow events

		return () => {
			// Cleanup
		};
	}, [enabled]);

	return {
		currentMetrics,
		history,
		reportMetrics,
		reset,
		getSummary,
	};
}

/**
 * React Profiler API integration for component render tracking
 *
 * Usage:
 * ```tsx
 * import { Profiler } from 'react';
 *
 * <Profiler id="FlowGraphView" onRender={onRenderCallback}>
 *   <FlowGraphViewInner {...props} />
 * </Profiler>
 * ```
 */
export function createProfilerCallback(
	monitorId: string,
	logToConsole: boolean = process.env.NODE_ENV === "development",
) {
	return (
		id: string,
		phase: "mount" | "update" | "nested-update",
		actualDuration: number,
		baseDuration: number,
		startTime: number,
		commitTime: number,
	) => {
		if (logToConsole) {
			logger.info(
				`%c[Profiler: ${monitorId}]`,
				"color: #8b5cf6; font-weight: bold",
				{
					id,
					phase,
					actualDuration: `${actualDuration.toFixed(2)}ms`,
					baseDuration: `${baseDuration.toFixed(2)}ms`,
					startTime,
					commitTime,
				},
			);
		}

		// Store in sessionStorage for debugging
		if (process.env.NODE_ENV === "development") {
			try {
				const key = `trace_profiler_${monitorId}`;
				const stored = sessionStorage.getItem(key);
				const history = stored ? JSON.parse(stored) : [];
				history.push({
					id,
					phase,
					actualDuration,
					baseDuration,
					startTime,
					commitTime,
					timestamp: Date.now(),
				});
				// Keep only last 50 entries
				const trimmed = history.slice(-50);
				sessionStorage.setItem(key, JSON.stringify(trimmed));
            } catch {
                // Ignore storage errors
			}
		}
	};
}

/**
 * Performance mark helpers for manual timing
 */
export const perfMark = {
	start: (name: string) => {
		if (process.env.NODE_ENV === "development") {
			performance.mark(`${name}-start`);
		}
	},
	end: (name: string) => {
		if (process.env.NODE_ENV === "development") {
			performance.mark(`${name}-end`);
			try {
				performance.measure(name, `${name}-start`, `${name}-end`);
				const measure = performance.getEntriesByName(name)[0];
				if (measure) {
					logger.info(
						`%c[Performance] ${name}:`,
						"color: #06b6d4",
						`${measure.duration.toFixed(2)}ms`,
					);
				}
            } catch {
                // Ignore measurement errors
			}
		}
	},
};
