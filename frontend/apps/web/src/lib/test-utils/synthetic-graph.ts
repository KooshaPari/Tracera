/**
 * Synthetic Graph Generator for Testing
 *
 * Generates realistic graph structures for testing graph visualization
 * and performance benchmarks.
 */

import type { Edge, Node } from '@xyflow/react';

const ASSIGNEE_RANGE = Number('10');
const CHILD_RELATION_BIAS = Number('0.7');
const CLUSTER_DISTANCE_LIMIT = Number('1500');
const CLUSTER_OFFSET = Number('1000');
const CLUSTER_OFFSET_HALF = Number('0.5');
const CLUSTER_SPACING = Number('3000');
const DAYS_IN_YEAR = Number('365');
const DEFAULT_CLUSTER_SIZE = Number('100');
const DEFAULT_DENSITY = Number('0.5');
const DEFAULT_YEAR = Number('2024');
const EDGE_ATTEMPT_MULTIPLIER = Number('3');
const HIERARCHY_LEVEL_SPACING = Number('500');
const HIERARCHY_X_MULTIPLIER = Number('10');
const PRIORITY_OFFSET = Number('1');
const PRIORITY_RANGE = Number('5');
const RANDOM_POSITION_SCALE = Number('2');
const SEED_MODULUS = Number('2147483647');
const SEED_MODULUS_MINUS_ONE = Number('2147483646');
const SEED_MULTIPLIER = Number('16807');
const TWO = Number('2');

export interface SyntheticGraphOptions {
  /**
   * Node distribution strategy
   * - 'random': Fully random placement
   * - 'clustered': Nodes grouped in clusters
   * - 'hierarchical': Tree-like structure
   */
  distribution?: 'random' | 'clustered' | 'hierarchical' | undefined;

  /**
   * Edge density (0-1)
   * Controls how connected the graph is
   */
  density?: number | undefined;

  /**
   * Cluster count (for clustered distribution)
   */
  clusterCount?: number | undefined;

  /**
   * Seed for reproducible graphs
   */
  seed?: number | undefined;
}

export interface GraphMetrics {
  avgDegree: number;
  density: number;
  edgeCount: number;
  isolatedNodes: number;
  maxDegree: number;
  minDegree: number;
  nodeCount: number;
}

/**
 * Simple seeded random number generator
 */
class SeededRandom {
  private seed: number;

  constructor(seed: number = Date.now()) {
    this.seed = seed % SEED_MODULUS;
    if (this.seed <= 0) this.seed += SEED_MODULUS_MINUS_ONE;
  }

  next(): number {
    this.seed = (this.seed * SEED_MULTIPLIER) % SEED_MODULUS;
    return (this.seed - 1) / SEED_MODULUS_MINUS_ONE;
  }
}

const pickRandom = <T>(items: T[], rng: SeededRandom, fallback: T): T => {
  const index = Math.floor(rng.next() * items.length);
  return items[index] ?? fallback;
};

const buildClusteredPosition = (
  clusterCount: number,
  rng: SeededRandom,
): { x: number; y: number } => {
  const clusterId = Math.floor(rng.next() * clusterCount);
  const clusterWidth = Math.ceil(Math.sqrt(clusterCount));
  const clusterX = (clusterId % clusterWidth) * CLUSTER_SPACING;
  const clusterY = Math.floor(clusterId / clusterWidth) * CLUSTER_SPACING;
  const offsetX = (rng.next() - CLUSTER_OFFSET_HALF) * CLUSTER_OFFSET;
  const offsetY = (rng.next() - CLUSTER_OFFSET_HALF) * CLUSTER_OFFSET;

  return {
    x: clusterX + offsetX,
    y: clusterY + offsetY,
  };
};

const buildHierarchicalPosition = (index: number, nodeCount: number): { x: number; y: number } => {
  const level = Math.floor(Math.log2(index + 1));
  const posInLevel = index - (TWO ** level - 1);
  const levelWidth = TWO ** level;

  return {
    x: (posInLevel / levelWidth) * nodeCount * HIERARCHY_X_MULTIPLIER,
    y: level * HIERARCHY_LEVEL_SPACING,
  };
};

const buildRandomPosition = (nodeCount: number, rng: SeededRandom): { x: number; y: number } => ({
  x: rng.next() * nodeCount * RANDOM_POSITION_SCALE,
  y: rng.next() * nodeCount * RANDOM_POSITION_SCALE,
});

