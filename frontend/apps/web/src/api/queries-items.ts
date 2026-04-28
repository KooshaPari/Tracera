import type {
  UseMutationOptions,
  UseMutationResult,
  UseQueryOptions,
  UseQueryResult,
} from '@tanstack/react-query';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { Item, PaginatedResponse } from '@tracertm/types';

import { queryKeys } from './queries-keys';
import { api, handleApiResponse } from './query-client';

type ItemListResponse = PaginatedResponse<Item>;

interface ItemFilters {
  page?: number;
  pageSize?: number;
  priority?: string;
  status?: string;
  view?: string;
}

interface CreateItemInput {
  data: Partial<Item>;
  projectId: string;
}

interface UpdateItemInput {
  data: Partial<Item>;
  itemId: string;
}

interface DeleteItemInput {
  itemId: string;
  projectId: string;
}

const useProjectItems = (
  projectId: string,
  filters?: ItemFilters,
  options?: UseQueryOptions<ItemListResponse>,
): UseQueryResult<ItemListResponse> => {
  const queryFilters: Record<string, unknown> | undefined = filters ? { ...filters } : undefined;
  const baseOptions: UseQueryOptions<ItemListResponse> = {
    enabled: Boolean(projectId),
    queryFn: async (): Promise<ItemListResponse> =>
      handleApiResponse(
        api.get<ItemListResponse>('/api/v1/projects/{projectId}/items', {
          params: {
            path: { projectId },
            query: queryFilters,
          },
        }),
      ),
    queryKey: queryKeys.projectItems(projectId, queryFilters),
  };

  return useQuery({ ...baseOptions, ...options });
};

const useItem = (itemId: string, options?: UseQueryOptions<Item>): UseQueryResult<Item> => {
  const baseOptions: UseQueryOptions<Item> = {
    enabled: Boolean(itemId),
    queryFn: async (): Promise<Item> =>
      handleApiResponse(
        api.get<Item>('/api/v1/items/{itemId}', {
          params: { path: { itemId } },
        }),
      ),
    queryKey: queryKeys.item(itemId),
  };

  return useQuery({ ...baseOptions, ...options });
};

const useCreateItem = (
  options?: UseMutationOptions<Item, Error, CreateItemInput>,
): UseMutationResult<Item, Error, CreateItemInput> => {
  const queryClient = useQueryClient();
  const baseOptions: UseMutationOptions<Item, Error, CreateItemInput> = {
    mutationFn: async (input: CreateItemInput): Promise<Item> =>
      handleApiResponse(
        api.post<Item>('/api/v1/projects/{projectId}/items', {
          body: input.data as Record<string, unknown>,
          params: { path: { projectId: input.projectId } },
        }),
      ),
    onSuccess: async (_data: Item, variables: CreateItemInput): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.projectItems(variables.projectId),
      });
    },
  };

  return useMutation({ ...baseOptions, ...options });
};

const useUpdateItem = (
  options?: UseMutationOptions<Item, Error, UpdateItemInput>,
): UseMutationResult<Item, Error, UpdateItemInput> => {
  const queryClient = useQueryClient();
  const baseOptions: UseMutationOptions<Item, Error, UpdateItemInput> = {
    mutationFn: async (input: UpdateItemInput): Promise<Item> =>
      handleApiResponse(
        api.put<Item>('/api/v1/items/{itemId}', {
          body: input.data,
          params: { path: { itemId: input.itemId } },
        }),
      ),
    onSuccess: async (data: Item): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.item(data.id),
      });
      await queryClient.invalidateQueries({
        queryKey: queryKeys.projectItems(data.projectId),
      });
    },
  };

  return useMutation({ ...baseOptions, ...options });
};

const useDeleteItem = (
  options?: UseMutationOptions<void, Error, DeleteItemInput>,
): UseMutationResult<void, Error, DeleteItemInput> => {
  const queryClient = useQueryClient();
  const baseOptions: UseMutationOptions<void, Error, DeleteItemInput> = {
    mutationFn: async (input: DeleteItemInput): Promise<void> => {
      await handleApiResponse(
        api.del<void>('/api/v1/items/{itemId}', {
          params: { path: { itemId: input.itemId } },
        }),
      );
    },
    onSuccess: async (_data: void, variables: DeleteItemInput): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.projectItems(variables.projectId),
      });
    },
  };

  return useMutation({ ...baseOptions, ...options });
};

export { useCreateItem, useDeleteItem, useItem, useProjectItems, useUpdateItem };
