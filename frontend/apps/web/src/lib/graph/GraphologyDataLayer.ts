/**
 * GraphologyDataLayer - High-performance graph data structure using Graphology
 *
 * Replaces legacy graph structure with Graphology for 100k+ node support
 *
 * Features:
 * - Graphology-based storage for efficient graph operations
 * - ReactFlow compatibility layer
 * - Incremental updates and synchronization
 * - Built-in clustering and layout computation
 * - Performance monitoring and benchmarks
 * - Memory-efficient data conversion
 *
 * Performance targets:
 * - Support 100k nodes with <2s initialization
 * - Layout computation: <5s for 100k nodes
 * - Memory usage: <500MB for 100k nodes
 */

import type { Node, Edge } from '@xyflow/react';
import type { Attributes } from 'graphology-types';

import Graph from 'graphology';
// Import clustering
import louvain from 'graphology-communities-louvain';
// Import layout algorithms
import forceAtlas2 from 'graphology-layout-forceatlas2';
import circular from 'graphology-layout/circular';
import random from 'graphology-layout/random';
// Import metrics
import { density, diameter } from 'graphology-metrics/graph';

import { logger } from '@/lib/logger';

/**
 * Node attributes stored in Graphology
 */
export interface GraphologyNodeData extends Attributes {
  id: string;
  label: string;
  type: string;
  x: number;
  y: number;
  size?: number | undefined;
  color?: string | undefined;
  // Original data from backend
  [key: string]: any;
}

/**
 * Edge attributes stored in Graphology
 */
export interface GraphologyEdgeData extends Attributes {
  id: string;
  label?: string | undefined;
  type?: string | undefined;
  weight?: number | undefined;
  color?: string | undefined;
  // Original data from backend
  [key: string]: any;
}

/**
 * Graph statistics
 */
export interface GraphStats {
  nodeCount: number;
  edgeCount: number;
  density: number;
  diameter: number;
  averageDegree: number;
  communityCount?: number | undefined;
  memoryUsage?: number | undefined;
}

/**
 * Performance metrics
 */
export interface PerformanceMetrics {
  initializationTime: number;
  layoutTime: number;
  conversionTime: number;
  totalMemory: number;
  nodeCount: number;
  edgeCount: number;
}

/**
 * Layout options
 */
export interface LayoutOptions {
  algorithm?: 'forceAtlas2' | 'circular' | 'random' | undefined;
  iterations?: number | undefined;
  settings?: {
    gravity?: number | undefined;
    scalingRatio?: number | undefined;
    strongGravityMode?: boolean | undefined;
    slowDown?: number | undefined;
    linLogMode?: boolean | undefined;
    outboundAttractionDistribution?: boolean | undefined;
    adjustSizes?: boolean | undefined;
    edgeWeightInfluence?: number | undefined;
    barnesHutOptimize?: boolean | undefined;
    barnesHutTheta?: number | undefined;
  };
}

/**
 * Main GraphologyDataLayer class
 */
export class GraphologyDataLayer {
  private graph: Graph;
  private performanceMetrics: PerformanceMetrics;
  private communities?: Map<string, number> | undefined;

  constructor() {
    this.graph = new Graph({
      multi: false,
      type: 'directed',
      allowSelfLoops: false,
    });

    this.performanceMetrics = {
      initializationTime: 0,
      layoutTime: 0,
      conversionTime: 0,
      totalMemory: 0,
      nodeCount: 0,
      edgeCount: 0,
    };
  }

  /**
   * Get the underlying Graphology instance
   */
  getGraph(): Graph {
    return this.graph;
  }

