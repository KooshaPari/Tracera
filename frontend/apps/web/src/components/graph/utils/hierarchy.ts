// Hierarchy utilities for graph visualization
// Handles parent-child relationships, depth calculation, and breadcrumb paths

import type { Item, Link } from '@tracertm/types';

const NOT_FOUND_DEPTH = -1;

/**
 * Hierarchy node with computed properties
 */
export interface HierarchyNode {
  id: string;
  item: Item;
  parentId?: string | undefined;
  childrenIds: string[];
  depth: number;
  ancestors: string[];
  descendants: string[];
  hierarchyPath: string[]; // Full path from root to this node
  isRoot: boolean;
  isLeaf: boolean;
  isOrphan: boolean; // Not connected to any hierarchy
}

/**
 * Build hierarchy from parent_of links
 *
 * @param items All items
 * @param links Links including parent_of relationships
 * @returns Map of item ID to HierarchyNode
 */
export function buildHierarchy(items: Item[], links: Link[]): Map<string, HierarchyNode> {
  // Map items by ID for quick lookup (currently unused but kept for future use)
  // Const itemMap = new Map(items.map((i) => [i.id, i]));
  const childMap = new Map<string, Set<string>>();
  const parentMap = new Map<string, string>();

  // Find parent_of links to build parent-child relationships
  for (const link of links) {
    if (link.type === 'parent_of') {
      // Parent_of: source is parent, target is child
      if (!childMap.has(link.sourceId)) {
        childMap.set(link.sourceId, new Set());
      }
      childMap.get(link.sourceId)!.add(link.targetId);
      parentMap.set(link.targetId, link.sourceId);
    }
  }

  // Build hierarchy nodes
  const hierarchyMap = new Map<string, HierarchyNode>();

  for (const item of items) {
    const parentId = parentMap.get(item.id);
    const childrenIds = [...(childMap.get(item.id) ?? new Set())];

    const hierarchyNode: HierarchyNode = {
      ancestors: [],
      childrenIds,
      depth: 0,
      descendants: [],
      hierarchyPath: [],
      id: item.id,
      isLeaf: childrenIds.length === 0,
      isOrphan: false,
      isRoot: !parentId,
      item,
      parentId,
    };

    hierarchyMap.set(item.id, hierarchyNode);
  }

  // Calculate depths via BFS from roots
  const visited = new Set<string>();
  const queue = [...hierarchyMap.values()]
    .filter((n) => n.isRoot)
    .map((n) => ({ depth: 0, nodeId: n.id }));

  while (queue.length > 0) {
    const { nodeId, depth } = queue.shift()!;
    if (visited.has(nodeId)) {
      continue;
    }

    visited.add(nodeId);
    const node = hierarchyMap.get(nodeId)!;
    node.depth = depth;

    // Process children
    for (const childId of node.childrenIds) {
      if (!visited.has(childId)) {
        queue.push({ depth: depth + 1, nodeId: childId });
      }
    }
  }

  // Mark orphans and calculate ancestors/descendants
  for (const node of hierarchyMap.values()) {
    // Check if orphan (not reachable from root)
    let current: HierarchyNode | undefined = node;
    let isOrphan = true;

    // Trace up to find root
    const visited = new Set<string>();
    while (current) {
      if (visited.has(current.id)) {
        break;
      } // Cycle detection
      visited.add(current.id);

      if (current.isRoot) {
        isOrphan = false;
        break;
      }

      const parentId: string | undefined = current.parentId;
      current = parentId ? hierarchyMap.get(parentId) : undefined;
    }

    node.isOrphan = isOrphan;

    // Calculate ancestors
    node.ancestors = getAncestors(node.id, hierarchyMap);

    // Calculate descendants
    node.descendants = getDescendants(node.id, hierarchyMap);

    // Build hierarchy path
    node.hierarchyPath = buildPath(node.id, hierarchyMap);
  }

  return hierarchyMap;
}

/**
 * Get all ancestors of a node
 */
