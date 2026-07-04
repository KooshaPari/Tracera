// Grouping algorithms for graph visualization
// Supports multiple grouping strategies for organizing items in the graph

import type { Item, Link } from '@tracertm/types';

/**
 * Grouping strategy options
 */
export type GroupingStrategy =
  | 'link-targets' // Group items that share common targets
  | 'dependencies' // Group items that depend on same things
  | 'paths' // Group items on same journey/trace path
  | 'semantic'; // Group by semantic similarity (if embeddings available)

/**
 * Result of grouping operation
 */
export interface GroupResult {
  groupId: string;
  strategy: GroupingStrategy;
  label: string;
  itemIds: string[];
  itemCount: number;
  metrics?: {
    cohesion?: number; // 0-1: how tightly grouped
    separation?: number; // 0-1: how distinct from other groups
    commonality?: number; // 0-1: shared characteristics
  };
  metadata?: Record<string, unknown>;
}

/**
 * Group items by shared link targets
 * Items that link to the same targets are grouped together
 *
 * @param items Items to group
 * @param links Links between items
 * @param minGroupSize Minimum items to form a group
 * @returns Array of groups
 */
export function groupByLinkTargets(items: Item[], links: Link[], minGroupSize = 2): GroupResult[] {
  const targetMap = new Map<string, Set<string>>();
  const itemMap = new Map(items.map((i) => [i.id, i]));

  // Build target map: item -> set of targets it links to
  for (const link of links) {
    if (!targetMap.has(link.sourceId)) {
      targetMap.set(link.sourceId, new Set());
    }
    targetMap.get(link.sourceId)!.add(link.targetId);
  }

  // Group items with same targets
  const groupMap = new Map<string, Set<string>>();
  let groupIndex = 0;

  for (const [itemId, targets] of targetMap) {
    if (targets.size === 0 || !itemMap.has(itemId)) {
      continue;
    }

    // Create a key from sorted targets
    const targetKey = [...targets].toSorted().join('|');

    if (!groupMap.has(targetKey)) {
      groupMap.set(targetKey, new Set());
    }
    groupMap.get(targetKey)!.add(itemId);
  }

  // Convert to GroupResult
  const groups: GroupResult[] = [];
  for (const [targetKey, itemIds] of groupMap) {
    if (itemIds.size >= minGroupSize) {
      const targets = targetKey.split('|').filter((t) => t.length > 0);
      groups.push({
        groupId: `group-targets-${groupIndex++}`,
        itemCount: itemIds.size,
        itemIds: [...itemIds],
        label: `Items targeting ${targets.length} common targets`,
        metadata: {
          commonTargets: targets,
          targetCount: targets.length,
        },
        metrics: {
          cohesion: Math.min(1, targets.length / 10),
          commonality: 1,
        },
        strategy: 'link-targets',
      });
    }
  }

  return groups;
}

/**
 * Group items that depend on the same things
 * Items with identical dependencies are grouped together
 *
 * @param items Items to group
 * @param links Links between items
 * @param minGroupSize Minimum items to form a group
 * @returns Array of groups
 */
export function groupByDependencies(items: Item[], links: Link[], minGroupSize = 2): GroupResult[] {
  const dependencyMap = new Map<string, Set<string>>();
  const itemMap = new Map(items.map((i) => [i.id, i]));

  // Build dependency map: item -> set of its dependencies
  for (const link of links) {
    if (itemMap.has(link.sourceId)) {
      if (!dependencyMap.has(link.sourceId)) {
        dependencyMap.set(link.sourceId, new Set());
      }
      dependencyMap.get(link.sourceId)!.add(link.targetId);
    }
  }

  // Group items with same dependencies
  const groupMap = new Map<string, Set<string>>();
  let groupIndex = 0;

  for (const [itemId, deps] of dependencyMap) {
    if (deps.size === 0) {
      continue;
    }

    const depKey = [...deps].toSorted().join('|');

    if (!groupMap.has(depKey)) {
      groupMap.set(depKey, new Set());
    }
    groupMap.get(depKey)!.add(itemId);
  }

  // Convert to GroupResult
  const groups: GroupResult[] = [];
  for (const [depKey, itemIds] of groupMap) {
    if (itemIds.size >= minGroupSize) {
      const deps = depKey.split('|').filter((d) => d.length > 0);
      groups.push({
        groupId: `group-deps-${groupIndex++}`,
        itemCount: itemIds.size,
        itemIds: [...itemIds],
        label: `Items with ${deps.length} shared dependencies`,
        metadata: {
          dependencyCount: deps.length,
          sharedDependencies: deps,
        },
        metrics: {
          cohesion: Math.min(1, deps.length / 10),
          commonality: 1,
        },
        strategy: 'dependencies',
      });
    }
  }

  return groups;
}

