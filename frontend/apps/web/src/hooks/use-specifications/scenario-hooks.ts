import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { CreateScenarioData, UpdateScenarioData } from '@/hooks/useSpecifications.api';

import {
  createScenario,
  deleteScenario,
  fetchProjectScenarioActivities,
  fetchProjectScenarios,
  fetchScenario,
  fetchScenarioActivities,
  fetchScenarios,
  runScenario,
  updateScenario,
} from '@/hooks/useSpecifications.api';

import type { MutationResult, QueryResult } from './query-utils';

import { invalidateQueries } from './query-utils';

type FetchScenarioActivitiesResult = Awaited<ReturnType<typeof fetchScenarioActivities>>;

type FetchProjectScenariosResult = Awaited<ReturnType<typeof fetchProjectScenarios>>;

type FetchProjectScenarioActivitiesResult = Awaited<
  ReturnType<typeof fetchProjectScenarioActivities>
>;

type FetchScenariosResult = Awaited<ReturnType<typeof fetchScenarios>>;

type FetchScenarioResult = Awaited<ReturnType<typeof fetchScenario>>;

type CreateScenarioResult = Awaited<ReturnType<typeof createScenario>>;

type UpdateScenarioResult = Awaited<ReturnType<typeof updateScenario>>;

type RunScenarioResult = Awaited<ReturnType<typeof runScenario>>;

const useScenarioActivities = (
  scenarioId: string,
  options?: { limit?: number; offset?: number },
): QueryResult<FetchScenarioActivitiesResult> =>
  useQuery({
    enabled: Boolean(scenarioId),
    queryFn: async () => {
      const response = await fetchScenarioActivities(scenarioId, options);
      return response;
    },
    queryKey: ['scenarioActivities', scenarioId, JSON.stringify(options)],
  });

const useProjectScenarios = (
  projectId: string,
  status?: string,
): QueryResult<FetchProjectScenariosResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await fetchProjectScenarios(projectId, status);
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
): QueryResult<FetchProjectScenarioActivitiesResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await fetchProjectScenarioActivities(projectId, options);
      return response;
    },
    queryKey: ['projectScenarioActivities', projectId, JSON.stringify(options)],
  });

const useScenarios = (featureId: string): QueryResult<FetchScenariosResult> =>
  useQuery({
    enabled: Boolean(featureId),
    queryFn: async () => {
      const response = await fetchScenarios(featureId);
      return response;
    },
    queryKey: ['scenarios', featureId],
  });

const useScenario = (id: string): QueryResult<FetchScenarioResult> =>
  useQuery({
    enabled: Boolean(id),
    queryFn: async () => {
      const response = await fetchScenario(id);
      return response;
    },
    queryKey: ['scenarios', id],
  });

const useCreateScenario = (): MutationResult<CreateScenarioResult, CreateScenarioData> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateScenarioData) => {
      const response = await createScenario(data);
      return response;
    },
    onSuccess: async () => {
      await invalidateQueries(queryClient, [
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
  { id: string; data: UpdateScenarioData }
> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateScenarioData }) => {
      const response = await updateScenario(id, data);
      return response;
    },
    onSuccess: async (_, { id }) => {
      await invalidateQueries(queryClient, [['scenarios', id], ['scenarios'], ['featureStats']]);
    },
  });
};

const useDeleteScenario = (): MutationResult<void, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await deleteScenario(id);
    },
    onSuccess: async () => {
      await invalidateQueries(queryClient, [
        ['scenarios'],
        ['projectScenarios'],
        ['featureStats'],
        ['specificationSummary'],
      ]);
    },
  });
};

const useRunScenario = (): MutationResult<RunScenarioResult, string> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await runScenario(id);
      return response;
    },
    onSuccess: async (_, id) => {
      await invalidateQueries(queryClient, [['scenarios', id], ['scenarios'], ['featureStats']]);
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
