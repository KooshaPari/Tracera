// Canonical Concepts API

import type {
  UseMutationOptions,
  UseMutationResult,
  UseQueryOptions,
  UseQueryResult,
} from '@tanstack/react-query';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { client } from './client';

const { apiClient, handleApiResponse } = client;

type ConceptProperties = Record<string, string | number | boolean | object | null | undefined>;
type ProjectionProperties = Record<string, string | number | boolean | object | null | undefined>;

interface CanonicalConcept {
  category?: string;
  createdAt: string;
  description?: string;
  id: string;
  itemCount: number;
  name: string;
  projectId: string;
  properties: ConceptProperties;
  updatedAt: string;
}

interface CanonicalProjection {
  confidence: number;
  createdAt: string;
  conceptId: string;
  id: string;
  itemId: string;
  mappedProperties: ProjectionProperties;
}

interface PivotTarget {
  confidence: number;
  conceptId: string;
  distance: number;
  itemId: string;
}

interface CreateCanonicalConceptInput {
  category?: string;
  description?: string;
  name: string;
  projectId: string;
  properties?: ConceptProperties;
}

interface UpdateCanonicalConceptInput {
  category?: string;
  description?: string;
  name?: string;
  properties?: ConceptProperties;
}

const canonicalQueryKeys = {
  all: ['canonical'] as const,
  detail: (id: string) => [...canonicalQueryKeys.details(), id] as const,
  details: () => [...canonicalQueryKeys.all, 'detail'] as const,
  list: (projectId: string) => [...canonicalQueryKeys.lists(), projectId] as const,
  lists: () => [...canonicalQueryKeys.all, 'list'] as const,
  pivots: (itemId: string) => ['canonical', 'pivots', itemId] as const,
  projections: (conceptId: string) => ['canonical', 'projections', conceptId] as const,
};

type ApiClient = typeof apiClient;

const apiDelete: ApiClient['DELETE'] = apiClient.DELETE;
const apiGet: ApiClient['GET'] = apiClient.GET;
const apiPost: ApiClient['POST'] = apiClient.POST;
const apiPut: ApiClient['PUT'] = apiClient.PUT;

const useCanonicalConcepts = (
  projectId: string,
  options?: UseQueryOptions<CanonicalConcept[]>,
): UseQueryResult<CanonicalConcept[]> => {
  const baseOptions = {
    enabled: Boolean(projectId),
    queryFn: async (): Promise<CanonicalConcept[]> =>
      handleApiResponse(
        apiGet('/api/v1/projects/{projectId}/concepts', {
          params: { path: { projectId } },
        }),
      ),
    queryKey: canonicalQueryKeys.list(projectId),
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useQuery(mergedOptions);
};

const useCanonicalConcept = (
  conceptId: string,
  options?: UseQueryOptions<CanonicalConcept>,
): UseQueryResult<CanonicalConcept> => {
  const baseOptions = {
    enabled: Boolean(conceptId),
    queryFn: async (): Promise<CanonicalConcept> =>
      handleApiResponse(
        apiGet('/api/v1/concepts/{conceptId}', {
          params: { path: { conceptId } },
        }),
      ),
    queryKey: canonicalQueryKeys.detail(conceptId),
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useQuery(mergedOptions);
};

const useCreateCanonicalConcept = (
  options?: UseMutationOptions<CanonicalConcept, Error, CreateCanonicalConceptInput>,
): UseMutationResult<CanonicalConcept, Error, CreateCanonicalConceptInput> => {
  const queryClient = useQueryClient();
  const baseOptions = {
    mutationFn: async (input: CreateCanonicalConceptInput) =>
      handleApiResponse(
        apiPost('/api/v1/projects/{projectId}/concepts', {
          body: {
            category: input.category,
            description: input.description,
            name: input.name,
            properties: input.properties,
          },
          params: { path: { projectId: input.projectId } },
        }),
      ),
    onSuccess: async (data: CanonicalConcept) => {
      await queryClient.invalidateQueries({
        queryKey: canonicalQueryKeys.list(data.projectId),
      });
    },
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useMutation(mergedOptions);
};

const useUpdateCanonicalConcept = (
  options?: UseMutationOptions<
    CanonicalConcept,
    Error,
    { conceptId: string; data: UpdateCanonicalConceptInput }
  >,
): UseMutationResult<
  CanonicalConcept,
  Error,
  { conceptId: string; data: UpdateCanonicalConceptInput }
> => {
  const queryClient = useQueryClient();
  const baseOptions = {
    mutationFn: async (input: { conceptId: string; data: UpdateCanonicalConceptInput }) =>
      handleApiResponse(
        apiPut('/api/v1/concepts/{conceptId}', {
          body: {
            category: input.data.category,
            description: input.data.description,
            name: input.data.name,
            properties: input.data.properties,
          },
          params: { path: { conceptId: input.conceptId } },
        }),
      ),
    onSuccess: async (data: CanonicalConcept) => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: canonicalQueryKeys.detail(data.id),
        }),
        queryClient.invalidateQueries({
          queryKey: canonicalQueryKeys.lists(),
        }),
      ]);
    },
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useMutation(mergedOptions);
};

