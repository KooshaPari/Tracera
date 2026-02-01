import { describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import type { Node, Edge } from '@xyflow/react';
import { useHybridGraph } from '@/hooks/useHybridGraph';

// Mock the graphology adapter
vi.mock('@/lib/graphology/adapter', () => ({
  createGraphologyAdapter: () => ({
    syncFromReactFlow: vi.fn(),
    getGraph: vi.fn(() => ({ type: 'mock-graph' })),
  }),
}));

describe('useHybridGraph', () => {
  it('should return reactflow mode for <10k nodes', () => {
    const nodes: Node[] = Array.from({ length: 5000 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    expect(result.current.useWebGL).toBe(false);
    expect(result.current.performanceMode).toBe('reactflow');
    expect(result.current.graphologyGraph).toBe(null);
    expect(result.current.nodeCount).toBe(5000);
  });

  it('should return webgl mode for >10k nodes', () => {
    const nodes: Node[] = Array.from({ length: 15000 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    expect(result.current.useWebGL).toBe(true);
    expect(result.current.performanceMode).toBe('webgl');
    expect(result.current.graphologyGraph).not.toBe(null);
    expect(result.current.nodeCount).toBe(15000);
  });

  it('should respect forceReactFlow override', () => {
    const nodes: Node[] = Array.from({ length: 15000 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() =>
      useHybridGraph(nodes, edges, { forceReactFlow: true })
    );

    expect(result.current.useWebGL).toBe(false);
    expect(result.current.performanceMode).toBe('reactflow');
  });

  it('should respect forceWebGL override', () => {
    const nodes: Node[] = Array.from({ length: 100 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() =>
      useHybridGraph(nodes, edges, { forceWebGL: true })
    );

    expect(result.current.useWebGL).toBe(true);
    expect(result.current.performanceMode).toBe('webgl');
  });

  it('should use custom threshold', () => {
    const nodes: Node[] = Array.from({ length: 3000 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() =>
      useHybridGraph(nodes, edges, { nodeThreshold: 2000 })
    );

    expect(result.current.useWebGL).toBe(true);
  });

  it('should count edges correctly', () => {
    const nodes: Node[] = [
      { id: 'node1', type: 'default', position: { x: 0, y: 0 }, data: {} },
      { id: 'node2', type: 'default', position: { x: 0, y: 0 }, data: {} },
    ];
    const edges: Edge[] = [
      { id: 'edge1', source: 'node1', target: 'node2' },
    ];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    expect(result.current.edgeCount).toBe(1);
  });

  it('should handle selectedNodeId state', () => {
    const nodes: Node[] = [
      { id: 'node1', type: 'default', position: { x: 0, y: 0 }, data: {} },
    ];
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
    expect(result.current.useWebGL).toBe(false);
  });

  it('should handle exactly threshold boundary (10k)', () => {
    const nodes: Node[] = Array.from({ length: 10000 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    // At exactly 10k, should switch to WebGL
    expect(result.current.useWebGL).toBe(true);
  });

  it('should handle 9999 nodes (just below threshold)', () => {
    const nodes: Node[] = Array.from({ length: 9999 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() => useHybridGraph(nodes, edges));

    expect(result.current.useWebGL).toBe(false);
  });

  it('should prioritize forceReactFlow over forceWebGL', () => {
    const nodes: Node[] = Array.from({ length: 15000 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));
    const edges: Edge[] = [];

    const { result } = renderHook(() =>
      useHybridGraph(nodes, edges, {
        forceReactFlow: true,
        forceWebGL: true,
      })
    );

    // forceReactFlow should take precedence (checked first in hook)
    expect(result.current.useWebGL).toBe(false);
  });

  it('should update mode when node count changes', () => {
    const nodes5k: Node[] = Array.from({ length: 5000 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));

    const nodes15k: Node[] = Array.from({ length: 15000 }, (_, i) => ({
      id: `node-${i}`,
      type: 'default',
      position: { x: 0, y: 0 },
      data: {},
    }));

    const edges: Edge[] = [];

    const { result, rerender } = renderHook(
      ({ nodes }) => useHybridGraph(nodes, edges),
      { initialProps: { nodes: nodes5k } }
    );

    // Initially ReactFlow
    expect(result.current.useWebGL).toBe(false);

    // Switch to WebGL after rerender with more nodes
    rerender({ nodes: nodes15k });
    expect(result.current.useWebGL).toBe(true);
  });
});
