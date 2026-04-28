import { useQuery } from '@tanstack/react-query';

import { fetchQualityReports, fetchSpecificationSummary } from '@/hooks/useSpecifications.api';

import type { QueryResult } from './query-utils';

type FetchSpecificationSummaryResult = Awaited<ReturnType<typeof fetchSpecificationSummary>>;

type FetchQualityReportsResult = Awaited<ReturnType<typeof fetchQualityReports>>;

const useSpecificationSummary = (projectId: string): QueryResult<FetchSpecificationSummaryResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await fetchSpecificationSummary(projectId);
      return response;
    },
    queryKey: ['specificationSummary', projectId],
  });

const useQualityReport = (projectId: string): QueryResult<FetchQualityReportsResult> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const response = await fetchQualityReports(projectId);
      return response;
    },
    queryKey: ['qualityReports', projectId],
  });

export {
  useQualityReport,
  useSpecificationSummary,
  type FetchQualityReportsResult,
  type FetchSpecificationSummaryResult,
};
