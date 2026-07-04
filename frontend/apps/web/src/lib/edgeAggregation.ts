/**
 * Edge Aggregation for 1M+ Edge Graphs
 *
 * Implements multiple strategies for reducing edge rendering complexity:
 * 1. Edge Bundling - Groups parallel edges into single thicker edge
 * 2. Statistical Sampling - Renders representative sample of dense clusters
 * 3. Semantic Filtering - Show only edges of selected types
 * 4. Canvas Fallback - Use canvas for dense clusters
 *
 * Target: 1M edges → <100 visible edges
 */

import type { LinkType } from '@tracertm/types';

// ============================================================================
// Types
// ============================================================================

export interface EdgeBase {
  id: string;
  source: string;
  target: string;
  type: LinkType;
  [key: string]: any;
}

export interface AggregatedEdge extends EdgeBase {
  // Aggregation metadata
  _isAggregated: boolean;
  _aggregatedCount: number;
  _aggregatedTypes: Partial<Record<LinkType, number>>;
  _originalEdgeIds: string[];

  // Visual properties for aggregated edge
  strokeWidth: number;
  opacity: number;
  label?: string | undefined;
}

export interface EdgeCluster {
  id: string;
  source: string;
  target: string;
  edges: EdgeBase[];
  totalCount: number;
  typeDistribution: Partial<Record<LinkType, number>>;
  dominantType: LinkType;
}

export interface NodePosition {
  x: number;
  y: number;
}

export interface Node {
  id: string;
  position: NodePosition;
  [key: string]: any;
}

export interface EdgeSamplingConfig {
  // Maximum edges to render
  maxVisibleEdges: number;

  // Sampling strategy
  samplingStrategy: 'statistical' | 'importance' | 'hybrid';

  // For importance sampling
  priorityTypes?: LinkType[] | undefined;

  // For statistical sampling
  sampleRatio?: number; // 0.0-1.0

  // Aggregation threshold
  minEdgesForAggregation: number;

  // Density threshold for canvas fallback
  canvasFallbackDensity: number; // edges per 10000px²
}

export interface EdgeFilterConfig {
  enabledTypes: Set<LinkType>;
  showRelatedForSelection: boolean;
  maxRelatedEdges: number;
}

// ============================================================================
// 1. Edge Bundling / Aggregation
// ============================================================================

/**
 * Groups parallel edges (same source→target) into aggregated edges
 * Reduces 1000 parallel edges → 50 aggregated edges
 */
export function aggregateParallelEdges(
  edges: EdgeBase[],
  minEdgesForAggregation: number = 2,
): AggregatedEdge[] {
  // Group edges by source-target pair
  const edgeGroups = new Map<string, EdgeBase[]>();

  for (const edge of edges) {
    const key = `${edge.source}→${edge.target}`;
    if (!edgeGroups.has(key)) {
      edgeGroups.set(key, []);
    }
    edgeGroups.get(key)!.push(edge);
  }

  const aggregatedEdges: AggregatedEdge[] = [];

  for (const [key, groupEdges] of edgeGroups) {
    if (groupEdges.length < minEdgesForAggregation) {
      // Don't aggregate, return original edges
      for (const edge of groupEdges) {
        aggregatedEdges.push({
          ...edge,
          _isAggregated: false,
          _aggregatedCount: 1,
          _aggregatedTypes: { [edge.type]: 1 } as any,
          _originalEdgeIds: [edge.id],
          strokeWidth: 2,
          opacity: 1.0,
        } as unknown as AggregatedEdge);
      }
    } else {
      // Aggregate edges
      const typeDistribution: Record<string, number> = {};
      const originalIds: string[] = [];

      for (const edge of groupEdges) {
        typeDistribution[edge.type] = (typeDistribution[edge.type] || 0) + 1;
        originalIds.push(edge.id);
      }

      // Find dominant type
      const firstEdge = groupEdges[0];
      if (!firstEdge) continue;
      let dominantType = firstEdge.type;
      let maxCount = 0;
      for (const [type, count] of Object.entries(typeDistribution)) {
        if (count > maxCount) {
          maxCount = count;
          dominantType = type as LinkType;
        }
      }

      // Create aggregated edge
      const aggregatedEdge: AggregatedEdge = {
        ...firstEdge, // Use first edge as base
        id: `agg_${key}`,
        type: dominantType,
        _isAggregated: true,
        _aggregatedCount: groupEdges.length,
        _aggregatedTypes: typeDistribution as Record<LinkType, number>,
        _originalEdgeIds: originalIds,
        strokeWidth: Math.min(2 + Math.log2(groupEdges.length), 8),
        opacity: 1.0,
        label: `${groupEdges.length} edges`,
      };

      aggregatedEdges.push(aggregatedEdge);
    }
  }

  return aggregatedEdges;
}

