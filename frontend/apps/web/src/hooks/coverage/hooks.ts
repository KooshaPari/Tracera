import type {
  UseMutationResult,
  UseQueryResult,
} from '@tanstack/react-query';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  CoverageActivity,
  CoverageGapsResponse,
  CoverageStats,
  TestCoverage,
  TraceabilityMatrix,
} from '@tracertm/types';

import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: getAuthHeaders() });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

async function postJson<T>(url: string, body?: unknown): Promise<T> {
  const init: RequestInit = {
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  };
  if (body !== undefined) {
    init.body = JSON.stringify(body);
  }
  const res = await fetch(url, init);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

async function putJson<T>(url: string, body?: unknown): Promise<T> {
  const init: RequestInit = {
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  };
  if (body !== undefined) {
    init.body = JSON.stringify(body);
  }
  const res = await fetch(url, init);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

async function deleteJson(url: string): Promise<void> {
  const res = await fetch(url, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  }
}

// Query key factories
const coverageKeys = {
  activities: (id: string) => ['coverage', 'activities', id] as const,
  all: ['coverage'] as const,
  byProject: (projectId: string) => ['coverage', 'project', projectId] as const,
  detail: (id: string) => ['coverage', 'detail', id] as const,
  gaps: (projectId: string, view?: string) =>
    ['coverage', 'gaps', projectId, view] as const,
  matrix: (projectId: string, view?: string) =>
    ['coverage', 'matrix', projectId, view] as const,
  stats: (projectId: string) => ['coverage', 'stats', projectId] as const,
};

/** Fetch a single coverage mapping by ID */
export function useCoverage(
  coverageId: string | undefined,
): UseQueryResult<TestCoverage> {
  return useQuery({
    enabled: Boolean(coverageId),
    queryFn: async () => {
      if (coverageId === undefined) throw new Error('coverageId is required');
      return fetchJson<TestCoverage>(
        `${API_URL}/api/v1/coverage/${coverageId}`,
      );
    },
    queryKey: coverageKeys.detail(coverageId ?? ''),
  });
}

/** Fetch all coverage mappings for a project */
export function useCoverages(
  projectId: string | undefined,
): UseQueryResult<TestCoverage[]> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) throw new Error('projectId is required');
      return fetchJson<TestCoverage[]>(
        `${API_URL}/api/v1/projects/${projectId}/coverage`,
      );
    },
    queryKey: coverageKeys.byProject(projectId ?? ''),
  });
}

/** Fetch coverage activity log for a single mapping */
export function useCoverageActivities(
  coverageId: string | undefined,
): UseQueryResult<CoverageActivity[]> {
  return useQuery({
    enabled: Boolean(coverageId),
    queryFn: async () => {
      if (coverageId === undefined) throw new Error('coverageId is required');
      return fetchJson<CoverageActivity[]>(
        `${API_URL}/api/v1/coverage/${coverageId}/activities`,
      );
    },
    queryKey: coverageKeys.activities(coverageId ?? ''),
  });
}

/** Fetch aggregate coverage stats for a project */
export function useCoverageStats(
  projectId: string | undefined,
): UseQueryResult<CoverageStats> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) throw new Error('projectId is required');
      return fetchJson<CoverageStats>(
        `${API_URL}/api/v1/projects/${projectId}/coverage/stats`,
      );
    },
    queryKey: coverageKeys.stats(projectId ?? ''),
  });
}

/** Fetch the traceability matrix for a project, optionally filtered by view */
export function useTraceabilityMatrix(
  projectId: string | undefined,
  view?: string,
): UseQueryResult<TraceabilityMatrix> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) throw new Error('projectId is required');
      const params = new URLSearchParams();
      if (view) params.set('view', view);
      const qs = params.toString();
      return fetchJson<TraceabilityMatrix>(
        `${API_URL}/api/v1/projects/${projectId}/coverage/matrix${qs ? `?${qs}` : ''}`,
      );
    },
    queryKey: coverageKeys.matrix(projectId ?? '', view),
  });
}

/** Fetch uncovered requirement gaps for a project */
export function useCoverageGaps(
  projectId: string | undefined,
  view?: string,
): UseQueryResult<CoverageGapsResponse> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) throw new Error('projectId is required');
      const params = new URLSearchParams();
      if (view) params.set('view', view);
      const qs = params.toString();
      return fetchJson<CoverageGapsResponse>(
        `${API_URL}/api/v1/projects/${projectId}/coverage/gaps${qs ? `?${qs}` : ''}`,
      );
    },
    queryKey: coverageKeys.gaps(projectId ?? '', view),
  });
}

interface CreateCoverageInput {
  projectId: string;
  testCaseId: string;
  requirementId: string;
  coverageType: string;
  rationale?: string;
}

/** Create a new coverage mapping */
export function useCreateCoverage(): UseMutationResult<
  TestCoverage,
  Error,
  CreateCoverageInput
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateCoverageInput) =>
      postJson<TestCoverage>(`${API_URL}/api/v1/coverage`, input),
    onSuccess: (data) => {
      void queryClient.invalidateQueries({
        queryKey: coverageKeys.byProject(data.projectId),
      });
      void queryClient.invalidateQueries({ queryKey: coverageKeys.all });
    },
  });
}

interface UpdateCoverageInput {
  coverageId: string;
  updates: Partial<Omit<TestCoverage, 'id' | 'projectId' | 'createdAt' | 'version'>>;
}

/** Update an existing coverage mapping */
export function useUpdateCoverage(): UseMutationResult<
  TestCoverage,
  Error,
  UpdateCoverageInput
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ coverageId, updates }: UpdateCoverageInput) =>
      putJson<TestCoverage>(
        `${API_URL}/api/v1/coverage/${coverageId}`,
        updates,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(coverageKeys.detail(data.id), data);
      void queryClient.invalidateQueries({
        queryKey: coverageKeys.byProject(data.projectId),
      });
    },
  });
}

interface DeleteCoverageInput {
  coverageId: string;
  projectId: string;
}

/** Delete a coverage mapping */
export function useDeleteCoverage(): UseMutationResult<
  void,
  Error,
  DeleteCoverageInput
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ coverageId }: DeleteCoverageInput) =>
      deleteJson(`${API_URL}/api/v1/coverage/${coverageId}`),
    onSuccess: (_data, { projectId, coverageId }) => {
      queryClient.removeQueries({ queryKey: coverageKeys.detail(coverageId) });
      void queryClient.invalidateQueries({
        queryKey: coverageKeys.byProject(projectId),
      });
    },
  });
}

interface VerifyCoverageInput {
  coverageId: string;
  projectId: string;
  notes?: string;
}

/** Mark a coverage mapping as verified */
export function useVerifyCoverage(): UseMutationResult<
  TestCoverage,
  Error,
  VerifyCoverageInput
> {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ coverageId, notes }: VerifyCoverageInput) =>
      postJson<TestCoverage>(
        `${API_URL}/api/v1/coverage/${coverageId}/verify`,
        notes !== undefined ? { notes } : undefined,
      ),
    onSuccess: (data) => {
      queryClient.setQueryData(coverageKeys.detail(data.id), data);
      void queryClient.invalidateQueries({
        queryKey: coverageKeys.byProject(data.projectId),
      });
    },
  });
}
