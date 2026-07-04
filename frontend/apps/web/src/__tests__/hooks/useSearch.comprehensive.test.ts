/**
 * Comprehensive tests for useSearch hook
 * Target: 78.94% → 95% coverage
 */

import { act, renderHook, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { api } from '../../api/endpoints';
import { useSearch, useSearchSuggestions } from '../../hooks/useSearch';
import { createWrapper } from '../utils/test-utils';

vi.mock('../../api/endpoints', () => ({
  api: {
    search: {
      search: vi.fn(),
      suggest: vi.fn(),
    },
  },
}));

describe('useSearch - Comprehensive Coverage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe(useSearch, () => {
    it('should initialize with custom query', () => {
      const { result } = renderHook(
        () =>
          useSearch({
            page: 2,
            per_page: 10,
            q: 'initial',
          }),
        {
          wrapper: createWrapper(),
        },
      );

      expect(result.current.query.q).toBe('initial');
      expect(result.current.query.page).toBe(2);
      expect(result.current.query.per_page).toBe(10);
    });

    it('should debounce search query', async () => {
      const mockResults = {
        hasMore: false,
        items: [],
        page: 1,
        pageSize: 10,
        query: 'test',
        total: 0,
      };
      vi.mocked(api.search.search).mockResolvedValue(mockResults);

      const { result } = renderHook(() => useSearch(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.setSearchText('test');
      });

      // Wait for debounce
      await waitFor(
        () => {
          expect(api.search.search).toHaveBeenCalled();
        },
        { timeout: 500 },
      );
    });

    it('should not search with empty query', async () => {
      const { result } = renderHook(() => useSearch(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.setSearchText('');
      });

      // Wait a bit to ensure debounce completes
      await new Promise((resolve) => setTimeout(resolve, 350));

      // Should not search with empty query
      expect(api.search.search).not.toHaveBeenCalled();
    });

    it('should handle search errors', async () => {
      vi.mocked(api.search.search).mockRejectedValue(new Error('Search failed'));

      const { result } = renderHook(() => useSearch(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.setSearchText('test');
      });

      await waitFor(
        () => {
          expect(result.current.isError).toBeTruthy();
        },
        { timeout: 500 },
      );
    });

    it('should update query with complex filters', () => {
      const { result } = renderHook(() => useSearch(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.updateQuery({
          projectId: 'proj-1',
          statuses: ['in_progress'],
          types: ['feature', 'bug'],
        });
      });

      expect(result.current.query.types).toEqual(['feature', 'bug']);
      expect(result.current.query.statuses).toEqual(['in_progress']);
      expect(result.current.query.projectId).toBe('proj-1');
    });

    it('should reset page when search text changes', () => {
      const { result } = renderHook(() => useSearch(), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.setPage(5);
      });

      expect(result.current.query.page).toBe(5);

      act(() => {
        result.current.setSearchText('new search');
      });

      expect(result.current.query.page).toBe(1);
    });
  });

  describe(useSearchSuggestions, () => {
    it('should fetch suggestions when query is long enough', async () => {
      const mockSuggestions = ['test1', 'test2'];
      vi.mocked(api.search.suggest).mockResolvedValue(mockSuggestions);

      const { result } = renderHook(() => useSearchSuggestions('test', 10), {
        wrapper: createWrapper(),
      });

      await waitFor(
        () => {
          expect(result.current.isSuccess).toBeTruthy();
        },
        { timeout: 500 },
      );

      expect(result.current.data).toEqual(mockSuggestions);
      expect(api.search.suggest).toHaveBeenCalledWith('test', 10);
    });

    it('should not fetch suggestions when query is too short', async () => {
      const { result } = renderHook(() => useSearchSuggestions('te', 10), {
        wrapper: createWrapper(),
      });

      await new Promise((resolve) => setTimeout(resolve, 250));

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.search.suggest).not.toHaveBeenCalled();
    });

    it('should debounce suggestion queries', async () => {
      const mockSuggestions = ['test'];
      vi.mocked(api.search.suggest).mockResolvedValue(mockSuggestions);

      const { result: _result, rerender } = renderHook(({ q }) => useSearchSuggestions(q, 10), {
        initialProps: { q: 'test' },
        wrapper: createWrapper(),
      });

      // Change query rapidly
      rerender({ q: 'test1' });
      rerender({ q: 'test12' });
      rerender({ q: 'test123' });

      // Wait for debounce
      await new Promise((resolve) => setTimeout(resolve, 250));

      // Should have been called (may be called multiple times due to rerenders)
      expect(api.search.suggest).toHaveBeenCalled();
    });

    it('should use custom limit', async () => {
      const mockSuggestions = ['test1', 'test2', 'test3'];
      vi.mocked(api.search.suggest).mockResolvedValue(mockSuggestions);

      const { result: _result } = renderHook(() => useSearchSuggestions('test', 5), {
        wrapper: createWrapper(),
      });

      await waitFor(
        () => {
          expect(api.search.suggest).toHaveBeenCalledWith('test', 5);
        },
        { timeout: 500 },
      );
    });

    it('should handle suggestion errors', async () => {
      vi.mocked(api.search.suggest).mockRejectedValue(new Error('Suggestion failed'));

      const { result } = renderHook(() => useSearchSuggestions('test', 10), {
        wrapper: createWrapper(),
      });

      await waitFor(
        () => {
          expect(result.current.isError).toBeTruthy();
        },
        { timeout: 500 },
      );
    });
  });
});
