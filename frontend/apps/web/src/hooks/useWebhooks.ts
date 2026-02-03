import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	WebhookIntegration,
	WebhookLog,
	WebhookProvider,
	WebhookStats,
	WebhookStatus,
} from "@tracertm/types";
import client from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformWebhook(data: Record<string, unknown>): WebhookIntegration {
	return {
		apiKey: data["api_key"],
		autoCompleteRun: data["auto_complete_run"],
		autoCreateRun: data["auto_create_run"],
		callbackHeaders: data["callback_headers"],
		callbackUrl: data["callback_url"],
		createdAt: data["created_at"],
		defaultSuiteId: data["default_suite_id"],
		description: data["description"],
		enabledEvents: data["enabled_events"],
		eventFilters: data["event_filters"],
		failedRequests: data["failed_requests"],
		id: data["id"],
		lastErrorMessage: data["last_error_message"],
		lastFailureAt: data["last_failure_at"],
		lastRequestAt: data["last_request_at"],
		lastSuccessAt: data["last_success_at"],
		metadata: data["webhook_metadata"],
		name: data.name,
		projectId: data["project_id"],
		provider: data["provider"],
		rateLimitPerMinute: data["rate_limit_per_minute"],
		status: data.status,
		successfulRequests: data["successful_requests"],
		totalRequests: data["total_requests"],
		updatedAt: data["updated_at"],
		verifySignatures: data["verify_signatures"],
		version: data["version"],
		webhookSecret: data["webhook_secret"],
	};
}

function transformWebhookLog(data: Record<string, unknown>): WebhookLog {
	return {
		createdAt: data["created_at"],
		errorMessage: data["error_message"],
		eventType: data["event_type"],
		httpMethod: data["http_method"],
		id: data["id"],
		payloadSizeBytes: data["payload_size_bytes"],
		processingTimeMs: data["processing_time_ms"],
		requestBodyPreview: data["request_body_preview"],
		requestHeaders: data["request_headers"],
		requestId: data["request_id"],
		resultsSubmitted: data["results_submitted"],
		sourceIp: data["source_ip"],
		statusCode: data["status_code"],
		success: data["success"],
		testRunId: data["test_run_id"],
		userAgent: data["user_agent"],
		webhookId: data["webhook_id"],
	};
}

interface WebhookFilters {
	projectId: string;
	provider?: WebhookProvider | undefined;
	status?: WebhookStatus | undefined;
	skip?: number | undefined;
	limit?: number | undefined;
}

async function fetchWebhooks(
	filters: WebhookFilters,
): Promise<{ webhooks: WebhookIntegration[]; total: number }> {
	const params = new URLSearchParams();
	params.set("project_id", filters.projectId);
	if (filters.provider) {
		params.set("provider", filters.provider);
	}
	if (filters.status) {
		params.set("status", filters.status);
	}
	if (filters.skip !== undefined) {
		params.set("skip", String(filters.skip));
	}
	if (filters.limit !== undefined) {
		params.set("limit", String(filters.limit));
	}

	const res = await fetch(`${API_URL}/api/v1/webhooks?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
			...getAuthHeaders(),
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch webhooks: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		total: data["total"] || 0,
		webhooks: (data["webhooks"] || []).map(transformWebhook),
	};
}

async function fetchWebhook(id: string): Promise<WebhookIntegration> {
	const res = await fetch(`${API_URL}/api/v1/webhooks/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) {
		throw new Error("Failed to fetch webhook");
	}
	const data = await res.json();
	return transformWebhook(data);
}

export interface CreateWebhookData {
	projectId: string;
	name: string;
	description?: string;
	provider?: WebhookProvider;
	enabledEvents?: string[];
	eventFilters?: Record<string, unknown>;
	callbackUrl?: string;
	callbackHeaders?: Record<string, string>;
	defaultSuiteId?: string;
	rateLimitPerMinute?: number;
	autoCreateRun?: boolean;
	autoCompleteRun?: boolean;
	verifySignatures?: boolean;
	metadata?: Record<string, unknown>;
}

async function createWebhook(
	data: CreateWebhookData,
): Promise<WebhookIntegration> {
	const res = await fetch(`${API_URL}/api/v1/webhooks`, {
		body: JSON.stringify({
			auto_complete_run: data["autoCompleteRun"] ?? true,
			auto_create_run: data["autoCreateRun"] ?? true,
			callback_headers: data["callbackHeaders"],
			callback_url: data["callbackUrl"],
			default_suite_id: data["defaultSuiteId"],
			description: data["description"],
			enabled_events: data["enabledEvents"],
			event_filters: data["eventFilters"],
			metadata: data["metadata"],
			name: data.name,
			project_id: data["projectId"],
			provider: data["provider"] || "custom",
			rate_limit_per_minute: data["rateLimitPerMinute"] ?? 60,
			verify_signatures: data["verifySignatures"] ?? true,
		}),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "POST",
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to create webhook: ${res.status} ${errorText}`);
	}
	const result = await res.json();
	return transformWebhook(result);
}

interface UpdateWebhookData {
	name?: string;
	description?: string;
	enabledEvents?: string[];
	eventFilters?: Record<string, unknown>;
	callbackUrl?: string;
	callbackHeaders?: Record<string, string>;
	defaultSuiteId?: string;
	rateLimitPerMinute?: number;
	autoCreateRun?: boolean;
	autoCompleteRun?: boolean;
	verifySignatures?: boolean;
	metadata?: Record<string, unknown>;
}

async function updateWebhook(
	id: string,
	data: UpdateWebhookData,
): Promise<WebhookIntegration> {
	const payload: Record<string, unknown> = {};
	if (data.name !== undefined) {
		payload.name = data.name;
	}
	if (data["description"] !== undefined) {
		payload["description"] = data["description"];
	}
	if (data["enabledEvents"] !== undefined) {
		payload["enabled_events"] = data["enabledEvents"];
	}
	if (data["eventFilters"] !== undefined) {
		payload["event_filters"] = data["eventFilters"];
	}
	if (data["callbackUrl"] !== undefined) {
		payload["callback_url"] = data["callbackUrl"];
	}
	if (data["callbackHeaders"] !== undefined) {
		payload["callback_headers"] = data["callbackHeaders"];
	}
	if (data["defaultSuiteId"] !== undefined) {
		payload["default_suite_id"] = data["defaultSuiteId"];
	}
	if (data["rateLimitPerMinute"] !== undefined) {
		payload["rate_limit_per_minute"] = data["rateLimitPerMinute"];
	}
	if (data["autoCreateRun"] !== undefined) {
		payload["auto_create_run"] = data["autoCreateRun"];
	}
	if (data["autoCompleteRun"] !== undefined) {
		payload["auto_complete_run"] = data["autoCompleteRun"];
	}
	if (data["verifySignatures"] !== undefined) {
		payload["verify_signatures"] = data["verifySignatures"];
	}
	if (data["metadata"] !== undefined) {
		payload["metadata"] = data["metadata"];
	}

	const res = await fetch(`${API_URL}/api/v1/webhooks/${id}`, {
		body: JSON.stringify(payload),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "PUT",
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to update webhook: ${res.status} ${errorText}`);
	}
	const result = await res.json();
	return transformWebhook(result);
}

