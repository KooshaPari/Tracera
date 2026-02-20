import Graph from 'graphology';
import { describe, it, expect, beforeEach } from 'vitest';

import { GraphClustering } from '@/lib/graphology/clustering';

describe('GraphClustering', () => {
  let clustering: GraphClustering;
  let graph: Graph;

  beforeEach(() => {
    clustering = new GraphClustering();
    graph = new Graph({ type: 'undirected' });
  });

  describe('detectCommunities', () => {
    it('should detect communities using Louvain', () => {
      // Create two distinct communities
      graph.addNode('a1', { x: 0, y: 0 });
      graph.addNode('a2', { x: 0, y: 0 });
      graph.addNode('b1', { x: 100, y: 100 });
      graph.addNode('b2', { x: 100, y: 100 });

      graph.addEdge('a1', 'a2');
      graph.addEdge('b1', 'b2');
      graph.addEdge('a2', 'b1'); // Weak connection

      const communities = clustering.detectCommunities(graph);

      expect(communities.size).toBe(4);
      // a1 and a2 should be in same community
      expect(communities.get('a1')).toBe(communities.get('a2'));
    });

    it('should handle single node graph', () => {
      graph.addNode('single', { x: 0, y: 0 });

      const communities = clustering.detectCommunities(graph);

      expect(communities.size).toBe(1);
      expect(communities.get('single')).toBeDefined();
    });
  });

  describe('createClusterGraph', () => {
    it('should aggregate nodes into clusters', () => {
      // Create graph with 2 communities
      graph.addNode('a1', { x: 0, y: 0 });
      graph.addNode('a2', { x: 10, y: 10 });
      graph.addNode('b1', { x: 100, y: 100 });

      graph.addEdge('a1', 'a2');
      graph.addEdge('b1', 'a2');

      const communities = new Map([
        ['a1', 0],
        ['a2', 0],
        ['b1', 1],
      ]);

      const result = clustering.createClusterGraph(graph, communities);

      expect(result.communityCount).toBe(2);
      expect(result.nodes).toHaveLength(2);

      // Check cluster 0 has 2 members
      const cluster0 = result.nodes.find((n) => n.id === 'cluster-0');
      expect(cluster0?.size).toBe(2);
      expect(cluster0?.memberIds).toEqual(['a1', 'a2']);

      // Check averaged position
      expect(cluster0?.x).toBe(5); // (0 + 10) / 2
      expect(cluster0?.y).toBe(5); // (0 + 10) / 2
    });

    it('should aggregate edges between clusters', () => {
      graph.addNode('a1', { x: 0, y: 0 });
      graph.addNode('a2', { x: 0, y: 0 });
      graph.addNode('b1', { x: 0, y: 0 });

      // Multiple edges between communities
      graph.addEdge('a1', 'b1');
      graph.addEdge('a2', 'b1');

      const communities = new Map([
        ['a1', 0],
        ['a2', 0],
        ['b1', 1],
      ]);

      const result = clustering.createClusterGraph(graph, communities);

      expect(result.edges).toHaveLength(1);
      expect(result.edges[0].weight).toBe(2); // 2 edges aggregated
    });

    it('should calculate reduction ratio', () => {
      // Create graph with 100 intra-cluster edges + 2 inter-cluster edges
      for (let i = 0; i < 10; i++) {
        graph.addNode(`a${i}`, { x: 0, y: 0 });
        if (i > 0) graph.addEdge(`a${i - 1}`, `a${i}`);
      }

      for (let i = 0; i < 10; i++) {
        graph.addNode(`b${i}`, { x: 0, y: 0 });
        if (i > 0) graph.addEdge(`b${i - 1}`, `b${i}`);
      }

      graph.addEdge('a0', 'b0');

      const communities = new Map();
      for (let i = 0; i < 10; i++) {
        communities.set(`a${i}`, 0);
        communities.set(`b${i}`, 1);
      }

      const result = clustering.createClusterGraph(graph, communities);

      // 19 total edges → 1 inter-cluster edge = 94.7% reduction
      expect(result.reductionRatio).toBeGreaterThan(90);
    });

    it('should skip intra-cluster edges', () => {
      graph.addNode('a1', { x: 0, y: 0 });
      graph.addNode('a2', { x: 0, y: 0 });

      graph.addEdge('a1', 'a2'); // Intra-cluster edge

      const communities = new Map([
        ['a1', 0],
        ['a2', 0],
      ]);

      const result = clustering.createClusterGraph(graph, communities);

      expect(result.edges).toHaveLength(0); // No inter-cluster edges
    });
  });

  describe('getCommunityStatistics', () => {
    it('should calculate community statistics', () => {
      const communities = new Map([
        ['n1', 0],
        ['n2', 0],
        ['n3', 0],
        ['n4', 1],
        ['n5', 1],
        ['n6', 2],
      ]);

      const stats = clustering.getCommunityStatistics(communities);

      expect(stats.totalCommunities).toBe(3);
      expect(stats.largestCommunity).toBe(3);
      expect(stats.smallestCommunity).toBe(1);
      expect(stats.averageSize).toBe(2);
      expect(stats.sizes.get(0)).toBe(3);
      expect(stats.sizes.get(1)).toBe(2);
      expect(stats.sizes.get(2)).toBe(1);
    });
  });

  describe('filterClustersBySize', () => {
    it('should filter out small clusters', () => {
      const result = {
        nodes: [
          { id: 'c1', label: 'C1', size: 10, memberIds: [], x: 0, y: 0 },
          { id: 'c2', label: 'C2', size: 2, memberIds: [], x: 0, y: 0 },
          { id: 'c3', label: 'C3', size: 5, memberIds: [], x: 0, y: 0 },
        ],
        edges: [
          { id: 'e1', source: 'c1', target: 'c2', weight: 1 },
          { id: 'e2', source: 'c1', target: 'c3', weight: 1 },
        ],
        communityCount: 3,
        reductionRatio: 99.9,
      };

      const filtered = clustering.filterClustersBySize(result, 5);

      expect(filtered.nodes).toHaveLength(2); // c1 and c3
      expect(filtered.edges).toHaveLength(1); // only e2 remains
    });
  });

  describe('expandCluster', () => {
    it('should expand cluster to member nodes and edges', () => {
      graph.addNode('a1', { x: 0, y: 0 });
      graph.addNode('a2', { x: 0, y: 0 });
      graph.addNode('b1', { x: 0, y: 0 });

      graph.addEdge('a1', 'a2');
      graph.addEdge('a2', 'b1');

      const communities = new Map([
        ['a1', 0],
        ['a2', 0],
        ['b1', 1],
      ]);

      const expanded = clustering.expandCluster('cluster-0', graph, communities);

      expect(expanded.nodes).toEqual(['a1', 'a2']);
      expect(expanded.edges).toHaveLength(1); // Only a1-a2 edge
    });
  });

  describe('edge cases', () => {
    it('should handle empty graph', () => {
      const communities = clustering.detectCommunities(graph);
      expect(communities.size).toBe(0);
    });

    it('should handle graph with no edges', () => {
      graph.addNode('a1', { x: 0, y: 0 });
      graph.addNode('a2', { x: 0, y: 0 });

      const communities = clustering.detectCommunities(graph);
      expect(communities.size).toBe(2);

      const result = clustering.createClusterGraph(graph, communities);
      expect(result.edges).toHaveLength(0);
    });

    it('should handle missing node positions', () => {
      graph.addNode('a1', {}); // No x, y
      graph.addNode('a2', {});

      const communities = new Map([
        ['a1', 0],
        ['a2', 0],
      ]);

      const result = clustering.createClusterGraph(graph, communities);
      const cluster = result.nodes[0];

      expect(cluster.x).toBe(0); // Default to 0
      expect(cluster.y).toBe(0);
    });
  });

  describe('performance characteristics', () => {
    it('should handle moderately large graphs', () => {
      // Create a graph with 100 nodes and ~200 edges
      for (let i = 0; i < 100; i++) {
        graph.addNode(`n${i}`, {
          x: Math.random() * 1000,
          y: Math.random() * 1000,
        });
      }

      // Create edges to form clusters
      for (let i = 0; i < 100; i++) {
        const clusterStart = Math.floor(i / 10) * 10;
        const target = clusterStart + ((i + 1) % 10);
        if (i !== target) {
          graph.addEdge(`n${i}`, `n${target}`);
        }
      }

      const startTime = Date.now();
      const communities = clustering.detectCommunities(graph);
      const communityTime = Date.now() - startTime;

      expect(communities.size).toBe(100);
      expect(communityTime).toBeLessThan(1000); // Should complete in <1s

      const result = clustering.createClusterGraph(graph, communities);
      expect(result.communityCount).toBeGreaterThan(0);
    });
  });
});
