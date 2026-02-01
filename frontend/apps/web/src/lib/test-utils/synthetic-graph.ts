/**
 * Synthetic Graph Generator for Testing
 *
 * Generates realistic graph structures for testing graph visualization
 * and performance benchmarks.
 */

import type { Node, Edge } from '@xyflow/react';

export interface SyntheticGraphOptions {
  /**
   * Node distribution strategy
   * - 'random': Fully random placement
   * - 'clustered': Nodes grouped in clusters
   * - 'hierarchical': Tree-like structure
   */
  distribution?: 'random' | 'clustered' | 'hierarchical';

  /**
   * Edge density (0-1)
   * Controls how connected the graph is
   */
  density?: number;

  /**
   * Cluster count (for clustered distribution)
   */
  clusterCount?: number;

  /**
   * Seed for reproducible graphs
   */
  seed?: number;
}

/**
 * Simple seeded random number generator
 */
class SeededRandom {
  private seed: number;

  constructor(seed: number = Date.now()) {
    this.seed = seed % 2147483647;
    if (this.seed <= 0) this.seed += 2147483646;
  }

  next(): number {
    this.seed = (this.seed * 16807) % 2147483647;
    return (this.seed - 1) / 2147483646;
  }
}

/**
 * Generate a synthetic graph for testing
 */
export function generateSyntheticGraph(
  nodeCount: number,
  edgeCount: number,
  options: SyntheticGraphOptions = {}
): { nodes: Node[]; edges: Edge[] } {
  const {
    distribution = 'random',
    density = 0.5,
    clusterCount = Math.ceil(nodeCount / 100),
    seed,
  } = options;

  const rng = new SeededRandom(seed);
  const nodeTypes = ['requirement', 'test', 'defect', 'task', 'epic', 'story'];
  const statuses = ['active', 'completed', 'blocked', 'pending', 'in-progress'];

  // Generate nodes
  const nodes: Node[] = Array.from({ length: nodeCount }, (_, i) => {
    let position: { x: number; y: number };

    if (distribution === 'clustered') {
      // Assign to cluster and position within cluster
      const clusterId = Math.floor(rng.next() * clusterCount);
      const clusterX = (clusterId % Math.ceil(Math.sqrt(clusterCount))) * 3000;
      const clusterY = Math.floor(clusterId / Math.ceil(Math.sqrt(clusterCount))) * 3000;
      const offsetX = (rng.next() - 0.5) * 1000;
      const offsetY = (rng.next() - 0.5) * 1000;

      position = {
        x: clusterX + offsetX,
        y: clusterY + offsetY,
      };
    } else if (distribution === 'hierarchical') {
      // Tree-like structure
      const level = Math.floor(Math.log2(i + 1));
      const posInLevel = i - (Math.pow(2, level) - 1);
      const levelWidth = Math.pow(2, level);

      position = {
        x: (posInLevel / levelWidth) * nodeCount * 10,
        y: level * 500,
      };
    } else {
      // Random distribution
      position = {
        x: rng.next() * nodeCount * 2,
        y: rng.next() * nodeCount * 2,
      };
    }

    const type = nodeTypes[Math.floor(rng.next() * nodeTypes.length)];
    const status = statuses[Math.floor(rng.next() * statuses.length)];

    return {
      id: `node-${i}`,
      type: 'default',
      position,
      data: {
        label: `${type.charAt(0).toUpperCase() + type.slice(1)} ${i}`,
        type,
        status,
        description: `Test ${type} node ${i}`,
        priority: Math.floor(rng.next() * 5) + 1,
        assignee: `user-${Math.floor(rng.next() * 10)}`,
        created: new Date(2024, 0, Math.floor(rng.next() * 365)).toISOString(),
      },
    };
  });

  // Generate edges ensuring valid connections
  const edges: Edge[] = [];
  const edgeSet = new Set<string>();
  const maxAttempts = edgeCount * 3; // Prevent infinite loops
  let attempts = 0;

  while (edges.length < edgeCount && attempts < maxAttempts) {
    attempts++;

    const sourceIdx = Math.floor(rng.next() * nodeCount);
    let targetIdx: number;

    if (distribution === 'hierarchical') {
      // Prefer parent-child relationships in hierarchical graphs
      const childStart = 2 * sourceIdx + 1;
      const childEnd = Math.min(2 * sourceIdx + 2, nodeCount - 1);

      if (childStart < nodeCount && rng.next() < 0.7) {
        targetIdx = childStart + (childEnd > childStart && rng.next() > 0.5 ? 1 : 0);
      } else {
        targetIdx = Math.floor(rng.next() * nodeCount);
      }
    } else if (distribution === 'clustered') {
      // Prefer connections within same cluster
      const sourceNode = nodes[sourceIdx];
      const candidates = nodes.filter((n, idx) => {
        if (idx === sourceIdx) return false;
        const dx = n.position.x - sourceNode.position.x;
        const dy = n.position.y - sourceNode.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        return distance < 1500;
      });

      if (candidates.length > 0 && rng.next() < density) {
        const candidate = candidates[Math.floor(rng.next() * candidates.length)];
        targetIdx = nodes.findIndex(n => n.id === candidate.id);
      } else {
        targetIdx = Math.floor(rng.next() * nodeCount);
      }
    } else {
      targetIdx = Math.floor(rng.next() * nodeCount);
    }

    // Avoid self-loops
    if (sourceIdx === targetIdx) continue;

    const edgeKey = `${sourceIdx}-${targetIdx}`;
    const reverseKey = `${targetIdx}-${sourceIdx}`;

    // Avoid duplicates
    if (edgeSet.has(edgeKey) || edgeSet.has(reverseKey)) continue;

    edgeSet.add(edgeKey);

    const edgeTypes = ['default', 'smoothstep', 'step', 'straight'];
    const linkTypes = ['depends_on', 'blocks', 'relates_to', 'implements', 'tests'];

    edges.push({
      id: `edge-${edges.length}`,
      source: `node-${sourceIdx}`,
      target: `node-${targetIdx}`,
      type: edgeTypes[Math.floor(rng.next() * edgeTypes.length)],
      data: {
        linkType: linkTypes[Math.floor(rng.next() * linkTypes.length)],
        weight: rng.next(),
        created: new Date(2024, 0, Math.floor(rng.next() * 365)).toISOString(),
      },
    });
  }

  return { nodes, edges };
}

