/**
 * Graph Cache Store
 *
 * Zustand store for managing cached graph state with intelligent,
 * hierarchical cache invalidation strategies.
 *
 * Features:
 * - Cached layout positions
 * - Cached grouping configurations
 * - Cached search results
 * - Hierarchical cache invalidation
 * - Cache statistics tracking
 */

import { create } from "zustand";
import { immer } from "zustand/middleware/immer";

/**
 * Layout position data
 */
export interface LayoutData {
	graphId: string;
	algorithm: string;
	positions: Record<string, { x: number; y: number }>;
	bounds: {
		minX: number;
		minY: number;
		maxX: number;
		maxY: number;
	};
	timestamp: number;
}

/**
 * Grouping data
 */
export interface GroupingData {
	graphId: string;
	strategy: string;
	groups: Array<{
		id: string;
		label: string;
		items: string[];
	}>;
	timestamp: number;
}

/**
 * Search result
 */
export interface SearchResult {
	id: string;
	title: string;
	description?: string;
	score: number;
	type: "item" | "link" | "group";
	graphId: string;
}

/**
 * Cache statistics
 */
export interface CacheStatistics {
	layouts: {
		count: number;
		hitRate: number;
		avgAge: number;
	};
	groupings: {
		count: number;
		hitRate: number;
		avgAge: number;
	};
	searches: {
		count: number;
		hitRate: number;
		avgAge: number;
	};
	totalInvalidations: number;
	lastInvalidationTime: number | null;
}

/**
 * Invalidation pattern for pattern-based cache clearing
 */
export interface InvalidationPattern {
	pattern: string;
	description: string;
	priority: "low" | "medium" | "high";
	timestamp: number;
}

/**
 * Item dependency for cascade invalidation
 */
interface ItemDependencies {
	ancestors: Set<string>;
	descendants: Set<string>;
	links: Set<string>;
	dependentLayouts: Set<string>;
	dependentGroupings: Set<string>;
}

/**
 * Store state
 */
interface GraphCacheStoreState {
	// Cached data
	layouts: Map<string, LayoutData>;
	groupings: Map<string, GroupingData>;
	searchResults: Map<string, SearchResult[]>;

	// Metadata
	itemDependencies: Map<string, ItemDependencies>;
	cacheStats: CacheStatistics;
	invalidationPatterns: InvalidationPattern[];

	// Methods - Layout management
	setLayout: (key: string, data: LayoutData) => void;
	getLayout: (key: string) => LayoutData | null;
	deleteLayout: (key: string) => void;

	// Methods - Grouping management
	setGrouping: (key: string, data: GroupingData) => void;
	getGrouping: (key: string) => GroupingData | null;
	deleteGrouping: (key: string) => void;

	// Methods - Search management
	setSearchResult: (key: string, results: SearchResult[]) => void;
	getSearchResult: (key: string) => SearchResult[] | null;
	deleteSearchResult: (key: string) => void;

	// Methods - Item dependencies
	setItemDependencies: (itemId: string, deps: ItemDependencies) => void;
	getItemDependencies: (itemId: string) => ItemDependencies | null;

	// Methods - Invalidation strategies
	invalidateByItem: (itemId: string, cascading?: boolean) => void;
	invalidateByProject: (projectId: string) => void;
	invalidateByPattern: (pattern: string) => number;
	invalidateLayout: (graphId: string) => void;
	invalidateGrouping: (graphId: string) => void;
	invalidateSearch: (graphId: string) => void;

	// Methods - Statistics and monitoring
	getStats: () => CacheStatistics;
	resetStats: () => void;
	recordInvalidation: (pattern: string, description: string) => void;

	// Methods - Bulk operations
	clearAll: () => void;
	prewarmCache: (data: {
		layouts?: LayoutData[];
		groupings?: GroupingData[];
	}) => void;

	// Methods - Invalidation patterns
	addInvalidationPattern: (
		pattern: string,
		description: string,
		priority?: "low" | "medium" | "high",
	) => void;
	getInvalidationPatterns: () => InvalidationPattern[];
}

/**
 * Create the graph cache store
 */
