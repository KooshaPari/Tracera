import { useCallback, useEffect, useRef, useState } from 'react';

import type { Item, Link, ItemDimensions } from '@tracertm/types';

/**
 * Cross-perspective search result with equivalence information
 */
export interface CrossPerspectiveSearchResult {
  item: Item;
  perspective: string;
  matchType: 'title' | 'description' | 'type' | 'dimension';
  score: number;
  matchedText?: string | undefined;
  equivalences: EquivalenceInfo[];
}

/**
 * Equivalence relationship information
 */
export interface EquivalenceInfo {
  equivalentItemId: string;
  equivalentPerspective: string;
  linkId?: string | undefined;
  confidence: number;
  linkType: 'same_as' | 'represents' | 'manifests_as';
}

/**
 * Grouped search results by perspective
 */
export interface GroupedSearchResults {
  perspective: string;
  results: CrossPerspectiveSearchResult[];
  count: number;
}

/**
 * Search filter options
 */
export interface SearchFilters {
  type?: string | undefined;
  status?: string | undefined;
  perspectives?: string[] | undefined;
  dimensionKey?: string | undefined;
  dimensionValue?: string | undefined;
}

/**
 * Search history entry
 */
interface SearchHistoryEntry {
  query: string;
  timestamp: number;
  filters?: SearchFilters | undefined;
}

/**
 * Saved search entry
 */
export interface SavedSearch {
  id: string;
  query: string;
  filters: SearchFilters;
  createdAt: number;
  results?: CrossPerspectiveSearchResult[] | undefined;
}

/**
 * Search cache entry with metadata
 */
interface SearchCacheEntry {
  results: CrossPerspectiveSearchResult[];
  timestamp: number;
  hitCount: number;
}

/**
 * Calculate search score based on relevance
 */
function calculateSearchScore(item: Item, query: string): number {
  const lowerQuery = query.toLowerCase();
  let score = 0;

  // Title match (highest priority)
  if (item.title) {
    const titleLower = item.title.toLowerCase();
    if (titleLower === lowerQuery) {
      score += 100; // Exact match
    } else if (titleLower.startsWith(lowerQuery)) {
      score += 75; // Prefix match
    } else if (titleLower.includes(lowerQuery)) {
      score += 50; // Substring match
    }
  }

  // Description match
  if (item.description) {
    const descLower = item.description.toLowerCase();
    if (descLower.includes(lowerQuery)) {
      score += 25;
    }
  }

  // Type match
  if (item.type) {
    const typeLower = item.type.toLowerCase();
    if (typeLower === lowerQuery) {
      score += 50;
    } else if (typeLower.includes(lowerQuery)) {
      score += 25;
    }
  }

  // Dimension value match
  if (item.dimensions) {
    for (const [_key, value] of Object.entries(item.dimensions)) {
      if (typeof value === 'string' && value.toLowerCase().includes(lowerQuery)) {
        score += 15;
      }
    }
  }

  return score;
}

/**
 * Get extracted matching text from item
 */
function getMatchedText(
  item: Item,
  query: string,
  matchType: 'title' | 'description' | 'type' | 'dimension',
): string | undefined {
  const lowerQuery = query.toLowerCase();

  switch (matchType) {
    case 'title': {
      return item.title;
    }
    case 'description': {
      return item.description;
    }
    case 'type': {
      return item.type;
    }
    case 'dimension': {
      if (item.dimensions) {
        for (const [_key, value] of Object.entries(item.dimensions)) {
          if (typeof value === 'string' && value.toLowerCase().includes(lowerQuery)) {
            return value;
          }
        }
      }
      return undefined;
    }
    default: {
      return undefined;
    }
  }
}

/**
 * Determine match type for a search query
 */
function determineMatchType(
  item: Item,
  query: string,
): 'title' | 'description' | 'type' | 'dimension' {
  const lowerQuery = query.toLowerCase();

  if (item.title?.toLowerCase().includes(lowerQuery)) {
    return 'title';
  }
  if (item.description?.toLowerCase().includes(lowerQuery)) {
    return 'description';
  }
  if (item.type?.toLowerCase().includes(lowerQuery)) {
    return 'type';
  }
  return 'dimension';
}

