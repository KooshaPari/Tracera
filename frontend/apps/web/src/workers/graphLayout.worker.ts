/**
 * Web Worker for off-main-thread graph layout computation
 *
 * This worker handles computationally expensive layout algorithms (Dagre, ELK, D3-Force)
 * without blocking the main UI thread. It uses Comlink for type-safe communication
 * and supports progressive layout streaming for large graphs.
 *
 * Performance targets:
 * - 10k nodes: <2s layout time, zero main thread blocking
 * - 100k nodes: <20s layout time with progressive updates
 *
 * @module graphLayout.worker
 */

import type { ElkExtendedEdge, ElkNode } from 'elkjs';

import * as Comlink from 'comlink';
import * as ELKModule from 'elkjs/lib/elk.bundled.js';

import { logger } from '@/lib/logger';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface LayoutNode {
  id: string;
  width: number;
  height: number;
}

export interface LayoutEdge {
  id: string;
  source: string;
  target: string;
}

export interface NodePosition {
  x: number;
  y: number;
}

export type LayoutAlgorithm = 'dagre' | 'elk' | 'd3-force' | 'grid' | 'circular' | 'radial';

export interface LayoutOptions {
  algorithm: LayoutAlgorithm;
  direction?: 'TB' | 'LR' | 'BT' | 'RL';
  nodeSep?: number;
  rankSep?: number;
  marginX?: number;
  marginY?: number;
  nodeWidth?: number;
  nodeHeight?: number;
  centerX?: number;
  centerY?: number;
  // Progressive layout options
  progressive?: boolean;
  batchSize?: number;
}

export interface LayoutResult {
  positions: Record<string, NodePosition>;
  size: { width: number; height: number };
  // For progressive layout
  isPartial?: boolean;
  progress?: number;
}

export type ProgressCallback = (result: LayoutResult) => void;

interface BenchmarkOptions {
  algorithm: LayoutAlgorithm;
  iterations?: number;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const ZERO = 0;
const ONE = 1;
const TWO = 2;
const HALF = 0.5;
const ONE_POINT_FIVE = 1.5;
const DEFAULT_NODE_WIDTH = 200;
const DEFAULT_NODE_HEIGHT = 120;
const DEFAULT_NODE_SEP = 60;
const DEFAULT_RANK_SEP = 100;
const DEFAULT_MARGIN_X = 40;
const DEFAULT_MARGIN_Y = 40;
const DEFAULT_CENTER_X = 500;
const DEFAULT_CENTER_Y = 400;
const DEFAULT_RADIUS_MIN = 300;
const DEFAULT_RADIUS_FACTOR = 20;
const DEFAULT_JITTER_SPREAD = 50;
const DEFAULT_REPULSION = 5000;
const DEFAULT_ATTRACTION = 0.1;
const DEFAULT_DAMPING = 0.9;
const DEFAULT_ITERATIONS_MAX = 50;
const DEFAULT_ITERATIONS_MIN = 20;
const DEFAULT_ITERATIONS_BASE = 100;
const DEFAULT_ITERATIONS_DIVISOR = 100;
const DEFAULT_NORMALIZE_PADDING = 50;
const DEFAULT_SIZE_PADDING = 100;
const DEFAULT_ORPHAN_SEGMENTS = 8;
const DEFAULT_BASE_RADIUS_MULTIPLIER = ONE_POINT_FIVE;
const DEFAULT_BATCH_SIZE = 100;
const DEFAULT_BENCHMARK_ITERATIONS = 5;

// ============================================================================
// ELK SETUP
// ============================================================================

const DIRECTION_MAP: Record<string, string> = {
  BT: 'UP',
  LR: 'RIGHT',
  RL: 'LEFT',
  TB: 'DOWN',
};

let elkInstance: any = null;

const getELK = () => {
  if (!elkInstance) {
    try {
      const ELK = (ELKModule as any).default ?? ELKModule;
      elkInstance = new ELK();
    } catch (error) {
      logger.error('[GraphLayoutWorker] Failed to initialize ELK:', error);
      throw error;
    }
  }
  return elkInstance;
};

// ============================================================================
// SHARED HELPERS
// ============================================================================

const createEmptyResult = (): LayoutResult => ({
  positions: {},
  size: { height: ZERO, width: ZERO },
});

const resolveSpacingOptions = (options: LayoutOptions) => ({
  marginX: options.marginX ?? DEFAULT_MARGIN_X,
  marginY: options.marginY ?? DEFAULT_MARGIN_Y,
  nodeSep: options.nodeSep ?? DEFAULT_NODE_SEP,
  nodeHeight: options.nodeHeight ?? DEFAULT_NODE_HEIGHT,
  nodeWidth: options.nodeWidth ?? DEFAULT_NODE_WIDTH,
  rankSep: options.rankSep ?? DEFAULT_RANK_SEP,
});

const resolveCenterOptions = (options: LayoutOptions) => ({
  centerX: options.centerX ?? DEFAULT_CENTER_X,
  centerY: options.centerY ?? DEFAULT_CENTER_Y,
  nodeHeight: options.nodeHeight ?? DEFAULT_NODE_HEIGHT,
  nodeWidth: options.nodeWidth ?? DEFAULT_NODE_WIDTH,
});

const computeSize = (
  width: number,
  height: number,
  marginX: number,
  marginY: number,
): { width: number; height: number } => ({
  height: height + marginY,
  width: width + marginX,
});

// ============================================================================
// ELK LAYOUT
// ============================================================================

const buildElkGraph = (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutOptions,
): ElkNode => {
  const {
    direction = 'TB',
    nodeSep = DEFAULT_NODE_SEP,
    rankSep = DEFAULT_RANK_SEP,
    marginX = DEFAULT_MARGIN_X,
    marginY = DEFAULT_MARGIN_Y,
    nodeWidth = DEFAULT_NODE_WIDTH,
    nodeHeight = DEFAULT_NODE_HEIGHT,
  } = options;

  return {
    children: nodes.map((node) => ({
      height: node.height || nodeHeight,
      id: node.id,
      width: node.width || nodeWidth,
    })),
    edges: edges.map((edge) => ({
      id: edge.id,
      sources: [edge.source],
      targets: [edge.target],
    })) as ElkExtendedEdge[],
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': DIRECTION_MAP[direction] ?? 'DOWN',
      'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
      'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX',
      'elk.layered.spacing.nodeNodeBetweenLayers': String(rankSep),
      'elk.padding': `[left=${marginX}, top=${marginY}, right=${marginX}, bottom=${marginY}]`,
      'elk.spacing.nodeNode': String(nodeSep),
    },
  };
};

