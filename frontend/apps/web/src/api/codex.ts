// Codex Agent API endpoints

import { apiClient, handleApiResponse, safeApiCall } from "./client";

/**
 * Input data for Codex agent tasks
 */
export interface CodexInputData {
	[key: string]: string | number | boolean | object | null | undefined;
}

/**
 * Output data from Codex agent tasks
 */
export interface CodexOutputData {
	[key: string]: string | number | boolean | object | null | undefined;
}

export interface CodexAgentTask {
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

export interface CodexReviewRequest {
	artifact_id: string;
	prompt?: string;
	execution_id?: string;
	max_frames?: number;
}

export interface CodexAuthStatus {
	available: boolean;
	version?: string;
	authenticated: boolean;
	status: string;
}

export const codexApi = {
	reviewImage: async (
		projectId: string,
		data: CodexReviewRequest,
	): Promise<CodexAgentTask> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.POST("/api/v1/projects/{project_id}/codex/review-image", {
					params: { path: { project_id: projectId } },
					body: data,
				}),
			),
		);
	},

	reviewVideo: async (
		projectId: string,
		data: CodexReviewRequest,
	): Promise<CodexAgentTask> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.POST("/api/v1/projects/{project_id}/codex/review-video", {
					params: { path: { project_id: projectId } },
					body: data,
				}),
			),
		);
	},

	listInteractions: async (
		projectId: string,
		params?: {
			limit?: number;
			offset?: number;
			status?: string;
			task_type?: string;
		},
	): Promise<{ tasks: CodexAgentTask[]; total: number }> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.GET("/api/v1/projects/{project_id}/codex/interactions", {
					params: {
						path: { project_id: projectId },
						query: params,
					},
				}),
			),
		);
	},

	getAuthStatus: async (projectId: string): Promise<CodexAuthStatus> => {
		return handleApiResponse(
			safeApiCall(
				apiClient.GET("/api/v1/projects/{project_id}/codex/auth-status", {
					params: { path: { project_id: projectId } },
				}),
			),
		);
	},
};