/**
 * Detect edge clusters (high density areas)
 */
export function detectEdgeClusters(
  edges: EdgeBase[],
  nodes: Node[],
  densityThreshold: number = 10, // edges per 10000px²
): EdgeCluster[] {
  const nodePositions = new Map<string, NodePosition>();
  for (const node of nodes) {
    nodePositions.set(node.id, node.position);
  }

  // Group edges by spatial proximity
  const spatialGroups = new Map<string, EdgeBase[]>();

  for (const edge of edges) {
    const sourcePos = nodePositions.get(edge.source);
    const targetPos = nodePositions.get(edge.target);

    if (!sourcePos || !targetPos) continue;

    // Create spatial hash (100px grid)
    const gridX = Math.floor((sourcePos.x + targetPos.x) / 200) * 100;
    const gridY = Math.floor((sourcePos.y + targetPos.y) / 200) * 100;
    const key = `${gridX},${gridY}`;

    if (!spatialGroups.has(key)) {
      spatialGroups.set(key, []);
    }
    spatialGroups.get(key)!.push(edge);
  }

  // Convert to clusters
  const clusters: EdgeCluster[] = [];

  for (const [key, groupEdges] of spatialGroups) {
    if (groupEdges.length < densityThreshold) continue;

    // Calculate type distribution
    const typeDistribution: Record<string, number> = {};
    for (const edge of groupEdges) {
      typeDistribution[edge.type] = (typeDistribution[edge.type] || 0) + 1;
    }

    // Find dominant type
    const firstClusterEdge = groupEdges[0];
    if (!firstClusterEdge) continue;
    let dominantType = firstClusterEdge.type;
    let maxCount = 0;
    for (const [type, count] of Object.entries(typeDistribution)) {
      if (count > maxCount) {
        maxCount = count;
        dominantType = type as LinkType;
      }
    }

    clusters.push({
      id: `cluster_${key}`,
      source: firstClusterEdge.source,
      target: firstClusterEdge.target,
      edges: groupEdges,
      totalCount: groupEdges.length,
      typeDistribution: typeDistribution as Record<LinkType, number>,
      dominantType,
    });
  }

  return clusters;
}

// ============================================================================
// 2. Statistical Sampling
// ============================================================================

/**
 * FNV-1a hash for deterministic sampling (no flicker)
 */
