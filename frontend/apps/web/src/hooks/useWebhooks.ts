import type { UseMutationResult, UseQueryResult } from '@tanstack/react-query';

import { useMutation, useQuery } from '@tanstack/react-query';

import type {
  WebhookIntegration,
  WebhookLog,
  WebhookProvider,
  WebhookStats,
  WebhookStatus,
} from '@tracertm/types';

import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

const toNumber = (value: unknown, fallback: number): number =>
  value === undefined ? fallback : Number(value);

const toString = (value: unknown, fallback: string): string =>
  value === undefined ? fallback : String(value);

const toStringOrUndefined = (value: unknown): string | undefined =>
  value === undefined ? undefined : String(value);

const toRecordOrUndefined = <T extends Record<string, unknown>>(value: unknown): T | undefined =>
  value === undefined ? undefined : (value as T);

const toStringArrayOrUndefined = (value: unknown): string[] | undefined =>
  value === undefined ? undefined : (value as string[]);

const toBoolean = (value: unknown): boolean => value === true;

// Transform API response (snake_case) to frontend format (camelCase)
function transformWebhook(data: Record<string, unknown>): WebhookIntegration {
  return {
    apiKey: toString(data['api_key'], ''),
    autoCompleteRun: toBoolean(data['auto_complete_run']),
    autoCreateRun: toBoolean(data['auto_create_run']),
    callbackHeaders: toRecordOrUndefined<Record<string, string>>(data['callback_headers']),
    callbackUrl: toString(data['callback_url'], ''),
    createdAt: toString(data['created_at'], ''),
    defaultSuiteId: toString(data['default_suite_id'], ''),
    description: toStringOrUndefined(data['description']),
    enabledEvents: toStringArrayOrUndefined(data['enabled_events']),
    eventFilters: toRecordOrUndefined<Record<string, unknown>>(data['event_filters']),
    failedRequests: toNumber(data['failed_requests'], 0),
    id: String(data['id']),
    lastErrorMessage: toStringOrUndefined(data['last_error_message']),
    lastFailureAt: toStringOrUndefined(data['last_failure_at']),
    lastRequestAt: toString(data['last_request_at'], ''),
    lastSuccessAt: toStringOrUndefined(data['last_success_at']),
    metadata: toRecordOrUndefined<Record<string, unknown>>(data['webhook_metadata']),
    name: String(data['name']),
    projectId: String(data['project_id']),
    provider: data['provider'] as WebhookProvider,
    rateLimitPerMinute: toNumber(data['rate_limit_per_minute'], 0),
    status: data['status'] as WebhookStatus,
    successfulRequests: toNumber(data['successful_requests'], 0),
    totalRequests: toNumber(data['total_requests'], 0),
    updatedAt: toString(data['updated_at'], ''),
    verifySignatures: toBoolean(data['verify_signatures']),
    version: toNumber(data['version'], 0),
    webhookSecret: toString(data['webhook_secret'], ''),
  };
}

