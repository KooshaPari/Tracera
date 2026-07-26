/**
 * Edge Rendering Benchmark Utility
 * Tests edge aggregation and rendering performance with large datasets
 */

import type { LinkType } from '@tracertm/types';

import { logger } from '@/lib/logger';

import {
  type EdgeBase,
  type EdgeSamplingConfig,
  type Node,
  applyLazyEdgeRendering,
  createDefaultFilterConfig,
  createDefaultSamplingConfig,
} from './edgeAggregation';

// ============================================================================
// Synthetic Data Generation
// ============================================================================

/**
 * Generate synthetic nodes for testing
 */
export function generateTestNodes(count: number): Node[] {
  const nodes: Node[] = [];
  const gridSize = Math.ceil(Math.sqrt(count));

  for (let i = 0; i < count; i++) {
    const row = Math.floor(i / gridSize);
    const col = i % gridSize;

    nodes.push({
      id: `node_${i}`,
      position: {
        x: col * 200 + Math.random() * 50,
        y: row * 200 + Math.random() * 50,
      },
    });
  }

  return nodes;
}

/**
 * Generate synthetic edges for testing
 */
export function generateTestEdges(
  nodeCount: number,
  edgeCount: number,
  distribution: 'random' | 'clustered' | 'parallel' = 'random',
): EdgeBase[] {
  const edges: EdgeBase[] = [];
  const linkTypes: LinkType[] = [
    'implements',
    'tests',
    'depends_on',
    'traces_to',
    'blocks',
    'related_to',
  ];

  switch (distribution) {
    case 'random':
      // Random connections
      for (let i = 0; i < edgeCount; i++) {
        const source = Math.floor(Math.random() * nodeCount);
        const target = Math.floor(Math.random() * nodeCount);
        if (source === target) continue;

        edges.push({
          id: `edge_${i}`,
          source: `node_${source}`,
          target: `node_${target}`,
          type: linkTypes[Math.floor(Math.random() * linkTypes.length)]!,
        });
      }
      break;

    case 'clustered':
      // Create dense clusters
      const clusterCount = Math.ceil(nodeCount / 50);
      for (let i = 0; i < edgeCount; i++) {
        const cluster = Math.floor(Math.random() * clusterCount);
        const clusterStart = cluster * 50;
        const clusterEnd = Math.min(clusterStart + 50, nodeCount);

        const source = clusterStart + Math.floor(Math.random() * (clusterEnd - clusterStart));
        const target = clusterStart + Math.floor(Math.random() * (clusterEnd - clusterStart));
        if (source === target) continue;

        edges.push({
          id: `edge_${i}`,
          source: `node_${source}`,
          target: `node_${target}`,
          type: linkTypes[Math.floor(Math.random() * linkTypes.length)]!,
        });
      }
      break;

    case 'parallel':
      // Create many parallel edges (same source→target)
      const pairCount = Math.floor(edgeCount / 20); // 20 edges per pair
      for (let i = 0; i < edgeCount; i++) {
        const pairIndex = i % pairCount;
        const source = Math.floor(pairIndex / Math.sqrt(pairCount));
        const target = pairIndex % Math.ceil(Math.sqrt(pairCount));

        edges.push({
          id: `edge_${i}`,
          source: `node_${source}`,
          target: `node_${target}`,
          type: linkTypes[i % linkTypes.length]!,
        });
      }
      break;
  }

  return edges;
}

// ============================================================================
// Benchmark Functions
// ============================================================================

export interface BenchmarkResult {
  name: string;
  totalEdges: number;
  visibleEdges: number;
  renderRatio: number;
  executionTime: number;
  aggregatedEdges: number;
  canvasClusters: number;
  memoryEstimate: number; // in MB
}

/**
 * Run a single benchmark test
 */
export function runEdgeBenchmark(
  name: string,
  edges: EdgeBase[],
  nodes: Node[],
  config?: EdgeSamplingConfig,
): BenchmarkResult {
  const actualConfig = config || createDefaultSamplingConfig(edges.length);
  const filterConfig = createDefaultFilterConfig();

  // Measure memory before
  const memBefore = (performance as any).memory?.usedJSHeapSize || 0;

  // Run benchmark
  const startTime = performance.now();

  const result = applyLazyEdgeRendering(edges, nodes, actualConfig, filterConfig);

  const endTime = performance.now();

  // Measure memory after
  const memAfter = (performance as any).memory?.usedJSHeapSize || 0;
  const memDelta = (memAfter - memBefore) / 1024 / 1024; // Convert to MB

  return {
    name,
    totalEdges: result.stats.totalEdges,
    visibleEdges: result.stats.sampledEdges,
    renderRatio: result.stats.renderRatio,
    executionTime: endTime - startTime,
    aggregatedEdges: result.stats.aggregatedEdges,
    canvasClusters: result.stats.canvasClusters,
    memoryEstimate: Math.max(0, memDelta),
  };
}

