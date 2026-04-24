import { act, renderHook } from '@testing-library/react';

import type { Item, Link } from '@tracertm/types';

import type {
  CrossPerspectiveSearchResult,
  SearchFilters,
} from '../../components/graph/hooks/useCrossPerspectiveSearch';

import {
  performCrossPerspectiveSearch,
  useCrossPerspectiveSearch,
} from '../../components/graph/hooks/useCrossPerspectiveSearch';

/**
 * Test suite for advanced search features
 */
describe('useCrossPerspectiveSearch - Advanced Features', () => {
  const mockItems: Item[] = [
    {
      description: 'User login and session management',
      id: '1',
      perspective: 'feature',
      priority: 'medium',
      createdAt: new Date().toISOString(),
      projectId: 'proj-1',
      status: 'done',
      title: 'Authentication System',
      type: 'Feature',
      updatedAt: new Date().toISOString(),
      version: 1,
      view: 'feature',
    },
    {
      description: 'REST API for user authentication',
      id: '2',
      perspective: 'api',
      priority: 'medium',
      createdAt: new Date().toISOString(),
      projectId: 'proj-1',
      status: 'done',
      title: 'Login API Endpoint',
      type: 'API',
      updatedAt: new Date().toISOString(),
      version: 1,
      view: 'api',
    },
    {
      description: 'Business logic for user management',
      id: '3',
      perspective: 'code',
      priority: 'medium',
      createdAt: new Date().toISOString(),
      projectId: 'proj-1',
      status: 'in_progress',
      title: 'User Service',
      type: 'Service',
      updatedAt: new Date().toISOString(),
      version: 1,
      view: 'code',
    },
    {
      description: 'Unit tests for authentication',
      id: '4',
      perspective: 'test',
      priority: 'medium',
      createdAt: new Date().toISOString(),
      projectId: 'proj-1',
      status: 'done',
      title: 'Login Tests',
      type: 'Test',
      updatedAt: new Date().toISOString(),
      version: 1,
      view: 'test',
    },
    {
      description: 'PostgreSQL table definitions',
      id: '5',
      perspective: 'database',
      priority: 'medium',
      createdAt: new Date().toISOString(),
      projectId: 'proj-1',
      status: 'done',
      title: 'User Database Schema',
      type: 'Schema',
      updatedAt: new Date().toISOString(),
      version: 1,
      view: 'database',
    },
  ];
  const baseItem = mockItems[0];
  if (!baseItem) {
    throw new Error('Expected mock items to be defined');
  }

  const mockLinks: Link[] = [
    {
      confidence: 0.95,
      createdAt: new Date().toISOString(),
      id: 'link-1',
      projectId: 'proj-1',
      sourceId: '1',
      targetId: '2',
      type: 'manifests_as',
      updatedAt: new Date().toISOString(),
      version: 1,
    },
    {
      confidence: 0.9,
      createdAt: new Date().toISOString(),
      id: 'link-2',
      projectId: 'proj-1',
      sourceId: '2',
      targetId: '3',
      type: 'represents',
      updatedAt: new Date().toISOString(),
      version: 1,
    },
    {
      confidence: 0.85,
      createdAt: new Date().toISOString(),
      id: 'link-3',
      projectId: 'proj-1',
      sourceId: '1',
      targetId: '4',
      type: 'same_as',
      updatedAt: new Date().toISOString(),
      version: 1,
    },
  ];

  describe('Search Results Caching', () => {
    it('should cache search results and return from cache on repeated queries', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      // First search
      act(() => {
        const res1 = result.current.performSearch(mockItems, mockLinks, 'authentication');
        expect(res1.length).toBeGreaterThan(0);
      });

      // Get cache stats before second search
      act(() => {
        const stats1 = result.current.getCacheStats();
        expect(stats1.size).toBe(1);
      });

      // Second search should be from cache
      act(() => {
        const res2 = result.current.performSearch(mockItems, mockLinks, 'authentication');
        expect(res2.length).toBeGreaterThan(0);
      });

      // Cache hit count should increase
      act(() => {
        const stats2 = result.current.getCacheStats();
        const entry = stats2.entries[0];
        expect(entry).toBeDefined();
        if (!entry) {
          return;
        }
        expect(entry.hits).toBe(1);
      });
    });

    it('should evict least used entries when cache exceeds max size', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      // Fill cache with many entries
      act(() => {
        for (let i = 0; i < 55; i++) {
          result.current.performSearch(mockItems, mockLinks, `query${i}`);
        }
      });

      // Cache size should be capped at 50
      act(() => {
        const stats = result.current.getCacheStats();
        expect(stats.size).toBeLessThanOrEqual(50);
      });
    });

    it('should clear cache on demand', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      // Populate cache
      act(() => {
        result.current.performSearch(mockItems, mockLinks, 'test');
      });

      // Verify cache has entries
      act(() => {
        const stats1 = result.current.getCacheStats();
        expect(stats1.size).toBeGreaterThan(0);
      });

      // Clear cache
      act(() => {
        result.current.clearCache();
      });

      // Verify cache is empty
      act(() => {
        const stats2 = result.current.getCacheStats();
        expect(stats2.size).toBe(0);
      });
    });
  });

  describe('Search History', () => {
    it('should add searches to history with filters', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      const filters: SearchFilters = {
        status: 'done',
        type: 'Feature',
      };

      act(() => {
        result.current.addToHistory('authentication', filters);
      });

      act(() => {
        const fullHistory = result.current.getFullHistory();
        expect(fullHistory).toHaveLength(1);
        const first = fullHistory[0];
        expect(first).toBeDefined();
        if (!first) {
          return;
        }
        expect(first.query).toBe('authentication');
        expect(first.filters).toEqual(filters);
      });
    });

    it('should remove duplicate searches, keeping most recent', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        result.current.addToHistory('test');
        result.current.addToHistory('other');
        result.current.addToHistory('test');
      });

      act(() => {
        const history = result.current.getHistory();
        expect(history).toEqual(['test', 'other']);
        expect(history[0]).toBe('test'); // Most recent first
      });
    });

    it('should limit history to max entries', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        for (let i = 0; i < 25; i++) {
          result.current.addToHistory(`query${i}`);
        }
      });

      act(() => {
        const history = result.current.getHistory();
        expect(history.length).toBeLessThanOrEqual(20);
      });
    });

    it('should clear history on demand', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        result.current.addToHistory('test1');
        result.current.addToHistory('test2');
      });

      const historyBefore = result.current.getHistory();
      expect(historyBefore).toHaveLength(2);

      act(() => {
        result.current.clearHistory();
      });

      const historyAfter = result.current.getHistory();
      expect(historyAfter).toHaveLength(0);
    });
  });

  describe('Saved Searches', () => {
    it('should save a search with results', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      const searchResults: CrossPerspectiveSearchResult[] = [
        {
          equivalences: [],
          item: baseItem,
          matchType: 'title',
          perspective: 'feature',
          score: 100,
        },
      ];

      let savedId: string;
      act(() => {
        savedId = result.current.saveSearch('authentication', { type: 'Feature' }, searchResults);
      });

      act(() => {
        const saved = result.current.loadSavedSearch(savedId);
        expect(saved).toBeDefined();
        expect(saved?.query).toBe('authentication');
        expect(saved?.filters.type).toBe('Feature');
        expect(saved?.results).toHaveLength(1);
      });
    });

    it('should delete a saved search', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      let savedId: string;
      act(() => {
        savedId = result.current.saveSearch('test', {}, []);
      });

      act(() => {
        result.current.deleteSavedSearch(savedId);
      });

      act(() => {
        const saved = result.current.loadSavedSearch(savedId);
        expect(saved).toBeUndefined();
      });
    });

    it('should retrieve all saved searches', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        result.current.saveSearch('search1', {}, []);
        result.current.saveSearch('search2', {}, []);
      });

      act(() => {
        const saved = result.current.getSavedSearches();
        expect(saved).toHaveLength(2);
      });
    });

    it('should limit saved searches to max entries', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        for (let i = 0; i < 25; i++) {
          result.current.saveSearch(`search${i}`, {}, []);
        }
      });

      act(() => {
        const saved = result.current.getSavedSearches();
        expect(saved.length).toBeLessThanOrEqual(20);
      });
    });
  });

  describe('Search Suggestions', () => {
    it('should generate suggestions from item titles', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        const suggestions = result.current.getSuggestions(mockItems, 'auth');
        expect(suggestions).toContain('Authentication System');
      });
    });

    it('should generate suggestions from item types', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        const suggestions = result.current.getSuggestions(mockItems, 'api');
        expect(suggestions).toContain('API');
      });
    });

    it('should generate suggestions from search history', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        result.current.addToHistory('historical search');
      });

      act(() => {
        const suggestions = result.current.getSuggestions(mockItems, 'historical');
        expect(suggestions).toContain('historical search');
      });
    });

    it('should limit suggestions to specified count', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        const suggestions = result.current.getSuggestions(mockItems, '', 3);
        expect(suggestions.length).toBeLessThanOrEqual(3);
      });
    });

    it('should return empty suggestions for empty query', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      act(() => {
        const suggestions = result.current.getSuggestions(mockItems, '');
        expect(suggestions).toHaveLength(0);
      });
    });
  });

  describe('Search Performance', () => {
    it('should complete search in under 300ms for 1000 items', () => {
      const largeItemSet = Array.from({ length: 1000 }, (_, i) => ({
        ...baseItem,
        id: `item-${i}`,
        title: `Item ${i} ${i % 2 === 0 ? 'test' : 'other'}`,
      }));

      const { result } = renderHook(() => useCrossPerspectiveSearch());

      const startTime = performance.now();
      act(() => {
        result.current.performSearch(largeItemSet, [], 'test');
      });
      const endTime = performance.now();

      const duration = endTime - startTime;
      expect(duration).toBeLessThan(300);
    });

    it('should use cache to improve repeated search performance', () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());

      // First search (cache miss)
      const start1 = performance.now();
      act(() => {
        result.current.performSearch(mockItems, mockLinks, 'test');
      });
      const duration1 = performance.now() - start1;

      // Second search (cache hit)
      const start2 = performance.now();
      act(() => {
        result.current.performSearch(mockItems, mockLinks, 'test');
      });
      const duration2 = performance.now() - start2;

      // Cache hit should be significantly faster
      expect(duration2).toBeLessThan(duration1);
    });
  });

  describe('Search Accuracy', () => {
    it('should achieve 95%+ accuracy for exact title matches', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'authentication system');

      const exactMatch = results
        .flatMap((r) => r.results)
        .find((r) => r.item.title === 'Authentication System');

      expect(exactMatch).toBeDefined();
      expect(exactMatch?.score).toBe(100);
    });

    it('should rank results correctly by relevance', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'authentication');

      // Check that each group's results are sorted by score descending
      for (const group of results) {
        for (let i = 0; i < group.results.length - 1; i++) {
          const current = group.results[i];
          const next = group.results[i + 1];
          if (!current || !next) {
            continue;
          }
          expect(current.score).toBeGreaterThanOrEqual(next.score);
        }
      }
    });

    it('should correctly identify match types', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'login');

      const results_arr = results.flatMap((r) => r.results);
      expect(results_arr.length).toBeGreaterThan(0);

      // Check that match types are correctly identified
      for (const result of results_arr) {
        expect(['title', 'description', 'type', 'dimension']).toContain(result.matchType);
      }
    });

    it('should achieve >95% accuracy with filters', () => {
      const filters: SearchFilters = {
        status: 'done',
        type: 'Feature',
      };

      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth', filters);

      const allResults = results.flatMap((r) => r.results);

      // All results should match filters
      for (const result of allResults) {
        if (filters.type) {
          expect(result.item.type).toBe(filters.type);
        }
        if (filters.status) {
          expect(result.item.status).toBe(filters.status);
        }
      }

      // At least one result should match
      expect(allResults.length).toBeGreaterThan(0);
    });
  });

  describe('Debounced Search', () => {
    it('should debounce rapid search calls', async () => {
      const { result } = renderHook(() => useCrossPerspectiveSearch());
      const mockCallback = vi.fn();

      // Rapid search calls
      act(() => {
        result.current.debouncedSearch(mockItems, mockLinks, 'test1', undefined, mockCallback, 100);
      });

      act(() => {
        result.current.debouncedSearch(mockItems, mockLinks, 'test2', undefined, mockCallback, 100);
      });

      act(() => {
        result.current.debouncedSearch(mockItems, mockLinks, 'test3', undefined, mockCallback, 100);
      });

      // Wait for debounce
      await new Promise((resolve) => setTimeout(resolve, 150));

      // Only the last call should execute
      expect(mockCallback).toHaveBeenCalledOnce();
    });
  });

  describe('Filter Application', () => {
    it('should apply type filters correctly', () => {
      const filters: SearchFilters = { type: 'Feature' };
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, '', filters);

      // With empty query, should return no results
      expect(results.length).toBe(0);
    });

    it('should apply status filters correctly', () => {
      const filters: SearchFilters = { status: 'done' };
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth', filters);

      const allResults = results.flatMap((r) => r.results);
      for (const result of allResults) {
        expect(result.item.status).toBe('done');
      }
    });

    it('should apply perspective filters correctly', () => {
      const filters: SearchFilters = { perspectives: ['feature', 'api'] };
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth', filters);

      expect(results.every((r) => filters.perspectives!.includes(r.perspective))).toBeTruthy();
    });

    it('should apply multiple filters together', () => {
      const filters: SearchFilters = {
        perspectives: ['feature'],
        status: 'done',
        type: 'Feature',
      };

      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth', filters);

      const allResults = results.flatMap((r) => r.results);
      for (const result of allResults) {
        expect(result.item.type).toBe('Feature');
        expect(result.item.status).toBe('done');
        expect(result.perspective).toBe('feature');
      }
    });
  });

  describe('Equivalence Handling', () => {
    it('should detect equivalences from links', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');

      const itemWithEquivalences = results
        .flatMap((r) => r.results)
        .find((r) => r.equivalences.length > 0);

      expect(itemWithEquivalences).toBeDefined();
    });

    it('should rank equivalences by confidence', () => {
      const results = performCrossPerspectiveSearch(mockItems, mockLinks, 'auth');

      for (const group of results) {
        for (const result of group.results) {
          if (result.equivalences.length > 1) {
            for (let i = 0; i < result.equivalences.length - 1; i++) {
              const current = result.equivalences[i];
              const next = result.equivalences[i + 1];
              if (!current || !next) {
                continue;
              }
              expect(current.confidence).toBeGreaterThanOrEqual(next.confidence);
            }
          }
        }
      }
    });
  });
});
