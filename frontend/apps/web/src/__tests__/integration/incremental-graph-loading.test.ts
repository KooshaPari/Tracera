/**
 * Integration tests for incremental graph loading
 *
 * Tests the full flow from API request to graph rendering
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { IncrementalGraphBuilder } from '../../lib/graph/IncrementalGraphBuilder';
import { useIncrementalGraph } from '../../hooks/useIncrementalGraph';

describe('IncrementalGraphBuilder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('NDJSON parsing', () => {
    it('parses stream chunks correctly', async () => {
      const builder = new IncrementalGraphBuilder();

      const chunks = [
        { type: 'metadata', data: { totalNodes: 2, totalEdges: 1 }, timestamp: Date.now() },
        { type: 'node', data: { id: 'n1', label: 'Node 1', position: { x: 0, y: 0 } }, timestamp: Date.now() },
        { type: 'node', data: { id: 'n2', label: 'Node 2', position: { x: 100, y: 100 } }, timestamp: Date.now() },
        { type: 'edge', data: { id: 'e1', sourceId: 'n1', targetId: 'n2' }, timestamp: Date.now() },
        { type: 'complete', data: {}, timestamp: Date.now() },
      ];

      // Process chunks
      for (const chunk of chunks) {
        builder.processChunk(chunk);
      }

      const result = builder.getResult();

      expect(result.nodes.size).toBe(2);
      expect(result.edges.size).toBe(1);
      expect(result.metadata?.totalNodes).toBe(2);
      expect(result.metadata?.totalEdges).toBe(1);
    });

    it('handles progress updates', async () => {
      const onProgress = vi.fn();
      const builder = new IncrementalGraphBuilder({ onProgress });

      builder.processChunk({
        type: 'node',
        data: { id: 'n1', label: 'Node 1', position: { x: 0, y: 0 } },
        progress: {
          current: 1,
          total: 10,
          percentage: 10,
          stage: 'nodes',
        },
        timestamp: Date.now(),
      });

      expect(onProgress).toHaveBeenCalledWith({
        current: 1,
        total: 10,
        percentage: 10,
        stage: 'nodes',
      });
    });

    it('batches node additions', async () => {
      const onNode = vi.fn();
      const builder = new IncrementalGraphBuilder({
        batchSize: 3,
        batchDelay: 10,
        onNode,
      });

      // Add 5 nodes
      for (let i = 1; i <= 5; i++) {
        builder.addNode({
          id: `n${i}`,
          type: 'test',
          label: `Node ${i}`,
          position: { x: i * 100, y: i * 100 },
          data: {},
        });
      }

      // Wait for batch flush
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(onNode).toHaveBeenCalledTimes(5);
    });
  });

  describe('Stream loading', () => {
    it('loads graph from mock stream', async () => {
      const mockStreamData = [
        { type: 'metadata', data: { totalNodes: 2 }, timestamp: Date.now() },
        { type: 'node', data: { id: 'n1', type: 'test', label: 'Node 1', position: { x: 0, y: 0 }, data: {} }, timestamp: Date.now() },
        { type: 'node', data: { id: 'n2', type: 'test', label: 'Node 2', position: { x: 100, y: 100 }, data: {} }, timestamp: Date.now() },
        { type: 'complete', data: {}, timestamp: Date.now() },
      ];

      const ndjsonData = mockStreamData.map(chunk => JSON.stringify(chunk)).join('\n');

      // Mock fetch
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(new TextEncoder().encode(ndjsonData));
            controller.close();
          },
        }),
      });

      const builder = new IncrementalGraphBuilder();
      const result = await builder.loadFromStream(
        '/api/v1/projects/test/graph/stream',
        { viewport: { minX: 0, minY: 0, maxX: 1000, maxY: 1000 } }
      );

      expect(result.nodes.size).toBe(2);
      expect(result.metadata?.totalNodes).toBe(2);
    });

    it('handles stream errors', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      const builder = new IncrementalGraphBuilder();

      await expect(
        builder.loadFromStream('/api/v1/projects/test/graph/stream', {})
      ).rejects.toThrow('HTTP 500: Internal Server Error');
    });

    it('supports cancellation', async () => {
      const builder = new IncrementalGraphBuilder();

      // Mock a slow stream
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        body: new ReadableStream({
          async start(controller) {
            // Simulate slow stream
            await new Promise(resolve => setTimeout(resolve, 1000));
            controller.enqueue(new TextEncoder().encode('{"type":"node"}\n'));
            controller.close();
          },
        }),
      });

      const promise = builder.loadFromStream('/api/v1/projects/test/graph/stream', {});

      // Abort after 100ms
      setTimeout(() => builder.abort(), 100);

      await expect(promise).rejects.toThrow();
    });
  });

  describe('State management', () => {
    it('tracks node and edge counts', () => {
      const builder = new IncrementalGraphBuilder();

      builder.addNode({ id: 'n1', type: 'test', label: 'N1', position: { x: 0, y: 0 }, data: {} });
      builder.addNode({ id: 'n2', type: 'test', label: 'N2', position: { x: 0, y: 0 }, data: {} });
      builder.addEdge({ id: 'e1', sourceId: 'n1', targetId: 'n2', type: 'link', label: 'Link' });

      const stats = builder.getStats();

      expect(stats.nodeCount).toBe(2);
      expect(stats.edgeCount).toBe(1);
      expect(stats.isComplete).toBe(false);
    });

    it('resets state correctly', () => {
      const builder = new IncrementalGraphBuilder();

      builder.addNode({ id: 'n1', type: 'test', label: 'N1', position: { x: 0, y: 0 }, data: {} });
      builder.reset();

      const stats = builder.getStats();

      expect(stats.nodeCount).toBe(0);
      expect(stats.edgeCount).toBe(0);
    });

    it('checks node existence', () => {
      const builder = new IncrementalGraphBuilder();

      builder.addNode({ id: 'n1', type: 'test', label: 'N1', position: { x: 0, y: 0 }, data: {} });

      expect(builder.hasNode('n1')).toBe(true);
      expect(builder.hasNode('n2')).toBe(false);
    });

    it('retrieves nodes by ID', () => {
      const builder = new IncrementalGraphBuilder();

      const node = { id: 'n1', type: 'test', label: 'N1', position: { x: 0, y: 0 }, data: {} };
      builder.addNode(node);

      expect(builder.getNode('n1')).toEqual(node);
      expect(builder.getNode('n2')).toBeUndefined();
    });
  });
});

describe('useIncrementalGraph', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with correct state', () => {
    const { result } = renderHook(() =>
      useIncrementalGraph({
        projectId: 'test-project',
        viewport: { minX: 0, minY: 0, maxX: 1000, maxY: 1000 },
      })
    );

    expect(result.current.state.nodes).toEqual([]);
    expect(result.current.state.edges).toEqual([]);
    expect(result.current.state.isLoading).toBe(false);
  });

  it('loads graph data', async () => {
    const mockStreamData = [
      { type: 'node', data: { id: 'n1', type: 'test', label: 'Node 1', position: { x: 0, y: 0 }, data: {} }, timestamp: Date.now() },
      { type: 'complete', data: {}, timestamp: Date.now() },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      body: new ReadableStream({
        start(controller) {
          const ndjson = mockStreamData.map(c => JSON.stringify(c)).join('\n');
          controller.enqueue(new TextEncoder().encode(ndjson));
          controller.close();
        },
      }),
    });

    const { result } = renderHook(() =>
      useIncrementalGraph({
        projectId: 'test-project',
        viewport: { minX: 0, minY: 0, maxX: 1000, maxY: 1000 },
      })
    );

    // Trigger load
    result.current.loadGraph();

    // Wait for loading to complete
    await waitFor(() => {
      expect(result.current.state.isLoading).toBe(false);
    });

    expect(result.current.state.nodes.length).toBeGreaterThan(0);
  });

  it('handles errors', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
    });

    const { result } = renderHook(() =>
      useIncrementalGraph({
        projectId: 'test-project',
        viewport: { minX: 0, minY: 0, maxX: 1000, maxY: 1000 },
      })
    );

    result.current.loadGraph();

    await waitFor(() => {
      expect(result.current.state.error).toBeDefined();
    });
  });

  it('supports cancellation', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      body: new ReadableStream({
        async start(controller) {
          await new Promise(resolve => setTimeout(resolve, 1000));
          controller.close();
        },
      }),
    });

    const { result } = renderHook(() =>
      useIncrementalGraph({
        projectId: 'test-project',
        viewport: { minX: 0, minY: 0, maxX: 1000, maxY: 1000 },
      })
    );

    result.current.loadGraph();

    // Wait for loading to start
    await waitFor(() => {
      expect(result.current.state.isLoading).toBe(true);
    });

    // Abort
    result.current.abort();

    expect(result.current.state.isLoading).toBe(false);
  });
});

describe('Prefetch functionality', () => {
  it('calculates pan direction correctly', async () => {
    const { calculatePanDirection } = await import('../../hooks/useIncrementalGraph');

    const oldViewport = { minX: 0, minY: 0, maxX: 1000, maxY: 1000 };

    // East
    expect(calculatePanDirection(oldViewport, { minX: 100, minY: 0, maxX: 1100, maxY: 1000 })).toBe('east');

    // West
    expect(calculatePanDirection(oldViewport, { minX: -100, minY: 0, maxX: 900, maxY: 1000 })).toBe('west');

    // North
    expect(calculatePanDirection(oldViewport, { minX: 0, minY: -100, maxX: 1000, maxY: 900 })).toBe('north');

    // South
    expect(calculatePanDirection(oldViewport, { minX: 0, minY: 100, maxX: 1000, maxY: 1100 })).toBe('south');
  });

  it('calculates pan velocity', async () => {
    const { calculatePanVelocity } = await import('../../hooks/useIncrementalGraph');

    const oldViewport = { minX: 0, minY: 0, maxX: 1000, maxY: 1000 };
    const newViewport = { minX: 100, minY: 0, maxX: 1100, maxY: 1000 };

    // 100px in 100ms = 1000px/s
    const velocity = calculatePanVelocity(oldViewport, newViewport, 100);

    expect(velocity).toBe(1000);
  });
});

describe('Edge cases', () => {
  it('handles empty graph', async () => {
    const builder = new IncrementalGraphBuilder();

    builder.processChunk({
      type: 'complete',
      data: { totalNodes: 0, totalEdges: 0 },
      timestamp: Date.now(),
    });

    const result = builder.getResult();

    expect(result.nodes.size).toBe(0);
    expect(result.edges.size).toBe(0);
  });

  it('handles malformed chunks gracefully', () => {
    const builder = new IncrementalGraphBuilder();

    // Should not throw
    expect(() => {
      builder.processChunk({
        type: 'invalid',
        data: null,
        timestamp: Date.now(),
      } as any);
    }).not.toThrow();
  });

  it('handles duplicate nodes', () => {
    const builder = new IncrementalGraphBuilder();

    const node = { id: 'n1', type: 'test', label: 'Node 1', position: { x: 0, y: 0 }, data: {} };

    builder.addNode(node);
    builder.addNode(node); // Duplicate

    expect(builder.getStats().nodeCount).toBe(1); // Should overwrite
  });
});
