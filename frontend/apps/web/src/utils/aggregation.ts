// Aggregation system for grouping items by type and shared dependencies
// Supports type-based grouping, dependency detection, and simplified Louvain community detection

import type { Item, Link } from '@tracertm/types';

/**
 * Aggregated group of items
 */
export interface AggregateGroup {
  id: string;
  type: string;
  label: string;
  itemIds: string[];
  itemCount: number;
  parentGroupId?: string;
  commonDependencies: string[];
  commonDependents: string[];
}

/**
 * Aggregation configuration
 */
export interface AggregationConfig {
  /** Enable type-based grouping */
  groupByType: boolean;
  /** Enable dependency-based grouping */
  groupByDependency: boolean;
  /** Minimum items in group for aggregation */
  minGroupSize: number;
  /** Maximum group size before splitting */
  maxGroupSize: number;
  /** Enable Louvain community detection */
  enableCommunityDetection: boolean;
  /** Community detection threshold (0-1) */
  communityThreshold: number;
}

const DEFAULT_CONFIG: AggregationConfig = {
  communityThreshold: Number('0.5'),
  enableCommunityDetection: true,
  groupByDependency: true,
  groupByType: true,
  maxGroupSize: Number('50'),
  minGroupSize: Number('3'),
};

const MIN_COMMUNITY_SIZE = Number('2');
const PERCENT_BASE = Number('100');
const ZERO = Number('0');
const ONE = Number('1');

const createConfig = function createConfig(config: Partial<AggregationConfig>): AggregationConfig {
  return { ...DEFAULT_CONFIG, ...config };
};

const getGroupKey = function getGroupKey(item: Item): string {
  return (item.type || item.view || 'unknown').toLowerCase();
};

/**
 * Group items by type
 */
const groupItemsByType = function groupItemsByType(
  items: Item[],
  minSize = DEFAULT_CONFIG.minGroupSize,
): Map<string, Item[]> {
  const groups = new Map<string, Item[]>();

  for (const item of items) {
    const typeKey = getGroupKey(item);
    if (!groups.has(typeKey)) {
      groups.set(typeKey, []);
    }
    groups.get(typeKey)!.push(item);
  }

  const filtered = new Map<string, Item[]>();
  for (const [typeKey, groupItems] of groups) {
    if (groupItems.length >= minSize) {
      filtered.set(typeKey, groupItems);
    }
  }

  return filtered;
};

/**
 * Find common dependencies between items
 */
const findCommonDependencies = function findCommonDependencies(
  itemIds: string[],
  links: Link[],
): string[] {
  if (itemIds.length === ZERO) {
    return [];
  }

  const dependencyMap = new Map<string, number>();
  const itemIdSet = new Set(itemIds);

  for (const link of links) {
    if (itemIdSet.has(link.sourceId) && !itemIdSet.has(link.targetId)) {
      const count = dependencyMap.get(link.targetId) ?? ZERO;
      dependencyMap.set(link.targetId, count + ONE);
    }
  }

  const common: string[] = [];
  for (const [depId, count] of dependencyMap) {
    if (count === itemIds.length) {
      common.push(depId);
    }
  }

  return common;
};

/**
 * Find common dependents (items that depend on this group)
 */
const findCommonDependents = function findCommonDependents(
  itemIds: string[],
  links: Link[],
): string[] {
  if (itemIds.length === ZERO) {
    return [];
  }

  const dependentMap = new Map<string, number>();
  const itemIdSet = new Set(itemIds);

  for (const link of links) {
    if (itemIdSet.has(link.targetId) && !itemIdSet.has(link.sourceId)) {
      const count = dependentMap.get(link.sourceId) ?? ZERO;
      dependentMap.set(link.sourceId, count + ONE);
    }
  }

  const common: string[] = [];
  for (const [depId, count] of dependentMap) {
    if (count === itemIds.length) {
      common.push(depId);
    }
  }

  return common;
};

const typeGroupToAggregate = function typeGroupToAggregate(
  typeKey: string,
  groupItems: Item[],
  groupIndex: number,
  links: Link[],
): AggregateGroup {
  const itemIds = groupItems.map((item) => item.id);
  const commonDeps = findCommonDependencies(itemIds, links);
  const commonDependents = findCommonDependents(itemIds, links);
  const groupLabel = `${typeKey.charAt(0).toUpperCase() + typeKey.slice(1)} (${groupItems.length})`;

  return {
    commonDependencies: commonDeps,
    commonDependents,
    id: `agg-${typeKey}-${groupIndex}`,
    itemCount: groupItems.length,
    itemIds,
    label: groupLabel,
    type: typeKey,
  };
};

const createTypeGroups = function createTypeGroups(
  items: Item[],
  links: Link[],
  minGroupSize: number,
): AggregateGroup[] {
  const groups: AggregateGroup[] = [];
  const typeGroups = groupItemsByType(items, minGroupSize);
  let groupIndex = ZERO;

  for (const [typeKey, groupItems] of typeGroups) {
    groups.push(typeGroupToAggregate(typeKey, groupItems, groupIndex, links));
    groupIndex += ONE;
  }

  return groups;
};

