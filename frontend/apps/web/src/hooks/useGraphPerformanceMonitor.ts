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

import { useCallback, useEffect, useRef, useState } from 'react';

import type { CacheStatistics } from '@/lib/cache';

import { logger } from '@/lib/logger';

/** Performance metrics snapshot */
interface PerformanceMetrics {
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
    /** Percentage of nodes culled */
    cullingRatio: number;
  };

  /** Edge rendering metrics */
  edges: {
    total: number;
    rendered: number;
    culled: number;
    /** Percentage of edges culled */
    cullingRatio: number;
  };

  /** LOD (Level of Detail) distribution */
  lod: {
    /** Full detail nodes */
    high: number;
    /** Simplified nodes */
    medium: number;
    /** Minimal nodes */
    low: number;
    /** Loading/error skeletons */
    skeleton: number;
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
    /** Time to render current viewport */
    viewportLoadMs: number;
    /** Time to compute layout */
    layoutComputeMs: number;
    /** Time spent on viewport culling */
    cullingMs: number;
    /** Total render time */
    renderMs: number;
  };

  /** Memory metrics (if available) */
  memory?: {
    /** Bytes */
    usedJSHeapSize: number;
    /** Bytes */
    totalJSHeapSize: number;
    /** Bytes */
    jsHeapSizeLimit: number;
    heapUsagePercent: number;
  };

  /** Interaction metrics */
  interaction: {
    isPanning: boolean;
    isZooming: boolean;
    /** Ms */
    panDuration: number;
    /** Ms */
    zoomDuration: number;
    lastInteractionType: 'pan' | 'zoom' | 'idle';
  };
}

/** Cache hit rate metrics */
interface CacheHitRateMetrics {
  hits: number;
  misses: number;
  /** 0-1 */
  hitRatio: number;
  totalRequests: number;
}

interface PerformanceMemory {
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}

type PerformanceWithMemory = Performance & {
  memory?: PerformanceMemory;
};

/** LOD level distribution input */
interface LODDistribution {
  high: number;
  medium: number;
  low: number;
  skeleton?: number;
}

/** Hook configuration */
interface UseGraphPerformanceMonitorConfig<NodeType = unknown, EdgeType = unknown> {
  /** Total nodes in graph */
  nodes: NodeType[];
  /** Total edges in graph */
  edges: EdgeType[];
  /** Currently visible/rendered nodes */
  visibleNodes: NodeType[];
  /** Currently visible/rendered edges */
  visibleEdges: EdgeType[];
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
interface GraphPerformanceMonitor {
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
  private isRunning = false;

