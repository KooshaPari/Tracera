import type { UseMutationResult, UseQueryResult } from '@tanstack/react-query';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { TestResult, TestRun, TestRunActivity, TestRunStats } from '@tracertm/types';

import type { CreateTestRunData, SubmitTestResultData, TestRunFilters } from './test-run-types';

import {
  cancelTestRun,
  completeTestRun,
  createTestRun,
  deleteTestRun,
  fetchTestRun,
  fetchTestRunActivities,
  fetchTestRunResults,
  fetchTestRunStats,
  fetchTestRuns,
  startTestRun,
  submitBulkTestResults,
  submitTestResult,
  type BulkSubmitResponse,
  type TestRunsResponse,
} from './test-run-api';

function useTestRuns(filters: TestRunFilters): UseQueryResult<TestRunsResponse, Error> {
  return useQuery({
    enabled: filters.projectId.length > 0,
    queryFn: async () => await fetchTestRuns(filters),
    queryKey: ['testRuns', JSON.stringify(filters)],
  });
}

function useTestRun(id: string): UseQueryResult<TestRun, Error> {
  return useQuery({
    enabled: id.length > 0,
    queryFn: async () => await fetchTestRun(id),
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
    mutationFn: async (data: CreateTestRunData) => await createTestRun(data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['testRuns'] });
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
    mutationFn: async (vars: { id: string; data: Partial<CreateTestRunData> }) =>
      await updateTestRun(vars.id, vars.data),
    onSuccess: (_, vars) => {
      void queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      void queryClient.invalidateQueries({ queryKey: ['testRuns', vars.id] });
    },
  });
}

function useStartTestRun(): UseMutationResult<
  { id: string; status: string; startedAt?: string },
  Error,
  { id: string; executedBy?: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; executedBy?: string }) =>
      await startTestRun(vars.id, vars.executedBy),
    onSuccess: (_, vars) => {
      void queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      void queryClient.invalidateQueries({ queryKey: ['testRuns', vars.id] });
      void queryClient.invalidateQueries({ queryKey: ['testRunActivities', vars.id] });
    },
  });
}

function useCompleteTestRun(): UseMutationResult<
  { id: string; status: string; passRate?: number; completedAt?: string },
  Error,
  { id: string; failureSummary?: string; notes?: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; failureSummary?: string; notes?: string }) =>
      await completeTestRun(vars.id, vars.failureSummary, vars.notes),
    onSuccess: (_, vars) => {
      void queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      void queryClient.invalidateQueries({ queryKey: ['testRuns', vars.id] });
      void queryClient.invalidateQueries({ queryKey: ['testRunActivities', vars.id] });
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
    mutationFn: async (vars: { id: string; reason?: string }) =>
      await cancelTestRun(vars.id, vars.reason),
    onSuccess: (_, vars) => {
      void queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      void queryClient.invalidateQueries({ queryKey: ['testRuns', vars.id] });
      void queryClient.invalidateQueries({ queryKey: ['testRunActivities', vars.id] });
    },
  });
}

function useDeleteTestRun(): UseMutationResult<void, Error, string> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => await deleteTestRun(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['testRuns'] });
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
    mutationFn: async (vars: { runId: string; data: SubmitTestResultData }) =>
      await submitTestResult(vars.runId, vars.data),
    onSuccess: (_, vars) => {
      void queryClient.invalidateQueries({ queryKey: ['testRunResults', vars.runId] });
      void queryClient.invalidateQueries({ queryKey: ['testRuns', vars.runId] });
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
    mutationFn: async (vars: { runId: string; results: SubmitTestResultData[] }) =>
      await submitBulkTestResults(vars.runId, vars.results),
    onSuccess: (_, vars) => {
      void queryClient.invalidateQueries({ queryKey: ['testRunResults', vars.runId] });
      void queryClient.invalidateQueries({ queryKey: ['testRuns', vars.runId] });
    },
  });
}

function useTestRunResults(runId: string): UseQueryResult<TestResult[], Error> {
  return useQuery({
    enabled: runId.length > 0,
    queryFn: async () => await fetchTestRunResults(runId),
    queryKey: ['testRunResults', runId],
  });
}

function useTestRunActivities(
  runId: string,
  limit: number = 50,
): UseQueryResult<{ runId: string; activities: TestRunActivity[] }, Error> {
  return useQuery({
    enabled: runId.length > 0,
    queryFn: async () => await fetchTestRunActivities(runId, limit),
    queryKey: ['testRunActivities', runId, limit],
  });
}

function useTestRunStats(projectId: string): UseQueryResult<TestRunStats, Error> {
  return useQuery({
    enabled: projectId.length > 0,
    queryFn: async () => await fetchTestRunStats(projectId),
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