/**
 * Run comprehensive benchmark suite
 */
export function runBenchmarkSuite(): BenchmarkResult[] {
  const results: BenchmarkResult[] = [];

  // Test 1: Small graph (baseline)
  const nodes_1k = generateTestNodes(100);
  const edges_1k = generateTestEdges(100, 1000, 'random');
  results.push(runEdgeBenchmark('1K edges (random)', edges_1k, nodes_1k));

  // Test 2: Medium graph
  const nodes_10k = generateTestNodes(500);
  const edges_10k = generateTestEdges(500, 10000, 'random');
  results.push(runEdgeBenchmark('10K edges (random)', edges_10k, nodes_10k));

  // Test 3: Large graph
  const nodes_100k = generateTestNodes(1000);
  const edges_100k = generateTestEdges(1000, 100000, 'random');
  results.push(runEdgeBenchmark('100K edges (random)', edges_100k, nodes_100k));

  // Test 4: 1M edges (target)
  const nodes_1m = generateTestNodes(2000);
  const edges_1m = generateTestEdges(2000, 1000000, 'random');
  results.push(runEdgeBenchmark('1M edges (random)', edges_1m, nodes_1m));

  // Test 5: Clustered distribution
  const edges_100k_clustered = generateTestEdges(1000, 100000, 'clustered');
  results.push(runEdgeBenchmark('100K edges (clustered)', edges_100k_clustered, nodes_100k));

  // Test 6: Parallel edges
  const edges_100k_parallel = generateTestEdges(1000, 100000, 'parallel');
  results.push(runEdgeBenchmark('100K edges (parallel)', edges_100k_parallel, nodes_100k));

  return results;
}

/**
 * Format benchmark results as table
 */
export function formatBenchmarkResults(results: BenchmarkResult[]): string {
  const header = [
    'Test',
    'Total Edges',
    'Visible',
    'Ratio',
    'Time (ms)',
    'Aggregated',
    'Canvas',
    'Memory (MB)',
  ].join('\t');

  const rows = results.map((r) =>
    [
      r.name,
      r.totalEdges.toLocaleString(),
      r.visibleEdges,
      `${r.renderRatio.toFixed(2)}%`,
      r.executionTime.toFixed(2),
      r.aggregatedEdges,
      r.canvasClusters,
      r.memoryEstimate.toFixed(2),
    ].join('\t'),
  );

  return [header, ...rows].join('\n');
}

/**
 * Run benchmark and log to console
 */
export function runAndLogBenchmark(): void {
  logger.info('🚀 Starting Edge Rendering Benchmark Suite...\n');

  const results = runBenchmarkSuite();

  logger.info(formatBenchmarkResults(results));

  logger.info('\n📊 Summary:');
  const avgRenderRatio = results.reduce((sum, r) => sum + r.renderRatio, 0) / results.length;
  const avgExecutionTime = results.reduce((sum, r) => sum + r.executionTime, 0) / results.length;

  logger.info(`Average Render Ratio: ${avgRenderRatio.toFixed(2)}%`);
  logger.info(`Average Execution Time: ${avgExecutionTime.toFixed(2)}ms`);

  // Check if we hit the target for 1M edges
  const millionEdgeTest = results.find((r) => r.name.includes('1M edges'));
  if (millionEdgeTest) {
    const hitTarget = millionEdgeTest.visibleEdges <= 100;
    logger.info(`\n🎯 Target (1M → <100 edges): ${hitTarget ? '✅ ACHIEVED' : '❌ MISSED'}`);
    logger.info(`   Actual: ${millionEdgeTest.visibleEdges} visible edges`);
  }
}

// ============================================================================
// Interactive Benchmark (for dev console)
// ============================================================================

/**
 * Run custom benchmark with specified parameters
 */
export function runCustomBenchmark(
  nodeCount: number,
  edgeCount: number,
  distribution: 'random' | 'clustered' | 'parallel' = 'random',
  customConfig?: Partial<EdgeSamplingConfig>,
): BenchmarkResult {
  const nodes = generateTestNodes(nodeCount);
  const edges = generateTestEdges(nodeCount, edgeCount, distribution);

  const config = customConfig
    ? { ...createDefaultSamplingConfig(edgeCount), ...customConfig }
    : createDefaultSamplingConfig(edgeCount);

  return runEdgeBenchmark(`Custom: ${edgeCount} edges (${distribution})`, edges, nodes, config);
}

// Expose to window for dev console access
if (typeof window !== 'undefined') {
  (window as any).edgeBenchmark = {
    run: runAndLogBenchmark,
    runCustom: runCustomBenchmark,
    runSuite: runBenchmarkSuite,
  };
}
