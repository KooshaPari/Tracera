/**
 * Tests for Impact API (re-exports from graph)
 */

import { beforeEach, describe, expect, it, vi } from 'vitest';

import impactApi from '../../api/impact';

// Mock endpoints
vi.mock('../../api/endpoints', () => ({
  graphApi: {
    getDependencyAnalysis: vi.fn(),
    getImpactAnalysis: vi.fn(),
  },
}));

import { graphApi } from '../../api/endpoints';

describe('Impact API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(impactApi, () => {
    it('should fetch impact analysis', async () => {
      const mockAnalysis = {
        affectedCount: 0,
        affectedItems: [],
        depth: 5,
        itemId: 'item-1',
      };
      vi.mocked(graphApi.getImpactAnalysis).mockResolvedValue(mockAnalysis);

      const result = await impactApi.fetchImpactAnalysis('item-1', 5);
      expect(result).toEqual(mockAnalysis);
      expect(graphApi.getImpactAnalysis).toHaveBeenCalledWith('item-1', 5);
    });
  });

  describe(impactApi, () => {
    it('should fetch dependency analysis', async () => {
      const mockAnalysis = {
        dependencies: [],
        dependencyCount: 0,
        depth: 5,
        itemId: 'item-1',
      };
      vi.mocked(graphApi.getDependencyAnalysis).mockResolvedValue(mockAnalysis);

      const result = await impactApi.fetchDependencyAnalysis('item-1', 5);
      expect(result).toEqual(mockAnalysis);
      expect(graphApi.getDependencyAnalysis).toHaveBeenCalledWith('item-1', 5);
    });
  });
});