function getAncestors(nodeId: string, hierarchyMap: Map<string, HierarchyNode>): string[] {
  const ancestors: string[] = [];
  let current = hierarchyMap.get(nodeId);
  const visited = new Set<string>();

  while (current?.parentId) {
    if (visited.has(current.id)) {
      break;
    } // Cycle detection
    visited.add(current.id);

    ancestors.unshift(current.parentId);
    current = hierarchyMap.get(current.parentId);
  }

  return ancestors;
}

/**
 * Get all descendants of a node
 */
function getDescendants(nodeId: string, hierarchyMap: Map<string, HierarchyNode>): string[] {
  const descendants: string[] = [];
  const queue = [nodeId];
  const visited = new Set<string>();

  while (queue.length > 0) {
    const currentId = queue.shift()!;
    if (visited.has(currentId)) {
      continue;
    }

    visited.add(currentId);
    const node = hierarchyMap.get(currentId);
    if (!node) {
      continue;
    }

    for (const childId of node.childrenIds) {
      descendants.push(childId);
      queue.push(childId);
    }
  }

  return descendants;
}

/**
 * Build full hierarchy path from root to node
 */
function buildPath(nodeId: string, hierarchyMap: Map<string, HierarchyNode>): string[] {
  const path: string[] = [];
  let current = hierarchyMap.get(nodeId);
  const visited = new Set<string>();

  // Collect path from node up to root
  while (current) {
    if (visited.has(current.id)) {
      break;
    } // Cycle detection
    visited.add(current.id);
    path.unshift(current.id);

    const { parentId } = current;
    current = parentId ? hierarchyMap.get(parentId) : undefined;
  }

  return path;
}

/**
 * Calculate depth level for an item
 * Depth is the distance from root in the hierarchy
 *
 * @param itemId Item ID
 * @param hierarchyMap Hierarchy map
 * @returns Depth level (0 for root, increases downward)
 */
export function getDepth(itemId: string, hierarchyMap: Map<string, HierarchyNode>): number {
  return hierarchyMap.get(itemId)?.depth ?? NOT_FOUND_DEPTH;
}

/**
 * Get parent item for a given item
 */
export function getParent(
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): HierarchyNode | undefined {
  const node = hierarchyMap.get(itemId);
  if (!node?.parentId) {
    return undefined;
  }
  return hierarchyMap.get(node.parentId);
}

/**
 * Get children items for a given item
 */
export function getChildren(
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): HierarchyNode[] {
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return [];
  }

  return node.childrenIds
    .map((id) => hierarchyMap.get(id))
    .filter((n): n is HierarchyNode => n !== undefined);
}

/**
 * Get all ancestors in order from immediate parent to root
 */
export function getAncestorChain(
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): HierarchyNode[] {
  const chain: HierarchyNode[] = [];
  let current = getParent(itemId, hierarchyMap);

  while (current) {
    chain.push(current);
    current = getParent(current.id, hierarchyMap);
  }

  return chain;
}

/**
 * Get all descendants recursively
 */
export function getDescendantNodes(
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): HierarchyNode[] {
  const descendants: HierarchyNode[] = [];
  const queue = [itemId];
  const visited = new Set<string>();

  while (queue.length > 0) {
    const currentId = queue.shift()!;
    if (visited.has(currentId)) {
      continue;
    }

    visited.add(currentId);
    const node = hierarchyMap.get(currentId);
    if (!node) {
      continue;
    }

    for (const childId of node.childrenIds) {
      const childNode = hierarchyMap.get(childId);
      if (childNode) {
        descendants.push(childNode);
        queue.push(childId);
      }
    }
  }

  return descendants;
}

/**
 * Generate breadcrumb path for an item
 * Returns human-readable path from root to item
 *
 * @param itemId Item ID
 * @param hierarchyMap Hierarchy map
 * @returns Array of {id, title} for breadcrumb display
 */
