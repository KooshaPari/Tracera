import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  createFeature,
  deleteFeature,
  fetchFeature,
  fetchFeatureActivities,
  fetchFeatures,
  fetchFeatureStats,
  updateFeature,
  type CreateFeatureData,
  type FeatureFilters,
  type UpdateFeatureData,
} from '@/hooks/useSpecifications.api';

import { invalidateQueries, type MutationResult, type QueryResult } from './query-utils';

type FetchFeaturesResult = Awaited<ReturnType<typeof fetchFeatures>>;

type FetchFeatureResult = Awaited<ReturnType<typeof fetchFeature>>;

type CreateFeatureResult = Awaited<ReturnType<typeof createFeature>>;

type UpdateFeatureResult = Awaited<ReturnType<typeof updateFeature>>;

type FetchFeatureActivitiesResult = Awaited<ReturnType<typeof fetchFeatureActivities>>;

type FetchFeatureStatsResult = Awaited<ReturnType<typeof fetchFeatureStats>>;

const useFeatures = (filters: FeatureFilters): QueryResult<FetchFeaturesResult> =>
  useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: async () => {
      const response = await fetchFeatures(filters);
      return response;
    },
    queryKey: ['features', JSON.stringify(filters)],
  });

const useFeature = (id: string): QueryResult<FetchFeatureResult> =>
  useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const response = await fetchFeature(id);
      return response;
    },
    queryKey: ['features', id],
  });

const useCreateFeature = (): MutationResult<CreateFeatureResult, CreateFeatureData> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateFeatureData) => {
      const response = await createFeature(data);
      return response;
    },
    onSuccess: async (_, variables) => {
      await invalidateQueries(queryClient, [['features'], ['featureStats']]);
      await queryClient.invalidateQueries({
        queryKey: ['specificationSummary', variables.projectId],
      });
    },
  });
};

const useUpdateFeature = (): MutationResult<
  UpdateFeatureResult,
  { id: string; data: UpdateFeatureData }
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateFeatureData }) => {
      const response = await updateFeature(id, data);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await invalidateQueries(queryClient, [['features', id], ['features']]);
    },
  });
};

const useDeleteFeature = (): MutationResult<void, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await deleteFeature(id);
    },
    onSuccess: async () => {
      await invalidateQueries(queryClient, [
        ['features'],
        ['featureStats'],
        ['specificationSummary'],
      ]);
    },
  });
};

const useFeatureActivities = (featureId: string): QueryResult<FetchFeatureActivitiesResult> =>
  useQuery({
    enabled: Boolean(featureId),
    queryFn: async () => {
      const response = await fetchFeatureActivities(featureId);
      return response;
    },
    queryKey: ['featureActivities', featureId],
  });

const useFeatureStats = (projectId: string): QueryResult<FetchFeatureStatsResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await fetchFeatureStats(projectId);
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