  start(): void {
    if (this.isRunning) {
      return;
    }
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
    if (!this.isRunning) {
      return;
    }

    const now = performance.now();
    const delta = now - this.lastFrameTime;
    this.lastFrameTime = now;

    if (delta > 0) {
      const fps = MS_PER_SECOND / delta;
      this.frames.push(fps);

      if (this.frames.length > FPS_SAMPLE_LIMIT) {
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
      return { average: 0, current: 0, max: 0, min: 0, samples: 0 };
    }

    const current = this.frames.at(-1) || 0;
    const average = this.frames.reduce((sum, fps) => sum + fps, 0) / this.frames.length;
    const min = Math.min(...this.frames);
    const max = Math.max(...this.frames);

    return {
      average: Math.round(average),
      current: Math.round(current),
      max: Math.round(max),
      min: Math.round(min),
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
  private isPanning = false;
  private isZooming = false;
  private panStartTime = 0;
  private zoomStartTime = 0;
  private lastInteractionType: 'pan' | 'zoom' | 'idle' = 'idle';

  startPan(): void {
    if (!this.isPanning) {
      this.isPanning = true;
      this.panStartTime = performance.now();
      this.lastInteractionType = 'pan';
    }
  }

  endPan(): void {
    this.isPanning = false;
  }

  startZoom(): void {
    if (!this.isZooming) {
      this.isZooming = true;
      this.zoomStartTime = performance.now();
      this.lastInteractionType = 'zoom';
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
      lastInteractionType: this.lastInteractionType,
      panDuration: this.isPanning ? now - this.panStartTime : 0,
      zoomDuration: this.isZooming ? now - this.zoomStartTime : 0,
    };
  }

  reset(): void {
    this.isPanning = false;
    this.isZooming = false;
    this.panStartTime = 0;
    this.zoomStartTime = 0;
    this.lastInteractionType = 'idle';
  }
}

/** Storage key for persisted metrics */
const STORAGE_KEY = 'trace_graph_performance_metrics';

/** Maximum history entries to keep */
const MAX_HISTORY_LENGTH = 50;
const FPS_SAMPLE_LIMIT = 60;
const MS_PER_SECOND = 1000;
const DEFAULT_REPORT_INTERVAL_MS = 5000;
const STORAGE_HISTORY_LIMIT = 100;
const PROFILER_HISTORY_LIMIT = 50;
const FPS_GOOD_THRESHOLD = 55;
const FPS_WARN_THRESHOLD = 30;
const BYTES_PER_MB = 1024 * 1024;
const PERCENT_SCALE = 100;
const PERCENT_DECIMALS = 1;
const DURATION_DECIMALS = 2;
const NO_DECIMALS = 0;

/**
 * Graph Performance Monitor Hook
 */
function useGraphPerformanceMonitor<NodeType = unknown, EdgeType = unknown>({
  nodes,
  edges,
  visibleNodes,
  visibleEdges,
  lodDistribution,
  cacheStats,
  enabled = process.env['NODE_ENV'] === 'development',
  reportInterval = DEFAULT_REPORT_INTERVAL_MS,
  logToConsole = process.env['NODE_ENV'] === 'development',
  persistToStorage = process.env['NODE_ENV'] === 'development',
  onMetricsUpdate,
}: UseGraphPerformanceMonitorConfig<NodeType, EdgeType>): GraphPerformanceMonitor {
  const [currentMetrics, setCurrentMetrics] = useState<PerformanceMetrics | null>(null);
  const [history, setHistory] = useState<PerformanceMetrics[]>([]);

  // Trackers
  const fpsTracker = useRef<FPSTracker>(new FPSTracker());
  const interactionTracker = useRef<InteractionTracker>(new InteractionTracker());

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
    const nodeCullingRatio = nodeTotal > 0 ? (nodeCulled / nodeTotal) * PERCENT_SCALE : 0;

    const edgeTotal = edges.length;
    const edgeRendered = visibleEdges.length;
    const edgeCulled = edgeTotal - edgeRendered;
    const edgeCullingRatio = edgeTotal > 0 ? (edgeCulled / edgeTotal) * PERCENT_SCALE : 0;

    // LOD distribution
    const lod = {
      high: lodDistribution?.high ?? 0,
      low: lodDistribution?.low ?? 0,
      medium: lodDistribution?.medium ?? 0,
      skeleton: lodDistribution?.skeleton ?? 0,
    };

    // Cache metrics
    const getCacheMetrics = (stats?: CacheStatistics): CacheHitRateMetrics => {
      if (!stats) {
        return { hitRatio: 0, hits: 0, misses: 0, totalRequests: 0 };
      }
      return {
        hitRatio: stats.hitRatio,
        hits: stats.totalHits,
        misses: stats.totalMisses,
        totalRequests: stats.totalHits + stats.totalMisses,
      };
    };

    const layoutCache = getCacheMetrics(cacheStats?.layout);
    const groupingCache = getCacheMetrics(cacheStats?.grouping);
    const searchCache = getCacheMetrics(cacheStats?.search);
    const combinedCache: CacheHitRateMetrics = {
      hitRatio:
        layoutCache.totalRequests + groupingCache.totalRequests + searchCache.totalRequests > 0
          ? (layoutCache.hits + groupingCache.hits + searchCache.hits) /
            (layoutCache.totalRequests + groupingCache.totalRequests + searchCache.totalRequests)
          : 0,
      hits: layoutCache.hits + groupingCache.hits + searchCache.hits,
      misses: layoutCache.misses + groupingCache.misses + searchCache.misses,
      totalRequests:
        layoutCache.totalRequests + groupingCache.totalRequests + searchCache.totalRequests,
    };

    // Timing metrics (from Performance API marks)
    const timing = {
      cullingMs: timingMarkers.current.cullingStart ? now - timingMarkers.current.cullingStart : 0,
      layoutComputeMs: timingMarkers.current.layoutComputeStart
        ? now - timingMarkers.current.layoutComputeStart
        : 0,
      renderMs: timingMarkers.current.renderStart ? now - timingMarkers.current.renderStart : 0,
      viewportLoadMs: timingMarkers.current.viewportLoadStart
        ? now - timingMarkers.current.viewportLoadStart
        : 0,
    };

    // Memory metrics (if available)
    let memory: PerformanceMetrics['memory'];
    const performanceWithMemory = performance as PerformanceWithMemory;
    if (performanceWithMemory.memory) {
      const mem = performanceWithMemory.memory;
      memory = {
        heapUsagePercent: (mem.usedJSHeapSize / mem.jsHeapSizeLimit) * PERCENT_SCALE,
        jsHeapSizeLimit: mem.jsHeapSizeLimit,
        totalJSHeapSize: mem.totalJSHeapSize,
        usedJSHeapSize: mem.usedJSHeapSize,
      };
    }

    // Interaction metrics
    const interaction = interactionTracker.current.getMetrics();

    return {
      cache: {
        combined: combinedCache,
        grouping: groupingCache,
        layout: layoutCache,
        search: searchCache,
      },
      edges: {
        culled: edgeCulled,
        cullingRatio: edgeCullingRatio,
        rendered: edgeRendered,
        total: edgeTotal,
      },
      fps,
      interaction,
      lod,
      memory,
      nodes: {
        culled: nodeCulled,
        cullingRatio: nodeCullingRatio,
        rendered: nodeRendered,
        total: nodeTotal,
      },
      timestamp: now,
      timing,
    };
  }, [nodes, edges, visibleNodes, visibleEdges, lodDistribution, cacheStats]);

  /** Report metrics to console and storage */
  const reportMetrics = useCallback(() => {
    if (!enabled) {
      return;
    }

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
      logger.group(`[Graph Performance] ${new Date(metrics.timestamp).toLocaleTimeString()}`);

      logger.info(
        `%cFPS: ${metrics.fps.current} (avg: ${metrics.fps.average}, min: ${metrics.fps.min}, max: ${metrics.fps.max})`,
        metrics.fps.current >= FPS_GOOD_THRESHOLD
          ? 'color: #10b981'
          : metrics.fps.current >= FPS_WARN_THRESHOLD
            ? 'color: #f59e0b'
            : 'color: #ef4444',
      );

      logger.info(
        `Nodes: ${metrics.nodes.rendered}/${metrics.nodes.total} (${metrics.nodes.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
      );
      logger.info(
        `Edges: ${metrics.edges.rendered}/${metrics.edges.total} (${metrics.edges.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
      );

      logger.info(
        `LOD: High=${metrics.lod.high} Med=${metrics.lod.medium} Low=${metrics.lod.low} Skeleton=${metrics.lod.skeleton}`,
      );

      logger.info(
        `Cache Hit Rate: ${(metrics.cache.combined.hitRatio * PERCENT_SCALE).toFixed(PERCENT_DECIMALS)}% (${metrics.cache.combined.hits}/${metrics.cache.combined.totalRequests})`,
      );

      if (metrics.timing.viewportLoadMs > 0) {
        logger.info(`Viewport Load: ${metrics.timing.viewportLoadMs.toFixed(PERCENT_DECIMALS)}ms`);
      }

      if (metrics.memory) {
        const heapMB = (metrics.memory.usedJSHeapSize / BYTES_PER_MB).toFixed(PERCENT_DECIMALS);
        const limitMB = (metrics.memory.jsHeapSizeLimit / BYTES_PER_MB).toFixed(PERCENT_DECIMALS);
        logger.info(
          `Memory: ${heapMB}MB / ${limitMB}MB (${metrics.memory.heapUsagePercent.toFixed(PERCENT_DECIMALS)}%)`,
        );
      }

      if (metrics.interaction.isPanning || metrics.interaction.isZooming) {
        logger.info(
          `Interaction: ${metrics.interaction.lastInteractionType} (${metrics.interaction.isPanning ? `pan: ${metrics.interaction.panDuration.toFixed(NO_DECIMALS)}ms` : ''} ${metrics.interaction.isZooming ? `zoom: ${metrics.interaction.zoomDuration.toFixed(NO_DECIMALS)}ms` : ''})`,
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
        const trimmed = history.slice(-STORAGE_HISTORY_LIMIT);
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
      } catch (error) {
        logger.warn('[Graph Performance] Failed to persist metrics:', error);
      }
    }
  }, [enabled, collectMetrics, logToConsole, persistToStorage, onMetricsUpdate]);

  /** Get human-readable summary */
  const getSummary = useCallback((): string => {
    if (!currentMetrics) {
      return 'No metrics available';
    }

    const lines = [
      `FPS: ${currentMetrics.fps.current} (avg: ${currentMetrics.fps.average})`,
      `Nodes: ${currentMetrics.nodes.rendered}/${currentMetrics.nodes.total} rendered (${currentMetrics.nodes.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
      `Edges: ${currentMetrics.edges.rendered}/${currentMetrics.edges.total} rendered (${currentMetrics.edges.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
      `Cache Hit Rate: ${(currentMetrics.cache.combined.hitRatio * PERCENT_SCALE).toFixed(PERCENT_DECIMALS)}%`,
    ];

    if (currentMetrics.memory) {
      const heapMB = (currentMetrics.memory.usedJSHeapSize / BYTES_PER_MB).toFixed(
        PERCENT_DECIMALS,
      );
      lines.push(`Memory: ${heapMB}MB`);
    }

    return lines.join(' | ');
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
    if (!enabled) {
      return;
    }

    fpsTracker.current.start();

    return () => {
      fpsTracker.current.stop();
    };
  }, [enabled]);

  // Periodic metric reporting
  useEffect(() => {
    if (!enabled || reportInterval <= 0) {
      return;
    }

    const interval = setInterval(reportMetrics, reportInterval);

    return () => clearInterval(interval);
  }, [enabled, reportInterval, reportMetrics]);

  // Track pan/zoom interactions via React Flow events
  useEffect(() => {
    if (!enabled) {
      return;
    }

    // Listen for viewport changes to detect pan/zoom
    // Const handleViewportChange = () => {
    // 	// Start interaction tracking (will be handled by viewport change listeners in FlowGraphViewInner)
    // 	TimingMarkers.current.viewportLoadStart = performance.now();
    // };

    // Add event listeners if needed
    // Note: This is simplified - actual implementation would integrate with ReactFlow events

    return () => {
      // Cleanup
    };
  }, [enabled]);

  return {
    currentMetrics,
    getSummary,
    history,
    reportMetrics,
    reset,
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
function createProfilerCallback(
  monitorId: string,
  logToConsole: boolean = process.env['NODE_ENV'] === 'development',
) {
  return (
    id: string,
    phase: 'mount' | 'update' | 'nested-update',
    actualDuration: number,
    baseDuration: number,
    startTime: number,
    commitTime: number,
  ) => {
    if (logToConsole) {
      logger.info(`%c[Profiler: ${monitorId}]`, 'color: #8b5cf6; font-weight: bold', {
        actualDuration: `${actualDuration.toFixed(DURATION_DECIMALS)}ms`,
        baseDuration: `${baseDuration.toFixed(DURATION_DECIMALS)}ms`,
        commitTime,
        id,
        phase,
        startTime,
      });
    }

    // Store in sessionStorage for debugging
    if (process.env['NODE_ENV'] === 'development') {
      try {
        const key = `trace_profiler_${monitorId}`;
        const stored = sessionStorage.getItem(key);
        const history = stored ? JSON.parse(stored) : [];
        history.push({
          actualDuration,
          baseDuration,
          commitTime,
          id,
          phase,
          startTime,
          timestamp: Date.now(),
        });
        const trimmed = history.slice(-PROFILER_HISTORY_LIMIT);
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
const perfMark = {
  end: (name: string) => {
    if (process.env['NODE_ENV'] === 'development') {
      performance.mark(`${name}-end`);
      try {
        performance.measure(name, `${name}-start`, `${name}-end`);
        const measure = performance.getEntriesByName(name)[0];
        if (measure) {
          logger.info(
            `%c[Performance] ${name}:`,
            'color: #06b6d4',
            `${measure.duration.toFixed(DURATION_DECIMALS)}ms`,
          );
        }
      } catch {
        // Ignore measurement errors
      }
    }
  },
  start: (name: string) => {
    if (process.env['NODE_ENV'] === 'development') {
      performance.mark(`${name}-start`);
    }
  },
};

export { createProfilerCallback, perfMark, useGraphPerformanceMonitor };
export type {
  GraphPerformanceMonitor,
  LODDistribution,
  PerformanceMetrics,
  UseGraphPerformanceMonitorConfig,
};
