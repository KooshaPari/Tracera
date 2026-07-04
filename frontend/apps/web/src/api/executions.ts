// Execution API endpoints for QA Integration

import { client, handleApiResponse, safeApiCall } from './client';

const { apiClient } = client;

// Types for execution API
type ExecutionConfig = Record<string, string | number | boolean | object | null | undefined>;

interface VideoSize {
  height?: number;
  width?: number;
  [key: string]: number | undefined;
}

interface ResourceLimits {
  cpu?: string | number;
  memory?: string | number;
  [key: string]: string | number | undefined;
}

export type ArtifactMetadata = Record<
  string,
  string | number | boolean | object | null | undefined
>;

export interface Execution {
  id: string;
  project_id: string;
  test_run_id?: string;
  item_id?: string;
  execution_type: 'vhs' | 'playwright' | 'codex' | 'custom';
  trigger_source: 'github_pr' | 'github_push' | 'webhook' | 'manual';
  trigger_ref?: string;
  status: 'pending' | 'running' | 'passed' | 'failed' | 'cancelled';
  container_id?: string;
  container_image?: string;
  config?: ExecutionConfig;
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
  exit_code?: number;
  error_message?: string;
  output_summary?: string;
  created_at: string;
  updated_at: string;
  artifact_count: number;
}

export interface ExecutionArtifact {
  id: string;
  execution_id: string;
  item_id?: string;
  artifact_type: 'screenshot' | 'video' | 'gif' | 'log' | 'trace' | 'tape';
  file_path: string;
  thumbnail_path?: string;
  file_size?: number;
  mime_type?: string;
  metadata?: ArtifactMetadata;
  captured_at: string;
  created_at: string;
  url?: string;
  thumbnail_url?: string;
}

export interface ExecutionCreate {
  execution_type: 'vhs' | 'playwright' | 'codex' | 'custom';
  trigger_source?: 'github_pr' | 'github_push' | 'webhook' | 'manual';
  trigger_ref?: string;
  test_run_id?: string;
  item_id?: string;
  config?: ExecutionConfig;
  container_image?: string;
}

export interface ExecutionComplete {
  duration_ms?: number;
  error_message?: string;
  exit_code?: number;
  output_summary?: string;
  status: 'passed' | 'failed' | 'cancelled';
}

export interface ExecutionEnvironmentConfig {
  auto_screenshot: boolean;
  auto_video: boolean;
  artifact_retention_days: number;
  codex_enabled: boolean;
  codex_full_auto: boolean;
  codex_sandbox_mode: string;
  codex_timeout: number;
  created_at: string;
  docker_image: string;
  execution_timeout: number;
  id: string;
  max_artifact_size_mb: number;
  max_concurrent_executions: number;
  network_mode: string;
  playwright_browser: string;
  playwright_enabled: boolean;
  playwright_headless: boolean;
  playwright_viewport_height: number;
  playwright_viewport_width: number;
  playwright_video_size?: VideoSize;
  storage_path?: string;
  project_id: string;
  updated_at: string;
  vhs_enabled: boolean;
  vhs_framerate: number;
  vhs_font_size: number;
  vhs_height: number;
  vhs_theme: string;
  vhs_width: number;
  vhs_viewport_height: number;
  vhs_viewport_width: number;
  working_directory?: string;
  resource_limits?: ResourceLimits;
}

export interface ExecutionEnvironmentConfigUpdate {
  artifact_retention_days?: number;
  auto_screenshot?: boolean;
  auto_video?: boolean;
  codex_enabled?: boolean;
  codex_full_auto?: boolean;
  codex_sandbox_mode?: 'read-only' | 'workspace-write' | 'danger-full-access';
  codex_timeout?: number;
  docker_image?: string;
  execution_timeout?: number;
  max_artifact_size_mb?: number;
  max_concurrent_executions?: number;
  network_mode?: 'bridge' | 'host' | 'none';
  playwright_browser?: 'chromium' | 'firefox' | 'webkit';
  playwright_enabled?: boolean;
  playwright_headless?: boolean;
  playwright_video_size?: VideoSize;
  playwright_viewport_height?: number;
  playwright_viewport_width?: number;
  resource_limits?: ResourceLimits;
  storage_path?: string;
  vhs_enabled?: boolean;
  vhs_framerate?: number;
  vhs_font_size?: number;
  vhs_height?: number;
  vhs_theme?: string;
  vhs_width?: number;
  working_directory?: string;
}

