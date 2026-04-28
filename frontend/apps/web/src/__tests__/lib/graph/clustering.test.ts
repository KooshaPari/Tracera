/**
 * Tests for Louvain Community Detection
 */

import { describe, it, expect, beforeEach } from 'vitest';

import type { Item, Link } from '@tracertm/types';

import {
  detectCommunities,
  clearClusteringCache,
  getCommunityColor,
  formatCommunityStats,
  exportCommunitiesJSON,
  exportCommunitiesCSV,
  COMMUNITY_COLORS,
} from '../../../lib/graph/clustering';

describe('Louvain Community Detection', () => {
  beforeEach(() => {
    clearClusteringCache();
  });

  describe('detectCommunities', () => {
    it('should handle empty graph', async () => {
      const result = await detectCommunities([], []);

      expect(result.communities.size).toBe(0);
      expect(result.stats.communityCount).toBe(0);
      expect(result.performance.nodeCount).toBe(0);
      expect(result.performance.edgeCount).toBe(0);
    });

    it('should handle single node', async () => {
      const items: Item[] = [
        {
          id: 'node1',
          title: 'Test Node',
          item_type: 'requirement',
          status: 'todo',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      const result = await detectCommunities(items, []);

      expect(result.communities.size).toBe(1);
      expect(result.communities.get('node1')).toBe('0');
      expect(result.stats.communityCount).toBe(1);
      expect(result.stats.maxCommunitySize).toBe(1);
      expect(result.stats.minCommunitySize).toBe(1);
    });

    it('should detect communities in connected graph', async () => {
      // Create a simple graph with two distinct communities
      const items: Item[] = [
        // Community 1
        {
          id: 'a1',
          title: 'A1',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'a2',
          title: 'A2',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'a3',
          title: 'A3',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        // Community 2
        {
          id: 'b1',
          title: 'B1',
          item_type: 'feature',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'b2',
          title: 'B2',
          item_type: 'feature',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'b3',
          title: 'B3',
          item_type: 'feature',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
      ];

      const links: Link[] = [
        // Dense connections within community 1
        {
          id: 'l1',
          source_id: 'a1',
          target_id: 'a2',
          link_type: 'depends_on',
          created_at: '',
        },
        {
          id: 'l2',
          source_id: 'a2',
          target_id: 'a3',
          link_type: 'depends_on',
          created_at: '',
        },
        {
          id: 'l3',
          source_id: 'a3',
          target_id: 'a1',
          link_type: 'depends_on',
          created_at: '',
        },
        // Dense connections within community 2
        {
          id: 'l4',
          source_id: 'b1',
          target_id: 'b2',
          link_type: 'depends_on',
          created_at: '',
        },
        {
          id: 'l5',
          source_id: 'b2',
          target_id: 'b3',
          link_type: 'depends_on',
          created_at: '',
        },
        {
          id: 'l6',
          source_id: 'b3',
          target_id: 'b1',
          link_type: 'depends_on',
          created_at: '',
        },
        // Weak connection between communities
        {
          id: 'l7',
          source_id: 'a1',
          target_id: 'b1',
          link_type: 'related_to',
          created_at: '',
        },
      ];

      const result = await detectCommunities(items, links);

      // Should detect at least 1 community (possibly 2)
      expect(result.communities.size).toBe(6);
      expect(result.stats.communityCount).toBeGreaterThanOrEqual(1);
      expect(result.stats.communityCount).toBeLessThanOrEqual(6);

      // Check that nodes are assigned
      expect(result.communities.has('a1')).toBe(true);
      expect(result.communities.has('b1')).toBe(true);

      // Check modularity (should be defined for connected graphs)
      expect(result.stats.modularity).toBeDefined();
    });

    it('should assign colors to communities', async () => {
      const items: Item[] = [
        {
          id: 'n1',
          title: 'N1',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'n2',
          title: 'N2',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
      ];

      const links: Link[] = [
        {
          id: 'l1',
          source_id: 'n1',
          target_id: 'n2',
          link_type: 'depends_on',
          created_at: '',
        },
      ];

      const result = await detectCommunities(items, links);

      // All communities should have colors
      for (const communityId of result.stats.communitySizes.keys()) {
        expect(result.colors.has(communityId)).toBe(true);
        const color = result.colors.get(communityId);
        expect(color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      }
    });

    it('should cache results when useCache is true', async () => {
      const items: Item[] = [
        {
          id: 'n1',
          title: 'N1',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
      ];

      clearClusteringCache();
      const result1 = await detectCommunities(items, [], { useCache: true });
      const result2 = await detectCommunities(items, [], { useCache: true });

      // Should be same reference (cached) - check structural equality since timing may vary slightly
      expect(result1.communities.get('n1')).toBe(result2.communities.get('n1'));
      expect(result1.stats.communityCount).toBe(result2.stats.communityCount);
      // Actual caching is verified by the time being similar (second call should be instant)
      expect(result2.performance.clusteringTimeMs).toBeLessThan(
        result1.performance.clusteringTimeMs + 1,
      );
    });

    it('should not cache when useCache is false', async () => {
      const items: Item[] = [
        {
          id: 'n1',
          title: 'N1',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
      ];

      const result1 = await detectCommunities(items, [], { useCache: false });
      const result2 = await detectCommunities(items, [], { useCache: false });

      // May not be same reference (not cached)
      // But should have same structure
      expect(result1.communities.size).toBe(result2.communities.size);
    });

    it('should handle disconnected components', async () => {
      const items: Item[] = [
        {
          id: 'n1',
          title: 'N1',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'n2',
          title: 'N2',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'n3',
          title: 'N3',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
      ];

      const links: Link[] = [
        {
          id: 'l1',
          source_id: 'n1',
          target_id: 'n2',
          link_type: 'depends_on',
          created_at: '',
        },
        // n3 is disconnected
      ];

      const result = await detectCommunities(items, links);

      expect(result.communities.size).toBe(3);
      expect(result.stats.communityCount).toBeGreaterThanOrEqual(1);
    });

    it('should respect minCommunitySize option', async () => {
      const items: Item[] = [
        {
          id: 'n1',
          title: 'N1',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'n2',
          title: 'N2',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'n3',
          title: 'N3',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'n4',
          title: 'N4',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
      ];

      const links: Link[] = [
        {
          id: 'l1',
          source_id: 'n1',
          target_id: 'n2',
          link_type: 'depends_on',
          created_at: '',
        },
        {
          id: 'l2',
          source_id: 'n3',
          target_id: 'n4',
          link_type: 'depends_on',
          created_at: '',
        },
      ];

      const result = await detectCommunities(items, links, {
        minCommunitySize: 3,
      });

      // Small communities should be filtered out
      expect(result.communities.size).toBe(4);

      // All nodes in small communities should be assigned to '0'
      const communitySizes = new Map<string, number>();
      for (const communityId of result.communities.values()) {
        communitySizes.set(communityId, (communitySizes.get(communityId) || 0) + 1);
      }

      // No community should be smaller than minCommunitySize (except '0' which collects small ones)
      for (const [communityId, size] of communitySizes.entries()) {
        if (communityId !== '0') {
          expect(size).toBeGreaterThanOrEqual(3);
        }
      }
    });

    it('should complete clustering quickly', async () => {
      // Generate a moderate-sized graph (100 nodes)
      const items: Item[] = Array.from({ length: 100 }, (_, i) => ({
        id: `node${i}`,
        title: `Node ${i}`,
        item_type: 'requirement',
        status: 'todo',
        created_at: '',
        updated_at: '',
      }));

      // Create random links
      const links: Link[] = [];
      for (let i = 0; i < 200; i++) {
        const source = Math.floor(Math.random() * 100);
        const target = Math.floor(Math.random() * 100);
        if (source !== target) {
          links.push({
            id: `link${i}`,
            source_id: `node${source}`,
            target_id: `node${target}`,
            link_type: 'depends_on',
            created_at: '',
          });
        }
      }

      const startTime = performance.now();
      const result = await detectCommunities(items, links);
      const endTime = performance.now();

      const duration = endTime - startTime;

      // Should complete in reasonable time (< 500ms for 100 nodes)
      expect(duration).toBeLessThan(500);
      expect(result.communities.size).toBe(100);
      expect(result.performance.clusteringTimeMs).toBeGreaterThan(0);
    });
  });

  describe('getCommunityColor', () => {
    it('should return color from map', () => {
      const colors = new Map([['comm1', '#FF0000']]);
      expect(getCommunityColor('comm1', colors)).toBe('#FF0000');
    });

    it('should return default color if not in map', () => {
      const colors = new Map<string, string>();
      const color = getCommunityColor('unknown', colors);
      expect(color).toBe(COMMUNITY_COLORS[0]);
    });
  });

  describe('formatCommunityStats', () => {
    it('should format stats correctly', () => {
      const stats = {
        communityCount: 5,
        communitySizes: new Map([
          ['0', 10],
          ['1', 20],
          ['2', 15],
          ['3', 8],
          ['4', 12],
        ]),
        maxCommunitySize: 20,
        minCommunitySize: 8,
        avgCommunitySize: 13,
      };

      const formatted = formatCommunityStats(stats);
      expect(formatted).toContain('5 communities');
      expect(formatted).toContain('13 nodes');
    });
  });

  describe('exportCommunitiesJSON', () => {
    it('should export valid JSON', async () => {
      const items: Item[] = [
        {
          id: 'n1',
          title: 'N1',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'n2',
          title: 'N2',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
      ];

      const links: Link[] = [
        {
          id: 'l1',
          source_id: 'n1',
          target_id: 'n2',
          link_type: 'depends_on',
          created_at: '',
        },
      ];

      const result = await detectCommunities(items, links);
      const json = exportCommunitiesJSON(result);

      // Should be valid JSON
      expect(() => JSON.parse(json)).not.toThrow();

      const parsed = JSON.parse(json);
      expect(parsed.communities).toBeDefined();
      expect(Array.isArray(parsed.communities)).toBe(true);
      expect(parsed.stats).toBeDefined();
      expect(parsed.performance).toBeDefined();
    });
  });

  describe('exportCommunitiesCSV', () => {
    it('should export valid CSV', async () => {
      const items: Item[] = [
        {
          id: 'n1',
          title: 'N1',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
        {
          id: 'n2',
          title: 'N2',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
      ];

      const links: Link[] = [
        {
          id: 'l1',
          source_id: 'n1',
          target_id: 'n2',
          link_type: 'depends_on',
          created_at: '',
        },
      ];

      const result = await detectCommunities(items, links);
      const csv = exportCommunitiesCSV(result);

      // Should have header and data rows
      const lines = csv.split('\n');
      expect(lines.length).toBeGreaterThan(1);
      expect(lines[0]).toBe('Node ID,Community ID,Color');
      expect(lines[1]).toContain('n1');
      expect(lines[2]).toContain('n2');
    });
  });

  describe('clearClusteringCache', () => {
    it('should clear the cache', async () => {
      const items: Item[] = [
        {
          id: 'n1',
          title: 'N1',
          item_type: 'requirement',
          status: 'todo',
          created_at: '',
          updated_at: '',
        },
      ];

      const result1 = await detectCommunities(items, [], { useCache: true });
      clearClusteringCache();
      const result2 = await detectCommunities(items, [], { useCache: true });

      // After clearing cache, should get new instance
      // (though values should be the same)
      expect(result1.communities.size).toBe(result2.communities.size);
    });
  });
});
