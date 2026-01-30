// Execution API endpoints for QA Integration

import { apiClient, handleApiResponse, safeApiCall } from "./client";

/**
 * Configuration object for execution containers and tools
 */
export interface ExecutionConfig {
	[key: string]: string | number | boolean | object | null | undefined;
}

/**
 * Size configuration for Playwright video recording
 */
export interface VideoSize {
	width?: number;
	height?: number;
	[key: string]: number | undefined;
}

/**
 * Resource limits configuration
 */
export interface ResourceLimits {
	cpu?: string | number;
	memory?: string | number;
	[key: string]: string | number | undefined;
}

export interface Execution {
	id: string;
	project_id: string;
	test_run_id?: string;
	item_id?: string;
	execution_type: "vhs" | "playwright" | "codex" | "custom";
	trigger_source: "github_pr" | "github_push" | "webhook" | "manual";
	trigger_ref?: string;
	status: "pending" | "running" | "passed" | "failed" | "cancelled";
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

/**
 * Artifact metadata for execution artifacts
 */
export interface ArtifactMetadata {
	[key: string]: string | number | boolean | object | null | undefined;
}

export interface ExecutionArtifact {
	id: string;
	execution_id: string;
	item_id?: string;
	artifact_type: "screenshot" | "video" | "gif" | "log" | "trace" | "tape";
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
	execution_type: "vhs" | "playwright" | "codex" | "custom";
	trigger_source?: "github_pr" | "github_push" | "webhook" | "manual";
	trigger_ref?: string;
	test_run_id?: string;
	item_id?: string;
	config?: ExecutionConfig;
	container_image?: string;
}

export interface ExecutionComplete {
	status: "passed" | "failed" | "cancelled";
	exit_code?: number;
	error_message?: string;
	output_summary?: string;
	duration_ms?: number;
}

export interface ExecutionEnvironmentConfig {
	id: string;
	project_id: string;
	docker_image: string;
	resource_limits?: ResourceLimits;
	working_directory?: string;
	network_mode: string;
	vhs_enabled: boolean;
	playwright_enabled: boolean;
	codex_enabled: boolean;
	auto_screenshot: boolean;
	auto_video: boolean;
	vhs_theme: string;
	vhs_font_size: number;
	vhs_width: number;
	vhs_height: number;
	vhs_framerate: number;
	playwright_browser: string;
	playwright_headless: boolean;
	playwright_viewport_width: number;
	playwright_viewport_height: number;
	playwright_video_size?: VideoSize;
	codex_sandbox_mode: string;
	codex_full_auto: boolean;
	codex_timeout: number;
	artifact_retention_days: number;
	storage_path?: string;
	max_artifact_size_mb: number;
	max_concurrent_executions: number;
	execution_timeout: number;
	created_at: string;
	updated_at: string;
}

export interface ExecutionEnvironmentConfigUpdate {
	docker_image?: string;
	resource_limits?: ResourceLimits;
	working_directory?: string;
	network_mode?: "bridge" | "host" | "none";
	vhs_enabled?: boolean;
	playwright_enabled?: boolean;
	codex_enabled?: boolean;
	auto_screenshot?: boolean;
	auto_video?: boolean;
	vhs_theme?: string;
	vhs_font_size?: number;
	vhs_width?: number;
	vhs_height?: number;
	vhs_framerate?: number;
	playwright_browser?: "chromium" | "firefox" | "webkit";
	playwright_headless?: boolean;
	playwright_viewport_width?: number;
	playwright_viewport_height?: number;
	playwright_video_size?: VideoSize;
	codex_sandbox_mode?: "read-only" | "workspace-write" | "danger-full-access";
	codex_full_auto?: boolean;
	codex_timeout?: number;
	artifact_retention_days?: number;
	storage_path?: string;
	max_artifact_size_mb?: number;
	max_concurrent_executions?: number;
	execution_timeout?: number;
}

export const executionsApi = {
	create: async (
		projectId: string,
		data: ExecutionCreate,
	): Promise<Execution> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.POST("/api/v1/projects/{project_id}/executions", {
					params: { path: { project_id: projectId } },
					body: data,
				}),
			),
		);
	},

	list: async (
		projectId: string,
		params?: {
			status?: string;
			execution_type?: string;
			limit?: number;
			offset?: number;
		},
	): Promise<{ executions: Execution[]; total: number }> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.GET("/api/v1/projects/{project_id}/executions", {
					params: {
						path: { project_id: projectId },
						query: params,
					},
				}),
			),
		);
	},

	get: async (projectId: string, executionId: string): Promise<Execution> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.GET(
					"/api/v1/projects/{project_id}/executions/{execution_id}",
					{
						params: {
							path: {
								project_id: projectId,
								execution_id: executionId,
							},
						},
					},
				),
			),
		);
	},

	start: async (
		projectId: string,
		executionId: string,
	): Promise<{ started: boolean; execution_id: string }> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.POST(
					"/api/v1/projects/{project_id}/executions/{execution_id}/start",
					{
						params: {
							path: {
								project_id: projectId,
								execution_id: executionId,
							},
						},
					},
				),
			),
		);
	},

	complete: async (
		projectId: string,
		executionId: string,
		data: ExecutionComplete,
	): Promise<{ completed: boolean; execution_id: string }> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.POST(
					"/api/v1/projects/{project_id}/executions/{execution_id}/complete",
					{
						params: {
							path: {
								project_id: projectId,
								execution_id: executionId,
							},
						},
						body: data,
					},
				),
			),
		);
	},

	listArtifacts: async (
		projectId: string,
		executionId: string,
		artifactType?: string,
	): Promise<{ artifacts: ExecutionArtifact[]; total: number }> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.GET(
					"/api/v1/projects/{project_id}/executions/{execution_id}/artifacts",
					{
						params: {
							path: {
								project_id: projectId,
								execution_id: executionId,
							},
							query: { artifact_type: artifactType },
						},
					},
				),
			),
		);
	},

	downloadArtifact: (
		projectId: string,
		executionId: string,
		artifactId: string,
	): string => {
		return `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/projects/${projectId}/executions/${executionId}/artifacts/${artifactId}/download`;
	},

	getConfig: async (projectId: string): Promise<ExecutionEnvironmentConfig> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.GET("/api/v1/projects/{project_id}/execution-config", {
					params: { path: { project_id: projectId } },
				}),
			),
		);
	},

	updateConfig: async (
		projectId: string,
		data: ExecutionEnvironmentConfigUpdate,
	): Promise<ExecutionEnvironmentConfig> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.PUT("/api/v1/projects/{project_id}/execution-config", {
					params: { path: { project_id: projectId } },
					body: data,
				}),
			),
		);
	},
};
