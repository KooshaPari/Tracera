import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { TestRunPayload } from './tests-api';
import type { TestSpecCreate, TestSpecUpdate, TestType } from './types';

import { itemSpecKeys } from './keys';
import {
  createTestSpec,
  deleteTestSpec,
  fetchFlakyTests,
  fetchQuarantinedTests,
  fetchTestHealthReport,
  fetchTestSpec,
  fetchTestSpecByItem,
  fetchTestSpecs,
  quarantineTest,
  recordTestRun,
  unquarantineTest,
  updateTestSpec,
} from './tests-api';

function useTestSpecs(
  projectId: string,
  options?: {
    testType?: TestType;
    isQuarantined?: boolean;
    limit?: number;
    offset?: number;
  },
) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchTestSpecs(projectId, options);
      return data;
    },
    queryKey: [...itemSpecKeys.tests(projectId), options],
  });
}

function useTestSpec(projectId: string, specId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(specId),
    queryFn: async () => {
      const data = await fetchTestSpec(projectId, specId);
      return data;
    },
    queryKey: itemSpecKeys.test(projectId, specId),
  });
}

function useTestSpecByItem(projectId: string, itemId: string) {
  return useQuery({
    enabled: Boolean(projectId) && Boolean(itemId),
    queryFn: async () => {
      const data = await fetchTestSpecByItem(projectId, itemId);
      return data;
    },
    queryKey: itemSpecKeys.testByItem(projectId, itemId),
  });
}

function useFlakyTests(projectId: string, threshold?: number, limit?: number) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchFlakyTests(projectId, threshold, limit);
      return data;
    },
    queryKey: [...itemSpecKeys.flakyTests(projectId), threshold],
  });
}

function useQuarantinedTests(projectId: string, limit?: number) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchQuarantinedTests(projectId, limit);
      return data;
    },
    queryKey: itemSpecKeys.quarantinedTests(projectId),
  });
}

function useTestHealthReport(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const data = await fetchTestHealthReport(projectId);
      return data;
    },
    queryKey: itemSpecKeys.testHealthReport(projectId),
  });
}

function useCreateTestSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: TestSpecCreate) => {
      const result = await createTestSpec(projectId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.test(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.tests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.flakyTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.quarantinedTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.testHealthReport(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useUpdateTestSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, data }: { specId: string; data: TestSpecUpdate }) => {
      const result = await updateTestSpec(projectId, specId, data);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.test(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.tests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.flakyTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.quarantinedTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.testHealthReport(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useDeleteTestSpec(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specId: string) => {
      await deleteTestSpec(projectId, specId);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.tests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.flakyTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.quarantinedTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.testHealthReport(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useRecordTestRun(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, ...payload }: { specId: string } & TestRunPayload) => {
      const result = await recordTestRun(projectId, specId, payload);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.test(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.tests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.flakyTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.quarantinedTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.testHealthReport(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useQuarantineTest(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ specId, reason }: { specId: string; reason: string }) => {
      const result = await quarantineTest(projectId, specId, reason);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.test(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.tests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.flakyTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.quarantinedTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.testHealthReport(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

function useUnquarantineTest(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (specId: string) => {
      const result = await unquarantineTest(projectId, specId);
      return result;
    },
    onSuccess: async (data) => {
      queryClient.setQueryData(itemSpecKeys.test(projectId, data['id']), data);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.tests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.flakyTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.quarantinedTests(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.testHealthReport(projectId) }),
        queryClient.invalidateQueries({ queryKey: itemSpecKeys.stats(projectId) }),
      ]);
    },
  });
}

export {
  useTestSpecs,
  useTestSpec,
  useTestSpecByItem,
  useFlakyTests,
  useQuarantinedTests,
  useTestHealthReport,
  useCreateTestSpec,
  useUpdateTestSpec,
  useDeleteTestSpec,
  useRecordTestRun,
  useQuarantineTest,
  useUnquarantineTest,
};
