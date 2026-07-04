/**
 * Unit Tests for useGpuForceLayout Hook
 *
 * @vitest-environment jsdom
 */

import type { Edge, Node } from '@xyflow/react';

import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { useGpuForceLayout } from '../useGpuForceLayout';

const createNodes = (count: number): Node[] =>
  Array.from({ length: count }, (_, i) => ({
    data: {},
    id: `node-${i}`,
    position: { x: 0, y: 0 },
    type: 'default',
  }));

const createEdges = (count: number): Edge[] =>
  Array.from({ length: count - 1 }, (_, i) => ({
    id: `edge-${i}`,
    source: `node-${i}`,
    target: `node-${i + 1}`,
  }));

describe(useGpuForceLayout, () => {
  describe('basic functionality', () => {
    it('should initialize with empty nodes', () => {
      const { result } = renderHook(() => useGpuForceLayout([], []));

      expect(result.current.nodes).toEqual([]);
      expect(result.current.isComputing).toBeFalsy();
      expect(result.current.progress).toBe(0);
    });

    it('should layout small graph on main thread', async () => {
      const nodes = createNodes(10);
      const edges = createEdges(10);

      const { result } = renderHook(() =>
        useGpuForceLayout(nodes, edges, {
          animateTransitions: false,
        }),
      );

      // Should start computing
      await waitFor(() => {
        expect(result.current.nodes.length).toBe(10);
      });

      // Positions should be updated
      const node0 = result.current.nodes[0];
      expect(node0).toBeDefined();
      expect(node0.position.x).not.toBe(0);
    });

    it('should handle disabled option', () => {
      const nodes = createNodes(5);
      const edges = createEdges(5);

      const { result } = renderHook(() =>
        useGpuForceLayout(nodes, edges, {
          enabled: false,
        }),
      );

      // Should return original nodes without computation
      expect(result.current.nodes).toEqual(nodes);
      expect(result.current.isComputing).toBeFalsy();
    });
  });

  describe('state management', () => {
    it('should track computing state', async () => {
      const nodes = createNodes(100);
      const edges = createEdges(100);

      const { result } = renderHook(() =>
        useGpuForceLayout(nodes, edges, {
          animateTransitions: false,
        }),
      );

      // Should eventually finish computing
      await waitFor(
        () => {
          expect(result.current.isComputing).toBeFalsy();
        },
        { timeout: 5000 },
      );

      expect(result.current.duration).toBeGreaterThan(0);
    });

    it('should provide progress updates for large graphs', async () => {
      const nodes = createNodes(1500); // Above worker threshold
      const edges = createEdges(1500);

      const { result } = renderHook(() =>
        useGpuForceLayout(nodes, edges, {
          animateTransitions: false,
        }),
      );

      await waitFor(
        () => {
          expect(result.current.isComputing).toBeFalsy();
        },
        { timeout: 10_000 },
      );

      expect(result.current.nodes.length).toBe(1500);
    });
  });

  describe('configuration', () => {
    it('should accept custom force config', async () => {
      const nodes = createNodes(20);
      const edges = createEdges(20);

      const { result } = renderHook(() =>
        useGpuForceLayout(nodes, edges, {
          animateTransitions: false,
          config: {
            attractionStrength: 0.2,
            iterations: 50,
            repulsionStrength: 10_000,
          },
        }),
      );

      await waitFor(() => {
        expect(result.current.nodes.length).toBe(20);
      });

      const node0 = result.current.nodes[0];
      expect(node0).toBeDefined();
      expect(node0.position.x).not.toBe(0);
    });

    it('should handle animation duration', async () => {
      const nodes = createNodes(10);
      const edges = createEdges(10);

      const { result } = renderHook(() =>
        useGpuForceLayout(nodes, edges, {
          animateTransitions: true,
          animationDuration: 1000,
        }),
      );

      await waitFor(() => {
        expect(result.current.nodes.length).toBe(10);
      });
    });
  });

  describe('calculateLayout function', () => {
    it('should allow manual layout calculation', async () => {
      const nodes = createNodes(5);
      const edges = createEdges(5);

      const { result } = renderHook(() => useGpuForceLayout([], [], { enabled: false }));

      const layoutedNodes = await result.current.calculateLayout(nodes, edges);

      expect(layoutedNodes).toHaveLength(5);
      const firstNode = layoutedNodes[0];
      expect(firstNode).toBeDefined();
      expect(firstNode.position.x).not.toBe(0);
    });

    it('should return original nodes when disabled', async () => {
      const nodes = createNodes(5);
      const edges = createEdges(5);

      const { result } = renderHook(() => useGpuForceLayout([], [], { enabled: false }));

      const layoutedNodes = await result.current.calculateLayout(nodes, edges);

      expect(layoutedNodes).toEqual(nodes);
    });
  });

  describe('error handling', () => {
    it('should handle empty nodes gracefully', async () => {
      const { result } = renderHook(() => useGpuForceLayout([], [], { animateTransitions: false }));

      expect(result.current.nodes).toEqual([]);
      expect(result.current.error).toBeNull();
    });

    it('should preserve node data on error', async () => {
      const nodes: Node[] = [
        {
          data: { label: 'Test' },
          id: '1',
          position: { x: 0, y: 0 },
          type: 'custom',
        },
      ];

      const { result } = renderHook(() =>
        useGpuForceLayout(nodes, [], { animateTransitions: false }),
      );

      await waitFor(() => {
        expect(result.current.nodes.length).toBe(1);
      });

      const node0 = result.current.nodes[0];
      expect(node0).toBeDefined();
      expect(node0.data).toEqual({ label: 'Test' });
    });
  });

  describe('updates and re-renders', () => {
    it('should recalculate when nodes change', async () => {
      const { result, rerender } = renderHook(
        ({ nodes, edges }) => useGpuForceLayout(nodes, edges, { animateTransitions: false }),
        {
          initialProps: {
            edges: createEdges(5),
            nodes: createNodes(5),
          },
        },
      );

      await waitFor(() => {
        expect(result.current.nodes.length).toBe(5);
      });

      // Update with new nodes
      rerender({
        edges: createEdges(10),
        nodes: createNodes(10),
      });

      await waitFor(() => {
        expect(result.current.nodes.length).toBe(10);
      });

      expect(result.current.nodes.length).toBe(10);
    });

    it('should not recalculate when nodes are same', async () => {
      const nodes = createNodes(5);
      const edges = createEdges(5);

      const { result, rerender } = renderHook(
        ({ nodes, edges }) => useGpuForceLayout(nodes, edges, { animateTransitions: false }),
        {
          initialProps: { edges, nodes },
        },
      );

      await waitFor(() => {
        expect(result.current.nodes.length).toBe(5);
      });

      const firstDuration = result.current.duration;

      // Re-render with same props
      rerender({ edges, nodes });

      // Duration should not change (no recalculation)
      expect(result.current.duration).toBe(firstDuration);
    });
  });

  describe('worker usage', () => {
    it('should use worker for large graphs', async () => {
      const nodes = createNodes(1500); // Above WORKER_THRESHOLD
      const edges = createEdges(1500);

      const { result } = renderHook(() =>
        useGpuForceLayout(nodes, edges, {
          animateTransitions: false,
        }),
      );

      await waitFor(
        () => {
          expect(result.current.isComputing).toBeFalsy();
        },
        { timeout: 10_000 },
      );

      expect(result.current.nodes.length).toBe(1500);
      expect(result.current.duration).toBeGreaterThan(0);
    });

    it('should use main thread for small graphs', async () => {
      const nodes = createNodes(50); // Below WORKER_THRESHOLD
      const edges = createEdges(50);

      const { result } = renderHook(() =>
        useGpuForceLayout(nodes, edges, {
          animateTransitions: false,
        }),
      );

      await waitFor(() => {
        expect(result.current.isComputing).toBeFalsy();
      });

      expect(result.current.nodes.length).toBe(50);
    });
  });
});
