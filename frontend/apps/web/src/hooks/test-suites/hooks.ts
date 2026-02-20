import type { UseMutationResult, UseQueryResult } from '@tanstack/react-query';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  TestSuite,
  TestSuiteActivity,
  TestSuiteStats,
  TestSuiteStatus,
  TestSuiteTestCase,
} from '@tracertm/types';

import type { AddTestCaseToSuiteInput, CreateTestSuiteData, TestSuiteFilters } from './api';

import { testSuitesApi } from './api';

interface FetchTestSuitesResponse {
  testSuites: TestSuite[];
  total: number;
}

function useTestSuitesHook(filters: TestSuiteFilters): UseQueryResult<FetchTestSuitesResponse> {
  return useQuery({
    enabled: filters.projectId.length > 0,
    queryFn: async () => {
      const result = await testSuitesApi.fetchTestSuites(filters);
      return result;
    },
    queryKey: ['testSuites', JSON.stringify(filters)],
  });
}

function useTestSuiteHook(id: string): UseQueryResult<TestSuite> {
  return useQuery({
    enabled: id.length > 0,
    queryFn: async () => {
      const result = await testSuitesApi.fetchTestSuite(id);
      return result;
    },
    queryKey: ['testSuites', id],
  });
}

function useCreateTestSuiteHook(): UseMutationResult<
  { id: string; suiteNumber: string },
  Error,
  CreateTestSuiteData
> {
  const queryClient = useQueryClient();
  return useMutation<{ id: string; suiteNumber: string }, Error, CreateTestSuiteData>({
    mutationFn: testSuitesApi.createTestSuite,
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
  Error,
  { id: string; data: Partial<CreateTestSuiteData> }
> {
  const queryClient = useQueryClient();
  return useMutation<
    { id: string; version: number },
    Error,
    { id: string; data: Partial<CreateTestSuiteData> }
  >({
    mutationFn: async (variables) => {
      const result = await testSuitesApi.updateTestSuite(variables.id, variables.data);
      return result;
    },
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
  Error,
  { id: string; newStatus: TestSuiteStatus; reason?: string }
> {
  const queryClient = useQueryClient();
  return useMutation<
    { id: string; status: string; version: number },
    Error,
    { id: string; newStatus: TestSuiteStatus; reason?: string }
  >({
    mutationFn: async (variables) => {
      const result = await testSuitesApi.transitionTestSuiteStatus(
        variables.id,
        variables.newStatus,
        variables.reason,
      );
      return result;
    },
    onSuccess: async (_, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testSuites', variables.id] }),
        queryClient.invalidateQueries({ queryKey: ['testSuites'] }),
        queryClient.invalidateQueries({ queryKey: ['testSuiteStats'] }),
      ]);
    },
  });
}

function useDeleteTestSuiteHook(): UseMutationResult<void, Error, string> {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: testSuitesApi.deleteTestSuite,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testSuites'] }),
        queryClient.invalidateQueries({ queryKey: ['testSuiteStats'] }),
      ]);
    },
  });
}

function useAddTestCaseToSuiteHook(): UseMutationResult<
  TestSuiteTestCase,
  Error,
  AddTestCaseToSuiteInput
> {
  const queryClient = useQueryClient();
  return useMutation<TestSuiteTestCase, Error, AddTestCaseToSuiteInput>({
    mutationFn: testSuitesApi.addTestCaseToSuite,
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
  Error,
  { suiteId: string; testCaseId: string }
> {
  const queryClient = useQueryClient();
  return useMutation<void, Error, { suiteId: string; testCaseId: string }>({
    mutationFn: async (variables) => {
      await testSuitesApi.removeTestCaseFromSuite(variables.suiteId, variables.testCaseId);
    },
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
    queryFn: async () => {
      const result = await testSuitesApi.fetchSuiteTestCases(suiteId);
      return result;
    },
    queryKey: ['suiteTestCases', suiteId],
  });
}

function useReorderSuiteTestCasesHook(): UseMutationResult<
  void,
  Error,
  { suiteId: string; testCaseIds: string[] }
> {
  const queryClient = useQueryClient();
  return useMutation<void, Error, { suiteId: string; testCaseIds: string[] }>({
    mutationFn: async (variables) => {
      await testSuitesApi.reorderSuiteTestCases(variables.suiteId, variables.testCaseIds);
    },
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
    queryFn: async () => {
      const result = await testSuitesApi.fetchTestSuiteActivities(suiteId, limit);
      return result;
    },
    queryKey: ['testSuiteActivities', suiteId, limit],
  });
}

function useTestSuiteStatsHook(projectId: string): UseQueryResult<TestSuiteStats> {
  return useQuery({
    enabled: projectId.length > 0,
    queryFn: async () => {
      const result = await testSuitesApi.fetchTestSuiteStats(projectId);
      return result;
    },
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