const extractElkPositions = (
  result: ElkNode,
  options: LayoutOptions,
): { positions: Record<string, NodePosition>; size: { width: number; height: number } } => {
  const { marginX, marginY, nodeHeight, nodeWidth } = resolveSpacingOptions(options);
  const positions: Record<string, NodePosition> = {};
  let maxX = ZERO;
  let maxY = ZERO;

  for (const child of result.children ?? []) {
    if (child.x === undefined || child.y === undefined) {
      continue;
    }
    positions[child.id] = { x: child.x, y: child.y };
    maxX = Math.max(maxX, child.x + (child.width ?? nodeWidth));
    maxY = Math.max(maxY, child.y + (child.height ?? nodeHeight));
  }

  return {
    positions,
    size: computeSize(maxX, maxY, marginX, marginY),
  };
};

const layoutWithELK = async (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutOptions,
): Promise<LayoutResult> => {
  if (nodes.length === ZERO) {
    return createEmptyResult();
  }

  const elk = getELK();
  const graph = buildElkGraph(nodes, edges, options);
  const result = await elk.layout(graph);
  return extractElkPositions(result, options);
};

// ============================================================================
// DAGRE-STYLE LAYOUT
// ============================================================================

const buildAdjacency = (nodes: LayoutNode[], edges: LayoutEdge[]): Map<string, string[]> => {
  const graph = new Map<string, string[]>();
  for (const node of nodes) {
    graph.set(node.id, []);
  }
  for (const edge of edges) {
    const targets = graph.get(edge.source);
    if (targets) {
      targets.push(edge.target);
    }
  }
  return graph;
};

const assignDagreLevels = (graph: Map<string, string[]>): Map<string, number> => {
  const levels = new Map<string, number>();
  const visited = new Set<string>();

  const assignLevel = (nodeId: string): number => {
    if (visited.has(nodeId)) {
      return levels.get(nodeId) ?? ZERO;
    }
    visited.add(nodeId);

    let maxIncomingLevel = -ONE;
    for (const [source, targets] of graph) {
      if (targets.includes(nodeId)) {
        const srcLevel = assignLevel(source);
        maxIncomingLevel = Math.max(maxIncomingLevel, srcLevel);
      }
    }

    const nodeLevel = maxIncomingLevel + ONE;
    levels.set(nodeId, nodeLevel);
    return nodeLevel;
  };

  for (const nodeId of graph.keys()) {
    assignLevel(nodeId);
  }

  return levels;
};

