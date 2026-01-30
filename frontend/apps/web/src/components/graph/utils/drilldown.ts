// Drill-down navigation utilities for graph visualization
// Supports progressive disclosure: Project → Repository → Module → File → Function

import type { Item, Link } from "@tracertm/types";
import type { HierarchyNode } from "./hierarchy";

/**
 * Drill-down level definitions
 */
export type DrillDownLevel =
	| "project" // Top level: entire project
	| "repository" // Code repository
	| "module" // Module or package
	| "file" // Individual file
	| "function"; // Function/method level

/**
 * Drill-down context for navigation
 */
export interface DrillDownContext {
	currentLevel: DrillDownLevel;
	itemId: string;
	itemTitle: string;
	parentId?: string;
	parentTitle?: string;
	breadcrumbs: DrillDownBreadcrumb[];
	visibleItems: string[]; // Items visible at current level
	childrenAvailable: boolean;
}

/**
 * Breadcrumb for drill-down navigation
 */
export interface DrillDownBreadcrumb {
	level: DrillDownLevel;
	itemId: string;
	itemTitle: string;
	icon: string;
}

/**
 * Node group for drill-down expansion
 */
export interface DrillDownNodeGroup {
	groupId: string;
	level: DrillDownLevel;
	label: string;
	parentItemId: string;
	itemIds: string[];
	itemCount: number;
	isExpanded: boolean;
	canExpand: boolean;
	icon: string;
	color: string;
	metadata?: Record<string, unknown>;
}

/**
 * Level hierarchy definition
 */
const LEVEL_HIERARCHY: Record<DrillDownLevel, number> = {
	project: 0,
	repository: 1,
	module: 2,
	file: 3,
	function: 4,
};

/**
 * Icon mapping for levels
 */
const LEVEL_ICONS: Record<DrillDownLevel, string> = {
	project: "Package",
	repository: "GitRepository",
	module: "Folder",
	file: "FileCode",
	function: "Function",
};

/**
 * Color mapping for levels
 */
const LEVEL_COLORS: Record<DrillDownLevel, string> = {
	project: "#3b82f6",
	repository: "#8b5cf6",
	module: "#ec4899",
	file: "#f59e0b",
	function: "#10b981",
};

/**
 * Infer drill-down level from item type
 */
export function inferDrillDownLevel(itemType: string): DrillDownLevel {
	const lower = itemType.toLowerCase();

	if (lower.includes("project")) return "project";
	if (lower.includes("repo") || lower.includes("repository"))
		return "repository";
	if (lower.includes("module") || lower.includes("package")) return "module";
	if (lower.includes("file") || lower.includes("code")) return "file";
	if (lower.includes("function") || lower.includes("method")) return "function";

	return "module"; // Default
}

/**
 * Determine next drill-down level
 */
export function getNextLevel(current: DrillDownLevel): DrillDownLevel | null {
	const levels: DrillDownLevel[] = [
		"project",
		"repository",
		"module",
		"file",
		"function",
	];
	const currentIndex = levels.indexOf(current);

	if (currentIndex === -1 || currentIndex === levels.length - 1) return null;
	return levels[currentIndex + 1];
}

/**
 * Determine previous drill-down level
 */
export function getPreviousLevel(
	current: DrillDownLevel,
): DrillDownLevel | null {
	const levels: DrillDownLevel[] = [
		"project",
		"repository",
		"module",
		"file",
		"function",
	];
	const currentIndex = levels.indexOf(current);

	if (currentIndex <= 0) return null;
	return levels[currentIndex - 1];
}

/**
 * Create drill-down breadcrumbs from hierarchy path
 */
export function createBreadcrumbs(
	itemId: string,
	hierarchyMap: Map<string, HierarchyNode>,
): DrillDownBreadcrumb[] {
	const node = hierarchyMap.get(itemId);
	if (!node) return [];

	const breadcrumbs: DrillDownBreadcrumb[] = [];

	for (const ancestorId of node.hierarchyPath) {
		const ancestorNode = hierarchyMap.get(ancestorId);
		if (ancestorNode) {
			const level = inferDrillDownLevel(ancestorNode.item.type);
			breadcrumbs.push({
				level,
				itemId: ancestorId,
				itemTitle: ancestorNode.item.title,
				icon: LEVEL_ICONS[level],
			});
		}
	}

	return breadcrumbs;
}