/**
 * Build equivalence info from links
 */
function getEquivalences(
  item: Item,
  allItems: Map<string, Item>,
  links: Link[],
  equivalentItemIds?: string[],
): EquivalenceInfo[] {
  const equivalences: EquivalenceInfo[] = [];

  // Check explicit equivalence item IDs
  if (equivalentItemIds) {
    for (const equivalentId of equivalentItemIds) {
      const equivalentItem = allItems.get(equivalentId);
      if (equivalentItem) {
        equivalences.push({
          confidence: 1,
          equivalentItemId: equivalentId,
          equivalentPerspective: equivalentItem.perspective ?? equivalentItem.view,
          linkType: 'same_as',
        });
      }
    }
  }

  // Check links for equivalence relationships
  for (const link of links) {
    if (
      (link.sourceId === item.id || link.targetId === item.id) &&
      (link.type === 'same_as' || link.type === 'represents' || link.type === 'manifests_as')
    ) {
      const equivalentId = link.sourceId === item.id ? link.targetId : link.sourceId;
      const equivalentItem = allItems.get(equivalentId);

      if (equivalentItem && !equivalences.some((e) => e.equivalentItemId === equivalentId)) {
        equivalences.push({
          confidence: link.confidence ?? 0.8,
          equivalentItemId: equivalentId,
          equivalentPerspective: equivalentItem.perspective ?? equivalentItem.view,
          linkId: link.id,
          linkType: link.type,
        });
      }
    }
  }

  // Deduplicate and sort by confidence
  const uniqueEquivalences = [
    ...new Map(equivalences.map((e) => [e.equivalentItemId, e])).values(),
  ];
  uniqueEquivalences.sort((a, b) => b.confidence - a.confidence);

  return uniqueEquivalences;
}

/**
 * Apply filters to search results
 */
function applyFilters(
  results: CrossPerspectiveSearchResult[],
  filters: SearchFilters,
): CrossPerspectiveSearchResult[] {
  return results.filter((result) => {
    // Type filter
    if (filters.type && result.item.type !== filters.type) {
      return false;
    }

    // Status filter
    if (filters.status && result.item.status !== filters.status) {
      return false;
    }

    // Perspective filter
    if (filters.perspectives && filters.perspectives.length > 0) {
      if (!filters.perspectives.includes(result.perspective)) {
        return false;
      }
    }

    // Dimension filter
    if (filters.dimensionKey && filters.dimensionValue) {
      const dimensionKey = filters.dimensionKey as keyof ItemDimensions;
      const dimensionValue = result.item.dimensions?.[dimensionKey];
      if (dimensionValue !== filters.dimensionValue) {
        return false;
      }
    }

    return true;
  });
}

/**
 * Pure function for cross-perspective search (exported for testing)
 */
export function performCrossPerspectiveSearch(
  items: Item[],
  links: Link[],
  query: string,
  filters?: SearchFilters,
): GroupedSearchResults[] {
  if (!query.trim()) {
    return [];
  }

  // Build item map for O(1) lookups
  const allItems = new Map(items.map((item) => [item.id, item]));

  // Perform search
  const searchResults: CrossPerspectiveSearchResult[] = [];

  for (const item of items) {
    const score = calculateSearchScore(item, query);

    if (score > 0) {
      const matchType = determineMatchType(item, query);
      const perspective = item.perspective ?? item.view;
      const equivalences = getEquivalences(item, allItems, links, item.equivalentItemIds);

      searchResults.push({
        item,
        perspective,
        matchType,
        score,
        ...(getMatchedText(item, query, matchType) && {
          matchedText: getMatchedText(item, query, matchType),
        }),
        equivalences,
      });
    }
  }

  // Apply filters
  let filtered = searchResults;
  if (filters) {
    filtered = applyFilters(searchResults, filters);
  }

  // Sort by score descending
  filtered.sort((a, b) => b.score - a.score);

  // Group by perspective
  const groupedByPerspective = new Map<string, CrossPerspectiveSearchResult[]>();

  for (const result of filtered) {
    const existing = groupedByPerspective.get(result.perspective) ?? [];
    existing.push(result);
    groupedByPerspective.set(result.perspective, existing);
  }

  // Convert to array and sort perspectives alphabetically
  const grouped: GroupedSearchResults[] = [...groupedByPerspective.entries()]
    .map(([perspective, results]) => ({
      count: results.length,
      perspective,
      results,
    }))
    .toSorted((a, b) => a.perspective.localeCompare(b.perspective));

  return grouped;
}

