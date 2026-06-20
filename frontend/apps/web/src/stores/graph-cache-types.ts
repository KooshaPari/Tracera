export interface GraphCacheTypes {
  CacheStatistics: {
    groupings: {
      avgAge: number;
      count: number;
      hitRate: number;
    };
    lastInvalidationTime: number | undefined;
    layouts: {
      avgAge: number;
      count: number;
      hitRate: number;
    };
    searches: {
      avgAge: number;
      count: number;
      hitRate: number;
    };
    totalInvalidations: number;
  };
  GroupingData: {
    graphId: string;
    groups: {
      id: string;
      items: string[];
      label: string;
    }[];
    strategy: string;
    timestamp: number;
  };
  InvalidationPattern: {
    description: string;
    pattern: string;
    priority: 'low' | 'medium' | 'high';
    timestamp: number;
  };
  ItemDependencies: {
    ancestors: Set<string>;
    dependentGroupings: Set<string>;
    dependentLayouts: Set<string>;
    descendants: Set<string>;
    links: Set<string>;
  };
  LayoutData: {
    algorithm: string;
    bounds: {
      maxX: number;
      maxY: number;
      minX: number;
      minY: number;
    };
    graphId: string;
    positions: Record<string, { x: number; y: number }>;
    timestamp: number;
  };
  SearchResult: {
    description?: string | undefined;
    graphId: string;
    id: string;
    score: number;
    title: string;
    type: 'item' | 'link' | 'group';
  };
}
