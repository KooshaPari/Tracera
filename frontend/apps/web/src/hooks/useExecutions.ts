// React hooks for execution management

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  ExecutionComplete,
  ExecutionCreate,
  ExecutionEnvironmentConfigUpdate,
} from '../api/executions';

import executionsApi from '../api/executions';

export function useExecutions(
  projectId: string,
  options?: {
    status?: string;
    execution_type?: string;
    limit?: number;
    offset?: number;
  },
) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => executionsApi.list(projectId, options),
    queryKey: ['executions', projectId, options],
  });
}

export function useExecution(projectId: string, executionId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(executionId),
    queryFn: async () => executionsApi.get(projectId, executionId),
    queryKey: ['execution', projectId, executionId],
  });
}

export function useExecutionArtifacts(
  projectId: string,
  executionId: string,
  artifactType?: string,
) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(executionId),
    queryFn: async () => executionsApi.listArtifacts(projectId, executionId, artifactType),
    queryKey: ['execution-artifacts', projectId, executionId, artifactType],
  });
}

export function useExecutionConfig(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => executionsApi.getConfig(projectId),
    queryKey: ['execution-config', projectId],
  });
}

export function useCreateExecution(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: ExecutionCreate) => executionsApi.create(projectId, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['executions', projectId],
      });
    },
  });
}

export function useStartExecution(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (executionId: string) => executionsApi.start(projectId, executionId),
    onSuccess: async (_data, executionId) => {
      await queryClient.invalidateQueries({
        queryKey: ['execution', projectId, executionId],
      });
      await queryClient.invalidateQueries({
        queryKey: ['executions', projectId],
      });
    },
  });
}

export function useCompleteExecution(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ executionId, data }: { executionId: string; data: ExecutionComplete }) =>
      executionsApi.complete(projectId, executionId, data),
    onSuccess: async (_data, { executionId }) => {
      await queryClient.invalidateQueries({
        queryKey: ['execution', projectId, executionId],
      });
      await queryClient.invalidateQueries({
        queryKey: ['executions', projectId],
      });
      await queryClient.invalidateQueries({
        queryKey: ['execution-artifacts', projectId, executionId],
      });
    },
  });
}

export function useUpdateExecutionConfig(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: ExecutionEnvironmentConfigUpdate) =>
      executionsApi.updateConfig(projectId, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['execution-config', projectId],
      });
    },
  });
}
