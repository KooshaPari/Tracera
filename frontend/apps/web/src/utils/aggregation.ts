// Aggregation system for grouping items by type and shared dependencies
// Supports type-based grouping, dependency detection, and simplified Louvain community detection

import type { Item, Link } from "@tracertm/types";

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
	communityThreshold: 0.5,
	enableCommunityDetection: true,
	groupByDependency: true,
	groupByType: true,
	maxGroupSize: 50,
	minGroupSize: 3,
};

const MIN_COMMUNITY_SIZE = 2;
const PERCENT_BASE = 100;

/**
 * Group items by type
 */
export const groupItemsByType = (
	items: Item[],
	minSize = 3,
): Map<string, Item[]> => {
	const groups = new Map<string, Item[]>();

	for (const item of items) {
		const type = (item.type || item.view || "unknown").toLowerCase();
		if (!groups.has(type)) {
			groups.set(type, []);
		}
		groups.get(type)!.push(item);
	}

	// Filter by minimum size
	const filtered = new Map<string, Item[]>();
	for (const [type, groupItems] of groups) {
		if (groupItems.length >= minSize) {
			filtered.set(type, groupItems);
		}
	}

	return filtered;
};

/**
 * Find common dependencies between items
 */
export const findCommonDependencies = (
	itemIds: string[],
	links: Link[],
): string[] => {
	if (itemIds.length === 0) return [];

	// Find all items that these items depend on
	const dependencyMap = new Map<string, number>();
	const itemIdSet = new Set(itemIds);

	for (const link of links) {
		if (itemIdSet.has(link.sourceId) && !itemIdSet.has(link.targetId)) {
			const count = dependencyMap.get(link.targetId) || 0;
			dependencyMap.set(link.targetId, count + 1);
		}
	}

	// Find dependencies common to all items
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
export const findCommonDependents = (
	itemIds: string[],
	links: Link[],
): string[] => {
	if (itemIds.length === 0) return [];

	const dependentMap = new Map<string, number>();
	const itemIdSet = new Set(itemIds);

	for (const link of links) {
		if (itemIdSet.has(link.targetId) && !itemIdSet.has(link.sourceId)) {
			const count = dependentMap.get(link.sourceId) || 0;
			dependentMap.set(link.sourceId, count + 1);
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

const typeGroupToAggregate = (
	type: string,
	groupItems: Item[],
	groupIndex: number,
	links: Link[],
): AggregateGroup => {
	const itemIds = groupItems.map((i) => i.id);
	const commonDeps = findCommonDependencies(itemIds, links);
	const commonDepents = findCommonDependents(itemIds, links);
	return {
		commonDependencies: commonDeps,
		commonDependents: commonDepents,
		id: `agg-${type}-${groupIndex}`,
		itemCount: groupItems.length,
		itemIds,
		label: `${type.charAt(0).toUpperCase() + type.slice(1)} (${groupItems.length})`,
		type,
	};
};

/**
 * Create aggregate groups from items
 */
export const createAggregateGroups = (
	items: Item[],
	links: Link[],
	config: Partial<AggregationConfig> = {},
): AggregateGroup[] => {
	const finalConfig = { ...DEFAULT_CONFIG, ...config };
	const groups: AggregateGroup[] = [];

	if (finalConfig.groupByType) {
		const typeGroups = groupItemsByType(items, finalConfig.minGroupSize);
		let groupIndex = 0;
		for (const [type, groupItems] of typeGroups) {
			groups.push(
				typeGroupToAggregate(type, groupItems, groupIndex++, links),
			);
		}
	}

	if (finalConfig.enableCommunityDetection && groups.length === 0) {
		const communities = detectCommunities(items, links);
		for (const community of communities) {
			if (community.itemIds.length >= finalConfig.minGroupSize) {
				groups.push(community);
			}
		}
	}

	return groups;
};

const buildAdjacencyMap = (
	items: Item[],
	links: Link[],
): Map<string, Set<string>> => {
	const adjacencyMap = new Map<string, Set<string>>();
	for (const item of items) {
		adjacencyMap.set(item.id, new Set());
	}
	for (const link of links) {
		const sources = adjacencyMap.get(link.sourceId);
		const targets = adjacencyMap.get(link.targetId);
		if (sources) sources.add(link.targetId);
		if (targets) targets.add(link.sourceId);
	}
	return adjacencyMap;
};

const dfs = (
	nodeId: string,
	adjacencyMap: Map<string, Set<string>>,
	visited: Set<string>,
	community: string[],
): void => {
	if (visited.has(nodeId)) return;
	visited.add(nodeId);
	community.push(nodeId);
	const neighbors = adjacencyMap.get(nodeId) ?? new Set();
	for (const neighbor of neighbors) {
		if (!visited.has(neighbor)) dfs(neighbor, adjacencyMap, visited, community);
	}
};

/**
 * Simplified Louvain community detection algorithm
 * This is a simplified version suitable for UI graphs
 */
const detectCommunities = (
	items: Item[],
	links: Link[],
): AggregateGroup[] => {
	const adjacencyMap = buildAdjacencyMap(items, links);
	const visited = new Set<string>();
	const communities: AggregateGroup[] = [];
	let groupIndex = 0;

	for (const item of items) {
		if (visited.has(item.id)) continue;
		const community: string[] = [];
		dfs(item.id, adjacencyMap, visited, community);
		if (community.length < MIN_COMMUNITY_SIZE) continue;

		const commonDeps = findCommonDependencies(community, links);
		const commonDepents = findCommonDependents(community, links);
		communities.push({
			commonDependencies: commonDeps,
			commonDependents: commonDepents,
			id: `community-${groupIndex}`,
			itemCount: community.length,
			itemIds: community,
			label: `Community ${groupIndex + 1} (${community.length})`,
			type: "community",
		});
		groupIndex += 1;
	}

	return communities;
};

export interface ApplyAggregationOptions {
	config?: Partial<AggregationConfig>;
	expandedGroupIds?: Set<string>;
}

const groupToAggregateItem = (group: AggregateGroup, baseItem: Item): Item =>
	({
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
		priority: "medium" as const,
		projectId: baseItem?.projectId ?? "unknown",
		status: "done" as const,
		title: group.label,
		type: "aggregate",
		updatedAt: new Date().toISOString(),
		version: 1,
		view: baseItem?.view ?? "technical",
	}) as Item;

const linkVisible = (
	link: Link,
	visibleItemIds: Set<string>,
	groups: AggregateGroup[],
): boolean => {
	if (visibleItemIds.has(link.sourceId) || visibleItemIds.has(link.targetId)) {
		return true;
	}
	return groups.some((g) => {
		const inGroup = (id: string) => g.itemIds.includes(id);
		return (
			(inGroup(link.sourceId) && visibleItemIds.has(link.targetId)) ||
			(inGroup(link.targetId) && visibleItemIds.has(link.sourceId))
		);
	});
};

/**
 * Apply aggregation to items and links
 * Returns filtered items/links with aggregates and expanded/collapsed state
 */
export const applyAggregation = (
	items: Item[],
	links: Link[],
	options: ApplyAggregationOptions = {},
) => {
	const { config = {}, expandedGroupIds = new Set<string>() } = options;
	const groups = createAggregateGroups(items, links, config);
	const baseItem = items[0];
	const aggregateItems: Item[] = groups.map((g) =>
		groupToAggregateItem(g, baseItem ?? ({} as Item)),
	);

	const aggregatedItemIds = new Set(groups.flatMap((g) => g.itemIds));
	const visibleItems: Item[] = [];
	const hiddenByAggregation = new Map<string, Item[]>();

	for (const item of items) {
		if (!aggregatedItemIds.has(item.id)) {
			visibleItems.push(item);
			continue;
		}
		const group = groups.find((g) => g.itemIds.includes(item.id));
		if (group?.id && expandedGroupIds.has(group.id)) {
			visibleItems.push(item);
		} else if (group) {
			const list = hiddenByAggregation.get(group.id) ?? [];
			list.push(item);
			hiddenByAggregation.set(group.id, list);
		}
	}

	for (const aggItem of aggregateItems) {
		if (!expandedGroupIds.has(aggItem.id)) visibleItems.push(aggItem);
	}

	const visibleItemIds = new Set(visibleItems.map((i) => i.id));
	const visibleLinks = links.filter((link) =>
		linkVisible(link, visibleItemIds, groups),
	);

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
export const toggleAggregateGroup = (
	groupId: string,
	expandedGroups: Set<string>,
): Set<string> => {
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
export const calculateAggregationSavings = (
	groups: AggregateGroup[],
	expandedGroupIds: Set<string>,
): number => {
	let hidden = 0;
	for (const group of groups) {
		if (!expandedGroupIds.has(group.id)) {
			hidden += Math.max(0, group.itemCount - 1);
		}
	}
	return hidden;
};

/**
 * Get statistics about aggregation
 */
export const getAggregationStats = (
	items: Item[],
	groups: AggregateGroup[],
) => {
	const totalItems = items.length;
	const totalAggregated = groups.reduce((sum, g) => sum + g.itemCount, 0);
	const aggregateNodes = groups.length;

	return {
		aggregateNodes,
		estimatedNodeCount: totalItems - totalAggregated + aggregateNodes,
		reductionPercent: Math.round(
			((totalAggregated - aggregateNodes) / totalItems) * PERCENT_BASE,
		),
		totalAggregated,
		totalItems,
	};
};
