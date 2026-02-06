import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { TestCase, TestCaseStats, TestCaseStatus } from '@tracertm/types';

import testCasesApi, {
  type CreateTestCaseData,
  type TestCaseActivitiesResult,
  type TestCaseFilters,
  type TestCaseListResult,
} from './testCasesApi';

interface UseTestCaseStatusInput {
  id: string;
  newStatus: TestCaseStatus;
  reason?: string;
}

interface UseSubmitTestCaseForReviewInput {
  id: string;
  reviewer: string;
  notes?: string;
}

interface UseApproveTestCaseInput {
  id: string;
  notes?: string;
}

interface UseDeprecateTestCaseInput {
  id: string;
  reason: string;
  replacementTestCaseId?: string;
}

interface UseUpdateTestCaseInput {
  id: string;
  data: Partial<CreateTestCaseData>;
}

const DEFAULT_ACTIVITY_LIMIT = 50;

function useTestCases(
  filters: TestCaseFilters,
): ReturnType<typeof useQuery<TestCaseListResult, Error>> {
  const hasProjectId = filters.projectId.length > 0;
  return useQuery<TestCaseListResult, Error>({
    enabled: hasProjectId,
    queryFn: () => testCasesApi.fetchTestCases(filters),
    queryKey: ['testCases', JSON.stringify(filters)],
  });
}

function useTestCase(id: string): ReturnType<typeof useQuery<TestCase, Error>> {
  const hasId = id.length > 0;
  return useQuery<TestCase, Error>({
    enabled: hasId,
    queryFn: () => testCasesApi.fetchTestCase(id),
    queryKey: ['testCases', id],
  });
}

function useCreateTestCase(): ReturnType<typeof useMutation> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateTestCaseData) => testCasesApi.createTestCase(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['testCases'] });
    },
  });
}

function useUpdateTestCase(): ReturnType<typeof useMutation> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: UseUpdateTestCaseInput) => testCasesApi.updateTestCase(id, data),
    onSuccess: async (_, { id }) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testCases'] }),
        queryClient.invalidateQueries({ queryKey: ['testCases', id] }),
      ]);
    },
  });
}

function useTransitionTestCaseStatus(): ReturnType<typeof useMutation> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, newStatus, reason }: UseTestCaseStatusInput) =>
      testCasesApi.transitionTestCaseStatus(id, newStatus, reason),
    onSuccess: async (_, { id }) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testCases'] }),
        queryClient.invalidateQueries({ queryKey: ['testCases', id] }),
      ]);
    },
  });
}

function useSubmitTestCaseForReview(): ReturnType<typeof useMutation> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reviewer, notes }: UseSubmitTestCaseForReviewInput) =>
      testCasesApi.submitTestCaseForReview(id, reviewer, notes),
    onSuccess: async (_, { id }) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testCases'] }),
        queryClient.invalidateQueries({ queryKey: ['testCases', id] }),
      ]);
    },
  });
}

function useApproveTestCase(): ReturnType<typeof useMutation> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, notes }: UseApproveTestCaseInput) => testCasesApi.approveTestCase(id, notes),
    onSuccess: async (_, { id }) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testCases'] }),
        queryClient.invalidateQueries({ queryKey: ['testCases', id] }),
      ]);
    },
  });
}

function useDeprecateTestCase(): ReturnType<typeof useMutation> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason, replacementTestCaseId }: UseDeprecateTestCaseInput) =>
      testCasesApi.deprecateTestCase(id, reason, replacementTestCaseId),
    onSuccess: async (_, { id }) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['testCases'] }),
        queryClient.invalidateQueries({ queryKey: ['testCases', id] }),
      ]);
    },
  });
}

function useDeleteTestCase(): ReturnType<typeof useMutation> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => testCasesApi.deleteTestCase(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['testCases'] });
    },
  });
}

function useTestCaseActivities(
  testCaseId: string,
  limit = DEFAULT_ACTIVITY_LIMIT,
): ReturnType<typeof useQuery<TestCaseActivitiesResult, Error>> {
  const hasTestCaseId = testCaseId.length > 0;
  return useQuery<TestCaseActivitiesResult, Error>({
    enabled: hasTestCaseId,
    queryFn: () => testCasesApi.fetchTestCaseActivities(testCaseId, limit),
    queryKey: ['testCaseActivities', testCaseId, limit],
  });
}

function useTestCaseStats(projectId: string): ReturnType<typeof useQuery<TestCaseStats, Error>> {
  const hasProjectId = projectId.length > 0;
  return useQuery<TestCaseStats, Error>({
    enabled: hasProjectId,
    queryFn: () => testCasesApi.fetchTestCaseStats(projectId),
    queryKey: ['testCaseStats', projectId],
  });
}

export {
  useApproveTestCase,
  useCreateTestCase,
  useDeleteTestCase,
  useDeprecateTestCase,
  useSubmitTestCaseForReview,
  useTestCase,
  useTestCaseActivities,
  useTestCaseStats,
  useTestCases,
  useTransitionTestCaseStatus,
  useUpdateTestCase,
};
