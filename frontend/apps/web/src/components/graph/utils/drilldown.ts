// Drill-down navigation utilities for graph visualization
// Supports progressive disclosure: Project → Repository → Module → File → Function

import type { Item } from '@tracertm/types';

import type { HierarchyNode } from './hierarchy';

/**
 * Drill-down level definitions
 */
export type DrillDownLevel =
  | 'project' // Top level: entire project
  | 'repository' // Code repository
  | 'module' // Module or package
  | 'file' // Individual file
  | 'function'; // Function/method level

/**
 * Drill-down context for navigation
 */
export interface DrillDownContext {
  currentLevel: DrillDownLevel;
  itemId: string;
  itemTitle: string;
  parentId?: string | undefined;
  parentTitle?: string | undefined;
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
  metadata?: Record<string, unknown> | undefined;
}

/**
 * Level hierarchy definition
 */
// Const LEVEL_HIERARCHY: Record<DrillDownLevel, number> = {
// 	Project: 0,
// 	Repository: 1,
// 	Module: 2,
// 	File: 3,
// 	Function: 4,
// };

/**
 * Icon mapping for levels
 */
const LEVEL_ICONS: Record<DrillDownLevel, string> = {
  file: 'FileCode',
  function: 'Function',
  module: 'Folder',
  project: 'Package',
  repository: 'GitRepository',
};

/**
 * Color mapping for levels
 */
const LEVEL_COLORS: Record<DrillDownLevel, string> = {
  file: '#f59e0b',
  function: '#10b981',
  module: '#ec4899',
  project: '#3b82f6',
  repository: '#8b5cf6',
};

/**
 * Infer drill-down level from item type
 */
export const inferDrillDownLevel = (itemType: string): DrillDownLevel => {
  const lower = itemType.toLowerCase();

  if (lower.includes('project')) {
    return 'project';
  }
  if (lower.includes('repo') || lower.includes('repository')) {
    return 'repository';
  }
  if (lower.includes('module') || lower.includes('package')) {
    return 'module';
  }
  if (lower.includes('file') || lower.includes('code')) {
    return 'file';
  }
  if (lower.includes('function') || lower.includes('method')) {
    return 'function';
  }

  return 'module'; // Default
};

/**
 * Determine next drill-down level
 */
export const getNextLevel = (current: DrillDownLevel): DrillDownLevel | null => {
  const levels: DrillDownLevel[] = ['project', 'repository', 'module', 'file', 'function'];
  const currentIndex = levels.indexOf(current);

  if (currentIndex === -1 || currentIndex === levels.length - 1) {
    return null;
  }
  return levels[currentIndex + 1] ?? null;
};

/**
 * Determine previous drill-down level
 */
export const getPreviousLevel = (current: DrillDownLevel): DrillDownLevel | null => {
  const levels: DrillDownLevel[] = ['project', 'repository', 'module', 'file', 'function'];
  const currentIndex = levels.indexOf(current);

  if (currentIndex <= 0) {
    return null;
  }
  return levels[currentIndex - 1] ?? null;
};

/**
 * Create drill-down breadcrumbs from hierarchy path
 */
export const createBreadcrumbs = (
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): DrillDownBreadcrumb[] => {
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return [];
  }

  const breadcrumbs: DrillDownBreadcrumb[] = [];

  for (const ancestorId of node.hierarchyPath) {
    const ancestorNode = hierarchyMap.get(ancestorId);
    if (ancestorNode) {
      const level = inferDrillDownLevel(ancestorNode.item.type);
      breadcrumbs.push({
        icon: LEVEL_ICONS[level],
        itemId: ancestorId,
        itemTitle: ancestorNode.item.title,
        level,
      });
    }
  }

  return breadcrumbs;
};

/**
 * Get children grouped by drill-down level
 */
export const getChildrenByDrillDownLevel = (
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
  items: Item[],
): Map<DrillDownLevel, Item[]> => {
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return new Map();
  }

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
};

export interface CreateDrillDownContextOptions {
  itemId: string;
  items: Item[];
  hierarchyMap: Map<string, HierarchyNode>;
  expandedGroups?: Set<string> | undefined;
}

/**
 * Create drill-down context for current navigation state
 */
