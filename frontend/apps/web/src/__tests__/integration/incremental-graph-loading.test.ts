/**
 * Integration tests for incremental graph loading
 *
 * Tests the full flow from API request to graph rendering
 */

import { renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { StreamChunk } from '../../lib/graph/IncrementalGraphBuilder';

import { useIncrementalGraph } from '../../hooks/useIncrementalGraph';
import { IncrementalGraphBuilder } from '../../lib/graph/IncrementalGraphBuilder';

describe(IncrementalGraphBuilder, () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('NDJSON parsing', () => {
    it('parses stream chunks correctly', async () => {
      const builder = new IncrementalGraphBuilder();

      const chunks: StreamChunk[] = [
        {
          data: { totalEdges: 1, totalNodes: 2 },
          timestamp: Date.now(),
          type: 'metadata',
        },
        {
          data: { id: 'n1', label: 'Node 1', position: { x: 0, y: 0 } },
          timestamp: Date.now(),
          type: 'node',
        },
        {
          data: { id: 'n2', label: 'Node 2', position: { x: 100, y: 100 } },
          timestamp: Date.now(),
          type: 'node',
        },
        {
          data: { id: 'e1', sourceId: 'n1', targetId: 'n2' },
          timestamp: Date.now(),
          type: 'edge',
        },
        { data: {}, timestamp: Date.now(), type: 'complete' },
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
        data: { id: 'n1', label: 'Node 1', position: { x: 0, y: 0 } },
        progress: {
          current: 1,
          percentage: 10,
          stage: 'nodes',
          total: 10,
        },
        timestamp: Date.now(),
        type: 'node',
      });

      expect(onProgress).toHaveBeenCalledWith({
        current: 1,
        percentage: 10,
        stage: 'nodes',
        total: 10,
      });
    });

    it('batches node additions', async () => {
      const onNode = vi.fn();
      const builder = new IncrementalGraphBuilder({
        batchDelay: 10,
        batchSize: 3,
        onNode,
      });

      // Add 5 nodes
      for (let i = 1; i <= 5; i++) {
        builder.addNode({
          data: {},
          id: `n${i}`,
          label: `Node ${i}`,
          position: { x: i * 100, y: i * 100 },
          type: 'test',
        });
      }

      // Wait for batch flush
      await new Promise((resolve) => setTimeout(resolve, 50));

      expect(onNode).toHaveBeenCalledTimes(5);
    });
  });

  describe('Stream loading', () => {
    it('loads graph from mock stream', async () => {
      const mockStreamData = [
        { data: { totalNodes: 2 }, timestamp: Date.now(), type: 'metadata' },
        {
          data: {
            data: {},
            id: 'n1',
            label: 'Node 1',
            position: { x: 0, y: 0 },
            type: 'test',
          },
          timestamp: Date.now(),
          type: 'node',
        },
        {
          data: {
            data: {},
            id: 'n2',
            label: 'Node 2',
            position: { x: 100, y: 100 },
            type: 'test',
          },
          timestamp: Date.now(),
          type: 'node',
        },
        { data: {}, timestamp: Date.now(), type: 'complete' },
      ];

      const ndjsonData = mockStreamData.map((chunk) => JSON.stringify(chunk)).join('\n');

      // Mock fetch
      globalThis.fetch = vi.fn().mockResolvedValue({
        body: new ReadableStream({
          start(controller) {
            controller.enqueue(new TextEncoder().encode(ndjsonData));
            controller.close();
          },
        }),
        ok: true,
      });

      const builder = new IncrementalGraphBuilder();
      const result = await builder.loadFromStream('/api/v1/projects/test/graph/stream', {
        viewport: { maxX: 1000, maxY: 1000, minX: 0, minY: 0 },
      });

      expect(result.nodes.size).toBe(2);
      expect(result.metadata?.totalNodes).toBe(2);
    });

    it('handles stream errors', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      const builder = new IncrementalGraphBuilder();

      await expect(
        builder.loadFromStream('/api/v1/projects/test/graph/stream', {}),
      ).rejects.toThrow('HTTP 500: Internal Server Error');
    });

    it('supports cancellation', async () => {
      const builder = new IncrementalGraphBuilder();

      // Mock a slow stream
      globalThis.fetch = vi.fn().mockResolvedValue({
        body: new ReadableStream({
          async start(controller) {
            // Simulate slow stream
            await new Promise((resolve) => setTimeout(resolve, 1000));
            controller.enqueue(new TextEncoder().encode('{"type":"node"}\n'));
            controller.close();
          },
        }),
        ok: true,
      });

      const promise = builder.loadFromStream('/api/v1/projects/test/graph/stream', {});

      // Abort after 100ms
      setTimeout(() => {
        builder.abort();
      }, 100);

      await expect(promise).rejects.toThrow();
    });
  });

  describe('State management', () => {
    it('tracks node and edge counts', () => {
      const builder = new IncrementalGraphBuilder();

      builder.addNode({
        data: {},
        id: 'n1',
        label: 'N1',
        position: { x: 0, y: 0 },
        type: 'test',
      });
      builder.addNode({
        data: {},
        id: 'n2',
        label: 'N2',
        position: { x: 0, y: 0 },
        type: 'test',
      });
      builder.addEdge({
        id: 'e1',
        label: 'Link',
        sourceId: 'n1',
        targetId: 'n2',
        type: 'link',
      });

      const stats = builder.getStats();

      expect(stats.nodeCount).toBe(2);
      expect(stats.edgeCount).toBe(1);
      expect(stats.isComplete).toBeFalsy();
    });

    it('resets state correctly', () => {
      const builder = new IncrementalGraphBuilder();

      builder.addNode({
        data: {},
        id: 'n1',
        label: 'N1',
        position: { x: 0, y: 0 },
        type: 'test',
      });
      builder.reset();

      const stats = builder.getStats();

      expect(stats.nodeCount).toBe(0);
      expect(stats.edgeCount).toBe(0);
    });

    it('checks node existence', () => {
      const builder = new IncrementalGraphBuilder();

      builder.addNode({
        data: {},
        id: 'n1',
        label: 'N1',
        position: { x: 0, y: 0 },
        type: 'test',
      });

      expect(builder.hasNode('n1')).toBeTruthy();
      expect(builder.hasNode('n2')).toBeFalsy();
    });

    it('retrieves nodes by ID', () => {
      const builder = new IncrementalGraphBuilder();

      const node = {
        data: {},
        id: 'n1',
        label: 'N1',
        position: { x: 0, y: 0 },
        type: 'test',
      };
      builder.addNode(node);

      expect(builder.getNode('n1')).toEqual(node);
      expect(builder.getNode('n2')).toBeUndefined();
    });
  });
});

