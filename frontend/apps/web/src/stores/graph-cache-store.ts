import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

import type { GraphCacheTypes } from './graph-cache-types';

import { createInvalidationActions } from './graph-cache-invalidation';
import { graphCacheStats } from './graph-cache-stats';

type CacheStatistics = GraphCacheTypes['CacheStatistics'];
type GroupingData = GraphCacheTypes['GroupingData'];
type InvalidationPattern = GraphCacheTypes['InvalidationPattern'];
type ItemDependencies = GraphCacheTypes['ItemDependencies'];
type LayoutData = GraphCacheTypes['LayoutData'];
type SearchResult = GraphCacheTypes['SearchResult'];

interface GraphCacheBaseState {
  cacheStats: CacheStatistics;
  groupings: Map<string, GroupingData>;
  invalidationPatterns: InvalidationPattern[];
  itemDependencies: Map<string, ItemDependencies>;
  layouts: Map<string, LayoutData>;
  searchResults: Map<string, SearchResult[]>;
}

interface GraphCacheStoreState extends GraphCacheBaseState {
  addInvalidationPattern: (
    pattern: string,
    description: string,
    priority?: 'low' | 'medium' | 'high',
  ) => void;
  clearAll: () => void;
  deleteGrouping: (key: string) => void;
  deleteLayout: (key: string) => void;
  deleteSearchResult: (key: string) => void;
  getGrouping: (key: string) => GroupingData | undefined;
  getInvalidationPatterns: () => InvalidationPattern[];
  getItemDependencies: (itemId: string) => ItemDependencies | undefined;
  getLayout: (key: string) => LayoutData | undefined;
  getSearchResult: (key: string) => SearchResult[] | undefined;
  getStats: () => CacheStatistics;
  invalidateByItem: (itemId: string, cascading?: boolean) => void;
  invalidateByPattern: (pattern: string) => number;
  invalidateByProject: (projectId: string) => void;
  invalidateGrouping: (graphId: string) => void;
  invalidateLayout: (graphId: string) => void;
  invalidateSearch: (graphId: string) => void;
  prewarmCache: (data: { groupings?: GroupingData[]; layouts?: LayoutData[] }) => void;
  recordInvalidation: (pattern: string, description: string) => void;
  resetStats: () => void;
  setGrouping: (key: string, data: GroupingData) => void;
  setItemDependencies: (itemId: string, deps: ItemDependencies) => void;
  setLayout: (key: string, data: LayoutData) => void;
  setSearchResult: (key: string, results: SearchResult[]) => void;
}

type StoreGetter = () => GraphCacheStoreState;
type StoreSetter = (fn: (state: GraphCacheStoreState) => void) => void;

interface LayoutActions {
  deleteLayout: (key: string) => void;
  getLayout: (key: string) => LayoutData | undefined;
  setLayout: (key: string, data: LayoutData) => void;
}

interface GroupingActions {
  deleteGrouping: (key: string) => void;
  getGrouping: (key: string) => GroupingData | undefined;
  setGrouping: (key: string, data: GroupingData) => void;
}

interface SearchActions {
  deleteSearchResult: (key: string) => void;
  getSearchResult: (key: string) => SearchResult[] | undefined;
  setSearchResult: (key: string, results: SearchResult[]) => void;
}

interface DependencyActions {
  getItemDependencies: (itemId: string) => ItemDependencies | undefined;
  setItemDependencies: (itemId: string, deps: ItemDependencies) => void;
}

interface BulkActions {
  clearAll: () => void;
  prewarmCache: (data: { groupings?: GroupingData[]; layouts?: LayoutData[] }) => void;
}

interface PatternActions {
  addInvalidationPattern: (
    pattern: string,
    description: string,
    priority?: 'low' | 'medium' | 'high',
  ) => void;
  getInvalidationPatterns: () => InvalidationPattern[];
}

const createBaseState = (): GraphCacheBaseState => ({
  cacheStats: graphCacheStats.createInitialCacheStats(),
  groupings: new Map(),
  invalidationPatterns: [],
  itemDependencies: new Map(),
  layouts: new Map(),
  searchResults: new Map(),
});

