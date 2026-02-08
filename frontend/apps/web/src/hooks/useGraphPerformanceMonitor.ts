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

import { logger } from '@/lib/logger';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import {
  BYTES_PER_MB,
  DURATION_DECIMALS,
  FPS_GOOD_THRESHOLD,
  FPS_WARN_THRESHOLD,
  MAX_HISTORY_LENGTH,
  NO_DECIMALS,
  PERCENT_DECIMALS,
  PERCENT_SCALE,
  ZERO,
} from './graph-performance-monitor/constants';
import { buildPerformanceMetrics } from './graph-performance-monitor/metrics';
import { appendMetricToStorage, appendProfilerEntryToStorage, clearMetricsStorage, isDevelopmentEnv, safeToLocaleTimeString } from './graph-performance-monitor/storage';
import { createInterval, resolveReportInterval } from './graph-performance-monitor/timing';
import { FPSTracker, InteractionTracker } from './graph-performance-monitor/trackers';
import type { GraphPerformanceMonitor, LODDistribution, PerformanceMetrics, UseGraphPerformanceMonitorConfig } from './graph-performance-monitor/types';

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
  enabled = isDevelopmentEnv(),
  reportInterval,
  logToConsole = isDevelopmentEnv(),
  persistToStorage = isDevelopmentEnv(),
  onMetricsUpdate,
}: UseGraphPerformanceMonitorConfig<NodeType, EdgeType>): GraphPerformanceMonitor {
  const [currentMetrics, setCurrentMetrics] = useState<PerformanceMetrics | undefined>(undefined);
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

  const resolvedReportInterval = useMemo(
    (): number => resolveReportInterval(reportInterval),
    [reportInterval],
  );

  const collectMetrics = useCallback((): PerformanceMetrics => {
    const now = performance.now();
    return buildPerformanceMetrics({
      cacheStats,
      edges: { rendered: visibleEdges.length, total: edges.length },
      fps: fpsTracker.current.getMetrics(),
      interaction: interactionTracker.current.getMetrics(),
      lodDistribution,
      nodes: { rendered: visibleNodes.length, total: nodes.length },
      now,
      timingMarkers: timingMarkers.current,
    });
  }, [cacheStats, edges.length, lodDistribution, nodes.length, visibleEdges.length, visibleNodes.length]);

  const reportMetrics = useCallback((): void => {
    if (!enabled) {
      return;
    }

    const metrics = collectMetrics();
    setCurrentMetrics(metrics);

    setHistory((prev): PerformanceMetrics[] => {
      const updated = [...prev, metrics];
      return updated.slice(-MAX_HISTORY_LENGTH);
    });

    if (onMetricsUpdate) {
      onMetricsUpdate(metrics);
    }

    if (logToConsole) {
      const timeLabel = safeToLocaleTimeString(metrics.timestamp);
      logger.group(`[Graph Performance] ${timeLabel}`);

      let fpsColor = 'color: #ef4444';
      if (metrics.fps.current >= FPS_GOOD_THRESHOLD) {
        fpsColor = 'color: #10b981';
      } else if (metrics.fps.current >= FPS_WARN_THRESHOLD) {
        fpsColor = 'color: #f59e0b';
      }

      logger.info(
        `%cFPS: ${metrics.fps.current} (avg: ${metrics.fps.average}, min: ${metrics.fps.min}, max: ${metrics.fps.max})`,
        fpsColor,
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

      if (metrics.timing.viewportLoadMs > ZERO) {
        logger.info(`Viewport Load: ${metrics.timing.viewportLoadMs.toFixed(PERCENT_DECIMALS)}ms`);
      }

      if (metrics.memory) {
        const heapMB = (metrics.memory.usedJSHeapSize / BYTES_PER_MB).toFixed(PERCENT_DECIMALS);
        const limitMB = (metrics.memory.jsHeapSizeLimit / BYTES_PER_MB).toFixed(PERCENT_DECIMALS);
        logger.info(
          `Memory: ${heapMB}MB / ${limitMB}MB (${metrics.memory.heapUsagePercent.toFixed(PERCENT_DECIMALS)}%)`,
        );
      }

      const interactionFragments: string[] = [];
      if (metrics.interaction.isPanning) {
        interactionFragments.push(
          `pan: ${metrics.interaction.panDuration.toFixed(NO_DECIMALS)}ms`,
        );
      }
      if (metrics.interaction.isZooming) {
        interactionFragments.push(
          `zoom: ${metrics.interaction.zoomDuration.toFixed(NO_DECIMALS)}ms`,
        );
      }
      if (interactionFragments.length > ZERO) {
        logger.info(
          `Interaction: ${metrics.interaction.lastInteractionType} (${interactionFragments.join(' ')})`,
        );
      }

      logger.groupEnd();
    }

    if (persistToStorage) {
      appendMetricToStorage(metrics);
    }
  }, [collectMetrics, enabled, logToConsole, onMetricsUpdate, persistToStorage]);

  const getSummary = useCallback((): string => {
    const metrics = currentMetrics;
    if (!metrics) {
      return 'No metrics available';
    }
    const lines = [
      `FPS: ${metrics.fps.current} (avg: ${metrics.fps.average})`,
      `Nodes: ${metrics.nodes.rendered}/${metrics.nodes.total} rendered (${metrics.nodes.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
      `Edges: ${metrics.edges.rendered}/${metrics.edges.total} rendered (${metrics.edges.cullingRatio.toFixed(PERCENT_DECIMALS)}% culled)`,
      `Cache Hit Rate: ${(metrics.cache.combined.hitRatio * PERCENT_SCALE).toFixed(PERCENT_DECIMALS)}%`,
    ];
    if (metrics.memory) {
      const heapMB = (metrics.memory.usedJSHeapSize / BYTES_PER_MB).toFixed(PERCENT_DECIMALS);
      lines.push(`Memory: ${heapMB}MB`);
    }
    return lines.join(' | ');
  }, [currentMetrics]);

  const reset = useCallback((): void => {
    fpsTracker.current.reset();
    interactionTracker.current.reset();
    setCurrentMetrics(undefined);
    setHistory([]);
    timingMarkers.current = {};

    if (persistToStorage) {
      clearMetricsStorage();
    }
  }, [persistToStorage]);

  // Start FPS tracking
  useEffect((): (() => void) | undefined => {
    if (!enabled) {
      return undefined;
    }

    const tracker = fpsTracker.current;
    tracker.start();

    return (): void => {
      tracker.stop();
    };
  }, [enabled]);

  // Periodic metric reporting
  useEffect(() => {
    if (!enabled) {
      return;
    }

    const interval = createInterval(reportMetrics, resolvedReportInterval);

    return () => interval?.clear();
  }, [enabled, reportMetrics, resolvedReportInterval]);

  // Track pan/zoom interactions via React Flow events
  // Placeholder for future ReactFlow viewport interaction integration.

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
  logToConsole: boolean = isDevelopmentEnv(),
) {
  return (
    id: string,
    phase: 'mount' | 'update' | 'nested-update',
    actualDuration: number,
    baseDuration: number,
    startTime: number,
    commitTime: number,
  ): void => {
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
    if (isDevelopmentEnv()) {
      appendProfilerEntryToStorage(monitorId, {
        actualDuration,
        baseDuration,
        commitTime,
        id,
        phase,
        startTime,
        timestamp: Date.now(),
      });
    }
  };
}

/**
 * Performance mark helpers for manual timing
 */
const perfMark = {
  end: (name: string) => {
    if (isDevelopmentEnv()) {
      performance.mark(`${name}-end`);
      try {
        performance.measure(name, `${name}-start`, `${name}-end`);
        const measure = performance.getEntriesByName(name)[0];
        if (measure !== undefined) {
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
  start: (name: string): void => {
    if (isDevelopmentEnv()) {
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
