import type { UseQueryResult } from '@tanstack/react-query';

import { useQuery } from '@tanstack/react-query';

import type {
  CoverageMetrics,
  DefectDensity,
  ExecutionHistory,
  FlakyTests,
  PassRateTrend,
  QAMetricsSummary,
} from './types';

import {
  fetchCoverageMetrics,
  fetchDefectDensity,
  fetchExecutionHistory,
  fetchFlakyTests,
  fetchPassRateTrend,
  fetchQAMetricsSummary,
} from './api';

function useQAMetricsSummary(projectId: string | undefined): UseQueryResult<QAMetricsSummary> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchQAMetricsSummary(projectId);
      return result;
    },
    queryKey: ['qaMetrics', 'summary', projectId],
  });
}

function usePassRateTrend(projectId: string | undefined, days = 30): UseQueryResult<PassRateTrend> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchPassRateTrend(projectId, days);
      return result;
    },
    queryKey: ['qaMetrics', 'passRate', projectId, days],
  });
}

function useCoverageMetrics(projectId: string | undefined): UseQueryResult<CoverageMetrics> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchCoverageMetrics(projectId);
      return result;
    },
    queryKey: ['qaMetrics', 'coverage', projectId],
  });
}

function useDefectDensity(projectId: string | undefined): UseQueryResult<DefectDensity> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchDefectDensity(projectId);
      return result;
    },
    queryKey: ['qaMetrics', 'defectDensity', projectId],
  });
}

function useFlakyTests(projectId: string | undefined): UseQueryResult<FlakyTests> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchFlakyTests(projectId);
      return result;
    },
    queryKey: ['qaMetrics', 'flakyTests', projectId],
  });
}

function useExecutionHistory(
  projectId: string | undefined,
  days = 7,
): UseQueryResult<ExecutionHistory> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchExecutionHistory(projectId, days);
      return result;
    },
    queryKey: ['qaMetrics', 'executionHistory', projectId, days],
  });
}

export {
  useCoverageMetrics,
  useDefectDensity,
  useExecutionHistory,
  useFlakyTests,
  usePassRateTrend,
  useQAMetricsSummary,
};
