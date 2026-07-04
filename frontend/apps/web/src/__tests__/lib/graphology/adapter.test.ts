import type { Node, Edge } from '@xyflow/react';

import { describe, it, expect, beforeEach } from 'vitest';

import { GraphologyDataAdapter } from '@/lib/graphology/adapter';

describe('GraphologyDataAdapter', () => {
  let adapter: GraphologyDataAdapter;

  beforeEach(() => {
    adapter = new GraphologyDataAdapter();
  });

  describe('syncFromReactFlow', () => {
    it('should sync nodes from ReactFlow format', () => {
      const nodes: Node[] = [
        {
          id: 'node1',
          type: 'default',
          position: { x: 100, y: 200 },
          data: { label: 'Node 1' },
        },
        {
          id: 'node2',
          type: 'default',
          position: { x: 300, y: 400 },
          data: { label: 'Node 2' },
        },
      ];

      adapter.syncFromReactFlow(nodes, []);

      expect(adapter.getNodeCount()).toBe(2);
      expect(adapter.getGraph().hasNode('node1')).toBe(true);
      expect(adapter.getGraph().hasNode('node2')).toBe(true);
    });

    it('should sync edges from ReactFlow format', () => {
      const nodes: Node[] = [
        { id: 'node1', type: 'default', position: { x: 0, y: 0 }, data: {} },
        { id: 'node2', type: 'default', position: { x: 0, y: 0 }, data: {} },
      ];

      const edges: Edge[] = [{ id: 'edge1', source: 'node1', target: 'node2' }];

      adapter.syncFromReactFlow(nodes, edges);

      expect(adapter.getEdgeCount()).toBe(1);
      expect(adapter.getGraph().hasEdge('node1', 'node2')).toBe(true);
    });

    it('should skip edges with missing nodes', () => {
      const nodes: Node[] = [{ id: 'node1', type: 'default', position: { x: 0, y: 0 }, data: {} }];

      const edges: Edge[] = [
        { id: 'edge1', source: 'node1', target: 'node2' }, // node2 doesn't exist
      ];

      adapter.syncFromReactFlow(nodes, edges);

      expect(adapter.getEdgeCount()).toBe(0);
    });

    it('should preserve node positions', () => {
      const nodes: Node[] = [
        {
          id: 'node1',
          type: 'default',
          position: { x: 123, y: 456 },
          data: { label: 'Test' },
        },
      ];

      adapter.syncFromReactFlow(nodes, []);

      const attrs = adapter.getGraph().getNodeAttributes('node1');
      expect(attrs.x).toBe(123);
      expect(attrs.y).toBe(456);
    });
  });

  describe('toReactFlow', () => {
    it('should convert back to ReactFlow format', () => {
      const nodes: Node[] = [
        {
          id: 'node1',
          type: 'test',
          position: { x: 100, y: 200 },
          data: { label: 'Node 1', custom: 'data' },
        },
      ];

      const edges: Edge[] = [{ id: 'edge1', source: 'node1', target: 'node1' }];

      adapter.syncFromReactFlow(nodes, edges);
      const result = adapter.toReactFlow();

      expect(result.nodes).toHaveLength(1);
      expect(result.nodes[0].id).toBe('node1');
      expect(result.nodes[0].position.x).toBe(100);
      expect(result.nodes[0].data.label).toBe('Node 1');

      expect(result.edges).toHaveLength(1);
      expect(result.edges[0].source).toBe('node1');
    });
  });

  describe('cluster', () => {
    it('should detect communities using Louvain', async () => {
      // Create a simple graph with 2 communities
      const nodes: Node[] = [
        { id: 'a1', type: 'default', position: { x: 0, y: 0 }, data: {} },
        { id: 'a2', type: 'default', position: { x: 0, y: 0 }, data: {} },
        { id: 'b1', type: 'default', position: { x: 0, y: 0 }, data: {} },
        { id: 'b2', type: 'default', position: { x: 0, y: 0 }, data: {} },
      ];

      const edges: Edge[] = [
        { id: 'e1', source: 'a1', target: 'a2' }, // Community A
        { id: 'e2', source: 'b1', target: 'b2' }, // Community B
        { id: 'e3', source: 'a2', target: 'b1' }, // Weak connection
      ];

      adapter.syncFromReactFlow(nodes, edges);
      const communities = await adapter.cluster();

      expect(communities.size).toBe(4);
      // a1 and a2 should be in same community
      expect(communities.get('a1')).toBe(communities.get('a2'));
    });
  });

  describe('computeLayout', () => {
    it('should compute ForceAtlas2 layout', async () => {
      // Use different starting positions so forces can act
      const nodes: Node[] = [
        { id: 'node1', type: 'default', position: { x: 0, y: 0 }, data: {} },
        { id: 'node2', type: 'default', position: { x: 100, y: 0 }, data: {} },
        { id: 'node3', type: 'default', position: { x: 50, y: 100 }, data: {} },
      ];

      const edges: Edge[] = [
        { id: 'edge1', source: 'node1', target: 'node2' },
        { id: 'edge2', source: 'node2', target: 'node3' },
      ];

      adapter.syncFromReactFlow(nodes, edges);

      const beforeX = adapter.getGraph().getNodeAttribute('node1', 'x');
      const beforeY = adapter.getGraph().getNodeAttribute('node1', 'y');

      // Run layout computation
      await adapter.computeLayout(100);

      const afterX = adapter.getGraph().getNodeAttribute('node1', 'x');
      const afterY = adapter.getGraph().getNodeAttribute('node1', 'y');

      // Position should have changed
      expect(afterX).not.toBe(beforeX);
      expect(afterY).not.toBe(beforeY);
    });
  });

  describe('clear', () => {
    it('should clear all nodes and edges', () => {
      const nodes: Node[] = [{ id: 'node1', type: 'default', position: { x: 0, y: 0 }, data: {} }];

      adapter.syncFromReactFlow(nodes, []);
      expect(adapter.getNodeCount()).toBe(1);

      adapter.clear();
      expect(adapter.getNodeCount()).toBe(0);
      expect(adapter.getEdgeCount()).toBe(0);
    });
  });

  describe('getCommunityStats', () => {
    it('should calculate community statistics', async () => {
      const communities = new Map([
        ['node1', 0],
        ['node2', 0],
        ['node3', 1],
        ['node4', 1],
        ['node5', 1],
      ]);

      const stats = await adapter.getCommunityStats(communities);

      expect(stats.communityCount).toBe(2);
      expect(stats.sizes.get(0)).toBe(2);
      expect(stats.sizes.get(1)).toBe(3);
      expect(stats.largestCommunity).toBe(3);
    });
  });
});
