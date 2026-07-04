/**
 * Unit Tests for GPU Force-Directed Layout
 */

import type { Edge, Node } from '@xyflow/react';

import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { disposeGPUForceLayout, getGPUForceLayout, GPUForceLayout } from '../gpuForceLayout';

describe(GPUForceLayout, () => {
  let layout: GPUForceLayout;

  beforeEach(() => {
    layout = new GPUForceLayout();
  });

  afterEach(() => {
    layout.dispose();
  });

  describe('initialization', () => {
    it('should create a new instance', () => {
      expect(layout).toBeInstanceOf(GPUForceLayout);
    });

    it('should handle empty node list', async () => {
      const result = await layout.simulate([], []);
      expect(result).toEqual([]);
    });
  });

  describe('basic simulation', () => {
    it('should layout simple graph with 3 nodes', async () => {
      const nodes: Node[] = [
        { data: {}, id: '1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: '2', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: '3', position: { x: 0, y: 0 }, type: 'default' },
      ];

      const edges: Edge[] = [
        { id: 'e1', source: '1', target: '2' },
        { id: 'e2', source: '2', target: '3' },
      ];

      const result = await layout.simulate(nodes, edges, {
        iterations: 100,
      });

      expect(result).toHaveLength(3);
      expect(result[0]?.id).toBe('1');
      expect(result[1]?.id).toBe('2');
      expect(result[2]?.id).toBe('3');

      // Positions should be updated
      expect(result[0]?.position.x).not.toBe(0);
      expect(result[0]?.position.y).not.toBe(0);
    });

    it('should handle disconnected nodes', async () => {
      const nodes: Node[] = [
        { data: {}, id: '1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: '2', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: '3', position: { x: 0, y: 0 }, type: 'default' },
      ];

      const edges: Edge[] = [];

      const result = await layout.simulate(nodes, edges, {
        iterations: 50,
      });

      expect(result).toHaveLength(3);

      // Disconnected nodes should repel each other
      const n0 = result[0];
      const n1 = result[1];
      const dist12 =
        n0 && n1 ? Math.hypot(n0.position.x - n1.position.x, n0.position.y - n1.position.y) : 0;

      expect(dist12).toBeGreaterThan(0);
    });
  });

  describe('configuration', () => {
    it('should respect custom repulsion strength', async () => {
      const nodes: Node[] = [
        { data: {}, id: '1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: '2', position: { x: 0, y: 0 }, type: 'default' },
      ];

      const edges: Edge[] = [];

      // High repulsion
      const result1 = await layout.simulate(nodes, edges, {
        iterations: 100,
        repulsionStrength: 10_000,
      });

      // Low repulsion
      const result2 = await layout.simulate(nodes, edges, {
        iterations: 100,
        repulsionStrength: 1000,
      });

      const r1a = result1[0];
      const r1b = result1[1];
      const dist1 =
        r1a && r1b
          ? Math.hypot(r1a.position.x - r1b.position.x, r1a.position.y - r1b.position.y)
          : 0;

      const r2a = result2[0];
      const r2b = result2[1];
      const dist2 =
        r2a && r2b
          ? Math.hypot(r2a.position.x - r2b.position.x, r2a.position.y - r2b.position.y)
          : 0;

      // Higher repulsion should result in larger distance
      expect(dist1).toBeGreaterThan(dist2);
    });

    it('should respect custom attraction strength', async () => {
      const nodes: Node[] = [
        { data: {}, id: '1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: '2', position: { x: 1000, y: 1000 }, type: 'default' },
      ];

      const edges: Edge[] = [{ id: 'e1', source: '1', target: '2' }];

      // High attraction
      const result1 = await layout.simulate(nodes, edges, {
        attractionStrength: 0.5,
        iterations: 100,
      });

      // Low attraction
      const result2 = await layout.simulate(nodes, edges, {
        attractionStrength: 0.05,
        iterations: 100,
      });

      const r1a = result1[0];
      const r1b = result1[1];
      const dist1 =
        r1a && r1b
          ? Math.hypot(r1a.position.x - r1b.position.x, r1a.position.y - r1b.position.y)
          : 0;

      const r2a = result2[0];
      const r2b = result2[1];
      const dist2 =
        r2a && r2b
          ? Math.hypot(r2a.position.x - r2b.position.x, r2a.position.y - r2b.position.y)
          : 0;

      // Higher attraction should result in smaller distance
      expect(dist1).toBeLessThan(dist2);
    });

    it('should respect iteration count', async () => {
      const nodes: Node[] = Array.from({ length: 10 }, (_, i) => ({
        data: {},
        id: `${i}`,
        position: { x: 0, y: 0 },
        type: 'default' as const,
      }));

      const edges: Edge[] = Array.from({ length: 9 }, (_, i) => ({
        id: `e${i}`,
        source: `${i}`,
        target: `${i + 1}`,
      }));

      // More iterations should converge better
      const result1 = await layout.simulate(nodes, edges, {
        iterations: 10,
      });

      const result2 = await layout.simulate(nodes, edges, {
        iterations: 200,
      });

      // Can't easily test convergence, but verify both complete
      expect(result1).toHaveLength(10);
      expect(result2).toHaveLength(10);
    });
  });

  describe('Barnes-Hut optimization', () => {
    it('should accept theta parameter', async () => {
      const nodes: Node[] = Array.from({ length: 100 }, (_, i) => ({
        data: {},
        id: `${i}`,
        position: { x: 0, y: 0 },
        type: 'default' as const,
      }));

      const edges: Edge[] = [];

      const result = await layout.simulate(nodes, edges, {
        iterations: 50,
        theta: 0.5,
      });

      expect(result).toHaveLength(100);
    });

    it('should handle different theta values', async () => {
      const nodes: Node[] = Array.from({ length: 50 }, (_, i) => ({
        data: {},
        id: `${i}`,
        position: { x: 0, y: 0 },
        type: 'default' as const,
      }));

      const edges: Edge[] = [];

      // Exact (theta = 0)
      const result1 = await layout.simulate(nodes, edges, {
        iterations: 30,
        theta: 0,
      });

      // Approximate (theta = 0.8)
      const result2 = await layout.simulate(nodes, edges, {
        iterations: 30,
        theta: 0.8,
      });

      // Both should complete
      expect(result1).toHaveLength(50);
      expect(result2).toHaveLength(50);

      // Results should be similar but not identical
      const pos1 = result1[0]?.position;
      const pos2 = result2[0]?.position;
      if (!pos1 || !pos2) {
        throw new Error('Expected result positions');
      }

      // Positions should be in same general area (within 50%)
      const dist = Math.hypot(pos1.x - pos2.x, pos1.y - pos2.y);
      const maxDist = Math.max(
        Math.abs(pos1.x),
        Math.abs(pos1.y),
        Math.abs(pos2.x),
        Math.abs(pos2.y),
      );

      expect(dist / maxDist).toBeLessThan(0.5);
    });
  });

  describe('edge cases', () => {
    it('should handle single node', async () => {
      const nodes: Node[] = [{ data: {}, id: '1', position: { x: 0, y: 0 }, type: 'default' }];

      const result = await layout.simulate(nodes, []);

      expect(result).toHaveLength(1);
      expect(result[0]?.position.x).toBeGreaterThanOrEqual(0);
      expect(result[0]?.position.y).toBeGreaterThanOrEqual(0);
    });

    it('should handle two nodes with edge', async () => {
      const nodes: Node[] = [
        { data: {}, id: '1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: '2', position: { x: 0, y: 0 }, type: 'default' },
      ];

      const edges: Edge[] = [{ id: 'e1', source: '1', target: '2' }];

      const result = await layout.simulate(nodes, edges, {
        iterations: 100,
      });

      expect(result).toHaveLength(2);

      // Nodes should be close but not overlapping
      const n0 = result[0];
      const n1 = result[1];
      const dist =
        n0 && n1 ? Math.hypot(n0.position.x - n1.position.x, n0.position.y - n1.position.y) : 0;

      expect(dist).toBeGreaterThan(10);
      expect(dist).toBeLessThan(500);
    });

    it('should handle self-loop edge', async () => {
      const nodes: Node[] = [{ data: {}, id: '1', position: { x: 0, y: 0 }, type: 'default' }];

      const edges: Edge[] = [{ id: 'e1', source: '1', target: '1' }];

      const result = await layout.simulate(nodes, edges);

      expect(result).toHaveLength(1);
    });

    it('should handle duplicate edges', async () => {
      const nodes: Node[] = [
        { data: {}, id: '1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: '2', position: { x: 0, y: 0 }, type: 'default' },
      ];

      const edges: Edge[] = [
        { id: 'e1', source: '1', target: '2' },
        { id: 'e2', source: '1', target: '2' },
      ];

      const result = await layout.simulate(nodes, edges);

      expect(result).toHaveLength(2);
    });
  });

  describe('position normalization', () => {
    it('should normalize positions to positive coordinates', async () => {
      const nodes: Node[] = Array.from({ length: 20 }, (_, i) => ({
        data: {},
        id: `${i}`,
        position: { x: 0, y: 0 },
        type: 'default' as const,
      }));

      const edges: Edge[] = [];

      const result = await layout.simulate(nodes, edges);

      // All positions should be positive
      for (const node of result) {
        expect(node.position.x).toBeGreaterThanOrEqual(0);
        expect(node.position.y).toBeGreaterThanOrEqual(0);
      }
    });

    it('should preserve node data', async () => {
      const nodes: Node[] = [
        {
          data: { label: 'Test Node', value: 42 },
          id: '1',
          position: { x: 0, y: 0 },
          type: 'custom',
        },
      ];

      const result = await layout.simulate(nodes, []);

      expect(result[0]?.data).toEqual({ label: 'Test Node', value: 42 });
      expect(result[0]?.type).toBe('custom');
    });
  });
});

describe('Singleton instance', () => {
  afterEach(() => {
    disposeGPUForceLayout();
  });

  it('should return same instance', () => {
    const instance1 = getGPUForceLayout();
    const instance2 = getGPUForceLayout();

    expect(instance1).toBe(instance2);
  });

  it('should dispose instance', () => {
    const instance1 = getGPUForceLayout();
    disposeGPUForceLayout();
    const instance2 = getGPUForceLayout();

    expect(instance1).not.toBe(instance2);
  });
});
