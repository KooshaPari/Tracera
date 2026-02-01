import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	WebhookIntegration,
	WebhookLog,
	WebhookProvider,
	WebhookStats,
	WebhookStatus,
} from "@tracertm/types";
import { getAuthHeaders } from "@/api/client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformWebhook(data: any): WebhookIntegration {
	return {
		id: data.id,
		projectId: data.project_id,
		name: data.name,
		description: data.description,
		provider: data.provider,
		status: data.status,
		webhookSecret: data.webhook_secret,
		apiKey: data.api_key,
		enabledEvents: data.enabled_events,
		eventFilters: data.event_filters,
		callbackUrl: data.callback_url,
		callbackHeaders: data.callback_headers,
		defaultSuiteId: data.default_suite_id,
		rateLimitPerMinute: data.rate_limit_per_minute,
		autoCreateRun: data.auto_create_run,
		autoCompleteRun: data.auto_complete_run,
		verifySignatures: data.verify_signatures,
		totalRequests: data.total_requests,
		successfulRequests: data.successful_requests,
		failedRequests: data.failed_requests,
		lastRequestAt: data.last_request_at,
		lastSuccessAt: data.last_success_at,
		lastFailureAt: data.last_failure_at,
		lastErrorMessage: data.last_error_message,
		metadata: data.webhook_metadata,
		version: data.version,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
	};
}

function transformWebhookLog(data: any): WebhookLog {
	return {
		id: data.id,
		webhookId: data.webhook_id,
		requestId: data.request_id,
		eventType: data.event_type,
		httpMethod: data.http_method,
		sourceIp: data.source_ip,
		userAgent: data.user_agent,
		requestHeaders: data.request_headers,
		requestBodyPreview: data.request_body_preview,
		payloadSizeBytes: data.payload_size_bytes,
		success: data.success,
		statusCode: data.status_code,
		errorMessage: data.error_message,
		processingTimeMs: data.processing_time_ms,
		testRunId: data.test_run_id,
		resultsSubmitted: data.results_submitted,
		createdAt: data.created_at,
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
	if (filters.provider) params.set("provider", filters.provider);
	if (filters.status) params.set("status", filters.status);
	if (filters.skip !== undefined) params.set("skip", String(filters.skip));
	if (filters.limit !== undefined) params.set("limit", String(filters.limit));

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
		webhooks: (data.webhooks || []).map(transformWebhook),
		total: data.total || 0,
	};
}

