import * as ReactQuery from '@tanstack/react-query';

import { client } from './client';

type ApiClient = typeof client.apiClient;

const { apiClient } = client;
const { handleApiResponse } = client;
const get: ApiClient['GET'] = apiClient.GET.bind(apiClient);
const post: ApiClient['POST'] = apiClient.POST.bind(apiClient);

// Types for equivalence API
interface EquivalenceLink {
  confirmedAt?: string;
  confidence: number;
  createdAt: string;
  id: string;
  itemId1: string;
  itemId2: string;
  similarity: number;
  status: 'pending' | 'confirmed' | 'rejected';
}

interface ConfirmEquivalenceInput {
  comment?: string;
  equivalenceId: string;
}

interface DetectEquivalencesInput {
  projectId: string;
  threshold?: number;
}

interface RejectEquivalenceInput {
  equivalenceId: string;
  reason?: string;
}

// Query Keys
const equivalenceQueryKeys = {
  all: ['equivalences'] as const,
  detail: (id: string) => [...equivalenceQueryKeys.details(), id] as const,
  details: () => [...equivalenceQueryKeys.all, 'detail'] as const,
  list: (projectId: string, status?: string) =>
    [...equivalenceQueryKeys.lists(), projectId, status] as const,
  lists: () => [...equivalenceQueryKeys.all, 'list'] as const,
};

const useEquivalenceLinks = (
  projectId: string,
  status?: string,
  options?: ReactQuery.UseQueryOptions<EquivalenceLink[]>,
): ReactQuery.UseQueryResult<EquivalenceLink[]> => {
  const query: Record<string, string> = {};
  if (status && status !== '') {
    query['status'] = status;
  }

  const baseOptions: ReactQuery.UseQueryOptions<EquivalenceLink[]> = {
    enabled: Boolean(projectId),
    queryFn: async (): Promise<EquivalenceLink[]> =>
      handleApiResponse(
        get('/api/v1/projects/{projectId}/equivalences', {
          params: {
            path: { projectId },
            query,
          },
        }),
      ),
    queryKey: equivalenceQueryKeys.list(projectId, status),
  };

  return ReactQuery.useQuery({ ...baseOptions, ...options });
};

const useEquivalenceLink = (
  equivalenceId: string,
  options?: ReactQuery.UseQueryOptions<EquivalenceLink>,
): ReactQuery.UseQueryResult<EquivalenceLink> => {
  const baseOptions: ReactQuery.UseQueryOptions<EquivalenceLink> = {
    enabled: Boolean(equivalenceId),
    queryFn: async (): Promise<EquivalenceLink> =>
      handleApiResponse(
        get('/api/v1/equivalences/{equivalenceId}', {
          params: { path: { equivalenceId } },
        }),
      ),
    queryKey: equivalenceQueryKeys.detail(equivalenceId),
  };

  return ReactQuery.useQuery({ ...baseOptions, ...options });
};

const useDetectEquivalences = (
  options?: ReactQuery.UseMutationOptions<EquivalenceLink[], Error, DetectEquivalencesInput>,
): ReactQuery.UseMutationResult<EquivalenceLink[], Error, DetectEquivalencesInput> => {
  const queryClient = ReactQuery.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<
    EquivalenceLink[],
    Error,
    DetectEquivalencesInput
  > = {
    mutationFn: async (input: DetectEquivalencesInput) => {
      const { projectId, threshold } = input;
      return handleApiResponse(
        post('/api/v1/projects/{projectId}/equivalences/detect', {
          body: { threshold },
          params: { path: { projectId } },
        }),
      );
    },
    onSuccess: async (_data: EquivalenceLink[], variables: DetectEquivalencesInput) => {
      await queryClient.invalidateQueries({
        queryKey: equivalenceQueryKeys.list(variables.projectId),
      });
    },
  };

  return ReactQuery.useMutation({ ...baseOptions, ...options });
};

const useConfirmEquivalence = (
  options?: ReactQuery.UseMutationOptions<EquivalenceLink, Error, ConfirmEquivalenceInput>,
): ReactQuery.UseMutationResult<EquivalenceLink, Error, ConfirmEquivalenceInput> => {
  const queryClient = ReactQuery.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<
    EquivalenceLink,
    Error,
    ConfirmEquivalenceInput
  > = {
    mutationFn: async (input: ConfirmEquivalenceInput) =>
      handleApiResponse(
        post('/api/v1/equivalences/{equivalenceId}/confirm', {
          body: { comment: input.comment },
          params: { path: { equivalenceId: input.equivalenceId } },
        }),
      ),
    onSuccess: async (data: EquivalenceLink) => {
      await queryClient.invalidateQueries({
        queryKey: equivalenceQueryKeys.detail(data.id),
      });
      await queryClient.invalidateQueries({
        queryKey: equivalenceQueryKeys.lists(),
      });
    },
  };

  return ReactQuery.useMutation({ ...baseOptions, ...options });
};

const useRejectEquivalence = (
  options?: ReactQuery.UseMutationOptions<void, Error, RejectEquivalenceInput>,
): ReactQuery.UseMutationResult<void, Error, RejectEquivalenceInput> => {
  const queryClient = ReactQuery.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<void, Error, RejectEquivalenceInput> = {
    mutationFn: async (input: RejectEquivalenceInput) =>
      handleApiResponse(
        post('/api/v1/equivalences/{equivalenceId}/reject', {
          body: { reason: input.reason },
          params: { path: { equivalenceId: input.equivalenceId } },
        }),
      ),
    onSuccess: async (_data, variables: RejectEquivalenceInput) => {
      await queryClient.invalidateQueries({
        queryKey: equivalenceQueryKeys.detail(variables.equivalenceId),
      });
      await queryClient.invalidateQueries({
        queryKey: equivalenceQueryKeys.lists(),
      });
    },
  };

  return ReactQuery.useMutation({ ...baseOptions, ...options });
};

const useBatchConfirmEquivalences = (
  options?: ReactQuery.UseMutationOptions<EquivalenceLink[], Error, string[]>,
): ReactQuery.UseMutationResult<EquivalenceLink[], Error, string[]> => {
  const queryClient = ReactQuery.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<EquivalenceLink[], Error, string[]> = {
    mutationFn: async (equivalenceIds: string[]) =>
      handleApiResponse(
        post('/api/v1/equivalences/batch-confirm', {
          body: { equivalenceIds },
        }),
      ),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: equivalenceQueryKeys.lists(),
      });
    },
  };

  return ReactQuery.useMutation({ ...baseOptions, ...options });
};

const useBatchRejectEquivalences = (
  options?: ReactQuery.UseMutationOptions<void, Error, string[]>,
): ReactQuery.UseMutationResult<void, Error, string[]> => {
  const queryClient = ReactQuery.useQueryClient();
  const baseOptions: ReactQuery.UseMutationOptions<void, Error, string[]> = {
    mutationFn: async (equivalenceIds: string[]) =>
      handleApiResponse(
        post('/api/v1/equivalences/batch-reject', {
          body: { equivalenceIds },
        }),
      ),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: equivalenceQueryKeys.lists(),
      });
    },
  };

  return ReactQuery.useMutation({ ...baseOptions, ...options });
};

export {
  equivalenceQueryKeys,
  useBatchConfirmEquivalences,
  useBatchRejectEquivalences,
  useConfirmEquivalence,
  useDetectEquivalences,
  useEquivalenceLink,
  useEquivalenceLinks,
  useRejectEquivalence,
  type ConfirmEquivalenceInput,
  type DetectEquivalencesInput,
  type EquivalenceLink,
  type RejectEquivalenceInput,
};
