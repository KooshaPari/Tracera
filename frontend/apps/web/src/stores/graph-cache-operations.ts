import type { GraphCacheStoreState } from './graph-cache-store';
import type { GraphCacheTypes } from './graph-cache-types';

import { useGraphCacheStore } from './graph-cache-store';

type CacheStatistics = GraphCacheTypes['CacheStatistics'];
type GroupingData = GraphCacheTypes['GroupingData'];
type LayoutData = GraphCacheTypes['LayoutData'];
type SearchResult = GraphCacheTypes['SearchResult'];

interface CacheSize {
  groupings: number;
  layouts: number;
  searches: number;
}

interface GraphCacheOperations {
  cacheGrouping: (key: string, data: GroupingData) => void;
  cacheLayout: (key: string, data: LayoutData) => void;
  cacheSearchResults: (key: string, results: SearchResult[]) => void;
  getCacheSize: () => CacheSize;
  getGrouping: (key: string) => GroupingData | undefined;
  getLayout: (key: string) => LayoutData | undefined;
  getSearchResults: (key: string) => SearchResult[] | undefined;
  getStats: () => CacheStatistics;
  invalidateItem: (itemId: string) => void;
  invalidatePattern: (pattern: string) => number;
  invalidateProject: (projectId: string) => void;
}

const createCacheSize = (store: GraphCacheStoreState): CacheSize => ({
  groupings: store.groupings.size,
  layouts: store.layouts.size,
  searches: store.searchResults.size,
});

const useGraphCacheOperations = (): GraphCacheOperations => {
  const store = useGraphCacheStore();

  return {
    cacheGrouping: (key: string, data: GroupingData): void => {
      store.setGrouping(key, data);
    },
    cacheLayout: (key: string, data: LayoutData): void => {
      store.setLayout(key, data);
    },
    cacheSearchResults: (key: string, results: SearchResult[]): void => {
      store.setSearchResult(key, results);
    },
    getCacheSize: (): CacheSize => createCacheSize(store),
    getGrouping: (key: string): GroupingData | undefined => store.getGrouping(key),
    getLayout: (key: string): LayoutData | undefined => store.getLayout(key),
    getSearchResults: (key: string): SearchResult[] | undefined => store.getSearchResult(key),
    getStats: (): CacheStatistics => store.getStats(),
    invalidateItem: (itemId: string): void => {
      store.invalidateByItem(itemId);
    },
    invalidatePattern: (pattern: string): number => store.invalidateByPattern(pattern),
    invalidateProject: (projectId: string): void => {
      store.invalidateByProject(projectId);
    },
  };
};

export { useGraphCacheOperations };
