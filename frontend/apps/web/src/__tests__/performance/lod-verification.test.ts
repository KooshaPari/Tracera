/**
 * LOD Performance Verification Tests - Task 16
 *
 * Tests verify:
 * 1. Node LOD selection logic (simple/medium/detailed based on context)
 * 2. R-tree spatial index performance (<5ms queries for 10k+ nodes)
 * 3. Edge LOD tier selection based on distance and zoom
 * 4. Integration with viewport culling
 *
 * Performance Targets (adjusted for test environment overhead):
 * - R-tree indexing: <300ms for 10,000 nodes (production: ~50ms)
 * - R-tree queries: <5ms for 10,000 nodes
 * - Edge culling: <300ms indexing, <50ms queries for 15,000 edges
 * - Edge LOD calculations: <100ms for 10,000 calculations (production: ~5ms)
 *
 * Note: Test environment has significant overhead compared to production.
 * The key verification is relative performance (O(log n) vs O(n)) not absolute timings.
 */

import { describe, expect, it } from 'vitest';

import type { NodeTypeContext } from '@/components/graph/nodeRegistry';

import { getNodeType } from '@/components/graph/nodeRegistry';
import { EDGE_LOD_TIERS, getEdgeLODTier } from '@/lib/edgeLOD';
import { GraphSpatialIndex } from '@/lib/spatialIndex';

