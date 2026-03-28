import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { WorkflowRun, WorkflowSchedule } from '@tracertm/types';

import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';
const REFRESH_RUNS_INTERVAL_MS = 15_000;
const REFRESH_SCHEDULES_INTERVAL_MS = 30_000;

function transformRun(data: Record<string, unknown>): WorkflowRun {
  return {
    completedAt: data['completed_at'],
    createdAt: data['created_at'],
    createdByUserId: data['created_by_user_id'],
    errorMessage: data['error_message'],
    externalRunId: data['external_run_id'],
    graphId: data['graph_id'],
    id: data['id'],
    payload: data['payload'],
    projectId: data['project_id'],
    result: data['result'],
    startedAt: data['started_at'],
    status: data['status'],
    updatedAt: data['updated_at'],
    workflowName: data['workflow_name'],
  } as WorkflowRun;
}

function transformSchedule(data: Record<string, unknown>): WorkflowSchedule {
  return {
    id: data['id'] ?? data['cron_id'],
    cronName: data['cron_name'] ?? data['name'],
    expression: data['expression'] ?? data['cron_expression'],
    workflowName: data['workflow_name'],
    additionalMetadata: data['additional_metadata'],
    ...data,
  } as WorkflowSchedule;
}

const useWorkflowRuns = (
  projectId: string,
  status?: string,
  workflowName?: string,
  limit = 100,
): ReturnType<typeof useQuery> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const params = new URLSearchParams({ limit: String(limit) });
      if (status) {
        params.set('status', status);
      }
      if (workflowName) {
        params.set('workflow_name', workflowName);
      }
      const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/workflows/runs?${params}`, {
        headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch workflow runs: ${res.status}`);
      }
      const data = await res.json();
      return {
        runs: (data['runs'] ?? []).map((run: Record<string, unknown>) => transformRun(run)),
        total: data['total'] ?? 0,
      };
    },
    queryKey: ['workflows', 'runs', projectId, status, workflowName, limit],
    refetchInterval: REFRESH_RUNS_INTERVAL_MS,
  });

const useWorkflowSchedules = (projectId: string): ReturnType<typeof useQuery> =>
  useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/workflows/schedules`, {
        headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch workflow schedules: ${res.status}`);
      }
      const data = await res.json();
      return {
        schedules: (data['schedules'] ?? []).map((schedule: Record<string, unknown>) =>
          transformSchedule(schedule),
        ),
        total: data['total'] ?? 0,
      };
    },
    queryKey: ['workflows', 'schedules', projectId],
    refetchInterval: REFRESH_SCHEDULES_INTERVAL_MS,
  });

const useBootstrapWorkflowSchedules = (): ReturnType<typeof useMutation<any, any, any, any>> => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (projectId: string) => {
      const res = await fetch(
        `${API_URL}/api/v1/projects/${projectId}/workflows/schedules/bootstrap`,
        {
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
          method: 'POST',
        },
      );
      if (!res.ok) {
        throw new Error(`Failed to bootstrap schedules: ${res.status}`);
      }
      return res.json();
    },
    onSuccess: async (_data, projectId) =>
      queryClient.invalidateQueries({
        queryKey: ['workflows', 'schedules', projectId],
      }),
  });
};

const useDeleteWorkflowSchedule = (): ReturnType<typeof useMutation<any, any, any, any>> => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ projectId, cronId }: { projectId: string; cronId: string }) => {
      const res = await fetch(
        `${API_URL}/api/v1/projects/${projectId}/workflows/schedules/${cronId}`,
        { headers: getAuthHeaders(), method: 'DELETE' },
      );
      if (!res.ok) {
        throw new Error(`Failed to delete schedule: ${res.status}`);
      }
      return res.json();
    },
    onSuccess: async (_data, variables) =>
      queryClient.invalidateQueries({
        queryKey: ['workflows', 'schedules', variables.projectId],
      }),
  });
};

export {
  useBootstrapWorkflowSchedules,
  useDeleteWorkflowSchedule,
  useWorkflowRuns,
  useWorkflowSchedules,
};