/**
 * Generate a performance test graph with known characteristics
 */
export function generatePerformanceGraph(size: 'small' | 'medium' | 'large' | 'xlarge'): {
  nodes: Node[];
  edges: Edge[];
} {
  const configs = {
    small: { nodes: 1000, edges: 1500 },
    medium: { nodes: 5000, edges: 7500 },
    large: { nodes: 10000, edges: 15000 },
    xlarge: { nodes: 50000, edges: 75000 },
  };

  const config = configs[size];
  return generateSyntheticGraph(config.nodes, config.edges, {
    distribution: 'clustered',
    density: 0.6,
    clusterCount: Math.ceil(config.nodes / 100),
  });
}

/**
 * Generate a minimal graph for quick tests
 */
export function generateMinimalGraph(): { nodes: Node[]; edges: Edge[] } {
  return {
    nodes: [
      {
        id: 'node-1',
        type: 'default',
        position: { x: 0, y: 0 },
        data: { label: 'Node 1', type: 'requirement', status: 'active' },
      },
      {
        id: 'node-2',
        type: 'default',
        position: { x: 200, y: 0 },
        data: { label: 'Node 2', type: 'test', status: 'active' },
      },
      {
        id: 'node-3',
        type: 'default',
        position: { x: 100, y: 200 },
        data: { label: 'Node 3', type: 'defect', status: 'blocked' },
      },
    ],
    edges: [
      {
        id: 'edge-1',
        source: 'node-1',
        target: 'node-2',
        type: 'default',
        data: { linkType: 'depends_on' },
      },
      {
        id: 'edge-2',
        source: 'node-2',
        target: 'node-3',
        type: 'default',
        data: { linkType: 'tests' },
      },
    ],
  };
}

/**
 * Calculate graph metrics
 */
export function calculateGraphMetrics(nodes: Node[], edges: Edge[]) {
  const nodeCount = nodes.length;
  const edgeCount = edges.length;

  // Calculate average degree
  const degrees = new Map<string, number>();
  edges.forEach(edge => {
    degrees.set(edge.source, (degrees.get(edge.source) || 0) + 1);
    degrees.set(edge.target, (degrees.get(edge.target) || 0) + 1);
  });

  const avgDegree = Array.from(degrees.values()).reduce((sum, d) => sum + d, 0) / nodeCount;

  // Calculate density
  const maxEdges = nodeCount * (nodeCount - 1) / 2;
  const density = edgeCount / maxEdges;

  // Find isolated nodes
  const connectedNodes = new Set([...edges.map(e => e.source), ...edges.map(e => e.target)]);
  const isolatedNodes = nodes.filter(n => !connectedNodes.has(n.id)).length;

  return {
    nodeCount,
    edgeCount,
    avgDegree,
    density,
    isolatedNodes,
    maxDegree: Math.max(...Array.from(degrees.values())),
    minDegree: Math.min(...Array.from(degrees.values())),
  };
}