  /**
   * Initialize from ReactFlow data
   * Performance target: <2s for 100k nodes
   */
  async initialize(nodes: Node[], edges: Edge[]): Promise<void> {
    const startTime = performance.now();

    try {
      // Clear existing graph
      this.graph.clear();

      // Batch add nodes
      logger.debug(`[GraphologyDataLayer] Adding ${nodes.length} nodes...`);
      for (const node of nodes) {
        this.addNode(node);
      }

      // Batch add edges
      logger.debug(`[GraphologyDataLayer] Adding ${edges.length} edges...`);
      for (const edge of edges) {
        this.addEdge(edge);
      }

      const endTime = performance.now();
      this.performanceMetrics.initializationTime = endTime - startTime;
      this.performanceMetrics.nodeCount = this.graph.order;
      this.performanceMetrics.edgeCount = this.graph.size;

      logger.info(
        `[GraphologyDataLayer] Initialized graph with ${this.graph.order} nodes, ` +
          `${this.graph.size} edges in ${this.performanceMetrics.initializationTime.toFixed(2)}ms`,
      );
    } catch (error) {
      logger['error']('[GraphologyDataLayer] Initialization failed:', error);
      throw error;
    }
  }

  /**
   * Add a single node to the graph
   */
  addNode(node: Node): void {
    const data = (node.data as any) || {};
    const attributes: GraphologyNodeData = {
      id: node['id'],
      label: typeof data.label === 'string' ? data.label : node['id'],
      type: typeof node.type === 'string' ? node.type : 'default',
      x: node.position?.x || 0,
      y: node.position?.y || 0,
      size: typeof data.size === 'number' ? data.size : 10,
      color: typeof data.color === 'string' ? data.color : '#64748b',
      ...data,
    };

    try {
      if (this.graph.hasNode(node['id'])) {
        this.graph.updateNodeAttributes(node['id'], (attrs) => ({ ...attrs, ...attributes }));
      } else {
        this.graph.addNode(node['id'], attributes);
      }
    } catch (error) {
      logger.warn(`[GraphologyDataLayer] Failed to add node ${node['id']}:`, error);
    }
  }

  /**
   * Add a single edge to the graph
   */
  addEdge(edge: Edge): void {
    // Skip if source or target doesn't exist
    if (!this.graph.hasNode(edge.source) || !this.graph.hasNode(edge.target)) {
      logger.warn(
        `[GraphologyDataLayer] Skipping edge ${edge['id']}: ` + `source or target node not found`,
      );
      return;
    }

    const data = (edge.data as any) || {};
    const attributes: GraphologyEdgeData = {
      id: edge['id'],
      label: typeof data.label === 'string' ? data.label : undefined,
      type: typeof edge.type === 'string' ? edge.type : 'default',
      weight: typeof data.weight === 'number' ? data.weight : 1,
      color:
        typeof (edge.style as any)?.stroke === 'string' ? (edge.style as any).stroke : '#94a3b8',
      ...data,
    };

    try {
      // Check if edge already exists
      const existingEdge = this.graph.hasEdge(edge.source, edge.target);

      if (existingEdge) {
        // Update existing edge attributes using updateEdgeAttributes
        this.graph.updateEdgeAttributes(edge.source, edge.target, (attrs) => ({
          ...attrs,
          ...attributes,
        }));
      } else {
        this.graph.addEdge(edge.source, edge.target, attributes);
      }
    } catch (error) {
      // Silently skip duplicate edges in simple directed graphs
      // This is expected when multi:false and edge already exists
    }
  }

  /**
   * Remove a node from the graph
   */
  removeNode(nodeId: string): void {
    if (this.graph.hasNode(nodeId)) {
      this.graph.dropNode(nodeId);
    }
  }

  /**
   * Remove an edge from the graph
   */
  removeEdge(edgeId: string): void {
    try {
      this.graph.dropEdge(edgeId);
    } catch (error) {
      logger.warn(`[GraphologyDataLayer] Failed to remove edge ${edgeId}:`, error);
    }
  }

  /**
   * Update node attributes
   */
  updateNode(nodeId: string, updates: Partial<GraphologyNodeData>): void {
    if (this.graph.hasNode(nodeId)) {
      this.graph.updateNodeAttributes(nodeId, (attrs) => ({
        ...attrs,
        ...updates,
      }));
    }
  }