function transformWebhookLog(data: Record<string, unknown>): WebhookLog {
  return {
    createdAt: String(data['created_at']),
    errorMessage: toStringOrUndefined(data['error_message']),
    eventType: String(data['event_type']),
    httpMethod: String(data['http_method']),
    id: String(data['id']),
    payloadSizeBytes: data['payload_size_bytes'] as number | undefined,
    processingTimeMs: toNumber(data['processing_time_ms'], 0),
    requestBodyPreview: toStringOrUndefined(data['request_body_preview']),
    requestHeaders: toRecordOrUndefined<Record<string, unknown>>(data['request_headers']),
    requestId: toString(data['request_id'], ''),
    resultsSubmitted: Number(data['results_submitted'] ?? 0),
    sourceIp: toStringOrUndefined(data['source_ip']),
    statusCode: toNumber(data['status_code'], 0),
    success: toBoolean(data['success']),
    testRunId: toStringOrUndefined(data['test_run_id']),
    userAgent: toStringOrUndefined(data['user_agent']),
    webhookId: String(data['webhook_id']),
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
  params.set('project_id', filters.projectId);
  if (filters.provider !== undefined) {
    params.set('provider', filters.provider);
  }
  if (filters.status !== undefined) {
    params.set('status', filters.status);
  }
  if (filters.skip !== undefined) {
    params.set('skip', String(filters.skip));
  }
  if (filters.limit !== undefined) {
    params.set('limit', String(filters.limit));
  }

  const res = await fetch(`${API_URL}/api/v1/webhooks?${params}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch webhooks: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  const webhooks = (data['webhooks'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    total: Number(data['total'] ?? 0),
    webhooks: webhooks.map((item) => transformWebhook(item)),
  };
}

async function fetchWebhook(id: string): Promise<WebhookIntegration> {
  const res = await fetch(`${API_URL}/api/v1/webhooks/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch webhook');
  }
  const data = await res.json();
  return transformWebhook(data);
}

interface CreateWebhookData {
  projectId: string;
  name: string;
  description?: string | undefined;
  provider?: WebhookProvider | undefined;
  enabledEvents?: string[] | undefined;
  eventFilters?: Record<string, unknown> | undefined;
  callbackUrl?: string | undefined;
  callbackHeaders?: Record<string, string> | undefined;
  defaultSuiteId?: string | undefined;
  rateLimitPerMinute?: number | undefined;
  autoCreateRun?: boolean | undefined;
  autoCompleteRun?: boolean | undefined;
  verifySignatures?: boolean | undefined;
  metadata?: Record<string, unknown> | undefined;
}

async function createWebhook(data: CreateWebhookData): Promise<WebhookIntegration> {
  const res = await fetch(`${API_URL}/api/v1/webhooks`, {
    body: JSON.stringify({
      auto_complete_run: data['autoCompleteRun'] ?? true,
      auto_create_run: data['autoCreateRun'] ?? true,
      callback_headers: data['callbackHeaders'],
      callback_url: data['callbackUrl'],
      default_suite_id: data['defaultSuiteId'],
      description: data['description'],
      enabled_events: data['enabledEvents'],
      event_filters: data['eventFilters'],
      metadata: data['metadata'],
      name: data.name,
      project_id: data['projectId'],
      provider: data['provider'] ?? 'custom',
      rate_limit_per_minute: data['rateLimitPerMinute'] ?? 60,
      verify_signatures: data['verifySignatures'] ?? true,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to create webhook: ${res.status} ${errorText}`);
  }
  const result = await res.json();
  return transformWebhook(result);
}

interface UpdateWebhookData {
  name?: string | undefined;
  description?: string | undefined;
  enabledEvents?: string[] | undefined;
  eventFilters?: Record<string, unknown> | undefined;
  callbackUrl?: string | undefined;
  callbackHeaders?: Record<string, string> | undefined;
  defaultSuiteId?: string | undefined;
  rateLimitPerMinute?: number | undefined;
  autoCreateRun?: boolean | undefined;
  autoCompleteRun?: boolean | undefined;
  verifySignatures?: boolean | undefined;
  metadata?: Record<string, unknown> | undefined;
}

const setPayload = <T>(
  payload: Record<string, unknown>,
  key: string,
  value: T | undefined,
): void => {
  if (value !== undefined) {
    payload[key] = value;
  }
};

async function updateWebhook(id: string, data: UpdateWebhookData): Promise<WebhookIntegration> {
  const payload: Record<string, unknown> = {};
  setPayload(payload, 'name', data['name']);
  setPayload(payload, 'description', data['description']);
  setPayload(payload, 'enabled_events', data['enabledEvents']);
  setPayload(payload, 'event_filters', data['eventFilters']);
  setPayload(payload, 'callback_url', data['callbackUrl']);
  setPayload(payload, 'callback_headers', data['callbackHeaders']);
  setPayload(payload, 'default_suite_id', data['defaultSuiteId']);
  setPayload(payload, 'rate_limit_per_minute', data['rateLimitPerMinute']);
  setPayload(payload, 'auto_create_run', data['autoCreateRun']);
  setPayload(payload, 'auto_complete_run', data['autoCompleteRun']);
  setPayload(payload, 'verify_signatures', data['verifySignatures']);
  setPayload(payload, 'metadata', data['metadata']);

  const res = await fetch(`${API_URL}/api/v1/webhooks/${id}`, {
    body: JSON.stringify(payload),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
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
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
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
  const res = await fetch(`${API_URL}/api/v1/webhooks/${id}/regenerate-secret`, {
    headers: getAuthHeaders(),
    method: 'POST',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to regenerate secret: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    id: data['id'],
    version: data['version'],
    webhookSecret: data['webhook_secret'],
  };
}

async function deleteWebhook(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/webhooks/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to delete webhook: ${res.status} ${errorText}`);
  }
}

interface WebhookLogFilters {
  webhookId: string;
  success?: boolean | undefined;
  eventType?: string | undefined;
  skip?: number | undefined;
  limit?: number | undefined;
}

async function fetchWebhookLogs(
  filters: WebhookLogFilters,
): Promise<{ logs: WebhookLog[]; total: number }> {
  const params = new URLSearchParams();
  if (filters.success !== undefined) {
    params.set('success', String(filters.success));
  }
  if (filters.eventType !== undefined && filters.eventType !== '') {
    params.set('event_type', filters.eventType);
  }
  if (filters.skip !== undefined) {
    params.set('skip', String(filters.skip));
  }
  if (filters.limit !== undefined) {
    params.set('limit', String(filters.limit));
  }

  const res = await fetch(`${API_URL}/api/v1/webhooks/${filters.webhookId}/logs?${params}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch webhook logs');
  }
  const data = await res.json();
  const logs = (data['logs'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    logs: logs.map((item) => transformWebhookLog(item)),
    total: Number(data['total'] ?? 0),
  };
}

async function fetchWebhookStats(projectId: string): Promise<WebhookStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/webhooks/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch webhook stats');
  }
  const data = await res.json();
  return {
    byProvider: data['by_provider'],
    byStatus: data['by_status'],
    failedRequests: data['failed_requests'],
    projectId: data['project_id'],
    successfulRequests: data['successful_requests'],
    total: data['total'],
    totalRequests: data['total_requests'],
  };
}

// ==================== HOOKS ====================

function useWebhooks(
  filters: WebhookFilters,
): UseQueryResult<{ webhooks: WebhookIntegration[]; total: number }> {
  return useQuery({
    enabled: filters.projectId !== '',
    queryFn: async () => fetchWebhooks(filters),
    queryKey: ['webhooks', JSON.stringify(filters)],
  });
}

function useWebhook(id = ''): UseQueryResult<WebhookIntegration> {
  return useQuery({
    enabled: id !== '',
    queryFn: async () => fetchWebhook(id),
    queryKey: ['webhook', id],
  });
}

function useCreateWebhook(): UseMutationResult<WebhookIntegration, Error, CreateWebhookData> {
  return useMutation({
    mutationFn: createWebhook,
  });
}

function useUpdateWebhook(): UseMutationResult<
  WebhookIntegration,
  Error,
  { id: string; data: UpdateWebhookData }
> {
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateWebhookData }) =>
      updateWebhook(id, data),
  });
}

function useSetWebhookStatus(): UseMutationResult<
  { id: string; status: string; version: number },
  Error,
  { id: string; status: WebhookStatus }
> {
  return useMutation({
    mutationFn: async ({ id, status }: { id: string; status: WebhookStatus }) =>
      setWebhookStatus(id, status),
  });
}

function useRegenerateWebhookSecret(): UseMutationResult<
  { id: string; webhookSecret: string; version: number },
  Error,
  string
> {
  return useMutation({
    mutationFn: regenerateSecret,
  });
}

function useDeleteWebhook(): UseMutationResult<void, Error, string> {
  return useMutation({
    mutationFn: deleteWebhook,
  });
}

function useWebhookLogs(
  filters: WebhookLogFilters,
): UseQueryResult<{ logs: WebhookLog[]; total: number }> {
  return useQuery({
    enabled: filters.webhookId !== '',
    queryFn: async () => fetchWebhookLogs(filters),
    queryKey: ['webhookLogs', JSON.stringify(filters)],
  });
}

function useWebhookStats(projectId = ''): UseQueryResult<WebhookStats> {
  return useQuery({
    enabled: projectId !== '',
    queryFn: async () => fetchWebhookStats(projectId),
    queryKey: ['webhookStats', projectId],
  });
}

export type { CreateWebhookData };
export {
  useCreateWebhook,
  useDeleteWebhook,
  useRegenerateWebhookSecret,
  useSetWebhookStatus,
  useUpdateWebhook,
  useWebhook,
  useWebhookLogs,
  useWebhookStats,
  useWebhooks,
};