/**
 * Create aggregate groups from items
 */
const createAggregateGroups = function createAggregateGroups(
  items: Item[],
  links: Link[],
  config: Partial<AggregationConfig> = {},
): AggregateGroup[] {
  const finalConfig = createConfig(config);
  const groups: AggregateGroup[] = [];

  if (finalConfig.groupByType) {
    groups.push(...createTypeGroups(items, links, finalConfig.minGroupSize));
  }

  if (finalConfig.enableCommunityDetection && groups.length === ZERO) {
    const communities = detectCommunities(items, links);
    for (const community of communities) {
      if (community.itemCount >= finalConfig.minGroupSize) {
        groups.push(community);
      }
    }
  }

  return groups;
};

const buildAdjacencyMap = function buildAdjacencyMap(
  items: Item[],
  links: Link[],
): Map<string, Set<string>> {
  const adjacencyMap = new Map<string, Set<string>>();
  for (const item of items) {
    adjacencyMap.set(item.id, new Set());
  }
  for (const link of links) {
    const sources = adjacencyMap.get(link.sourceId);
    const targets = adjacencyMap.get(link.targetId);
    if (sources) {
      sources.add(link.targetId);
    }
    if (targets) {
      targets.add(link.sourceId);
    }
  }
  return adjacencyMap;
};

const depthFirstSearch = function (
  nodeId: string,
  adjacencyMap: Map<string, Set<string>>,
  visited: Set<string>,
  community: string[],
): void {
  if (visited.has(nodeId)) {
    return;
  }
  visited.add(nodeId);
  community.push(nodeId);
  const neighbors = adjacencyMap.get(nodeId) ?? new Set();
  for (const neighbor of neighbors) {
    if (!visited.has(neighbor)) {
      depthFirstSearch(neighbor, adjacencyMap, visited, community);
    }
  }
};

const buildCommunityGroup = function buildCommunityGroup(
  communityItemIds: string[],
  links: Link[],
  groupIndex: number,
): AggregateGroup {
  const commonDeps = findCommonDependencies(communityItemIds, links);
  const commonDependents = findCommonDependents(communityItemIds, links);

  return {
    commonDependencies: commonDeps,
    commonDependents,
    id: `community-${groupIndex}`,
    itemCount: communityItemIds.length,
    itemIds: communityItemIds,
    label: `Community ${groupIndex + ONE} (${communityItemIds.length})`,
    type: 'community',
  };
};

/**
 * Simplified Louvain community detection algorithm
 * This is a simplified version suitable for UI graphs
 */
const detectCommunities = function detectCommunities(
  items: Item[],
  links: Link[],
): AggregateGroup[] {
  const adjacencyMap = buildAdjacencyMap(items, links);
  const visited = new Set<string>();
  const communities: AggregateGroup[] = [];
  let groupIndex = ZERO;

  for (const item of items) {
    if (visited.has(item.id)) {
      continue;
    }
    const community: string[] = [];
    depthFirstSearch(item.id, adjacencyMap, visited, community);
    if (community.length < MIN_COMMUNITY_SIZE) {
      continue;
    }
    communities.push(buildCommunityGroup(community, links, groupIndex));
    groupIndex += ONE;
  }

  return communities;
};

export interface ApplyAggregationOptions {
  config?: Partial<AggregationConfig>;
  expandedGroupIds?: Set<string>;
}

const groupToAggregateItem = function groupToAggregateItem(
  group: AggregateGroup,
  baseItem: Item,
): Item {
  return {
    createdAt: new Date().toISOString(),
    description: `Aggregated group of ${group.itemCount} ${group.type} items`,
    id: group.id,
    metadata: {
      aggregateType: group.type,
      commonDependencies: group.commonDependencies,
      commonDependents: group.commonDependents,
      itemCount: group.itemCount,
      itemIds: group.itemIds,
    },
    priority: 'medium' as const,
    projectId: baseItem.projectId ?? 'unknown',
    status: 'done' as const,
    title: group.label,
    type: 'aggregate',
    updatedAt: new Date().toISOString(),
    version: ONE,
    view: baseItem.view ?? 'FEATURE',
  };
};

const isItemInGroup = function isItemInGroup(group: AggregateGroup, id: string): boolean {
  return group.itemIds.includes(id);
};

const linkVisible = function linkVisible(
  link: Link,
  visibleItemIds: Set<string>,
  groups: AggregateGroup[],
): boolean {
  if (visibleItemIds.has(link.sourceId) || visibleItemIds.has(link.targetId)) {
    return true;
  }
  return groups.some((group) => {
    const sourceInGroup = isItemInGroup(group, link.sourceId);
    const targetInGroup = isItemInGroup(group, link.targetId);
    return (
      (sourceInGroup && visibleItemIds.has(link.targetId)) ||
      (targetInGroup && visibleItemIds.has(link.sourceId))
    );
  });
};