  /**
   * Update edge attributes
   */
  updateEdge(source: string, target: string, updates: Partial<GraphologyEdgeData>): void {
    if (this.graph.hasEdge(source, target)) {
      this.graph.updateEdgeAttributes(source, target, (attrs) => ({
        ...attrs,
        ...updates,
      }));
    }
  }

  /**
   * Convert back to ReactFlow format
   * Performance target: <500ms for 100k nodes
   */
  toReactFlow(): { nodes: Node[]; edges: Edge[] } {
    const startTime = performance.now();

    const nodes: Node[] = [];
    const edges: Edge[] = [];

    // Convert nodes
    this.graph.forEachNode((nodeId, attributes) => {
      const attrs = attributes as GraphologyNodeData;
      nodes.push({
        id: nodeId,
        type: attrs['type'] || 'default',
        position: {
          x: attrs.x || 0,
          y: attrs.y || 0,
        },
        data: {
          ...attrs,
        },
      });
    });

    // Convert edges
    this.graph.forEachEdge((edgeId, attributes, source, target) => {
      const attrs = attributes as GraphologyEdgeData;
      edges.push({
        id: attrs['id'] || edgeId,
        source,
        target,
        type: attrs['type'] || 'default',
        ...(attrs['label'] !== undefined ? { label: attrs['label'] } : {}),
        data: attrs,
        ...(attrs.color ? { style: { stroke: attrs.color } } : {}),
      });
    });

    const endTime = performance.now();
    this.performanceMetrics.conversionTime = endTime - startTime;

    logger.debug(
      `[GraphologyDataLayer] Converted to ReactFlow in ` +
        `${this.performanceMetrics.conversionTime.toFixed(2)}ms`,
    );

    return { nodes, edges };
  }

  /**
   * Compute graph layout
   * Performance target: <5s for 100k nodes
   */
  async computeLayout(options: LayoutOptions = {}): Promise<void> {
    const startTime = performance.now();

    const { algorithm = 'forceAtlas2', iterations = 500, settings = {} } = options;

    try {
      logger.debug(`[GraphologyDataLayer] Computing ${algorithm} layout...`);

      switch (algorithm) {
        case 'forceAtlas2':
          forceAtlas2.assign(this.graph, {
            iterations,
            settings: {
              gravity: settings.gravity ?? 1,
              scalingRatio: settings.scalingRatio ?? 10,
              strongGravityMode: settings.strongGravityMode ?? false,
              slowDown: settings.slowDown ?? 1,
              linLogMode: settings.linLogMode ?? false,
              outboundAttractionDistribution: settings.outboundAttractionDistribution ?? false,
              adjustSizes: settings.adjustSizes ?? false,
              edgeWeightInfluence: settings.edgeWeightInfluence ?? 1,
              barnesHutOptimize: settings.barnesHutOptimize ?? this.graph.order > 1000,
              barnesHutTheta: settings.barnesHutTheta ?? 0.5,
            },
          });
          break;

        case 'circular':
          circular.assign(this.graph, {
            center: 0,
            scale: 1000,
          });
          break;

        case 'random':
          random.assign(this.graph, {
            center: 0,
            scale: 1000,
          });
          break;

        default:
          throw new Error(`Unknown layout algorithm: ${algorithm}`);
      }

      const endTime = performance.now();
      this.performanceMetrics.layoutTime = endTime - startTime;

      logger.info(
        `[GraphologyDataLayer] Layout computed in ` +
          `${this.performanceMetrics.layoutTime.toFixed(2)}ms`,
      );
    } catch (error) {
      logger['error']('[GraphologyDataLayer] Layout computation failed:', error);
      throw error;
    }
  }

