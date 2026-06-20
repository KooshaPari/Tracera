import type { GraphCacheTypes } from './graph-cache-types';

import { graphCacheConstants } from './graph-cache-constants';

type CacheStatistics = GraphCacheTypes['CacheStatistics'];
type GroupingData = GraphCacheTypes['GroupingData'];
type ItemDependencies = GraphCacheTypes['ItemDependencies'];
type LayoutData = GraphCacheTypes['LayoutData'];
type SearchResult = GraphCacheTypes['SearchResult'];

interface GraphCacheInvalidationState {
  cacheStats: CacheStatistics;
  getItemDependencies: (itemId: string) => ItemDependencies | undefined;
  groupings: Map<string, GroupingData>;
  layouts: Map<string, LayoutData>;
  searchResults: Map<string, SearchResult[]>;
}

type StoreGetter = () => GraphCacheInvalidationState;
type StoreSetter = (fn: (state: GraphCacheInvalidationState) => void) => void;

interface InvalidationActions {
  invalidateByItem: (itemId: string, cascading?: boolean) => void;
  invalidateByPattern: (pattern: string) => number;
  invalidateByProject: (projectId: string) => void;
  invalidateGrouping: (graphId: string) => void;
  invalidateLayout: (graphId: string) => void;
  invalidateSearch: (graphId: string) => void;
}

const incrementInvalidations = (cacheStats: CacheStatistics): void => {
  cacheStats.lastInvalidationTime = Date.now();
  cacheStats.totalInvalidations += graphCacheConstants.incrementByOne;
};

const groupingContainsItem = (grouping: GroupingData, itemId: string): boolean => {
  for (const group of grouping.groups) {
    if (group.items.includes(itemId)) {
      return true;
    }
  }

  return false;
};

const removeLayoutsByGraphId = (layouts: Map<string, LayoutData>, graphId: string): void => {
  for (const [layoutKey, layout] of layouts) {
    if (layout.graphId.includes(graphId)) {
      layouts.delete(layoutKey);
    }
  }
};

const removeGroupingsByGraphId = (groupings: Map<string, GroupingData>, graphId: string): void => {
  for (const [groupingKey, grouping] of groupings) {
    if (grouping.graphId.includes(graphId)) {
      groupings.delete(groupingKey);
    }
  }
};

const removeSearchResultsByGraphId = (
  searchResults: Map<string, SearchResult[]>,
  graphId: string,
): void => {
  for (const [searchKey] of searchResults) {
    if (searchKey.includes(graphId)) {
      searchResults.delete(searchKey);
    }
  }
};

const removeLayoutsForItem = (layouts: Map<string, LayoutData>, itemId: string): void => {
  for (const [layoutKey, layout] of layouts) {
    if (layout.graphId.includes(itemId)) {
      layouts.delete(layoutKey);
    }
  }
};

const removeGroupingsForItem = (groupings: Map<string, GroupingData>, itemId: string): void => {
  for (const [groupingKey, grouping] of groupings) {
    if (groupingContainsItem(grouping, itemId)) {
      groupings.delete(groupingKey);
    }
  }
};

const collectRelatedItemIds = (
  itemId: string,
  deps: ItemDependencies,
  getItemDependencies: (targetId: string) => ItemDependencies | undefined,
): Set<string> => {
  const itemsToInvalidate = new Set<string>([itemId]);

  for (const ancestorId of deps.ancestors) {
    itemsToInvalidate.add(ancestorId);
  }

  for (const descendantId of deps.descendants) {
    itemsToInvalidate.add(descendantId);
  }

  for (const relatedItemId of itemsToInvalidate) {
    const relatedDeps = getItemDependencies(relatedItemId);
    if (!relatedDeps) {
      continue;
    }

    for (const ancestorId of relatedDeps.ancestors) {
      itemsToInvalidate.add(ancestorId);
    }

    for (const descendantId of relatedDeps.descendants) {
      itemsToInvalidate.add(descendantId);
    }
  }

  return itemsToInvalidate;
};

