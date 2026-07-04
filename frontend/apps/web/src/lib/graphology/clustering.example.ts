/**
 * Graphology Clustering Usage Examples
 *
 * Demonstrates how to use the GraphClustering class to reduce
 * large graphs from 1M edges to <100 visible clusters.
 */

import Graph from 'graphology';

import { logger } from '@/lib/logger';

import { createClustering, type ClusteringResult } from './clustering';

// Example 1: Basic clustering workflow
export function basicClusteringExample() {
  // Create a graph with 100 nodes
  const graph = new Graph({ type: 'undirected' });

  // Add nodes with positions
  for (let i = 0; i < 100; i++) {
    graph.addNode(`node-${i}`, {
      label: `Node ${i}`,
      x: Math.random() * 1000,
      y: Math.random() * 1000,
    });
  }

  // Add edges to form clusters (10 clusters of 10 nodes each)
  for (let cluster = 0; cluster < 10; cluster++) {
    for (let i = 0; i < 10; i++) {
      const nodeA = `node-${cluster * 10 + i}`;
      const nodeB = `node-${cluster * 10 + ((i + 1) % 10)}`;
      graph.addEdge(nodeA, nodeB);
    }
  }

  // Add some inter-cluster edges
  graph.addEdge('node-0', 'node-10');
  graph.addEdge('node-20', 'node-30');

  // Perform clustering
  const clustering = createClustering();
  const communities = clustering.detectCommunities(graph);
  const result = clustering.createClusterGraph(graph, communities);

  logger.info(`Original: ${graph.order} nodes, ${graph.size} edges`);
  logger.info(`Clustered: ${result.communityCount} clusters, ${result.edges.length} edges`);
  logger.info(`Reduction: ${result.reductionRatio.toFixed(1)}%`);

  return result;
}

// Example 2: Filtering small clusters
export function filterSmallClustersExample() {
  const graph = new Graph({ type: 'undirected' });

  // Create graph with mixed cluster sizes
  // Large cluster A: 50 nodes
  for (let i = 0; i < 50; i++) {
    graph.addNode(`a${i}`, { x: 0, y: 0 });
    if (i > 0) graph.addEdge(`a${i - 1}`, `a${i}`);
  }

  // Medium cluster B: 20 nodes
  for (let i = 0; i < 20; i++) {
    graph.addNode(`b${i}`, { x: 100, y: 0 });
    if (i > 0) graph.addEdge(`b${i - 1}`, `b${i}`);
  }

  // Small clusters C, D, E: 2 nodes each
  for (const cluster of ['c', 'd', 'e']) {
    graph.addNode(`${cluster}0`, { x: 200, y: 0 });
    graph.addNode(`${cluster}1`, { x: 200, y: 0 });
    graph.addEdge(`${cluster}0`, `${cluster}1`);
  }

  const clustering = createClustering();
  const communities = clustering.detectCommunities(graph);
  const result = clustering.createClusterGraph(graph, communities);

  logger.info('Before filtering:', result.nodes.length, 'clusters');

  // Filter out clusters with < 10 nodes
  const filtered = clustering.filterClustersBySize(result, 10);

  logger.info('After filtering:', filtered.nodes.length, 'clusters');
  logger.info(
    'Clusters:',
    filtered.nodes.map((n) => `${n.label} (${n.size} nodes)`),
  );

  return filtered;
}

// Example 3: Community statistics
export function communityStatisticsExample() {
  const graph = new Graph({ type: 'undirected' });

  // Create graph with known community structure
  for (let i = 0; i < 100; i++) {
    graph.addNode(`node-${i}`, { x: i * 10, y: i * 10 });
  }

  // Dense intra-cluster edges
  for (let i = 0; i < 100; i++) {
    const cluster = Math.floor(i / 10);
    const clusterStart = cluster * 10;
    const clusterEnd = clusterStart + 10;

    for (let j = clusterStart; j < clusterEnd; j++) {
      if (i !== j) {
        graph.addEdge(`node-${i}`, `node-${j}`);
      }
    }
  }

  const clustering = createClustering();
  const communities = clustering.detectCommunities(graph);
  const stats = clustering.getCommunityStatistics(communities);

  logger.info('Community Statistics:');
  logger.info('- Total communities:', stats.totalCommunities);
  logger.info('- Largest community:', stats.largestCommunity, 'nodes');
  logger.info('- Smallest community:', stats.smallestCommunity, 'nodes');
  logger.info('- Average size:', stats.averageSize.toFixed(1), 'nodes');
  logger.info('- Size distribution:', Array.from(stats.sizes.entries()));

  return stats;
}

