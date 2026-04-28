/**
 * Integration test for search flow
 */

import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import type { ItemStatus } from '../../api/types';

import { useSearch } from '../../hooks/useSearch';
import { createWrapper } from '../utils/test-utils';

describe('Search Flow Integration', () => {
  beforeEach(() => {
    // Don't use fake timers - causes issues with async hooks
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should search and display results', async () => {
    const { result } = renderHook(() => useSearch(), {
      wrapper: createWrapper(),
    });

    // Start with empty search
    expect(result.current.query.q).toBe('');

    // Enter search query
    act(() => {
      result.current.setSearchText('test');
    });

    // Verify search text was set
    expect(result.current.query.q).toBe('test');
  }, 10_000);

  it('should handle pagination', async () => {
    const { result } = renderHook(() => useSearch(), {
      wrapper: createWrapper(),
    });

    // Search first
    act(() => {
      result.current.setSearchText('test');
    });

    // Change page
    act(() => {
      result.current.setPage(2);
    });

    // Verify pagination state changed
    expect(result.current.query.page).toBe(2);
  }, 10_000);

  it('should handle search clear', async () => {
    const { result } = renderHook(() => useSearch(), {
      wrapper: createWrapper(),
    });

    // Search first
    act(() => {
      result.current.setSearchText('test');
      result.current.setPage(3);
    });

    // Clear
    act(() => {
      result.current.clearSearch();
    });

    expect(result.current.query).toEqual({
      page: 1,
      per_page: 20,
      q: '',
    });
  });

  it('should update filters', async () => {
    const { result } = renderHook(() => useSearch(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.updateQuery({
        statuses: ['in_progress' as ItemStatus],
        types: ['feature'],
      });
    });

    expect(result.current.query.types).toEqual(['feature']);
    expect(result.current.query.statuses).toEqual(['in_progress']);
  });
});
