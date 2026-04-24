import type { CacheStatistics } from '@/lib/cache';

import type { CacheHitRateMetrics, LODDistribution, PerformanceMetrics } from './types';

import { PERCENT_SCALE, ZERO } from './constants';

interface PerformanceMemory {
  usedJSHeapSize: number;
  totalJSHeapSize: number;
  jsHeapSizeLimit: number;
}

type PerformanceWithMemory = Performance & {
  memory?: PerformanceMemory | undefined;
};

interface InteractionMetrics {
  isPanning: boolean;
  isZooming: boolean;
  panDuration: number;
  zoomDuration: number;
  lastInteractionType: 'pan' | 'zoom' | 'idle';
}

interface FPSMetrics {
  current: number;
  average: number;
  min: number;
  max: number;
  samples: number;
}

interface TimingMarkers {
  viewportLoadStart?: number | undefined;
  layoutComputeStart?: number | undefined;
  cullingStart?: number | undefined;
  renderStart?: number | undefined;
}

function toCacheHitRateMetrics(stats: CacheStatistics | undefined): CacheHitRateMetrics {
  if (!stats) {
    return { hitRatio: ZERO, hits: ZERO, misses: ZERO, totalRequests: ZERO };
  }
  return {
    hitRatio: stats.hitRatio,
    hits: stats.totalHits,
    misses: stats.totalMisses,
    totalRequests: stats.totalHits + stats.totalMisses,
  };
}

function computeCombinedCache(
  layout: CacheHitRateMetrics,
  grouping: CacheHitRateMetrics,
  search: CacheHitRateMetrics,
): CacheHitRateMetrics {
  const totalRequests = layout.totalRequests + grouping.totalRequests + search.totalRequests;
  const hits = layout.hits + grouping.hits + search.hits;
  const misses = layout.misses + grouping.misses + search.misses;
  let hitRatio = ZERO;
  if (totalRequests > ZERO) {
    hitRatio = hits / totalRequests;
  }
  return { hitRatio, hits, misses, totalRequests };
}

function computeCullingRatio(total: number, rendered: number): { culled: number; ratio: number } {
  const culled = total - rendered;
  if (total <= ZERO) {
    return { culled, ratio: ZERO };
  }
  return { culled, ratio: (culled / total) * PERCENT_SCALE };
}

function resolveLOD(lodDistribution: LODDistribution | undefined): PerformanceMetrics['lod'] {
  return {
    high: lodDistribution?.high ?? ZERO,
    low: lodDistribution?.low ?? ZERO,
    medium: lodDistribution?.medium ?? ZERO,
    skeleton: lodDistribution?.skeleton ?? ZERO,
  };
}

function resolveTiming(now: number, markers: TimingMarkers): PerformanceMetrics['timing'] {
  let cullingMs = ZERO;
  if (markers.cullingStart !== undefined) {
    cullingMs = now - markers.cullingStart;
  }

  let layoutComputeMs = ZERO;
  if (markers.layoutComputeStart !== undefined) {
    layoutComputeMs = now - markers.layoutComputeStart;
  }

  let renderMs = ZERO;
  if (markers.renderStart !== undefined) {
    renderMs = now - markers.renderStart;
  }

  let viewportLoadMs = ZERO;
  if (markers.viewportLoadStart !== undefined) {
    viewportLoadMs = now - markers.viewportLoadStart;
  }

  return { cullingMs, layoutComputeMs, renderMs, viewportLoadMs };
}

function resolveMemory(): PerformanceMetrics['memory'] | undefined {
  const { memory } = performance as PerformanceWithMemory;
  if (memory === undefined) {
    return undefined;
  }
  return {
    heapUsagePercent: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * PERCENT_SCALE,
    jsHeapSizeLimit: memory.jsHeapSizeLimit,
    totalJSHeapSize: memory.totalJSHeapSize,
    usedJSHeapSize: memory.usedJSHeapSize,
  };
}

function buildPerformanceMetrics(params: {
  now: number;
  fps: FPSMetrics;
  interaction: InteractionMetrics;
  nodes: { total: number; rendered: number };
  edges: { total: number; rendered: number };
  lodDistribution: LODDistribution | undefined;
  cacheStats:
    | {
        layout?: CacheStatistics | undefined;
        grouping?: CacheStatistics | undefined;
        search?: CacheStatistics | undefined;
      }
    | undefined;
  timingMarkers: TimingMarkers;
}): PerformanceMetrics {
  const { edges, nodes } = params;
  const nodeRatios = computeCullingRatio(nodes.total, nodes.rendered);
  const edgeRatios = computeCullingRatio(edges.total, edges.rendered);

  const { cacheStats } = params;
  const layoutCache = toCacheHitRateMetrics(cacheStats?.layout);
  const groupingCache = toCacheHitRateMetrics(cacheStats?.grouping);
  const searchCache = toCacheHitRateMetrics(cacheStats?.search);
  const combined = computeCombinedCache(layoutCache, groupingCache, searchCache);

  const { fps, interaction, lodDistribution, now, timingMarkers } = params;

  return {
    cache: {
      combined,
      grouping: groupingCache,
      layout: layoutCache,
      search: searchCache,
    },
    edges: {
      culled: edgeRatios.culled,
      cullingRatio: edgeRatios.ratio,
      rendered: edges.rendered,
      total: edges.total,
    },
    fps,
    interaction,
    lod: resolveLOD(lodDistribution),
    memory: resolveMemory(),
    nodes: {
      culled: nodeRatios.culled,
      cullingRatio: nodeRatios.ratio,
      rendered: nodes.rendered,
      total: nodes.total,
    },
    timestamp: now,
    timing: resolveTiming(now, timingMarkers),
  };
}

export { buildPerformanceMetrics };
export type { FPSMetrics, InteractionMetrics, TimingMarkers };
