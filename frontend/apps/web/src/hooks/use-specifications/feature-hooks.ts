import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import * as specificationsApi from '@/hooks/useSpecifications.api';
import * as queryUtils from './query-utils';
import type { MutationResult } from './query-utils';

type FetchFeaturesResult = Awaited<ReturnType<typeof specificationsApi.fetchFeatures>>;

type FetchFeatureResult = Awaited<ReturnType<typeof specificationsApi.fetchFeature>>;

type CreateFeatureResult = Awaited<ReturnType<typeof specificationsApi.createFeature>>;

type UpdateFeatureResult = Awaited<ReturnType<typeof specificationsApi.updateFeature>>;

type FetchFeatureActivitiesResult = Awaited<
  ReturnType<typeof specificationsApi.fetchFeatureActivities>
>;

type FetchFeatureStatsResult = Awaited<ReturnType<typeof specificationsApi.fetchFeatureStats>>;

const useFeatures = (
  filters: specificationsApi.FeatureFilters,
): queryUtils.QueryResult<FetchFeaturesResult> =>
  useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: async () => {
      const response = await specificationsApi.fetchFeatures(filters);
      return response;
    },
    queryKey: ['features', JSON.stringify(filters)],
  });

const useFeature = (id: string): queryUtils.QueryResult<FetchFeatureResult> =>
  useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const response = await specificationsApi.fetchFeature(id);
      return response;
    },
    queryKey: ['features', id],
  });

const useCreateFeature = (): queryUtils.MutationResult<
  CreateFeatureResult,
  specificationsApi.CreateFeatureData
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: specificationsApi.CreateFeatureData) => {
      const response = await specificationsApi.createFeature(data);
      return response;
    },
    onSuccess: async (_, variables) => {
      await queryUtils.invalidateQueries(queryClient, [['features'], ['featureStats']]);
      await queryClient.invalidateQueries({
        queryKey: ['specificationSummary', variables.projectId],
      });
    },
  });
};

const useUpdateFeature = (): MutationResult<
  UpdateFeatureResult,
  { id: string; data: specificationsApi.UpdateFeatureData }
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: specificationsApi.UpdateFeatureData }) => {
      const response = await specificationsApi.updateFeature(id, data);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await queryUtils.invalidateQueries(queryClient, [['features', id], ['features']]);
    },
  });
};

const useDeleteFeature = (): queryUtils.MutationResult<void, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await specificationsApi.deleteFeature(id);
    },
    onSuccess: async () => {
      await queryUtils.invalidateQueries(queryClient, [
        ['features'],
        ['featureStats'],
        ['specificationSummary'],
      ]);
    },
  });
};

const useFeatureActivities = (
  featureId: string,
): queryUtils.QueryResult<FetchFeatureActivitiesResult> =>
  useQuery({
    enabled: Boolean(featureId),
    queryFn: async () => {
      const response = await specificationsApi.fetchFeatureActivities(featureId);
      return response;
    },
    queryKey: ['featureActivities', featureId],
  });

const useFeatureStats = (
  projectId: string,
): queryUtils.QueryResult<FetchFeatureStatsResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await specificationsApi.fetchFeatureStats(projectId);
      return response;
    },
    queryKey: ['featureStats', projectId],
  });

export {
  useCreateFeature,
  useDeleteFeature,
  useFeature,
  useFeatureActivities,
  useFeatures,
  useFeatureStats,
  useUpdateFeature,
  type CreateFeatureResult,
  type FetchFeatureActivitiesResult,
  type FetchFeatureResult,
  type FetchFeaturesResult,
  type FetchFeatureStatsResult,
  type UpdateFeatureResult,
};