export const createDrillDownContext = (opts: CreateDrillDownContextOptions): DrillDownContext => {
  const { itemId, items, hierarchyMap } = opts;
  const node = hierarchyMap.get(itemId);
  const item = items.find((i) => i.id === itemId);

  if (!node || !item) {
    return {
      breadcrumbs: [],
      childrenAvailable: false,
      currentLevel: 'project',
      itemId,
      itemTitle: 'Unknown',
      visibleItems: [],
    };
  }

  const breadcrumbs = createBreadcrumbs(itemId, hierarchyMap);
  const childrenByLevel = getChildrenByDrillDownLevel(itemId, hierarchyMap, items);

  // Determine visible items based on expansions
  const visibleItems: string[] = [];
  for (const [, children] of childrenByLevel) {
    for (const child of children) {
      visibleItems.push(child.id);
    }
  }

  const parentNode = node.parentId ? hierarchyMap.get(node.parentId) : undefined;

  return {
    breadcrumbs,
    childrenAvailable: node.childrenIds.length > 0,
    currentLevel: inferDrillDownLevel(item.type),
    itemId,
    itemTitle: item.title,
    parentId: node.parentId,
    parentTitle: parentNode?.item.title,
    visibleItems,
  };
};

const DEFAULT_MAX_ITEMS_PER_GROUP = 20;

const buildLevelGroup = (opts: {
  itemId: string;
  level: DrillDownLevel;
  children: Item[];
  subGroupIndex: number;
  totalSubGroups: number;
  start: number;
  end: number;
  hierarchyMap: Map<string, HierarchyNode>;
}): DrillDownNodeGroup => {
  const {
    itemId,
    level,
    children,
    subGroupIndex: i,
    totalSubGroups: subGroups,
    start,
    end,
    hierarchyMap,
  } = opts;
  const groupChildren = children.slice(start, end);
  const label =
    subGroups > 1 ? `${level} (${start + 1}-${end})` : `${level} (${groupChildren.length})`;
  return {
    canExpand: groupChildren.some((c) => (hierarchyMap.get(c.id)?.childrenIds.length ?? 0) > 0),
    color: LEVEL_COLORS[level],
    groupId: `dd-${itemId}-${level}-${i}`,
    icon: LEVEL_ICONS[level],
    isExpanded: false,
    itemCount: groupChildren.length,
    itemIds: groupChildren.map((c) => c.id),
    label,
    level,
    metadata: {
      level,
      subGroupIndex: i,
      totalSubGroups: subGroups,
    },
    parentItemId: itemId,
  };
};

export interface CreateDrillDownNodeGroupsOptions {
  itemId: string;
  items: Item[];
  hierarchyMap: Map<string, HierarchyNode>;
  maxItemsPerGroup?: number | undefined;
}

/**
 * Create node groups for drill-down expansion
 */
export const createDrillDownNodeGroups = (
  opts: CreateDrillDownNodeGroupsOptions,
): DrillDownNodeGroup[] => {
  const { itemId, items, hierarchyMap, maxItemsPerGroup = DEFAULT_MAX_ITEMS_PER_GROUP } = opts;
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return [];
  }

  const childrenByLevel = getChildrenByDrillDownLevel(itemId, hierarchyMap, items);
  const groups: DrillDownNodeGroup[] = [];

  for (const [level, children] of childrenByLevel) {
    if (children.length === 0) {
      continue;
    }
    const subGroups = Math.ceil(children.length / maxItemsPerGroup);
    for (let i = 0; i < subGroups; i += 1) {
      const start = i * maxItemsPerGroup;
      const end = Math.min(start + maxItemsPerGroup, children.length);
      groups.push(
        buildLevelGroup({
          children,
          end,
          hierarchyMap,
          itemId,
          level,
          start,
          subGroupIndex: i,
          totalSubGroups: subGroups,
        }),
      );
    }
  }

  return groups;
};

/**
 * Expand a drill-down node group
 */
export const expandDrillDownGroup = (groupId: string, expandedGroups: Set<string>): Set<string> => {
  const newExpanded = new Set(expandedGroups);
  newExpanded.add(groupId);
  return newExpanded;
};

/**
 * Collapse a drill-down node group
 */
export const collapseDrillDownGroup = (
  groupId: string,
  expandedGroups: Set<string>,
): Set<string> => {
  const newExpanded = new Set(expandedGroups);
  newExpanded.delete(groupId);
  return newExpanded;
};