type ApiResponse<T> = Promise<{
  data?: T;
  error?: unknown;
  response: Response;
}>;

type ApiMethod<T> = (path: string, init: Record<string, unknown>) => ApiResponse<T>;

const complete = async (
  projectId: string,
  executionId: string,
  data: ExecutionComplete,
): Promise<{ completed: boolean; execution_id: string }> =>
  handleApiResponse(
    safeApiCall(
      (
        apiClient.POST as ApiMethod<{
          completed: boolean;
          execution_id: string;
        }>
      )('/api/v1/projects/{project_id}/executions/{execution_id}/complete', {
        body: data,
        params: {
          path: { execution_id: executionId, project_id: projectId },
        },
      }),
    ),
  );

const create = async (projectId: string, data: ExecutionCreate): Promise<Execution> =>
  handleApiResponse(
    safeApiCall(
      (apiClient.POST as ApiMethod<Execution>)('/api/v1/projects/{project_id}/executions', {
        body: data,
        params: { path: { project_id: projectId } },
      }),
    ),
  );

const downloadArtifact = (projectId: string, executionId: string, artifactId: string): string =>
  `${import.meta.env.VITE_API_URL ?? 'http://localhost:4000'}/api/v1/projects/${projectId}/executions/${executionId}/artifacts/${artifactId}/download`;

const get = async (projectId: string, executionId: string): Promise<Execution> =>
  handleApiResponse(
    safeApiCall(
      (apiClient.GET as ApiMethod<Execution>)(
        '/api/v1/projects/{project_id}/executions/{execution_id}',
        {
          params: {
            path: { execution_id: executionId, project_id: projectId },
          },
        },
      ),
    ),
  );

const getConfig = async (projectId: string): Promise<ExecutionEnvironmentConfig> =>
  handleApiResponse(
    safeApiCall(
      (apiClient.GET as ApiMethod<ExecutionEnvironmentConfig>)(
        '/api/v1/projects/{project_id}/execution-config',
        {
          params: { path: { project_id: projectId } },
        },
      ),
    ),
  );

const list = async (
  projectId: string,
  params?: {
    execution_type?: string;
    limit?: number;
    offset?: number;
    status?: string;
  },
): Promise<{ executions: Execution[]; total: number }> =>
  handleApiResponse(
    safeApiCall(
      (
        apiClient.GET as ApiMethod<{
          executions: Execution[];
          total: number;
        }>
      )('/api/v1/projects/{project_id}/executions', {
        params: { path: { project_id: projectId }, query: params },
      }),
    ),
  );

const listArtifacts = async (
  projectId: string,
  executionId: string,
  artifactType?: string,
): Promise<{ artifacts: ExecutionArtifact[]; total: number }> =>
  handleApiResponse(
    safeApiCall(
      (
        apiClient.GET as ApiMethod<{
          artifacts: ExecutionArtifact[];
          total: number;
        }>
      )('/api/v1/projects/{project_id}/executions/{execution_id}/artifacts', {
        params: {
          path: { execution_id: executionId, project_id: projectId },
          query: { artifact_type: artifactType },
        },
      }),
    ),
  );

const start = async (
  projectId: string,
  executionId: string,
): Promise<{ started: boolean; execution_id: string }> =>
  handleApiResponse(
    safeApiCall(
      (
        apiClient.POST as ApiMethod<{
          execution_id: string;
          started: boolean;
        }>
      )('/api/v1/projects/{project_id}/executions/{execution_id}/start', {
        params: {
          path: { execution_id: executionId, project_id: projectId },
        },
      }),
    ),
  );

const updateConfig = async (
  projectId: string,
  data: ExecutionEnvironmentConfigUpdate,
): Promise<ExecutionEnvironmentConfig> =>
  handleApiResponse(
    safeApiCall(
      (apiClient.PUT as ApiMethod<ExecutionEnvironmentConfig>)(
        '/api/v1/projects/{project_id}/execution-config',
        {
          body: data,
          params: { path: { project_id: projectId } },
        },
      ),
    ),
  );

const executionsApi = {
  complete,
  create,
  downloadArtifact,
  get,
  getConfig,
  list,
  listArtifacts,
  start,
  updateConfig,
};

export { executionsApi };
export default executionsApi;
