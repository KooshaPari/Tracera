/**
 * Benchmark Tests for R-tree Spatial Index
 *
 * Validates O(log n) performance claims and compares against O(n) linear search.
 *
 * Run with: bun test spatialIndex.benchmark.test.ts
 */

import { describe, expect, test } from 'bun:test';

import {
  RBushSpatialIndex,
  benchmarkSpatialIndex,
  createSpatialIndex,
  type Edge,
  type NodePosition,
  type ViewportBounds,
} from '../spatialIndex';

/**
 * Generate synthetic graph data for benchmarking
 */
function generateGraphData(numEdges: number): {
  edges: Edge[];
  nodePositions: Map<string, NodePosition>;
} {
  const nodes = new Map<string, NodePosition>();
  const edges: Edge[] = [];

  // Create nodes in a grid pattern
  const gridSize = Math.ceil(Math.sqrt(numEdges * 2)); // ~2 nodes per edge
  for (let i = 0; i < gridSize; i++) {
    for (let j = 0; j < gridSize; j++) {
      const nodeId = `node-${i}-${j}`;
      nodes.set(nodeId, {
        x: i * 100,
        y: j * 100,
      });
    }
  }

  // Create edges between adjacent nodes
  const nodeIds = Array.from(nodes.keys());
  for (let i = 0; i < Math.min(numEdges, nodeIds.length - 1); i++) {
    edges.push({
      id: `edge-${i}`,
      source: nodeIds[i],
      target: nodeIds[i + 1],
    });
  }

  return { edges, nodePositions: nodes };
}

/**
 * Linear search baseline (O(n))
 */
function linearSearchViewport(
  edges: Edge[],
  nodePositions: Map<string, NodePosition>,
  viewportBounds: ViewportBounds,
  padding: number = 100,
): Edge[] {
  const searchBounds = {
    minX: viewportBounds.minX - padding,
    maxX: viewportBounds.maxX + padding,
    minY: viewportBounds.minY - padding,
    maxY: viewportBounds.maxY + padding,
  };

  return edges.filter((edge) => {
    const sourcePos = nodePositions.get(edge.source);
    const targetPos = nodePositions.get(edge.target);
    if (!sourcePos || !targetPos) return false;

    const edgeBounds = {
      minX: Math.min(sourcePos.x, targetPos.x),
      maxX: Math.max(sourcePos.x, targetPos.x),
      minY: Math.min(sourcePos.y, targetPos.y),
      maxY: Math.max(sourcePos.y, targetPos.y),
    };

    return !(
      edgeBounds.maxX < searchBounds.minX ||
      edgeBounds.minX > searchBounds.maxX ||
      edgeBounds.maxY < searchBounds.minY ||
      edgeBounds.minY > searchBounds.maxY
    );
  });
}