const buildAggregateItems = function buildAggregateItems(
  groups: AggregateGroup[],
  items: Item[],
): Item[] {
  const baseItem = items[ZERO] ?? ({} as Item);
  return groups.map((group) => groupToAggregateItem(group, baseItem));
};

const buildAggregatedItemIdSet = function buildAggregatedItemIdSet(
  groups: AggregateGroup[],
): Set<string> {
  const aggregatedItemIds = new Set<string>();
  for (const group of groups) {
    for (const itemId of group.itemIds) {
      aggregatedItemIds.add(itemId);
    }
  }
  return aggregatedItemIds;
};

const addToHiddenMap = function addToHiddenMap(
  hiddenByAggregation: Map<string, Item[]>,
  groupId: string,
  item: Item,
): void {
  const list = hiddenByAggregation.get(groupId) ?? [];
  list.push(item);
  hiddenByAggregation.set(groupId, list);
};

const collectVisibleItems = function collectVisibleItems(
  items: Item[],
  groups: AggregateGroup[],
  aggregateItems: Item[],
  expandedGroupIds: Set<string>,
): {
  hiddenByAggregation: Map<string, Item[]>;
  visibleItems: Item[];
} {
  const aggregatedItemIds = buildAggregatedItemIdSet(groups);
  const visibleItems: Item[] = [];
  const hiddenByAggregation = new Map<string, Item[]>();

  for (const item of items) {
    if (!aggregatedItemIds.has(item.id)) {
      visibleItems.push(item);
      continue;
    }

    const group = groups.find((candidate) => candidate.itemIds.includes(item.id));
    if (group?.id && expandedGroupIds.has(group.id)) {
      visibleItems.push(item);
    } else if (group) {
      addToHiddenMap(hiddenByAggregation, group.id, item);
    }
  }

  for (const aggregateItem of aggregateItems) {
    if (!expandedGroupIds.has(aggregateItem.id)) {
      visibleItems.push(aggregateItem);
    }
  }

  return { hiddenByAggregation, visibleItems };
};

const collectVisibleLinks = function collectVisibleLinks(
  links: Link[],
  visibleItems: Item[],
  groups: AggregateGroup[],
): Link[] {
  const visibleItemIds = new Set(visibleItems.map((item) => item.id));
  return links.filter((link) => linkVisible(link, visibleItemIds, groups));
};

/**
 * Apply aggregation to items and links
 * Returns filtered items/links with aggregates and expanded/collapsed state
 */
const applyAggregation = function applyAggregation(
  items: Item[],
  links: Link[],
  options: ApplyAggregationOptions = {},
): {
  groups: AggregateGroup[];
  hiddenByAggregation: Map<string, Item[]>;
  items: Item[];
  links: Link[];
} {
  const config = options.config ?? {};
  const expandedGroupIds = options.expandedGroupIds ?? new Set<string>();
  const groups = createAggregateGroups(items, links, config);
  const aggregateItems = buildAggregateItems(groups, items);
  const { hiddenByAggregation, visibleItems } = collectVisibleItems(
    items,
    groups,
    aggregateItems,
    expandedGroupIds,
  );
  const visibleLinks = collectVisibleLinks(links, visibleItems, groups);

  return {
    groups,
    hiddenByAggregation,
    items: visibleItems,
    links: visibleLinks,
  };
};

/**
 * Toggle aggregation group expanded state
 */
const toggleAggregateGroup = function toggleAggregateGroup(
  groupId: string,
  expandedGroups: Set<string>,
): Set<string> {
  const newExpanded = new Set(expandedGroups);
  if (newExpanded.has(groupId)) {
    newExpanded.delete(groupId);
  } else {
    newExpanded.add(groupId);
  }
  return newExpanded;
};

/**
 * Calculate aggregation savings (number of items hidden)
 */
const calculateAggregationSavings = function calculateAggregationSavings(
  groups: AggregateGroup[],
  expandedGroupIds: Set<string>,
): number {
  let hidden = ZERO;
  for (const group of groups) {
    if (!expandedGroupIds.has(group.id)) {
      hidden += Math.max(ZERO, group.itemCount - ONE);
    }
  }
  return hidden;
};

/**
 * Get statistics about aggregation
 */
const getAggregationStats = function getAggregationStats(
  items: Item[],
  groups: AggregateGroup[],
): {
  aggregateNodes: number;
  estimatedNodeCount: number;
  reductionPercent: number;
  totalAggregated: number;
  totalItems: number;
} {
  const totalItems = items.length;
  const totalAggregated = groups.reduce((sum, group) => sum + group.itemCount, ZERO);
  const aggregateNodes = groups.length;

  return {
    aggregateNodes,
    estimatedNodeCount: totalItems - totalAggregated + aggregateNodes,
    reductionPercent: Math.round(((totalAggregated - aggregateNodes) / totalItems) * PERCENT_BASE),
    totalAggregated,
    totalItems,
  };
};

export {
  applyAggregation,
  calculateAggregationSavings,
  createAggregateGroups,
  findCommonDependencies,
  findCommonDependents,
  getAggregationStats,
  groupItemsByType,
  toggleAggregateGroup,
};