export function getBreadcrumbPath(
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): { id: string; title: string }[] {
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return [];
  }

  return node.hierarchyPath.map((id) => {
    const n = hierarchyMap.get(id);
    return {
      id,
      title: n?.item.title ?? 'Unknown',
    };
  });
}

/**
 * Find common ancestor of two items
 * Returns the closest (most immediate) common ancestor
 */
export function findCommonAncestor(
  itemId1: string,
  itemId2: string,
  hierarchyMap: Map<string, HierarchyNode>,
): string | undefined {
  const node1 = hierarchyMap.get(itemId1);
  const node2 = hierarchyMap.get(itemId2);

  if (!node1 || !node2) {
    return undefined;
  }

  // Build reversed ancestor arrays (from leaf to root for easier finding)
  const ancestors1 = [...node1.ancestors].toReversed();
  const ancestors2 = new Set([...node2.ancestors].toReversed());

  // Find first match going from immediate parent upward (closest common ancestor)
  for (const ancestorId of ancestors1) {
    if (ancestors2.has(ancestorId)) {
      return ancestorId;
    }
  }

  return undefined;
}

/**
 * Get siblings (items with same parent)
 */
export function getSiblings(
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): HierarchyNode[] {
  const node = hierarchyMap.get(itemId);
  if (!node?.parentId) {
    return [];
  }

  const parent = hierarchyMap.get(node.parentId);
  if (!parent) {
    return [];
  }

  return parent.childrenIds
    .filter((id) => id !== itemId)
    .map((id) => hierarchyMap.get(id))
    .filter((n): n is HierarchyNode => n !== undefined);
}

/**
 * Check if one item is ancestor of another
 */
export function isAncestor(
  potentialAncestorId: string,
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): boolean {
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return false;
  }

  return node.ancestors.includes(potentialAncestorId);
}

/**
 * Check if one item is descendant of another
 */
export function isDescendant(
  potentialDescendantId: string,
  itemId: string,
  hierarchyMap: Map<string, HierarchyNode>,
): boolean {
  const node = hierarchyMap.get(itemId);
  if (!node) {
    return false;
  }

  return node.descendants.includes(potentialDescendantId);
}

/**
 * Get all items at a specific depth level
 */
export function getItemsAtDepth(
  depth: number,
  hierarchyMap: Map<string, HierarchyNode>,
): HierarchyNode[] {
  return [...hierarchyMap.values()].filter((n) => n.depth === depth);
}

/**
 * Calculate statistics about hierarchy
 */
export function getHierarchyStats(hierarchyMap: Map<string, HierarchyNode>) {
  const nodes = [...hierarchyMap.values()];

  const depths = nodes.map((n) => n.depth);
  const maxDepth = Math.max(...depths, 0);
  const minDepth = Math.min(...depths, 0);

  const roots = nodes.filter((n) => n.isRoot);
  const leaves = nodes.filter((n) => n.isLeaf);
  const orphans = nodes.filter((n) => n.isOrphan);

  const depthDistribution = new Map<number, number>();
  for (const node of nodes) {
    depthDistribution.set(node.depth, (depthDistribution.get(node.depth) ?? 0) + 1);
  }

  return {
    averageDepth: depths.reduce((a, b) => a + b, 0) / Math.max(nodes.length, 1),
    depthDistribution: Object.fromEntries(depthDistribution),
    leafCount: leaves.length,
    maxDepth,
    minDepth,
    orphanCount: orphans.length,
    rootCount: roots.length,
    totalNodes: nodes.length,
  };
}

/**
 * Export hierarchy structure for visualization
 */
export function exportHierarchyStructure(hierarchyMap: Map<string, HierarchyNode>): {
  id: string;
  parentId?: string | undefined;
  depth: number;
  title: string;
  childCount: number;
}[] {
  return [...hierarchyMap.values()].map((node) => ({
    childCount: node.childrenIds.length,
    depth: node.depth,
    id: node.id,
    parentId: node.parentId,
    title: node.item.title,
  }));
}
