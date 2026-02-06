import type { Node, Edge } from '@xyflow/react';

import { describe, it, expect } from 'vitest';

import { createGraphologyAdapter } from '@/lib/graphology/adapter';
import { createClustering } from '@/lib/graphology/clustering';
import { logger } from '@/lib/logger';

describe('Graphology Integration: Adapter + Clustering', () => {
  it('should cluster React Flow graph and reduce edges', () => {
    // Create React Flow data
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    // Create 3 clusters of 10 nodes each
    for (let cluster = 0; cluster < 3; cluster++) {
      for (let i = 0; i < 10; i++) {
        const nodeId = `node-${cluster}-${i}`;
        nodes.push({
          id: nodeId,
          type: 'default',
          position: { x: cluster * 200 + i * 20, y: cluster * 200 + i * 20 },
          data: { label: `Node ${cluster}-${i}` },
        });

        // Connect within cluster
        if (i > 0) {
          edges.push({
            id: `edge-${cluster}-${i}`,
            source: `node-${cluster}-${i - 1}`,
            target: nodeId,
          });
        }
      }
    }

    // Add inter-cluster edges
    edges.push({
      id: 'inter-0-1',
      source: 'node-0-0',
      target: 'node-1-0',
    });
    edges.push({
      id: 'inter-1-2',
      source: 'node-1-0',
      target: 'node-2-0',
    });

    logger.info('Original graph:', nodes.length, 'nodes,', edges.length, 'edges');

    // Step 1: Sync to Graphology
    const adapter = createGraphologyAdapter();
    adapter.syncFromReactFlow(nodes, edges);

    const graph = adapter.getGraph();
    expect(graph.order).toBe(30); // 30 nodes
    expect(graph.size).toBe(29); // 27 intra + 2 inter

    // Step 2: Detect communities
    const clustering = createClustering();
    const communities = clustering.detectCommunities(graph);

    expect(communities.size).toBe(30);

    // Step 3: Create cluster graph
    const result = clustering.createClusterGraph(graph, communities);

    logger.info(
      'Clustered graph:',
      result.communityCount,
      'clusters,',
      result.edges.length,
      'edges',
    );
    logger.info('Reduction ratio:', result.reductionRatio.toFixed(1), '%');

    // Should detect communities (may not match human intuition due to modularity optimization)
    expect(result.communityCount).toBeGreaterThanOrEqual(2);
    expect(result.communityCount).toBeLessThanOrEqual(10);

    // Should reduce edges significantly
    expect(result.edges.length).toBeLessThan(edges.length);
    expect(result.reductionRatio).toBeGreaterThan(50); // At least 50% reduction

    // Step 4: Convert back to React Flow
    const clusterNodes = result.nodes.map((cluster) => ({
      id: cluster.id,
      type: 'cluster',
      position: { x: cluster.x, y: cluster.y },
      data: {
        label: cluster.label,
        size: cluster.size,
        memberIds: cluster.memberIds,
        color: cluster.color,
      },
    }));

    const clusterEdges = result.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: `${edge.weight} edges`,
    }));

    expect(clusterNodes.length).toBe(result.communityCount);
    expect(clusterEdges.length).toBe(result.edges.length);
  });

  it('should handle large graph clustering performance', () => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    // Create 500 nodes
    for (let i = 0; i < 500; i++) {
      nodes.push({
        id: `node-${i}`,
        type: 'default',
        position: { x: Math.random() * 5000, y: Math.random() * 5000 },
        data: { label: `Node ${i}` },
      });
    }

    // Create ~1500 edges (3 per node average)
    for (let i = 0; i < 500; i++) {
      for (let j = 0; j < 3; j++) {
        const target = Math.floor(Math.random() * 500);
        if (target !== i) {
          edges.push({
            id: `edge-${i}-${j}`,
            source: `node-${i}`,
            target: `node-${target}`,
          });
        }
      }
    }

    const adapter = createGraphologyAdapter();
    adapter.syncFromReactFlow(nodes, edges);

    const graph = adapter.getGraph();
    const clustering = createClustering();

    const startTime = performance.now();
    const communities = clustering.detectCommunities(graph);
    const result = clustering.createClusterGraph(graph, communities);
    const duration = performance.now() - startTime;

    logger.info('Performance test:');
    logger.info('- Graph size:', graph.order, 'nodes,', graph.size, 'edges');
    logger.info('- Processing time:', duration.toFixed(0), 'ms');
    logger.info('- Clusters:', result.communityCount);
    logger.info('- Reduction:', result.reductionRatio.toFixed(1), '%');

    // Should complete in reasonable time
    expect(duration).toBeLessThan(2000); // < 2 seconds for 500 nodes

    // Should achieve significant reduction
    expect(result.reductionRatio).toBeGreaterThan(70);
  });

  it('should expand cluster back to nodes', () => {
    const nodes: Node[] = [
      { id: 'a1', type: 'default', position: { x: 0, y: 0 }, data: {} },
      { id: 'a2', type: 'default', position: { x: 10, y: 10 }, data: {} },
      { id: 'b1', type: 'default', position: { x: 100, y: 100 }, data: {} },
    ];

    const edges: Edge[] = [
      { id: 'e1', source: 'a1', target: 'a2' },
      { id: 'e2', source: 'a2', target: 'b1' },
    ];

    const adapter = createGraphologyAdapter();
    adapter.syncFromReactFlow(nodes, edges);

    const graph = adapter.getGraph();
    const clustering = createClustering();
    const communities = clustering.detectCommunities(graph);
    const result = clustering.createClusterGraph(graph, communities);

    // Expand first cluster
    const firstCluster = result.nodes[0];
    const expanded = clustering.expandCluster(firstCluster.id, graph, communities);

    expect(expanded.nodes.length).toBeGreaterThan(0);
    expect(expanded.nodes.length).toBeLessThanOrEqual(3);

    // All expanded nodes should be in the original graph
    expanded.nodes.forEach((nodeId) => {
      expect(graph.hasNode(nodeId)).toBe(true);
    });
  });
});
