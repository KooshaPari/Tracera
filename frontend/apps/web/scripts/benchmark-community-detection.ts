#!/usr/bin/env bun

/**
 * Performance Benchmark for Louvain Community Detection
 *
 * Tests community detection performance across various graph sizes
 * to ensure <2s requirement for 10k nodes is met.
 */

import { detectCommunities, clearClusteringCache } from '../src/lib/graph/clustering';
import type { Item, Link } from '../src/api/types';

interface BenchmarkResult {
  nodeCount: number;
  edgeCount: number;
  clusteringTimeMs: number;
  communityCount: number;
  avgCommunitySize: number;
  modularity?: number;
}

/**
 * Generate a random graph for testing
 */
function generateGraph(nodeCount: number, avgDegree: number): { items: Item[]; links: Link[] } {
  const items: Item[] = Array.from({ length: nodeCount }, (_, i) => ({
    id: `node${i}`,
    title: `Node ${i}`,
    item_type: 'requirement',
    status: 'todo',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }));

  const links: Link[] = [];
  const edgeCount = Math.floor((nodeCount * avgDegree) / 2);

  // Create preferential attachment (scale-free network)
  for (let i = 0; i < edgeCount; i++) {
    let source = Math.floor(Math.random() * nodeCount);
    let target = Math.floor(Math.random() * nodeCount);

    // Avoid self-loops
    if (source === target) {
      target = (target + 1) % nodeCount;
    }

    links.push({
      id: `link${i}`,
      source_id: `node${source}`,
      target_id: `node${target}`,
      link_type: 'depends_on',
      created_at: new Date().toISOString(),
    });
  }

  return { items, links };
}

/**
 * Run benchmark for a specific graph size
 */
async function runBenchmark(nodeCount: number, avgDegree: number): Promise<BenchmarkResult> {
  console.log(`\n📊 Benchmarking ${nodeCount} nodes...`);

  const { items, links } = generateGraph(nodeCount, avgDegree);

  console.log(`  Generated graph: ${items.length} nodes, ${links.length} edges`);

  // Clear cache to ensure fresh run
  clearClusteringCache();

  // Run community detection
  const result = await detectCommunities(items, links, {
    useCache: false,
  });

  console.log(`  ✅ Completed in ${result.performance.clusteringTimeMs.toFixed(2)}ms`);
  console.log(`  Communities: ${result.stats.communityCount}`);
  console.log(`  Avg community size: ${result.stats.avgCommunitySize.toFixed(2)}`);
  if (result.stats.modularity !== undefined) {
    console.log(`  Modularity: ${result.stats.modularity.toFixed(4)}`);
  }

  return {
    nodeCount,
    edgeCount: links.length,
    clusteringTimeMs: result.performance.clusteringTimeMs,
    communityCount: result.stats.communityCount,
    avgCommunitySize: result.stats.avgCommunitySize,
    modularity: result.stats.modularity,
  };
}

/**
 * Format time in appropriate units
 */
function formatTime(ms: number): string {
  if (ms < 1000) {
    return `${ms.toFixed(2)}ms`;
  }
  return `${(ms / 1000).toFixed(2)}s`;
}

/**
 * Main benchmark runner
 */
async function main() {
  console.log('🚀 Louvain Community Detection Performance Benchmark\n');
  console.log('Target: <2s for 10,000 nodes\n');
  console.log('=' .repeat(70));

  const benchmarks: BenchmarkResult[] = [];

  // Test configurations
  const configs = [
    { nodes: 100, avgDegree: 4 },
    { nodes: 500, avgDegree: 6 },
    { nodes: 1000, avgDegree: 8 },
    { nodes: 2500, avgDegree: 8 },
    { nodes: 5000, avgDegree: 10 },
    { nodes: 10000, avgDegree: 10 },
    { nodes: 20000, avgDegree: 12 },
  ];

  for (const config of configs) {
    try {
      const result = await runBenchmark(config.nodes, config.avgDegree);
      benchmarks.push(result);

      // Check if 10k node requirement is met
      if (config.nodes === 10000) {
        const passed = result.clusteringTimeMs < 2000;
        console.log(`\n  ${passed ? '✅ PASSED' : '❌ FAILED'}: 10k nodes requirement`);
        if (passed) {
          const margin = 2000 - result.clusteringTimeMs;
          console.log(`  Completed with ${formatTime(margin)} to spare`);
        }
      }
    } catch (error) {
      console.error(`❌ Benchmark failed for ${config.nodes} nodes:`, error);
    }
  }

  // Print summary table
  console.log('\n' + '='.repeat(70));
  console.log('\n📈 Benchmark Summary\n');
  console.log('┌─────────────┬─────────────┬──────────────┬──────────────┬────────────┐');
  console.log('│ Nodes       │ Edges       │ Time         │ Communities  │ Modularity │');
  console.log('├─────────────┼─────────────┼──────────────┼──────────────┼────────────┤');

  for (const result of benchmarks) {
    const nodes = result.nodeCount.toString().padStart(11);
    const edges = result.edgeCount.toString().padStart(11);
    const time = formatTime(result.clusteringTimeMs).padStart(12);
    const communities = result.communityCount.toString().padStart(12);
    const modularity = result.modularity !== undefined
      ? result.modularity.toFixed(4).padStart(10)
      : 'N/A'.padStart(10);

    console.log(`│ ${nodes} │ ${edges} │ ${time} │ ${communities} │ ${modularity} │`);

    // Highlight 10k row
    if (result.nodeCount === 10000) {
      const passed = result.clusteringTimeMs < 2000;
      const status = passed ? '✅ PASSED' : '❌ FAILED';
      console.log(`│ ${status.padStart(11)} │${' '.repeat(11)}│${' '.repeat(14)}│${' '.repeat(14)}│${' '.repeat(12)}│`);
    }
  }

  console.log('└─────────────┴─────────────┴──────────────┴──────────────┴────────────┘');

  // Performance analysis
  console.log('\n📊 Performance Analysis\n');

  const tenKResult = benchmarks.find(b => b.nodeCount === 10000);
  if (tenKResult) {
    const throughput = (tenKResult.nodeCount / tenKResult.clusteringTimeMs) * 1000;
    console.log(`Throughput at 10k nodes: ${throughput.toFixed(0)} nodes/second`);

    if (tenKResult.clusteringTimeMs < 2000) {
      const percentOfTarget = (tenKResult.clusteringTimeMs / 2000) * 100;
      console.log(`Performance: ${percentOfTarget.toFixed(1)}% of target time`);
    }
  }

  // Estimate scaling
  if (benchmarks.length >= 3) {
    const last = benchmarks[benchmarks.length - 1];
    const estimate50k = (last.clusteringTimeMs / last.nodeCount) * 50000;
    console.log(`\nEstimated time for 50k nodes: ${formatTime(estimate50k)}`);
  }

  console.log('\n✅ Benchmark complete\n');
}

// Run benchmarks
main().catch(error => {
  console.error('Benchmark failed:', error);
  process.exit(1);
});