describe('R-tree Spatial Index Benchmarks', () => {
  test('Small graph (1k edges) - baseline performance', () => {
    const { edges, nodePositions } = generateGraphData(1000);
    const viewport: ViewportBounds = {
      minX: 0,
      minY: 0,
      maxX: 500,
      maxY: 500,
    };

    const result = benchmarkSpatialIndex(edges, nodePositions, viewport);

    logger.info('\n📊 1k edges:');
    logger.info(`  Linear:  ${result.linearSearchMs.toFixed(3)}ms`);
    logger.info(
      `  R-tree:  ${result.rtreeSearchMs.toFixed(3)}ms (build: ${result.rtreeBuildMs.toFixed(3)}ms)`,
    );
    logger.info(`  Speedup: ${result.speedup.toFixed(2)}x`);

    expect(result.resultsMatch).toBe(true);
    expect(result.speedup).toBeGreaterThan(1);
  });

  test('Medium graph (10k edges) - noticeable speedup', () => {
    const { edges, nodePositions } = generateGraphData(10000);
    const viewport: ViewportBounds = {
      minX: 0,
      minY: 0,
      maxX: 500,
      maxY: 500,
    };

    const result = benchmarkSpatialIndex(edges, nodePositions, viewport);

    logger.info('\n📊 10k edges:');
    logger.info(`  Linear:  ${result.linearSearchMs.toFixed(3)}ms`);
    logger.info(
      `  R-tree:  ${result.rtreeSearchMs.toFixed(3)}ms (build: ${result.rtreeBuildMs.toFixed(3)}ms)`,
    );
    logger.info(`  Speedup: ${result.speedup.toFixed(2)}x`);

    expect(result.resultsMatch).toBe(true);
    expect(result.speedup).toBeGreaterThan(2); // Should be >2x faster
  });

  test('Large graph (100k edges) - significant speedup', () => {
    const { edges, nodePositions } = generateGraphData(100000);
    const viewport: ViewportBounds = {
      minX: 0,
      minY: 0,
      maxX: 500,
      maxY: 500,
    };

    const result = benchmarkSpatialIndex(edges, nodePositions, viewport);

    logger.info('\n📊 100k edges:');
    logger.info(`  Linear:  ${result.linearSearchMs.toFixed(3)}ms`);
    logger.info(
      `  R-tree:  ${result.rtreeSearchMs.toFixed(3)}ms (build: ${result.rtreeBuildMs.toFixed(3)}ms)`,
    );
    logger.info(`  Speedup: ${result.speedup.toFixed(2)}x`);

    expect(result.resultsMatch).toBe(true);
    expect(result.speedup).toBeGreaterThan(10); // Should be >10x faster
    expect(result.rtreeSearchMs).toBeLessThan(1); // Target: <1ms
  });

  test('Bulk loading vs incremental insertion', () => {
    const { edges, nodePositions } = generateGraphData(10000);

    // Bulk loading
    const bulkStart = performance.now();
    const bulkIndex = new RBushSpatialIndex();
    bulkIndex.bulkLoad(edges, nodePositions);
    const bulkLoadMs = performance.now() - bulkStart;

    // Incremental insertion
    const incrementalStart = performance.now();
    const incrementalIndex = new RBushSpatialIndex();
    for (const edge of edges) {
      incrementalIndex.insertEdge(edge, nodePositions);
    }
    const incrementalMs = performance.now() - incrementalStart;

    const speedup = incrementalMs / bulkLoadMs;

    logger.info('\n📊 Bulk vs Incremental (10k edges):');
    logger.info(`  Bulk:        ${bulkLoadMs.toFixed(3)}ms`);
    logger.info(`  Incremental: ${incrementalMs.toFixed(3)}ms`);
    logger.info(`  Speedup:     ${speedup.toFixed(2)}x`);

    expect(speedup).toBeGreaterThan(3); // Bulk should be >3x faster
  });

  test('Memory usage scaling', () => {
    const testSizes = [1000, 10000, 50000, 100000];

    logger.info('\n📊 Memory Usage Scaling:');
    for (const size of testSizes) {
      const { edges, nodePositions } = generateGraphData(size);
      const index = createSpatialIndex(edges, nodePositions);
      const stats = index.getStats();

      logger.info(
        `  ${size.toLocaleString()} edges: ${stats.memoryEstimate} (depth: ${stats.treeDepth})`,
      );

      // Verify memory estimate is reasonable
      // ~24 bytes per edge * 1.3 overhead
      const expectedBytes = size * 24 * 1.3;
      const actualBytes = stats.memoryEstimate.includes('KB')
        ? Number.parseFloat(stats.memoryEstimate) * 1024
        : Number.parseFloat(stats.memoryEstimate) * 1024 * 1024;

      expect(actualBytes).toBeGreaterThan(expectedBytes * 0.5);
      expect(actualBytes).toBeLessThan(expectedBytes * 2);
    }
  });

  test('Query performance consistency', () => {
    const { edges, nodePositions } = generateGraphData(100000);
    const index = createSpatialIndex(edges, nodePositions);

    const viewports: ViewportBounds[] = [
      { minX: 0, minY: 0, maxX: 500, maxY: 500 },
      { minX: 1000, minY: 1000, maxX: 1500, maxY: 1500 },
      { minX: 5000, minY: 5000, maxX: 5500, maxY: 5500 },
    ];

    logger.info('\n📊 Query Performance (100k edges):');
    for (let i = 0; i < viewports.length; i++) {
      const start = performance.now();
      const results = index.searchViewport(viewports[i], 100);
      const queryMs = performance.now() - start;

      logger.info(`  Viewport ${i + 1}: ${queryMs.toFixed(3)}ms (${results.length} results)`);

      // All queries should be fast (<10ms is excellent for 100k edges)
      expect(queryMs).toBeLessThan(10);
    }
  });

  test('Correctness: R-tree matches linear search', () => {
    const { edges, nodePositions } = generateGraphData(10000);
    const viewport: ViewportBounds = {
      minX: 0,
      minY: 0,
      maxX: 500,
      maxY: 500,
    };

    // Linear search (ground truth)
    const linearResults = linearSearchViewport(edges, nodePositions, viewport, 100);

    // R-tree search
    const index = createSpatialIndex(edges, nodePositions);
    const rtreeResults = index.searchViewport(viewport, 100);

    // Compare results
    const linearIds = new Set(linearResults.map((e) => e.id));
    const rtreeIds = new Set(rtreeResults.map((e) => e.id));

    // Should have same count
    expect(rtreeIds.size).toBe(linearIds.size);

    // Should have same IDs
    for (const id of linearIds) {
      expect(rtreeIds.has(id)).toBe(true);
    }

    logger.info(`\n✅ Correctness verified: ${linearIds.size} edges matched`);
  });

  test('Incremental updates maintain correctness', () => {
    const { edges, nodePositions } = generateGraphData(1000);
    const index = createSpatialIndex(edges, nodePositions);

    // Add new edge
    const newEdge: Edge = {
      id: 'new-edge',
      source: 'node-0-0',
      target: 'node-1-1',
    };
    const inserted = index.insertEdge(newEdge, nodePositions);
    expect(inserted).toBe(true);
    expect(index.size()).toBe(edges.length + 1);

    // Remove edge
    const removed = index.removeEdge('edge-0');
    expect(removed).toBe(true);
    expect(index.size()).toBe(edges.length);

    // Verify query still works
    const viewport: ViewportBounds = {
      minX: 0,
      minY: 0,
      maxX: 200,
      maxY: 200,
    };
    const results = index.searchViewport(viewport, 100);
    expect(results.length).toBeGreaterThan(0);

    logger.info('\n✅ Incremental updates verified');
  });
});
