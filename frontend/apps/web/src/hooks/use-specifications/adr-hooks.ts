import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  createADR,
  deleteADR,
  fetchADR,
  fetchADRActivities,
  fetchADRs,
  fetchADRStats,
  updateADR,
  verifyADR,
  type ADRFilters,
  type CreateADRData,
  type UpdateADRData,
} from '@/hooks/useSpecifications.api';

import { invalidateQueries, type MutationResult, type QueryResult } from './query-utils';

type FetchADRsResult = Awaited<ReturnType<typeof fetchADRs>>;

type FetchADRResult = Awaited<ReturnType<typeof fetchADR>>;

type CreateADRResult = Awaited<ReturnType<typeof createADR>>;

type UpdateADRResult = Awaited<ReturnType<typeof updateADR>>;

type VerifyADRResult = Awaited<ReturnType<typeof verifyADR>>;

type FetchADRActivitiesResult = Awaited<ReturnType<typeof fetchADRActivities>>;

type FetchADRStatsResult = Awaited<ReturnType<typeof fetchADRStats>>;

const useADRs = (filters: ADRFilters): QueryResult<FetchADRsResult> =>
  useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: async () => {
      const response = await fetchADRs(filters);
      return response;
    },
    queryKey: ['adrs', JSON.stringify(filters)],
  });

const useADR = (id: string): QueryResult<FetchADRResult> =>
  useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const response = await fetchADR(id);
      return response;
    },
    queryKey: ['adrs', id],
  });

const useCreateADR = (): MutationResult<CreateADRResult, CreateADRData> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateADRData) => {
      const response = await createADR(data);
      return response;
    },
    onSuccess: async (_, variables) => {
      await invalidateQueries(queryClient, [['adrs'], ['adrStats']]);
      await queryClient.invalidateQueries({
        queryKey: ['specificationSummary', variables.projectId],
      });
    },
  });
};

const useUpdateADR = (): MutationResult<UpdateADRResult, { id: string; data: UpdateADRData }> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateADRData }) => {
      const response = await updateADR(id, data);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await invalidateQueries(queryClient, [['adrs', id], ['adrs'], ['adrStats']]);
    },
  });
};

const useDeleteADR = (): MutationResult<void, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await deleteADR(id);
    },
    onSuccess: async () => {
      await invalidateQueries(queryClient, [['adrs'], ['adrStats'], ['specificationSummary']]);
    },
  });
};

const useVerifyADR = (): MutationResult<VerifyADRResult, { id: string; notes: string }> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, notes }: { id: string; notes: string }) => {
      const response = await verifyADR(id, notes);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await invalidateQueries(queryClient, [['adrs', id], ['adrs'], ['adrStats']]);
      await queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
};

const useADRActivities = (adrId: string): QueryResult<FetchADRActivitiesResult> =>
  useQuery({
    enabled: Boolean(adrId),
    queryFn: async () => {
      const response = await fetchADRActivities(adrId);
      return response;
    },
    queryKey: ['adrActivities', adrId],
  });

const useADRStats = (projectId: string): QueryResult<FetchADRStatsResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await fetchADRStats(projectId);
      return response;
    },
    queryKey: ['adrStats', projectId],
  });

export {
  useADR,
  useADRActivities,
  useADRs,
  useADRStats,
  useCreateADR,
  useDeleteADR,
  useUpdateADR,
  useVerifyADR,
  type CreateADRResult,
  type FetchADRActivitiesResult,
  type FetchADRResult,
  type FetchADRsResult,
  type FetchADRStatsResult,
  type UpdateADRResult,
  type VerifyADRResult,
};