const groupByLevel = (levels: Map<string, number>): Map<number, string[]> => {
  const levelGroups = new Map<number, string[]>();
  for (const [nodeId, level] of levels) {
    const group = levelGroups.get(level);
    if (group) {
      group.push(nodeId);
    } else {
      levelGroups.set(level, [nodeId]);
    }
  }
  return levelGroups;
};

const computeDagrePositions = (
  levelGroups: Map<number, string[]>,
  options: LayoutOptions,
): LayoutResult => {
  const { marginX, marginY, nodeHeight, nodeWidth, nodeSep, rankSep } =
    resolveSpacingOptions(options);
  const positions: Record<string, NodePosition> = {};
  let maxWidth = ZERO;
  let maxHeight = ZERO;

  const maxLevel = Math.max(...levelGroups.keys());
  const centerThreshold = DEFAULT_BENCHMARK_ITERATIONS;

  for (const [level, nodeIds] of levelGroups) {
    const y = marginY + level * (nodeHeight + rankSep);
    const levelWidth = nodeIds.length * (nodeWidth + nodeSep);
    const shouldCenter = maxLevel > centerThreshold;
    const startX = marginX + (shouldCenter ? -levelWidth / TWO : ZERO);

    nodeIds.forEach((nodeId, index) => {
      const x = startX + index * (nodeWidth + nodeSep);
      positions[nodeId] = { x: Math.max(marginX, x), y };
      maxWidth = Math.max(maxWidth, x + nodeWidth + marginX);
      maxHeight = Math.max(maxHeight, y + nodeHeight + marginY);
    });
  }

  return {
    positions,
    size: { height: maxHeight, width: maxWidth },
  };
};

const layoutWithDagre = (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutOptions,
): LayoutResult => {
  if (nodes.length === ZERO) {
    return createEmptyResult();
  }

  const graph = buildAdjacency(nodes, edges);
  const levels = assignDagreLevels(graph);
  const levelGroups = groupByLevel(levels);
  return computeDagrePositions(levelGroups, options);
};

// ============================================================================
// FORCE LAYOUT
// ============================================================================

const initForcePositions = (
  nodes: LayoutNode[],
  options: LayoutOptions,
): Map<string, { x: number; y: number; vx: number; vy: number }> => {
  const { nodeWidth, nodeHeight, nodeSep } = resolveSpacingOptions(options);
  const cols = Math.ceil(Math.sqrt(nodes.length));
  const positions = new Map<string, { x: number; y: number; vx: number; vy: number }>();

  nodes.forEach((node, index) => {
    const baseX = (index % cols) * (nodeWidth + nodeSep * TWO);
    const baseY = Math.floor(index / cols) * (nodeHeight + nodeSep * TWO);
    positions.set(node.id, {
      vx: ZERO,
      vy: ZERO,
      x: baseX + (Math.random() - HALF) * DEFAULT_JITTER_SPREAD,
      y: baseY + (Math.random() - HALF) * DEFAULT_JITTER_SPREAD,
    });
  });

  return positions;
};

const buildAdjacencySet = (edges: LayoutEdge[]): Map<string, Set<string>> => {
  const adjacency = new Map<string, Set<string>>();
  for (const edge of edges) {
    if (!adjacency.has(edge.source)) {
      adjacency.set(edge.source, new Set());
    }
    if (!adjacency.has(edge.target)) {
      adjacency.set(edge.target, new Set());
    }
    adjacency.get(edge.source)?.add(edge.target);
    adjacency.get(edge.target)?.add(edge.source);
  }
  return adjacency;
};

const computeForceIterations = (nodeCount: number): number => {
  const reduced = DEFAULT_ITERATIONS_BASE - Math.floor(nodeCount / DEFAULT_ITERATIONS_DIVISOR);
  return Math.min(DEFAULT_ITERATIONS_MAX, Math.max(DEFAULT_ITERATIONS_MIN, reduced));
};

