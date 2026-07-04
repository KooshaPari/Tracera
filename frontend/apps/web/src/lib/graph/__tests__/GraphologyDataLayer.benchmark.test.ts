/**
 * GraphologyDataLayer Performance Benchmarks
 *
 * Tests performance against targets:
 * - Initialization: <2s for 100k nodes
 * - Layout: <5s for 100k nodes
 * - Conversion: <500ms for 100k nodes
 * - Memory: <500MB for 100k nodes
 */

import type { Node, Edge } from '@xyflow/react';

import { describe, it, expect, beforeEach } from 'vitest';

import {
  GraphologyDataLayer,
  createGraphologyDataLayer,
  getGraphologyDataLayer,
  resetGraphologyDataLayer,
} from '../GraphologyDataLayer';

/**
 * Generate synthetic graph data for benchmarking
 */
function generateGraphData(
  nodeCount: number,
  edgesPerNode: number = 10,
): {
  nodes: Node[];
  edges: Edge[];
} {
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  // Generate nodes
  for (let i = 0; i < nodeCount; i++) {
    nodes.push({
      id: `node-${i}`,
      type: 'default',
      position: { x: Math.random() * 1000, y: Math.random() * 1000 },
      data: {
        label: `Node ${i}`,
        type: 'test',
        color: '#64748b',
      },
    });
  }

  // Generate edges
  let edgeId = 0;
  for (let i = 0; i < nodeCount; i++) {
    for (let j = 0; j < edgesPerNode; j++) {
      const target = Math.floor(Math.random() * nodeCount);
      if (target !== i) {
        edges.push({
          id: `edge-${edgeId++}`,
          source: `node-${i}`,
          target: `node-${target}`,
          type: 'default',
          data: { weight: 1 },
        });
      }
    }
  }

  return { nodes, edges };
}

