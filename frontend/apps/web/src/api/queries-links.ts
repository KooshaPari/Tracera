import type {
  UseMutationOptions,
  UseMutationResult,
  UseQueryOptions,
  UseQueryResult,
} from '@tanstack/react-query';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { Link } from '@tracertm/types';

import { queryKeys } from './queries-keys';
import { api, handleApiResponse } from './query-client';

interface CreateLinkInput {
  data: Partial<Link>;
  projectId: string;
}

interface DeleteLinkInput {
  linkId: string;
  projectId: string;
}

const useProjectLinks = (
  projectId: string,
  options?: UseQueryOptions<Link[]>,
): UseQueryResult<Link[]> => {
  const baseOptions: UseQueryOptions<Link[]> = {
    enabled: Boolean(projectId),
    queryFn: async () =>
      handleApiResponse(
        api.get<Link[]>('/api/v1/projects/{projectId}/links', {
          params: { path: { projectId } },
        }),
      ),
    queryKey: queryKeys.projectLinks(projectId),
  };

  return useQuery({ ...baseOptions, ...options });
};

const useCreateLink = (
  options?: UseMutationOptions<Link, Error, CreateLinkInput>,
): UseMutationResult<Link, Error, CreateLinkInput> => {
  const queryClient = useQueryClient();
  const baseOptions: UseMutationOptions<Link, Error, CreateLinkInput> = {
    mutationFn: async (input: CreateLinkInput) =>
      handleApiResponse(
        api.post<Link>('/api/v1/projects/{projectId}/links', {
          body: input.data as Record<string, unknown>,
          params: { path: { projectId: input.projectId } },
        }),
      ),
    onSuccess: async (_res: Link, variables: CreateLinkInput): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.projectLinks(variables.projectId),
      });
    },
  };

  return useMutation({ ...baseOptions, ...options });
};

const useDeleteLink = (
  options?: UseMutationOptions<void, Error, DeleteLinkInput>,
): UseMutationResult<void, Error, DeleteLinkInput> => {
  const queryClient = useQueryClient();
  const baseOptions: UseMutationOptions<void, Error, DeleteLinkInput> = {
    mutationFn: async (input: DeleteLinkInput) => {
      await handleApiResponse(
        api.del<void>('/api/v1/links/{linkId}', {
          params: { path: { linkId: input.linkId } },
        }),
      );
    },
    onSuccess: async (_res: void, variables: DeleteLinkInput): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.projectLinks(variables.projectId),
      });
    },
  };

  return useMutation({ ...baseOptions, ...options });
};

export { useCreateLink, useDeleteLink, useProjectLinks };
