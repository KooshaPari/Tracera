import type { Node, Edge } from '@xyflow/react';

import Graph from 'graphology';

import { logger } from '@/lib/logger';

import type {
  GraphologyAdapter,
  GraphologyNodeAttributes,
  GraphologyEdgeAttributes,
} from './types';

export class GraphologyDataAdapter implements GraphologyAdapter {
  private graph: Graph;

  constructor() {
    this.graph = new Graph({ multi: false, type: 'directed' });
  }

  getGraph(): Graph {
    return this.graph;
  }

  syncFromReactFlow(nodes: Node[], edges: Edge[]): void {
    this.graph.clear();

    // Add nodes with all data as attributes
    nodes.forEach((node) => {
      const data = (node.data as any) || {};
      const attributes: GraphologyNodeAttributes = {
        label: data.label || node.id,
        type: (node.type as string) || 'default',
        x: node.position?.x || 0,
        y: node.position?.y || 0,
        size: 10,
        color: data.color || '#64748b',
        ...data,
      };

      this.graph.addNode(node.id, attributes);
    });

    // Add edges with attributes
    edges.forEach((edge) => {
      // Skip if source or target doesn't exist
      if (!this.graph.hasNode(edge.source) || !this.graph.hasNode(edge.target)) {
        logger.warn(`Skipping edge ${edge.id}: source or target node not found`);
        return;
      }

      try {
        const data = (edge.data as any) || {};
        const attributes: GraphologyEdgeAttributes = {
          id: edge.id,
          label: typeof edge.label === 'string' ? edge.label : undefined,
          weight: 1,
          color:
            typeof (edge.style as any)?.stroke === 'string'
              ? (edge.style as any).stroke
              : '#94a3b8',
          ...data,
        };

        this.graph.addEdge(edge.source, edge.target, attributes);
      } catch (error) {
        // Edge already exists (shouldn't happen with multi: false, but catch anyway)
        logger.warn(`Edge ${edge.id} already exists or invalid`);
      }
    });
  }

  toReactFlow(): { nodes: Node[]; edges: Edge[] } {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    // Convert nodes
    this.graph.forEachNode((nodeId, attributes) => {
      nodes.push({
        id: nodeId,
        type: attributes['type'] || 'default',
        position: {
          x: attributes['x'] || 0,
          y: attributes['y'] || 0,
        },
        data: {
          label: attributes['label'],
          ...attributes,
        },
      });
    });

    // Convert edges
    this.graph.forEachEdge((edgeId, attributes, source, target) => {
      edges.push({
        id: attributes['id'] || edgeId,
        source,
        target,
        label: attributes['label'],
        data: attributes,
      });
    });

    return { nodes, edges };
  }

  async cluster(): Promise<Map<string, number>> {
    // Dynamically import Louvain (for code splitting)
    const louvainModule = await import('graphology-communities-louvain');
    const louvain = louvainModule.default;
    const communities = louvain(this.graph);
    return new Map(Object.entries(communities));
  }

  async computeLayout(iterations: number = 500): Promise<void> {
    // Dynamically import ForceAtlas2 (for code splitting)
    const forceAtlas2Module = await import('graphology-layout-forceatlas2');
    const forceAtlas2 = forceAtlas2Module.default;

    // Compute layout in-place (mutates graph node positions)
    forceAtlas2.assign(this.graph, {
      iterations,
      settings: {
        gravity: 1,
        scalingRatio: 10,
        strongGravityMode: false,
        slowDown: 1,
      },
    });
  }

  clear(): void {
    this.graph.clear();
  }

  // Utility: Get node count
  getNodeCount(): number {
    return this.graph.order;
  }

  // Utility: Get edge count
  getEdgeCount(): number {
    return this.graph.size;
  }

  // Utility: Get community statistics
  async getCommunityStats(communities: Map<string, number>): Promise<{
    communityCount: number;
    sizes: Map<number, number>;
    largestCommunity: number;
  }> {
    const sizes = new Map<number, number>();

    communities.forEach((communityId) => {
      sizes.set(communityId, (sizes.get(communityId) || 0) + 1);
    });

    const communityCount = sizes.size;
    const largestCommunity = Math.max(...Array.from(sizes.values()));

    return { communityCount, sizes, largestCommunity };
  }
}

// Export factory function
export function createGraphologyAdapter(): GraphologyAdapter {
  return new GraphologyDataAdapter();
}