/**
 * Group items that lie on the same trace path
 * Items that form a connected chain (journey) are grouped together
 *
 * @param items Items to group
 * @param links Links between items
 * @param minGroupSize Minimum items to form a group
 * @returns Array of groups
 */
export function groupByPaths(items: Item[], links: Link[], minGroupSize = 2): GroupResult[] {
  const itemSet = new Set(items.map((i) => i.id));
  const adjacency = new Map<string, Set<string>>();

  // Build adjacency list
  for (const item of items) {
    adjacency.set(item.id, new Set());
  }

  for (const link of links) {
    if (itemSet.has(link.sourceId) && itemSet.has(link.targetId)) {
      adjacency.get(link.sourceId)!.add(link.targetId);
      adjacency.get(link.targetId)!.add(link.sourceId);
    }
  }

  // Find connected components (paths)
  const visited = new Set<string>();
  const groups: GroupResult[] = [];
  let groupIndex = 0;

  function dfs(start: string): string[] {
    const path: string[] = [];
    const queue = [start];

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (visited.has(current)) {
        continue;
      }

      visited.add(current);
      path.push(current);

      const neighbors = adjacency.get(current) ?? new Set();
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          queue.push(neighbor);
        }
      }
    }

    return path;
  }

  // Find all connected paths
  for (const itemId of itemSet) {
    if (!visited.has(itemId)) {
      const path = dfs(itemId);
      if (path.length >= minGroupSize) {
        groups.push({
          groupId: `group-path-${groupIndex++}`,
          itemCount: path.length,
          itemIds: path,
          label: `Trace path (${path.length} items)`,
          metadata: {
            pathLength: path.length,
          },
          metrics: {
            cohesion: 1, // Connected components have perfect cohesion
            separation: 0.5,
          },
          strategy: 'paths',
        });
      }
    }
  }

  return groups;
}

/**
 * Group items by semantic similarity
 * Groups items with similar titles, types, or embeddings
 *
 * @param items Items to group
 * @param minGroupSize Minimum items to form a group
 * @param embeddingDistance Distance threshold for semantic similarity (0-1)
 * @returns Array of groups
 */
export function groupBySemantic(
  items: Item[],
  minGroupSize = 2,
  _embeddingDistance = 0.3,
): GroupResult[] {
  const groups: GroupResult[] = [];
  let groupIndex = 0;

  // Group by type first (semantic baseline)
  const typeGroups = new Map<string, Item[]>();
  for (const item of items) {
    const type = (item.type || 'unknown').toLowerCase();
    if (!typeGroups.has(type)) {
      typeGroups.set(type, []);
    }
    typeGroups.get(type)!.push(item);
  }

  // Convert type groups to GroupResult
  for (const [type, typeItems] of typeGroups) {
    if (typeItems.length >= minGroupSize) {
      // Calculate title similarity within type group
      const titles = typeItems.map((i) => i.title);
      const commonality = calculateTitleSimilarity(titles);

      groups.push({
        groupId: `group-semantic-${groupIndex++}`,
        itemCount: typeItems.length,
        itemIds: typeItems.map((i) => i.id),
        label: `${type} items (${typeItems.length})`,
        metadata: {
          titleSimilarity: commonality,
          type,
        },
        metrics: {
          cohesion: 0.8, // Type-based cohesion
          commonality,
          separation: 0.6,
        },
        strategy: 'semantic',
      });
    }
  }

  return groups;
}

/**
 * Calculate similarity between titles using string distance
 * Returns a value 0-1 where 1 is maximum similarity
 */
