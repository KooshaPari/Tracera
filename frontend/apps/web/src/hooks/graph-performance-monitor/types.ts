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

  memory?: {
    usedJSHeapSize: number;
    totalJSHeapSize: number;
    jsHeapSizeLimit: number;
    heapUsagePercent: number;
  };

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
  skeleton?: number;
}

interface UseGraphPerformanceMonitorConfig<NodeType = unknown, EdgeType = unknown> {
  nodes: NodeType[];
  edges: EdgeType[];
  visibleNodes: NodeType[];
  visibleEdges: EdgeType[];
  lodDistribution?: LODDistribution;
  cacheStats?: {
    layout?: CacheStatistics;
    grouping?: CacheStatistics;
    search?: CacheStatistics;
  };
  enabled?: boolean;
  reportInterval?: number;
  logToConsole?: boolean;
  persistToStorage?: boolean;
  onMetricsUpdate?: (metrics: PerformanceMetrics) => void;
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