/**
 * Hook for cross-perspective search functionality with advanced features
 */
export function useCrossPerspectiveSearch() {
  const [searchHistory, setSearchHistory] = useState<SearchHistoryEntry[]>([]);
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const searchCacheRef = useRef<Map<string, SearchCacheEntry>>(new Map());
  const MAX_CACHE_ENTRIES = 50;
  const MAX_HISTORY_ENTRIES = 20;
  const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

  /**
   * Generate cache key from search parameters
   */
  const getCacheKey = useCallback((query: string, filters?: SearchFilters) => {
    const filterStr = filters ? JSON.stringify(filters) : '';
    return `${query}:${filterStr}`;
  }, []);

  /**
   * Clean expired cache entries
   */
  const cleanCache = useCallback(() => {
    const now = Date.now();
    const cache = searchCacheRef.current;

    for (const [key, entry] of cache.entries()) {
      if (now - entry.timestamp > CACHE_TTL_MS) {
        cache.delete(key);
      }
    }

    // Remove least used entries if cache is too large
    if (cache.size > MAX_CACHE_ENTRIES) {
      const entries = [...cache.entries()];
      entries.sort((a, b) => a[1].hitCount - b[1].hitCount);

      const toDelete = entries.slice(0, cache.size - MAX_CACHE_ENTRIES);
      for (const [key] of toDelete) {
        cache.delete(key);
      }
    }
  }, []);

  /**
   * Perform cross-perspective search across all items
   */
  const performSearch = useCallback(
    (
      items: Item[],
      links: Link[],
      query: string,
      filters?: SearchFilters,
    ): GroupedSearchResults[] => {
      const cacheKey = getCacheKey(query, filters);

      // Check cache
      const cached = searchCacheRef.current.get(cacheKey);
      if (cached) {
        cached.hitCount += 1;
        // Convert cached results back to grouped format
        const grouped = new Map<string, CrossPerspectiveSearchResult[]>();

        for (const result of cached.results) {
          const existing = grouped.get(result.perspective) ?? [];
          existing.push(result);
          grouped.set(result.perspective, existing);
        }

        return [...grouped.entries()]
          .map(([perspective, results]) => ({
            count: results.length,
            perspective,
            results,
          }))
          .toSorted((a, b) => a.perspective.localeCompare(b.perspective));
      }

      // Perform search
      const results = performCrossPerspectiveSearch(items, links, query, filters);

      // Flatten results for caching
      const flatResults = results.flatMap((group) => group.results);

      // Cache the results
      searchCacheRef.current.set(cacheKey, {
        hitCount: 0,
        results: flatResults,
        timestamp: Date.now(),
      });

      // Clean cache if needed
      cleanCache();

      return results;
    },
    [getCacheKey, cleanCache],
  );

  /**
   * Perform debounced search
   */
  const debouncedSearch = useCallback(
    (
      items: Item[],
      links: Link[],
      query: string,
      filters: SearchFilters | undefined,
      onResults: (results: GroupedSearchResults[]) => void,
      delay = 300,
    ) => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      debounceTimerRef.current = setTimeout(() => {
        const results = performSearch(items, links, query, filters);
        onResults(results);
      }, delay);
    },
    [performSearch],
  );

  /**
   * Add query to search history with filters
   */
  const addToHistory = useCallback((query: string, filters?: SearchFilters) => {
    setSearchHistory((prev) => {
      const filtered = prev.filter((entry) => entry.query !== query);
      return [{ filters, query, timestamp: Date.now() }, ...filtered].slice(0, MAX_HISTORY_ENTRIES);
    });
  }, []);

  /**
   * Get search history
   */
  const getHistory = useCallback(() => searchHistory.map((entry) => entry.query), [searchHistory]);

  /**
   * Get full history with filters
   */
  const getFullHistory = useCallback(() => searchHistory, [searchHistory]);

  /**
   * Clear search history
   */
  const clearHistory = useCallback(() => {
    setSearchHistory([]);
  }, []);

  /**
   * Save a search query for later reference
   */
  const saveSearch = useCallback(
    (query: string, filters: SearchFilters, results: CrossPerspectiveSearchResult[]) => {
      const id = `saved-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
      const newSearch: SavedSearch = {
        createdAt: Date.now(),
        filters,
        id,
        query,
        results,
      };

      setSavedSearches((prev) => [newSearch, ...prev].slice(0, 20)); // Keep last 20
      return id;
    },
    [],
  );

  /**
   * Delete a saved search
   */
  const deleteSavedSearch = useCallback((id: string) => {
    setSavedSearches((prev) => prev.filter((search) => search.id !== id));
  }, []);

  /**
   * Get all saved searches
   */
  const getSavedSearches = useCallback(() => savedSearches, [savedSearches]);

  /**
   * Load a saved search
   */
  const loadSavedSearch = useCallback(
    (id: string): SavedSearch | undefined => savedSearches.find((search) => search.id === id),
    [savedSearches],
  );

  /**
   * Get search suggestions based on query
   */
  const getSuggestions = useCallback(
    (items: Item[], query: string, limit = 10): string[] => {
      if (!query.trim()) {
        return [];
      }

      const lowerQuery = query.toLowerCase();
      const suggestions = new Set<string>();

      // Add matching item titles
      for (const item of items) {
        if (item.title?.toLowerCase().includes(lowerQuery) && suggestions.size < limit) {
          suggestions.add(item.title);
        }
      }

      // Add matching item types
      for (const item of items) {
        if (item.type?.toLowerCase().includes(lowerQuery) && suggestions.size < limit) {
          suggestions.add(item.type);
        }
      }

      // Add from history
      for (const entry of searchHistory) {
        if (entry.query.toLowerCase().includes(lowerQuery) && suggestions.size < limit) {
          suggestions.add(entry.query);
        }
      }

      return [...suggestions].slice(0, limit);
    },
    [searchHistory],
  );

  /**
   * Export search results as JSON
   */
  const exportResults = useCallback((results: GroupedSearchResults[], filename?: string) => {
    const data = JSON.stringify(results, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename ?? `search-results-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, []);

  /**
   * Export search results as CSV
   */
  const exportResultsCSV = useCallback((results: GroupedSearchResults[], filename?: string) => {
    const rows: string[] = ['ID,Title,Perspective,Type,Status,Match Type,Score'];

    for (const group of results) {
      for (const result of group.results) {
        const row = [
          result.item.id,
          `"${result.item.title.replaceAll('"', '""')}"`,
          result.perspective,
          result.item.type || '',
          result.item.status || '',
          result.matchType,
          result.score,
        ].join(',');
        rows.push(row);
      }
    }

    const csv = rows.join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename ?? `search-results-${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }, []);

  /**
   * Clear search cache
   */
  const clearCache = useCallback(() => {
    searchCacheRef.current.clear();
  }, []);

  /**
   * Get cache statistics
   */
  const getCacheStats = useCallback(() => {
    const cache = searchCacheRef.current;
    const entries: {
      key: string;
      hits: number;
      age: number;
    }[] = [];

    cache.forEach((entry, key) => {
      entries.push({
        age: Date.now() - entry.timestamp,
        hits: entry.hitCount,
        key,
      });
    });

    const stats = {
      entries,
      size: cache.size,
    };
    return stats;
  }, []);

  // Cleanup debounce timer on unmount
  useEffect(
    () => () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    },
    [],
  );

  return {
    addToHistory,
    clearCache,
    clearHistory,
    debouncedSearch,
    deleteSavedSearch,
    exportResults,
    exportResultsCSV,
    getCacheStats,
    getFullHistory,
    getHistory,
    getSavedSearches,
    getSuggestions,
    loadSavedSearch,
    performSearch,
    saveSearch,
  };
}
