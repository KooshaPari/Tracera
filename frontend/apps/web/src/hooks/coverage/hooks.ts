import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { client } from '../../api/client';

export type CoverageViewFilter = 'unit' | 'integration' | 'e2e' | 'manual';

export interface CoverageGap {
  requirementId: string;
  title: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  reason?: string;
}

export interface CoverageGapsResponse {
  gaps: CoverageGap[];
  uncoveredCount: number;
}

export interface TraceabilityMatrixCell {
  requirementId: string;
  testIds: string[];
  covered: boolean;
}

export interface TraceabilityMatrixResponse {
  matrix: TraceabilityMatrixCell[];
  totalRequirements: number;
  coveredRequirements: number;
  uncoveredRequirements: number;
  coveragePercentage: number;
}

interface CoverageGapsResult {
  data: CoverageGapsResponse;
}

interface TraceabilityMatrixResult {
  data: TraceabilityMatrixResponse;
}

async function fetchCoverageGaps(
  projectId: string,
  viewFilter: CoverageViewFilter,
): Promise<CoverageGapsResponse> {
  const params = new URLSearchParams({ filter: viewFilter });
  const response = await client.apiClient.get<CoverageGapsResponse>(
    `/api/v1/projects/${projectId}/coverage/gaps?${params.toString()}`,
    {
      headers: await client.getAuthHeaders(),
    },
  );
  return response;
}

async function fetchTraceabilityMatrix(
  projectId: string,
  viewFilter: CoverageViewFilter,
): Promise<TraceabilityMatrixResponse> {
  const params = new URLSearchParams({ filter: viewFilter });
  const response = await client.apiClient.get<TraceabilityMatrixResponse>(
    `/api/v1/projects/${projectId}/coverage/matrix?${params.toString()}`,
    {
      headers: await client.getAuthHeaders(),
    },
  );
  return response;
}

const EMPTY_GAPS: CoverageGapsResponse = {
  gaps: [],
  uncoveredCount: 0,
};

const EMPTY_MATRIX: TraceabilityMatrixResponse = {
  matrix: [],
  totalRequirements: 0,
  coveredRequirements: 0,
  uncoveredRequirements: 0,
  coveragePercentage: 0,
};

function useCoverageGaps(
  projectId: string | undefined,
  viewFilter: CoverageViewFilter,
): CoverageGapsResult {
  const query = useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        return EMPTY_GAPS;
      }
      try {
        return await fetchCoverageGaps(projectId, viewFilter);
      } catch {
        return EMPTY_GAPS;
      }
    },
    queryKey: ['coverage', 'gaps', projectId, viewFilter],
  });
  return {
    data: query.data ?? EMPTY_GAPS,
  };
}

function useTraceabilityMatrix(
  projectId: string | undefined,
  viewFilter: CoverageViewFilter,
): TraceabilityMatrixResult {
  const query = useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        return EMPTY_MATRIX;
      }
      try {
        return await fetchTraceabilityMatrix(projectId, viewFilter);
      } catch {
        return EMPTY_MATRIX;
      }
    },
    queryKey: ['coverage', 'matrix', projectId, viewFilter],
  });
  return {
    data: query.data ?? EMPTY_MATRIX,
  };
}

export interface CoverageRecord {
  id: string;
  projectId: string;
  viewFilter: CoverageViewFilter;
  totalRequirements: number;
  coveredRequirements: number;
  coveragePercentage: number;
  updatedAt: string;
}

interface CoverageListResult {
  data: CoverageRecord[];
}

interface CoverageResult {
  data: CoverageRecord | undefined;
}

interface CoverageResultMap<T> {
  data: T | undefined;
}

async function fetchCoverages(projectId: string): Promise<CoverageRecord[]> {
  const response = await client.apiClient.get<CoverageRecord[]>(
    `/api/v1/projects/${projectId}/coverage`,
    { headers: await client.getAuthHeaders() },
  );
  return response;
}

async function fetchCoverage(
  projectId: string,
  coverageId: string,
): Promise<CoverageRecord> {
  const response = await client.apiClient.get<CoverageRecord>(
    `/api/v1/projects/${projectId}/coverage/${coverageId}`,
    { headers: await client.getAuthHeaders() },
  );
  return response;
}

async function postCoverage(
  projectId: string,
  payload: Partial<CoverageRecord>,
): Promise<CoverageRecord> {
  const response = await client.apiClient.post<CoverageRecord>(
    `/api/v1/projects/${projectId}/coverage`,
    { body: payload, headers: await client.getAuthHeaders() },
  );
  return response;
}