const removeLayoutsForItems = (layouts: Map<string, LayoutData>, itemIds: Set<string>): void => {
  for (const relatedItemId of itemIds) {
    removeLayoutsForItem(layouts, relatedItemId);
  }
};

interface CountTracker {
  value: number;
}

const removeMatchingKeys = <EntryValue>(
  entries: Map<string, EntryValue>,
  regex: RegExp,
  tracker: CountTracker,
): void => {
  for (const [entryKey] of entries) {
    if (regex.test(entryKey)) {
      entries.delete(entryKey);
      tracker.value += graphCacheConstants.incrementByOne;
    }
  }
};

interface InvalidateItemOptions {
  cascading: boolean;
  get: StoreGetter;
  itemId: string;
  set: StoreSetter;
}

const invalidateItem = (options: InvalidateItemOptions): void => {
  const { cascading, get, itemId, set } = options;
  const state = get();
  const deps = state.getItemDependencies(itemId);

  set((draft) => {
    removeLayoutsForItem(draft.layouts, itemId);
    removeGroupingsForItem(draft.groupings, itemId);
    draft.searchResults.clear();

    if (cascading && deps) {
      const relatedItemIds = collectRelatedItemIds(itemId, deps, state.getItemDependencies);
      removeLayoutsForItems(draft.layouts, relatedItemIds);
    }

    incrementInvalidations(draft.cacheStats);
  });
};

const invalidateProject = (set: StoreSetter, projectId: string): void => {
  set((draft) => {
    removeLayoutsByGraphId(draft.layouts, projectId);
    removeGroupingsByGraphId(draft.groupings, projectId);
    draft.searchResults.clear();
    incrementInvalidations(draft.cacheStats);
  });
};

const invalidatePattern = (set: StoreSetter, pattern: string): number => {
  const tracker: CountTracker = { value: graphCacheConstants.emptyCount };
  const regex = new RegExp(`^${pattern.replaceAll('*', '.*').replaceAll('?', '.')}$`);

  set((draft) => {
    removeMatchingKeys(draft.layouts, regex, tracker);
    removeMatchingKeys(draft.groupings, regex, tracker);
    removeMatchingKeys(draft.searchResults, regex, tracker);
    incrementInvalidations(draft.cacheStats);
  });

  return tracker.value;
};

const invalidateLayoutOnly = (set: StoreSetter, graphId: string): void => {
  set((draft) => {
    removeLayoutsByGraphId(draft.layouts, graphId);
    draft.cacheStats.totalInvalidations += graphCacheConstants.incrementByOne;
  });
};

const invalidateGroupingOnly = (set: StoreSetter, graphId: string): void => {
  set((draft) => {
    removeGroupingsByGraphId(draft.groupings, graphId);
    draft.cacheStats.totalInvalidations += graphCacheConstants.incrementByOne;
  });
};

const invalidateSearchOnly = (set: StoreSetter, graphId: string): void => {
  set((draft) => {
    removeSearchResultsByGraphId(draft.searchResults, graphId);
    draft.cacheStats.totalInvalidations += graphCacheConstants.incrementByOne;
  });
};

const createInvalidationActions = (set: StoreSetter, get: StoreGetter): InvalidationActions => ({
  invalidateByItem: (itemId: string, cascading = true): void => {
    invalidateItem({ cascading, get, itemId, set });
  },
  invalidateByPattern: (pattern: string): number => invalidatePattern(set, pattern),
  invalidateByProject: (projectId: string): void => {
    invalidateProject(set, projectId);
  },
  invalidateGrouping: (graphId: string): void => {
    invalidateGroupingOnly(set, graphId);
  },
  invalidateLayout: (graphId: string): void => {
    invalidateLayoutOnly(set, graphId);
  },
  invalidateSearch: (graphId: string): void => {
    invalidateSearchOnly(set, graphId);
  },
});

export { createInvalidationActions };