const applyForceRepulsion = (
  nodes: LayoutNode[],
  positions: Map<string, { x: number; y: number; vx: number; vy: number }>,
): void => {
  for (const node1 of nodes) {
    const p1 = positions.get(node1.id);
    if (!p1) {
      continue;
    }
    for (const node2 of nodes) {
      if (node1.id === node2.id) {
        continue;
      }
      const p2 = positions.get(node2.id);
      if (!p2) {
        continue;
      }

      const dx = p1.x - p2.x;
      const dy = p1.y - p2.y;
      const dist = Math.max(Math.hypot(dx, dy), ONE);
      const force = DEFAULT_REPULSION / (dist * dist);

      p1.vx += (dx / dist) * force;
      p1.vy += (dy / dist) * force;
    }
  }
};

const applyForceAttraction = (
  edges: LayoutEdge[],
  positions: Map<string, { x: number; y: number; vx: number; vy: number }>,
): void => {
  for (const edge of edges) {
    const p1 = positions.get(edge.source);
    const p2 = positions.get(edge.target);
    if (!p1 || !p2) {
      continue;
    }

    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    p1.vx += dx * DEFAULT_ATTRACTION;
    p1.vy += dy * DEFAULT_ATTRACTION;
    p2.vx -= dx * DEFAULT_ATTRACTION;
    p2.vy -= dy * DEFAULT_ATTRACTION;
  }
};

const applyForceDamping = (
  nodes: LayoutNode[],
  positions: Map<string, { x: number; y: number; vx: number; vy: number }>,
): void => {
  for (const node of nodes) {
    const p = positions.get(node.id);
    if (!p) {
      continue;
    }
    p.x += p.vx;
    p.y += p.vy;
    p.vx *= DEFAULT_DAMPING;
    p.vy *= DEFAULT_DAMPING;
  }
};

const normalizePositions = (
  positions: Map<string, { x: number; y: number }>,
): {
  bounds: { minX: number; minY: number; maxX: number; maxY: number };
  result: Record<string, NodePosition>;
} => {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const pos of positions.values()) {
    minX = Math.min(minX, pos.x);
    minY = Math.min(minY, pos.y);
    maxX = Math.max(maxX, pos.x);
    maxY = Math.max(maxY, pos.y);
  }

  const result: Record<string, NodePosition> = {};
  for (const [id, pos] of positions) {
    result[id] = {
      x: pos.x - minX + DEFAULT_NORMALIZE_PADDING,
      y: pos.y - minY + DEFAULT_NORMALIZE_PADDING,
    };
  }

  return { bounds: { maxX, maxY, minX, minY }, result };
};

const layoutWithForce = (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutOptions,
): LayoutResult => {
  if (nodes.length === ZERO) {
    return createEmptyResult();
  }

  const { nodeHeight, nodeWidth } = resolveSpacingOptions(options);
  const positions = initForcePositions(nodes, options);
  buildAdjacencySet(edges);

  const iterations = computeForceIterations(nodes.length);
  for (let iter = ZERO; iter < iterations; iter += ONE) {
    applyForceRepulsion(nodes, positions);
    applyForceAttraction(edges, positions);
    applyForceDamping(nodes, positions);
  }

  const { bounds, result } = normalizePositions(positions);
  return {
    positions: result,
    size: {
      height: bounds.maxY - bounds.minY + nodeHeight + DEFAULT_SIZE_PADDING,
      width: bounds.maxX - bounds.minX + nodeWidth + DEFAULT_SIZE_PADDING,
    },
  };
};

// ============================================================================
// GRID LAYOUT
// ============================================================================

const layoutWithGrid = (
  nodes: LayoutNode[],
  _edges: LayoutEdge[],
  options: LayoutOptions,
): LayoutResult => {
  if (nodes.length === ZERO) {
    return createEmptyResult();
  }

  const { marginX, marginY, nodeHeight, nodeWidth, nodeSep } = resolveSpacingOptions(options);
  const cols = Math.ceil(Math.sqrt(nodes.length));
  const positions: Record<string, NodePosition> = {};
  let maxWidth = ZERO;
  let maxHeight = ZERO;

  nodes.forEach((node, index) => {
    const x = marginX + (index % cols) * (nodeWidth + nodeSep);
    const y = marginY + Math.floor(index / cols) * (nodeHeight + nodeSep);
    positions[node.id] = { x, y };
    maxWidth = Math.max(maxWidth, x + nodeWidth + marginX);
    maxHeight = Math.max(maxHeight, y + nodeHeight + marginY);
  });

  return {
    positions,
    size: { height: maxHeight, width: maxWidth },
  };
};

// ============================================================================
// CIRCULAR LAYOUT
// ============================================================================