async function fetchWebhook(id: string): Promise<WebhookIntegration> {
	const res = await fetch(`${API_URL}/api/v1/webhooks/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch webhook");
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
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			project_id: data.projectId,
			name: data.name,
			description: data.description,
			provider: data.provider || "custom",
			enabled_events: data.enabledEvents,
			event_filters: data.eventFilters,
			callback_url: data.callbackUrl,
			callback_headers: data.callbackHeaders,
			default_suite_id: data.defaultSuiteId,
			rate_limit_per_minute: data.rateLimitPerMinute ?? 60,
			auto_create_run: data.autoCreateRun ?? true,
			auto_complete_run: data.autoCompleteRun ?? true,
			verify_signatures: data.verifySignatures ?? true,
			metadata: data.metadata,
		}),
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
	if (data.name !== undefined) payload.name = data.name;
	if (data.description !== undefined) payload.description = data.description;
	if (data.enabledEvents !== undefined)
		payload.enabled_events = data.enabledEvents;
	if (data.eventFilters !== undefined)
		payload.event_filters = data.eventFilters;
	if (data.callbackUrl !== undefined) payload.callback_url = data.callbackUrl;
	if (data.callbackHeaders !== undefined)
		payload.callback_headers = data.callbackHeaders;
	if (data.defaultSuiteId !== undefined)
		payload.default_suite_id = data.defaultSuiteId;
	if (data.rateLimitPerMinute !== undefined)
		payload.rate_limit_per_minute = data.rateLimitPerMinute;
	if (data.autoCreateRun !== undefined)
		payload.auto_create_run = data.autoCreateRun;
	if (data.autoCompleteRun !== undefined)
		payload.auto_complete_run = data.autoCompleteRun;
	if (data.verifySignatures !== undefined)
		payload.verify_signatures = data.verifySignatures;
	if (data.metadata !== undefined) payload.metadata = data.metadata;

	const res = await fetch(`${API_URL}/api/v1/webhooks/${id}`, {
		method: "PUT",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify(payload),
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
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({ status }),
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
			method: "POST",
			headers: getAuthHeaders(),
		},
	);
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to regenerate secret: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		id: data.id,
		webhookSecret: data.webhook_secret,
		version: data.version,
	};
}

async function deleteWebhook(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/webhooks/${id}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
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
	if (filters.success !== undefined)
		params.set("success", String(filters.success));
	if (filters.eventType) params.set("event_type", filters.eventType);
	if (filters.skip !== undefined) params.set("skip", String(filters.skip));
	if (filters.limit !== undefined) params.set("limit", String(filters.limit));

	const res = await fetch(
		`${API_URL}/api/v1/webhooks/${filters.webhookId}/logs?${params}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch webhook logs");
	const data = await res.json();
	return {
		logs: (data.logs || []).map(transformWebhookLog),
		total: data.total || 0,
	};
}

async function fetchWebhookStats(projectId: string): Promise<WebhookStats> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/webhooks/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch webhook stats");
	const data = await res.json();
	return {
		projectId: data.project_id,
		total: data.total,
		byStatus: data.by_status,
		byProvider: data.by_provider,
		totalRequests: data.total_requests,
		successfulRequests: data.successful_requests,
		failedRequests: data.failed_requests,
	};
}

// ==================== HOOKS ====================

export function useWebhooks(filters: WebhookFilters) {
	return useQuery({
		queryKey: ["webhooks", filters],
		queryFn: () => fetchWebhooks(filters),
		enabled: !!filters.projectId,
	});
}

export function useWebhook(id: string | undefined) {
	return useQuery({
		queryKey: ["webhook", id],
		queryFn: () => fetchWebhook(id!),
		enabled: !!id,
	});
}

export function useCreateWebhook() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createWebhook,
		onSuccess: (data) => {
			queryClient.invalidateQueries({ queryKey: ["webhooks"] });
			queryClient.invalidateQueries({
				queryKey: ["webhookStats", data.projectId],
			});
		},
	});
}

export function useUpdateWebhook() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: UpdateWebhookData }) =>
			updateWebhook(id, data),
		onSuccess: (data) => {
			queryClient.invalidateQueries({ queryKey: ["webhooks"] });
			queryClient.invalidateQueries({ queryKey: ["webhook", data.id] });
		},
	});
}

export function useSetWebhookStatus() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, status }: { id: string; status: WebhookStatus }) =>
			setWebhookStatus(id, status),
		onSuccess: (data) => {
			queryClient.invalidateQueries({ queryKey: ["webhooks"] });
			queryClient.invalidateQueries({ queryKey: ["webhook", data.id] });
		},
	});
}

export function useRegenerateWebhookSecret() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: regenerateSecret,
		onSuccess: (data) => {
			queryClient.invalidateQueries({ queryKey: ["webhook", data.id] });
		},
	});
}

export function useDeleteWebhook() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteWebhook,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["webhooks"] });
		},
	});
}

export function useWebhookLogs(filters: WebhookLogFilters) {
	return useQuery({
		queryKey: ["webhookLogs", filters],
		queryFn: () => fetchWebhookLogs(filters),
		enabled: !!filters.webhookId,
	});
}

export function useWebhookStats(projectId: string | undefined) {
	return useQuery({
		queryKey: ["webhookStats", projectId],
		queryFn: () => fetchWebhookStats(projectId!),
		enabled: !!projectId,
	});
}