const useDeleteCanonicalConcept = (
  options?: UseMutationOptions<void, Error, string>,
): UseMutationResult<void, Error, string> => {
  const queryClient = useQueryClient();
  const baseOptions = {
    mutationFn: async (conceptId: string) =>
      handleApiResponse(
        apiDelete('/api/v1/concepts/{conceptId}', {
          params: { path: { conceptId } },
        }),
      ),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: canonicalQueryKeys.lists(),
      });
    },
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useMutation(mergedOptions);
};

const useCanonicalProjections = (
  conceptId: string,
  options?: UseQueryOptions<CanonicalProjection[]>,
): UseQueryResult<CanonicalProjection[]> => {
  const baseOptions = {
    enabled: Boolean(conceptId),
    queryFn: async (): Promise<CanonicalProjection[]> =>
      handleApiResponse(
        apiGet('/api/v1/concepts/{conceptId}/projections', {
          params: { path: { conceptId } },
        }),
      ),
    queryKey: canonicalQueryKeys.projections(conceptId),
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useQuery(mergedOptions);
};

const useCreateCanonicalProjection = (
  options?: UseMutationOptions<
    CanonicalProjection,
    Error,
    { conceptId: string; itemId: string; confidence?: number }
  >,
): UseMutationResult<
  CanonicalProjection,
  Error,
  { conceptId: string; itemId: string; confidence?: number }
> => {
  const queryClient = useQueryClient();
  const baseOptions = {
    mutationFn: async (input: { conceptId: string; itemId: string; confidence?: number }) =>
      handleApiResponse(
        apiPost('/api/v1/concepts/{conceptId}/projections', {
          body: { confidence: input.confidence, itemId: input.itemId },
          params: { path: { conceptId: input.conceptId } },
        }),
      ),
    onSuccess: async (data: CanonicalProjection) => {
      await queryClient.invalidateQueries({
        queryKey: canonicalQueryKeys.projections(data.conceptId),
      });
    },
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useMutation(mergedOptions);
};

const useDeleteCanonicalProjection = (
  options?: UseMutationOptions<void, Error, { conceptId: string; projectionId: string }>,
): UseMutationResult<void, Error, { conceptId: string; projectionId: string }> => {
  const queryClient = useQueryClient();
  const baseOptions = {
    mutationFn: async (input: { conceptId: string; projectionId: string }): Promise<void> =>
      handleApiResponse(
        apiDelete('/api/v1/concepts/{conceptId}/projections/{projectionId}', {
          params: {
            path: { conceptId: input.conceptId, projectionId: input.projectionId },
          },
        }),
      ),
    onSuccess: async (_result: void, variables: { conceptId: string; projectionId: string }) => {
      await queryClient.invalidateQueries({
        queryKey: canonicalQueryKeys.projections(variables.conceptId),
      });
    },
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useMutation(mergedOptions);
};

const usePivotTargets = (
  itemId: string,
  options?: UseQueryOptions<PivotTarget[]>,
): UseQueryResult<PivotTarget[]> => {
  const baseOptions = {
    enabled: Boolean(itemId),
    queryFn: async (): Promise<PivotTarget[]> =>
      handleApiResponse(
        apiGet('/api/v1/items/{itemId}/pivot-targets', {
          params: { path: { itemId } },
        }),
      ),
    queryKey: canonicalQueryKeys.pivots(itemId),
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useQuery(mergedOptions);
};

const usePivotItem = (
  options?: UseMutationOptions<void, Error, { itemId: string; conceptId: string }>,
): UseMutationResult<void, Error, { itemId: string; conceptId: string }> => {
  const queryClient = useQueryClient();
  const baseOptions = {
    mutationFn: async (input: { itemId: string; conceptId: string }): Promise<void> =>
      handleApiResponse(
        apiPost('/api/v1/items/{itemId}/pivot', {
          body: { conceptId: input.conceptId },
          params: { path: { itemId: input.itemId } },
        }),
      ),
    onSuccess: async (_result: void, variables: { itemId: string; conceptId: string }) => {
      await queryClient.invalidateQueries({
        queryKey: canonicalQueryKeys.pivots(variables.itemId),
      });
    },
  };
  const mergedOptions = { ...baseOptions, ...options };

  return useMutation(mergedOptions);
};

const canonicalApi = {
  canonicalQueryKeys,
  useCanonicalConcept,
  useCanonicalConcepts,
  useCanonicalProjections,
  useCreateCanonicalConcept,
  useCreateCanonicalProjection,
  useDeleteCanonicalConcept,
  useDeleteCanonicalProjection,
  usePivotItem,
  usePivotTargets,
  useUpdateCanonicalConcept,
};

export { canonicalApi };
export type {
  CanonicalConcept,
  CanonicalProjection,
  CreateCanonicalConceptInput,
  PivotTarget,
  UpdateCanonicalConceptInput,
};
