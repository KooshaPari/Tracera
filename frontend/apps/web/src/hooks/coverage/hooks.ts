import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { Item, Link } from '../../api/types';

import { exportMatrix, fetchMatrix, type TraceabilityMatrix } from '../../api/matrix';

const coverageKeys = {
  all: ['coverage'] as const,
  matrix: (projectId: string, viewFilter?: string) =>
    [...coverageKeys.all, 'matrix', projectId, viewFilter] as const,
  gaps: (projectId: string, viewFilter?: string) =>
    [...coverageKeys.all, 'gaps', projectId, viewFilter] as const,
  stats: (projectId: string) => [...coverageKeys.all, 'stats', projectId] as const,
  activities: (projectId: string) => [...coverageKeys.all, 'activities', projectId] as const,
};

interface CoverageGap {
  itemId: string;
  reason: 'untraced' | 'unlinked';
  item?: Item;
}

interface CoverageStats {
  percentage: number;
  total: number;
  traced: number;
  untraced: number;
}

interface CoverageActivity {
  id: string;
  itemId: string;
  action: string;
  timestamp: string;
}

function deriveGaps(matrix: TraceabilityMatrix): CoverageGap[] {
  const linkedItemIds = new Set<string>(
    matrix.links.flatMap((link) => [link.sourceId, link.targetId].filter(Boolean) as string[]),
  );

  return matrix.items
    .filter((item) => !linkedItemIds.has(item.id))
    .map((item) => ({ item, itemId: item.id, reason: 'untraced' as const }));
}

function useTraceabilityMatrix(projectId: string, viewFilter?: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => fetchMatrix(projectId),
    queryKey: coverageKeys.matrix(projectId, viewFilter),
  });
}

function useCoverage(projectId: string, viewFilter?: string) {
  return useTraceabilityMatrix(projectId, viewFilter);
}

function useCoverages(projectId: string, viewFilter?: string) {
  return useTraceabilityMatrix(projectId, viewFilter);
}

function useCoverageGaps(projectId: string, viewFilter?: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const matrix = await fetchMatrix(projectId);
      return deriveGaps(matrix);
    },
    queryKey: coverageKeys.gaps(projectId, viewFilter),
  });
}

function useCoverageStats(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async (): Promise<CoverageStats> => {
      const matrix = await fetchMatrix(projectId);
      return matrix.coverage;
    },
    queryKey: coverageKeys.stats(projectId),
  });
}

function useCoverageActivities(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async (): Promise<CoverageActivity[]> => [],
    queryKey: coverageKeys.activities(projectId),
  });
}

function useCreateCoverage(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (_payload: { sourceId: string; targetId: string }): Promise<Link> => {
      throw new Error('Creating coverage links is not yet supported.');
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: coverageKeys.matrix(projectId) });
    },
  });
}

function useUpdateCoverage(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (_payload: { linkId: string; status?: string }): Promise<void> => {
      throw new Error('Updating coverage links is not yet supported.');
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: coverageKeys.matrix(projectId) });
    },
  });
}

function useDeleteCoverage(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (_linkId: string): Promise<void> => {
      throw new Error('Deleting coverage links is not yet supported.');
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: coverageKeys.matrix(projectId) });
    },
  });
}

function useVerifyCoverage(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (_linkId: string): Promise<void> => {
      throw new Error('Verifying coverage links is not yet supported.');
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: coverageKeys.matrix(projectId) });
    },
  });
}

export {
  coverageKeys,
  useCoverage,
  useCoverageActivities,
  useCoverageGaps,
  useCoverages,
  useCoverageStats,
  useCreateCoverage,
  useDeleteCoverage,
  useTraceabilityMatrix,
  useUpdateCoverage,
  useVerifyCoverage,
  type CoverageActivity,
  type CoverageGap,
  type CoverageStats,
};

export { exportMatrix };
