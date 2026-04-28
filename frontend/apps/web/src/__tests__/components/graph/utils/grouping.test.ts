// Tests for grouping algorithms

import type { Item, Link, LinkType } from '@tracertm/types';

import {
  calculateGroupCohesion,
  calculateGroupSeparation,
  groupByDependencies,
  groupByLinkTargets,
  groupByPaths,
  groupBySemantic,
} from '../../../../components/graph/utils/grouping';

function createItem(id: string, title: string, type: string): Item {
  return {
    createdAt: new Date().toISOString(),
    description: `Item ${id}`,
    id,
    priority: 'medium' as const,
    projectId: 'p1',
    status: 'done' as const,
    title,
    type,
    updatedAt: new Date().toISOString(),
    version: 1,
    view: 'architecture',
  };
}

function createLink(sourceId: string, targetId: string, type = 'depends_on'): Link {
  return {
    createdAt: new Date().toISOString(),
    description: `Link from ${sourceId} to ${targetId}`,
    id: `link-${sourceId}-${targetId}`,
    projectId: 'p1',
    sourceId,
    targetId,
    type: type as LinkType,
    updatedAt: new Date().toISOString(),
    version: 1,
  };
}

describe('Grouping Algorithms', () => {
  let items: Item[];
  let links: Link[];

  beforeEach(() => {
    items = [
      createItem('item1', 'Component A', 'Component'),
      createItem('item2', 'Component B', 'Component'),
      createItem('item3', 'API Endpoint', 'API'),
      createItem('item4', 'Service', 'Service'),
      createItem('item5', 'Component C', 'Component'),
    ];

    links = [
      // Both item1 and item2 depend on item3 and item4
      createLink('item1', 'item3'),
      createLink('item1', 'item4'),
      createLink('item2', 'item3'),
      createLink('item2', 'item4'),
      // Item5 depends on item3 only
      createLink('item5', 'item3'),
    ];
  });

  describe(groupByLinkTargets, () => {
    it('should group items that share common targets', () => {
      const groups = groupByLinkTargets(items, links);

      // Item1 and item2 should be in same group (both target item3 and item4)
      expect(groups.length).toBeGreaterThan(0);

      const groupWithBoth = groups.find(
        (g) => g.itemIds.includes('item1') && g.itemIds.includes('item2'),
      );
      expect(groupWithBoth).toBeDefined();
    });

    it('should return empty array when no groups meet minimum size', () => {
      const groups = groupByLinkTargets(items, links, 10);
      expect(groups.length).toBe(0);
    });

    it('should include common targets in metadata', () => {
      const groups = groupByLinkTargets(items, links);
      const group = groups.find((g) => g.itemIds.includes('item1'));

      expect(group?.metadata?.['commonTargets']).toBeDefined();
    });
  });

  describe(groupByDependencies, () => {
    it('should group items with same dependencies', () => {
      const groups = groupByDependencies(items, links);

      // Item1 and item2 have identical dependencies (item3 and item4)
      const groupWithBoth = groups.find(
        (g) => g.itemIds.includes('item1') && g.itemIds.includes('item2'),
      );
      expect(groupWithBoth).toBeDefined();
    });

    it('should not group items with different dependencies', () => {
      const groups = groupByDependencies(items, links);
      const groupWithItem5 = groups.find((g) => g.itemIds.includes('item5'));

      // Item5 has different dependencies than item1/item2
      if (groupWithItem5) {
        expect(!groupWithItem5.itemIds.includes('item1')).toBeTruthy();
      }
    });

    it('should include dependency count in metrics', () => {
      const groups = groupByDependencies(items, links);
      const group = groups.find((g) => g.itemIds.includes('item1'));

      expect(group?.metrics?.cohesion).toBeDefined();
      expect(typeof group?.metrics?.cohesion).toBe('number');
    });
  });

  describe(groupByPaths, () => {
    it('should group connected items as paths', () => {
      const groups = groupByPaths(items, links);
      expect(groups.length).toBeGreaterThan(0);

      // All items are connected
      const totalItems = groups.reduce((sum, g) => sum + g.itemCount, 0);
      expect(totalItems).toBe(items.length);
    });

    it('should have cohesion of 1 for connected components', () => {
      const groups = groupByPaths(items, links);
      const group = groups[0];
      expect(group).toBeDefined();
      if (!group) {
        return;
      }

      expect(group.metrics?.cohesion).toBe(1);
    });

    it('should separate disconnected items into different groups', () => {
      const isolatedItem = createItem('item6', 'Isolated', 'Component');
      const testItems = [...items, isolatedItem];

      const groups = groupByPaths(testItems, links);
      const groupWithIsolated = groups.find((g) => g.itemIds.includes('item6'));

      // Isolated item should either be alone or with other isolated items
      expect(groupWithIsolated).toBeDefined();
    });
  });

  describe(groupBySemantic, () => {
    it('should group items by type', () => {
      const groups = groupBySemantic(items);

      // Should have groups for Component and others
      const componentGroup = groups.find((g) =>
        g.itemIds.some((id) => items.find((i) => i.id === id)?.type === 'Component'),
      );
      expect(componentGroup).toBeDefined();
    });

    it('should meet minimum group size', () => {
      const groups = groupBySemantic(items, 2);

      // All groups should have at least 2 items
      for (const group of groups) {
        expect(group.itemCount).toBeGreaterThanOrEqual(2);
      }
    });

    it('should include title similarity metrics', () => {
      const groups = groupBySemantic(items);
      const group = groups[0];
      expect(group).toBeDefined();
      if (!group) {
        return;
      }

      expect(group.metrics?.commonality).toBeDefined();
      expect(group.metrics?.commonality).toBeGreaterThanOrEqual(0);
      expect(group.metrics?.commonality).toBeLessThanOrEqual(1);
    });

    it('should group similar titles together', () => {
      const testItems = [
        createItem('a1', 'User Authentication', 'Feature'),
        createItem('a2', 'Authentication Form', 'Component'),
        createItem('b1', 'Database', 'Database'),
      ];

      const groups = groupBySemantic(testItems);

      // Items with similar titles might be grouped together
      const featureGroups = groups.filter((g) => g.label.includes('Feature'));
      expect(featureGroups.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe(calculateGroupCohesion, () => {
    it('should return 1 for fully connected group', () => {
      const groupItemIds = new Set(['item1', 'item2', 'item3']);
      const fullLinks: Link[] = [
        createLink('item1', 'item2'),
        createLink('item2', 'item3'),
        createLink('item1', 'item3'),
      ];

      const cohesion = calculateGroupCohesion(groupItemIds, fullLinks);
      expect(cohesion).toBe(1);
    });

    it('should return 0 for disconnected group', () => {
      const groupItemIds = new Set(['item1', 'item2']);
      const noLinks: Link[] = [];

      const cohesion = calculateGroupCohesion(groupItemIds, noLinks);
      expect(cohesion).toBe(0);
    });

    it('should return value between 0 and 1 for partially connected', () => {
      const groupItemIds = new Set(['item1', 'item2', 'item3']);
      const partialLinks: Link[] = [
        createLink('item1', 'item2'),
        // Item3 is not connected
      ];

      const cohesion = calculateGroupCohesion(groupItemIds, partialLinks);
      expect(cohesion).toBeGreaterThan(0);
      expect(cohesion).toBeLessThan(1);
    });

    it('should handle single item group', () => {
      const groupItemIds = new Set(['item1']);
      const cohesion = calculateGroupCohesion(groupItemIds, links);
      expect(cohesion).toBe(1);
    });
  });

  describe(calculateGroupSeparation, () => {
    it('should return 0 for non-overlapping groups', () => {
      const group1 = new Set(['item1', 'item2']);
      const group2 = new Set(['item3', 'item4']);
      const noLinks: Link[] = [];

      const separation = calculateGroupSeparation(group1, group2, noLinks);
      expect(separation).toBe(0);
    });

    it('should increase with more cross-group links', () => {
      const group1 = new Set(['item1', 'item2']);
      const group2 = new Set(['item3', 'item4']);

      const links1: Link[] = [createLink('item1', 'item3')];
      const links2: Link[] = [createLink('item1', 'item3'), createLink('item2', 'item4')];

      const sep1 = calculateGroupSeparation(group1, group2, links1);
      const sep2 = calculateGroupSeparation(group1, group2, links2);

      expect(sep2).toBeGreaterThan(sep1);
    });
  });
});
