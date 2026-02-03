import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	GitHubIssue,
	GitHubProject,
	GitHubRepo,
	IntegrationCredential,
	IntegrationMapping,
	IntegrationProvider,
	IntegrationStats,
	LinearIssue,
	LinearProject,
	LinearTeam,
	MappingDirection,
	SyncConflict,
	SyncLog,
	SyncQueueItem,
	SyncStatusSummary,
} from "@tracertm/types";
import client from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformCredential(
	data: Record<string, unknown>,
): IntegrationCredential {
	return {
		createdAt: data["created_at"] as string,
		credentialType: data[
			"credential_type"
		] as IntegrationCredential["credentialType"],
		expiresAt: data["expires_at"] as string | undefined,
		id: data["id"] as string,
		lastValidatedAt: data["last_validated_at"] as string | undefined,
		projectId: (data["project_id"] as string | undefined) || undefined,
		provider: data["provider"] as IntegrationProvider,
		providerMetadata: data["provider_metadata"] as
			| Record<string, unknown>
			| undefined,
		providerUserId: data["provider_user_id"] as string | undefined,
		scopes: (data["scopes"] as string[]) || [],
		status: data["status"] as IntegrationCredential["status"],
		updatedAt: data["updated_at"] as string,
		validationError: data["validation_error"] as string | undefined,
	};
}

function transformMapping(data: Record<string, unknown>): IntegrationMapping {
	return {
		createdAt: data["created_at"] as string,
		credentialId: data["credential_id"] as string,
		direction: data["direction"] as MappingDirection,
		externalId: data["external_id"] as string,
		externalKey: data["external_key"] as string | undefined,
		externalType: data["external_type"] as string,
		externalUrl: data["external_url"] as string | undefined,
		externalVersion: data["external_version"] as string | undefined,
		fieldMappings: data["field_mappings"] as Record<string, string> | undefined,
		fieldResolutionRules: data["field_resolution_rules"] as
			| Record<string, unknown>
			| undefined,
		id: data["id"] as string,
		lastSyncError: data["last_sync_error"] as string | undefined,
		lastSyncStatus: data["last_sync_status"] as string | undefined,
		lastSyncedAt: data["last_synced_at"] as string | undefined,
		localItemId: data["local_item_id"] as string,
		localItemType: data["local_item_type"] as string,
		localVersion: data["local_version"] as number | undefined,
		mappingMetadata: data["mapping_metadata"] as
			| Record<string, unknown>
			| undefined,
		provider: data["provider"] as IntegrationProvider,
		status: data["status"] as IntegrationMapping["status"],
		syncEnabled: data["sync_enabled"] as boolean,
		updatedAt: data["updated_at"] as string,
	};
}

function transformSyncQueueItem(data: Record<string, unknown>): SyncQueueItem {
	return {
		completedAt: data["completed_at"] as string | undefined,
		createdAt: data["created_at"] as string,
		credentialId: data["credential_id"] as string,
		direction: data["direction"] as MappingDirection,
		errorMessage: data["error_message"] as string | undefined,
		eventType: data["event_type"] as string,
		id: data["id"] as string,
		mappingId: data["mapping_id"] as string | undefined,
		maxRetries: data["max_retries"] as number,
		priority: data["priority"] as number,
		provider: data["provider"] as IntegrationProvider,
		retryCount: data["retry_count"] as number,
		scheduledAt: data["scheduled_at"] as string,
		startedAt: data["started_at"] as string | undefined,
		status: data["status"] as SyncQueueItem["status"],
	};
}

function transformSyncLog(data: Record<string, unknown>): SyncLog {
	return {
		completedAt: data["completed_at"] as string | undefined,
		createdAt: data["created_at"] as string,
		credentialId: data["credential_id"] as string,
		direction: data["direction"] as MappingDirection,
		durationMs: data["duration_ms"] as number | undefined,
		errorMessage: data["error_message"] as string | undefined,
		eventType: data["event_type"] as string,
		id: data["id"] as string,
		itemsFailed: data["items_failed"] as number,
		itemsProcessed: data["items_processed"] as number,
		itemsSkipped: data["items_skipped"] as number,
		mappingId: data["mapping_id"] as string | undefined,
		provider: data["provider"] as IntegrationProvider,
		startedAt: data["started_at"] as string,
		status: data["status"] as SyncLog["status"],
	};
}