function hashString(str: string): number {
  let hash = 2166136261;
  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

/**
 * Statistical sampling - render representative sample
 * User sees 5% of edges but gets accurate density visualization
 */
export function sampleEdgesStatistically(
  edges: EdgeBase[],
  sampleRatio: number = 0.05,
): EdgeBase[] {
  const sampledEdges: EdgeBase[] = [];

  for (const edge of edges) {
    // Deterministic sampling based on edge ID hash
    const hash = hashString(edge.id);
    const normalizedHash = hash / 0xffffffff;

    if (normalizedHash < sampleRatio) {
      sampledEdges.push(edge);
    }
  }

  return sampledEdges;
}

/**
 * Importance-based sampling - prioritize certain edge types
 */
export function sampleEdgesByImportance(
  edges: EdgeBase[],
  maxEdges: number,
  priorityTypes: LinkType[] = ['implements', 'tests', 'blocks'],
): AggregatedEdge[] {
  // Separate priority and non-priority edges
  const priorityEdges: EdgeBase[] = [];
  const normalEdges: EdgeBase[] = [];

  for (const edge of edges) {
    if (priorityTypes.includes(edge.type)) {
      priorityEdges.push(edge);
    } else {
      normalEdges.push(edge);
    }
  }

  // Calculate how many edges we can take from each group
  const priorityCount = Math.min(priorityEdges.length, Math.floor(maxEdges * 0.7));
  const normalCount = Math.min(normalEdges.length, maxEdges - priorityCount);

  // Sample normal edges if we have too many
  let sampledNormal = normalEdges;
  if (normalEdges.length > normalCount) {
    const sampleRatio = normalCount / normalEdges.length;
    sampledNormal = sampleEdgesStatistically(normalEdges, sampleRatio);
  }

  return [...priorityEdges.slice(0, priorityCount), ...sampledNormal] as AggregatedEdge[];
}

/**
 * Hybrid sampling - combines statistical and importance sampling
 */
export function sampleEdgesHybrid(edges: EdgeBase[], config: EdgeSamplingConfig): AggregatedEdge[] {
  // First, aggregate parallel edges
  const aggregated = aggregateParallelEdges(edges, config.minEdgesForAggregation);

  // If still too many, apply importance sampling
  if (aggregated.length > config.maxVisibleEdges) {
    return sampleEdgesByImportance(
      aggregated,
      config.maxVisibleEdges,
      config.priorityTypes,
    ) as unknown as AggregatedEdge[];
  }

  return aggregated as unknown as AggregatedEdge[];
}

// ============================================================================
// 3. Semantic Edge Filtering
// ============================================================================

/**
 * Filter edges by type
 */
export function filterEdgesByType(edges: EdgeBase[], config: EdgeFilterConfig): EdgeBase[] {
  if (config.enabledTypes.size === 0) {
    return edges; // No filter, return all
  }

  return edges.filter((edge) => config.enabledTypes.has(edge.type));
}

/**
 * Get edges related to selected node(s)
 */
export function getRelatedEdges(
  edges: EdgeBase[],
  selectedNodeIds: Set<string>,
  maxEdges: number = 100,
): EdgeBase[] {
  const relatedEdges: EdgeBase[] = [];

  for (const edge of edges) {
    if (selectedNodeIds.has(edge.source) || selectedNodeIds.has(edge.target)) {
      relatedEdges.push(edge);
      if (relatedEdges.length >= maxEdges) break;
    }
  }

  return relatedEdges;
}

/**
 * On-demand edge loading for selected nodes
 */
export function getEdgesOnDemand(
  allEdges: EdgeBase[],
  selectedNodeIds: Set<string>,
  config: EdgeFilterConfig,
): EdgeBase[] {
  if (selectedNodeIds.size === 0) {
    // No selection, return filtered edges
    return filterEdgesByType(allEdges, config);
  }

  // Get related edges for selection
  const relatedEdges = getRelatedEdges(allEdges, selectedNodeIds, config.maxRelatedEdges);

  // Apply type filter
  return filterEdgesByType(relatedEdges, config);
}

// ============================================================================
// 4. Canvas Fallback Detection
// ============================================================================

export interface DenseClusterInfo {
  clusterId: string;
  bounds: {
    minX: number;
    maxX: number;
    minY: number;
    maxY: number;
  };
  edgeCount: number;
  density: number; // edges per 10000px²
  useCanvasRendering: boolean;
}

/**
 * Detect areas that should use canvas rendering
 */
export function detectCanvasFallbackAreas(
  edges: EdgeBase[],
  nodes: Node[],
  densityThreshold: number = 50, // edges per 10000px²
): DenseClusterInfo[] {
  const nodePositions = new Map<string, NodePosition>();
  for (const node of nodes) {
    nodePositions.set(node.id, node.position);
  }

  // Group edges by 200px grid
  const gridGroups = new Map<string, EdgeBase[]>();

  for (const edge of edges) {
    const sourcePos = nodePositions.get(edge.source);
    const targetPos = nodePositions.get(edge.target);

    if (!sourcePos || !targetPos) continue;

    const gridX = Math.floor((sourcePos.x + targetPos.x) / 400);
    const gridY = Math.floor((sourcePos.y + targetPos.y) / 400);
    const key = `${gridX},${gridY}`;

    if (!gridGroups.has(key)) {
      gridGroups.set(key, []);
    }
    gridGroups.get(key)!.push(edge);
  }

  const clusterInfos: DenseClusterInfo[] = [];

  for (const [key, groupEdges] of gridGroups) {
    const parts = key.split(',').map(Number);
    const gridX = parts[0] ?? 0;
    const gridY = parts[1] ?? 0;

    // Calculate bounds (200x200 grid)
    const bounds = {
      minX: gridX * 200,
      maxX: (gridX + 1) * 200,
      minY: gridY * 200,
      maxY: (gridY + 1) * 200,
    };

    const area = (bounds.maxX - bounds.minX) * (bounds.maxY - bounds.minY);
    const density = (groupEdges.length / area) * 10000;

    clusterInfos.push({
      clusterId: `canvas_${key}`,
      bounds,
      edgeCount: groupEdges.length,
      density,
      useCanvasRendering: density >= densityThreshold,
    });
  }

  return clusterInfos.filter((info) => info.useCanvasRendering);
}

// ============================================================================
// 5. Main Orchestration Function
// ============================================================================

export interface LazyEdgeRenderingResult {
  visibleEdges: AggregatedEdge[];
  stats: {
    totalEdges: number;
    aggregatedEdges: number;
    sampledEdges: number;
    filteredEdges: number;
    canvasClusters: number;
    renderRatio: number;
  };
  canvasClusters: DenseClusterInfo[];
}

/**
 * Main function - orchestrates all edge reduction strategies
 * Target: 1M edges → <100 visible edges
 */
export function applyLazyEdgeRendering(
  edges: EdgeBase[],
  nodes: Node[],
  config: EdgeSamplingConfig,
  filterConfig?: EdgeFilterConfig,
  selectedNodeIds?: Set<string>,
): LazyEdgeRenderingResult {
  const totalEdges = edges.length;

  // Step 1: Detect canvas fallback areas (for very dense clusters)
  const canvasClusters = detectCanvasFallbackAreas(edges, nodes, config.canvasFallbackDensity);

  // Remove edges that will be rendered in canvas
  const canvasEdgeIds = new Set<string>();
  for (const cluster of canvasClusters) {
    // Mark edges in this area for canvas rendering
    for (const edge of edges) {
      const sourcePos = nodes.find((n) => n.id === edge.source)?.position;
      const targetPos = nodes.find((n) => n.id === edge.target)?.position;

      if (!sourcePos || !targetPos) continue;

      const midX = (sourcePos.x + targetPos.x) / 2;
      const midY = (sourcePos.y + targetPos.y) / 2;

      if (
        midX >= cluster.bounds.minX &&
        midX <= cluster.bounds.maxX &&
        midY >= cluster.bounds.minY &&
        midY <= cluster.bounds.maxY
      ) {
        canvasEdgeIds.add(edge.id);
      }
    }
  }

  const domEdges = edges.filter((edge) => !canvasEdgeIds.has(edge.id));

  // Step 2: Apply semantic filtering if provided
  let filteredEdges = domEdges;
  if (filterConfig) {
    if (selectedNodeIds && selectedNodeIds.size > 0) {
      filteredEdges = getEdgesOnDemand(domEdges, selectedNodeIds, filterConfig);
    } else {
      filteredEdges = filterEdgesByType(domEdges, filterConfig);
    }
  }

  // Step 3: Apply aggregation and sampling
  let visibleEdges: AggregatedEdge[];

  if (config.samplingStrategy === 'statistical') {
    // Pure statistical sampling
    const aggregated = aggregateParallelEdges(filteredEdges, config.minEdgesForAggregation);
    const sampleRatio = Math.min(config.maxVisibleEdges / aggregated.length, 1.0);
    const sampled = sampleEdgesStatistically(aggregated, sampleRatio);
    visibleEdges = sampled as AggregatedEdge[];
  } else if (config.samplingStrategy === 'importance') {
    // Importance-based sampling
    const aggregated = aggregateParallelEdges(filteredEdges, config.minEdgesForAggregation);
    visibleEdges = sampleEdgesByImportance(
      aggregated,
      config.maxVisibleEdges,
      config.priorityTypes,
    ) as AggregatedEdge[];
  } else {
    // Hybrid (default)
    visibleEdges = sampleEdgesHybrid(filteredEdges, config) as any;
  }

  return {
    visibleEdges: visibleEdges as AggregatedEdge[],
    stats: {
      totalEdges,
      aggregatedEdges: visibleEdges.filter((e) => e._isAggregated).length,
      sampledEdges: visibleEdges.length,
      filteredEdges: filteredEdges.length,
      canvasClusters: canvasClusters.length,
      renderRatio: (visibleEdges.length / totalEdges) * 100,
    },
    canvasClusters,
  };
}

// ============================================================================
// Helper: Create default config
// ============================================================================

export function createDefaultSamplingConfig(totalEdges: number): EdgeSamplingConfig {
  // Auto-tune based on edge count
  let maxVisibleEdges = 100;
  let samplingStrategy: 'statistical' | 'importance' | 'hybrid' = 'hybrid';

  if (totalEdges < 1000) {
    maxVisibleEdges = 500;
    samplingStrategy = 'importance';
  } else if (totalEdges < 10000) {
    maxVisibleEdges = 300;
    samplingStrategy = 'hybrid';
  } else if (totalEdges < 100000) {
    maxVisibleEdges = 150;
    samplingStrategy = 'hybrid';
  } else {
    maxVisibleEdges = 100;
    samplingStrategy = 'statistical';
  }

  return {
    maxVisibleEdges,
    samplingStrategy,
    priorityTypes: ['implements', 'tests', 'blocks', 'depends_on'],
    sampleRatio: maxVisibleEdges / totalEdges,
    minEdgesForAggregation: 2,
    canvasFallbackDensity: 50,
  };
}

export function createDefaultFilterConfig(): EdgeFilterConfig {
  return {
    enabledTypes: new Set(), // Empty = all types enabled
    showRelatedForSelection: true,
    maxRelatedEdges: 100,
  };
}