const layoutWithCircular = (
  nodes: LayoutNode[],
  _edges: LayoutEdge[],
  options: LayoutOptions,
): LayoutResult => {
  if (nodes.length === ZERO) {
    return createEmptyResult();
  }

  const { centerX, centerY, nodeHeight, nodeWidth } = resolveCenterOptions(options);
  const count = nodes.length;
  const radius = Math.max(DEFAULT_RADIUS_MIN, count * DEFAULT_RADIUS_FACTOR);
  const angleStep = (TWO * Math.PI) / count;
  const positions: Record<string, NodePosition> = {};

  nodes.forEach((node, index) => {
    const angle = index * angleStep - Math.PI / TWO;
    positions[node.id] = {
      x: centerX + radius * Math.cos(angle) - nodeWidth / TWO,
      y: centerY + radius * Math.sin(angle) - nodeHeight / TWO,
    };
  });

  const size = {
    height: centerY * TWO + radius + nodeHeight,
    width: centerX * TWO + radius + nodeWidth,
  };

  return { positions, size };
};

// ============================================================================
// RADIAL LAYOUT
// ============================================================================

const buildChildrenMap = (edges: LayoutEdge[]): Map<string, string[]> => {
  const children = new Map<string, string[]>();
  for (const edge of edges) {
    const list = children.get(edge.source);
    if (list) {
      list.push(edge.target);
    } else {
      children.set(edge.source, [edge.target]);
    }
  }
  return children;
};

const findRoots = (nodes: LayoutNode[], edges: LayoutEdge[]): LayoutNode[] => {
  const hasIncoming = new Set(edges.map((edge) => edge.target));
  return nodes.filter((node) => !hasIncoming.has(node.id));
};

const assignDepths = (
  roots: LayoutNode[],
  children: Map<string, string[]>,
): Map<string, number> => {
  const depths = new Map<string, number>();
  const queue: { id: string; depth: number }[] = roots.map((root) => ({
    depth: ZERO,
    id: root.id,
  }));
  let index = ZERO;

  while (index < queue.length) {
    const entry = queue[index];
    index += ONE;
    if (!entry) {
      continue;
    }
    const { depth, id } = entry;
    if (depths.has(id)) {
      continue;
    }
    depths.set(id, depth);

    const nodeChildren = children.get(id) ?? [];
    for (const childId of nodeChildren) {
      if (!depths.has(childId)) {
        queue.push({ depth: depth + ONE, id: childId });
      }
    }
  }

  return depths;
};

const groupByDepth = (depths: Map<string, number>): Map<number, string[]> => {
  const byDepth = new Map<number, string[]>();
  for (const [id, depth] of depths) {
    const group = byDepth.get(depth);
    if (group) {
      group.push(id);
    } else {
      byDepth.set(depth, [id]);
    }
  }
  return byDepth;
};

const layoutWithRadial = (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutOptions,
): LayoutResult => {
  if (nodes.length === ZERO) {
    return createEmptyResult();
  }

  const { centerX, centerY, nodeHeight, nodeWidth } = resolveCenterOptions(options);
  const roots = findRoots(nodes, edges);
  const children = buildChildrenMap(edges);
  const depths = assignDepths(roots, children);
  const byDepth = groupByDepth(depths);

  const positions: Record<string, NodePosition> = {};
  const baseRadius = Math.max(nodeWidth, nodeHeight) * DEFAULT_BASE_RADIUS_MULTIPLIER;

  for (const [depth, nodeIds] of byDepth) {
    const radius = (depth + ONE) * baseRadius;
    const angleStep = (TWO * Math.PI) / nodeIds.length;
    nodeIds.forEach((id, index) => {
      const angle = index * angleStep - Math.PI / TWO;
      positions[id] = {
        x: centerX + radius * Math.cos(angle) - nodeWidth / TWO,
        y: centerY + radius * Math.sin(angle) - nodeHeight / TWO,
      };
    });
  }

  let orphanIndex = ZERO;
  const orphanRadius = (byDepth.size + ONE) * baseRadius;
  for (const node of nodes) {
    if (positions[node.id]) {
      continue;
    }
    const angle = (orphanIndex * TWO * Math.PI) / DEFAULT_ORPHAN_SEGMENTS - Math.PI / TWO;
    orphanIndex += ONE;
    positions[node.id] = {
      x: centerX + orphanRadius * Math.cos(angle) - nodeWidth / TWO,
      y: centerY + orphanRadius * Math.sin(angle) - nodeHeight / TWO,
    };
  }

  const maxDepth = byDepth.size;
  const size = {
    height: centerY * TWO + maxDepth * baseRadius + nodeHeight,
    width: centerX * TWO + maxDepth * baseRadius + nodeWidth,
  };

  return { positions, size };
};

