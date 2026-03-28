import type { UseMutationResult, UseQueryResult } from '@tanstack/react-query';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { TestResult, TestRunActivity, TestRunStats } from '@tracertm/types';

import type { CreateTestRunData, SubmitTestResultData, TestRunFilters } from './test-run-types';

import { testRunApi } from './test-run-api';

type TestRunsResponse = Awaited<ReturnType<typeof testRunApi.fetchTestRuns>>;
type BulkSubmitResponse = Awaited<ReturnType<typeof testRunApi.submitBulkTestResults>>;
type TestRun = Awaited<ReturnType<typeof testRunApi.fetchTestRun>>;

function useTestRuns(filters: TestRunFilters): UseQueryResult<TestRunsResponse> {
  return useQuery({
    enabled: filters.projectId.length > 0,
    queryFn: async () => {
      const result = await testRunApi.fetchTestRuns(filters);
      return result;
    },
    queryKey: ['testRuns', JSON.stringify(filters)],
  });
}

function useTestRun(id: string): UseQueryResult<TestRun> {
  return useQuery({
    enabled: id.length > 0,
    queryFn: async () => {
      const result = await testRunApi.fetchTestRun(id);
      return result;
    },
    queryKey: ['testRuns', id],
  });
}

function useCreateTestRun(): UseMutationResult<
  { id: string; runNumber: string },
  Error,
  CreateTestRunData
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateTestRunData) => {
      const result = await testRunApi.createTestRun(data);
      return result;
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['testRuns'] });
    },
  });
}

function useUpdateTestRun(): UseMutationResult<
  { id: string; version: number },
  Error,
  { id: string; data: Partial<CreateTestRunData> }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; data: Partial<CreateTestRunData> }) => {
      const result = await testRunApi.updateTestRun(vars.id, vars.data);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      await queryClient.invalidateQueries({ queryKey: ['testRuns', vars.id] });
    },
  });
}

function useStartTestRun(): UseMutationResult<
  { id: string; status: string; startedAt?: string | undefined },
  Error,
  { id: string; executedBy?: string },
  unknown
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; executedBy?: string }) => {
      const result = await testRunApi.startTestRun(vars.id, vars.executedBy);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      await queryClient.invalidateQueries({ queryKey: ['testRuns', vars.id] });
      await queryClient.invalidateQueries({ queryKey: ['testRunActivities', vars.id] });
    },
  });
}

function useCompleteTestRun(): UseMutationResult<
  { id: string; status: string; passRate?: number | undefined; completedAt?: string | undefined },
  Error,
  { id: string; failureSummary?: string; notes?: string },
  unknown
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; failureSummary?: string; notes?: string }) => {
      const result = await testRunApi.completeTestRun(vars.id, vars.failureSummary, vars.notes);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      await queryClient.invalidateQueries({ queryKey: ['testRuns', vars.id] });
      await queryClient.invalidateQueries({ queryKey: ['testRunActivities', vars.id] });
    },
  });
}

function useCancelTestRun(): UseMutationResult<
  { id: string; status: string },
  Error,
  { id: string; reason?: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; reason?: string }) => {
      const result = await testRunApi.cancelTestRun(vars.id, vars.reason);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      await queryClient.invalidateQueries({ queryKey: ['testRuns', vars.id] });
      await queryClient.invalidateQueries({ queryKey: ['testRunActivities', vars.id] });
    },
  });
}

function useDeleteTestRun(): UseMutationResult<void, Error, string> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await testRunApi.deleteTestRun(id);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['testRuns'] });
    },
  });
}

function useSubmitTestResult(): UseMutationResult<
  TestResult,
  Error,
  { runId: string; data: SubmitTestResultData }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { runId: string; data: SubmitTestResultData }) => {
      const result = await testRunApi.submitTestResult(vars.runId, vars.data);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['testRunResults', vars.runId] });
      await queryClient.invalidateQueries({ queryKey: ['testRuns', vars.runId] });
    },
  });
}

function useSubmitBulkTestResults(): UseMutationResult<
  BulkSubmitResponse,
  Error,
  { runId: string; results: SubmitTestResultData[] }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { runId: string; results: SubmitTestResultData[] }) => {
      const result = await testRunApi.submitBulkTestResults(vars.runId, vars.results);
      return result;
    },
    onSuccess: async (_, vars) => {
      await queryClient.invalidateQueries({ queryKey: ['testRunResults', vars.runId] });
      await queryClient.invalidateQueries({ queryKey: ['testRuns', vars.runId] });
    },
  });
}

function useTestRunResults(runId: string): UseQueryResult<TestResult[]> {
  return useQuery({
    enabled: runId.length > 0,
    queryFn: async () => {
      const result = await testRunApi.fetchTestRunResults(runId);
      return result;
    },
    queryKey: ['testRunResults', runId],
  });
}

function useTestRunActivities(
  runId: string,
  limit = 50,
): UseQueryResult<{ runId: string; activities: TestRunActivity[] }> {
  return useQuery({
    enabled: runId.length > 0,
    queryFn: async () => {
      const result = await testRunApi.fetchTestRunActivities(runId, limit);
      return result;
    },
    queryKey: ['testRunActivities', runId, limit],
  });
}

function useTestRunStats(projectId: string): UseQueryResult<TestRunStats> {
  return useQuery({
    enabled: projectId.length > 0,
    queryFn: async () => {
      const result = await testRunApi.fetchTestRunStats(projectId);
      return result;
    },
    queryKey: ['testRunStats', projectId],
  });
}

export {
  useCancelTestRun,
  useCompleteTestRun,
  useCreateTestRun,
  useDeleteTestRun,
  useStartTestRun,
  useSubmitBulkTestResults,
  useSubmitTestResult,
  useTestRun,
  useTestRunActivities,
  useTestRunResults,
  useTestRuns,
  useTestRunStats,
  useUpdateTestRun,
};
