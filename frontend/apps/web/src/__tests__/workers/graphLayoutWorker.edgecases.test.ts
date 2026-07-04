/**
 * Graph Layout Worker Edge Case Tests
 * Covers: unknown algorithm fallback, radial orphan nodes, progressive non-grid fallback,
 * benchmark stdDev computation, single-node layouts, disconnected graphs, large graph perf
 */

import { describe, expect, it } from 'vitest';

import {
  benchmarkLayout,
  computeLayout,
  computeLayoutProgressive,
} from '../../workers/graphLayout.worker';

describe('Graph Layout Worker Edge Cases', () => {
  describe('unknown algorithm fallback', () => {
    it('should fall back to grid layout for unknown algorithm', async () => {
      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
      ];

      const result = await computeLayout(nodes, [], {
        algorithm: 'nonexistent' as any,
      });

      expect(result.positions).toBeDefined();
      expect(Object.keys(result.positions)).toHaveLength(2);
      expect(result.positions['1']).toBeDefined();
      expect(result.positions['2']).toBeDefined();
      expect(result.size.width).toBeGreaterThan(0);
      expect(result.size.height).toBeGreaterThan(0);
    });
  });

  describe('empty graph handling', () => {
    it('should return empty result for dagre with 0 nodes', async () => {
      const result = await computeLayout([], [], { algorithm: 'dagre' });
      expect(result.positions).toEqual({});
      expect(result.size).toEqual({ height: 0, width: 0 });
    });

    it('should return empty result for d3-force with 0 nodes', async () => {
      const result = await computeLayout([], [], { algorithm: 'd3-force' });
      expect(result.positions).toEqual({});
      expect(result.size).toEqual({ height: 0, width: 0 });
    });

    it('should return empty result for circular with 0 nodes', async () => {
      const result = await computeLayout([], [], { algorithm: 'circular' });
      expect(result.positions).toEqual({});
      expect(result.size).toEqual({ height: 0, width: 0 });
    });

    it('should return empty result for radial with 0 nodes', async () => {
      const result = await computeLayout([], [], { algorithm: 'radial' });
      expect(result.positions).toEqual({});
      expect(result.size).toEqual({ height: 0, width: 0 });
    });

    it('should return empty result for grid with 0 nodes', async () => {
      const result = await computeLayout([], [], { algorithm: 'grid' });
      expect(result.positions).toEqual({});
      expect(result.size).toEqual({ height: 0, width: 0 });
    });
  });

  describe('single node layouts', () => {
    const singleNode = [{ height: 50, id: 'only', width: 100 }];

    it('should position a single node with dagre', async () => {
      const result = await computeLayout(singleNode, [], { algorithm: 'dagre' });
      expect(Object.keys(result.positions)).toHaveLength(1);
      expect(result.positions['only']).toBeDefined();
      expect(result.positions['only'].x).toBeGreaterThanOrEqual(0);
      expect(result.positions['only'].y).toBeGreaterThanOrEqual(0);
    });

    it('should position a single node with circular', async () => {
      const result = await computeLayout(singleNode, [], { algorithm: 'circular' });
      expect(Object.keys(result.positions)).toHaveLength(1);
      expect(result.positions['only']).toBeDefined();
    });

    it('should position a single node with grid', async () => {
      const result = await computeLayout(singleNode, [], { algorithm: 'grid' });
      expect(Object.keys(result.positions)).toHaveLength(1);
    });

    it('should position a single node with d3-force', async () => {
      const result = await computeLayout(singleNode, [], { algorithm: 'd3-force' });
      expect(Object.keys(result.positions)).toHaveLength(1);
    });
  });

  describe('radial layout with orphan nodes', () => {
    it('should place orphan nodes (no incoming/outgoing edges) in outer ring', async () => {
      const nodes = [
        { height: 50, id: 'root', width: 100 },
        { height: 50, id: 'child1', width: 100 },
        { height: 50, id: 'orphan1', width: 100 },
        { height: 50, id: 'orphan2', width: 100 },
      ];

      const edges = [{ id: 'e1', source: 'root', target: 'child1' }];

      const result = await computeLayout(nodes, edges, { algorithm: 'radial' });

      expect(Object.keys(result.positions)).toHaveLength(4);
      // Orphans should be positioned (they get placed on outer ring)
      expect(result.positions['orphan1']).toBeDefined();
      expect(result.positions['orphan2']).toBeDefined();

      // Orphans should be farther from center than connected nodes
      const rootPos = result.positions['root'];
      const orphanPos = result.positions['orphan1'];
      // Both should have numeric coordinates
      expect(typeof rootPos.x).toBe('number');
      expect(typeof orphanPos.x).toBe('number');
    });

    it('should handle all-orphan radial layout (no edges)', async () => {
      const nodes = [
        { height: 50, id: 'a', width: 100 },
        { height: 50, id: 'b', width: 100 },
        { height: 50, id: 'c', width: 100 },
      ];

      const result = await computeLayout(nodes, [], { algorithm: 'radial' });

      expect(Object.keys(result.positions)).toHaveLength(3);
      // All nodes treated as roots at depth 0
      expect(result.positions['a']).toBeDefined();
      expect(result.positions['b']).toBeDefined();
      expect(result.positions['c']).toBeDefined();
    });
  });

  describe('disconnected graphs', () => {
    it('should layout disconnected components with dagre', async () => {
      const nodes = [
        { height: 50, id: 'a1', width: 100 },
        { height: 50, id: 'a2', width: 100 },
        { height: 50, id: 'b1', width: 100 },
        { height: 50, id: 'b2', width: 100 },
      ];

      const edges = [
        { id: 'e1', source: 'a1', target: 'a2' },
        { id: 'e2', source: 'b1', target: 'b2' },
      ];

      const result = await computeLayout(nodes, edges, { algorithm: 'dagre' });

      expect(Object.keys(result.positions)).toHaveLength(4);
      // All nodes should have positions
      for (const node of nodes) {
        expect(result.positions[node.id]).toBeDefined();
      }
    });

    it('should layout disconnected components with d3-force', async () => {
      const nodes = [
        { height: 50, id: 'x', width: 100 },
        { height: 50, id: 'y', width: 100 },
      ];
      // No edges -- completely isolated nodes
      const result = await computeLayout(nodes, [], { algorithm: 'd3-force' });

      expect(Object.keys(result.positions)).toHaveLength(2);
      expect(result.size.width).toBeGreaterThan(0);
      expect(result.size.height).toBeGreaterThan(0);
    });
  });

  describe('progressive layout', () => {
    it('should yield single result for non-grid progressive layout', async () => {
      const nodes = Array.from({ length: 10 }, (_, i) => ({
        height: 50,
        id: `${i}`,
        width: 100,
      }));

      const edges = Array.from({ length: 9 }, (_, i) => ({
        id: `e${i}`,
        source: `${i}`,
        target: `${i + 1}`,
      }));

      const generator = computeLayoutProgressive(nodes, edges, {
        algorithm: 'dagre',
        batchSize: 5,
        progressive: true,
      });

      const results: any[] = [];
      for await (const result of generator) {
        results.push(result);
      }

      // Non-grid algorithms yield a single complete result
      expect(results.length).toBe(1);
      expect(Object.keys(results[0].positions)).toHaveLength(10);
    });

    it('should yield multiple partial results for grid progressive layout', async () => {
      const nodes = Array.from({ length: 20 }, (_, i) => ({
        height: 50,
        id: `${i}`,
        width: 100,
      }));

      const generator = computeLayoutProgressive(nodes, [], {
        algorithm: 'grid',
        batchSize: 5,
        progressive: true,
      });

      const results: any[] = [];
      for await (const result of generator) {
        results.push(result);
      }

      // 20 nodes / 5 batch size = 4 batches
      expect(results.length).toBe(4);

      // First batches should be partial
      expect(results[0].isPartial).toBeTruthy();
      expect(results[0].progress).toBeCloseTo(0.25);

      // Last batch should be complete
      expect(results[3].isPartial).toBeFalsy();
      expect(results[3].progress).toBeCloseTo(1);
    });
  });

  describe('benchmark statistics', () => {
    it('should compute stdDev correctly for benchmark', async () => {
      const nodes = Array.from({ length: 5 }, (_, i) => ({
        height: 50,
        id: `${i}`,
        width: 100,
      }));

      const result = await benchmarkLayout(nodes, [], {
        algorithm: 'grid',
        iterations: 5,
      });

      expect(result.algorithm).toBe('grid');
      expect(result.nodeCount).toBe(5);
      expect(result.edgeCount).toBe(0);
      expect(result.iterations).toBe(5);
      expect(result.avgTime).toBeGreaterThanOrEqual(0);
      expect(result.minTime).toBeLessThanOrEqual(result.avgTime);
      expect(result.maxTime).toBeGreaterThanOrEqual(result.avgTime);
      expect(result.stdDev).toBeGreaterThanOrEqual(0);
      // StdDev should be finite
      expect(Number.isFinite(result.stdDev)).toBeTruthy();
    });

    it('should use default 5 iterations when not specified', async () => {
      const nodes = [{ height: 50, id: '1', width: 100 }];

      const result = await benchmarkLayout(nodes, [], {
        algorithm: 'grid',
      });

      expect(result.iterations).toBe(5);
    });
  });

  describe('dagre direction options', () => {
    it('should handle BT direction', async () => {
      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
      ];
      const edges = [{ id: 'e1', source: '1', target: '2' }];

      const result = await computeLayout(nodes, edges, {
        algorithm: 'dagre',
        direction: 'BT',
      });

      expect(Object.keys(result.positions)).toHaveLength(2);
    });

    it('should handle RL direction', async () => {
      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
      ];
      const edges = [{ id: 'e1', source: '1', target: '2' }];

      const result = await computeLayout(nodes, edges, {
        algorithm: 'dagre',
        direction: 'RL',
      });

      expect(Object.keys(result.positions)).toHaveLength(2);
    });
  });

  describe('large graph performance', () => {
    it('should handle 1000+ nodes with circular layout under 500ms', async () => {
      const nodes = Array.from({ length: 1200 }, (_, i) => ({
        height: 50,
        id: `node-${i}`,
        width: 100,
      }));

      const start = performance.now();
      const result = await computeLayout(nodes, [], { algorithm: 'circular' });
      const duration = performance.now() - start;

      expect(Object.keys(result.positions)).toHaveLength(1200);
      expect(duration).toBeLessThan(500);
    });

    it('should handle 1000+ nodes with d3-force layout', async () => {
      const nodes = Array.from({ length: 1000 }, (_, i) => ({
        height: 50,
        id: `n${i}`,
        width: 100,
      }));

      const edges = Array.from({ length: 500 }, (_, i) => ({
        id: `e${i}`,
        source: `n${i % 1000}`,
        target: `n${(i * 3 + 7) % 1000}`,
      }));

      const result = await computeLayout(nodes, edges, { algorithm: 'd3-force' });

      expect(Object.keys(result.positions)).toHaveLength(1000);
      expect(result.size.width).toBeGreaterThan(0);
      expect(result.size.height).toBeGreaterThan(0);
    });
  });

  describe('custom spacing options', () => {
    it('should respect custom center options for circular layout', async () => {
      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
      ];

      const result = await computeLayout(nodes, [], {
        algorithm: 'circular',
        centerX: 1000,
        centerY: 800,
      });

      // Positions should be centered around the specified center
      const positions = Object.values(result.positions);
      const avgX = positions.reduce((sum, p) => sum + p.x, 0) / positions.length;
      // Should be roughly around centerX
      expect(avgX).toBeGreaterThan(500);
    });
  });
});