// ============================================================================
// PROGRESSIVE LAYOUT
// ============================================================================

const buildPartialResult = (
  result: LayoutResult,
  isPartial: boolean,
  progress: number,
): LayoutResult => ({
  isPartial,
  positions: result.positions,
  progress,
  size: result.size,
});

const layoutProgressive = async function* layoutProgressive(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutOptions,
): AsyncGenerator<LayoutResult> {
  const batchSize = options.batchSize ?? DEFAULT_BATCH_SIZE;
  const totalBatches = Math.ceil(nodes.length / batchSize);

  if (options.algorithm === 'grid') {
    for (let i = ZERO; i < totalBatches; i += ONE) {
      const start = i * batchSize;
      const end = Math.min(start + batchSize, nodes.length);
      const batchNodes = nodes.slice(ZERO, end);
      const result = layoutWithGrid(batchNodes, edges, options);
      yield buildPartialResult(result, i < totalBatches - ONE, (i + ONE) / totalBatches);
    }
    return;
  }

  const result = await computeLayout(nodes, edges, options);
  yield result;
};

// ============================================================================
// MAIN API
// ============================================================================

export const computeLayout = async (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutOptions,
): Promise<LayoutResult> => {
  const startTime = performance.now();

  let result: LayoutResult;
  switch (options.algorithm) {
    case 'elk': {
      result = await layoutWithELK(nodes, edges, options);
      break;
    }
    case 'dagre': {
      result = layoutWithDagre(nodes, edges, options);
      break;
    }
    case 'd3-force': {
      result = layoutWithForce(nodes, edges, options);
      break;
    }
    case 'grid': {
      result = layoutWithGrid(nodes, edges, options);
      break;
    }
    case 'circular': {
      result = layoutWithCircular(nodes, edges, options);
      break;
    }
    case 'radial': {
      result = layoutWithRadial(nodes, edges, options);
      break;
    }
    default: {
      result = layoutWithGrid(nodes, edges, options);
    }
  }

  const duration = performance.now() - startTime;
  logger.info(
    `[GraphLayoutWorker] Layout ${options.algorithm} for ${nodes.length} nodes completed in ${duration.toFixed(2)}ms`,
  );

  return result;
};

export const computeLayoutProgressive = async function* computeLayoutProgressive(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutOptions,
): AsyncGenerator<LayoutResult> {
  yield* layoutProgressive(nodes, edges, options);
};

const summarizeBenchmark = (
  times: number[],
  algorithm: LayoutAlgorithm,
  nodeCount: number,
  edgeCount: number,
  iterations: number,
): {
  algorithm: LayoutAlgorithm;
  nodeCount: number;
  edgeCount: number;
  iterations: number;
  avgTime: number;
  minTime: number;
  maxTime: number;
  stdDev: number;
} => {
  const avgTime = times.reduce((sum, time) => sum + time, ZERO) / times.length;
  const minTime = Math.min(...times);
  const maxTime = Math.max(...times);
  const variance = times.reduce((sum, time) => sum + (time - avgTime) ** TWO, ZERO) / times.length;
  const stdDev = Math.sqrt(variance);

  return {
    algorithm,
    avgTime,
    edgeCount,
    iterations,
    maxTime,
    minTime,
    nodeCount,
    stdDev,
  };
};

export const benchmarkLayout = async (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: BenchmarkOptions,
): Promise<{
  algorithm: LayoutAlgorithm;
  nodeCount: number;
  edgeCount: number;
  iterations: number;
  avgTime: number;
  minTime: number;
  maxTime: number;
  stdDev: number;
}> => {
  const iterations = options.iterations ?? DEFAULT_BENCHMARK_ITERATIONS;
  const times: number[] = [];

  for (let i = ZERO; i < iterations; i += ONE) {
    const start = performance.now();
    await computeLayout(nodes, edges, { algorithm: options.algorithm });
    const duration = performance.now() - start;
    times.push(duration);
  }

  return summarizeBenchmark(times, options.algorithm, nodes.length, edges.length, iterations);
};

// ============================================================================
// EXPOSE API VIA COMLINK
// ============================================================================

const api = {
  benchmarkLayout,
  computeLayout,
  computeLayoutProgressive,
};

Comlink.expose(api);

export type GraphLayoutWorkerAPI = typeof api;