const buildNodeData = (
  index: number,
  rng: SeededRandom,
  nodeTypes: string[],
  statuses: string[],
): Node['data'] => {
  const type = pickRandom(nodeTypes, rng, nodeTypes[0] ?? 'node');
  const status = pickRandom(statuses, rng, statuses[0] ?? 'active');
  const priority = Math.floor(rng.next() * PRIORITY_RANGE) + PRIORITY_OFFSET;
  const assignee = `user-${Math.floor(rng.next() * ASSIGNEE_RANGE)}`;
  const created = new Date(DEFAULT_YEAR, 0, Math.floor(rng.next() * DAYS_IN_YEAR)).toISOString();

  return {
    assignee,
    created,
    description: `Test ${type} node ${index}`,
    label: `${type.charAt(0).toUpperCase() + type.slice(1)} ${index}`,
    priority,
    status,
    type,
  };
};

const buildNodes = (
  nodeCount: number,
  rng: SeededRandom,
  options: { clusterCount: number; distribution: string },
): Node[] => {
  const nodeTypes = ['requirement', 'test', 'defect', 'task', 'epic', 'story'];
  const statuses = ['active', 'completed', 'blocked', 'pending', 'in-progress'];

  return Array.from({ length: nodeCount }, (_unused, index) => {
    let position: { x: number; y: number };

    if (options.distribution === 'clustered') {
      position = buildClusteredPosition(options.clusterCount, rng);
    } else if (options.distribution === 'hierarchical') {
      position = buildHierarchicalPosition(index, nodeCount);
    } else {
      position = buildRandomPosition(nodeCount, rng);
    }

    return {
      data: buildNodeData(index, rng, nodeTypes, statuses),
      id: `node-${index}`,
      position,
      type: 'default',
    };
  });
};

const pickHierarchicalTarget = (
  sourceIdx: number,
  nodeCount: number,
  rng: SeededRandom,
): number => {
  const childStart = TWO * sourceIdx + 1;
  const childEnd = Math.min(TWO * sourceIdx + TWO, nodeCount - 1);

  if (childStart < nodeCount && rng.next() < CHILD_RELATION_BIAS) {
    return childStart + (childEnd > childStart && rng.next() > DEFAULT_DENSITY ? 1 : 0);
  }
  return Math.floor(rng.next() * nodeCount);
};

const pickClusteredTarget = (
  sourceIdx: number,
  nodeCount: number,
  nodes: Node[],
  rng: SeededRandom,
  density: number,
): number => {
  const sourceNode = nodes[sourceIdx];
  if (!sourceNode) {
    return Math.floor(rng.next() * nodeCount);
  }

  const candidates = nodes.filter((node, index) => {
    if (index === sourceIdx) return false;
    const dx = node.position.x - sourceNode.position.x;
    const dy = node.position.y - sourceNode.position.y;
    const distance = Math.hypot(dx, dy);
    return distance < CLUSTER_DISTANCE_LIMIT;
  });

  if (candidates.length > 0 && rng.next() < density) {
    const candidate = pickRandom(candidates, rng, candidates[0]!);
    const candidateIndex = nodes.findIndex((node) => node.id === candidate.id);
    return candidateIndex >= 0 ? candidateIndex : Math.floor(rng.next() * nodeCount);
  }

  return Math.floor(rng.next() * nodeCount);
};

const pickTargetIndex = (options: {
  distribution: string;
  density: number;
  nodeCount: number;
  nodes: Node[];
  seededRandom: SeededRandom;
  sourceIdx: number;
}): number => {
  const { distribution, density, nodeCount, nodes, seededRandom, sourceIdx } = options;

  if (distribution === 'hierarchical') {
    return pickHierarchicalTarget(sourceIdx, nodeCount, seededRandom);
  }
  if (distribution === 'clustered') {
    return pickClusteredTarget(sourceIdx, nodeCount, nodes, seededRandom, density);
  }
  return Math.floor(seededRandom.next() * nodeCount);
};

const buildEdges = (options: {
  clusterCount: number;
  density: number;
  distribution: string;
  edgeCount: number;
  nodeCount: number;
  nodes: Node[];
  seededRandom: SeededRandom;
}): Edge[] => {
  const { density, distribution, edgeCount, nodeCount, nodes, seededRandom } = options;

  const edges: Edge[] = [];
  const edgeSet = new Set<string>();
  const maxAttempts = edgeCount * EDGE_ATTEMPT_MULTIPLIER; // Prevent infinite loops
  let attempts = 0;

  const edgeTypes = ['default', 'smoothstep', 'step', 'straight'];
  const linkTypes = ['depends_on', 'blocks', 'relates_to', 'implements', 'tests'];

  while (edges.length < edgeCount && attempts < maxAttempts) {
    attempts += 1;

    const sourceIdx = Math.floor(seededRandom.next() * nodeCount);
    const targetIdx = pickTargetIndex({
      density,
      distribution,
      nodeCount,
      nodes,
      seededRandom,
      sourceIdx,
    });

    // Avoid self-loops
    if (sourceIdx === targetIdx) continue;

    const edgeKey = `${sourceIdx}-${targetIdx}`;
    const reverseKey = `${targetIdx}-${sourceIdx}`;

    // Avoid duplicates
    if (edgeSet.has(edgeKey) || edgeSet.has(reverseKey)) continue;

    edgeSet.add(edgeKey);

    const type = pickRandom(edgeTypes, seededRandom, 'default');
    const linkType = pickRandom(linkTypes, seededRandom, 'depends_on');
    const created = new Date(
      DEFAULT_YEAR,
      0,
      Math.floor(seededRandom.next() * DAYS_IN_YEAR),
    ).toISOString();

    edges.push({
      data: {
        created,
        linkType,
        weight: seededRandom.next(),
      },
      id: `edge-${edges.length}`,
      source: `node-${sourceIdx}`,
      target: `node-${targetIdx}`,
      type,
    });
  }

  return edges;
};

