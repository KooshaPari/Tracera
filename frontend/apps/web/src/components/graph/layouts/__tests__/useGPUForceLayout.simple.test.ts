/**
 * Simplified Tests for GPU Force Layout Hook Logic
 */

import type { Edge, Node } from '@xyflow/react';

import { afterEach, describe, expect, it } from 'vitest';

import { disposeGPUForceLayout, getGPUForceLayout } from '../gpuForceLayout';

function createNodes(count: number): Node[] {
  return Array.from({ length: count }, (_, i) => ({
    data: {},
    id: `node-${i}`,
    position: { x: 0, y: 0 },
    type: 'default',
  }));
}

function createEdges(count: number): Edge[] {
  return Array.from({ length: count - 1 }, (_, i) => ({
    id: `edge-${i}`,
    source: `node-${i}`,
    target: `node-${i + 1}`,
  }));
}

describe('GPU Force Layout Hook Logic', () => {
  afterEach(() => {
    disposeGPUForceLayout();
  });

  describe('Manual layout calculation', () => {
    it('should calculate layout for small graphs', async () => {
      const nodes = createNodes(5);
      const edges = createEdges(5);

      const layout = getGPUForceLayout();
      const result = await layout.simulate(nodes, edges, {
        animateTransitions: false,
        iterations: 50,
      });

      expect(result).toHaveLength(5);
      expect(result[0].position.x).not.toBe(0);
    });

    it('should handle empty nodes', async () => {
      const layout = getGPUForceLayout();
      const result = await layout.simulate([], []);

      expect(result).toEqual([]);
    });

    it('should preserve node data', async () => {
      const nodes: Node[] = [
        {
          data: { label: 'Test' },
          id: '1',
          position: { x: 0, y: 0 },
          type: 'custom',
        },
      ];

      const layout = getGPUForceLayout();
      const result = await layout.simulate(nodes, []);

      expect(result[0].data).toEqual({ label: 'Test' });
      expect(result[0].type).toBe('custom');
    });

    it('should accept custom configuration', async () => {
      const nodes = createNodes(10);
      const edges = createEdges(10);

      const layout = getGPUForceLayout();
      const result = await layout.simulate(nodes, edges, {
        iterations: 20,
        repulsionStrength: 10_000,
        theta: 0.6,
      });

      expect(result).toHaveLength(10);
    });
  });

  describe('Performance characteristics', () => {
    it('should complete small graphs quickly', async () => {
      const nodes = createNodes(50);
      const edges = createEdges(50);

      const layout = getGPUForceLayout();
      const start = performance.now();
      await layout.simulate(nodes, edges, {
        iterations: 30,
      });
      const duration = performance.now() - start;

      expect(duration).toBeLessThan(5000);
    });

    it('should handle different graph sizes', async () => {
      const sizes = [5, 10, 20];

      for (const size of sizes) {
        const nodes = createNodes(size);
        const edges = createEdges(size);

        const layout = getGPUForceLayout();
        const result = await layout.simulate(nodes, edges, {
          iterations: 20,
        });

        expect(result).toHaveLength(size);
      }
    });
  });

  describe('Error handling', () => {
    it('should handle disconnected nodes', async () => {
      const nodes = createNodes(3);
      const edges: Edge[] = []; // No edges

      const layout = getGPUForceLayout();
      const result = await layout.simulate(nodes, edges);

      expect(result).toHaveLength(3);
      // Disconnected nodes should still get positions
      expect(result[0].position.x).toBeGreaterThanOrEqual(0);
    });

    it('should handle self-loops', async () => {
      const nodes: Node[] = [{ data: {}, id: '1', position: { x: 0, y: 0 }, type: 'default' }];
      const edges: Edge[] = [{ id: 'e1', source: '1', target: '1' }];

      const layout = getGPUForceLayout();
      const result = await layout.simulate(nodes, edges);

      expect(result).toHaveLength(1);
    });
  });

  describe('Configuration options', () => {
    it('should respect low iteration count', async () => {
      const nodes = createNodes(10);
      const edges = createEdges(10);

      const layout = getGPUForceLayout();
      const start = performance.now();
      await layout.simulate(nodes, edges, {
        iterations: 5,
      });
      const duration = performance.now() - start;

      // Low iterations should be fast
      expect(duration).toBeLessThan(1000);
    });

    it('should respect high repulsion', async () => {
      const nodes = createNodes(5);
      const edges: Edge[] = [];

      const layout = getGPUForceLayout();
      const result = await layout.simulate(nodes, edges, {
        iterations: 50,
        repulsionStrength: 10_000,
      });

      // Calculate average distance between nodes
      let totalDist = 0;
      let count = 0;
      for (let i = 0; i < result.length; i++) {
        for (let j = i + 1; j < result.length; j++) {
          const dx = result[i].position.x - result[j].position.x;
          const dy = result[i].position.y - result[j].position.y;
          totalDist += Math.sqrt(dx * dx + dy * dy);
          count++;
        }
      }
      const avgDist = totalDist / count;

      // High repulsion should create larger distances
      expect(avgDist).toBeGreaterThan(50);
    });
  });
});
