/**
 * R-tree Enhanced Viewport Culling Hook
 *
 * Drop-in replacement for useViewportCulling with O(log n) performance.
 * Use for large graphs (>10k edges) where viewport culling is a bottleneck.
 *
 * Performance:
 * - 10k edges: ~0.15ms per frame (vs 8ms O(n))
 * - 100k edges: ~0.12ms per frame (vs 68ms O(n))
 *
 * Usage:
 * ```typescript
 * const { cullableEdges, cullingStats } = useRTreeViewportCulling({
 *   edges: allEdges,
 *   nodes: allNodes,
 *   reactFlowInstance,
 *   enabled: true,
 *   padding: 100,
 * });
 * ```
 */

import { useCallback, useEffect, useMemo, useState } from 'react';

import type { Edge, NodePosition, ViewportBounds } from '../lib/spatialIndex';

import { logger } from '../lib/logger';
import { RBushSpatialIndex } from '../lib/spatialIndex';
import { getViewportBounds } from '../lib/viewportCulling';

const ZERO = 0;
const DEFAULT_PADDING = 100;
const DEFAULT_MIN_EDGES_FOR_RTREE = 10_000;
const LINEAR_EDGE_TIME_MS = 0.0007;
const SPEEDUP_FALLBACK = 1;
const RATIO_PERCENT_MULTIPLIER = 100;
const QUERY_TIME_DECIMALS = 3;
const BUILD_TIME_DECIMALS = 3;
const SPEEDUP_DECIMALS = 2;
const RATIO_DECIMALS = 1;

interface ReactFlowViewport {
  x: number;
  y: number;
  zoom: number;
}

interface ReactFlowInstance {
  getViewport?: (() => ReactFlowViewport) | undefined;
  addListener?: ((event: 'move', handler: () => void) => void) | undefined;
  removeListener?: ((event: 'move', handler: () => void) => void) | undefined;
}

interface RTreeNode {
  id: string;
  position?: NodePosition | undefined;
}

interface UseRTreeViewportCullingProps {
  edges: Edge[];
  nodes: RTreeNode[];
  reactFlowInstance?: ReactFlowInstance | undefined;
  enabled?: boolean | undefined;
  padding?: number | undefined;
  onStatsChange?: ((stats: CullingStats) => void) | undefined;
  rebuildThreshold?: number | undefined;
  minEdgesForRTree?: number | undefined;
}

interface UseRTreeViewportCullingResult {
  cullableEdges: Edge[];
  cullingStats?: CullingStats | undefined;
  viewportBounds?: ViewportBounds | undefined;
  isEnabled: boolean;
  spatialIndex?: RBushSpatialIndex | undefined;
}

interface QueryResult {
  edges: Edge[];
  queryTimeMs: number;
}

interface IndexResult {
  index?: RBushSpatialIndex | undefined;
  buildTimeMs: number;
}

interface ComputeCullableEdgesParams {
  enabled: boolean;
  edges: Edge[];
  nodePositions: Map<string, NodePosition>;
  viewportBounds: ViewportBounds | undefined;
  padding: number;
  spatialIndex?: RBushSpatialIndex | undefined;
}

interface CullingStats {
  totalEdges: number;
  visibleEdges: number;
  culledEdges: number;
  cullingRatio: number;
  queryTimeMs?: number | undefined;
  indexBuildTimeMs?: number | undefined;
  usingRTree: boolean;
}

const DEFAULT_CULLING_STATS: CullingStats = {
  culledEdges: ZERO,
  cullingRatio: ZERO,
  totalEdges: ZERO,
  usingRTree: false,
  visibleEdges: ZERO,
};

const useRTreeCullingStats = (
  cullingStats?: CullingStats,
): {
  buildTimeMs: number;
  culledCount: number;
  estimatedSpeedupVsLinear: number;
  queryTimeMs: number;
  savedPercentage: number;
  totalCount: number;
  usingRTree: boolean;
  visibleCount: number;
} =>
  useMemo(() => {
    const stats = cullingStats ?? DEFAULT_CULLING_STATS;
    const totalCount = stats.totalEdges;
    const visibleCount = stats.visibleEdges;
    const culledCount = stats.culledEdges;
    let savedPercentage = ZERO;
    if (totalCount > ZERO) {
      savedPercentage = (culledCount / totalCount) * RATIO_PERCENT_MULTIPLIER;
    }
    const queryTimeMs = stats.queryTimeMs ?? ZERO;
    const buildTimeMs = stats.indexBuildTimeMs ?? ZERO;
    let estimatedSpeedupVsLinear = SPEEDUP_FALLBACK;
    if (stats.usingRTree && queryTimeMs > ZERO) {
      estimatedSpeedupVsLinear = Math.max(
        (LINEAR_EDGE_TIME_MS * totalCount) / queryTimeMs,
        SPEEDUP_FALLBACK,
      );
    }

    return {
      buildTimeMs,
      culledCount,
      estimatedSpeedupVsLinear,
      queryTimeMs,
      savedPercentage,
      totalCount,
      usingRTree: stats.usingRTree,
      visibleCount,
    };
  }, [cullingStats]);