async function setWebhookStatus(
	id: string,
	status: WebhookStatus,
): Promise<{ id: string; status: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/webhooks/${id}/status`, {
		body: JSON.stringify({ status }),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "POST",
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to update status: ${res.status} ${errorText}`);
	}
	return res.json();
}

async function regenerateSecret(
	id: string,
): Promise<{ id: string; webhookSecret: string; version: number }> {
	const res = await fetch(
		`${API_URL}/api/v1/webhooks/${id}/regenerate-secret`,
		{
			headers: getAuthHeaders(),
			method: "POST",
		},
	);
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to regenerate secret: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		id: data["id"],
		version: data["version"],
		webhookSecret: data["webhook_secret"],
	};
}

async function deleteWebhook(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/webhooks/${id}`, {
		headers: getAuthHeaders(),
		method: "DELETE",
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to delete webhook: ${res.status} ${errorText}`);
	}
}

interface WebhookLogFilters {
	webhookId: string;
	success?: boolean;
	eventType?: string;
	skip?: number;
	limit?: number;
}

async function fetchWebhookLogs(
	filters: WebhookLogFilters,
): Promise<{ logs: WebhookLog[]; total: number }> {
	const params = new URLSearchParams();
	if (filters.success !== undefined) {
		params.set("success", String(filters.success));
	}
	if (filters.eventType) {
		params.set("event_type", filters.eventType);
	}
	if (filters.skip !== undefined) {
		params.set("skip", String(filters.skip));
	}
	if (filters.limit !== undefined) {
		params.set("limit", String(filters.limit));
	}

	const res = await fetch(
		`${API_URL}/api/v1/webhooks/${filters.webhookId}/logs?${params}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) {
		throw new Error("Failed to fetch webhook logs");
	}
	const data = await res.json();
	return {
		logs: (data["logs"] || []).map(transformWebhookLog),
		total: data["total"] || 0,
	};
}

async function fetchWebhookStats(projectId: string): Promise<WebhookStats> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/webhooks/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) {
		throw new Error("Failed to fetch webhook stats");
	}
	const data = await res.json();
	return {
		byProvider: data["by_provider"],
		byStatus: data["by_status"],
		failedRequests: data["failed_requests"],
		projectId: data["project_id"],
		successfulRequests: data["successful_requests"],
		total: data["total"],
		totalRequests: data["total_requests"],
	};
}

// ==================== HOOKS ====================

export function useWebhooks(filters: WebhookFilters) {
	return useQuery({
		enabled: !!filters.projectId,
		queryFn: () => fetchWebhooks(filters),
		queryKey: ["webhooks", filters],
	});
}

export function useWebhook(id: string | undefined) {
	return useQuery({
		enabled: !!id,
		queryFn: () => fetchWebhook(id!),
		queryKey: ["webhook", id],
	});
}

export function useCreateWebhook() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createWebhook,
		onSuccess: (data) => {
			undefined;
			undefined;
		},
	});
}

export function useUpdateWebhook() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: UpdateWebhookData }) =>
			updateWebhook(id, data),
		onSuccess: (data) => {
			undefined;
			undefined;
		},
	});
}

export function useSetWebhookStatus() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, status }: { id: string; status: WebhookStatus }) =>
			setWebhookStatus(id, status),
		onSuccess: (data) => {
			undefined;
			undefined;
		},
	});
}

export function useRegenerateWebhookSecret() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: regenerateSecret,
		onSuccess: (data) => {
			undefined;
		},
	});
}

export function useDeleteWebhook() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteWebhook,
		onSuccess: () => {
			undefined;
		},
	});
}

export function useWebhookLogs(filters: WebhookLogFilters) {
	return useQuery({
		enabled: !!filters.webhookId,
		queryFn: () => fetchWebhookLogs(filters),
		queryKey: ["webhookLogs", filters],
	});
}

export function useWebhookStats(projectId: string | undefined) {
	return useQuery({
		enabled: !!projectId,
		queryFn: () => fetchWebhookStats(projectId!),
		queryKey: ["webhookStats", projectId],
	});
}
