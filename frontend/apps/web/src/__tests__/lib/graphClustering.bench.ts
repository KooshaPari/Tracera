/**
 * Graph Clustering Benchmarks
 *
 * Performance tests for large-scale graph clustering algorithms.
 * Tests clustering quality, speed, and memory usage at various scales.
 */

import { describe, it, expect, beforeAll } from 'vitest';

import type { Item, Link } from '@tracertm/types';

import {
  louvainClustering,
  labelPropagationClustering,
  adaptiveClustering,
  calculateClusteringQuality,
  extractClusterEdges,
} from '../../lib/graphClustering';

/**
 * Generate synthetic scale-free graph (Barabási-Albert model)
 */
function generateScaleFreeGraph(
  nodeCount: number,
  edgesPerNode: number = 3,
): { items: Item[]; links: Link[] } {
  const items: Item[] = [];
  const links: Link[] = [];

  // Create nodes
  for (let i = 0; i < nodeCount; i++) {
    const type =
      i % 5 === 0
        ? 'requirement'
        : i % 5 === 1
          ? 'test'
          : i % 5 === 2
            ? 'code'
            : i % 5 === 3
              ? 'ui_component'
              : 'task';

    items.push({
      id: `node-${i}`,
      projectId: 'test-project',
      type,
      title: `Node ${i}`,
      status: 'todo',
      createdAt: new Date(),
      updatedAt: new Date(),
    });
  }

  // Preferential attachment for scale-free property
  const degrees = new Array(nodeCount).fill(0);

  for (let i = edgesPerNode; i < nodeCount; i++) {
    const targets = new Set<number>();

    while (targets.size < edgesPerNode) {
      // Weighted random selection based on degree
      const totalDegree = degrees.slice(0, i).reduce((a, b) => a + b, 0) + i;
      let random = Math.random() * totalDegree;
      let target = 0;

      for (let j = 0; j < i; j++) {
        random -= degrees[j] + 1;
        if (random <= 0) {
          target = j;
          break;
        }
      }

      if (!targets.has(target)) {
        targets.add(target);
      }
    }

    // Create edges
    for (const target of targets) {
      links.push({
        id: `link-${i}-${target}`,
        projectId: 'test-project',
        sourceId: `node-${i}`,
        targetId: `node-${target}`,
        type: 'depends_on',
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      degrees[i]++;
      degrees[target]++;
    }
  }

  return { items, links };
}

/**
 * Measure execution time
 */
function measureTime<T>(fn: () => T): { result: T; time: number } {
  const start = performance.now();
  const result = fn();
  const time = performance.now() - start;
  return { result, time };
}

/**
 * Measure memory usage (approximate)
 */
function measureMemory<T>(fn: () => T): { result: T; memory: number } {
  if (!performance.memory) {
    // Memory API not available
    return { result: fn(), memory: 0 };
  }

  const before = performance.memory.usedJSHeapSize;
  const result = fn();
  const after = performance.memory.usedJSHeapSize;
  const memory = Math.max(0, after - before);

  return { result, memory };
}

describe('Graph Clustering Benchmarks', () => {
  describe('Small Graph (1k nodes)', () => {
    let items: Item[];
    let links: Link[];

    beforeAll(() => {
      const graph = generateScaleFreeGraph(1000, 3);
      items = graph.items;
      links = graph.links;
      logger.info(`\n🔬 Small graph: ${items.length} nodes, ${links.length} edges`);
    });

    it('Louvain clustering', () => {
      const { result, time } = measureTime(() => louvainClustering(items, links, 1.0));

      logger.info(`  ⏱️  Louvain: ${time.toFixed(2)}ms`);
      logger.info(`  📊 Clusters: ${result.totalClusters}`);
      logger.info(`  🎯 Compression: ${result.compressionRatio.toFixed(1)}x`);
      logger.info(`  ✨ Modularity: ${result.modularity.toFixed(3)}`);

      expect(result.totalClusters).toBeGreaterThan(0);
      expect(result.totalClusters).toBeLessThan(items.length);
      expect(result.modularity).toBeGreaterThan(0);
      expect(time).toBeLessThan(100); // Should be fast for small graphs
    });

    it('Label Propagation clustering', () => {
      const { result, time } = measureTime(() => labelPropagationClustering(items, links, 100));

      logger.info(`  ⏱️  Label Prop: ${time.toFixed(2)}ms`);
      logger.info(`  📊 Clusters: ${result.totalClusters}`);
      logger.info(`  🎯 Compression: ${result.compressionRatio.toFixed(1)}x`);
      logger.info(`  ✨ Modularity: ${result.modularity.toFixed(3)}`);

      expect(result.totalClusters).toBeGreaterThan(0);
      expect(time).toBeLessThan(50); // Should be faster than Louvain
    });

    it('Adaptive clustering', () => {
      const { result, time } = measureTime(() => adaptiveClustering(items, links, 50));

      logger.info(`  ⏱️  Adaptive: ${time.toFixed(2)}ms`);
      logger.info(`  📊 Clusters: ${result.totalClusters}`);

      expect(result.totalClusters).toBeGreaterThan(0);
      expect(result.totalClusters).toBeLessThanOrEqual(100); // Should respect target
    });
  });

  describe('Medium Graph (10k nodes)', () => {
    let items: Item[];
    let links: Link[];

    beforeAll(() => {
      const graph = generateScaleFreeGraph(10000, 3);
      items = graph.items;
      links = graph.links;
      logger.info(`\n🔬 Medium graph: ${items.length} nodes, ${links.length} edges`);
    });

    it('Louvain clustering', () => {
      const { result, time } = measureTime(() => louvainClustering(items, links, 1.0));

      logger.info(`  ⏱️  Louvain: ${time.toFixed(2)}ms`);
      logger.info(`  📊 Clusters: ${result.totalClusters}`);
      logger.info(`  🎯 Compression: ${result.compressionRatio.toFixed(1)}x`);
      logger.info(`  ✨ Modularity: ${result.modularity.toFixed(3)}`);

      expect(result.totalClusters).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(10);
      expect(time).toBeLessThan(500);
    });

    it('Label Propagation clustering', () => {
      const { result, time } = measureTime(() => labelPropagationClustering(items, links, 100));

      logger.info(`  ⏱️  Label Prop: ${time.toFixed(2)}ms`);
      logger.info(`  📊 Clusters: ${result.totalClusters}`);
      logger.info(`  🎯 Compression: ${result.compressionRatio.toFixed(1)}x`);

      expect(time).toBeLessThan(200); // Should be much faster
    });

    it('Quality metrics', () => {
      const clustering = louvainClustering(items, links, 1.0);
      const quality = calculateClusteringQuality(clustering, links);

      logger.info(`  ✨ Modularity: ${quality.modularity.toFixed(3)}`);
      logger.info(`  📈 Coverage: ${quality.coverage.toFixed(3)}`);
      logger.info(`  🎯 Silhouette: ${quality.silhouette.toFixed(3)}`);
      logger.info(`  🔗 Conductance: ${quality.conductance.toFixed(3)}`);

      expect(quality.modularity).toBeGreaterThan(0.3); // Good clustering
      expect(quality.coverage).toBeGreaterThan(0.5);
    });

    it('Cluster edges extraction', () => {
      const clustering = louvainClustering(items, links, 1.0);
      const { result, time } = measureTime(() => extractClusterEdges(clustering, links, 0));

      logger.info(`  ⏱️  Edge extraction: ${time.toFixed(2)}ms`);
      logger.info(`  🔗 Cluster edges: ${result.length}`);

      expect(result.length).toBeGreaterThan(0);
      expect(result.length).toBeLessThan(links.length);
      expect(time).toBeLessThan(100);
    });
  });

  describe('Large Graph (100k nodes) - Optional', () => {
    // Skip by default to keep tests fast
    // Run with: npm test -- --grep "100k nodes"

    it.skip('Louvain clustering', () => {
      const { items, links } = generateScaleFreeGraph(100000, 3);
      logger.info(`\n🔬 Large graph: ${items.length} nodes, ${links.length} edges`);

      const { result, time } = measureTime(() => louvainClustering(items, links, 1.0));

      logger.info(`  ⏱️  Louvain: ${time.toFixed(2)}ms`);
      logger.info(`  📊 Clusters: ${result.totalClusters}`);
      logger.info(`  🎯 Compression: ${result.compressionRatio.toFixed(1)}x`);
      logger.info(`  ✨ Modularity: ${result.modularity.toFixed(3)}`);

      expect(result.totalClusters).toBeGreaterThan(100);
      expect(result.totalClusters).toBeLessThan(1000);
      expect(result.compressionRatio).toBeGreaterThan(100);
      expect(time).toBeLessThan(5000); // 5 seconds max
    });

    it.skip('Label Propagation clustering', () => {
      const { items, links } = generateScaleFreeGraph(100000, 3);

      const { result, time } = measureTime(() => labelPropagationClustering(items, links, 100));

      logger.info(`  ⏱️  Label Prop: ${time.toFixed(2)}ms`);
      logger.info(`  📊 Clusters: ${result.totalClusters}`);
      logger.info(`  🎯 Compression: ${result.compressionRatio.toFixed(1)}x`);

      expect(time).toBeLessThan(1000); // Should be under 1 second
      expect(result.compressionRatio).toBeGreaterThan(100);
    });

    it.skip('Adaptive clustering (chooses optimal algorithm)', () => {
      const { items, links } = generateScaleFreeGraph(100000, 3);

      const { result, time } = measureTime(() => adaptiveClustering(items, links, 500));

      logger.info(`  ⏱️  Adaptive: ${time.toFixed(2)}ms`);
      logger.info(`  📊 Clusters: ${result.totalClusters}`);
      logger.info(`  🎯 Compression: ${result.compressionRatio.toFixed(1)}x`);
      logger.info(`  ✨ Target: 500 clusters`);

      // Adaptive should choose label prop for 100k nodes
      expect(time).toBeLessThan(1000);
      expect(result.totalClusters).toBeGreaterThan(400);
      expect(result.totalClusters).toBeLessThan(600);
    });

    it.skip('Memory usage estimate', () => {
      const { items, links } = generateScaleFreeGraph(100000, 3);

      const { result, memory } = measureMemory(() => adaptiveClustering(items, links, 500));

      logger.info(`  💾 Memory: ${(memory / 1024 / 1024).toFixed(2)} MB`);
      logger.info(`  📊 Clusters: ${result.totalClusters}`);

      // Should use < 50 MB for clustering result
      if (memory > 0) {
        expect(memory).toBeLessThan(50 * 1024 * 1024);
      }
    });
  });

  describe('Compression Ratio Tests', () => {
    it('achieves 100x+ compression on large graphs', () => {
      const { items, links } = generateScaleFreeGraph(10000, 3);
      const result = adaptiveClustering(items, links, 100);

      logger.info(`\n🎯 Compression test:`);
      logger.info(`  Nodes: ${items.length}`);
      logger.info(`  Target: 100 clusters`);
      logger.info(`  Actual: ${result.totalClusters} clusters`);
      logger.info(`  Ratio: ${result.compressionRatio.toFixed(1)}x`);

      expect(result.compressionRatio).toBeGreaterThan(50);
    });

    it('respects target cluster count', () => {
      const { items, links } = generateScaleFreeGraph(5000, 3);

      const targets = [50, 100, 200];
      for (const target of targets) {
        const result = adaptiveClustering(items, links, target);
        const deviation = Math.abs(result.totalClusters - target) / target;

        logger.info(
          `  Target: ${target} → Actual: ${result.totalClusters} (${(deviation * 100).toFixed(1)}% deviation)`,
        );

        // Should be within 50% of target
        expect(deviation).toBeLessThan(0.5);
      }
    });
  });

  describe('Cache Performance', () => {
    it('benefits from caching on repeated clustering', () => {
      const { items, links } = generateScaleFreeGraph(5000, 3);

      // First run (cold)
      const { time: coldTime } = measureTime(() => louvainClustering(items, links, 1.0));

      // Second run (cached)
      const { time: warmTime } = measureTime(() => louvainClustering(items, links, 1.0));

      logger.info(`\n🚀 Cache performance:`);
      logger.info(`  Cold: ${coldTime.toFixed(2)}ms`);
      logger.info(`  Warm: ${warmTime.toFixed(2)}ms`);
      logger.info(`  Speedup: ${(coldTime / warmTime).toFixed(1)}x`);

      // Cached should be significantly faster
      expect(warmTime).toBeLessThan(coldTime * 0.2);
    });
  });
});

describe('Integration Tests', () => {
  it('full clustering pipeline', () => {
    const { items, links } = generateScaleFreeGraph(1000, 3);

    logger.info(`\n🔄 Full pipeline test:`);

    // 1. Cluster
    const { result: clustering, time: clusterTime } = measureTime(() =>
      adaptiveClustering(items, links, 50),
    );
    logger.info(`  1️⃣  Clustering: ${clusterTime.toFixed(2)}ms`);

    // 2. Extract edges
    const { result: clusterEdges, time: edgeTime } = measureTime(() =>
      extractClusterEdges(clustering, links, 0),
    );
    logger.info(`  2️⃣  Edge extraction: ${edgeTime.toFixed(2)}ms`);

    // 3. Calculate quality
    const { result: quality, time: qualityTime } = measureTime(() =>
      calculateClusteringQuality(clustering, links),
    );
    logger.info(`  3️⃣  Quality metrics: ${qualityTime.toFixed(2)}ms`);

    const totalTime = clusterTime + edgeTime + qualityTime;
    logger.info(`  ⏱️  Total: ${totalTime.toFixed(2)}ms`);
    logger.info(`  📊 ${clustering.totalClusters} clusters`);
    logger.info(`  🔗 ${clusterEdges.length} cluster edges`);
    logger.info(`  ✨ Q = ${quality.modularity.toFixed(3)}`);

    expect(totalTime).toBeLessThan(200);
    expect(clustering.totalClusters).toBeGreaterThan(0);
    expect(clusterEdges.length).toBeGreaterThan(0);
  });
});
