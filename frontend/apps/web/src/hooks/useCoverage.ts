import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  CoverageActivity,
  CoverageGap,
  CoverageGapsResponse,
  CoverageStats,
  CoverageStatus,
  CoverageType,
  TestCoverage,
  TraceabilityMatrix,
  TraceabilityMatrixItem,
} from '@tracertm/types';

import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

// Transform API response (snake_case) to frontend format (camelCase)
function transformCoverage(data: Record<string, unknown>): TestCoverage {
  return {
    coveragePercentage: data['coverage_percentage'] as number | undefined,
    coverageType: data['coverage_type'] as CoverageType,
    createdAt: data['created_at'] as string,
    createdBy: data['created_by'] as string | undefined,
    id: data['id'] as string,
    lastTestResult: data['last_test_result'] as string | undefined,
    lastTestedAt: data['last_tested_at'] as string | undefined,
    lastVerifiedAt: data['last_verified_at'] as string | undefined,
    metadata: data['coverage_metadata'] as Record<string, unknown> | undefined,
    notes: data['notes'] as string | undefined,
    projectId: data['project_id'] as string,
    rationale: data['rationale'] as string | undefined,
    requirementId: data['requirement_id'] as string,
    status: data['status'] as CoverageStatus,
    testCaseId: data['test_case_id'] as string,
    updatedAt: data['updated_at'] as string,
    verifiedBy: data['verified_by'] as string | undefined,
    version: data['version'] as number,
  };
}

interface CoverageFilters {
  projectId: string;
  coverageType?: CoverageType;
  status?: CoverageStatus;
  testCaseId?: string;
  requirementId?: string;
  skip?: number;
  limit?: number;
}

async function fetchCoverages(
  filters: CoverageFilters,
): Promise<{ coverages: TestCoverage[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.coverageType) {
    params.set('coverage_type', filters.coverageType);
  }
  if (filters.status) {
    params.set('status', filters.status);
  }
  if (filters.testCaseId) {
    params.set('test_case_id', filters.testCaseId);
  }
  if (filters.requirementId) {
    params.set('requirement_id', filters.requirementId);
  }
  if (filters.skip !== undefined) {
    params.set('skip', String(filters.skip));
  }
  if (filters.limit !== undefined) {
    params.set('limit', String(filters.limit));
  }

  const res = await fetch(`${API_URL}/api/v1/coverage?${params}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch coverages: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    coverages: (data['coverages'] || []).map(transformCoverage),
    total: data['total'] || 0,
  };
}

async function fetchCoverage(id: string): Promise<TestCoverage> {
  const res = await fetch(`${API_URL}/api/v1/coverage/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch coverage');
  }
  const data = await res.json();
  return transformCoverage(data);
}

interface CreateCoverageData {
  projectId: string;
  testCaseId: string;
  requirementId: string;
  coverageType?: CoverageType;
  coveragePercentage?: number;
  rationale?: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}

