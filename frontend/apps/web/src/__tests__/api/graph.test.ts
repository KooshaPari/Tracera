/**
 * Tests for Graph API
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { fetchDependencyAnalysis, fetchGraph, fetchImpactAnalysis } from '@/api/graph';

// Mock endpoints
vi.mock('@/api/endpoints', () => ({
  graphApi: {
    get: vi.fn(),
    getDependencyAnalysis: vi.fn(),
    getImpactAnalysis: vi.fn(),
  },
}));

import { graphApi } from '@/api/endpoints';

describe('Graph API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(fetchGraph, () => {
    it('should fetch graph data', async () => {
      const mockGraph = { edges: [], nodes: [] };
      vi.mocked(graphApi.get).mockResolvedValue(mockGraph);

      const result = await fetchGraph('proj-1');
      expect(result).toEqual(mockGraph);
      expect(graphApi.get).toHaveBeenCalledWith('proj-1');
    });

    it('should fetch graph without projectId', async () => {
      const mockGraph = { edges: [], nodes: [] };
      vi.mocked(graphApi.get).mockResolvedValue(mockGraph);

      const result = await fetchGraph();
      expect(result).toEqual(mockGraph);
      // Get can be called with no args (optional parameter)
      expect(graphApi.get).toHaveBeenCalled();
    });
  });

  describe(fetchImpactAnalysis, () => {
    it('should fetch impact analysis', async () => {
      const mockAnalysis = {
        affected_count: 0,
        affected_items: [],
        depth: 5,
        item_id: 'item-1',
      };
      vi.mocked(graphApi.getImpactAnalysis).mockResolvedValue(mockAnalysis);

      const result = await fetchImpactAnalysis('item-1', 5);
      expect(result).toEqual(mockAnalysis);
      expect(graphApi.getImpactAnalysis).toHaveBeenCalledWith('item-1', 5);
    });

    it('should fetch impact analysis without depth', async () => {
      const mockAnalysis = {
        affected_count: 0,
        affected_items: [],
        depth: undefined,
        item_id: 'item-1',
      };
      vi.mocked(graphApi.getImpactAnalysis).mockResolvedValue(mockAnalysis);

      const result = await fetchImpactAnalysis('item-1');
      expect(result).toEqual(mockAnalysis);
      // Depth is optional parameter
      expect(graphApi.getImpactAnalysis).toHaveBeenCalled();
    });
  });

  describe(fetchDependencyAnalysis, () => {
    it('should fetch dependency analysis', async () => {
      const mockAnalysis = {
        dependencies: [],
        dependency_count: 0,
        depth: 5,
        item_id: 'item-1',
      };
      vi.mocked(graphApi.getDependencyAnalysis).mockResolvedValue(mockAnalysis);

      const result = await fetchDependencyAnalysis('item-1', 5);
      expect(result).toEqual(mockAnalysis);
      expect(graphApi.getDependencyAnalysis).toHaveBeenCalledWith('item-1', 5);
    });
  });
});
