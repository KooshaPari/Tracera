/**
 * Graph Layout Worker Integration Tests
 *
 * These tests verify the implementation exists and is correctly structured.
 * Actual worker execution is tested in E2E tests due to jsdom limitations.
 *
 * @module graphLayoutWorker.integration.test
 */

import { describe, expect, it } from 'vitest';

describe('Graph Layout Worker Implementation', () => {
  describe('Worker Module', () => {
    it('should have graphLayout.worker.ts file', async () => {
      // Verify the worker file can be imported as a module
      const workerModule = await import('../../workers/graphLayout.worker');

      expect(workerModule).toBeDefined();
      expect(workerModule.computeLayout).toBeDefined();
      expect(workerModule.computeLayoutProgressive).toBeDefined();
      expect(workerModule.benchmarkLayout).toBeDefined();
    });

    it('should export correct type definitions', async () => {
      const workerModule = await import('../../workers/graphLayout.worker');

      // Type definitions should be available
      expect(typeof workerModule.computeLayout).toBe('function');
      expect(typeof workerModule.computeLayoutProgressive).toBe('function');
      expect(typeof workerModule.benchmarkLayout).toBe('function');
    });
  });

  describe('Hook Module', () => {
    it('should have useGraphLayoutWorker hook', async () => {
      const hookModule = await import('../../hooks/useGraphLayoutWorker');

      expect(hookModule).toBeDefined();
      expect(hookModule.useGraphLayoutWorker).toBeDefined();
      expect(typeof hookModule.useGraphLayoutWorker).toBe('function');
    });

    it('should export benchmark hook', async () => {
      const hookModule = await import('../../hooks/useGraphLayoutWorker');

      expect(hookModule.useGraphLayoutBenchmark).toBeDefined();
      expect(typeof hookModule.useGraphLayoutBenchmark).toBe('function');
    });
  });

  describe('Comlink Integration', () => {
    it('should have comlink installed', async () => {
      const comlink = await import('comlink');

      expect(comlink).toBeDefined();
      expect(comlink.wrap).toBeDefined();
      expect(comlink.expose).toBeDefined();
    });
  });

  describe('Layout Algorithm Support', () => {
    it('should support multiple layout algorithms', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      // Test with empty graph to verify function signatures
      const emptyResult = await computeLayout([], [], { algorithm: 'dagre' });
      expect(emptyResult).toEqual({
        positions: {},
        size: { height: 0, width: 0 },
      });
    });

    it('should support Dagre layout algorithm', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
      ];

      const edges = [{ id: 'e1', source: '1', target: '2' }];

      const result = await computeLayout(nodes, edges, {
        algorithm: 'dagre',
        direction: 'TB',
      });

      expect(result.positions).toBeDefined();
      expect(result.positions['1']).toBeDefined();
      expect(result.positions['2']).toBeDefined();
      expect(result.size).toBeDefined();
    });

    it.skip('should support ELK layout algorithm (requires browser environment)', async () => {
      // ELK requires Web Workers which are not fully supported in jsdom
      // This test should be run in E2E tests or browser environment
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
      ];

      const edges = [{ id: 'e1', source: '1', target: '2' }];

      const result = await computeLayout(nodes, edges, {
        algorithm: 'elk',
        direction: 'TB',
      });

      expect(result.positions).toBeDefined();
      expect(Object.keys(result.positions).length).toBeGreaterThan(0);
    });

    it('should support Grid layout algorithm', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
        { height: 50, id: '3', width: 100 },
        { height: 50, id: '4', width: 100 },
      ];

      const result = await computeLayout(nodes, [], {
        algorithm: 'grid',
      });

      expect(Object.keys(result.positions).length).toBe(4);
    });

    it('should support Circular layout algorithm', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
        { height: 50, id: '3', width: 100 },
      ];

      const result = await computeLayout(nodes, [], {
        algorithm: 'circular',
      });

      expect(Object.keys(result.positions).length).toBe(3);
    });

    it('should support Force layout algorithm', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
      ];

      const edges = [{ id: 'e1', source: '1', target: '2' }];

      const result = await computeLayout(nodes, edges, {
        algorithm: 'd3-force',
      });

      expect(Object.keys(result.positions).length).toBe(2);
    });

    it('should support Radial layout algorithm', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
        { height: 50, id: '3', width: 100 },
      ];

      const edges = [
        { id: 'e1', source: '1', target: '2' },
        { id: 'e2', source: '1', target: '3' },
      ];

      const result = await computeLayout(nodes, edges, {
        algorithm: 'radial',
      });

      expect(Object.keys(result.positions).length).toBe(3);
    });
  });

  describe('Progressive Layout', () => {
    it('should support progressive layout', async () => {
      const { computeLayoutProgressive } = await import('../../workers/graphLayout.worker');

      const nodes = Array.from({ length: 100 }, (_, i) => ({
        height: 50,
        id: `${i}`,
        width: 100,
      }));

      const generator = computeLayoutProgressive(nodes, [], {
        algorithm: 'grid',
        batchSize: 50,
        progressive: true,
      });

      let results = 0;
      for await (const _result of generator) {
        results++;
      }

      expect(results).toBeGreaterThan(0);
    });
  });

  describe('Benchmark API', () => {
    it('should support benchmarking', async () => {
      const { benchmarkLayout } = await import('../../workers/graphLayout.worker');

      const nodes = Array.from({ length: 10 }, (_, i) => ({
        height: 50,
        id: `${i}`,
        width: 100,
      }));

      const edges = Array.from({ length: 9 }, (_, i) => ({
        id: `e${i}`,
        source: `${i}`,
        target: `${i + 1}`,
      }));

      const benchmark = await benchmarkLayout(nodes, edges, {
        algorithm: 'grid',
        iterations: 3,
      });

      expect(benchmark.algorithm).toBe('grid');
      expect(benchmark.nodeCount).toBe(10);
      expect(benchmark.iterations).toBe(3);
      expect(benchmark.avgTime).toBeGreaterThan(0);
    });
  });

  describe('Layout Options', () => {
    it('should support different directions', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
      ];

      const edges = [{ id: 'e1', source: '1', target: '2' }];

      const directions = ['TB', 'LR', 'BT', 'RL'] as const;

      for (const direction of directions) {
        const result = await computeLayout(nodes, edges, {
          algorithm: 'dagre',
          direction,
        });

        expect(result.positions).toBeDefined();
        expect(Object.keys(result.positions).length).toBe(2);
      }
    });

    it('should support custom spacing options', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = [
        { height: 50, id: '1', width: 100 },
        { height: 50, id: '2', width: 100 },
      ];

      const result = await computeLayout(nodes, [], {
        algorithm: 'grid',
        marginX: 50,
        marginY: 50,
        nodeSep: 100,
        rankSep: 150,
      });

      expect(result.positions).toBeDefined();
      expect(result.size.width).toBeGreaterThan(0);
      expect(result.size.height).toBeGreaterThan(0);
    });
  });

  describe('Performance Characteristics', () => {
    it('should complete layout quickly for small graphs', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = Array.from({ length: 50 }, (_, i) => ({
        height: 50,
        id: `${i}`,
        width: 100,
      }));

      const edges = Array.from({ length: 49 }, (_, i) => ({
        id: `e${i}`,
        source: `${i}`,
        target: `${i + 1}`,
      }));

      const start = performance.now();
      await computeLayout(nodes, edges, { algorithm: 'dagre' });
      const duration = performance.now() - start;

      // Should complete in less than 1 second for 50 nodes
      expect(duration).toBeLessThan(1000);
    });

    it('should handle large graphs efficiently with grid layout', async () => {
      const { computeLayout } = await import('../../workers/graphLayout.worker');

      const nodes = Array.from({ length: 500 }, (_, i) => ({
        height: 50,
        id: `${i}`,
        width: 100,
      }));

      const start = performance.now();
      await computeLayout(nodes, [], { algorithm: 'grid' });
      const duration = performance.now() - start;

      // Grid layout should be very fast
      expect(duration).toBeLessThan(500);
    });
  });
});