function calculateTitleSimilarity(titles: string[]): number {
  if (titles.length < 2) {
    return 1;
  }

  let totalSimilarity = 0;
  let comparisons = 0;

  for (let i = 0; i < titles.length; i += 1) {
    for (let j = i + 1; j < titles.length; j += 1) {
      const title1 = titles[i];
      const title2 = titles[j];
      if (title1 && title2) {
        const similarity = stringSimilarity(title1, title2);
        totalSimilarity += similarity;
        comparisons += 1;
      }
    }
  }

  return comparisons > 0 ? totalSimilarity / comparisons : 0;
}

/**
 * Calculate similarity between two strings (0-1)
 * Uses a simple Levenshtein-inspired approach
 */
function stringSimilarity(a: string, b: string): number {
  const s1 = a.toLowerCase();
  const s2 = b.toLowerCase();

  // Check for substring matches (highest similarity)
  if (s1.includes(s2) || s2.includes(s1)) {
    return 1;
  }

  // Calculate character overlap
  const chars1 = new Set(s1);
  const chars2 = new Set(s2);
  const intersection = new Set([...chars1].filter((c) => chars2.has(c)));

  const union = new Set([...chars1, ...chars2]);

  return union.size === 0 ? 0 : intersection.size / union.size;
}

/**
 * Combine multiple grouping results by finding intersections
 * Useful for finding items that match multiple grouping criteria
 */
export function intersectGroupResults(groupSets: GroupResult[][]): GroupResult[] {
  if (groupSets.length === 0) {
    return [];
  }

  // Start with first set
  let current = groupSets[0]!.map((g) => new Set(g.itemIds));

  // Intersect with subsequent sets
  for (let i = 1; i < groupSets.length; i += 1) {
    const nextSets = groupSets[i]!.map((g) => new Set(g.itemIds));

    current = current.flatMap((currentSet) => {
      const intersections: Set<string>[] = [];

      for (const nextSet of nextSets) {
        const intersection = new Set([...currentSet].filter((id) => nextSet.has(id)));
        if (intersection.size > 0) {
          intersections.push(intersection);
        }
      }

      return intersections;
    });
  }

  // Convert back to GroupResult
  return current.map((itemSet, idx) => ({
    groupId: `group-intersection-${idx}`,
    strategy: 'paths', // Default strategy for intersections
    label: `Intersection group (${itemSet.size} items)`,
    itemIds: [...itemSet],
    itemCount: itemSet.size,
    metrics: {
      cohesion: 0.8,
      commonality: 0.7,
      separation: 0.5,
    },
  }));
}

/**
 * Calculate cohesion score for a group
 * Higher score means items in group are more connected
 */
export function calculateGroupCohesion(groupItemIds: Set<string>, links: Link[]): number {
  if (groupItemIds.size < 2) {
    return 1;
  }

  let internalLinks = 0;
  let totalLinks = 0;

  for (const link of links) {
    const sourceInGroup = groupItemIds.has(link.sourceId);
    const targetInGroup = groupItemIds.has(link.targetId);

    if (sourceInGroup || targetInGroup) {
      totalLinks += 1;
      if (sourceInGroup && targetInGroup) {
        internalLinks += 1;
      }
    }
  }

  return totalLinks === 0 ? 0 : internalLinks / totalLinks;
}

/**
 * Calculate separation score between two groups
 * Lower score means groups are more independent
 */
export function calculateGroupSeparation(
  group1ItemIds: Set<string>,
  group2ItemIds: Set<string>,
  links: Link[],
): number {
  let crossGroupLinks = 0;

  for (const link of links) {
    const source = group1ItemIds.has(link.sourceId) ? 1 : group2ItemIds.has(link.sourceId) ? 2 : 0;
    const target = group1ItemIds.has(link.targetId) ? 1 : group2ItemIds.has(link.targetId) ? 2 : 0;

    // Cross-group link exists
    if ((source === 1 && target === 2) || (source === 2 && target === 1)) {
      crossGroupLinks += 1;
    }
  }

  const maxPossible = group1ItemIds.size * group2ItemIds.size;
  return maxPossible === 0 ? 0 : crossGroupLinks / maxPossible;
}
