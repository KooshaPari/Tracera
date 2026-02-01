import type Graph from 'graphology';
import louvain from 'graphology-communities-louvain';

export interface ClusterNode {
  id: string;
  label: string;
  size: number; // Number of nodes in cluster
  memberIds: string[];
  x: number;
  y: number;
  color?: string;
  type?: string;
}

export interface ClusterEdge {
  id: string;
  source: string;
  target: string;
  weight: number; // Number of edges between clusters
  color?: string;
}

export interface ClusteringResult {
  nodes: ClusterNode[];
  edges: ClusterEdge[];
  communityCount: number;
  reductionRatio: number; // % reduction (e.g., 99.9 = 99.9% reduction)
}

export class GraphClustering {
  /**
   * Detect communities using Louvain algorithm
   * Performance: ~937ms for 50k nodes, 994k edges
   */
  detectCommunities(graph: Graph): Map<string, number> {
    const communities = louvain(graph);
    return new Map(Object.entries(communities));
  }

  /**
   * Create aggregated cluster graph from communities
   * Reduces 1M edges → <100 visible clusters
   */
  createClusterGraph(
    graph: Graph,
    communities: Map<string, number>
  ): ClusteringResult {
    const clusterNodes = new Map<number, ClusterNode>();
    const clusterEdgeWeights = new Map<string, number>();

    // Aggregate nodes into clusters
    graph.forEachNode((nodeId, attrs) => {
      const communityId = communities.get(nodeId) ?? 0;

      if (!clusterNodes.has(communityId)) {
        clusterNodes.set(communityId, {
          id: `cluster-${communityId}`,
          label: `Cluster ${communityId}`,
          size: 0,
          memberIds: [],
          x: 0,
          y: 0,
          color: this.generateClusterColor(communityId),
          type: 'cluster',
        });
      }

      const cluster = clusterNodes.get(communityId)!;
      cluster.size++;
      cluster.memberIds.push(nodeId);
      cluster.x += attrs.x || 0;
      cluster.y += attrs.y || 0;
    });

    // Average cluster positions
    clusterNodes.forEach(cluster => {
      cluster.x /= cluster.size;
      cluster.y /= cluster.size;
    });

    // Aggregate edges between clusters
    graph.forEachEdge((edgeId, attrs, source, target) => {
      const sourceCommunity = communities.get(source) ?? 0;
      const targetCommunity = communities.get(target) ?? 0;

      // Skip intra-cluster edges
      if (sourceCommunity === targetCommunity) return;

      const edgeKey = `${sourceCommunity}-${targetCommunity}`;
      clusterEdgeWeights.set(edgeKey, (clusterEdgeWeights.get(edgeKey) || 0) + 1);
    });

    // Build cluster edges
    const clusterEdges: ClusterEdge[] = Array.from(clusterEdgeWeights.entries()).map(
      ([key, weight]) => {
        const [source, target] = key.split('-');
        return {
          id: key,
          source: `cluster-${source}`,
          target: `cluster-${target}`,
          weight,
          color: '#94a3b8',
        };
      }
    );

    // Calculate reduction ratio
    const originalEdgeCount = graph.size;
    const clusterEdgeCount = clusterEdges.length;
    const reductionRatio = ((1 - clusterEdgeCount / originalEdgeCount) * 100);

    return {
      nodes: Array.from(clusterNodes.values()),
      edges: clusterEdges,
      communityCount: clusterNodes.size,
      reductionRatio,
    };
  }

  /**
   * Get detailed community statistics
   */
  getCommunityStatistics(communities: Map<string, number>): {
    totalCommunities: number;
    sizes: Map<number, number>;
    largestCommunity: number;
    smallestCommunity: number;
    averageSize: number;
    modularity?: number;
  } {
    const sizes = new Map<number, number>();

    communities.forEach((communityId) => {
      sizes.set(communityId, (sizes.get(communityId) || 0) + 1);
    });

    const sizeValues = Array.from(sizes.values());
    const totalCommunities = sizes.size;
    const largestCommunity = Math.max(...sizeValues);
    const smallestCommunity = Math.min(...sizeValues);
    const averageSize = communities.size / totalCommunities;

    return {
      totalCommunities,
      sizes,
      largestCommunity,
      smallestCommunity,
      averageSize,
    };
  }

  /**
   * Generate deterministic color for cluster based on ID
   */
  private generateClusterColor(clusterId: number): string {
    const hue = (clusterId * 137.508) % 360; // Golden angle for good distribution
    return `hsl(${hue}, 70%, 60%)`;
  }

  /**
   * Filter clusters by minimum size (remove small clusters)
   */
  filterClustersBySize(
    result: ClusteringResult,
    minSize: number
  ): ClusteringResult {
    const filteredNodes = result.nodes.filter(node => node.size >= minSize);
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));

    const filteredEdges = result.edges.filter(
      edge => filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target)
    );

    return {
      nodes: filteredNodes,
      edges: filteredEdges,
      communityCount: filteredNodes.length,
      reductionRatio: result.reductionRatio,
    };
  }

  /**
   * Expand a cluster back to individual nodes
   */
  expandCluster(
    clusterId: string,
    graph: Graph,
    communities: Map<string, number>
  ): { nodes: string[]; edges: string[] } {
    const clusterNumber = parseInt(clusterId.replace('cluster-', ''));
    const memberNodes: string[] = [];

    communities.forEach((community, nodeId) => {
      if (community === clusterNumber) {
        memberNodes.push(nodeId);
      }
    });

    const memberEdges: string[] = [];
    graph.forEachEdge((edgeId, attrs, source, target) => {
      if (memberNodes.includes(source) && memberNodes.includes(target)) {
        memberEdges.push(edgeId);
      }
    });

    return { nodes: memberNodes, edges: memberEdges };
  }
}

// Export factory function
export function createClustering(): GraphClustering {
  return new GraphClustering();
}