function transformConflict(data: Record<string, unknown>): SyncConflict {
	return {
		conflictType: data["conflict_type"] as SyncConflict["conflictType"],
		createdAt: data["created_at"] as string,
		externalModifiedAt: data["external_modified_at"] as string,
		externalValue: data["external_value"] as unknown,
		fieldName: data["field_name"] as string,
		id: data["id"] as string,
		localModifiedAt: data["local_modified_at"] as string,
		localValue: data["local_value"] as unknown,
		mappingId: data["mapping_id"] as string,
		provider: data["provider"] as IntegrationProvider,
		resolution: data["resolution"] as SyncConflict["resolution"] | undefined,
		resolvedAt: data["resolved_at"] as string | undefined,
		resolvedBy: data["resolved_by"] as string | undefined,
		resolvedValue: data["resolved_value"] as unknown,
		status: data["status"] as SyncConflict["status"],
	};
}

function transformSyncStatus(data: Record<string, unknown>): SyncStatusSummary {
	return {
		projectId: data["project_id"] as string,
		providers: ((data["providers"] as Record<string, unknown>[]) || []).map(
			(p: Record<string, unknown>) => ({
				lastValidated: p["last_validated"] as string | undefined,
				provider: p["provider"] as IntegrationProvider,
				status: p["status"] as string,
			}),
		),
		queue: data["queue"] as SyncStatusSummary["queue"],
		recentSyncs: (
			(data["recent_syncs"] as Record<string, unknown>[]) || []
		).map(transformSyncLog),
	};
}

function transformStats(data: Record<string, unknown>): IntegrationStats {
	const mappings = data["mappings"] as Record<string, unknown> | undefined;
	const sync = data["sync"] as Record<string, unknown> | undefined;
	const conflicts = data["conflicts"] as Record<string, unknown> | undefined;

	return {
		conflicts: {
			pending: (conflicts?.pending as number) || 0,
			resolved: (conflicts?.resolved as number) || 0,
		},
		mappings: {
			active: (mappings?.active as number) || 0,
			byProvider: (mappings?.by_provider as Record<string, number>) || {},
			total: (mappings?.total as number) || 0,
		},
		projectId: data["project_id"] as string,
		providers: ((data["providers"] as Record<string, unknown>[]) || []).map(
			(p: Record<string, unknown>) => ({
				credentialType: p["credential_type"] as string,
				provider: p["provider"] as IntegrationProvider,
				status: p["status"] as string,
			}),
		),
		sync: {
			queuePending: (sync?.queue_pending as number) || 0,
			recentSyncs: (sync?.recent_syncs as number) || 0,
			successRate: (sync?.success_rate as number) || 0,
		},
	};
}

// ==================== Credentials ====================

async function fetchCredentials(
	projectId: string,
): Promise<{ credentials: IntegrationCredential[]; total: number }> {
	const res = await fetch(
		`${API_URL}/api/v1/integrations/credentials?project_id=${projectId}`,
		{
			headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() },
		},
	);
	if (!res.ok) {
		throw new Error(`Failed to fetch credentials: ${res.status}`);
	}
	const data = await res.json();
	return {
		credentials: (data["credentials"] || []).map(transformCredential),
		total: data["total"] || 0,
	};
}

export function useCredentials(projectId: string) {
	return useQuery({
		enabled: Boolean(projectId),
		queryFn: () => fetchCredentials(projectId),
		queryKey: ["integrations", "credentials", projectId],
	});
}

export function useValidateCredential() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (credentialId: string) => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/credentials/${credentialId}/validate`,
				{
					headers: { "Content-Type": "application/json", ...getAuthHeaders() },
					method: "POST",
				},
			);
			if (!res.ok) {
				throw new Error(`Failed to validate credential: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			undefined;
		},
	});
}

export function useDeleteCredential() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (credentialId: string) => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/credentials/${credentialId}`,
				{ headers: getAuthHeaders(), method: "DELETE" },
			);
			if (!res.ok) {
				throw new Error(`Failed to delete credential: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			undefined;
		},
	});
}

// ==================== OAuth ====================

export function useStartOAuth() {
	return useMutation({
		mutationFn: async (data: {
			projectId?: string;
			provider: IntegrationProvider;
			redirectUri: string;
			scopes?: string[];
			credentialScope?: "project" | "user";
		}) => {
			const res = await fetch(`${API_URL}/api/v1/integrations/oauth/start`, {
				body: JSON.stringify({
					credential_scope: data["credentialScope"],
					project_id: data["projectId"],
					provider: data["provider"],
					redirect_uri: data["redirectUri"],
					scopes: data["scopes"],
				}),
				headers: { "Content-Type": "application/json", ...getAuthHeaders() },
				method: "POST",
			});
			if (!res.ok) {
				throw new Error(`Failed to start OAuth: ${res.status}`);
			}
			return res.json();
		},
	});
}