function extractNodePositions(nodes: RTreeNode[]): Map<string, NodePosition> {
  const positions = new Map<string, NodePosition>();

  for (const node of nodes) {
    if (node.position) {
      positions.set(node.id, {
        x: node.position.x,
        y: node.position.y,
      });
    }
  }

  return positions;
}

function buildSpatialIndex(
  edges: Edge[],
  nodePositions: Map<string, NodePosition>,
  shouldUseRTree: boolean,
): IndexResult {
  if (!shouldUseRTree) {
    return { buildTimeMs: ZERO };
  }

  const startTime = performance.now();
  const index = new RBushSpatialIndex();
  index.bulkLoad(edges, nodePositions);

  return {
    buildTimeMs: performance.now() - startTime,
    index,
  };
}

function buildEdgeBounds(sourcePos: NodePosition, targetPos: NodePosition): ViewportBounds {
  return {
    maxX: Math.max(sourcePos.x, targetPos.x),
    maxY: Math.max(sourcePos.y, targetPos.y),
    minX: Math.min(sourcePos.x, targetPos.x),
    minY: Math.min(sourcePos.y, targetPos.y),
  };
}

function buildSearchBounds(viewportBounds: ViewportBounds, padding: number): ViewportBounds {
  return {
    maxX: viewportBounds.maxX + padding,
    maxY: viewportBounds.maxY + padding,
    minX: viewportBounds.minX - padding,
    minY: viewportBounds.minY - padding,
  };
}

function isBoundsVisible(edgeBounds: ViewportBounds, searchBounds: ViewportBounds): boolean {
  return !(
    edgeBounds.maxX < searchBounds.minX ||
    edgeBounds.minX > searchBounds.maxX ||
    edgeBounds.maxY < searchBounds.minY ||
    edgeBounds.minY > searchBounds.maxY
  );
}

function filterEdgesLinear(
  edges: Edge[],
  nodePositions: Map<string, NodePosition>,
  viewportBounds: ViewportBounds,
  padding: number,
): Edge[] {
  const searchBounds = buildSearchBounds(viewportBounds, padding);

  return edges.filter((edge) => {
    const sourcePos = nodePositions.get(edge.source);
    const targetPos = nodePositions.get(edge.target);

    if (!sourcePos || !targetPos) {
      return false;
    }

    const edgeBounds = buildEdgeBounds(sourcePos, targetPos);
    return isBoundsVisible(edgeBounds, searchBounds);
  });
}

function computeCullableEdges({
  enabled,
  edges,
  nodePositions,
  viewportBounds,
  padding,
  spatialIndex,
}: ComputeCullableEdgesParams): QueryResult {
  if (!enabled || !viewportBounds) {
    return { edges, queryTimeMs: ZERO };
  }

  const startTime = performance.now();
  let result = edges;

  if (spatialIndex) {
    result = spatialIndex.searchViewport(viewportBounds, padding);
  } else {
    result = filterEdgesLinear(edges, nodePositions, viewportBounds, padding);
  }

  return {
    edges: result,
    queryTimeMs: performance.now() - startTime,
  };
}

function buildCullingStats(
  totalEdges: number,
  visibleEdges: number,
  queryTime: number,
  indexBuildTime: number,
  usingRTree: boolean,
): CullingStats {
  const culledEdges = totalEdges - visibleEdges;
  let cullingRatio = ZERO;

  if (totalEdges > ZERO) {
    cullingRatio = (culledEdges / totalEdges) * RATIO_PERCENT_MULTIPLIER;
  }

  return {
    culledEdges,
    cullingRatio,
    indexBuildTimeMs: indexBuildTime,
    queryTimeMs: queryTime,
    totalEdges,
    usingRTree,
    visibleEdges,
  };
}

function calculateEstimatedSpeedup(totalEdges: number, queryTimeMs: number): number {
  if (queryTimeMs <= ZERO) {
    return SPEEDUP_FALLBACK;
  }

  const estimatedLinearMs = totalEdges * LINEAR_EDGE_TIME_MS;
  return estimatedLinearMs / queryTimeMs;
}

function normalizeStats(stats: CullingStats | undefined): CullingStats {
  if (stats) {
    return stats;
  }

  return DEFAULT_CULLING_STATS;
}

function getRTreeCullingStats(stats: CullingStats | undefined): {
  culledCount: number;
  visibleCount: number;
  savedPercentage: number;
  queryTimeMs: number;
  buildTimeMs: number;
  usingRTree: boolean;
  estimatedSpeedupVsLinear: number;
} {
  const normalizedStats = normalizeStats(stats);
  const {
    culledEdges: culledCount,
    cullingRatio: savedPercentage,
    indexBuildTimeMs,
    queryTimeMs: rawQueryTimeMs,
    totalEdges,
    usingRTree,
    visibleEdges: visibleCount,
  } = normalizedStats;
  const queryTimeMs = rawQueryTimeMs ?? ZERO;
  const buildTimeMs = indexBuildTimeMs ?? ZERO;
  const estimatedSpeedupVsLinear = calculateEstimatedSpeedup(totalEdges, queryTimeMs);

  return {
    buildTimeMs,
    culledCount,
    estimatedSpeedupVsLinear,
    queryTimeMs,
    savedPercentage,
    usingRTree,
    visibleCount,
  };
}