export const useGraphCacheStore = create<GraphCacheStoreState>()(
	immer((set, get) => ({
		layouts: new Map(),
		groupings: new Map(),
		searchResults: new Map(),
		itemDependencies: new Map(),
		cacheStats: {
			layouts: { count: 0, hitRate: 0, avgAge: 0 },
			groupings: { count: 0, hitRate: 0, avgAge: 0 },
			searches: { count: 0, hitRate: 0, avgAge: 0 },
			totalInvalidations: 0,
			lastInvalidationTime: null,
		},
		invalidationPatterns: [],

		// Layout management
		setLayout: (key: string, data: LayoutData) => {
			set((state) => {
				state.layouts.set(key, { ...data, timestamp: Date.now() });
			});
		},

		getLayout: (key: string): LayoutData | null => {
			return get().layouts.get(key) || null;
		},

		deleteLayout: (key: string) => {
			set((state) => {
				state.layouts.delete(key);
			});
		},

		// Grouping management
		setGrouping: (key: string, data: GroupingData) => {
			set((state) => {
				state.groupings.set(key, { ...data, timestamp: Date.now() });
			});
		},

		getGrouping: (key: string): GroupingData | null => {
			return get().groupings.get(key) || null;
		},

		deleteGrouping: (key: string) => {
			set((state) => {
				state.groupings.delete(key);
			});
		},

		// Search management
		setSearchResult: (key: string, results: SearchResult[]) => {
			set((state) => {
				state.searchResults.set(key, results);
			});
		},

		getSearchResult: (key: string): SearchResult[] | null => {
			return get().searchResults.get(key) || null;
		},

		deleteSearchResult: (key: string) => {
			set((state) => {
				state.searchResults.delete(key);
			});
		},

		// Item dependencies
		setItemDependencies: (itemId: string, deps: ItemDependencies) => {
			set((state) => {
				state.itemDependencies.set(itemId, deps);
			});
		},

		getItemDependencies: (itemId: string): ItemDependencies | null => {
			return get().itemDependencies.get(itemId) || null;
		},

		// Invalidation - Single item
		invalidateByItem: (itemId: string, cascading: boolean = true) => {
			const state = get();
			const deps = state.getItemDependencies(itemId);

			set((draft) => {
				// Invalidate direct caches
				draft.layouts.forEach((layout, key) => {
					if (layout.graphId.includes(itemId)) {
						draft.layouts.delete(key);
					}
				});

				draft.groupings.forEach((grouping, key) => {
					if (grouping.groups.some((g) => g.items.includes(itemId))) {
						draft.groupings.delete(key);
					}
				});

				draft.searchResults.clear(); // Search results become stale

				// Cascade invalidation if enabled
				if (cascading && deps) {
					const itemsToInvalidate = new Set<string>();
					itemsToInvalidate.add(itemId);

					// Add ancestors and descendants
					deps.ancestors.forEach((id) => itemsToInvalidate.add(id));
					deps.descendants.forEach((id) => itemsToInvalidate.add(id));

					// Recursively invalidate related items
					itemsToInvalidate.forEach((id) => {
						const itemDeps = state.getItemDependencies(id);
						if (itemDeps) {
							itemDeps.ancestors.forEach((aid) => itemsToInvalidate.add(aid));
							itemDeps.descendants.forEach((did) => itemsToInvalidate.add(did));
						}
					});

					// Clear caches for all affected items
					itemsToInvalidate.forEach((id) => {
						draft.layouts.forEach((layout, key) => {
							if (layout.graphId.includes(id)) {
								draft.layouts.delete(key);
							}
						});
					});
				}

				draft.cacheStats.totalInvalidations++;
				draft.cacheStats.lastInvalidationTime = Date.now();
			});
		},

		// Invalidation - Project level
		invalidateByProject: (projectId: string) => {
			set((draft) => {
				draft.layouts.forEach((_, key) => {
					if (key.includes(projectId)) {
						draft.layouts.delete(key);
					}
				});

				draft.groupings.forEach((_, key) => {
					if (key.includes(projectId)) {
						draft.groupings.delete(key);
					}
				});

				draft.searchResults.clear();
				draft.cacheStats.totalInvalidations++;
				draft.cacheStats.lastInvalidationTime = Date.now();
			});
		},

		// Invalidation - Pattern based
		invalidateByPattern: (pattern: string): number => {
			let count = 0;

			set((draft) => {
				const regex = new RegExp(
					`^${pattern.replace(/\*/g, ".*").replace(/\?/g, ".")}$`,
				);

				// Invalidate layouts
				draft.layouts.forEach((_, key) => {
					if (regex.test(key)) {
						draft.layouts.delete(key);
						count++;
					}
				});

				// Invalidate groupings
				draft.groupings.forEach((_, key) => {
					if (regex.test(key)) {
						draft.groupings.delete(key);
						count++;
					}
				});

				// Invalidate search results
				draft.searchResults.forEach((_, key) => {
					if (regex.test(key)) {
						draft.searchResults.delete(key);
						count++;
					}
				});

				draft.cacheStats.totalInvalidations++;
				draft.cacheStats.lastInvalidationTime = Date.now();
			});

			return count;
		},

		// Invalidation - Layout only
		invalidateLayout: (graphId: string) => {
			set((draft) => {
				draft.layouts.forEach((_, key) => {
					if (key.includes(graphId)) {
						draft.layouts.delete(key);
					}
				});
				draft.cacheStats.totalInvalidations++;
			});
		},

		// Invalidation - Grouping only
		invalidateGrouping: (graphId: string) => {
			set((draft) => {
				draft.groupings.forEach((_, key) => {
					if (key.includes(graphId)) {
						draft.groupings.delete(key);
					}
				});
				draft.cacheStats.totalInvalidations++;
			});
		},

		// Invalidation - Search only
		invalidateSearch: (graphId: string) => {
			set((draft) => {
				draft.searchResults.forEach((_, key) => {
					if (key.includes(graphId)) {
						draft.searchResults.delete(key);
					}
				});
				draft.cacheStats.totalInvalidations++;
			});
		},

		// Statistics
		getStats: (): CacheStatistics => {
			const state = get();
			const now = Date.now();

			// Calculate average ages
			let totalLayoutAge = 0;
			state.layouts.forEach((layout) => {
				totalLayoutAge += now - layout.timestamp;
			});
			const avgLayoutAge =
				state.layouts.size > 0 ? totalLayoutAge / state.layouts.size : 0;

			let totalGroupingAge = 0;
			state.groupings.forEach((grouping) => {
				totalGroupingAge += now - grouping.timestamp;
			});
			const avgGroupingAge =
				state.groupings.size > 0 ? totalGroupingAge / state.groupings.size : 0;

			return {
				layouts: {
					count: state.layouts.size,
					hitRate: 0.5, // Placeholder - should be tracked during gets
					avgAge: avgLayoutAge / 1000, // Convert to seconds
				},
				groupings: {
					count: state.groupings.size,
					hitRate: 0.5,
					avgAge: avgGroupingAge / 1000,
				},
				searches: {
					count: state.searchResults.size,
					hitRate: 0.5,
					avgAge: 0,
				},
				totalInvalidations: state.cacheStats.totalInvalidations,
				lastInvalidationTime: state.cacheStats.lastInvalidationTime,
			};
		},

		resetStats: () => {
			set((draft) => {
				draft.cacheStats = {
					layouts: { count: 0, hitRate: 0, avgAge: 0 },
					groupings: { count: 0, hitRate: 0, avgAge: 0 },
					searches: { count: 0, hitRate: 0, avgAge: 0 },
					totalInvalidations: 0,
					lastInvalidationTime: null,
				};
			});
		},

		recordInvalidation: (pattern: string, description: string) => {
			set((draft) => {
				draft.invalidationPatterns.push({
					pattern,
					description,
					priority: "medium",
					timestamp: Date.now(),
				});
				// Keep only last 100 patterns
				if (draft.invalidationPatterns.length > 100) {
					draft.invalidationPatterns = draft.invalidationPatterns.slice(-100);
				}
			});
		},

		// Bulk operations
		clearAll: () => {
			set((draft) => {
				draft.layouts.clear();
				draft.groupings.clear();
				draft.searchResults.clear();
			});
		},

		prewarmCache: (data) => {
			set((draft) => {
				if (data.layouts) {
					data.layouts.forEach((layout) => {
						const key = `layout:${layout.graphId}:${layout.algorithm}`;
						draft.layouts.set(key, layout);
					});
				}

				if (data.groupings) {
					data.groupings.forEach((grouping) => {
						const key = `grouping:${grouping.graphId}:${grouping.strategy}`;
						draft.groupings.set(key, grouping);
					});
				}
			});
		},

		// Invalidation patterns
		addInvalidationPattern: (
			pattern: string,
			description: string,
			priority: "low" | "medium" | "high" = "medium",
		) => {
			set((draft) => {
				draft.invalidationPatterns.push({
					pattern,
					description,
					priority,
					timestamp: Date.now(),
				});
			});
		},

		getInvalidationPatterns: (): InvalidationPattern[] => {
			return get().invalidationPatterns;
		},
	})),
);

/**
 * Hook for common cache operations
 */
export function useGraphCacheOperations() {
	const store = useGraphCacheStore();

	return {
		// Get cached items
		getLayout: (key: string) => store.getLayout(key),
		getGrouping: (key: string) => store.getGrouping(key),
		getSearchResults: (key: string) => store.getSearchResult(key),

		// Set cached items
		cacheLayout: (key: string, data: LayoutData) => store.setLayout(key, data),
		cacheGrouping: (key: string, data: GroupingData) =>
			store.setGrouping(key, data),
		cacheSearchResults: (key: string, results: SearchResult[]) =>
			store.setSearchResult(key, results),

		// Invalidation
		invalidateItem: (itemId: string) => store.invalidateByItem(itemId),
		invalidateProject: (projectId: string) =>
			store.invalidateByProject(projectId),
		invalidatePattern: (pattern: string) => store.invalidateByPattern(pattern),

		// Statistics
		getStats: () => store.getStats(),
		getCacheSize: () => ({
			layouts: store.layouts.size,
			groupings: store.groupings.size,
			searches: store.searchResults.size,
		}),
	};
}