// Example 4: Expanding a cluster
export function expandClusterExample() {
  const graph = new Graph({ type: 'undirected' });

  // Create simple graph with 2 clusters
  graph.addNode('a1', { x: 0, y: 0 });
  graph.addNode('a2', { x: 10, y: 10 });
  graph.addNode('a3', { x: 20, y: 20 });
  graph.addNode('b1', { x: 100, y: 100 });
  graph.addNode('b2', { x: 110, y: 110 });

  graph.addEdge('a1', 'a2');
  graph.addEdge('a2', 'a3');
  graph.addEdge('b1', 'b2');
  graph.addEdge('a3', 'b1'); // Inter-cluster edge

  const clustering = createClustering();
  const communities = clustering.detectCommunities(graph);

  // Expand first cluster
  const clusterId = 'cluster-0';
  const expanded = clustering.expandCluster(clusterId, graph, communities);

  logger.info('Expanded cluster', clusterId);
  logger.info('- Member nodes:', expanded.nodes);
  logger.info('- Internal edges:', expanded.edges);

  return expanded;
}

// Example 5: React Flow integration
export function reactFlowIntegrationExample() {
  const graph = new Graph({ type: 'undirected' });

  // Add sample nodes and edges
  for (let i = 0; i < 50; i++) {
    graph.addNode(`node-${i}`, {
      label: `Node ${i}`,
      x: Math.random() * 1000,
      y: Math.random() * 1000,
      type: i < 25 ? 'requirement' : 'test',
    });
  }

  // Add edges
  for (let i = 0; i < 50; i++) {
    const target = (i + Math.floor(Math.random() * 5) + 1) % 50;
    graph.addEdge(`node-${i}`, `node-${target}`);
  }

  const clustering = createClustering();
  const communities = clustering.detectCommunities(graph);
  const result = clustering.createClusterGraph(graph, communities);

  // Convert to React Flow nodes
  const reactFlowNodes = result.nodes.map((cluster) => ({
    id: cluster.id,
    type: 'cluster',
    position: { x: cluster.x, y: cluster.y },
    data: {
      label: cluster.label,
      size: cluster.size,
      memberIds: cluster.memberIds,
      color: cluster.color,
      isExpanded: false,
      onExpand: (id: string) => logger.info('Expand', id),
      onCollapse: (id: string) => logger.info('Collapse', id),
    },
  }));

  // Convert to React Flow edges
  const reactFlowEdges = result.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: `${edge.weight} edges`,
    style: { stroke: edge.color, strokeWidth: Math.min(edge.weight / 2, 5) },
  }));

  return { nodes: reactFlowNodes, edges: reactFlowEdges };
}

// Example 6: Performance benchmark for large graphs
export function performanceBenchmarkExample() {
  logger.info('Creating large graph...');
  const graph = new Graph({ type: 'undirected' });

  // Create 10,000 nodes
  for (let i = 0; i < 10000; i++) {
    graph.addNode(`node-${i}`, {
      x: Math.random() * 10000,
      y: Math.random() * 10000,
    });
  }

  // Create ~50,000 edges (5 edges per node on average)
  for (let i = 0; i < 10000; i++) {
    for (let j = 0; j < 5; j++) {
      const target = Math.floor(Math.random() * 10000);
      if (target !== i && !graph.hasEdge(`node-${i}`, `node-${target}`)) {
        graph.addEdge(`node-${i}`, `node-${target}`);
      }
    }
  }

  logger.info(`Graph: ${graph.order} nodes, ${graph.size} edges`);

  const clustering = createClustering();

  // Benchmark community detection
  const startDetect = performance.now();
  const communities = clustering.detectCommunities(graph);
  const detectTime = performance.now() - startDetect;

  // Benchmark cluster graph creation
  const startCluster = performance.now();
  const result = clustering.createClusterGraph(graph, communities);
  const clusterTime = performance.now() - startCluster;

  logger.info('Performance:');
  logger.info(`- Community detection: ${detectTime.toFixed(0)}ms`);
  logger.info(`- Cluster graph creation: ${clusterTime.toFixed(0)}ms`);
  logger.info(`- Total: ${(detectTime + clusterTime).toFixed(0)}ms`);
  logger.info('');
  logger.info('Results:');
  logger.info(`- Communities detected: ${result.communityCount}`);
  logger.info(`- Edge reduction: ${result.reductionRatio.toFixed(1)}%`);
  logger.info(`- Original edges: ${graph.size}`);
  logger.info(`- Clustered edges: ${result.edges.length}`);

  return result;
}