export function useCompleteOAuth() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (data: {
			code: string;
			state: string;
			redirectUri: string;
		}) => {
			const res = await fetch(`${API_URL}/api/v1/integrations/oauth/callback`, {
				body: JSON.stringify({
					code: data["code"],
					redirect_uri: data["redirectUri"],
					state: data["state"],
				}),
				headers: { "Content-Type": "application/json", ...getAuthHeaders() },
				method: "POST",
			});
			if (!res.ok) {
				throw new Error(`Failed to complete OAuth: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			undefined;
		},
	});
}

// ==================== Mappings ====================

async function fetchMappings(
	projectId: string,
	provider?: IntegrationProvider,
): Promise<{ mappings: IntegrationMapping[]; total: number }> {
	const params = new URLSearchParams({ project_id: projectId });
	if (provider) {
		params.set("provider", provider);
	}

	const res = await fetch(`${API_URL}/api/v1/integrations/mappings?${params}`, {
		headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() },
	});
	if (!res.ok) {
		throw new Error(`Failed to fetch mappings: ${res.status}`);
	}
	const data = await res.json();
	return {
		mappings: (data["mappings"] || []).map(transformMapping),
		total: data["total"] || 0,
	};
}

export function useMappings(projectId: string, provider?: IntegrationProvider) {
	return useQuery({
		enabled: Boolean(projectId),
		queryFn: () => fetchMappings(projectId, provider),
		queryKey: ["integrations", "mappings", projectId, provider],
	});
}

export function useCreateMapping() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (data: {
			credentialId: string;
			localItemId: string;
			localItemType: string;
			projectId: string;
			externalId: string;
			externalType: string;
			direction?: MappingDirection;
			externalUrl?: string;
			externalKey?: string;
			fieldMappings?: Record<string, string>;
			mappingMetadata?: Record<string, unknown>;
			syncEnabled?: boolean;
		}) => {
			const res = await fetch(`${API_URL}/api/v1/integrations/mappings`, {
				body: JSON.stringify({
					credential_id: data["credentialId"],
					direction: data["direction"] || "bidirectional",
					external_id: data["externalId"],
					external_key: data["externalKey"],
					external_type: data["externalType"],
					external_url: data["externalUrl"],
					field_mappings: data["fieldMappings"],
					local_item_id: data["localItemId"],
					local_item_type: data["localItemType"],
					mapping_metadata: data["mappingMetadata"],
					project_id: data["projectId"],
					sync_enabled: data["syncEnabled"] ?? true,
				}),
				headers: { "Content-Type": "application/json", ...getAuthHeaders() },
				method: "POST",
			});
			if (!res.ok) {
				throw new Error(`Failed to create mapping: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			undefined;
		},
	});
}

export function useUpdateMapping() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async ({
			mappingId,
			...data
		}: {
			mappingId: string;
			direction?: MappingDirection;
			fieldMappings?: Record<string, string>;
			syncEnabled?: boolean;
			status?: string;
		}) => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/mappings/${mappingId}`,
				{
					body: JSON.stringify({
						direction: data["direction"],
						field_mappings: data["fieldMappings"],
						status: data["status"],
						sync_enabled: data["syncEnabled"],
					}),
					headers: { "Content-Type": "application/json", ...getAuthHeaders() },
					method: "PUT",
				},
			);
			if (!res.ok) {
				throw new Error(`Failed to update mapping: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			undefined;
		},
	});
}

export function useDeleteMapping() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (mappingId: string) => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/mappings/${mappingId}`,
				{ headers: getAuthHeaders(), method: "DELETE" },
			);
			if (!res.ok) {
				throw new Error(`Failed to delete mapping: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			undefined;
		},
	});
}

// ==================== Sync ====================

