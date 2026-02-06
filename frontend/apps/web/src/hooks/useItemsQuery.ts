import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { CreateItemInput, UpdateItemInput } from '../api/types';

import { api } from '../api/endpoints';
import { useItemsStore } from '../stores/items-store';

// Query keys
export const itemKeys = {
  all: ['items'] as const,
  byProject: (projectId: string) => [...itemKeys.all, 'project', projectId] as const,
  detail: (id: string) => [...itemKeys.details(), id] as const,
  details: () => [...itemKeys.all, 'detail'] as const,
  list: (filters: any) => [...itemKeys.lists(), filters] as const,
  lists: () => [...itemKeys.all, 'list'] as const,
};

// Hooks
export function useItemsQuery(projectId?: string) {
  const { addItems, setLoading } = useItemsStore();

  return useQuery({
    queryFn: async () => {
      setLoading(true);
      try {
        const response = await api.items.list(projectId ? { project_id: projectId } : {});
        const items = Array.isArray(response) ? response : response.items;
        addItems(items);
        return response;
      } finally {
        setLoading(false);
      }
    },
    queryKey: projectId ? itemKeys.byProject(projectId) : itemKeys.lists(),
    staleTime: 30_000, // 30 seconds
  });
}

export function useItemQuery(id: string) {
  const { addItem } = useItemsStore();

  return useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const item = await api.items.get(id);
      addItem(item);
      return item;
    },
    queryKey: itemKeys.detail(id),
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();
  const { optimisticCreate, confirmCreate, rollbackCreate } = useItemsStore();

  return useMutation({
    mutationFn: async (data: CreateItemInput) => {
      const tempId = `temp-${Date.now()}`;
      optimisticCreate(tempId, data);

      try {
        const item = await api.items.create(data);
        confirmCreate(tempId, item);
        return item;
      } catch (error) {
        rollbackCreate(tempId);
        throw error;
      }
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: itemKeys.all });
    },
  });
}

export function useUpdateItem() {
  const queryClient = useQueryClient();
  const { optimisticUpdate, confirmUpdate, rollbackUpdate } = useItemsStore();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateItemInput }) => {
      optimisticUpdate(id, data);

      try {
        const item = await api.items.update(id, data);
        confirmUpdate(id, item);
        return item;
      } catch (error) {
        rollbackUpdate(id);
        throw error;
      }
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: itemKeys.all });
    },
  });
}

export function useDeleteItem() {
  const queryClient = useQueryClient();
  const { optimisticDelete, confirmDelete, rollbackDelete, getItem } = useItemsStore();

  return useMutation({
    mutationFn: async (id: string) => {
      const item = getItem(id);
      if (!item) {
        throw new Error('Item not found');
      }

      optimisticDelete(id);

      try {
        await api.items.delete(id);
        confirmDelete(id);
      } catch (error) {
        rollbackDelete(id, item);
        throw error;
      }
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: itemKeys.all });
    },
  });
}

// Get items from store
export function useItemsFromStore(projectId?: string) {
  return useItemsStore((state) =>
    projectId ? state.getItemsByProject(projectId) : [...state.items.values()],
  );
}

export function useItemFromStore(id: string) {
  return useItemsStore((state) => state.getItem(id));
}