const createLayoutActions = (set: StoreSetter, get: StoreGetter): LayoutActions => ({
  deleteLayout: (key: string): void => {
    set((state) => {
      state.layouts.delete(key);
    });
  },
  getLayout: (key: string): LayoutData | undefined => get().layouts.get(key),
  setLayout: (key: string, data: LayoutData): void => {
    set((state) => {
      const updatedLayout = { ...data, timestamp: Date.now() };
      state.layouts.set(key, updatedLayout);
    });
  },
});

const createGroupingActions = (set: StoreSetter, get: StoreGetter): GroupingActions => ({
  deleteGrouping: (key: string): void => {
    set((state) => {
      state.groupings.delete(key);
    });
  },
  getGrouping: (key: string): GroupingData | undefined => get().groupings.get(key),
  setGrouping: (key: string, data: GroupingData): void => {
    set((state) => {
      const updatedGrouping = { ...data, timestamp: Date.now() };
      state.groupings.set(key, updatedGrouping);
    });
  },
});

const createSearchActions = (set: StoreSetter, get: StoreGetter): SearchActions => ({
  deleteSearchResult: (key: string): void => {
    set((state) => {
      state.searchResults.delete(key);
    });
  },
  getSearchResult: (key: string): SearchResult[] | undefined => get().searchResults.get(key),
  setSearchResult: (key: string, results: SearchResult[]): void => {
    set((state) => {
      state.searchResults.set(key, results);
    });
  },
});

const createDependencyActions = (set: StoreSetter, get: StoreGetter): DependencyActions => ({
  getItemDependencies: (itemId: string): ItemDependencies | undefined =>
    get().itemDependencies.get(itemId),
  setItemDependencies: (itemId: string, deps: ItemDependencies): void => {
    set((state) => {
      state.itemDependencies.set(itemId, deps);
    });
  },
});

const createBulkActions = (set: StoreSetter): BulkActions => ({
  clearAll: (): void => {
    set((draft) => {
      draft.groupings.clear();
      draft.layouts.clear();
      draft.searchResults.clear();
    });
  },
  prewarmCache: (data: { groupings?: GroupingData[]; layouts?: LayoutData[] }): void => {
    set((draft) => {
      if (data.layouts) {
        for (const layout of data.layouts) {
          const layoutKey = `layout:${layout.graphId}:${layout.algorithm}`;
          draft.layouts.set(layoutKey, layout);
        }
      }

      if (data.groupings) {
        for (const grouping of data.groupings) {
          const groupingKey = `grouping:${grouping.graphId}:${grouping.strategy}`;
          draft.groupings.set(groupingKey, grouping);
        }
      }
    });
  },
});

const createPatternActions = (set: StoreSetter, get: StoreGetter): PatternActions => ({
  addInvalidationPattern: (
    pattern: string,
    description: string,
    priority: 'low' | 'medium' | 'high' = 'medium',
  ): void => {
    set((draft) => {
      draft.invalidationPatterns.push({
        description,
        pattern,
        priority,
        timestamp: Date.now(),
      });
    });
  },
  getInvalidationPatterns: (): InvalidationPattern[] => get().invalidationPatterns,
});

const buildGraphCacheStore = (set: StoreSetter, get: StoreGetter): GraphCacheStoreState => {
  const baseState = createBaseState();
  const actions: Omit<GraphCacheStoreState, keyof GraphCacheBaseState> = {
    ...createLayoutActions(set, get),
    ...createGroupingActions(set, get),
    ...createSearchActions(set, get),
    ...createDependencyActions(set, get),
    ...createInvalidationActions(set, get),
    ...graphCacheStats.createStatsActions(set, get),
    ...createBulkActions(set),
    ...createPatternActions(set, get),
  };

  return { ...baseState, ...actions };
};

const useGraphCacheStore = create<GraphCacheStoreState>()(
  immer<GraphCacheStoreState>((set, get) => buildGraphCacheStore(set, get)),
);

export { useGraphCacheStore };
export type { GraphCacheStoreState };