export function useSyncStatus(projectId: string) {
	return useQuery({
		enabled: Boolean(projectId),
		queryFn: async () => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/sync/status?project_id=${projectId}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch sync status: ${res.status}`);
			}
			const data = await res.json();
			return transformSyncStatus(data);
		},
		queryKey: ["integrations", "sync", "status", projectId],
		refetchInterval: 30000, // Refresh every 30 seconds
	});
}

export function useSyncQueue(
	projectId: string,
	status?: string,
	limit?: number,
) {
	return useQuery({
		enabled: Boolean(projectId),
		queryFn: async () => {
			const params = new URLSearchParams({ project_id: projectId });
			if (status) params.set("status", status);
			if (limit) params.set("limit", String(limit));

			const res = await fetch(
				`${API_URL}/api/v1/integrations/sync/queue?${params}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch sync queue: ${res.status}`);
			}
			const data = await res.json();
			return {
				items: (data["items"] || []).map(transformSyncQueueItem),
				total: data["total"] || 0,
			};
		},
		queryKey: ["integrations", "sync", "queue", projectId, status, limit],
	});
}

export function useTriggerSync() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (data: {
			mappingId?: string;
			credentialId?: string;
			direction?: string;
			payload?: Record<string, unknown>;
		}) => {
			const res = await fetch(`${API_URL}/api/v1/integrations/sync/trigger`, {
				body: JSON.stringify({
					credential_id: data["credentialId"],
					direction: data["direction"] || "pull",
					mapping_id: data["mappingId"],
					payload: data["payload"],
				}),
				headers: { "Content-Type": "application/json", ...getAuthHeaders() },
				method: "POST",
			});
			if (!res.ok) {
				throw new Error(`Failed to trigger sync: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			undefined;
		},
	});
}

// ==================== Conflicts ====================

export function useConflicts(projectId: string, status?: string) {
	return useQuery({
		enabled: Boolean(projectId),
		queryFn: async () => {
			const params = new URLSearchParams({ project_id: projectId });
			if (status) params.set("status", status);

			const res = await fetch(
				`${API_URL}/api/v1/integrations/conflicts?${params}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch conflicts: ${res.status}`);
			}
			const data = await res.json();
			return {
				conflicts: (data["conflicts"] || []).map(transformConflict),
				total: data["total"] || 0,
			};
		},
		queryKey: ["integrations", "conflicts", projectId, status],
	});
}

export function useResolveConflict() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async ({
			conflictId,
			resolution,
			mergedValue,
		}: {
			conflictId: string;
			resolution: "local" | "external" | "merge" | "skip";
			mergedValue?: unknown;
		}) => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/conflicts/${conflictId}/resolve`,
				{
					body: JSON.stringify({
						merged_value: mergedValue,
						resolution,
					}),
					headers: { "Content-Type": "application/json", ...getAuthHeaders() },
					method: "POST",
				},
			);
			if (!res.ok) {
				throw new Error(`Failed to resolve conflict: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			undefined;
		},
	});
}

// ==================== Stats ====================

