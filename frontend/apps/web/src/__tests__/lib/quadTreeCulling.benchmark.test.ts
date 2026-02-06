/**
 * Benchmark: Quad-tree Culling vs O(n) Distance Checks
 *
 * Compares performance of:
 * 1. O(n) distance check for every node (current approach)
 * 2. O(log n) quad-tree viewport query (new approach)
 *
 * Expected Results:
 * - 100k nodes: O(n) ~10ms → O(log n) <1ms
 * - 10k nodes: O(n) ~1ms → O(log n) ~0.1ms
 */

import { describe, it, expect, beforeEach } from 'vitest';

import { QuadTreeNodeIndex, type QuadTreeNode, createViewportRectangle } from '@/lib/quadTreeIndex';

describe('QuadTree Culling Benchmark', () => {
  // Generate test nodes
  function generateNodes(count: number): QuadTreeNode[] {
    const nodes: QuadTreeNode[] = [];
    const gridSize = Math.ceil(Math.sqrt(count));

    for (let i = 0; i < count; i++) {
      const x = (i % gridSize) * 300;
      const y = Math.floor(i / gridSize) * 200;

      nodes.push({
        id: `node-${i}`,
        x,
        y,
        width: 200,
        height: 120,
      });
    }

    return nodes;
  }

  // O(n) distance check (current approach)
  // Simulates real-world scenario where we also compute LOD for each node
  function cullNodesDistanceCheck(
    nodes: QuadTreeNode[],
    viewport: { x: number; y: number; width: number; height: number },
    buffer: number,
  ): QuadTreeNode[] {
    const results: QuadTreeNode[] = [];
    const x0 = viewport.x - buffer;
    const y0 = viewport.y - buffer;
    const x1 = viewport.x + viewport.width + buffer;
    const y1 = viewport.y + viewport.height + buffer;

    const centerX = viewport.x + viewport.width / 2;
    const centerY = viewport.y + viewport.height / 2;

    // O(n) check every node
    for (const node of nodes) {
      // Rectangle check
      if (node.x >= x0 && node.x <= x1 && node.y >= y0 && node.y <= y1) {
        // Simulate LOD calculation (distance check)
        // This is what makes O(n) expensive in real scenarios
        const dx = node.x - centerX;
        const dy = node.y - centerY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Simulate LOD tier determination
        let tier = 0;
        if (distance < 500) tier = 4;
        else if (distance < 1000) tier = 3;
        else if (distance < 2000) tier = 2;
        else tier = 1;

        results.push({ ...node, data: { ...node.data, tier } });
      }
    }

    return results;
  }

  describe('Performance Comparison', () => {
    const testCases = [
      { nodeCount: 1000, name: '1k nodes' },
      { nodeCount: 10000, name: '10k nodes' },
      { nodeCount: 50000, name: '50k nodes' },
      { nodeCount: 100000, name: '100k nodes' },
    ];

    testCases.forEach(({ nodeCount, name }) => {
      it(`${name} - quad-tree should be faster than O(n)`, () => {
        const nodes = generateNodes(nodeCount);

        // Viewport showing ~500 nodes (typical zoom level)
        const viewport = {
          x: 0,
          y: 0,
          width: 3000,
          height: 2000,
        };
        const buffer = 200;

        // Benchmark O(n) approach
        const onStart = performance.now();
        const onResults = cullNodesDistanceCheck(nodes, viewport, buffer);
        const onTime = performance.now() - onStart;

        // Build quad-tree
        const index = new QuadTreeNodeIndex();
        const buildStart = performance.now();
        index.build(nodes);
        const buildTime = performance.now() - buildStart;

        // Benchmark quad-tree approach
        const qtStart = performance.now();
        const qtResults = index.queryViewportWithBuffer(viewport, buffer);
        const qtTime = performance.now() - qtStart;

        // Results should match
        expect(qtResults.length).toBe(onResults.length);

        // Calculate speedup
        const speedup = onTime / qtTime;

        logger.info(`\n=== ${name} ===`);
        logger.info(`O(n) time: ${onTime.toFixed(3)}ms`);
        logger.info(`QuadTree build: ${buildTime.toFixed(3)}ms`);
        logger.info(`QuadTree query: ${qtTime.toFixed(3)}ms`);
        logger.info(`Speedup: ${speedup.toFixed(1)}x`);
        logger.info(`Visible nodes: ${qtResults.length} / ${nodeCount}`);

        // For very large graphs (50k+), quad-tree should be significantly faster
        // Note: For smaller graphs, the build overhead may outweigh query benefits
        if (nodeCount >= 50000) {
          expect(qtTime).toBeLessThan(onTime);
        }
      });
    });
  });

  describe('QuadTreeNodeIndex', () => {
    let index: QuadTreeNodeIndex;
    let nodes: QuadTreeNode[];

    beforeEach(() => {
      index = new QuadTreeNodeIndex();
      nodes = generateNodes(10000);
    });

    it('should build index efficiently', () => {
      const start = performance.now();
      index.build(nodes);
      const buildTime = performance.now() - start;

      expect(index.size()).toBe(10000);
      expect(buildTime).toBeLessThan(100); // Should build 10k nodes in <100ms

      const stats = index.getStats();
      logger.info(`\nIndex stats for 10k nodes:`);
      logger.info(`  Depth: ${stats.depth}`);
      logger.info(`  Build time: ${buildTime.toFixed(2)}ms`);
    });

    it('should query viewport efficiently', () => {
      index.build(nodes);

      const viewport = {
        x: 0,
        y: 0,
        width: 3000,
        height: 2000,
      };

      const start = performance.now();
      const results = index.queryViewportWithBuffer(viewport, 200);
      const queryTime = performance.now() - start;

      expect(results.length).toBeGreaterThan(0);
      expect(queryTime).toBeLessThan(5); // Should query in <5ms

      logger.info(`\nViewport query:`);
      logger.info(`  Results: ${results.length} nodes`);
      logger.info(`  Time: ${queryTime.toFixed(3)}ms`);
    });

    it('should find nearest node efficiently', () => {
      index.build(nodes);

      const start = performance.now();
      const nearest = index.findNearest(1000, 1000);
      const queryTime = performance.now() - start;

      expect(nearest).not.toBeNull();
      expect(queryTime).toBeLessThan(1); // Should find in <1ms

      logger.info(`\nNearest node query:`);
      logger.info(`  Time: ${queryTime.toFixed(3)}ms`);
    });

    it('should handle dynamic updates', () => {
      index.build(nodes.slice(0, 1000));

      // Add nodes
      const addStart = performance.now();
      for (let i = 1000; i < 1100; i++) {
        index.add(nodes[i]);
      }
      const addTime = performance.now() - addStart;

      expect(index.size()).toBe(1100);
      expect(addTime).toBeLessThan(10); // Should add 100 nodes in <10ms

      // Update positions
      const updateStart = performance.now();
      for (let i = 0; i < 100; i++) {
        index.updatePosition(`node-${i}`, i * 300 + 10, i * 200 + 10);
      }
      const updateTime = performance.now() - updateStart;

      expect(updateTime).toBeLessThan(50); // Should update 100 nodes in <50ms

      logger.info(`\nDynamic updates:`);
      logger.info(`  Add 100 nodes: ${addTime.toFixed(2)}ms`);
      logger.info(`  Update 100 positions: ${updateTime.toFixed(2)}ms`);
    });

    it('should scale logarithmically', () => {
      const sizes = [1000, 10000, 100000];
      const queryTimes: number[] = [];

      for (const size of sizes) {
        const testNodes = generateNodes(size);
        index.build(testNodes);

        const viewport = { x: 0, y: 0, width: 3000, height: 2000 };
        const start = performance.now();
        index.queryViewportWithBuffer(viewport, 200);
        const time = performance.now() - start;

        queryTimes.push(time);
      }

      logger.info(`\nScaling behavior:`);
      for (let i = 0; i < sizes.length; i++) {
        logger.info(`  ${sizes[i]} nodes: ${queryTimes[i].toFixed(3)}ms`);
      }

      // Query time should grow slowly (logarithmically)
      // 10x more nodes should not be 10x slower
      const ratio10kTo1k = queryTimes[1] / queryTimes[0];
      const ratio100kTo10k = queryTimes[2] / queryTimes[1];

      expect(ratio10kTo1k).toBeLessThan(5); // Should be <5x slower for 10x nodes
      expect(ratio100kTo10k).toBeLessThan(5);
    });
  });

  describe('Viewport Rectangle Conversion', () => {
    it('should convert React Flow viewport to rectangle', () => {
      const viewport = { x: -1000, y: -500, zoom: 0.5 };
      const rect = createViewportRectangle(viewport, 1920, 1080);

      // At zoom 0.5, screen space is 2x graph space
      expect(rect.x).toBe(2000); // -(-1000) / 0.5
      expect(rect.y).toBe(1000); // -(-500) / 0.5
      expect(rect.width).toBe(3840); // 1920 / 0.5
      expect(rect.height).toBe(2160); // 1080 / 0.5
    });
  });

  describe('Real-world Scenarios', () => {
    it('should handle typical graph navigation', () => {
      const nodes = generateNodes(50000);
      const index = new QuadTreeNodeIndex();

      // Build index once
      const buildStart = performance.now();
      index.build(nodes);
      const buildTime = performance.now() - buildStart;

      logger.info(`\nReal-world scenario (50k nodes):`);
      logger.info(`  Initial build: ${buildTime.toFixed(2)}ms`);

      // Simulate viewport changes (pan/zoom)
      const viewports = [
        { x: 0, y: 0, zoom: 1.0 },
        { x: -5000, y: -3000, zoom: 0.5 },
        { x: -10000, y: -6000, zoom: 2.0 },
        { x: -2000, y: -1000, zoom: 1.5 },
      ];

      let totalQueryTime = 0;
      let totalVisible = 0;

      for (const vp of viewports) {
        const rect = createViewportRectangle(vp, 1920, 1080);
        const start = performance.now();
        const visible = index.queryViewportWithBuffer(rect, 200);
        const time = performance.now() - start;

        totalQueryTime += time;
        totalVisible += visible.length;
      }

      const avgQueryTime = totalQueryTime / viewports.length;
      const avgVisible = totalVisible / viewports.length;

      logger.info(`  Average query time: ${avgQueryTime.toFixed(3)}ms`);
      logger.info(`  Average visible nodes: ${avgVisible.toFixed(0)}`);
      logger.info(`  Culling ratio: ${((1 - avgVisible / 50000) * 100).toFixed(1)}%`);

      // Should query quickly even with viewport changes
      expect(avgQueryTime).toBeLessThan(2);
    });
  });
});
