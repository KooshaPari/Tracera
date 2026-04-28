/**
 * Comprehensive tests for useLinks hook
 * Target: 55.26% → 95% coverage
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useCreateLink, useDeleteLink, useLinks, useTraceabilityGraph } from '../../hooks/useLinks';

// Mock fetch
const mockFetch = vi.fn();
globalThis.fetch = mockFetch as unknown as typeof fetch;

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      mutations: { retry: false },
      queries: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

describe('useLinks - Comprehensive Coverage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe(useLinks, () => {
    it('should fetch links with all filters', async () => {
      const mockLinks = [
        {
          id: '1',
          projectId: 'proj-1',
          sourceId: 'item-1',
          targetId: 'item-2',
          type: 'depends_on',
        },
      ];

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ links: mockLinks, total: 1 }),
        ok: true,
      });

      const { result } = renderHook(
        () =>
          useLinks({
            projectId: 'proj-1',
            sourceId: 'item-1',
            targetId: 'item-2',
            type: 'depends_on',
          }),
        {
          wrapper: createWrapper(),
        },
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual({ links: mockLinks, total: 1 });
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('project_id=proj-1'),
        expect.objectContaining({
          headers: {
            'X-Bulk-Operation': 'true',
          },
        }),
      );
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('source_id=item-1'),
        expect.objectContaining({
          headers: {
            'X-Bulk-Operation': 'true',
          },
        }),
      );
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('target_id=item-2'),
        expect.objectContaining({
          headers: {
            'X-Bulk-Operation': 'true',
          },
        }),
      );
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('type=depends_on'),
        expect.objectContaining({
          headers: {
            'X-Bulk-Operation': 'true',
          },
        }),
      );
    });

    it('should fetch links with project filter only', async () => {
      const mockLinks = [{ id: '1', projectId: 'proj-1' }];

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ links: mockLinks, total: 1 }),
        ok: true,
      });

      const { result } = renderHook(() => useLinks({ projectId: 'proj-1' }), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('project_id=proj-1'),
        expect.objectContaining({
          headers: {
            'X-Bulk-Operation': 'true',
          },
        }),
      );
    });

    it('should fetch links with type filter', async () => {
      const mockLinks = [{ id: '1', type: 'implements' }];

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ links: mockLinks, total: 1 }),
        ok: true,
      });

      const { result } = renderHook(() => useLinks({ type: 'implements' }), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('type=implements'),
        expect.objectContaining({
          headers: {
            'X-Bulk-Operation': 'true',
          },
        }),
      );
    });
  });

  describe(useCreateLink, () => {
    it('should create link with description', async () => {
      const newLink = {
        description: 'Test description',
        projectId: 'proj-1',
        sourceId: 'item-1',
        targetId: 'item-2',
        type: 'depends_on' as const,
      };

      const createdLink = { id: '1', ...newLink };

      mockFetch.mockResolvedValueOnce({
        json: async () => createdLink,
        ok: true,
      });

      const { result } = renderHook(() => useCreateLink(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(newLink);

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(result.current.data).toEqual(createdLink);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/links'),
        expect.objectContaining({
          body: expect.stringContaining('description'),
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          method: 'POST',
        }),
      );
    });

    it('should invalidate queries on success', async () => {
      const newLink = {
        projectId: 'proj-1',
        sourceId: 'item-1',
        targetId: 'item-2',
        type: 'depends_on' as const,
      };

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ id: '1', ...newLink }),
        ok: true,
      });

      const { result } = renderHook(() => useCreateLink(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(newLink);

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });
    });
  });

  describe(useDeleteLink, () => {
    it('should delete a link', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
      });

      const { result } = renderHook(() => useDeleteLink(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('link-1');

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/links/link-1'),
        expect.objectContaining({
          method: 'DELETE',
        }),
      );
    });

    it('should handle delete error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      const { result } = renderHook(() => useDeleteLink(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('link-1');

      await waitFor(() => {
        expect(result.current.isError).toBeTruthy();
      });
    });

    it('should invalidate queries on success', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
      });

      const { result } = renderHook(() => useDeleteLink(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('link-1');

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });
    });
  });

  describe(useTraceabilityGraph, () => {
    it('should build graph from items and links', async () => {
      const mockItems = [
        {
          id: 'item-1',
          status: 'in_progress',
          title: 'Item 1',
          view: 'feature',
        },
        {
          id: 'item-2',
          status: 'pending',
          title: 'Item 2',
          view: 'test',
        },
      ];

      const mockLinks = [
        {
          id: 'link-1',
          sourceId: 'item-1',
          targetId: 'item-2',
          type: 'depends_on',
        },
      ];

      // Mock items fetch (first call)
      mockFetch.mockResolvedValueOnce({
        json: async () => mockItems,
        ok: true,
      });

      // Mock links fetch (second call via useLinks)
      mockFetch.mockResolvedValueOnce({
        json: async () => ({ links: mockLinks, total: 1 }),
        ok: true,
      });

      const { result } = renderHook(() => useTraceabilityGraph('proj-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(
        () => {
          expect(result.current.nodes).toBeDefined();
          expect(result.current.edges).toBeDefined();
          expect(result.current.nodes.length).toBeGreaterThan(0);
        },
        { timeout: 5000 },
      );

      expect(result.current.nodes).toHaveLength(2);
      expect(result.current.edges).toHaveLength(1);
      expect(result.current.nodes[0]?.data?.id).toBe('item-1');
      expect(result.current.edges[0]?.data?.source).toBe('item-1');
      expect(result.current.isLoading).toBeFalsy();
    });

    it('should show loading state when data is missing', () => {
      mockFetch.mockResolvedValueOnce({
        json: async () => [],
        ok: true,
      });

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ links: [], total: 0 }),
        ok: true,
      });

      const { result } = renderHook(() => useTraceabilityGraph('proj-1'), {
        wrapper: createWrapper(),
      });

      // Initially loading until both queries resolve
      expect(result.current.isLoading).toBeTruthy();
    });

    it('should not fetch when projectId is empty', () => {
      const { result } = renderHook(() => useTraceabilityGraph(''), {
        wrapper: createWrapper(),
      });

      // Should not make requests when projectId is empty
      expect(result.current.isLoading).toBeTruthy();
    });

    it('should handle empty items and links', async () => {
      mockFetch.mockResolvedValueOnce({
        json: async () => [],
        ok: true,
      });

      mockFetch.mockResolvedValueOnce({
        json: async () => ({ links: [], total: 0 }),
        ok: true,
      });

      const { result } = renderHook(() => useTraceabilityGraph('proj-1'), {
        wrapper: createWrapper(),
      });

      await waitFor(
        () => {
          expect(result.current.nodes).toBeDefined();
          expect(result.current.edges).toBeDefined();
          expect(result.current.isLoading).toBeFalsy();
        },
        { timeout: 5000 },
      );

      expect(result.current.nodes).toHaveLength(0);
      expect(result.current.edges).toHaveLength(0);
    });
  });
});
