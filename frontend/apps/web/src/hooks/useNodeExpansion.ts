// Hook for managing node expansion state and hierarchy navigation
// Tracks expansion state (collapsed/preview/panel), manages parent/children hierarchy
// Supports keyboard navigation and memoization for performance

import { useCallback, useMemo, useRef } from 'react';

export type NodeExpansionState = 'collapsed' | 'preview' | 'panel';

/**
 * Expansion state for a single node
 */
export interface NodeExpansionInfo {
  id: string;
  state: NodeExpansionState;
  parentId?: string;
  childIds: string[];
  depth: number;
}

/**
 * Navigation history for breadcrumb support
 */
export interface NavigationHistory {
  current: string | null;
  previous: string[];
  next: string[];
}

/**
 * Hook for managing node expansion state with hierarchy support
 */
export function useNodeExpansion(items: { id: string; parentId?: string }[]) {
  // Map items for quick lookup
  const itemMap = useMemo(() => new Map(items.map((item) => [item.id, item])), [items]);

  // Build hierarchy structure
  const hierarchy = useMemo(() => {
    const parentToChildren = new Map<string, string[]>();
    const depths = new Map<string, number>();

    // First pass: calculate depths
    for (const item of items) {
      let depth = 0;
      let currentId: string | undefined = item.parentId;
      while (currentId && depth < 100) {
        depth += 1;
        const parent = itemMap.get(currentId);
        currentId = parent?.parentId;
      }
      depths.set(item.id, depth);
    }

    // Second pass: build parent-to-children mapping
    for (const item of items) {
      if (item.parentId) {
        if (!parentToChildren.has(item.parentId)) {
          parentToChildren.set(item.parentId, []);
        }
        parentToChildren.get(item.parentId)!.push(item.id);
      }
    }

    return { depths, parentToChildren };
  }, [items, itemMap]);

  // State tracking
  const expansionStateRef = useRef<Map<string, NodeExpansionState>>(new Map());
  const navigationHistoryRef = useRef<NavigationHistory>({
    current: null,
    next: [],
    previous: [],
  });

  // Get expansion state for a node
  const getExpansionState = useCallback(
    (nodeId: string): NodeExpansionState => expansionStateRef.current.get(nodeId) ?? 'collapsed',
    [],
  );

  // Set expansion state
  const setExpansionState = useCallback((nodeId: string, state: NodeExpansionState) => {
    expansionStateRef.current.set(nodeId, state);
  }, []);

  // Get children of a node
  const getChildren = useCallback(
    (nodeId: string): string[] => hierarchy.parentToChildren.get(nodeId) ?? [],
    [hierarchy],
  );

  // Get parent of a node
  const getParent = useCallback(
    (nodeId: string): string | undefined => itemMap.get(nodeId)?.parentId,
    [itemMap],
  );

  // Get depth of a node
  const getDepth = useCallback(
    (nodeId: string): number => hierarchy.depths.get(nodeId) ?? 0,
    [hierarchy],
  );

  // Get full breadcrumb path for a node
  const getBreadcrumbPath = useCallback(
    (nodeId: string): string[] => {
      const path: string[] = [];
      let currentId: string | undefined = nodeId;

      while (currentId) {
        path.unshift(currentId);
        const parent = itemMap.get(currentId);
        currentId = parent?.parentId;
      }

      return path;
    },
    [itemMap],
  );

  // Navigate to parent
  const navigateToParent = useCallback(
    (nodeId: string): string | null => {
      const parent = getParent(nodeId);
      if (parent) {
        navigationHistoryRef.current.previous.push(navigationHistoryRef.current.current ?? nodeId);
        navigationHistoryRef.current.current = parent;
        navigationHistoryRef.current.next = [];
        return parent;
      }
      return null;
    },
    [getParent],
  );

  // Navigate to child
  const navigateToChild = useCallback(
    (nodeId: string, childIndex = 0): string | null => {
      const children = getChildren(nodeId);
      if (children[childIndex]) {
        navigationHistoryRef.current.previous.push(navigationHistoryRef.current.current ?? nodeId);
        navigationHistoryRef.current.current = children[childIndex];
        navigationHistoryRef.current.next = [];
        return children[childIndex];
      }
      return null;
    },
    [getChildren],
  );

  // Navigate back
  const navigateBack = useCallback((): string | null => {
    const previous = navigationHistoryRef.current.previous.pop();
    if (previous) {
      if (navigationHistoryRef.current.current) {
        navigationHistoryRef.current.next.unshift(navigationHistoryRef.current.current);
      }
      navigationHistoryRef.current.current = previous;
      return previous;
    }
    return null;
  }, []);

  // Navigate forward
  const navigateForward = useCallback((): string | null => {
    const next = navigationHistoryRef.current.next.shift();
    if (next) {
      if (navigationHistoryRef.current.current) {
        navigationHistoryRef.current.previous.push(navigationHistoryRef.current.current);
      }
      navigationHistoryRef.current.current = next;
      return next;
    }
    return null;
  }, []);

  // Get expansion info for a node
  const getNodeExpansionInfo = useCallback(
    (nodeId: string): NodeExpansionInfo => {
      const parentId = getParent(nodeId);
      return {
        id: nodeId,
        state: getExpansionState(nodeId),
        ...(parentId ? { parentId } : {}),
        childIds: getChildren(nodeId),
        depth: getDepth(nodeId),
      };
    },
    [getExpansionState, getParent, getChildren, getDepth],
  );

  // Get all expanded nodes (memoized for performance)
  const expandedNodes = useMemo(() => {
    const expanded: string[] = [];
    for (const [nodeId, state] of expansionStateRef.current) {
      if (state !== 'collapsed') {
        expanded.push(nodeId);
      }
    }
    return expanded;
  }, []);

  // Handle keyboard navigation
  const handleKeyboardNavigation = useCallback(
    (key: string, currentNodeId: string): string | null => {
      switch (key) {
        case 'ArrowUp': {
          // Navigate to parent
          return navigateToParent(currentNodeId);
        }
        case 'ArrowDown': {
          // Navigate to first child
          return navigateToChild(currentNodeId, 0);
        }
        case 'ArrowLeft': {
          // Collapse current node
          setExpansionState(currentNodeId, 'collapsed');
          return currentNodeId;
        }
        case 'ArrowRight': {
          // Expand current node
          const state = getExpansionState(currentNodeId);
          if (state === 'collapsed') {
            setExpansionState(currentNodeId, 'preview');
          } else if (state === 'preview') {
            setExpansionState(currentNodeId, 'panel');
          }
          return currentNodeId;
        }
        case 'Backspace': {
          // Go back in history
          return navigateBack();
        }
        case 'Enter': {
          // Toggle expansion state
          {
            const state = getExpansionState(currentNodeId);
            const nextState: NodeExpansionState =
              state === 'collapsed' ? 'preview' : state === 'preview' ? 'panel' : 'collapsed';
            setExpansionState(currentNodeId, nextState);
          }
          return currentNodeId;
        }
        default: {
          return null;
        }
      }
    },
    [navigateToParent, navigateToChild, navigateBack, setExpansionState, getExpansionState],
  );

  return {
    // State accessors
    getExpansionState,
    setExpansionState,
    getNodeExpansionInfo,
    expandedNodes,

    // Hierarchy accessors
    getChildren,
    getParent,
    getDepth,
    getBreadcrumbPath,

    // Navigation
    navigateToParent,
    navigateToChild,
    navigateBack,
    navigateForward,

    // Keyboard support
    handleKeyboardNavigation,

    // Internals for testing
    __expansionState: expansionStateRef.current,
    __navigationHistory: navigationHistoryRef.current,
  };
}

/**
 * Get the memoized expansion state (for use in components)
 */
export function useExpansionStateSelector(
  expansionState: Map<string, NodeExpansionState>,
  nodeId: string,
): NodeExpansionState {
  return useMemo(() => expansionState.get(nodeId) ?? 'collapsed', [expansionState, nodeId]);
}