async function patchCoverage(
  projectId: string,
  coverageId: string,
  payload: Partial<CoverageRecord>,
): Promise<CoverageRecord> {
  const response = await client.apiClient.put<CoverageRecord>(
    `/api/v1/projects/${projectId}/coverage/${coverageId}`,
    { body: payload, headers: await client.getAuthHeaders() },
  );
  return response;
}

async function deleteCoverage(projectId: string, coverageId: string): Promise<void> {
  await client.apiClient.delete(
    `/api/v1/projects/${projectId}/coverage/${coverageId}`,
    { headers: await client.getAuthHeaders() },
  );
}

async function postVerifyCoverage(
  projectId: string,
  coverageId: string,
): Promise<{ verified: boolean }> {
  const response = await client.apiClient.post<{ verified: boolean }>(
    `/api/v1/projects/${projectId}/coverage/${coverageId}/verify`,
    { body: {}, headers: await client.getAuthHeaders() },
  );
  return response;
}

const EMPTY_COVERAGE_LIST: CoverageRecord[] = [];

function useCoverages(projectId: string | undefined): CoverageListResult {
  const query = useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        return EMPTY_COVERAGE_LIST;
      }
      try {
        return await fetchCoverages(projectId);
      } catch {
        return EMPTY_COVERAGE_LIST;
      }
    },
    queryKey: ['coverage', 'list', projectId],
  });
  return { data: query.data ?? EMPTY_COVERAGE_LIST };
}

function useCoverage(
  projectId: string | undefined,
  coverageId: string | undefined,
): CoverageResult {
  const query = useQuery({
    enabled: Boolean(projectId) && Boolean(coverageId),
    queryFn: async () => {
      if (projectId === undefined || coverageId === undefined) {
        return undefined;
      }
      try {
        return await fetchCoverage(projectId, coverageId);
      } catch {
        return undefined;
      }
    },
    queryKey: ['coverage', 'item', projectId, coverageId],
  });
  return { data: query.data };
}

function useCoverageStats(
  projectId: string | undefined,
  viewFilter: CoverageViewFilter,
): CoverageResultMap<{
  totalRequirements: number;
  coveredRequirements: number;
  coveragePercentage: number;
}> {
  const matrix = useTraceabilityMatrix(projectId, viewFilter);
  return {
    data: {
      totalRequirements: matrix.data.totalRequirements,
      coveredRequirements: matrix.data.coveredRequirements,
      coveragePercentage: matrix.data.coveragePercentage,
    },
  };
}

function useCoverageActivities(
  projectId: string | undefined,
  viewFilter: CoverageViewFilter,
): CoverageGapsResult {
  return useCoverageGaps(projectId, viewFilter);
}

function useCreateCoverage(projectId: string): CoverageResultMap<CoverageRecord> {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (payload: Partial<CoverageRecord>) => {
      if (projectId === undefined) {
        return Promise.reject(new Error('missing projectId'));
      }
      return postCoverage(projectId, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coverage', 'list', projectId] });
    },
  });
  return { data: mutation.data };
}

function useUpdateCoverage(
  projectId: string,
  coverageId: string,
): CoverageResultMap<CoverageRecord> {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (payload: Partial<CoverageRecord>) => {
      if (projectId === undefined || coverageId === undefined) {
        return Promise.reject(new Error('missing projectId/coverageId'));
      }
      return patchCoverage(projectId, coverageId, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coverage', 'list', projectId] });
      queryClient.invalidateQueries({
        queryKey: ['coverage', 'item', projectId, coverageId],
      });
    },
  });
  return { data: mutation.data };
}

function useDeleteCoverage(projectId: string): CoverageResultMap<void> {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (coverageId: string) => {
      if (projectId === undefined) {
        return Promise.reject(new Error('missing projectId'));
      }
      return deleteCoverage(projectId, coverageId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coverage', 'list', projectId] });
    },
  });
  return { data: mutation.data };
}

function useVerifyCoverage(
  projectId: string,
  coverageId: string,
): CoverageResultMap<{ verified: boolean }> {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => {
      if (projectId === undefined || coverageId === undefined) {
        return Promise.reject(new Error('missing projectId/coverageId'));
      }
      return postVerifyCoverage(projectId, coverageId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coverage', 'item', projectId, coverageId] });
    },
  });
  return { data: mutation.data };
}

export {
  useCoverageGaps,
  useTraceabilityMatrix,
  useCoverages,
  useCoverage,
  useCoverageStats,
  useCoverageActivities,
  useCreateCoverage,
  useUpdateCoverage,
  useDeleteCoverage,
  useVerifyCoverage,
};