  /**
   * Detect communities using Louvain algorithm
   */
  async detectCommunities(): Promise<Map<string, number>> {
    const startTime = performance.now();

    try {
      const communities = louvain(this.graph);
      this.communities = new Map(Object.entries(communities));

      const endTime = performance.now();
      logger.info(
        `[GraphologyDataLayer] Detected ${this.communities.size} communities ` +
          `in ${(endTime - startTime).toFixed(2)}ms`,
      );

      return this.communities;
    } catch (error) {
      logger['error']('[GraphologyDataLayer] Community detection failed:', error);
      throw error;
    }
  }

  /**
   * Get communities (cached)
   */
  getCommunities(): Map<string, number> | undefined {
    return this.communities;
  }

  /**
   * Get graph statistics
   */
  getStats(): GraphStats {
    const nodeCount = this.graph.order;
    const edgeCount = this.graph.size;

    // Calculate metrics (expensive for large graphs)
    let graphDensity = 0;
    let graphDiameter = 0;
    let avgDegree = 0;

    try {
      graphDensity = density(this.graph);

      // Diameter is expensive, skip for large graphs
      if (nodeCount < 10000) {
        graphDiameter = diameter(this.graph);
      }

      // Calculate average degree
      let totalDegree = 0;
      this.graph.forEachNode((node) => {
        totalDegree += this.graph.degree(node);
      });
      avgDegree = nodeCount > 0 ? totalDegree / nodeCount : 0;
    } catch (error) {
      logger.warn('[GraphologyDataLayer] Failed to calculate some metrics:', error);
    }

    return {
      nodeCount,
      edgeCount,
      density: graphDensity,
      diameter: graphDiameter,
      averageDegree: avgDegree,
      communityCount: this.communities?.size,
    };
  }

  /**
   * Get node degree
   */
  getNodeDegree(nodeId: string): number {
    if (!this.graph.hasNode(nodeId)) return 0;
    return this.graph.degree(nodeId);
  }

  /**
   * Get node in-degree
   */
  getNodeInDegree(nodeId: string): number {
    if (!this.graph.hasNode(nodeId)) return 0;
    return this.graph.inDegree(nodeId);
  }

  /**
   * Get node out-degree
   */
  getNodeOutDegree(nodeId: string): number {
    if (!this.graph.hasNode(nodeId)) return 0;
    return this.graph.outDegree(nodeId);
  }

  /**
   * Get node neighbors
   */
  getNeighbors(nodeId: string): string[] {
    if (!this.graph.hasNode(nodeId)) return [];
    return this.graph.neighbors(nodeId);
  }

  /**
   * Get performance metrics
   */
  getPerformanceMetrics(): PerformanceMetrics {
    // Estimate memory usage
    const estimatedMemory =
      this.graph.order * 200 + // ~200 bytes per node
      this.graph.size * 100; // ~100 bytes per edge

    return {
      ...this.performanceMetrics,
      totalMemory: estimatedMemory,
    };
  }

  /**
   * Clear the graph
   */
  clear(): void {
    this.graph.clear();
    this.communities = undefined;
    this.performanceMetrics = {
      initializationTime: 0,
      layoutTime: 0,
      conversionTime: 0,
      totalMemory: 0,
      nodeCount: 0,
      edgeCount: 0,
    };
  }

  /**
   * Export graph as JSON
   */
  exportJSON(): any {
    return this.graph.export();
  }

  /**
   * Import graph from JSON
   */
  importJSON(data: any): void {
    this.graph.clear();
    this.graph.import(data);
  }
}

/**
 * Factory function to create GraphologyDataLayer
 */
export function createGraphologyDataLayer(): GraphologyDataLayer {
  return new GraphologyDataLayer();
}

/**
 * Singleton instance for global use
 */
let globalInstance: GraphologyDataLayer | null = null;

/**
 * Get or create global GraphologyDataLayer instance
 */
export function getGraphologyDataLayer(): GraphologyDataLayer {
  if (!globalInstance) {
    globalInstance = createGraphologyDataLayer();
  }
  return globalInstance;
}

/**
 * Reset global instance
 */
export function resetGraphologyDataLayer(): void {
  if (globalInstance) {
    globalInstance.clear();
    globalInstance = null;
  }
}