describe(useIncrementalGraph, () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with correct state', () => {
    const { result } = renderHook(() =>
      useIncrementalGraph({
        projectId: 'test-project',
        viewport: { maxX: 1000, maxY: 1000, minX: 0, minY: 0 },
      }),
    );

    expect(result.current.state.nodes).toEqual([]);
    expect(result.current.state.edges).toEqual([]);
    expect(result.current.state.isLoading).toBeFalsy();
  });

  it('loads graph data', async () => {
    const mockStreamData = [
      {
        data: {
          data: {},
          id: 'n1',
          label: 'Node 1',
          position: { x: 0, y: 0 },
          type: 'test',
        },
        timestamp: Date.now(),
        type: 'node',
      },
      { data: {}, timestamp: Date.now(), type: 'complete' },
    ];

    globalThis.fetch = vi.fn().mockResolvedValue({
      body: new ReadableStream({
        start(controller) {
          const ndjson = mockStreamData.map((c) => JSON.stringify(c)).join('\n');
          controller.enqueue(new TextEncoder().encode(ndjson));
          controller.close();
        },
      }),
      ok: true,
    });

    const { result } = renderHook(() =>
      useIncrementalGraph({
        projectId: 'test-project',
        viewport: { maxX: 1000, maxY: 1000, minX: 0, minY: 0 },
      }),
    );

    // Trigger load
    result.current.loadGraph();

    // Wait for loading to complete
    await waitFor(() => {
      expect(result.current.state.isLoading).toBeFalsy();
    });

    expect(result.current.state.nodes.length).toBeGreaterThan(0);
  });

  it('handles errors', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Server Error',
    });

    const { result } = renderHook(() =>
      useIncrementalGraph({
        projectId: 'test-project',
        viewport: { maxX: 1000, maxY: 1000, minX: 0, minY: 0 },
      }),
    );

    result.current.loadGraph();

    await waitFor(() => {
      expect(result.current.state.error).toBeDefined();
    });
  });

  it('supports cancellation', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      body: new ReadableStream({
        async start(controller) {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          controller.close();
        },
      }),
      ok: true,
    });

    const { result } = renderHook(() =>
      useIncrementalGraph({
        projectId: 'test-project',
        viewport: { maxX: 1000, maxY: 1000, minX: 0, minY: 0 },
      }),
    );

    result.current.loadGraph();

    // Wait for loading to start
    await waitFor(() => {
      expect(result.current.state.isLoading).toBeTruthy();
    });

    // Abort
    result.current.abort();

    expect(result.current.state.isLoading).toBeFalsy();
  });
});