/**
 * Get children grouped by drill-down level
 */
export function getChildrenByDrillDownLevel(
	itemId: string,
	hierarchyMap: Map<string, HierarchyNode>,
	items: Item[],
): Map<DrillDownLevel, Item[]> {
	const node = hierarchyMap.get(itemId);
	if (!node) return new Map();

	const itemMap = new Map(items.map((i) => [i.id, i]));
	const levelGroups = new Map<DrillDownLevel, Item[]>();

	for (const childId of node.childrenIds) {
		const childItem = itemMap.get(childId);
		if (childItem) {
			const level = inferDrillDownLevel(childItem.type);

			if (!levelGroups.has(level)) {
				levelGroups.set(level, []);
			}
			levelGroups.get(level)!.push(childItem);
		}
	}

	return levelGroups;
}

/**
 * Create drill-down context for current navigation state
 */
export function createDrillDownContext(
	itemId: string,
	items: Item[],
	hierarchyMap: Map<string, HierarchyNode>,
	expandedGroups: Set<string> = new Set(),
): DrillDownContext {
	const node = hierarchyMap.get(itemId);
	const item = items.find((i) => i.id === itemId);

	if (!node || !item) {
		return {
			currentLevel: "project",
			itemId,
			itemTitle: "Unknown",
			breadcrumbs: [],
			visibleItems: [],
			childrenAvailable: false,
		};
	}

	const breadcrumbs = createBreadcrumbs(itemId, hierarchyMap);
	const childrenByLevel = getChildrenByDrillDownLevel(
		itemId,
		hierarchyMap,
		items,
	);

	// Determine visible items based on expansions
	const visibleItems: string[] = [];
	for (const [, children] of childrenByLevel) {
		for (const child of children) {
			visibleItems.push(child.id);
		}
	}

	const parentNode = node.parentId
		? hierarchyMap.get(node.parentId)
		: undefined;

	return {
		currentLevel: inferDrillDownLevel(item.type),
		itemId,
		itemTitle: item.title,
		parentId: node.parentId,
		parentTitle: parentNode?.item.title,
		breadcrumbs,
		visibleItems,
		childrenAvailable: node.childrenIds.length > 0,
	};
}

/**
 * Create node groups for drill-down expansion
 */
export function createDrillDownNodeGroups(
	itemId: string,
	items: Item[],
	hierarchyMap: Map<string, HierarchyNode>,
	maxItemsPerGroup: number = 20,
): DrillDownNodeGroup[] {
	const node = hierarchyMap.get(itemId);
	if (!node) return [];

	const itemMap = new Map(items.map((i) => [i.id, i]));
	const childrenByLevel = getChildrenByDrillDownLevel(
		itemId,
		hierarchyMap,
		items,
	);
	const groups: DrillDownNodeGroup[] = [];

	const groupIndex = 0;

	for (const [level, children] of childrenByLevel) {
		if (children.length === 0) continue;

		// Split into sub-groups if too many items
		const subGroups = Math.ceil(children.length / maxItemsPerGroup);

		for (let i = 0; i < subGroups; i++) {
			const start = i * maxItemsPerGroup;
			const end = Math.min(start + maxItemsPerGroup, children.length);
			const groupChildren = children.slice(start, end);

			const label =
				subGroups > 1
					? `${level} (${start + 1}-${end})`
					: `${level} (${groupChildren.length})`;

			groups.push({
				groupId: `dd-${itemId}-${level}-${i}`,
				level,
				label,
				parentItemId: itemId,
				itemIds: groupChildren.map((c) => c.id),
				itemCount: groupChildren.length,
				isExpanded: false,
				canExpand: groupChildren.some(
					(c) => hierarchyMap.get(c.id)?.childrenIds.length ?? 0 > 0,
				),
				icon: LEVEL_ICONS[level],
				color: LEVEL_COLORS[level],
				metadata: {
					level,
					subGroupIndex: i,
					totalSubGroups: subGroups,
				},
			});
		}
	}

	return groups;
}

/**
 * Expand a drill-down node group
 */
export function expandDrillDownGroup(
	groupId: string,
	expandedGroups: Set<string>,
): Set<string> {
	const newExpanded = new Set(expandedGroups);
	newExpanded.add(groupId);
	return newExpanded;
}

/**
 * Collapse a drill-down node group
 */
