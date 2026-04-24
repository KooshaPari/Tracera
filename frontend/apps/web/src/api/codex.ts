// Codex Agent API endpoints

/* oxlint-disable import/no-named-export */

import { client } from './client';

const { apiClient } = client;
const { handleApiResponse } = client;
const { safeApiCall } = client;
const get = apiClient.GET.bind(apiClient);
const post = apiClient.POST.bind(apiClient);

/**
 * Input data for Codex agent tasks
 */
type CodexInputData = Record<string, string | number | boolean | object | null | undefined>;

/**
 * Output data from Codex agent tasks
 */
type CodexOutputData = Record<string, string | number | boolean | object | null | undefined>;

interface CodexAgentTask {
  id: string;
  project_id: string;
  execution_id?: string;
  artifact_id?: string;
  task_type: string;
  status: string;
  prompt?: string;
  response?: string;
  input_data?: CodexInputData;
  output_data?: CodexOutputData;
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
  tokens_used?: number;
  model_used?: string;
  error_message?: string;
  retry_count: number;
  created_at: string;
}

interface CodexReviewRequest {
  artifact_id: string;
  prompt?: string;
  execution_id?: string;
  max_frames?: number;
}

interface CodexAuthStatus {
  available: boolean;
  version?: string;
  authenticated: boolean;
  status: string;
}

const codexApi = {
  getAuthStatus: async (projectId: string): Promise<CodexAuthStatus> =>
    handleApiResponse(
      safeApiCall(
        get('/api/v1/projects/{project_id}/codex/auth-status', {
          params: { path: { project_id: projectId } },
        }),
      ),
    ),

  listInteractions: async (
    projectId: string,
    params?: {
      limit?: number;
      offset?: number;
      status?: string;
      task_type?: string;
    },
  ): Promise<{ tasks: CodexAgentTask[]; total: number }> =>
    handleApiResponse(
      safeApiCall(
        get('/api/v1/projects/{project_id}/codex/interactions', {
          params: {
            path: { project_id: projectId },
            query: params,
          },
        }),
      ),
    ),

  reviewImage: async (projectId: string, data: CodexReviewRequest): Promise<CodexAgentTask> =>
    handleApiResponse(
      safeApiCall(
        post('/api/v1/projects/{project_id}/codex/review-image', {
          body: data,
          params: { path: { project_id: projectId } },
        }),
      ),
    ),

  reviewVideo: async (projectId: string, data: CodexReviewRequest): Promise<CodexAgentTask> =>
    handleApiResponse(
      safeApiCall(
        post('/api/v1/projects/{project_id}/codex/review-video', {
          body: data,
          params: { path: { project_id: projectId } },
        }),
      ),
    ),
};

export { codexApi, type CodexAuthStatus, type CodexAgentTask, type CodexReviewRequest };
