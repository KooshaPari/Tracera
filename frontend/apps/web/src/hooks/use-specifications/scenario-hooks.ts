import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import * as specificationsApi from '@/hooks/useSpecifications.api';
import * as queryUtils from './query-utils';
import type { MutationResult } from './query-utils';

type FetchScenarioActivitiesResult = Awaited<
  ReturnType<typeof specificationsApi.fetchScenarioActivities>
>;

type FetchProjectScenariosResult = Awaited<ReturnType<typeof specificationsApi.fetchProjectScenarios>>;

type FetchProjectScenarioActivitiesResult = Awaited<
  ReturnType<typeof specificationsApi.fetchProjectScenarioActivities>
>;

type FetchScenariosResult = Awaited<ReturnType<typeof specificationsApi.fetchScenarios>>;

type FetchScenarioResult = Awaited<ReturnType<typeof specificationsApi.fetchScenario>>;

type CreateScenarioResult = Awaited<ReturnType<typeof specificationsApi.createScenario>>;

type UpdateScenarioResult = Awaited<ReturnType<typeof specificationsApi.updateScenario>>;

type RunScenarioResult = Awaited<ReturnType<typeof specificationsApi.runScenario>>;

const useScenarioActivities = (
  scenarioId: string,
  options?: { limit?: number; offset?: number },
): queryUtils.QueryResult<FetchScenarioActivitiesResult> =>
  useQuery({
    enabled: Boolean(scenarioId),
    queryFn: async () => {
      const response = await specificationsApi.fetchScenarioActivities(scenarioId, options);
      return response;
    },
    queryKey: ['scenarioActivities', scenarioId, JSON.stringify(options)],
  });

const useProjectScenarios = (
  projectId: string,
  status?: string,
): queryUtils.QueryResult<FetchProjectScenariosResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await specificationsApi.fetchProjectScenarios(projectId, status);
      return response;
    },
    queryKey: ['projectScenarios', projectId, status],
  });

const useProjectScenarioActivities = (
  projectId: string,
  options?: {
    limit?: number;
    offset?: number;
    eventType?: string;
    since?: string;
    until?: string;
  },
): queryUtils.QueryResult<FetchProjectScenarioActivitiesResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await specificationsApi.fetchProjectScenarioActivities(projectId, options);
      return response;
    },
    queryKey: ['projectScenarioActivities', projectId, JSON.stringify(options)],
  });

const useScenarios = (featureId: string): queryUtils.QueryResult<FetchScenariosResult> =>
  useQuery({
    enabled: Boolean(featureId),
    queryFn: async () => {
      const response = await specificationsApi.fetchScenarios(featureId);
      return response;
    },
    queryKey: ['scenarios', featureId],
  });

const useScenario = (id: string): queryUtils.QueryResult<FetchScenarioResult> =>
  useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const response = await specificationsApi.fetchScenario(id);
      return response;
    },
    queryKey: ['scenarios', id],
  });

const useCreateScenario = (): queryUtils.MutationResult<
  CreateScenarioResult,
  specificationsApi.CreateScenarioData
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: specificationsApi.CreateScenarioData) => {
      const response = await specificationsApi.createScenario(data);
      return response;
    },
    onSuccess: async () => {
      await queryUtils.invalidateQueries(queryClient, [
        ['scenarios'],
        ['projectScenarios'],
        ['featureStats'],
        ['specificationSummary'],
      ]);
    },
  });
};

const useUpdateScenario = (): MutationResult<
  UpdateScenarioResult,
  { id: string; data: specificationsApi.UpdateScenarioData }
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: specificationsApi.UpdateScenarioData }) => {
      const response = await specificationsApi.updateScenario(id, data);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await queryUtils.invalidateQueries(queryClient, [['scenarios', id], ['scenarios'], ['featureStats']]);
    },
  });
};

const useDeleteScenario = (): queryUtils.MutationResult<void, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await specificationsApi.deleteScenario(id);
    },
    onSuccess: async () => {
      await queryUtils.invalidateQueries(queryClient, [
        ['scenarios'],
        ['projectScenarios'],
        ['featureStats'],
        ['specificationSummary'],
      ]);
    },
  });
};

const useRunScenario = (): queryUtils.MutationResult<RunScenarioResult, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await specificationsApi.runScenario(id);
      return response;
    },
    onSuccess: async (_, id) => {
      await queryUtils.invalidateQueries(queryClient, [['scenarios', id], ['scenarios'], ['featureStats']]);
      await queryClient.invalidateQueries({ queryKey: ['specificationSummary'] });
    },
  });
};

export {
  useCreateScenario,
  useDeleteScenario,
  useProjectScenarioActivities,
  useProjectScenarios,
  useRunScenario,
  useScenario,
  useScenarioActivities,
  useScenarios,
  useUpdateScenario,
  type CreateScenarioResult,
  type FetchProjectScenarioActivitiesResult,
  type FetchProjectScenariosResult,
  type FetchScenarioActivitiesResult,
  type FetchScenarioResult,
  type FetchScenariosResult,
  type RunScenarioResult,
  type UpdateScenarioResult,
};