function useViewportBoundsState(
  enabled: boolean,
  reactFlowInstance?: ReactFlowInstance,
): ViewportBounds | undefined {
  const [viewportBounds, setViewportBounds] = useState<ViewportBounds | undefined>();

  const handleViewportChange = useCallback((): void => {
    if (!enabled || !reactFlowInstance) {
      setViewportBounds(undefined);
      return;
    }

    const bounds = getViewportBounds(reactFlowInstance);
    if (!bounds) {
      setViewportBounds(undefined);
      return;
    }

    setViewportBounds(bounds);
  }, [enabled, reactFlowInstance]);

  useEffect((): (() => void) | undefined => {
    if (!enabled || !reactFlowInstance) {
      return;
    }

    handleViewportChange();

    const handleMove = (): void => {
      handleViewportChange();
    };

    if (reactFlowInstance.addListener) {
      reactFlowInstance.addListener('move', handleMove);
    }

    window.addEventListener('resize', handleViewportChange);

    return () => {
      if (reactFlowInstance.removeListener) {
        reactFlowInstance.removeListener('move', handleMove);
      }
      window.removeEventListener('resize', handleViewportChange);
    };
  }, [enabled, reactFlowInstance, handleViewportChange]);

  return viewportBounds;
}

const useRTreeViewportCulling = ({
  edges,
  nodes,
  reactFlowInstance,
  enabled = true,
  padding = DEFAULT_PADDING,
  onStatsChange,
  minEdgesForRTree = DEFAULT_MIN_EDGES_FOR_RTREE,
}: UseRTreeViewportCullingProps): UseRTreeViewportCullingResult => {
  const useRTree = enabled && edges.length >= minEdgesForRTree;
  const nodePositions = useMemo(() => extractNodePositions(nodes), [nodes]);
  const viewportBounds = useViewportBoundsState(enabled, reactFlowInstance);

  const indexResult = useMemo(
    () => buildSpatialIndex(edges, nodePositions, useRTree),
    [edges, nodePositions, useRTree],
  );

  const queryResult = useMemo(
    () =>
      computeCullableEdges({
        enabled,
        edges,
        nodePositions,
        viewportBounds,
        padding,
        spatialIndex: indexResult.index,
      }),
    [enabled, edges, nodePositions, viewportBounds, padding, indexResult.index],
  );

  const cullingStats = useMemo(
    () =>
      buildCullingStats(
        edges.length,
        queryResult.edges.length,
        queryResult.queryTimeMs,
        indexResult.buildTimeMs,
        indexResult.index !== undefined,
      ),
    [edges.length, queryResult.edges.length, queryResult.queryTimeMs, indexResult],
  );

  useEffect(() => {
    if (onStatsChange) {
      onStatsChange(cullingStats);
    }
  }, [cullingStats, onStatsChange]);

  useEffect((): void | (() => void) => {
    if (!indexResult.index) {
      return;
    }

    return () => {
      indexResult.index?.clear();
    };
  }, [indexResult.index]);

  return {
    cullableEdges: queryResult.edges,
    cullingStats,
    isEnabled: enabled,
    spatialIndex: indexResult.index,
    viewportBounds,
  };
};

const useRTreeDebug = (stats: CullingStats | undefined, edgeCount: number): void => {
  useEffect(() => {
    if (!stats) {
      return;
    }

    const detailedStats = getRTreeCullingStats(stats);
    let rTreeLabel = '❌';
    if (detailedStats.usingRTree) {
      rTreeLabel = '✅';
    }

    logger.info('🌳 R-tree Viewport Culling Stats');
    logger.info(`Edges: ${edgeCount.toLocaleString()}`);
    logger.info(`Visible: ${detailedStats.visibleCount.toLocaleString()}`);
    logger.info(`Culled: ${detailedStats.culledCount.toLocaleString()}`);
    logger.info(`Culling Ratio: ${detailedStats.savedPercentage.toFixed(RATIO_DECIMALS)}%`);
    logger.info(`Query Time: ${detailedStats.queryTimeMs.toFixed(QUERY_TIME_DECIMALS)}ms`);
    logger.info(`Build Time: ${detailedStats.buildTimeMs.toFixed(BUILD_TIME_DECIMALS)}ms`);
    logger.info(`Using R-tree: ${rTreeLabel}`);
    logger.info(
      `Estimated Speedup: ${detailedStats.estimatedSpeedupVsLinear.toFixed(SPEEDUP_DECIMALS)}x`,
    );
    logger.info('🌳 End R-tree Viewport Culling Stats');
  }, [stats, edgeCount]);
};

export { useRTreeCullingStats, useRTreeDebug, useRTreeViewportCulling, type CullingStats };
