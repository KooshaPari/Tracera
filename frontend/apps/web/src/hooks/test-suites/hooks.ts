import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
} from '@tanstack/react-query';

import type {
  TestSuite,
  TestSuiteActivity,
  TestSuiteStats,
  TestSuiteStatus,
  TestSuiteTestCase,
} from '@tracertm/types';

import * as api from './api';
import type { AddTestCaseToSuiteInput, CreateTestSuiteData, TestSuiteFilters } from './api';

interface FetchTestSuitesResponse {
  testSuites: TestSuite[];
  total: number;
}

function useTestSuitesHook(filters: TestSuiteFilters): UseQueryResult<FetchTestSuitesResponse> {
  return useQuery({
    enabled: filters.projectId.length > 0,
    queryFn: async () => await api.fetchTestSuites(filters),
    queryKey: ['testSuites', JSON.stringify(filters)],
  });
}

function useTestSuiteHook(id: string): UseQueryResult<TestSuite> {
  return useQuery({
    enabled: id.length > 0,
    queryFn: async () => await api.fetchTestSuite(id),
    queryKey: ['testSuites', id],
  });
}

function useCreateTestSuiteHook(): UseMutationResult<
  { id: string; suiteNumber: string },
  CreateTestSuiteData
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.createTestSuite,
    onSuccess: async (_, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testSuites'] }),
        queryClient.invalidateQueries({
          queryKey: ['testSuiteStats', variables.projectId],
        }),
      ]);
    },
  });
}

function useUpdateTestSuiteHook(): UseMutationResult<
  { id: string; version: number },
  { id: string; data: Partial<CreateTestSuiteData> }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (variables) => await api.updateTestSuite(variables.id, variables.data),
    onSuccess: async (_, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testSuites', variables.id] }),
        queryClient.invalidateQueries({ queryKey: ['testSuites'] }),
      ]);
    },
  });
}

function useTransitionTestSuiteStatusHook(): UseMutationResult<
  { id: string; status: string; version: number },
  { id: string; newStatus: TestSuiteStatus; reason?: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (variables) =>
      await api.transitionTestSuiteStatus(variables.id, variables.newStatus, variables.reason),
    onSuccess: async (_, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testSuites', variables.id] }),
        queryClient.invalidateQueries({ queryKey: ['testSuites'] }),
        queryClient.invalidateQueries({ queryKey: ['testSuiteStats'] }),
      ]);
    },
  });
}

function useDeleteTestSuiteHook(): UseMutationResult<void, unknown, string> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.deleteTestSuite,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testSuites'] }),
        queryClient.invalidateQueries({ queryKey: ['testSuiteStats'] }),
      ]);
    },
  });
}

function useAddTestCaseToSuiteHook(): UseMutationResult<TestSuiteTestCase, unknown, AddTestCaseToSuiteInput> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.addTestCaseToSuite,
    onSuccess: async (_, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['suiteTestCases', variables.suiteId] }),
        queryClient.invalidateQueries({ queryKey: ['testSuites', variables.suiteId] }),
      ]);
    },
  });
}

function useRemoveTestCaseFromSuiteHook(): UseMutationResult<
  void,
  unknown,
  { suiteId: string; testCaseId: string }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (variables) =>
      await api.removeTestCaseFromSuite(variables.suiteId, variables.testCaseId),
    onSuccess: async (_, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['suiteTestCases', variables.suiteId] }),
        queryClient.invalidateQueries({ queryKey: ['testSuites', variables.suiteId] }),
      ]);
    },
  });
}

function useSuiteTestCasesHook(suiteId: string): UseQueryResult<TestSuiteTestCase[]> {
  return useQuery({
    enabled: suiteId.length > 0,
    queryFn: async () => await api.fetchSuiteTestCases(suiteId),
    queryKey: ['suiteTestCases', suiteId],
  });
}

function useReorderSuiteTestCasesHook(): UseMutationResult<
  void,
  unknown,
  { suiteId: string; testCaseIds: string[] }
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (variables) =>
      await api.reorderSuiteTestCases(variables.suiteId, variables.testCaseIds),
    onSuccess: async (_, variables) => {
      await queryClient.invalidateQueries({ queryKey: ['suiteTestCases', variables.suiteId] });
    },
  });
}

function useTestSuiteActivitiesHook(
  suiteId: string,
  limit = 50,
): UseQueryResult<{ suiteId: string; activities: TestSuiteActivity[] }> {
  return useQuery({
    enabled: suiteId.length > 0,
    queryFn: async () => await api.fetchTestSuiteActivities(suiteId, limit),
    queryKey: ['testSuiteActivities', suiteId, limit],
  });
}

function useTestSuiteStatsHook(projectId: string): UseQueryResult<TestSuiteStats> {
  return useQuery({
    enabled: projectId.length > 0,
    queryFn: async () => await api.fetchTestSuiteStats(projectId),
    queryKey: ['testSuiteStats', projectId],
  });
}

export {
  useAddTestCaseToSuiteHook as useAddTestCaseToSuite,
  useCreateTestSuiteHook as useCreateTestSuite,
  useDeleteTestSuiteHook as useDeleteTestSuite,
  useReorderSuiteTestCasesHook as useReorderSuiteTestCases,
  useRemoveTestCaseFromSuiteHook as useRemoveTestCaseFromSuite,
  useSuiteTestCasesHook as useSuiteTestCases,
  useTestSuiteActivitiesHook as useTestSuiteActivities,
  useTestSuiteHook as useTestSuite,
  useTestSuiteStatsHook as useTestSuiteStats,
  useTestSuitesHook as useTestSuites,
  useTransitionTestSuiteStatusHook as useTransitionTestSuiteStatus,
  useUpdateTestSuiteHook as useUpdateTestSuite,
};
