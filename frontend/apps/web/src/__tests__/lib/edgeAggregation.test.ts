/**
 * Edge Aggregation Tests
 * Validates edge reduction strategies for large graphs
 */

import { describe, expect, it } from 'vitest';

import type { LinkType } from '@tracertm/types';

import {
  aggregateParallelEdges,
  applyLazyEdgeRendering,
  createDefaultFilterConfig,
  createDefaultSamplingConfig,
  detectCanvasFallbackAreas,
  detectEdgeClusters,
  filterEdgesByType,
  getRelatedEdges,
  sampleEdgesByImportance,
  sampleEdgesStatistically,
  type EdgeBase,
  type Node,
} from '@/lib/edgeAggregation';

// Helper to create test edges
function createEdge(
  id: string,
  source: string,
  target: string,
  type: LinkType = 'implements',
): EdgeBase {
  return { id, source, target, type };
}

// Helper to create test nodes
function createNode(id: string, x: number, y: number): Node {
  return {
    id,
    position: { x, y },
  };
}

describe('Edge Aggregation', () => {
  describe('aggregateParallelEdges', () => {
    it('should aggregate parallel edges (same source→target)', () => {
      const edges = [
        createEdge('e1', 'A', 'B', 'implements'),
        createEdge('e2', 'A', 'B', 'tests'),
        createEdge('e3', 'A', 'B', 'depends_on'),
        createEdge('e4', 'C', 'D', 'implements'),
      ];

      const result = aggregateParallelEdges(edges, 2);

      // A→B should be aggregated (3 edges)
      // C→D should not be aggregated (1 edge)
      expect(result).toHaveLength(2);

      const aggEdge = result.find((e) => e._isAggregated);
      expect(aggEdge).toBeDefined();
      expect(aggEdge?._aggregatedCount).toBe(3);
      expect(aggEdge?.source).toBe('A');
      expect(aggEdge?.target).toBe('B');

      const normalEdge = result.find((e) => !e._isAggregated);
      expect(normalEdge).toBeDefined();
      expect(normalEdge?.source).toBe('C');
    });

    it('should not aggregate below threshold', () => {
      const edges = [createEdge('e1', 'A', 'B', 'implements'), createEdge('e2', 'C', 'D', 'tests')];

      const result = aggregateParallelEdges(edges, 2);

      expect(result).toHaveLength(2);
      expect(result.every((e) => !e._isAggregated)).toBe(true);
    });

    it('should set correct stroke width for aggregated edges', () => {
      const edges = Array.from({ length: 10 }, (_, i) =>
        createEdge(`e${i}`, 'A', 'B', 'implements'),
      );

      const result = aggregateParallelEdges(edges, 2);

      expect(result).toHaveLength(1);
      expect(result[0].strokeWidth).toBeGreaterThan(2);
      expect(result[0].strokeWidth).toBeLessThanOrEqual(8);
    });
  });

  describe('detectEdgeClusters', () => {
    it('should detect dense spatial clusters', () => {
      const nodes = [createNode('A', 0, 0), createNode('B', 10, 10), createNode('C', 20, 20)];

      // Create 15 edges in same area (should exceed threshold of 10)
      const edges = Array.from({ length: 15 }, (_, i) =>
        createEdge(`e${i}`, 'A', 'B', 'implements'),
      );

      const clusters = detectEdgeClusters(edges, nodes, 10);

      expect(clusters.length).toBeGreaterThan(0);
      expect(clusters[0].totalCount).toBeGreaterThanOrEqual(10);
    });

    it('should not detect clusters below threshold', () => {
      const nodes = [createNode('A', 0, 0), createNode('B', 10, 10)];

      const edges = [createEdge('e1', 'A', 'B', 'implements')];

      const clusters = detectEdgeClusters(edges, nodes, 10);

      expect(clusters).toHaveLength(0);
    });
  });

  describe('sampleEdgesStatistically', () => {
    it('should sample edges at specified ratio', () => {
      const edges = Array.from({ length: 1000 }, (_, i) =>
        createEdge(`e${i}`, 'A', 'B', 'implements'),
      );

      const result = sampleEdgesStatistically(edges, 0.1);

      // Should be approximately 10% (allow ±4% variance due to hashing)
      expect(result.length).toBeGreaterThan(60);
      expect(result.length).toBeLessThan(140);
    });

    it('should be deterministic (same results each call)', () => {
      const edges = Array.from({ length: 100 }, (_, i) =>
        createEdge(`e${i}`, 'A', 'B', 'implements'),
      );

      const result1 = sampleEdgesStatistically(edges, 0.1);
      const result2 = sampleEdgesStatistically(edges, 0.1);

      expect(result1.length).toBe(result2.length);
      expect(result1.map((e) => e.id)).toEqual(result2.map((e) => e.id));
    });
  });

  describe('sampleEdgesByImportance', () => {
    it('should prioritize important edge types', () => {
      const edges = [
        ...Array.from({ length: 50 }, (_, i) => createEdge(`priority${i}`, 'A', 'B', 'implements')),
        ...Array.from({ length: 50 }, (_, i) => createEdge(`normal${i}`, 'A', 'B', 'related_to')),
      ];

      const result = sampleEdgesByImportance(edges, 60, ['implements']);

      // Should include more priority edges
      const priorityCount = result.filter((e) => e.type === 'implements').length;
      const normalCount = result.filter((e) => e.type === 'related_to').length;

      expect(priorityCount).toBeGreaterThan(normalCount);
    });

    it('should respect max edge limit', () => {
      const edges = Array.from({ length: 1000 }, (_, i) =>
        createEdge(`e${i}`, 'A', 'B', 'implements'),
      );

      const result = sampleEdgesByImportance(edges, 100, ['implements']);

      expect(result.length).toBeLessThanOrEqual(100);
    });
  });

  describe('filterEdgesByType', () => {
    it('should filter edges by enabled types', () => {
      const edges = [
        createEdge('e1', 'A', 'B', 'implements'),
        createEdge('e2', 'A', 'B', 'tests'),
        createEdge('e3', 'A', 'B', 'depends_on'),
      ];

      const config = {
        enabledTypes: new Set<LinkType>(['implements', 'tests']),
        showRelatedForSelection: true,
        maxRelatedEdges: 100,
      };

      const result = filterEdgesByType(edges, config);

      expect(result).toHaveLength(2);
      expect(result.every((e) => ['implements', 'tests'].includes(e.type))).toBe(true);
    });

    it('should return all edges when no filter', () => {
      const edges = [createEdge('e1', 'A', 'B', 'implements'), createEdge('e2', 'A', 'B', 'tests')];

      const config = {
        enabledTypes: new Set<LinkType>(),
        showRelatedForSelection: true,
        maxRelatedEdges: 100,
      };

      const result = filterEdgesByType(edges, config);

      expect(result).toHaveLength(2);
    });
  });

  describe('getRelatedEdges', () => {
    it('should return edges connected to selected nodes', () => {
      const edges = [
        createEdge('e1', 'A', 'B', 'implements'),
        createEdge('e2', 'B', 'C', 'tests'),
        createEdge('e3', 'C', 'D', 'depends_on'),
      ];

      const selectedNodes = new Set(['B']);
      const result = getRelatedEdges(edges, selectedNodes, 100);

      // Should include e1 (A→B) and e2 (B→C)
      expect(result).toHaveLength(2);
      expect(result.some((e) => e.id === 'e1')).toBe(true);
      expect(result.some((e) => e.id === 'e2')).toBe(true);
    });

    it('should respect max edge limit', () => {
      const edges = Array.from({ length: 200 }, (_, i) =>
        createEdge(`e${i}`, 'A', 'B', 'implements'),
      );

      const selectedNodes = new Set(['A']);
      const result = getRelatedEdges(edges, selectedNodes, 50);

      expect(result.length).toBeLessThanOrEqual(50);
    });
  });

  describe('detectCanvasFallbackAreas', () => {
    it('should detect ultra-dense areas', () => {
      const nodes = [createNode('A', 0, 0), createNode('B', 10, 10)];

      // Create 1000 edges in small area to ensure high density
      const edges = Array.from({ length: 1000 }, (_, i) =>
        createEdge(`e${i}`, 'A', 'B', 'implements'),
      );

      const clusters = detectCanvasFallbackAreas(edges, nodes, 50);

      expect(clusters.length).toBeGreaterThan(0);
      expect(clusters[0].useCanvasRendering).toBe(true);
    });

    it('should not flag low-density areas', () => {
      const nodes = [createNode('A', 0, 0), createNode('B', 1000, 1000)];

      const edges = [createEdge('e1', 'A', 'B', 'implements')];

      const clusters = detectCanvasFallbackAreas(edges, nodes, 50);

      expect(clusters).toHaveLength(0);
    });
  });

  describe('applyLazyEdgeRendering', () => {
    it('should reduce 10K edges to <300 visible edges', () => {
      const nodes = Array.from({ length: 100 }, (_, i) => createNode(`n${i}`, i * 100, i * 100));

      const edges = Array.from({ length: 10000 }, (_, i) => {
        const source = Math.floor(Math.random() * 100);
        const target = Math.floor(Math.random() * 100);
        return createEdge(`e${i}`, `n${source}`, `n${target}`, 'implements');
      });

      const config = createDefaultSamplingConfig(edges.length);
      const filterConfig = createDefaultFilterConfig();

      const result = applyLazyEdgeRendering(edges, nodes, config, filterConfig);

      expect(result.visibleEdges.length).toBeLessThan(300);
      expect(result.stats.renderRatio).toBeLessThan(5);
    });

    it('should handle 1M edge target', () => {
      const nodes = Array.from({ length: 1000 }, (_, i) => createNode(`n${i}`, i * 100, i * 100));

      // Create subset of 1000 edges to avoid test timeout
      // (full 1M would be tested in benchmark)
      const edges = Array.from({ length: 1000 }, (_, i) => {
        const source = Math.floor(Math.random() * 1000);
        const target = Math.floor(Math.random() * 1000);
        return createEdge(`e${i}`, `n${source}`, `n${target}`, 'implements');
      });

      const config = createDefaultSamplingConfig(1000000); // Configure for 1M
      const filterConfig = createDefaultFilterConfig();

      const result = applyLazyEdgeRendering(edges, nodes, config, filterConfig);

      // Should use very aggressive config (maxVisibleEdges = 100)
      // With 1000 input edges, should still respect the small input size
      expect(result.visibleEdges.length).toBeLessThanOrEqual(100);
    });

    it('should provide stats about reduction', () => {
      const nodes = [createNode('A', 0, 0), createNode('B', 100, 100)];
      const edges = Array.from({ length: 100 }, (_, i) =>
        createEdge(`e${i}`, 'A', 'B', 'implements'),
      );

      const config = createDefaultSamplingConfig(edges.length);
      const result = applyLazyEdgeRendering(edges, nodes, config);

      expect(result.stats).toBeDefined();
      expect(result.stats.totalEdges).toBe(100);
      expect(result.stats.sampledEdges).toBeGreaterThan(0);
      expect(result.stats.renderRatio).toBeGreaterThan(0);
    });
  });

  describe('createDefaultSamplingConfig', () => {
    it('should auto-tune for small graphs', () => {
      const config = createDefaultSamplingConfig(500);

      expect(config.maxVisibleEdges).toBe(500);
      expect(config.samplingStrategy).toBe('importance');
    });

    it('should auto-tune for large graphs', () => {
      const config = createDefaultSamplingConfig(1000000);

      expect(config.maxVisibleEdges).toBe(100);
      expect(config.samplingStrategy).toBe('statistical');
    });

    it('should provide reasonable defaults', () => {
      const config = createDefaultSamplingConfig(10000);

      expect(config.maxVisibleEdges).toBeGreaterThan(0);
      expect(config.minEdgesForAggregation).toBeGreaterThanOrEqual(2);
      expect(config.canvasFallbackDensity).toBeGreaterThan(0);
      expect(config.priorityTypes).toBeDefined();
    });
  });
});
