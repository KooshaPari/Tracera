import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import type {
  GraphPerformanceMonitor,
  PerformanceMetrics,
  UseGraphPerformanceMonitorConfig,
} from './types';

import { MAX_HISTORY_LENGTH } from './constants';
import { formatSummary } from './formatting';
import { FPSTracker } from './fps-tracker';
import { InteractionTracker } from './interaction-tracker';
import { logGraphPerformanceMetrics } from './logging';
import { buildPerformanceMetrics } from './metrics';
import { appendMetricToStorage, clearMetricsStorage, isDevelopmentEnv } from './storage';
import { createInterval, resolveReportInterval } from './timing';

interface TimingMarkers {
  viewportLoadStart?: number;
  layoutComputeStart?: number;
  cullingStart?: number;
  renderStart?: number;
}

interface RefLike<Value> {
  current: Value;
}

type StateSetter<Value> = (value: Value | ((prev: Value) => Value)) => void;

function appendHistory(
  prev: PerformanceMetrics[],
  metrics: PerformanceMetrics,
): PerformanceMetrics[] {
  const updated = [...prev, metrics];
  return updated.slice(-MAX_HISTORY_LENGTH);
}

function resetMonitorState(args: {
  fpsTracker: RefLike<FPSTracker>;
  interactionTracker: RefLike<InteractionTracker>;
  setCurrentMetrics: StateSetter<PerformanceMetrics | undefined>;
  setHistory: StateSetter<PerformanceMetrics[]>;
  timingMarkers: RefLike<TimingMarkers>;
  persistToStorage: boolean;
}): void {
  const {
    fpsTracker,
    interactionTracker,
    persistToStorage,
    setCurrentMetrics,
    setHistory,
    timingMarkers,
  } = args;

  fpsTracker.current.reset();
  interactionTracker.current.reset();
  setCurrentMetrics(undefined);
  setHistory([]);
  timingMarkers.current = {};

  if (persistToStorage) {
    clearMetricsStorage();
  }
}

function useFpsTracking(enabled: boolean, fpsTracker: RefLike<FPSTracker>): void {
  useEffect((): void | (() => void) => {
    if (!enabled) {
      return;
    }

    const tracker = fpsTracker.current;
    tracker.start();

    return (): void => {
      tracker.stop();
    };
  }, [enabled, fpsTracker]);
}

function usePeriodicReporting(
  enabled: boolean,
  reportMetrics: () => void,
  resolvedReportInterval: number,
): void {
  useEffect((): void | (() => void) => {
    if (!enabled) {
      return;
    }

    const interval = createInterval(reportMetrics, resolvedReportInterval);
    if (interval === undefined) {
      return;
    }

    return (): void => {
      interval.clear();
    };
  }, [enabled, reportMetrics, resolvedReportInterval]);
}

function useGraphPerformanceMonitorImpl<NodeType = unknown, EdgeType = unknown>(
  config: UseGraphPerformanceMonitorConfig<NodeType, EdgeType>,
): GraphPerformanceMonitor {
  const {
    cacheStats,
    edges,
    enabled = isDevelopmentEnv(),
    lodDistribution,
    logToConsole = isDevelopmentEnv(),
    nodes,
    onMetricsUpdate,
    persistToStorage = isDevelopmentEnv(),
    reportInterval,
    visibleEdges,
    visibleNodes,
  } = config;

  const [currentMetrics, setCurrentMetrics] = useState<PerformanceMetrics | undefined>();
  const [history, setHistory] = useState<PerformanceMetrics[]>(() => []);

  const fpsTracker = useRef<FPSTracker>(new FPSTracker());
  const interactionTracker = useRef<InteractionTracker>(new InteractionTracker());
  const timingMarkers = useRef<TimingMarkers>({});

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
  }, [
    cacheStats,
    edges.length,
    lodDistribution,
    nodes.length,
    visibleEdges.length,
    visibleNodes.length,
  ]);

  const reportMetrics = useCallback((): void => {
    if (!enabled) {
      return;
    }

    const metrics = collectMetrics();
    setCurrentMetrics(metrics);
    setHistory((prev): PerformanceMetrics[] => appendHistory(prev, metrics));

    if (onMetricsUpdate) {
      onMetricsUpdate(metrics);
    }

    if (logToConsole) {
      logGraphPerformanceMetrics(metrics);
    }

    if (persistToStorage) {
      appendMetricToStorage(metrics);
    }
  }, [collectMetrics, enabled, logToConsole, onMetricsUpdate, persistToStorage]);

  const getSummary = useCallback((): string => {
    const metrics = currentMetrics;
    if (metrics === undefined) {
      return 'No metrics available';
    }
    return formatSummary(metrics);
  }, [currentMetrics]);

  const reset = useCallback((): void => {
    resetMonitorState({
      fpsTracker,
      interactionTracker,
      persistToStorage,
      setCurrentMetrics,
      setHistory,
      timingMarkers,
    });
  }, [persistToStorage]);

  useFpsTracking(enabled, fpsTracker);
  usePeriodicReporting(enabled, reportMetrics, resolvedReportInterval);

  return {
    currentMetrics,
    getSummary,
    history,
    reportMetrics,
    reset,
  };
}

export { useGraphPerformanceMonitorImpl };