/**
 * Toggle drill-down node group expansion
 */
export const toggleDrillDownGroup = (groupId: string, expandedGroups: Set<string>): Set<string> => {
  const newExpanded = new Set(expandedGroups);

  if (newExpanded.has(groupId)) {
    newExpanded.delete(groupId);
  } else {
    newExpanded.add(groupId);
  }

  return newExpanded;
};

export interface GetVisibleDrillDownItemsOptions {
  itemId: string;
  items: Item[];
  hierarchyMap: Map<string, HierarchyNode>;
  expandedGroups: Set<string>;
}

/**
 * Get all visible items for drill-down navigation
 */
export const getVisibleDrillDownItems = (opts: GetVisibleDrillDownItemsOptions): Item[] => {
  const { itemId, items, hierarchyMap, expandedGroups } = opts;
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return [];
  }

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
      // 			Const _groupIdx = groupId.split("-").pop();
      const node = hierarchyMap.get(itemId);

      if (node) {
        // Would need group index to item mapping for full implementation
        // This is simplified version
      }
    }
  }

  return [...visibleIds]
    .map((id) => itemMap.get(id))
    .filter((item): item is Item => item !== undefined);
};

/**
 * Navigate to parent in drill-down
 */
export const navigateUp = (
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): string | null => {
  const node = hierarchyMap.get(itemId);
  const pid = node?.parentId;
  return pid ?? null;
};

/**
 * Navigate to specific child in drill-down
 */
export const navigateToChild = (
  itemId: string,
  childIndex: number,
  hierarchyMap: Map<string, HierarchyNode>,
): string | null => {
  const node = hierarchyMap.get(itemId);
  if (!node || childIndex < 0 || childIndex >= node.childrenIds.length) {
    return null;
  }

  const childId = node.childrenIds[childIndex];
  if (childId === undefined) {
    return null;
  }
  return childId;
};

/**
 * Get drill-down path for lazy loading
 * Returns the sequence of item IDs from root to target
 */
export const getDrillDownPath = (
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): string[] => {
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return [];
  }

  return node.hierarchyPath;
};

const processQueueNode = (
  itemId: string,
  currentDepth: number,
  itemsToLoad: Set<string>,
  hierarchyMap: Map<string, HierarchyNode>,
  queue: { itemId: string; currentDepth: number }[],
): void => {
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return;
  }
  for (const childId of node.childrenIds) {
    if (!itemsToLoad.has(childId)) {
      queue.push({
        currentDepth: currentDepth + 1,
        itemId: childId,
      });
    }
  }
};

/**
 * Calculate lazy loading requirements for drill-down
 * Returns items that need to be fetched for full drill-down experience
 */
export const calculateLazyLoadingRequirements = (
  rootItemId: string,
  maxDepth: number,
  hierarchyMap: Map<string, HierarchyNode>,
): {
  depth: number;
  estimatedSize: number;
  itemsToLoad: string[];
} => {
  const itemsToLoad = new Set<string>();
  const queue = [
    {
      currentDepth: 0,
      itemId: rootItemId,
    },
  ];

  let maxDepthReached = 0;

  while (queue.length > 0) {
    const entry = queue.shift()!;
    const { itemId, currentDepth } = entry;

    if (currentDepth > maxDepth) {
      continue;
    }

    itemsToLoad.add(itemId);
    maxDepthReached = Math.max(maxDepthReached, currentDepth);
    processQueueNode(itemId, currentDepth, itemsToLoad, hierarchyMap, queue);
  }

  return {
    depth: maxDepthReached,
    estimatedSize: itemsToLoad.size,
    itemsToLoad: [...itemsToLoad],
  };
};

/**
 * Get drill-down statistics
 */
export const getDrillDownStats = (
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): {
  childCount: number;
  depth: number;
  expandableCount: number;
  totalDescendants: number;
} => {
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return {
      childCount: 0,
      depth: 0,
      expandableCount: 0,
      totalDescendants: 0,
    };
  }

  const expandableCount = node.childrenIds.filter((childId) => {
    const childNode = hierarchyMap.get(childId);
    return (childNode?.childrenIds.length ?? 0) > 0;
  }).length;

  return {
    childCount: node.childrenIds.length,
    depth: node.depth,
    expandableCount,
    totalDescendants: node.descendants.length,
  };
};
