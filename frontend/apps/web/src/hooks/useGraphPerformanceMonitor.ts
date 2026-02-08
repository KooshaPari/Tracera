/**
 * Graph Performance Monitor Hook
 *
 * Thin wrapper that keeps public exports stable; implementation lives under
 * `./graph-performance-monitor/` to satisfy per-file oxlint constraints.
 */

import type { ProfilerOnRenderCallback } from 'react';

import { logger } from '@/lib/logger';

import type {
  GraphPerformanceMonitor,
  LODDistribution,
  PerformanceMetrics,
  UseGraphPerformanceMonitorConfig,
} from './graph-performance-monitor/types';

import { DURATION_DECIMALS } from './graph-performance-monitor/constants';
import {
  appendProfilerEntryToStorage,
  isDevelopmentEnv,
} from './graph-performance-monitor/storage';
import { useGraphPerformanceMonitorImpl } from './graph-performance-monitor/use-graph-performance-monitor-impl';

/**
 * Graph Performance Monitor Hook
 */
function useGraphPerformanceMonitor<NodeType = unknown, EdgeType = unknown>(
  config: UseGraphPerformanceMonitorConfig<NodeType, EdgeType>,
): GraphPerformanceMonitor {
  return useGraphPerformanceMonitorImpl(config);
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
): ProfilerOnRenderCallback {
  return (...args: Parameters<ProfilerOnRenderCallback>): void => {
    const [id, phase, actualDuration, baseDuration, startTime, commitTime] = args;
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
interface PerfMark {
  end: (name: string) => void;
  start: (name: string) => void;
}

const perfMark = {
  end: (name: string): void => {
    if (isDevelopmentEnv()) {
      performance.mark(`${name}-end`);
      try {
        performance.measure(name, `${name}-start`, `${name}-end`);
        const [measure] = performance.getEntriesByName(name);
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
} satisfies PerfMark;

export { createProfilerCallback, perfMark, useGraphPerformanceMonitor };
export type {
  GraphPerformanceMonitor,
  LODDistribution,
  PerformanceMetrics,
  UseGraphPerformanceMonitorConfig,
};
