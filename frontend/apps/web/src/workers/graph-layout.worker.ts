/**
 * Graph Layout Worker
 *
 * Performs heavy graph layout computations off the main thread:
 * - Dagre layouts
 * - Force-directed layouts
 * - ELK hierarchical layouts
 */

import { expose } from 'comlink';

export interface LayoutNode {
  id: string;
  width: number;
  height: number;
  data?: any;
}

export interface LayoutEdge {
  id: string;
  source: string;
  target: string;
  data?: any;
}

export interface LayoutOptions {
  type: 'dagre' | 'force' | 'elk' | 'hierarchical';
  direction?: 'TB' | 'LR' | 'BT' | 'RL';
  nodeSep?: number;
  rankSep?: number;
  marginX?: number;
  marginY?: number;
  iterations?: number;
}

export interface LayoutResult {
  positions: Record<string, { x: number; y: number }>;
  size: { width: number; height: number };
}

export type ProgressCallback = (progress: number) => void;

type LayoutTaskOptions = LayoutOptions & { onProgress?: ProgressCallback };

const ZERO = 0;
const ONE = 1;
const TWO = 2;
const DEFAULT_NODE_SEP = 60;
const DEFAULT_RANK_SEP = 100;
const DEFAULT_MARGIN_X = 40;
const DEFAULT_MARGIN_Y = 40;
const DEFAULT_FORCE_ITERATIONS = 100;
const DEFAULT_FORCE_WIDTH = 1000;
const DEFAULT_FORCE_HEIGHT = 800;
const DEFAULT_FORCE_DAMPING = 0.1;
const DEFAULT_VELOCITY_DECAY = 0.9;
const DEFAULT_BOUNDARY_PADDING = 50;
const DEFAULT_MIN_DISTANCE = 0.01;
const DEFAULT_GRID_PROGRESS_STEP = 10;
const PROGRESS_START = 0;
const PROGRESS_GRAPH_READY = 20;
const PROGRESS_INDEGREE_READY = 40;
const PROGRESS_LEVELS_READY = 60;
const PROGRESS_GROUPED = 80;
const PROGRESS_COMPLETE = 100;

const reportProgress = (onProgress: ProgressCallback | undefined, value: number): void => {
  if (onProgress) {
    onProgress(value);
  }
};

const clamp = (value: number, min: number, max: number): number =>
  Math.max(min, Math.min(max, value));