/**
 * Generate a synthetic graph for testing
 */
export const generateSyntheticGraph = (
  nodeCount: number,
  edgeCount: number,
  options: SyntheticGraphOptions = {},
): { nodes: Node[]; edges: Edge[] } => {
  const {
    clusterCount = Math.ceil(nodeCount / DEFAULT_CLUSTER_SIZE),
    density = DEFAULT_DENSITY,
    distribution = 'random',
    seed,
  } = options;

  const rng = new SeededRandom(seed);
  const nodes = buildNodes(nodeCount, rng, { clusterCount, distribution });
  const edges = buildEdges({
    clusterCount,
    density,
    distribution,
    edgeCount,
    nodeCount,
    nodes,
    seededRandom: rng,
  });

  return { edges, nodes };
};

const PERFORMANCE_GRAPH_CONFIGS = {
  large: { edges: 15000, nodes: 10000 },
  medium: { edges: 7500, nodes: 5000 },
  small: { edges: 1500, nodes: 1000 },
  xlarge: { edges: 75000, nodes: 50000 },
} as const;

/**
 * Generate a performance test graph with known characteristics
 */
export const generatePerformanceGraph = (
  size: 'small' | 'medium' | 'large' | 'xlarge',
): {
  edges: Edge[];
  nodes: Node[];
} => {
  const config = PERFORMANCE_GRAPH_CONFIGS[size];
  return generateSyntheticGraph(config.nodes, config.edges, {
    clusterCount: Math.ceil(config.nodes / DEFAULT_CLUSTER_SIZE),
    density: Number('0.6'),
    distribution: 'clustered',
  });
};

/**
 * Generate a minimal graph for quick tests
 */
export const generateMinimalGraph = (): { nodes: Node[]; edges: Edge[] } => ({
  edges: [
    {
      data: { linkType: 'depends_on' },
      id: 'edge-1',
      source: 'node-1',
      target: 'node-2',
      type: 'default',
    },
    {
      data: { linkType: 'tests' },
      id: 'edge-2',
      source: 'node-2',
      target: 'node-3',
      type: 'default',
    },
  ],
  nodes: [
    {
      data: { label: 'Node 1', status: 'active', type: 'requirement' },
      id: 'node-1',
      position: { x: 0, y: 0 },
      type: 'default',
    },
    {
      data: { label: 'Node 2', status: 'active', type: 'test' },
      id: 'node-2',
      position: { x: 200, y: 0 },
      type: 'default',
    },
    {
      data: { label: 'Node 3', status: 'blocked', type: 'defect' },
      id: 'node-3',
      position: { x: 100, y: 200 },
      type: 'default',
    },
  ],
});

/**
 * Calculate graph metrics
 */
export const calculateGraphMetrics = (nodes: Node[], edges: Edge[]): GraphMetrics => {
  const nodeCount = nodes.length;
  const edgeCount = edges.length;

  // Calculate average degree
  const degrees = new Map<string, number>();
  edges.forEach((edge) => {
    degrees.set(edge.source, (degrees.get(edge.source) || 0) + 1);
    degrees.set(edge.target, (degrees.get(edge.target) || 0) + 1);
  });

  const totalDegree = [...degrees.values()].reduce((sum, degree) => sum + degree, 0);
  const avgDegree = totalDegree / nodeCount;

  // Calculate density
  const maxEdges = (nodeCount * (nodeCount - 1)) / TWO;
  const density = edgeCount / maxEdges;

  // Find isolated nodes
  const connectedNodes = new Set([
    ...edges.map((edge) => edge.source),
    ...edges.map((edge) => edge.target),
  ]);
  const isolatedNodes = nodes.filter((node) => !connectedNodes.has(node.id)).length;

  return {
    avgDegree,
    density,
    edgeCount,
    isolatedNodes,
    maxDegree: Math.max(...degrees.values()),
    minDegree: Math.min(...degrees.values()),
    nodeCount,
  };
};
