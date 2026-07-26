/**
 * Comprehensive tests for useItems hooks
 * Tests all React Query hooks for items CRUD operations
 */

import type { ReactNode } from 'react';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { Item, ItemStatus, ViewType } from '@tracertm/types';

import {
  useCreateItem,
  useDeleteItem,
  useItem,
  useItems,
  useUpdateItem,
} from '../../hooks/useItems';

// Mock fetch globally
globalThis.fetch = vi.fn();

const mockItem: Item = {
  createdAt: '2024-01-01T00:00:00Z',
  id: 'item-1',
  priority: 'high',
  projectId: 'proj-1',
  status: 'todo',
  title: 'Test Feature',
  type: 'feature',
  updatedAt: '2024-01-01T00:00:00Z',
  view: 'features',
} as any;

const mockItems: Item[] = [
  mockItem,
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'item-2',
    priority: 'medium',
    projectId: 'proj-1',
    status: 'in_progress',
    title: 'Test Task',
    type: 'task',
    updatedAt: '2024-01-01T00:00:00Z',
    view: 'code',
  } as any,
  {
    createdAt: '2024-01-01T00:00:00Z',
    id: 'item-3',
    priority: 'low',
    projectId: 'proj-2',
    status: 'done',
    title: 'Test Bug',
    type: 'bug',
    updatedAt: '2024-01-01T00:00:00Z',
    view: 'tests',
  } as any,
];

describe('useItems hooks', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: {
          retry: false,
        },
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  describe(useItems, () => {
    it('should not fetch without projectId', () => {
      (fetch as any).mockResolvedValueOnce({
        json: async () => ({ items: mockItems, total: mockItems.length }),
        ok: true,
      } as Response);

      const { result } = renderHook(() => useItems(), { wrapper });

      expect(result.current.fetchStatus).toBe('idle');
      expect(fetch).not.toHaveBeenCalled();
    });

    it('should fetch items with multiple filters', async () => {
      (fetch as any).mockResolvedValueOnce({
        json: async () => ({
          items: mockItems,
          total: mockItems.length,
        }),
        ok: true,
      } as Response);

      const { result } = renderHook(
        () =>
          useItems({
            projectId: 'proj-1',
            status: 'todo' as ItemStatus,
            view: 'features' as ViewType,
          }),
        { wrapper },
      );

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      const call = (fetch as any).mock.calls[0]?.[0] as string;
      expect(call).toContain('project_id=proj-1');
      expect(call).toContain('view=features');
      expect(call).toContain('status=todo');
    });
  });

  describe(useItem, () => {
    it('should not fetch when id is empty', () => {
      const { result } = renderHook(() => useItem(''), { wrapper });

      expect(result.current.fetchStatus).toBe('idle');
      expect(fetch).not.toHaveBeenCalled();
    });
  });

  describe(useCreateItem, () => {
    it('should invalidate queries on success', async () => {
      (fetch as any).mockResolvedValueOnce({
        json: async () => mockItem,
        ok: true,
      } as Response);

      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useCreateItem(), { wrapper });

      result.current.mutate({
        priority: 'high' as const,
        projectId: 'proj-1',
        status: 'todo' as ItemStatus,
        title: 'New Feature',
        type: 'feature',
        view: 'FEATURE' as ViewType,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(invalidateSpy).toHaveBeenCalledWith(expect.objectContaining({ queryKey: ['items'] }));
    });

    it('should include optional fields in request', async () => {
      (fetch as any).mockResolvedValueOnce({
        json: async () => mockItem,
        ok: true,
      } as Response);

      const { result } = renderHook(() => useCreateItem(), { wrapper });

      result.current.mutate({
        description: 'Test description',
        owner: 'user-1',
        parentId: 'parent-1',
        priority: 'high' as const,
        projectId: 'proj-1',
        status: 'todo' as ItemStatus,
        title: 'New Feature',
        type: 'feature',
        view: 'FEATURE' as ViewType,
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      const callBody = JSON.parse((fetch as any).mock.calls[0]?.[1]?.body as string);
      expect(callBody.description).toBe('Test description');
      expect(callBody.parent_id).toBe('parent-1');
      expect(callBody.owner).toBe('user-1');
    });
  });

  describe(useUpdateItem, () => {
    it('should invalidate item and list queries on success', async () => {
      (fetch as any).mockResolvedValueOnce({
        json: async () => mockItem,
        ok: true,
      } as Response);

      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useUpdateItem(), { wrapper });

      result.current.mutate({
        data: { title: 'Updated' },
        id: 'item-1',
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(invalidateSpy).toHaveBeenCalledWith(expect.objectContaining({ queryKey: ['items'] }));
      expect(invalidateSpy).toHaveBeenCalledWith(
        expect.objectContaining({ queryKey: ['items', 'item-1'] }),
      );
    });
  });

  describe(useDeleteItem, () => {
    it('should delete item', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: true,
      } as Response);

      const { result } = renderHook(() => useDeleteItem(), { wrapper });

      result.current.mutate('item-1');

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/items/item-1'),
        expect.objectContaining({
          method: 'DELETE',
        }),
      );
    });

    it('should invalidate queries on success', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: true,
      } as Response);

      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useDeleteItem(), { wrapper });

      result.current.mutate('item-1');

      await waitFor(() => {
        expect(result.current.isSuccess).toBeTruthy();
      });

      expect(invalidateSpy).toHaveBeenCalledWith(expect.objectContaining({ queryKey: ['items'] }));
    });
  });
});
