import type {
  UseMutationOptions,
  UseMutationResult,
  UseQueryOptions,
  UseQueryResult,
} from '@tanstack/react-query';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { Mutation } from '@tracertm/types';

import { queryKeys } from './queries-keys';
import { api, handleApiResponse } from './query-client';

interface MutationFilters {
  since?: string;
  synced?: boolean;
}

const useMutations = (
  filters?: MutationFilters,
  options?: UseQueryOptions<Mutation[]>,
): UseQueryResult<Mutation[]> => {
  const baseOptions: UseQueryOptions<Mutation[]> = {
    queryFn: async () =>
      await handleApiResponse(
        api.get<Mutation[]>('/api/v1/mutations', {
          params: { query: filters },
        }),
      ),
    queryKey: queryKeys.mutations(filters),
  };

  return useQuery({ ...baseOptions, ...options });
};

const useCreateMutation = (
  options?: UseMutationOptions<Mutation, Error, Partial<Mutation>>,
): UseMutationResult<Mutation, Error, Partial<Mutation>> => {
  const queryClient = useQueryClient();
  const baseOptions: UseMutationOptions<Mutation, Error, Partial<Mutation>> = {
    mutationFn: async (data: Partial<Mutation>) =>
      await handleApiResponse(
        api.post<Mutation>('/api/v1/mutations', {
          body: data as Record<string, unknown>,
        }),
      ),
    onSuccess: async (): Promise<void> => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.mutations() });
    },
  };

  return useMutation({ ...baseOptions, ...options });
};

export { useCreateMutation, useMutations };