describe('Prefetch functionality', () => {
  it('calculates pan direction correctly', async () => {
    const { calculatePanDirection } = await import('../../hooks/useIncrementalGraph');

    const oldViewport = { maxX: 1000, maxY: 1000, minX: 0, minY: 0 };

    // East
    expect(
      calculatePanDirection(oldViewport, {
        maxX: 1100,
        maxY: 1000,
        minX: 100,
        minY: 0,
      }),
    ).toBe('east');

    // West
    expect(
      calculatePanDirection(oldViewport, {
        maxX: 900,
        maxY: 1000,
        minX: -100,
        minY: 0,
      }),
    ).toBe('west');

    // North
    expect(
      calculatePanDirection(oldViewport, {
        maxX: 1000,
        maxY: 900,
        minX: 0,
        minY: -100,
      }),
    ).toBe('north');

    // South
    expect(
      calculatePanDirection(oldViewport, {
        maxX: 1000,
        maxY: 1100,
        minX: 0,
        minY: 100,
      }),
    ).toBe('south');
  });

  it('calculates pan velocity', async () => {
    const { calculatePanVelocity } = await import('../../hooks/useIncrementalGraph');

    const oldViewport = { maxX: 1000, maxY: 1000, minX: 0, minY: 0 };
    const newViewport = { maxX: 1100, maxY: 1000, minX: 100, minY: 0 };

    // 100px in 100ms = 1000px/s
    const velocity = calculatePanVelocity(oldViewport, newViewport, 100);

    expect(velocity).toBe(1000);
  });
});

describe('Edge cases', () => {
  it('handles empty graph', async () => {
    const builder = new IncrementalGraphBuilder();

    builder.processChunk({
      data: { totalEdges: 0, totalNodes: 0 },
      timestamp: Date.now(),
      type: 'complete',
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
        data: null,
        timestamp: Date.now(),
        type: 'invalid',
      } as any);
    }).not.toThrow();
  });

  it('handles duplicate nodes', () => {
    const builder = new IncrementalGraphBuilder();

    const node = {
      data: {},
      id: 'n1',
      label: 'Node 1',
      position: { x: 0, y: 0 },
      type: 'test',
    };

    builder.addNode(node);
    builder.addNode(node); // Duplicate

    expect(builder.getStats().nodeCount).toBe(1); // Should overwrite
  });
});
