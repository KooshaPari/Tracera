/**
 * GraphologyDataLayer Unit Tests
 */

import type { Edge, Node } from '@xyflow/react';

import { beforeEach, describe, expect, it } from 'vitest';

import {
  GraphologyDataLayer,
  createGraphologyDataLayer,
  getGraphologyDataLayer,
  resetGraphologyDataLayer,
} from '../GraphologyDataLayer';

describe('GraphologyDataLayer', () => {
  let dataLayer: GraphologyDataLayer;

  beforeEach(() => {
    resetGraphologyDataLayer();
    dataLayer = createGraphologyDataLayer();
  });

  describe('Initialization', () => {
    it('should create an empty graph', () => {
      const graph = dataLayer.getGraph();
      expect(graph.order).toBe(0);
      expect(graph.size).toBe(0);
    });

    it('should initialize from ReactFlow data', async () => {
      const nodes: Node[] = [
        {
          data: { label: 'Node 1' },
          id: 'node1',
          position: { x: 0, y: 0 },
          type: 'default',
        },
        {
          data: { label: 'Node 2' },
          id: 'node2',
          position: { x: 100, y: 100 },
          type: 'default',
        },
      ];

      const edges: Edge[] = [
        {
          id: 'edge1',
          source: 'node1',
          target: 'node2',
          type: 'default',
        },
      ];

      await dataLayer.initialize(nodes, edges);

      expect(dataLayer.getGraph().order).toBe(2);
      expect(dataLayer.getGraph().size).toBe(1);
    });

    it('should track performance metrics', async () => {
      const nodes: Node[] = [
        {
          data: { label: 'Node 1' },
          id: 'node1',
          position: { x: 0, y: 0 },
          type: 'default',
        },
      ];

      await dataLayer.initialize(nodes, []);

      const metrics = dataLayer.getPerformanceMetrics();
      expect(metrics.initializationTime).toBeGreaterThan(0);
      expect(metrics.nodeCount).toBe(1);
      expect(metrics.edgeCount).toBe(0);
    });
  });

  describe('Node Operations', () => {
    it('should add a node', () => {
      const node: Node = {
        data: { color: '#ff0000', label: 'Node 1' },
        id: 'node1',
        position: { x: 0, y: 0 },
        type: 'default',
      };

      dataLayer.addNode(node);

      expect(dataLayer.getGraph().hasNode('node1')).toBe(true);
      const attrs = dataLayer.getGraph().getNodeAttributes('node1');
      expect(attrs['label']).toBe('Node 1');
      expect(attrs['color']).toBe('#ff0000');
    });

    it('should update existing node', () => {
      const node: Node = {
        data: { label: 'Node 1' },
        id: 'node1',
        position: { x: 0, y: 0 },
        type: 'default',
      };

      dataLayer.addNode(node);
      dataLayer.updateNode('node1', { color: '#00ff00' });

      const attrs = dataLayer.getGraph().getNodeAttributes('node1');
      expect(attrs['color']).toBe('#00ff00');
    });

    it('should remove a node', () => {
      const node: Node = {
        data: { label: 'Node 1' },
        id: 'node1',
        position: { x: 0, y: 0 },
        type: 'default',
      };

      dataLayer.addNode(node);
      expect(dataLayer.getGraph().hasNode('node1')).toBe(true);

      dataLayer.removeNode('node1');
      expect(dataLayer.getGraph().hasNode('node1')).toBe(false);
    });

    it('should get node neighbors', async () => {
      const nodes: Node[] = [
        { data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: 'node2', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: 'node3', position: { x: 0, y: 0 }, type: 'default' },
      ];

      const edges: Edge[] = [
        { id: 'edge1', source: 'node1', target: 'node2' },
        { id: 'edge2', source: 'node1', target: 'node3' },
      ];

      await dataLayer.initialize(nodes, edges);

      const neighbors = dataLayer.getNeighbors('node1');
      expect(neighbors).toHaveLength(2);
      expect(neighbors).toContain('node2');
      expect(neighbors).toContain('node3');
    });
  });

  describe('Edge Operations', () => {
    beforeEach(async () => {
      const nodes: Node[] = [
        { data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: 'node2', position: { x: 0, y: 0 }, type: 'default' },
      ];
      await dataLayer.initialize(nodes, []);
    });

    it('should add an edge', () => {
      const edge: Edge = {
        data: { weight: 5 },
        id: 'edge1',
        source: 'node1',
        target: 'node2',
        type: 'default',
      };

      dataLayer.addEdge(edge);

      expect(dataLayer.getGraph().hasEdge('node1', 'node2')).toBe(true);
      const attrs = dataLayer.getGraph().getEdgeAttributes('node1', 'node2');
      expect(attrs['weight']).toBe(5);
    });

    it('should skip edges with missing nodes', () => {
      const edge: Edge = {
        id: 'edge1',
        source: 'node1',
        target: 'nonexistent',
        type: 'default',
      };

      dataLayer.addEdge(edge);

      expect(dataLayer.getGraph().size).toBe(0);
    });

    it('should update existing edge', () => {
      const edge: Edge = {
        id: 'edge1',
        source: 'node1',
        target: 'node2',
        type: 'default',
      };

      dataLayer.addEdge(edge);
      dataLayer.updateEdge('node1', 'node2', { weight: 10 });

      const attrs = dataLayer.getGraph().getEdgeAttributes('node1', 'node2');
      expect(attrs['weight']).toBe(10);
    });
  });

  describe('ReactFlow Conversion', () => {
    it('should convert to ReactFlow format', async () => {
      const nodes: Node[] = [
        {
          data: { color: '#ff0000', label: 'Node 1' },
          id: 'node1',
          position: { x: 100, y: 200 },
          type: 'custom',
        },
        {
          data: { label: 'Node 2' },
          id: 'node2',
          position: { x: 300, y: 400 },
          type: 'default',
        },
      ];

      const edges: Edge[] = [
        {
          id: 'edge1',
          label: 'connects',
          source: 'node1',
          target: 'node2',
          type: 'default',
        },
      ];

      await dataLayer.initialize(nodes, edges);

      const result = dataLayer.toReactFlow();

      expect(result.nodes).toHaveLength(2);
      expect(result.edges).toHaveLength(1);

      const node1 = result.nodes.find((node) => node.id === 'node1');
      expect(node1).toBeDefined();
      if (!node1) {
        throw new Error('Expected node1 to exist.');
      }
      expect(node1.type).toBe('custom');
      expect(node1.position.x).toBe(100);
      expect(node1.data['color']).toBe('#ff0000');

      const [edge1] = result.edges;
      if (!edge1) {
        throw new Error('Expected edge1 to exist.');
      }
      expect(edge1.source).toBe('node1');
      expect(edge1.target).toBe('node2');
      expect(edge1.label).toBe('connects');
    });

    it('should preserve all node attributes', async () => {
      const nodes: Node[] = [
        {
          data: {
            customProp: 'value',
            label: 'Node 1',
            nested: { key: 'value' },
          },
          id: 'node1',
          position: { x: 0, y: 0 },
          type: 'default',
        },
      ];

      await dataLayer.initialize(nodes, []);

      const result = dataLayer.toReactFlow();
      const [node1] = result.nodes;
      if (!node1) {
        throw new Error('Expected node1 to exist.');
      }

      expect(node1.data['customProp']).toBe('value');
      expect(node1.data['nested']).toEqual({ key: 'value' });
    });
  });

  describe('Layout Computation', () => {
    beforeEach(async () => {
      const nodes: Node[] = Array.from({ length: 10 }, (_, i) => ({
        data: { label: `Node ${i}` },
        id: `node${i}`,
        position: { x: 0, y: 0 },
        type: 'default',
      }));

      const edges: Edge[] = Array.from({ length: 9 }, (_, i) => ({
        id: `edge${i}`,
        source: `node${i}`,
        target: `node${i + 1}`,
      }));

      await dataLayer.initialize(nodes, edges);
    });

    it('should compute ForceAtlas2 layout', async () => {
      await dataLayer.computeLayout({
        algorithm: 'forceAtlas2',
        iterations: 100,
      });

      const metrics = dataLayer.getPerformanceMetrics();
      expect(metrics.layoutTime).toBeGreaterThan(0);

      // Check that positions were updated
      const node = dataLayer.getGraph().getNodeAttributes('node0');
      expect(node['x']).toBeDefined();
      expect(node['y']).toBeDefined();
    });

    it('should compute circular layout', async () => {
      await dataLayer.computeLayout({
        algorithm: 'circular',
      });

      const metrics = dataLayer.getPerformanceMetrics();
      expect(metrics.layoutTime).toBeGreaterThan(0);
    });

    it('should compute random layout', async () => {
      await dataLayer.computeLayout({
        algorithm: 'random',
      });

      const metrics = dataLayer.getPerformanceMetrics();
      expect(metrics.layoutTime).toBeGreaterThan(0);
    });

    it('should throw error for unknown layout', async () => {
      await expect(
        dataLayer.computeLayout({
          algorithm: 'unknown' as any,
        }),
      ).rejects.toThrow('Unknown layout algorithm');
    });
  });

  describe('Community Detection', () => {
    it('should detect communities', async () => {
      const nodes: Node[] = Array.from({ length: 20 }, (_, i) => ({
        data: { label: `Node ${i}` },
        id: `node${i}`,
        position: { x: 0, y: 0 },
        type: 'default',
      }));

      const edges: Edge[] = [];
      // Create two separate communities
      for (let i = 0; i < 9; i += 1) {
        edges.push({
          id: `edge-a-${i}`,
          source: `node${i}`,
          target: `node${i + 1}`,
        });
      }
      for (let i = 10; i < 19; i += 1) {
        edges.push({
          id: `edge-b-${i}`,
          source: `node${i}`,
          target: `node${i + 1}`,
        });
      }

      await dataLayer.initialize(nodes, edges);

      const communities = await dataLayer.detectCommunities();

      expect(communities.size).toBeGreaterThan(0);
      expect(dataLayer.getCommunities()).toBe(communities);
    });
  });

  describe('Statistics', () => {
    it('should compute graph statistics', async () => {
      const nodes: Node[] = [
        { data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: 'node2', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: 'node3', position: { x: 0, y: 0 }, type: 'default' },
      ];

      const edges: Edge[] = [
        { id: 'edge1', source: 'node1', target: 'node2' },
        { id: 'edge2', source: 'node2', target: 'node3' },
      ];

      await dataLayer.initialize(nodes, edges);

      const stats = dataLayer.getStats();

      expect(stats.nodeCount).toBe(3);
      expect(stats.edgeCount).toBe(2);
      expect(stats.density).toBeGreaterThan(0);
      expect(stats.averageDegree).toBeGreaterThan(0);
    });

    it('should get node degree metrics', async () => {
      const nodes: Node[] = [
        { data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: 'node2', position: { x: 0, y: 0 }, type: 'default' },
        { data: {}, id: 'node3', position: { x: 0, y: 0 }, type: 'default' },
      ];

      const edges: Edge[] = [
        { id: 'edge1', source: 'node1', target: 'node2' },
        { id: 'edge2', source: 'node1', target: 'node3' },
      ];

      await dataLayer.initialize(nodes, edges);

      expect(dataLayer.getNodeDegree('node1')).toBe(2);
      expect(dataLayer.getNodeOutDegree('node1')).toBe(2);
      expect(dataLayer.getNodeInDegree('node1')).toBe(0);

      expect(dataLayer.getNodeDegree('node2')).toBe(1);
      expect(dataLayer.getNodeInDegree('node2')).toBe(1);
    });
  });

  describe('Import/Export', () => {
    it('should export to JSON', async () => {
      const nodes: Node[] = [{ data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' }];

      await dataLayer.initialize(nodes, []);

      const json = dataLayer.exportJSON();

      expect(json).toBeDefined();
      expect(json.nodes).toBeDefined();
    });

    it('should import from JSON', async () => {
      const nodes: Node[] = [{ data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' }];

      await dataLayer.initialize(nodes, []);
      const json = dataLayer.exportJSON();

      const newLayer = createGraphologyDataLayer();
      newLayer.importJSON(json);

      expect(newLayer.getGraph().order).toBe(1);
      expect(newLayer.getGraph().hasNode('node1')).toBe(true);
    });
  });

  describe('Clear', () => {
    it('should clear the graph', async () => {
      const nodes: Node[] = [{ data: {}, id: 'node1', position: { x: 0, y: 0 }, type: 'default' }];

      await dataLayer.initialize(nodes, []);
      expect(dataLayer.getGraph().order).toBe(1);

      dataLayer.clear();
      expect(dataLayer.getGraph().order).toBe(0);

      const metrics = dataLayer.getPerformanceMetrics();
      expect(metrics.initializationTime).toBe(0);
    });
  });

  describe('Factory Functions', () => {
    it('should create instance via factory', () => {
      const instance = createGraphologyDataLayer();
      expect(instance).toBeInstanceOf(GraphologyDataLayer);
    });

    it('should provide singleton instance', () => {
      const instance1 = getGraphologyDataLayer();
      const instance2 = getGraphologyDataLayer();
      expect(instance1).toBe(instance2);
    });

    it('should reset singleton instance', () => {
      const instance1 = getGraphologyDataLayer();
      resetGraphologyDataLayer();
      const instance2 = getGraphologyDataLayer();
      expect(instance1).not.toBe(instance2);
    });
  });
});