export function collapseDrillDownGroup(
	groupId: string,
	expandedGroups: Set<string>,
): Set<string> {
	const newExpanded = new Set(expandedGroups);
	newExpanded.delete(groupId);
	return newExpanded;
}

/**
 * Toggle drill-down node group expansion
 */
export function toggleDrillDownGroup(
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
}

/**
 * Get all visible items for drill-down navigation
 */
export function getVisibleDrillDownItems(
	itemId: string,
	items: Item[],
	hierarchyMap: Map<string, HierarchyNode>,
	expandedGroups: Set<string>,
): Item[] {
	const node = hierarchyMap.get(itemId);
	if (!node) return [];

	const itemMap = new Map(items.map((i) => [i.id, i]));
	const visibleIds = new Set<string>();

	// Add children
	for (const childId of node.childrenIds) {
		visibleIds.add(childId);
	}

	// Add expanded grandchildren
	for (const groupId of expandedGroups) {
		// Parse group ID to check if it relates to this item
		if (groupId.startsWith(`dd-${itemId}-`)) {
			const groupIdx = groupId.split("-").pop();
			const node = hierarchyMap.get(itemId);

			if (node) {
				// Would need group index to item mapping for full implementation
				// This is simplified version
			}
		}
	}

	return Array.from(visibleIds)
		.map((id) => itemMap.get(id))
		.filter((item): item is Item => item !== undefined);
}

/**
 * Navigate to parent in drill-down
 */
export function navigateUp(
	itemId: string,
	hierarchyMap: Map<string, HierarchyNode>,
): string | null {
	const node = hierarchyMap.get(itemId);
	return node?.parentId ?? null;
}

/**
 * Navigate to specific child in drill-down
 */
export function navigateToChild(
	itemId: string,
	childIndex: number,
	hierarchyMap: Map<string, HierarchyNode>,
): string | null {
	const node = hierarchyMap.get(itemId);
	if (!node || childIndex < 0 || childIndex >= node.childrenIds.length) {
		return null;
	}

	return node.childrenIds[childIndex];
}

/**
 * Get drill-down path for lazy loading
 * Returns the sequence of item IDs from root to target
 */
export function getDrillDownPath(
	itemId: string,
	hierarchyMap: Map<string, HierarchyNode>,
): string[] {
	const node = hierarchyMap.get(itemId);
	if (!node) return [];

	return node.hierarchyPath;
}

/**
 * Calculate lazy loading requirements for drill-down
 * Returns items that need to be fetched for full drill-down experience
 */
export function calculateLazyLoadingRequirements(
	rootItemId: string,
	maxDepth: number,
	hierarchyMap: Map<string, HierarchyNode>,
): {
	itemsToLoad: string[];
	depth: number;
	estimatedSize: number;
} {
	const itemsToLoad = new Set<string>();
	const queue = [
		{
			itemId: rootItemId,
			currentDepth: 0,
		},
	];

	let maxDepthReached = 0;

	while (queue.length > 0) {
		const { itemId, currentDepth } = queue.shift()!;

		if (currentDepth > maxDepth) continue;

		itemsToLoad.add(itemId);
		maxDepthReached = Math.max(maxDepthReached, currentDepth);

		const node = hierarchyMap.get(itemId);
		if (node) {
			for (const childId of node.childrenIds) {
				if (!itemsToLoad.has(childId)) {
					queue.push({
						itemId: childId,
						currentDepth: currentDepth + 1,
					});
				}
			}
		}
	}

	return {
		itemsToLoad: Array.from(itemsToLoad),
		depth: maxDepthReached,
		estimatedSize: itemsToLoad.size,
	};
}

/**
 * Get drill-down statistics
 */
export function getDrillDownStats(
	itemId: string,
	hierarchyMap: Map<string, HierarchyNode>,
): {
	totalDescendants: number;
	depth: number;
	childCount: number;
	expandableCount: number;
} {
	const node = hierarchyMap.get(itemId);
	if (!node) {
		return {
			totalDescendants: 0,
			depth: 0,
			childCount: 0,
			expandableCount: 0,
		};
	}

	const expandableCount = node.childrenIds.filter((childId) => {
		const childNode = hierarchyMap.get(childId);
		return (childNode?.childrenIds.length ?? 0) > 0;
	}).length;

	return {
		totalDescendants: node.descendants.length,
		depth: node.depth,
		childCount: node.childrenIds.length,
		expandableCount,
	};
}
