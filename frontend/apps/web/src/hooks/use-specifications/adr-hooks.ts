import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import * as specificationsApi from '@/hooks/useSpecifications.api';
import * as queryUtils from './query-utils';

type FetchADRsResult = Awaited<ReturnType<typeof specificationsApi.fetchADRs>>;

type FetchADRResult = Awaited<ReturnType<typeof specificationsApi.fetchADR>>;

type CreateADRResult = Awaited<ReturnType<typeof specificationsApi.createADR>>;

type UpdateADRResult = Awaited<ReturnType<typeof specificationsApi.updateADR>>;

type VerifyADRResult = Awaited<ReturnType<typeof specificationsApi.verifyADR>>;

type FetchADRActivitiesResult = Awaited<ReturnType<typeof specificationsApi.fetchADRActivities>>;

type FetchADRStatsResult = Awaited<ReturnType<typeof specificationsApi.fetchADRStats>>;

const useADRs = (
  filters: specificationsApi.ADRFilters,
): queryUtils.QueryResult<FetchADRsResult> =>
  useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: async () => {
      const response = await specificationsApi.fetchADRs(filters);
      return response;
    },
    queryKey: ['adrs', JSON.stringify(filters)],
  });

const useADR = (id: string): queryUtils.QueryResult<FetchADRResult> =>
  useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const response = await specificationsApi.fetchADR(id);
      return response;
    },
    queryKey: ['adrs', id],
  });

const useCreateADR = (): queryUtils.MutationResult<CreateADRResult, specificationsApi.CreateADRData> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: specificationsApi.CreateADRData) => {
      const response = await specificationsApi.createADR(data);
      return response;
    },
    onSuccess: async (_, variables) => {
      await queryUtils.invalidateQueries(queryClient, [['adrs'], ['adrStats']]);
      await queryClient.invalidateQueries({
        queryKey: ['specificationSummary', variables.projectId],
      });
    },
  });
};

const useUpdateADR = (): queryUtils.MutationResult<
  UpdateADRResult,
  { id: string; data: specificationsApi.UpdateADRData }
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: specificationsApi.UpdateADRData }) => {
      const response = await specificationsApi.updateADR(id, data);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await queryUtils.invalidateQueries(queryClient, [['adrs', id], ['adrs'], ['adrStats']]);
    },
  });
};

const useDeleteADR = (): queryUtils.MutationResult<void, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await specificationsApi.deleteADR(id);
    },
    onSuccess: async () => {
      await queryUtils.invalidateQueries(queryClient, [['adrs'], ['adrStats'], ['specificationSummary']]);
    },
  });
};

const useVerifyADR = (): queryUtils.MutationResult<VerifyADRResult, { id: string; notes: string }> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, notes }: { id: string; notes: string }) => {
      const response = await specificationsApi.verifyADR(id, notes);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await queryUtils.invalidateQueries(queryClient, [['adrs', id], ['adrs'], ['adrStats']]);
      await queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
};

const useADRActivities = (adrId: string): queryUtils.QueryResult<FetchADRActivitiesResult> =>
  useQuery({
    enabled: Boolean(adrId),
    queryFn: async () => {
      const response = await specificationsApi.fetchADRActivities(adrId);
      return response;
    },
    queryKey: ['adrActivities', adrId],
  });

const useADRStats = (projectId: string): queryUtils.QueryResult<FetchADRStatsResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await specificationsApi.fetchADRStats(projectId);
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