describe('LOD System Verification', () => {
  describe('Node LOD Selection', () => {
    it('should use SimplePill for >5000 nodes', () => {
      const context: NodeTypeContext = {
        distance: 100,
        isFocused: false,
        isSelected: false,
        totalNodeCount: 6000,
        zoom: 1,
      };

      const nodeType = getNodeType('requirement', context);
      expect(nodeType).toBe('simple');
    });

    it('should use MediumPill for 2000-5000 nodes', () => {
      const context: NodeTypeContext = {
        distance: 100,
        isFocused: false,
        isSelected: false,
        totalNodeCount: 3000,
        zoom: 1,
      };

      const nodeType = getNodeType('requirement', context);
      expect(nodeType).toBe('medium');
    });

    it('should use full detail for selected nodes regardless of count', () => {
      const context: NodeTypeContext = {
        distance: 1000,
        isFocused: false,
        isSelected: true,
        totalNodeCount: 10_000,
        zoom: 0.1,
      };

      const nodeType = getNodeType('requirement', context);
      // Should not be simple or medium when selected
      expect(nodeType).not.toBe('simple');
      expect(nodeType).not.toBe('medium');
      // Should be a type-specific node (requirement, test, epic, etc.)
      expect(['requirement', 'test', 'epic', 'default', 'richPill']).toContain(nodeType);
    });

    it('should use SimplePill when zoomed out (<0.5)', () => {
      const context: NodeTypeContext = {
        distance: 100,
        isFocused: false,
        isSelected: false,
        totalNodeCount: 100,
        zoom: 0.3,
      };

      const nodeType = getNodeType('requirement', context);
      expect(nodeType).toBe('simple');
    });

    it('should use SimplePill when far from viewport (>800px)', () => {
      const context: NodeTypeContext = {
        distance: 900,
        isFocused: false,
        isSelected: false,
        totalNodeCount: 100,
        zoom: 1,
      };

      const nodeType = getNodeType('requirement', context);
      expect(nodeType).toBe('simple');
    });

    it('should use skeleton for loading state', () => {
      const context: NodeTypeContext = {
        isFocused: false,
        isSelected: false,
        loadingState: 'loading',
        totalNodeCount: 100,
        zoom: 1,
      };

      const nodeType = getNodeType('requirement', context);
      expect(nodeType).toBe('skeleton');
    });

    it('should use skeleton for error state', () => {
      const context: NodeTypeContext = {
        isFocused: false,
        isSelected: false,
        loadingState: 'error',
        totalNodeCount: 100,
        zoom: 1,
      };

      const nodeType = getNodeType('requirement', context);
      expect(nodeType).toBe('skeleton');
    });

    it('should prioritize focused state like selected state', () => {
      const context: NodeTypeContext = {
        distance: 1000,
        isFocused: true,
        isSelected: false,
        totalNodeCount: 10_000,
        zoom: 0.1,
      };

      const nodeType = getNodeType('requirement', context);
      expect(nodeType).not.toBe('simple');
      expect(nodeType).not.toBe('medium');
    });

    it('should use medium for moderate zoom (0.5-0.8)', () => {
      const context: NodeTypeContext = {
        distance: 100,
        isFocused: false,
        isSelected: false,
        totalNodeCount: 1000,
        zoom: 0.6,
      };

      const nodeType = getNodeType('requirement', context);
      expect(nodeType).toBe('medium');
    });

    it('should use medium for moderate distance (400-800px)', () => {
      const context: NodeTypeContext = {
        distance: 500,
        isFocused: false,
        isSelected: false,
        totalNodeCount: 1000,
        zoom: 1,
      };

      const nodeType = getNodeType('requirement', context);
      expect(nodeType).toBe('medium');
    });
  });

  describe('R-tree Spatial Index Performance', () => {
    it('should index 10,000 nodes in <300ms', () => {
      const nodes = Array.from({ length: 10_000 }, (_, i) => ({
        id: `node-${i}`,
        position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
      }));

      const spatialIndex = new GraphSpatialIndex();
      const startTime = performance.now();
      spatialIndex.indexNodes(nodes);
      const duration = performance.now() - startTime;

      // Allow 300ms for test environment overhead (production: ~50ms)
      expect(duration).toBeLessThan(300);
      expect(spatialIndex.getNodeCount()).toBe(10_000);
    });

    it('should query viewport in <5ms for 10,000 nodes', () => {
      const nodes = Array.from({ length: 10_000 }, (_, i) => ({
        id: `node-${i}`,
        position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
      }));

      const spatialIndex = new GraphSpatialIndex();
      spatialIndex.indexNodes(nodes);

      const startTime = performance.now();
      const result = spatialIndex.queryViewport({
        height: 1080,
        width: 1920,
        x: 0,
        y: 0,
        zoom: 1,
      });
      const duration = performance.now() - startTime;

      expect(duration).toBeLessThan(5);
      expect(result.nodes.length).toBeGreaterThan(0);
      expect(result.nodes.length).toBeLessThan(nodes.length); // Should cull some nodes
    });

    it('should cull edges efficiently for 15,000 edges', () => {
      const nodes = Array.from({ length: 5000 }, (_, i) => ({
        id: `node-${i}`,
        position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
      }));

      const edges = Array.from({ length: 15_000 }, (_, i) => ({
        id: `edge-${i}`,
        sourceId: `node-${Math.floor(Math.random() * 5000)}`,
        targetId: `node-${Math.floor(Math.random() * 5000)}`,
      }));

      const spatialIndex = new GraphSpatialIndex();
      spatialIndex.indexNodes(nodes);

      const nodePositions = new Map(nodes.map((n) => [n.id, n.position]));

      const startTime = performance.now();
      spatialIndex.indexEdges(edges, nodePositions);
      const indexDuration = performance.now() - startTime;

      // Allow 300ms for test environment overhead with large edge set
      expect(indexDuration).toBeLessThan(300);
      expect(spatialIndex.getEdgeCount()).toBe(15_000);

      const queryStart = performance.now();
      const result = spatialIndex.queryViewport({
        height: 1080,
        width: 1920,
        x: 0,
        y: 0,
        zoom: 1,
      });
      const queryDuration = performance.now() - queryStart;

      // Allow 50ms for test environment overhead with large edge set
      expect(queryDuration).toBeLessThan(50);
      expect(result.edges.length).toBeLessThan(edges.length); // Should cull some edges
    });

    it('should handle viewport panning without performance degradation', () => {
      const nodes = Array.from({ length: 10_000 }, (_, i) => ({
        id: `node-${i}`,
        position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
      }));

      const spatialIndex = new GraphSpatialIndex();
      spatialIndex.indexNodes(nodes);

      // Simulate 10 viewport panning queries
      const queries = Array.from({ length: 10 }, (_, i) => ({
        height: 1080,
        width: 1920,
        x: i * 500,
        y: i * 500,
        zoom: 1,
      }));

      const startTime = performance.now();
      for (const query of queries) {
        spatialIndex.queryViewport(query);
      }
      const totalDuration = performance.now() - startTime;

      // All 10 queries should complete in <50ms total (5ms each)
      expect(totalDuration).toBeLessThan(50);
    });

    it('should scale with zoom level', () => {
      const nodes = Array.from({ length: 5000 }, (_, i) => ({
        id: `node-${i}`,
        position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
      }));

      const spatialIndex = new GraphSpatialIndex();
      spatialIndex.indexNodes(nodes);

      // Query at different zoom levels
      const zoom1x = spatialIndex.queryViewport({
        height: 1080,
        width: 1920,
        x: 0,
        y: 0,
        zoom: 1,
      });

      const zoom2x = spatialIndex.queryViewport({
        height: 1080,
        width: 1920,
        x: 0,
        y: 0,
        zoom: 2,
      });

      const zoom05x = spatialIndex.queryViewport({
        height: 1080,
        width: 1920,
        x: 0,
        y: 0,
        zoom: 0.5,
      });

      // Higher zoom should return fewer nodes
      expect(zoom2x.nodes.length).toBeLessThan(zoom1x.nodes.length);
      // Lower zoom should return more nodes
      expect(zoom05x.nodes.length).toBeGreaterThan(zoom1x.nodes.length);
    });
  });

  describe('Edge LOD Tiers', () => {
    it('should return detailed tier for close edges (<300px)', () => {
      const tier = getEdgeLODTier({ x: 100, y: 100 }, { x: 150, y: 150 }, 1);
      expect(tier.level).toBe('detailed');
      expect(tier.showLabel).toBeTruthy();
      expect(tier.showArrow).toBeTruthy();
      expect(tier.pathType).toBe('bezier');
      expect(tier.opacity).toBe(1);
    });

    it('should return medium tier for mid-distance edges (300-600px)', () => {
      const tier = getEdgeLODTier({ x: 100, y: 100 }, { x: 500, y: 100 }, 1);
      expect(tier.level).toBe('medium');
      expect(tier.showLabel).toBeFalsy();
      expect(tier.showArrow).toBeTruthy();
      expect(tier.pathType).toBe('bezier');
      expect(tier.opacity).toBe(0.8);
    });

    it('should return simple tier for far edges (600-1200px)', () => {
      const tier = getEdgeLODTier({ x: 100, y: 100 }, { x: 900, y: 100 }, 1);
      expect(tier.level).toBe('simple');
      expect(tier.pathType).toBe('straight');
      expect(tier.showLabel).toBeFalsy();
      expect(tier.showArrow).toBeFalsy();
      expect(tier.opacity).toBe(0.5);
    });

    it('should return hidden tier for very far edges (>1200px)', () => {
      const tier = getEdgeLODTier({ x: 100, y: 100 }, { x: 1500, y: 100 }, 1);
      expect(tier.level).toBe('hidden');
      expect(tier.opacity).toBe(0);
      expect(tier.strokeWidth).toBe(0);
    });

    it('should adjust thresholds based on zoom level', () => {
      // At 2x zoom, 300px threshold becomes 150px effective distance
      // So a 200px actual distance should be medium (>150px at 2x zoom)
      const tier = getEdgeLODTier(
        { x: 100, y: 100 },
        { x: 300, y: 100 }, // 200px distance
        2,
      );
      expect(tier.level).toBe('medium');
    });

    it('should handle zoom factor clamping', () => {
      // Very high zoom (>2) should be clamped to 2
      const tierHigh = getEdgeLODTier({ x: 100, y: 100 }, { x: 500, y: 100 }, 5);

      // Very low zoom (<0.5) should be clamped to 0.5
      const tierLow = getEdgeLODTier({ x: 100, y: 100 }, { x: 500, y: 100 }, 0.1);

      // Both should be valid tiers (not crash)
      expect(['detailed', 'medium', 'simple', 'hidden']).toContain(tierHigh.level);
      expect(['detailed', 'medium', 'simple', 'hidden']).toContain(tierLow.level);
    });

    it('should verify all tier thresholds are correctly defined', () => {
      expect(EDGE_LOD_TIERS).toHaveLength(4);

      // Verify tiers are sorted by increasing distance
      expect(EDGE_LOD_TIERS[0]!.level).toBe('detailed');
      expect(EDGE_LOD_TIERS[0]!.distanceThreshold).toBe(0);

      expect(EDGE_LOD_TIERS[1]!.level).toBe('medium');
      expect(EDGE_LOD_TIERS[1]!.distanceThreshold).toBe(300);

      expect(EDGE_LOD_TIERS[2]!.level).toBe('simple');
      expect(EDGE_LOD_TIERS[2]!.distanceThreshold).toBe(600);

      expect(EDGE_LOD_TIERS[3]!.level).toBe('hidden');
      expect(EDGE_LOD_TIERS[3]!.distanceThreshold).toBe(1200);
    });

    it('should calculate diagonal distances correctly', () => {
      // Pythagorean theorem: sqrt(300^2 + 400^2) = 500px
      const tier = getEdgeLODTier({ x: 0, y: 0 }, { x: 300, y: 400 }, 1);
      // 500px should be in medium tier (300-600px)
      expect(tier.level).toBe('medium');
    });
  });

  describe('Integration Tests', () => {
    it('should demonstrate viewport culling efficiency', () => {
      const nodes = Array.from({ length: 10_000 }, (_, i) => ({
        id: `node-${i}`,
        position: {
          x: (i % 100) * 100,
          y: Math.floor(i / 100) * 100,
        },
      }));

      const spatialIndex = new GraphSpatialIndex();
      spatialIndex.indexNodes(nodes);

      // Small viewport should only return a fraction of nodes
      const result = spatialIndex.queryViewport({
        height: 1080,
        width: 1920,
        x: 0,
        y: 0,
        zoom: 1,
      });

      // Should have significant culling (>50% reduction)
      const cullingRate = 1 - result.nodes.length / nodes.length;
      expect(cullingRate).toBeGreaterThan(0.5);
    });

    it('should handle empty graph gracefully', () => {
      const spatialIndex = new GraphSpatialIndex();

      const result = spatialIndex.queryViewport({
        height: 1080,
        width: 1920,
        x: 0,
        y: 0,
        zoom: 1,
      });

      expect(result.nodes).toHaveLength(0);
      expect(result.edges).toHaveLength(0);
    });

    it('should maintain accuracy with buffer zones', () => {
      const nodes = Array.from({ length: 1000 }, (_, i) => ({
        id: `node-${i}`,
        position: {
          x: Math.random() * 5000,
          y: Math.random() * 5000,
        },
      }));

      const spatialIndex = new GraphSpatialIndex();
      spatialIndex.indexNodes(nodes);

      // Nodes near viewport edge should be included (buffer zone)
      const result = spatialIndex.queryViewport({
        height: 1000,
        width: 1000,
        x: 1000,
        y: 1000,
        zoom: 1,
      });

      // Should include nodes within and slightly outside viewport
      expect(result.nodes.length).toBeGreaterThan(0);

      // All returned nodes should be within a reasonable distance
      for (const node of result.nodes) {
        const nodePos = nodes.find((n) => n.id === node.id)?.position;
        if (nodePos) {
          // Buffer is ~200px at zoom 1.0, so max distance is ~1414px from center
          const centerX = 1000 + 1000 / 2;
          const centerY = 1000 + 1000 / 2;
          const distance = Math.sqrt((nodePos.x - centerX) ** 2 + (nodePos.y - centerY) ** 2);
          expect(distance).toBeLessThan(2000); // Generous bound
        }
      }
    });

    it('should verify LOD reduces rendered nodes at scale', () => {
      // Test that LOD system correctly identifies when to use simple nodes
      const testCases = [
        { distance: 100, expectedSimple: false, nodeCount: 1000, zoom: 1 },
        { distance: 100, expectedSimple: true, nodeCount: 6000, zoom: 1 },
        { distance: 100, expectedSimple: true, nodeCount: 1000, zoom: 0.3 },
        { distance: 900, expectedSimple: true, nodeCount: 1000, zoom: 1 },
      ];

      for (const testCase of testCases) {
        const context: NodeTypeContext = {
          distance: testCase.distance,
          isFocused: false,
          isSelected: false,
          totalNodeCount: testCase.nodeCount,
          zoom: testCase.zoom,
        };

        const nodeType = getNodeType('requirement', context);
        const isSimple = nodeType === 'simple';
        expect(isSimple).toBe(testCase.expectedSimple);
      }
    });
  });

  describe('Performance Regression Tests', () => {
    it('should maintain consistent query performance across multiple runs', () => {
      const nodes = Array.from({ length: 10_000 }, (_, i) => ({
        id: `node-${i}`,
        position: { x: Math.random() * 10_000, y: Math.random() * 10_000 },
      }));

      const spatialIndex = new GraphSpatialIndex();
      spatialIndex.indexNodes(nodes);

      const timings: number[] = [];

      // Run 100 queries
      for (let i = 0; i < 100; i++) {
        const startTime = performance.now();
        spatialIndex.queryViewport({
          height: 1080,
          width: 1920,
          x: Math.random() * 5000,
          y: Math.random() * 5000,
          zoom: 1,
        });
        timings.push(performance.now() - startTime);
      }

      // Calculate statistics
      const avgTime = timings.reduce((a, b) => a + b, 0) / timings.length;
      const maxTime = Math.max(...timings);

      // Average should be <5ms, max should be <10ms
      expect(avgTime).toBeLessThan(5);
      expect(maxTime).toBeLessThan(10);
    });

    it('should verify edge LOD calculation performance', () => {
      // Calculate 10,000 edge LOD tiers
      const calculations = 10_000;
      const startTime = performance.now();

      for (let i = 0; i < calculations; i++) {
        getEdgeLODTier(
          { x: Math.random() * 10_000, y: Math.random() * 10_000 },
          { x: Math.random() * 10_000, y: Math.random() * 10_000 },
          Math.random() * 2,
        );
      }

      const duration = performance.now() - startTime;

      // 10,000 calculations should take <100ms (allowing for test overhead)
      expect(duration).toBeLessThan(100);
    });
  });
});
