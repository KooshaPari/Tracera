import type { GraphCacheTypes } from './graph-cache-types';

import { graphCacheConstants } from './graph-cache-constants';

type CacheStatistics = GraphCacheTypes['CacheStatistics'];
type GroupingData = GraphCacheTypes['GroupingData'];
type LayoutData = GraphCacheTypes['LayoutData'];
type SearchResult = GraphCacheTypes['SearchResult'];

interface GraphCacheStatsState {
  cacheStats: CacheStatistics;
  groupings: Map<string, GroupingData>;
  invalidationPatterns: GraphCacheTypes['InvalidationPattern'][];
  layouts: Map<string, LayoutData>;
  searchResults: Map<string, SearchResult[]>;
}

type StoreGetter = () => GraphCacheStatsState;
type StoreSetter = (fn: (state: GraphCacheStatsState) => void) => void;

interface StatsActions {
  getStats: () => CacheStatistics;
  recordInvalidation: (pattern: string, description: string) => void;
  resetStats: () => void;
}

const createInitialCacheStats = (): CacheStatistics => ({
  groupings: {
    avgAge: graphCacheConstants.emptyCount,
    count: graphCacheConstants.emptyCount,
    hitRate: graphCacheConstants.emptyCount,
  },
  lastInvalidationTime: undefined,
  layouts: {
    avgAge: graphCacheConstants.emptyCount,
    count: graphCacheConstants.emptyCount,
    hitRate: graphCacheConstants.emptyCount,
  },
  searches: {
    avgAge: graphCacheConstants.emptyCount,
    count: graphCacheConstants.emptyCount,
    hitRate: graphCacheConstants.emptyCount,
  },
  totalInvalidations: graphCacheConstants.emptyCount,
});

const calculateAverageAge = (totalAge: number, totalCount: number): number => {
  let averageAge = graphCacheConstants.emptyCount;

  if (totalCount > graphCacheConstants.emptyCount) {
    averageAge = totalAge / totalCount;
  }

  return averageAge;
};

const createStatsBlock = (
  averageAgeMs: number,
  totalCount: number,
): { avgAge: number; count: number; hitRate: number } => ({
  avgAge: averageAgeMs / graphCacheConstants.avgAgeDenominatorMs,
  count: totalCount,
  hitRate: graphCacheConstants.defaultHitRate,
});

const calculateLayoutStats = (
  now: number,
  state: GraphCacheStatsState,
): { avgAge: number; count: number; hitRate: number } => {
  let totalLayoutAge = graphCacheConstants.emptyCount;

  for (const layout of state.layouts.values()) {
    totalLayoutAge += now - layout.timestamp;
  }

  const avgLayoutAge = calculateAverageAge(totalLayoutAge, state.layouts.size);
  return createStatsBlock(avgLayoutAge, state.layouts.size);
};

const calculateGroupingStats = (
  now: number,
  state: GraphCacheStatsState,
): { avgAge: number; count: number; hitRate: number } => {
  let totalGroupingAge = graphCacheConstants.emptyCount;

  for (const grouping of state.groupings.values()) {
    totalGroupingAge += now - grouping.timestamp;
  }

  const avgGroupingAge = calculateAverageAge(totalGroupingAge, state.groupings.size);
  return createStatsBlock(avgGroupingAge, state.groupings.size);
};

const createStatsActions = (set: StoreSetter, get: StoreGetter): StatsActions => ({
  getStats: (): CacheStatistics => {
    const state = get();
    const now = Date.now();
    const groupings = calculateGroupingStats(now, state);
    const layouts = calculateLayoutStats(now, state);

    return {
      groupings,
      lastInvalidationTime: state.cacheStats.lastInvalidationTime,
      layouts,
      searches: {
        avgAge: graphCacheConstants.emptyCount,
        count: state.searchResults.size,
        hitRate: graphCacheConstants.defaultHitRate,
      },
      totalInvalidations: state.cacheStats.totalInvalidations,
    };
  },
  recordInvalidation: (pattern: string, description: string): void => {
    set((draft) => {
      draft.invalidationPatterns.push({
        description,
        pattern,
        priority: 'medium',
        timestamp: Date.now(),
      });

      if (draft.invalidationPatterns.length > graphCacheConstants.invalidationPatternLimit) {
        draft.invalidationPatterns = draft.invalidationPatterns.slice(
          graphCacheConstants.invalidationPatternTrimStart,
        );
      }
    });
  },
  resetStats: (): void => {
    set((draft) => {
      draft.cacheStats = createInitialCacheStats();
    });
  },
});

const graphCacheStats = {
  createInitialCacheStats,
  createStatsActions,
};

export { graphCacheStats };
