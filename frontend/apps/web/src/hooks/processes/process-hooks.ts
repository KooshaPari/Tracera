import type { UseMutationResult, UseQueryResult } from '@tanstack/react-query';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { ExecutionStatus, Process, ProcessExecution } from '@tracertm/types';

import type { CreateExecutionData, CreateProcessData, ProcessFilters } from './process-types';

import { processApi } from './process-api';

type ProcessesResponse = Awaited<ReturnType<typeof processApi.fetchProcesses>>;
type ExecutionsResponse = Awaited<ReturnType<typeof processApi.fetchExecutions>>;

function useProcesses(filters: ProcessFilters): UseQueryResult<ProcessesResponse> {
  return useQuery({
    enabled: filters.projectId.length > 0,
    queryFn: async () => {
      const result = await processApi.fetchProcesses(filters);
      return result;
    },
    queryKey: ['processes', JSON.stringify(filters)],
  });
}

function useProcess(id: string): UseQueryResult<Process> {
  return useQuery({
    enabled: id.length > 0,
    queryFn: async () => {
      const result = await processApi.fetchProcess(id);
      return result;
    },
    queryKey: ['processes', id],
  });
}

function useCreateProcess(): UseMutationResult<
  { id: string; processNumber: string },
  unknown,
  CreateProcessData
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateProcessData) => {
      const result = await processApi.createProcess(data);
      return result;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['processes'] });
    },
  });
}

function useUpdateProcess(): UseMutationResult<
  { id: string; version: number },
  unknown,
  { id: string; data: Partial<Omit<CreateProcessData, 'projectId'>> }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: {
      id: string;
      data: Partial<Omit<CreateProcessData, 'projectId'>>;
    }) => {
      const result = await processApi.updateProcess(vars.id, vars.data);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['processes'] });
      await queryClient.invalidateQueries({ queryKey: ['processes', vars.id] });
    },
  });
}

function useCreateProcessVersion(): UseMutationResult<
  { id: string; processNumber: string; versionNumber: number; parentVersionId: string },
  unknown,
  { processId: string; versionNotes?: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { processId: string; versionNotes?: string }) => {
      const result = await processApi.createProcessVersion(vars.processId, vars.versionNotes);
      return result;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['processes'] });
    },
  });
}

function useActivateProcess(): UseMutationResult<
  { id: string; status: string; isActiveVersion: boolean },
  unknown,
  string
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (processId: string) => {
      const result = await processApi.activateProcess(processId);
      return result;
    },
    onSuccess: async (_, processId) => {
      await queryClient.invalidateQueries({ queryKey: ['processes', processId] });
      await queryClient.invalidateQueries({ queryKey: ['processes'] });
    },
  });
}

function useDeprecateProcess(): UseMutationResult<
  { id: string; status: string },
  unknown,
  { processId: string; deprecationReason?: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { processId: string; deprecationReason?: string }) => {
      const result = await processApi.deprecateProcess(vars.processId, vars.deprecationReason);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['processes', vars.processId] });
      await queryClient.invalidateQueries({ queryKey: ['processes'] });
    },
  });
}

function useDeleteProcess(): UseMutationResult<void, unknown, string> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await processApi.deleteProcess(id);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['processes'] });
    },
  });
}

function useProcessStats(
  projectId: string,
): UseQueryResult<Awaited<ReturnType<typeof processApi.fetchProcessStats>>> {
  return useQuery({
    enabled: projectId.length > 0,
    queryFn: async () => {
      const result = await processApi.fetchProcessStats(projectId);
      return result;
    },
    queryKey: ['processStats', projectId],
  });
}

function useProcessExecutions(
  processId: string,
  status: ExecutionStatus | undefined,
  limit = 50,
): UseQueryResult<ExecutionsResponse> {
  return useQuery({
    enabled: processId.length > 0,
    queryFn: async () => {
      const result = await processApi.fetchExecutions({ limit, processId, status });
      return result;
    },
    queryKey: ['processExecutions', processId, status, limit],
  });
}

function useExecution(executionId: string): UseQueryResult<ProcessExecution> {
  return useQuery({
    enabled: executionId.length > 0,
    queryFn: async () => {
      const result = await processApi.fetchExecution(executionId);
      return result;
    },
    queryKey: ['executions', executionId],
  });
}

function useCreateExecution(): UseMutationResult<
  { id: string; executionNumber: string },
  unknown,
  CreateExecutionData
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: CreateExecutionData) => {
      const result = await processApi.createExecution(vars);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['processExecutions', vars.processId] });
    },
  });
}

function useStartExecution(): UseMutationResult<{ id: string; status: string }, unknown, string> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (executionId: string) => {
      const result = await processApi.startExecution(executionId);
      return result;
    },
    onSuccess: async (_, executionId) => {
      await queryClient.invalidateQueries({ queryKey: ['executions', executionId] });
    },
  });
}

function useAdvanceExecution(): UseMutationResult<
  { id: string; currentStageId: string; completedStages: string[] },
  unknown,
  { executionId: string; stageId: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { executionId: string; stageId: string }) => {
      const result = await processApi.advanceExecution(vars.executionId, vars.stageId);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['executions', vars.executionId] });
    },
  });
}

function useCompleteExecution(): UseMutationResult<
  { id: string; status: string },
  unknown,
  { executionId: string; resultSummary?: string | undefined; outputItemIds?: string[] | undefined }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: {
      executionId: string;
      resultSummary?: string | undefined;
      outputItemIds?: string[] | undefined;
    }) => {
      const result = await processApi.completeExecution(
        vars.executionId,
        vars.resultSummary,
        vars.outputItemIds,
      );
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['executions', vars.executionId] });
    },
  });
}

export {
  useActivateProcess,
  useAdvanceExecution,
  useCompleteExecution,
  useCreateExecution,
  useCreateProcess,
  useCreateProcessVersion,
  useDeleteProcess,
  useDeprecateProcess,
  useExecution,
  useProcess,
  useProcessExecutions,
  useProcesses,
  useProcessStats,
  useStartExecution,
  useUpdateProcess,
};