async function createCoverage(
  data: CreateCoverageData,
): Promise<{ id: string; coverageType: string; status: string }> {
  const params = new URLSearchParams();
  params.set('project_id', data['projectId']);
  params.set('test_case_id', data['testCaseId']);
  params.set('requirement_id', data['requirementId']);
  if (data['coverageType']) {
    params.set('coverage_type', data['coverageType']);
  }
  if (data['coveragePercentage'] !== undefined) {
    params.set('coverage_percentage', String(data['coveragePercentage']));
  }
  if (data['rationale']) {
    params.set('rationale', data['rationale']);
  }
  if (data['notes']) {
    params.set('notes', data['notes']);
  }

  const res = await fetch(`${API_URL}/api/v1/coverage?${params}`, {
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create coverage');
  }
  const result = await res.json();
  return {
    coverageType: result['coverage_type'],
    id: result['id'],
    status: result.status,
  };
}

async function updateCoverage(
  id: string,
  data: Partial<{
    coverageType: CoverageType;
    status: CoverageStatus;
    coveragePercentage: number;
    rationale: string;
    notes: string;
  }>,
): Promise<{ id: string; version: number }> {
  const params = new URLSearchParams();
  if (data['coverageType']) {
    params.set('coverage_type', data['coverageType']);
  }
  if (data.status) {
    params.set('status', data.status);
  }
  if (data['coveragePercentage'] !== undefined) {
    params.set('coverage_percentage', String(data['coveragePercentage']));
  }
  if (data['rationale']) {
    params.set('rationale', data['rationale']);
  }
  if (data['notes']) {
    params.set('notes', data['notes']);
  }

  const res = await fetch(`${API_URL}/api/v1/coverage/${id}?${params}`, {
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  if (!res.ok) {
    throw new Error('Failed to update coverage');
  }
  return res.json();
}

async function deleteCoverage(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/coverage/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete coverage');
  }
}

async function verifyCoverage(
  id: string,
  notes?: string,
): Promise<{ id: string; lastVerifiedAt: string; verifiedBy: string }> {
  const params = new URLSearchParams();
  if (notes) {
    params.set('notes', notes);
  }

  const res = await fetch(`${API_URL}/api/v1/coverage/${id}/verify?${params}`, {
    headers: getAuthHeaders(),
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to verify coverage');
  }
  const result = await res.json();
  return {
    id: result['id'],
    lastVerifiedAt: result['last_verified_at'],
    verifiedBy: result['verified_by'],
  };
}

async function fetchTraceabilityMatrix(
  projectId: string,
  requirementView?: string,
): Promise<TraceabilityMatrix> {
  const params = new URLSearchParams();
  params.set('project_id', projectId);
  if (requirementView) {
    params.set('requirement_view', requirementView);
  }

  const res = await fetch(`${API_URL}/api/v1/coverage/matrix?${params}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch traceability matrix');
  }
  const data = await res.json();

  return {
    coveragePercentage: data['coverage_percentage'],
    coveredRequirements: data['covered_requirements'],
    matrix: ((data['matrix'] as unknown[]) || []).map((value: unknown) => {
      const item = (typeof value === 'object' && value !== null ? value : {}) as Record<
        string,
        unknown
      >;
      return {
        isCovered: item['is_covered'],
        overallStatus: item['overall_status'],
        requirementId: item['requirement_id'],
        requirementStatus: item['requirement_status'],
        requirementTitle: item['requirement_title'],
        requirementView: item['requirement_view'],
        testCases: ((item['test_cases'] as unknown[]) || []).map((tcValue: unknown) => {
          const tc = (typeof tcValue === 'object' && tcValue !== null ? tcValue : {}) as Record<
            string,
            unknown
          >;
          return {
            coveragePercentage: tc['coverage_percentage'],
            coverageType: tc['coverage_type'],
            lastTestResult: tc['last_test_result'],
            lastTestedAt: tc['last_tested_at'],
            testCaseId: tc['test_case_id'],
          };
        }),
        testCount: item['test_count'],
      };
    }) as TraceabilityMatrixItem[],
    projectId: data['project_id'],
    totalRequirements: data['total_requirements'],
    uncoveredRequirements: data['uncovered_requirements'],
  };
}

async function fetchCoverageGaps(
  projectId: string,
  requirementView?: string,
): Promise<CoverageGapsResponse> {
  const params = new URLSearchParams();
  params.set('project_id', projectId);
  if (requirementView) {
    params.set('requirement_view', requirementView);
  }

  const res = await fetch(`${API_URL}/api/v1/coverage/gaps?${params}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch coverage gaps');
  }
  const data = await res.json();

  return {
    coveragePercentage: data['coverage_percentage'],
    gaps: ((data['gaps'] as unknown[]) || []).map((value: unknown) => {
      const gap = (typeof value === 'object' && value !== null ? value : {}) as Record<
        string,
        unknown
      >;
      return {
        priority: gap['priority'],
        requirementId: gap['requirement_id'],
        requirementStatus: gap['requirement_status'],
        requirementTitle: gap['requirement_title'],
        requirementView: gap['requirement_view'],
      };
    }) as CoverageGap[],
    projectId: data['project_id'],
    totalRequirements: data['total_requirements'],
    uncoveredCount: data['uncovered_count'],
  };
}

async function fetchCoverageStats(projectId: string): Promise<CoverageStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/coverage/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch coverage stats');
  }
  const data = await res.json();

  return {
    byStatus: data['by_status'] || {},
    byType: data['by_type'] || {},
    projectId: data['project_id'],
    totalMappings: data['total_mappings'] || 0,
    uniqueRequirements: data['unique_requirements'] || 0,
    uniqueTestCases: data['unique_test_cases'] || 0,
  };
}

async function fetchCoverageActivities(
  coverageId: string,
  limit = 50,
): Promise<{ coverageId: string; activities: CoverageActivity[] }> {
  const res = await fetch(`${API_URL}/api/v1/coverage/${coverageId}/activities?limit=${limit}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch activities');
  }
  const data = await res.json();

  return {
    activities: ((data['activities'] as unknown[]) || []).map((value: unknown) => {
      const a = (typeof value === 'object' && value !== null ? value : {}) as Record<
        string,
        unknown
      >;
      return {
        activityType: a['activity_type'],
        coverageId: a['coverage_id'],
        createdAt: a['created_at'],
        description: a['description'],
        fromValue: a['from_value'],
        id: a['id'],
        metadata: a['activity_metadata'],
        performedBy: a['performed_by'],
        toValue: a['to_value'],
      };
    }) as CoverageActivity[],
    coverageId: data['coverage_id'],
  };
}

// React Query hooks

export function useCoverages(filters: CoverageFilters) {
  return useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: () => fetchCoverages(filters),
    queryKey: ['coverages', JSON.stringify(filters)],
  });
}

export function useCoverage(id: string) {
  return useQuery({
    enabled: Boolean(id),
    queryFn: () => fetchCoverage(id),
    queryKey: ['coverages', id],
  });
}

export function useCreateCoverage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createCoverage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coverages'] });
      queryClient.invalidateQueries({ queryKey: ['traceabilityMatrix'] });
      queryClient.invalidateQueries({ queryKey: ['coverageGaps'] });
      queryClient.invalidateQueries({ queryKey: ['coverageStats'] });
    },
  });
}

export function useUpdateCoverage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<{
        coverageType: CoverageType;
        status: CoverageStatus;
        coveragePercentage: number;
        rationale: string;
        notes: string;
      }>;
    }) => updateCoverage(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['coverages'] });
      queryClient.invalidateQueries({ queryKey: ['coverages', id] });
      queryClient.invalidateQueries({ queryKey: ['traceabilityMatrix'] });
    },
  });
}

export function useDeleteCoverage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteCoverage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coverages'] });
      queryClient.invalidateQueries({ queryKey: ['traceabilityMatrix'] });
      queryClient.invalidateQueries({ queryKey: ['coverageGaps'] });
      queryClient.invalidateQueries({ queryKey: ['coverageStats'] });
    },
  });
}

export function useVerifyCoverage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) => verifyCoverage(id, notes),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['coverages', id] });
      queryClient.invalidateQueries({ queryKey: ['coverageActivities', id] });
    },
  });
}

export function useTraceabilityMatrix(projectId: string, requirementView?: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchTraceabilityMatrix(projectId, requirementView),
    queryKey: ['traceabilityMatrix', projectId, requirementView],
  });
}

export function useCoverageGaps(projectId: string, requirementView?: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchCoverageGaps(projectId, requirementView),
    queryKey: ['coverageGaps', projectId, requirementView],
  });
}

export function useCoverageStats(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchCoverageStats(projectId),
    queryKey: ['coverageStats', projectId],
  });
}

export function useCoverageActivities(coverageId: string, limit = 50) {
  return useQuery({
    enabled: Boolean(coverageId),
    queryFn: () => fetchCoverageActivities(coverageId, limit),
    queryKey: ['coverageActivities', coverageId, limit],
  });
}