export function useIntegrationStats(projectId: string) {
	return useQuery({
		enabled: Boolean(projectId),
		queryFn: async () => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/stats?project_id=${projectId}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch integration stats: ${res.status}`);
			}
			const data = await res.json();
			return transformStats(data);
		},
		queryKey: ["integrations", "stats", projectId],
	});
}

// ==================== GitHub Discovery ====================

export function useGitHubRepos(
	credentialId: string,
	search?: string,
	page?: number,
) {
	return useQuery({
		enabled: Boolean(credentialId),
		queryFn: async () => {
			const params = new URLSearchParams({ credential_id: credentialId });
			if (search) params.set("search", search);
			if (page) params.set("page", String(page));

			const res = await fetch(
				`${API_URL}/api/v1/integrations/github/repos?${params}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch GitHub repos: ${res.status}`);
			}
			const data = await res.json();
			return {
				page: data["page"],
				perPage: data["per_page"],
				repos: (data["repos"] || []).map((r: Record<string, unknown>) => ({
					id: r.id,
					name: r.name,
					fullName: r.full_name,
					description: r.description,
					htmlUrl: r.html_url,
					private: r["private"],
					owner: {
						login: r["owner"]?.login,
						avatarUrl: r["owner"]?.avatar_url,
					},
					defaultBranch: r.default_branch,
					updatedAt: r.updated_at,
				})) as GitHubRepo[],
			};
		},
		queryKey: ["integrations", "github", "repos", credentialId, search, page],
	});
}

export function useGitHubIssues(
	credentialId: string,
	owner: string,
	repo: string,
	state?: string,
	page?: number,
) {
	return useQuery({
		enabled: Boolean(credentialId) && Boolean(owner) && Boolean(repo),
		queryFn: async () => {
			const params = new URLSearchParams({ credential_id: credentialId });
			if (state) params.set("state", state);
			if (page) params.set("page", String(page));

			const res = await fetch(
				`${API_URL}/api/v1/integrations/github/repos/${owner}/${repo}/issues?${params}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch GitHub issues: ${res.status}`);
			}
			const data = await res.json();
			return {
				issues: (data["issues"] || []).map((i: Record<string, unknown>) => ({
					assignees: i["assignees"] || [],
					body: i["body"],
					createdAt: i.created_at,
					htmlUrl: i.html_url,
					id: i.id,
					labels: i["labels"] || [],
					number: i.number,
					state: i["state"],
					title: i.title,
					updatedAt: i.updated_at,
					user: {
						login: i["user"]?.login,
						avatarUrl: i["user"]?.avatar_url,
					},
				})) as GitHubIssue[],
				page: data["page"],
				perPage: data["per_page"],
			};
		},
		queryKey: [
			"integrations",
			"github",
			"issues",
			credentialId,
			owner,
			repo,
			state,
			page,
		],
	});
}

export function useGitHubProjects(
	credentialId: string,
	owner: string,
	isOrg?: boolean,
) {
	return useQuery({
		enabled: Boolean(credentialId) && Boolean(owner),
		queryFn: async () => {
			const params = new URLSearchParams({
				credential_id: credentialId,
				owner,
			});
			if (isOrg !== undefined) params.set("is_org", String(isOrg));

			const res = await fetch(
				`${API_URL}/api/v1/integrations/github/projects?${params}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch GitHub projects: ${res.status}`);
			}
			const data = await res.json();
			return {
				projects: (data["projects"] || []).map(
					(p: Record<string, unknown>) => ({
						closed: p["closed"],
						createdAt: p.created_at,
						description: p.description,
						id: p.id,
						public: p["public"],
						title: p.title,
						updatedAt: p.updated_at,
						url: p.url,
					}),
				) as GitHubProject[],
			};
		},
		queryKey: [
			"integrations",
			"github",
			"projects",
			credentialId,
			owner,
			isOrg,
		],
	});
}

// ==================== Linear Discovery ====================

export function useLinearTeams(credentialId: string) {
	return useQuery({
		enabled: Boolean(credentialId),
		queryFn: async () => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/linear/teams?credential_id=${credentialId}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch Linear teams: ${res.status}`);
			}
			const data = await res.json();
			return {
				teams: (data["teams"] || []).map((t: Record<string, unknown>) => ({
					color: t["color"],
					description: t.description,
					icon: t["icon"],
					id: t.id,
					key: t.key,
					name: t.name,
				})) as LinearTeam[],
			};
		},
		queryKey: ["integrations", "linear", "teams", credentialId],
	});
}

export function useLinearIssues(
	credentialId: string,
	teamId: string,
	first?: number,
) {
	return useQuery({
		enabled: Boolean(credentialId) && Boolean(teamId),
		queryFn: async () => {
			const params = new URLSearchParams({ credential_id: credentialId });
			if (first) params.set("first", String(first));

			const res = await fetch(
				`${API_URL}/api/v1/integrations/linear/teams/${teamId}/issues?${params}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch Linear issues: ${res.status}`);
			}
			const data = await res.json();
			return {
				issues: (data["issues"] || []).map((i: Record<string, unknown>) => ({
					assignee: i["assignee"],
					createdAt: i.created_at,
					description: i.description,
					id: i.id,
					identifier: i.identifier,
					labels: i["labels"] || [],
					priority: i.priority,
					state: i["state"],
					title: i.title,
					updatedAt: i.updated_at,
					url: i.url,
				})) as LinearIssue[],
			};
		},
		queryKey: ["integrations", "linear", "issues", credentialId, teamId, first],
	});
}

export function useLinearProjects(credentialId: string, first?: number) {
	return useQuery({
		enabled: Boolean(credentialId),
		queryFn: async () => {
			const params = new URLSearchParams({ credential_id: credentialId });
			if (first) params.set("first", String(first));

			const res = await fetch(
				`${API_URL}/api/v1/integrations/linear/projects?${params}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch Linear projects: ${res.status}`);
			}
			const data = await res.json();
			return {
				projects: (data["projects"] || []).map(
					(p: Record<string, unknown>) => ({
						description: p.description,
						id: p.id,
						name: p.name,
						progress: p["progress"],
						startDate: p.start_date,
						state: p["state"],
						targetDate: p.target_date,
						url: p.url,
					}),
				) as LinearProject[],
			};
		},
		queryKey: ["integrations", "linear", "projects", credentialId, first],
	});
}