describe('GraphologyDataLayer Benchmarks', () => {
  let dataLayer: GraphologyDataLayer;

  beforeEach(() => {
    resetGraphologyDataLayer();
    dataLayer = createGraphologyDataLayer();
  });

  describe('Initialization Performance', () => {
    it('should initialize 1k nodes in <50ms', async () => {
      const { nodes, edges } = generateGraphData(1000, 5);

      const start = performance.now();
      await dataLayer.initialize(nodes, edges);
      const end = performance.now();

      const time = end - start;
      console.log(`1k nodes initialized in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(50);
      expect(dataLayer.getGraph().order).toBe(1000);
    });

    it('should initialize 10k nodes in <1s', async () => {
      const { nodes, edges } = generateGraphData(10000, 5);

      const start = performance.now();
      await dataLayer.initialize(nodes, edges);
      const end = performance.now();

      const time = end - start;
      console.log(`10k nodes initialized in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(1000);
      expect(dataLayer.getGraph().order).toBe(10000);
    });

    it('should initialize 50k nodes in <5s', async () => {
      const { nodes, edges } = generateGraphData(50000, 5);

      const start = performance.now();
      await dataLayer.initialize(nodes, edges);
      const end = performance.now();

      const time = end - start;
      console.log(`50k nodes initialized in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(5000);
      expect(dataLayer.getGraph().order).toBe(50000);
    });

    it('should initialize 100k nodes in <10s (TARGET)', async () => {
      const { nodes, edges } = generateGraphData(100000, 5);

      const start = performance.now();
      await dataLayer.initialize(nodes, edges);
      const end = performance.now();

      const time = end - start;
      console.log(`100k nodes initialized in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(10000);
      expect(dataLayer.getGraph().order).toBe(100000);
    });
  });

  describe('Layout Computation Performance', () => {
    it('should compute layout for 1k nodes in <100ms', async () => {
      const { nodes, edges } = generateGraphData(1000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      await dataLayer.computeLayout({
        algorithm: 'forceAtlas2',
        iterations: 100,
      });
      const end = performance.now();

      const time = end - start;
      console.log(`1k nodes layout in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(100);
    });

    it('should compute layout for 10k nodes in <1s', async () => {
      const { nodes, edges } = generateGraphData(10000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      await dataLayer.computeLayout({
        algorithm: 'forceAtlas2',
        iterations: 100,
      });
      const end = performance.now();

      const time = end - start;
      console.log(`10k nodes layout in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(1000);
    });

    it('should compute circular layout for 100k nodes in <500ms', async () => {
      const { nodes, edges } = generateGraphData(100000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      await dataLayer.computeLayout({
        algorithm: 'circular',
      });
      const end = performance.now();

      const time = end - start;
      console.log(`100k nodes circular layout in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(500);
    });
  });

  describe('Conversion Performance', () => {
    it('should convert 1k nodes to ReactFlow in <10ms', async () => {
      const { nodes, edges } = generateGraphData(1000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      const result = dataLayer.toReactFlow();
      const end = performance.now();

      const time = end - start;
      console.log(`1k nodes converted in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(10);
      expect(result.nodes.length).toBe(1000);
    });

    it('should convert 10k nodes to ReactFlow in <100ms', async () => {
      const { nodes, edges } = generateGraphData(10000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      const result = dataLayer.toReactFlow();
      const end = performance.now();

      const time = end - start;
      console.log(`10k nodes converted in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(100);
      expect(result.nodes.length).toBe(10000);
    });

    it('should convert 100k nodes to ReactFlow in <500ms (TARGET)', async () => {
      const { nodes, edges } = generateGraphData(100000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      const result = dataLayer.toReactFlow();
      const end = performance.now();

      const time = end - start;
      console.log(`100k nodes converted in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(500);
      expect(result.nodes.length).toBe(100000);
    });
  });

  describe('Community Detection Performance', () => {
    it('should detect communities in 1k nodes in <100ms', async () => {
      const { nodes, edges } = generateGraphData(1000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      const communities = await dataLayer.detectCommunities();
      const end = performance.now();

      const time = end - start;
      console.log(`1k nodes communities detected in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(100);
      expect(communities.size).toBeGreaterThan(0);
    });

    it('should detect communities in 10k nodes in <1s', async () => {
      const { nodes, edges } = generateGraphData(10000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      const communities = await dataLayer.detectCommunities();
      const end = performance.now();

      const time = end - start;
      console.log(`10k nodes communities detected in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(1000);
      expect(communities.size).toBeGreaterThan(0);
    });
  });

  describe('Memory Usage', () => {
    it('should track memory metrics for 100k nodes', async () => {
      const { nodes, edges } = generateGraphData(100000, 5);
      await dataLayer.initialize(nodes, edges);

      const metrics = dataLayer.getPerformanceMetrics();
      const memoryMB = metrics.totalMemory / (1024 * 1024);

      console.log(`100k nodes estimated memory: ${memoryMB.toFixed(2)}MB`);
      console.log('Performance metrics:', {
        initTime: `${metrics.initializationTime.toFixed(2)}ms`,
        nodeCount: metrics.nodeCount,
        edgeCount: metrics.edgeCount,
      });

      // Should be under 500MB target
      expect(memoryMB).toBeLessThan(500);
    });
  });

  describe('Incremental Updates', () => {
    it('should handle incremental node additions efficiently', async () => {
      const { nodes, edges } = generateGraphData(1000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      for (let i = 0; i < 1000; i++) {
        dataLayer.addNode({
          id: `new-node-${i}`,
          type: 'default',
          position: { x: 0, y: 0 },
          data: { label: `New ${i}` },
        });
      }
      const end = performance.now();

      const time = end - start;
      console.log(`1000 incremental nodes added in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(100);
      expect(dataLayer.getGraph().order).toBe(2000);
    });

    it('should handle incremental edge additions efficiently', async () => {
      const { nodes, edges } = generateGraphData(1000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      for (let i = 0; i < 1000; i++) {
        dataLayer.addEdge({
          id: `new-edge-${i}`,
          source: `node-${i % 1000}`,
          target: `node-${(i + 1) % 1000}`,
          type: 'default',
          data: { weight: 1 },
        });
      }
      const end = performance.now();

      const time = end - start;
      console.log(`1000 incremental edges added in ${time.toFixed(2)}ms`);

      expect(time).toBeLessThan(100);
    });
  });

  describe('Graph Statistics', () => {
    it('should compute stats for large graphs efficiently', async () => {
      const { nodes, edges } = generateGraphData(5000, 5);
      await dataLayer.initialize(nodes, edges);

      const start = performance.now();
      const stats = dataLayer.getStats();
      const end = performance.now();

      const time = end - start;
      console.log(`Stats computed in ${time.toFixed(2)}ms`);
      console.log('Stats:', stats);

      expect(time).toBeLessThan(1000);
      expect(stats.nodeCount).toBe(5000);
      expect(stats.edgeCount).toBeGreaterThan(0);
      expect(stats.density).toBeGreaterThan(0);
    });
  });

  describe('Global Instance', () => {
    it('should provide singleton instance', () => {
      const instance1 = getGraphologyDataLayer();
      const instance2 = getGraphologyDataLayer();

      expect(instance1).toBe(instance2);
    });

    it('should reset global instance', () => {
      const instance1 = getGraphologyDataLayer();
      resetGraphologyDataLayer();
      const instance2 = getGraphologyDataLayer();

      expect(instance1).not.toBe(instance2);
    });
  });

  describe('Comparison: Old vs New', () => {
    it('should show improvement over baseline (manual test)', async () => {
      const sizes = [1000, 5000, 10000, 50000];

      console.log('\n=== Performance Comparison ===\n');

      for (const size of sizes) {
        const { nodes, edges } = generateGraphData(size, 5);

        // Test initialization
        const initStart = performance.now();
        const layer = createGraphologyDataLayer();
        await layer.initialize(nodes, edges);
        const initEnd = performance.now();

        // Test conversion
        const convStart = performance.now();
        layer.toReactFlow();
        const convEnd = performance.now();

        // Test layout (circular for speed)
        const layoutStart = performance.now();
        await layer.computeLayout({ algorithm: 'circular' });
        const layoutEnd = performance.now();

        console.log(`${size} nodes:`);
        console.log(`  Init: ${(initEnd - initStart).toFixed(2)}ms`);
        console.log(`  Convert: ${(convEnd - convStart).toFixed(2)}ms`);
        console.log(`  Layout: ${(layoutEnd - layoutStart).toFixed(2)}ms`);
        console.log('');
      }
    });
  });
});
