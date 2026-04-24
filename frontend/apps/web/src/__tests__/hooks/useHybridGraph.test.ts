import type { Edge, Node } from '@xyflow/react';

import { renderHook } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { useHybridGraph } from '@/hooks/useHybridGraph';

// Mock the graphology adapter
vi.mock('@/lib/graphology/adapter', () => ({
  createGraphologyAdapter: () => ({
    getGraph: vi.fn(() => ({ type: 'mock-graph' })),
    syncFromReactFlow: vi.fn(),
  }),
}));

describe(useHybridGraph, () => {
  it('should return reactflow mode for <10k nodes', () => {
    const nodes: Node[] = Array.from({ length: 5000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    expect(result.current.useWebGL).toBeFalsy();
    expect(result.current.performanceMode).toBe('reactflow');
    expect(result.current.graphologyGraph).toBe(null);
    expect(result.current.nodeCount).toBe(5000);
  });

  it('should return webgl mode for >10k nodes', () => {
    const nodes: Node[] = Array.from({ length: 15_000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    expect(result.current.useWebGL).toBeTruthy();
    expect(result.current.performanceMode).toBe('webgl');
    expect(result.current.graphologyGraph).not.toBe(null);
    expect(result.current.nodeCount).toBe(15_000);
  });

  it('should respect forceReactFlow override', () => {
    const nodes: Node[] = Array.from({ length: 15_000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges, { forceReactFlow: true }));

    expect(result.current.useWebGL).toBeFalsy();
    expect(result.current.performanceMode).toBe('reactflow');
  });

  it('should respect forceWebGL override', () => {
    const nodes: Node[] = Array.from({ length: 100 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges, { forceWebGL: true }));

    expect(result.current.useWebGL).toBeTruthy();
    expect(result.current.performanceMode).toBe('webgl');
  });

  it('should use custom threshold', () => {
    const nodes: Node[] = Array.from({ length: 3000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges, { nodeThreshold: 2000 }));

    expect(result.current.useWebGL).toBeTruthy();
  });

  it('should count edges correctly', () => {
    const nodes: Node[] = [
      { data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' },
      { data: {}, id: 'node2', position: { x: 0, y: 0 }, type: 'default' },
    ];
    const edges: Edge[] = [{ id: 'edge1', source: 'node1', target: 'node2' }];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    expect(result.current.edgeCount).toBe(1);
  });

  it('should handle selectedNodeId state', () => {
    const nodes: Node[] = [{ data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' }];
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    expect(result.current.selectedNodeId).toBe(null);

    // Test setter exists
    expect(typeof result.current.setSelectedNodeId).toBe('function');
  });

  it('should handle empty arrays', () => {
    const { result } = renderHook(() => useHybridGraph([], []));

    expect(result.current.nodeCount).toBe(0);
    expect(result.current.edgeCount).toBe(0);
    expect(result.current.useWebGL).toBeFalsy();
  });

  it('should handle exactly threshold boundary (10k)', () => {
    const nodes: Node[] = Array.from({ length: 10_000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    // At exactly 10k, should switch to WebGL
    expect(result.current.useWebGL).toBeTruthy();
  });

  it('should handle 9999 nodes (just below threshold)', () => {
    const nodes: Node[] = Array.from({ length: 9999 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    expect(result.current.useWebGL).toBeFalsy();
  });

  it('should prioritize forceReactFlow over forceWebGL', () => {
    const nodes: Node[] = Array.from({ length: 15_000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() =>
      useHybridGraph(nodes, edges, {
        forceReactFlow: true,
        forceWebGL: true,
      }),
    );

    // ForceReactFlow should take precedence (checked first in hook)
    expect(result.current.useWebGL).toBeFalsy();
  });

  it('should update mode when node count changes', () => {
    const nodes5k: Node[] = Array.from({ length: 5000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const nodes15k: Node[] = Array.from({ length: 15_000 }, (_, i) => ({
      data: {},
      id: `node-${i}`,
      position: { x: 0, y: 0 },
      type: 'default',
    }));

    const edges: Edge[] = [];

    const { result, rerender } = renderHook(({ nodes }) => useHybridGraph(nodes, edges), {
      initialProps: { nodes: nodes5k },
    });

    // Initially ReactFlow
    expect(result.current.useWebGL).toBeFalsy();

    // Switch to WebGL after rerender with more nodes
    rerender({ nodes: nodes15k });
    expect(result.current.useWebGL).toBeTruthy();
  });
});
