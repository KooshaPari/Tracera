/**
 * Tests for Search API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { fetchSearchResults } from '@/api/search';

// Mock endpoints
vi.mock('@/api/endpoints', () => ({
  searchApi: {
    search: vi.fn(),
  },
}));

import { searchApi } from '@/api/endpoints';

describe('Search API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchSearchResults, () => {
    it('should fetch search results', async () => {
      const mockResult = {
        items: [],
        page: 1,
        per_page: 10,
        query: 'test',
        total: 0,
      };
      vi.mocked(searchApi.search).mockResolvedValue(mockResult);

      const result = await fetchSearchResults({ q: 'test' });
      expect(result).toEqual(mockResult);
      expect(searchApi.search).toHaveBeenCalledWith({ q: 'test' });
    });

    it('should handle complex search queries', async () => {
      const mockResult = {
        items: [],
        page: 1,
        per_page: 20,
        query: 'complex search',
        total: 0,
      };
      vi.mocked(searchApi.search).mockResolvedValue(mockResult);

      const query = {
        limit: 20,
        offset: 0,
        projectId: 'proj-1',
        q: 'complex search',
        type: 'item',
      };
      const result = await fetchSearchResults(query);
      expect(result).toEqual(mockResult);
      expect(searchApi.search).toHaveBeenCalledWith(query);
    });
  });
});
