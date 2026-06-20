/**
 * Comprehensive tests for useGraph hooks
 * Target: 40% → 95% coverage
 */

import { renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  useAncestors,
  useDependencyAnalysis,
  useDescendants,
  useDetectCycles,
  useFindPath,
  useFullGraph,
  useImpactAnalysis,
  useOrphanItems,
} from '../../hooks/useGraph';
import { createWrapper } from '../utils/test-utils';

// Mock the API
vi.mock('../../api/endpoints', () => ({
  api: {
    graph: {
      detectCycles: vi.fn(),
      findPath: vi.fn(),
      getAncestors: vi.fn(),
      getDependencyAnalysis: vi.fn(),
      getDescendants: vi.fn(),
      getFullGraph: vi.fn(),
      getImpactAnalysis: vi.fn(),
      getOrphanItems: vi.fn(),
    },
  },
}));

import type { DependencyAnalysis, GraphData, ImpactAnalysis, Item } from '../../api/types';

import { api } from '../../api/endpoints';

describe('useGraph - Comprehensive Coverage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(useFullGraph, () => {
    it('should fetch full graph data with projectId', async () => {
      const mockGraph = { edges: [], nodes: [] };
      vi.mocked(api.graph.getFullGraph).mockResolvedValue(mockGraph);

      const { result } = renderHook(() => useFullGraph('proj-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(mockGraph);
      expect(api.graph.getFullGraph).toHaveBeenCalledWith('proj-1');
    });

    it('should fetch full graph data without projectId', async () => {
      const mockGraph = { edges: [], nodes: [] };
      vi.mocked(api.graph.getFullGraph).mockResolvedValue(mockGraph);

      const { result } = renderHook(() => useFullGraph(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(mockGraph);
      expect(api.graph.getFullGraph).toHaveBeenCalledWith(undefined);
    });

    it('should handle errors', async () => {
      vi.mocked(api.graph.getFullGraph).mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useFullGraph('proj-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBeTruthy();
      });
      expect(result.current.error).toBeTruthy();
    });
  });

  describe(useAncestors, () => {
    it('should fetch ancestors with id and depth', async () => {
      const mockAncestors: GraphData = { edges: [], nodes: [] };
      vi.mocked(api.graph.getAncestors).mockResolvedValue(mockAncestors);

      const { result } = renderHook(() => useAncestors('item-1', 5), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(mockAncestors);
      expect(api.graph.getAncestors).toHaveBeenCalledWith('item-1', 5);
    });

    it('should fetch ancestors without depth', async () => {
      const mockAncestors: GraphData = { edges: [], nodes: [] };
      vi.mocked(api.graph.getAncestors).mockResolvedValue(mockAncestors);

      const { result } = renderHook(() => useAncestors('item-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(api.graph.getAncestors).toHaveBeenCalledWith('item-1', undefined);
    });

    it('should not fetch when id is empty', () => {
      const { result } = renderHook(() => useAncestors(''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.graph.getAncestors).not.toHaveBeenCalled();
    });

    it('should handle errors', async () => {
      vi.mocked(api.graph.getAncestors).mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useAncestors('item-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBeTruthy();
      });
    });
  });

  describe(useDescendants, () => {
    it('should fetch descendants with id and depth', async () => {
      const mockDescendants: GraphData = { edges: [], nodes: [] };
      vi.mocked(api.graph.getDescendants).mockResolvedValue(mockDescendants);

      const { result } = renderHook(() => useDescendants('item-1', 5), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(mockDescendants);
      expect(api.graph.getDescendants).toHaveBeenCalledWith('item-1', 5);
    });

    it('should not fetch when id is empty', () => {
      const { result } = renderHook(() => useDescendants(''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.graph.getDescendants).not.toHaveBeenCalled();
    });

    it('should handle errors', async () => {
      vi.mocked(api.graph.getDescendants).mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useDescendants('item-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBeTruthy();
      });
    });
  });

  describe(useImpactAnalysis, () => {
    it('should fetch impact analysis with depth', async () => {
      const mockAnalysis: ImpactAnalysis = {
        affectedCount: 0,
        affectedItems: [],
        depth: 5,
        itemId: 'item-1',
      };
      vi.mocked(api.graph.getImpactAnalysis).mockResolvedValue(mockAnalysis);

      const { result } = renderHook(() => useImpactAnalysis('item-1', 5), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(mockAnalysis);
      expect(api.graph.getImpactAnalysis).toHaveBeenCalledWith('item-1', 5);
    });

    it('should not fetch when id is empty', () => {
      const { result } = renderHook(() => useImpactAnalysis(''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.graph.getImpactAnalysis).not.toHaveBeenCalled();
    });
  });

  describe(useDependencyAnalysis, () => {
    it('should fetch dependency analysis with depth', async () => {
      const mockAnalysis: DependencyAnalysis = {
        dependencies: [],
        dependencyCount: 0,
        depth: 5,
        itemId: 'item-1',
      };
      vi.mocked(api.graph.getDependencyAnalysis).mockResolvedValue(mockAnalysis);

      const { result } = renderHook(() => useDependencyAnalysis('item-1', 5), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(mockAnalysis);
      expect(api.graph.getDependencyAnalysis).toHaveBeenCalledWith('item-1', 5);
    });

    it('should not fetch when id is empty', () => {
      const { result } = renderHook(() => useDependencyAnalysis(''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.graph.getDependencyAnalysis).not.toHaveBeenCalled();
    });
  });

  describe(useFindPath, () => {
    it('should find path between two items', async () => {
      const mockPath = [
        {
          createdAt: '',
          id: 'item-1',
          projectId: 'p1',
          status: 'todo',
          title: '',
          type: 'requirement',
          updatedAt: '',
        },
        {
          createdAt: '',
          id: 'item-2',
          projectId: 'p1',
          status: 'todo',
          title: '',
          type: 'requirement',
          updatedAt: '',
        },
        {
          createdAt: '',
          id: 'item-3',
          projectId: 'p1',
          status: 'todo',
          title: '',
          type: 'requirement',
          updatedAt: '',
        },
      ] as Item[];
      vi.mocked(api.graph.findPath).mockResolvedValue(mockPath);

      const { result } = renderHook(() => useFindPath('item-1', 'item-3'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(mockPath);
      expect(api.graph.findPath).toHaveBeenCalledWith('item-1', 'item-3');
    });

    it('should not fetch when sourceId is empty', () => {
      const { result } = renderHook(() => useFindPath('', 'item-3'), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.graph.findPath).not.toHaveBeenCalled();
    });

    it('should not fetch when targetId is empty', () => {
      const { result } = renderHook(() => useFindPath('item-1', ''), {
        wrapper: createWrapper(),
      });

      expect(result.current.fetchStatus).toBe('idle');
      expect(api.graph.findPath).not.toHaveBeenCalled();
    });

    it('should handle errors', async () => {
      vi.mocked(api.graph.findPath).mockRejectedValue(new Error('Path not found'));

      const { result } = renderHook(() => useFindPath('item-1', 'item-3'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBeTruthy();
      });
    });
  });

  describe(useDetectCycles, () => {
    it('should detect cycles with projectId', async () => {
      const mockCycles: string[][] = [['item-1', 'item-2', 'item-1']];
      vi.mocked(api.graph.detectCycles).mockResolvedValue(mockCycles);

      const { result } = renderHook(() => useDetectCycles('proj-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(mockCycles);
      expect(api.graph.detectCycles).toHaveBeenCalledWith('proj-1');
    });

    it('should detect cycles without projectId', async () => {
      const mockCycles: string[][] = [];
      vi.mocked(api.graph.detectCycles).mockResolvedValue(mockCycles);

      const { result } = renderHook(() => useDetectCycles(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(api.graph.detectCycles).toHaveBeenCalledWith(undefined);
    });

    it('should handle errors', async () => {
      vi.mocked(api.graph.detectCycles).mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useDetectCycles('proj-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBeTruthy();
      });
    });
  });

  describe(useOrphanItems, () => {
    it('should fetch orphan items with projectId', async () => {
      const mockOrphans = [{ id: 'orphan-1' }];
      vi.mocked(api.graph.getOrphanItems).mockResolvedValue(mockOrphans);

      const { result } = renderHook(() => useOrphanItems('proj-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(mockOrphans);
      expect(api.graph.getOrphanItems).toHaveBeenCalledWith('proj-1');
    });

    it('should fetch orphan items without projectId', async () => {
      const mockOrphans = [];
      vi.mocked(api.graph.getOrphanItems).mockResolvedValue(mockOrphans);

      const { result } = renderHook(() => useOrphanItems(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(api.graph.getOrphanItems).toHaveBeenCalledWith(undefined);
    });

    it('should handle errors', async () => {
      vi.mocked(api.graph.getOrphanItems).mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useOrphanItems('proj-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBeTruthy();
      });
    });
  });
});
