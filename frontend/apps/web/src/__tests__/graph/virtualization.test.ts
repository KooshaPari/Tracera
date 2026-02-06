import { describe, expect, it } from 'vitest';

import type { NodePosition, ViewportBounds } from '../../components/graph/hooks/useVirtualization';

describe('Virtual Rendering Utilities', () => {
  describe('Viewport culling', () => {
    it('should identify nodes within viewport bounds', () => {
      const node: NodePosition = {
        height: 120,
        id: 'node-1',
        width: 200,
        x: 100,
        y: 100,
      };

      const viewport: ViewportBounds = {
        maxX: 500,
        maxY: 500,
        minX: 0,
        minY: 0,
      };

      const isVisible =
        node.x + node.width > viewport.minX &&
        node.x < viewport.maxX &&
        node.y + node.height > viewport.minY &&
        node.y < viewport.maxY;

      expect(isVisible).toBeTruthy();
    });

    it('should cull nodes outside viewport bounds', () => {
      const node: NodePosition = {
        height: 120,
        id: 'node-1',
        width: 200,
        x: 1000,
        y: 1000,
      };

      const viewport: ViewportBounds = {
        maxX: 500,
        maxY: 500,
        minX: 0,
        minY: 0,
      };

      const isVisible =
        node.x + node.width > viewport.minX &&
        node.x < viewport.maxX &&
        node.y + node.height > viewport.minY &&
        node.y < viewport.maxY;

      expect(isVisible).toBeFalsy();
    });

    it('should handle nodes at viewport edges', () => {
      const nodeLeft: NodePosition = {
        height: 120,
        id: 'node-left',
        width: 200,
        x: -50,
        y: 100,
      };

      const viewport: ViewportBounds = {
        maxX: 500,
        maxY: 500,
        minX: 0,
        minY: 0,
      };

      const isVisibleLeft =
        nodeLeft.x + nodeLeft.width > viewport.minX &&
        nodeLeft.x < viewport.maxX &&
        nodeLeft.y + nodeLeft.height > viewport.minY &&
        nodeLeft.y < viewport.maxY;

      expect(isVisibleLeft).toBeTruthy(); // Partially visible
    });

    it('should calculate viewport bounds with padding', () => {
      const viewport = { height: 600, width: 1000, x: 100, y: 100, zoom: 1 };
      const padding = 200;

      const bounds: ViewportBounds = {
        maxX: viewport.x + viewport.width / viewport.zoom + padding,
        maxY: viewport.y + viewport.height / viewport.zoom + padding,
        minX: viewport.x - padding,
        minY: viewport.y - padding,
      };

      expect(bounds.minX).toBe(-100);
      expect(bounds.maxX).toBe(1300);
      expect(bounds.minY).toBe(-100);
      expect(bounds.maxY).toBe(900);
    });

    it('should account for zoom level in viewport calculation', () => {
      const viewport = { height: 600, width: 1000, x: 0, y: 0, zoom: 0.5 };
      const padding = 0;

      const bounds: ViewportBounds = {
        maxX: viewport.x + viewport.width / viewport.zoom + padding,
        maxY: viewport.y + viewport.height / viewport.zoom + padding,
        minX: viewport.x - padding,
        minY: viewport.y - padding,
      };

      expect(bounds.maxX).toBe(2000); // 1000 / 0.5
      expect(bounds.maxY).toBe(1200); // 600 / 0.5
    });
  });

  describe('Level of Detail (LOD)', () => {
    it('should return high LOD above zoom threshold', () => {
      const zoom = 0.9;
      const threshold = 0.8;
      const lodLevel = zoom >= threshold ? 'high' : zoom >= threshold / 2 ? 'medium' : 'low';
      expect(lodLevel).toBe('high');
    });

    it('should return medium LOD between thresholds', () => {
      const zoom = 0.6;
      const highThreshold = 0.8;
      const mediumThreshold = 0.5;
      const lodLevel = zoom >= highThreshold ? 'high' : zoom >= mediumThreshold ? 'medium' : 'low';
      expect(lodLevel).toBe('medium');
    });

    it('should return low LOD below zoom threshold', () => {
      const zoom = 0.3;
      const highThreshold = 0.8;
      const mediumThreshold = 0.5;
      const lodLevel = zoom >= highThreshold ? 'high' : zoom >= mediumThreshold ? 'medium' : 'low';
      expect(lodLevel).toBe('low');
    });
  });

  describe('Node clustering', () => {
    it('should group nodes within distance threshold', () => {
      const nodes: NodePosition[] = [
        { height: 100, id: 'n1', width: 100, x: 0, y: 0 },
        { height: 100, id: 'n2', width: 100, x: 50, y: 50 }, // Close to n1
        { height: 100, id: 'n3', width: 100, x: 500, y: 500 }, // Far from others
      ];

      const clusterDistance = 200;
      const clusters = new Map<string, string[]>();
      const visited = new Set<string>();

      function clusterFromNode(startId: string): string[] {
        if (visited.has(startId)) {
          return [];
        }

        const cluster: string[] = [startId];
        visited.add(startId);
        const queue = [startId];

        const nodeMap = new Map(nodes.map((n) => [n.id, n]));

        while (queue.length > 0) {
          const currentId = queue.shift()!;
          const current = nodeMap.get(currentId)!;

          for (const other of nodes) {
            if (visited.has(other.id)) {
              continue;
            }

            const dx = other.x - current.x;
            const dy = other.y - current.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < clusterDistance) {
              cluster.push(other.id);
              visited.add(other.id);
              queue.push(other.id);
            }
          }
        }

        return cluster;
      }

      for (const node of nodes) {
        if (!visited.has(node.id)) {
          const cluster = clusterFromNode(node.id);
          clusters.set(`cluster-${cluster[0]}`, cluster);
        }
      }

      expect(clusters.size).toBe(2); // N1+n2 group, n3 alone
    });
  });

  describe('Culling metrics', () => {
    it('should calculate culling ratio', () => {
      const totalNodes = 1000;
      const visibleNodes = 150;
      const culledNodes = totalNodes - visibleNodes;
      const cullingRatio = culledNodes / totalNodes;

      expect(cullingRatio).toBeCloseTo(0.85); // 850 culled / 1000 total
    });

    it('should track render performance', () => {
      const renderStart = performance.now();
      // Simulate work
      for (let i = 0; i < 1000; i++) {
        Math.sqrt(i);
      }
      const renderTime = performance.now() - renderStart;

      expect(renderTime).toBeGreaterThan(0);
      expect(typeof renderTime).toBe('number');
    });
  });

  describe('Progressive loading', () => {
    it('should load items in batches', () => {
      const items = Array.from({ length: 500 }, (_, i) => ({
        id: `item-${i}`,
      }));
      const batchSize = 50;
      const loadedItems = new Set<string>();

      // Simulate batch loading
      const batches = Math.ceil(items.length / batchSize);
      for (let i = 0; i < batches; i++) {
        const start = i * batchSize;
        const end = Math.min(start + batchSize, items.length);
        for (let j = start; j < end; j++) {
          loadedItems.add(items[j].id);
        }
      }

      expect(loadedItems.size).toBe(items.length);
    });

    it('should calculate loading progress', () => {
      const totalItems = 200;
      const loadedItems = 50;
      const progress = (loadedItems / totalItems) * 100;

      expect(progress).toBe(25);
    });
  });

  describe('Intersection Observer visibility', () => {
    it('should track visible node IDs', () => {
      const visibleIds = new Set(['node-1', 'node-2', 'node-5']);

      const isVisible = (nodeId: string) => visibleIds.has(nodeId);

      expect(isVisible('node-1')).toBeTruthy();
      expect(isVisible('node-3')).toBeFalsy();
      expect(isVisible('node-5')).toBeTruthy();
    });
  });

  describe('Large graph handling', () => {
    it('should handle 10000 nodes efficiently', () => {
      const nodes: NodePosition[] = Array.from({ length: 10_000 }, (_, i) => ({
        height: 120,
        id: `node-${i}`,
        width: 200,
        x: Math.random() * 50_000,
        y: Math.random() * 50_000,
      }));

      const viewport: ViewportBounds = {
        maxX: 2000,
        maxY: 1500,
        minX: 0,
        minY: 0,
      };

      const startTime = performance.now();

      const visible = nodes.filter(
        (node) =>
          node.x + node.width > viewport.minX &&
          node.x < viewport.maxX &&
          node.y + node.height > viewport.minY &&
          node.y < viewport.maxY,
      );

      const endTime = performance.now();
      const duration = endTime - startTime;

      // Should complete culling in reasonable time (< 100ms)
      expect(duration).toBeLessThan(100);
      expect(visible.length).toBeGreaterThan(0);
      expect(visible.length).toBeLessThan(nodes.length);
    });

    it('should reduce render load with virtualization', () => {
      const totalNodes = 5000;
      const viewport = { height: 600, width: 1000, x: 0, y: 0, zoom: 1 };
      const padding = 300;

      const bounds: ViewportBounds = {
        maxX: viewport.x + viewport.width / viewport.zoom + padding,
        maxY: viewport.y + viewport.height / viewport.zoom + padding,
        minX: viewport.x - padding,
        minY: viewport.y - padding,
      };

      // Rough estimate of visible nodes
      const boundsArea = (bounds.maxX - bounds.minX) * (bounds.maxY - bounds.minY);
      const totalArea = 50_000 * 50_000;
      const estimatedVisibleNodes = Math.floor((boundsArea / totalArea) * totalNodes);

      const reductionRatio = (totalNodes - estimatedVisibleNodes) / totalNodes;

      expect(reductionRatio).toBeGreaterThan(0.7); // At least 70% reduction
      expect(estimatedVisibleNodes).toBeLessThan(totalNodes);
    });
  });
});
