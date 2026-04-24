#!/usr/bin/env bun

/**
 * Performance Benchmark for Louvain Community Detection
 *
 * Tests community detection performance across various graph sizes
 * to ensure <2s requirement for 10k nodes is met.
 */

import type { Item, Link } from '../src/api/types';

import { clearClusteringCache, detectCommunities } from '../src/lib/graph/clustering';

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
    created_at: new Date().toISOString(),
    id: `node${i}`,
    item_type: 'requirement',
    status: 'todo',
    title: `Node ${i}`,
    updated_at: new Date().toISOString(),
  }));

  const links: Link[] = [];
  const edgeCount = Math.floor((nodeCount * avgDegree) / 2);

  // Create preferential attachment (scale-free network)
  for (let i = 0; i < edgeCount; i += 1) {
    let source = Math.floor(Math.random() * nodeCount);
    let target = Math.floor(Math.random() * nodeCount);

    // Avoid self-loops
    if (source === target) {
      target = (target + 1) % nodeCount;
    }

    links.push({
      created_at: new Date().toISOString(),
      id: `link${i}`,
      link_type: 'depends_on',
      source_id: `node${source}`,
      target_id: `node${target}`,
    });
  }

  return { items, links };
}

/**
 * Run benchmark for a specific graph size
 */
async function runBenchmark(nodeCount: number, avgDegree: number): Promise<BenchmarkResult> {
  const { items, links } = generateGraph(nodeCount, avgDegree);

  // Clear cache to ensure fresh run
  clearClusteringCache();

  // Run community detection
  const result = await detectCommunities(items, links, {
    useCache: false,
  });

  if (result.stats.modularity !== undefined) {
  }

  return {
    avgCommunitySize: result.stats.avgCommunitySize,
    clusteringTimeMs: result.performance.clusteringTimeMs,
    communityCount: result.stats.communityCount,
    edgeCount: links.length,
    modularity: result.stats.modularity,
    nodeCount,
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
  const benchmarks: BenchmarkResult[] = [];

  // Test configurations
  const configs = [
    { avgDegree: 4, nodes: 100 },
    { avgDegree: 6, nodes: 500 },
    { avgDegree: 8, nodes: 1000 },
    { avgDegree: 8, nodes: 2500 },
    { avgDegree: 10, nodes: 5000 },
    { avgDegree: 10, nodes: 10_000 },
    { avgDegree: 12, nodes: 20_000 },
  ];

  for (const config of configs) {
    try {
      const result = await runBenchmark(config.nodes, config.avgDegree);
      benchmarks.push(result);

      // Check if 10k node requirement is met
      if (config.nodes === 10_000) {
        const passed = result.clusteringTimeMs < 2000;

        if (passed) {
          const margin = 2000 - result.clusteringTimeMs;
        }
      }
    } catch {}
  }

  // Print summary table

  for (const result of benchmarks) {
    const nodes = result.nodeCount.toString().padStart(11);
    const edges = result.edgeCount.toString().padStart(11);
    const time = formatTime(result.clusteringTimeMs).padStart(12);
    const communities = result.communityCount.toString().padStart(12);
    const modularity =
      result.modularity !== undefined
        ? result.modularity.toFixed(4).padStart(10)
        : 'N/A'.padStart(10);

    // Highlight 10k row
    if (result.nodeCount === 10_000) {
      const passed = result.clusteringTimeMs < 2000;
      const status = passed ? '✅ PASSED' : '❌ FAILED';
    }
  }

  // Performance analysis

  const tenKResult = benchmarks.find((b) => b.nodeCount === 10_000);
  if (tenKResult) {
    const throughput = (tenKResult.nodeCount / tenKResult.clusteringTimeMs) * 1000;

    if (tenKResult.clusteringTimeMs < 2000) {
      const percentOfTarget = (tenKResult.clusteringTimeMs / 2000) * 100;
    }
  }

  // Estimate scaling
  if (benchmarks.length >= 3) {
    const last = benchmarks.at(-1);
    const estimate50k = (last.clusteringTimeMs / last.nodeCount) * 50_000;
  }
}

// Run benchmarks
main().catch((error) => {
  process.exit(1);
});