const createAdjacency = (nodes: LayoutNode[], edges: LayoutEdge[]): Map<string, string[]> => {
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

const createInDegree = (nodes: LayoutNode[], graph: Map<string, string[]>): Map<string, number> => {
  const inDegree = new Map<string, number>();
  for (const node of nodes) {
    inDegree.set(node.id, ZERO);
  }
  for (const targets of graph.values()) {
    for (const target of targets) {
      inDegree.set(target, (inDegree.get(target) ?? ZERO) + ONE);
    }
  }
  return inDegree;
};

const assignLevels = (
  graph: Map<string, string[]>,
  inDegree: Map<string, number>,
): { levels: Map<string, number>; maxLevel: number } => {
  const levels = new Map<string, number>();
  const visited = new Set<string>();
  let queue: string[] = [];

  for (const [nodeId, degree] of inDegree) {
    if (degree === ZERO) {
      queue.push(nodeId);
      levels.set(nodeId, ZERO);
    }
  }

  let level = ZERO;
  while (queue.length > ZERO) {
    const levelSize = queue.length;
    const nextQueue: string[] = [];

    for (let i = ZERO; i < levelSize; i += ONE) {
      const nodeId = queue[i];
      if (!nodeId) {
        continue;
      }
      visited.add(nodeId);

      const targets = graph.get(nodeId) ?? [];
      for (const target of targets) {
        const newDegree = (inDegree.get(target) ?? ZERO) - ONE;
        inDegree.set(target, newDegree);

        if (newDegree === ZERO && !visited.has(target)) {
          nextQueue.push(target);
          levels.set(target, level + ONE);
        }
      }
    }

    queue = nextQueue;
    level += ONE;
  }

  return { levels, maxLevel: level };
};

const fillMissingLevels = (
  nodes: LayoutNode[],
  levels: Map<string, number>,
  defaultLevel: number,
): void => {
  for (const node of nodes) {
    if (!levels.has(node.id)) {
      levels.set(node.id, defaultLevel);
    }
  }
};

const groupByLevel = (levels: Map<string, number>): Map<number, string[]> => {
  const levelGroups = new Map<number, string[]>();
  for (const [nodeId, nodeLevel] of levels) {
    const group = levelGroups.get(nodeLevel);
    if (group) {
      group.push(nodeId);
    } else {
      levelGroups.set(nodeLevel, [nodeId]);
    }
  }
  return levelGroups;
};

const calculateLevelWidth = (
  nodeIds: string[],
  nodeMap: Map<string, LayoutNode>,
  nodeSep: number,
): number => {
  const totalNodeWidth = nodeIds.reduce((sum, id) => {
    const node = nodeMap.get(id);
    return sum + (node ? node.width : ZERO);
  }, ZERO);
  const totalSepWidth = Math.max(ZERO, nodeIds.length - ONE) * nodeSep;
  return totalNodeWidth + totalSepWidth;
};

const calculateMaxLevelWidth = (
  levelGroups: Map<number, string[]>,
  nodeMap: Map<string, LayoutNode>,
  nodeSep: number,
): number => {
  let maxWidth = ZERO;
  for (const nodeIds of levelGroups.values()) {
    const levelWidth = calculateLevelWidth(nodeIds, nodeMap, nodeSep);
    maxWidth = Math.max(maxWidth, levelWidth);
  }
  return maxWidth;
};

const placeLevelNodes = (
  nodeIds: string[],
  nodeMap: Map<string, LayoutNode>,
  positions: Record<string, { x: number; y: number }>,
  config: {
    isHorizontal: boolean;
    isReverse: boolean;
    primaryCoord: number;
    secondaryStart: number;
    offset: number;
    nodeSep: number;
    marginX: number;
    marginY: number;
    maxWidth: number;
    maxHeight: number;
  },
): { maxWidth: number; maxHeight: number } => {
  const {
    isHorizontal,
    isReverse,
    primaryCoord,
    secondaryStart,
    offset,
    nodeSep,
    marginX,
    marginY,
    maxWidth,
    maxHeight,
  } = config;

  let currentSecondary = secondaryStart;
  let nextMaxWidth = maxWidth;
  let nextMaxHeight = maxHeight;

  for (const nodeId of nodeIds) {
    const node = nodeMap.get(nodeId);
    if (!node) {
      continue;
    }

    if (isHorizontal) {
      const x = isReverse ? nextMaxWidth - primaryCoord : primaryCoord;
      const y = currentSecondary + offset;
      positions[nodeId] = { x, y };
      nextMaxWidth = Math.max(nextMaxWidth, x + node.width + marginX);
      nextMaxHeight = Math.max(nextMaxHeight, y + node.height + marginY);
    } else {
      const x = currentSecondary + offset;
      const y = isReverse ? nextMaxHeight - primaryCoord : primaryCoord;
      positions[nodeId] = { x, y };
      nextMaxWidth = Math.max(nextMaxWidth, x + node.width + marginX);
      nextMaxHeight = Math.max(nextMaxHeight, y + node.height + marginY);
    }

    currentSecondary += node.width + nodeSep;
  }

  return { maxHeight: nextMaxHeight, maxWidth: nextMaxWidth };
};

const normalizeSize = (width: number, height: number): { width: number; height: number } => ({
  width: width || DEFAULT_FORCE_WIDTH,
  height: height || DEFAULT_FORCE_HEIGHT,
});

/**
 * Dagre-style hierarchical layout
 */
const layoutDagre = (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutTaskOptions,
): LayoutResult => {
  const { onProgress } = options;
  reportProgress(onProgress, PROGRESS_START);

  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  const graph = createAdjacency(nodes, edges);
  reportProgress(onProgress, PROGRESS_GRAPH_READY);

  const inDegree = createInDegree(nodes, graph);
  reportProgress(onProgress, PROGRESS_INDEGREE_READY);

  const { levels, maxLevel } = assignLevels(graph, inDegree);
  reportProgress(onProgress, PROGRESS_LEVELS_READY);

  fillMissingLevels(nodes, levels, maxLevel);
  const levelGroups = groupByLevel(levels);
  reportProgress(onProgress, PROGRESS_GROUPED);

  const positions: Record<string, { x: number; y: number }> = {};
  const nodeSep = options.nodeSep ?? DEFAULT_NODE_SEP;
  const rankSep = options.rankSep ?? DEFAULT_RANK_SEP;
  const marginX = options.marginX ?? DEFAULT_MARGIN_X;
  const marginY = options.marginY ?? DEFAULT_MARGIN_Y;

  let maxWidth = ZERO;
  let maxHeight = ZERO;

  const direction = options.direction ?? 'TB';
  const isHorizontal = direction === 'LR' || direction === 'RL';
  const isReverse = direction === 'BT' || direction === 'RL';
  const maxLevelWidth = calculateMaxLevelWidth(levelGroups, nodeMap, nodeSep);

  for (const [nodeLevel, nodeIds] of levelGroups) {
    const levelWidth = calculateLevelWidth(nodeIds, nodeMap, nodeSep);
    const offset = (maxLevelWidth - levelWidth) / TWO;
    const primaryCoord = marginY + nodeLevel * rankSep;
    const secondaryStart = marginX;

    const updated = placeLevelNodes(nodeIds, nodeMap, positions, {
      isHorizontal,
      isReverse,
      primaryCoord,
      secondaryStart,
      offset,
      nodeSep,
      marginX,
      marginY,
      maxWidth,
      maxHeight,
    });
    ({ maxWidth } = updated);
    ({ maxHeight } = updated);
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);

  return {
    positions,
    size: normalizeSize(maxWidth, maxHeight),
  };
};

const initializeForcePositions = (
  nodes: LayoutNode[],
  width: number,
  height: number,
): Map<string, { x: number; y: number; vx: number; vy: number }> => {
  const positions = new Map<string, { x: number; y: number; vx: number; vy: number }>();
  for (const node of nodes) {
    positions.set(node.id, {
      vx: ZERO,
      vy: ZERO,
      x: Math.random() * width,
      y: Math.random() * height,
    });
  }
  return positions;
};

const applyRepulsion = (
  nodes: LayoutNode[],
  positions: Map<string, { x: number; y: number; vx: number; vy: number }>,
  k: number,
): void => {
  for (let i = ZERO; i < nodes.length; i += ONE) {
    const node1 = nodes[i];
    if (!node1) {
      continue;
    }
    const pos1 = positions.get(node1.id);
    if (!pos1) {
      continue;
    }

    for (let j = i + ONE; j < nodes.length; j += ONE) {
      const node2 = nodes[j];
      if (!node2) {
        continue;
      }
      const pos2 = positions.get(node2.id);
      if (!pos2) {
        continue;
      }

      const dx = pos2.x - pos1.x;
      const dy = pos2.y - pos1.y;
      const distance = Math.max(Math.hypot(dx, dy), DEFAULT_MIN_DISTANCE);
      const force = (k * k) / distance;

      pos1.vx -= (dx / distance) * force;
      pos1.vy -= (dy / distance) * force;
      pos2.vx += (dx / distance) * force;
      pos2.vy += (dy / distance) * force;
    }
  }
};

const applyAttraction = (
  edges: LayoutEdge[],
  positions: Map<string, { x: number; y: number; vx: number; vy: number }>,
  k: number,
): void => {
  for (const edge of edges) {
    const pos1 = positions.get(edge.source);
    const pos2 = positions.get(edge.target);

    if (!pos1 || !pos2) {
      continue;
    }

    const dx = pos2.x - pos1.x;
    const dy = pos2.y - pos1.y;
    const distance = Math.max(Math.hypot(dx, dy), DEFAULT_MIN_DISTANCE);
    const force = distance / k;

    pos1.vx += (dx / distance) * force;
    pos1.vy += (dy / distance) * force;
    pos2.vx -= (dx / distance) * force;
    pos2.vy -= (dy / distance) * force;
  }
};

const updateForcePositions = (
  positions: Map<string, { x: number; y: number; vx: number; vy: number }>,
  width: number,
  height: number,
): void => {
  for (const pos of positions.values()) {
    pos.x += pos.vx * DEFAULT_FORCE_DAMPING;
    pos.y += pos.vy * DEFAULT_FORCE_DAMPING;
    pos.vx *= DEFAULT_VELOCITY_DECAY;
    pos.vy *= DEFAULT_VELOCITY_DECAY;

    pos.x = clamp(pos.x, DEFAULT_BOUNDARY_PADDING, width - DEFAULT_BOUNDARY_PADDING);
    pos.y = clamp(pos.y, DEFAULT_BOUNDARY_PADDING, height - DEFAULT_BOUNDARY_PADDING);
  }
};

const reportIteration = (
  onProgress: ProgressCallback | undefined,
  iteration: number,
  iterations: number,
): void => {
  if (iteration % DEFAULT_GRID_PROGRESS_STEP === ZERO) {
    reportProgress(onProgress, (iteration / iterations) * PROGRESS_COMPLETE);
  }
};

/**
 * Force-directed layout (simple spring model)
 */
const layoutForce = (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutTaskOptions,
): LayoutResult => {
  const { onProgress } = options;
  const iterations = options.iterations ?? DEFAULT_FORCE_ITERATIONS;
  const width = DEFAULT_FORCE_WIDTH;
  const height = DEFAULT_FORCE_HEIGHT;

  const positions = initializeForcePositions(nodes, width, height);
  const k = Math.sqrt((width * height) / Math.max(nodes.length, ONE));

  for (let iteration = ZERO; iteration < iterations; iteration += ONE) {
    applyRepulsion(nodes, positions, k);
    applyAttraction(edges, positions, k);
    updateForcePositions(positions, width, height);
    reportIteration(onProgress, iteration, iterations);
  }

  reportProgress(onProgress, PROGRESS_COMPLETE);

  const result: Record<string, { x: number; y: number }> = {};
  for (const [nodeId, pos] of positions) {
    result[nodeId] = { x: pos.x, y: pos.y };
  }

  return {
    positions: result,
    size: { height, width },
  };
};

/**
 * Grid layout (fallback for unsupported layouts)
 */
const layoutGrid = (
  nodes: LayoutNode[],
  _edges: LayoutEdge[],
  options: LayoutTaskOptions,
): LayoutResult => {
  const { onProgress } = options;
  reportProgress(onProgress, PROGRESS_START);

  const positions: Record<string, { x: number; y: number }> = {};
  const perRow = Math.ceil(Math.sqrt(nodes.length));
  const nodeSep = options.nodeSep ?? DEFAULT_NODE_SEP;
  const marginX = options.marginX ?? DEFAULT_MARGIN_X;
  const marginY = options.marginY ?? DEFAULT_MARGIN_Y;

  let maxWidth = ZERO;
  let maxHeight = ZERO;

  nodes.forEach((node, index) => {
    const col = index % perRow;
    const row = Math.floor(index / perRow);

    const x = marginX + col * (node.width + nodeSep);
    const y = marginY + row * (node.height + nodeSep);

    positions[node.id] = { x, y };
    maxWidth = Math.max(maxWidth, x + node.width + marginX);
    maxHeight = Math.max(maxHeight, y + node.height + marginY);

    if (index % DEFAULT_GRID_PROGRESS_STEP === ZERO) {
      reportProgress(onProgress, (index / Math.max(nodes.length, ONE)) * PROGRESS_COMPLETE);
    }
  });

  reportProgress(onProgress, PROGRESS_COMPLETE);

  return {
    positions,
    size: { height: maxHeight, width: maxWidth },
  };
};

/**
 * Main layout function
 */
const computeLayout = (
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  options: LayoutTaskOptions,
): LayoutResult => {
  if (nodes.length === ZERO) {
    return { positions: {}, size: { height: ZERO, width: ZERO } };
  }

  switch (options.type) {
    case 'dagre':
    case 'hierarchical':
    case 'elk': {
      return layoutDagre(nodes, edges, options);
    }
    case 'force': {
      return layoutForce(nodes, edges, options);
    }
    default: {
      return layoutGrid(nodes, edges, options);
    }
  }
};

// Worker API
const api = {
  computeLayout,
};

expose(api);

export type GraphLayoutWorkerAPI = typeof api;
