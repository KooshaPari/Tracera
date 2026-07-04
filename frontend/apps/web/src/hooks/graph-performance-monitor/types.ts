import type { CacheStatistics } from '@/lib/cache';

interface PerformanceMetrics {
  timestamp: number;

  fps: {
    current: number;
    average: number;
    min: number;
    max: number;
    samples: number;
  };

  nodes: {
    total: number;
    rendered: number;
    culled: number;
    cullingRatio: number;
  };

  edges: {
    total: number;
    rendered: number;
    culled: number;
    cullingRatio: number;
  };

  lod: {
    high: number;
    medium: number;
    low: number;
    skeleton: number;
  };

  cache: {
    layout: CacheHitRateMetrics;
    grouping: CacheHitRateMetrics;
    search: CacheHitRateMetrics;
    combined: CacheHitRateMetrics;
  };

  timing: {
    viewportLoadMs: number;
    layoutComputeMs: number;
    cullingMs: number;
    renderMs: number;
  };

  memory?:
    | {
        usedJSHeapSize: number;
        totalJSHeapSize: number;
        jsHeapSizeLimit: number;
        heapUsagePercent: number;
      }
    | undefined;

  interaction: {
    isPanning: boolean;
    isZooming: boolean;
    panDuration: number;
    zoomDuration: number;
    lastInteractionType: 'pan' | 'zoom' | 'idle';
  };
}

interface CacheHitRateMetrics {
  hits: number;
  misses: number;
  hitRatio: number;
  totalRequests: number;
}

interface LODDistribution {
  high: number;
  medium: number;
  low: number;
  skeleton?: number | undefined;
}

interface UseGraphPerformanceMonitorConfig<NodeType = unknown, EdgeType = unknown> {
  nodes: NodeType[];
  edges: EdgeType[];
  visibleNodes: NodeType[];
  visibleEdges: EdgeType[];
  lodDistribution?: LODDistribution | undefined;
  cacheStats?: {
    layout?: CacheStatistics | undefined;
    grouping?: CacheStatistics | undefined;
    search?: CacheStatistics | undefined;
  };
  enabled?: boolean | undefined;
  reportInterval?: number | undefined;
  logToConsole?: boolean | undefined;
  persistToStorage?: boolean | undefined;
  onMetricsUpdate?: ((metrics: PerformanceMetrics) => void) | undefined;
}

interface GraphPerformanceMonitor {
  currentMetrics: PerformanceMetrics | undefined;
  history: PerformanceMetrics[];
  reportMetrics: () => void;
  reset: () => void;
  getSummary: () => string;
}

export type {
  CacheHitRateMetrics,
  GraphPerformanceMonitor,
  LODDistribution,
  PerformanceMetrics,
  UseGraphPerformanceMonitorConfig,
};
