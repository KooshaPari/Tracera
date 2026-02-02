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
function transformCredential(data: Record<string, unknown>): IntegrationCredential {
	return {
		id: data['id'] as string,
		projectId: (data['project_id'] as string | undefined) || undefined,
		provider: data['provider'] as IntegrationProvider,
		credentialType: data['credential_type'] as IntegrationCredential['credentialType'],
		status: data['status'] as IntegrationCredential['status'],
		scopes: (data['scopes'] as string[]) || [],
		providerUserId: data['provider_user_id'] as string | undefined,
		providerMetadata: data['provider_metadata'] as Record<string, unknown> | undefined,
		lastValidatedAt: data['last_validated_at'] as string | undefined,
		validationError: data['validation_error'] as string | undefined,
		expiresAt: data['expires_at'] as string | undefined,
		createdAt: data['created_at'] as string,
		updatedAt: data['updated_at'] as string,
	};
}

function transformMapping(data: Record<string, unknown>): IntegrationMapping {
	return {
		id: data['id'] as string,
		credentialId: data['credential_id'] as string,
		provider: data['provider'] as IntegrationProvider,
		direction: data['direction'] as MappingDirection,
		localItemId: data['local_item_id'] as string,
		localItemType: data['local_item_type'] as string,
		externalId: data['external_id'] as string,
		externalType: data['external_type'] as string,
		externalUrl: data['external_url'] as string | undefined,
		externalKey: data['external_key'] as string | undefined,
		mappingMetadata: data['mapping_metadata'] as Record<string, unknown> | undefined,
		status: data['status'] as IntegrationMapping['status'],
		syncEnabled: data['sync_enabled'] as boolean,
		lastSyncedAt: data['last_synced_at'] as string | undefined,
		lastSyncStatus: data['last_sync_status'] as string | undefined,
		lastSyncError: data['last_sync_error'] as string | undefined,
		fieldMappings: data['field_mappings'] as Record<string, string> | undefined,
		fieldResolutionRules: data['field_resolution_rules'] as Record<string, unknown> | undefined,
		localVersion: data['local_version'] as number | undefined,
		externalVersion: data['external_version'] as string | undefined,
		createdAt: data['created_at'] as string,
		updatedAt: data['updated_at'] as string,
	};
}

function transformSyncQueueItem(data: Record<string, unknown>): SyncQueueItem {
	return {
		id: data['id'] as string,
		credentialId: data['credential_id'] as string,
		mappingId: data['mapping_id'] as string | undefined,
		provider: data['provider'] as IntegrationProvider,
		eventType: data['event_type'] as string,
		direction: data['direction'] as MappingDirection,
		status: data['status'] as SyncQueueItem['status'],
		priority: data['priority'] as number,
		retryCount: data['retry_count'] as number,
		maxRetries: data['max_retries'] as number,
		errorMessage: data['error_message'] as string | undefined,
		scheduledAt: data['scheduled_at'] as string,
		startedAt: data['started_at'] as string | undefined,
		completedAt: data['completed_at'] as string | undefined,
		createdAt: data['created_at'] as string,
	};
}

function transformSyncLog(data: Record<string, unknown>): SyncLog {
	return {
		id: data['id'] as string,
		credentialId: data['credential_id'] as string,
		mappingId: data['mapping_id'] as string | undefined,
		provider: data['provider'] as IntegrationProvider,
		eventType: data['event_type'] as string,
		direction: data['direction'] as MappingDirection,
		status: data['status'] as SyncLog['status'],
		itemsProcessed: data['items_processed'] as number,
		itemsFailed: data['items_failed'] as number,
		itemsSkipped: data['items_skipped'] as number,
		errorMessage: data['error_message'] as string | undefined,
		startedAt: data['started_at'] as string,
		completedAt: data['completed_at'] as string | undefined,
		durationMs: data['duration_ms'] as number | undefined,
		createdAt: data['created_at'] as string,
	};
}

function transformConflict(data: Record<string, unknown>): SyncConflict {
	return {
		id: data['id'] as string,
		mappingId: data['mapping_id'] as string,
		provider: data['provider'] as IntegrationProvider,
		conflictType: data['conflict_type'] as SyncConflict['conflictType'],
		fieldName: data['field_name'] as string,
		localValue: data['local_value'] as unknown,
		externalValue: data['external_value'] as unknown,
		localModifiedAt: data['local_modified_at'] as string,
		externalModifiedAt: data['external_modified_at'] as string,
		status: data['status'] as SyncConflict['status'],
		resolution: data['resolution'] as SyncConflict['resolution'] | undefined,
		resolvedValue: data['resolved_value'] as unknown,
		resolvedBy: data['resolved_by'] as string | undefined,
		resolvedAt: data['resolved_at'] as string | undefined,
		createdAt: data['created_at'] as string,
	};
}

function transformSyncStatus(data: Record<string, unknown>): SyncStatusSummary {
	return {
		projectId: data['project_id'] as string,
		queue: data['queue'] as SyncStatusSummary['queue'],
		recentSyncs: ((data['recent_syncs'] as Record<string, unknown>[]) || []).map(transformSyncLog),
		providers: ((data['providers'] as Record<string, unknown>[]) || []).map((p: Record<string, unknown>) => ({
			provider: p['provider'] as IntegrationProvider,
			status: p['status'] as string,
			lastValidated: p['last_validated'] as string | undefined,
		})),
	};
}

function transformStats(data: Record<string, unknown>): IntegrationStats {
	const mappings = data['mappings'] as Record<string, unknown> | undefined;
	const sync = data['sync'] as Record<string, unknown> | undefined;
	const conflicts = data['conflicts'] as Record<string, unknown> | undefined;

	return {
		projectId: data['project_id'] as string,
		providers: ((data['providers'] as Record<string, unknown>[]) || []).map((p: Record<string, unknown>) => ({
			provider: p['provider'] as IntegrationProvider,
			status: p['status'] as string,
			credentialType: p['credential_type'] as string,
		})),
		mappings: {
			total: (mappings?.total as number) || 0,
			active: (mappings?.active as number) || 0,
			byProvider: (mappings?.by_provider as Record<string, number>) || {},
		},
		sync: {
			queuePending: (sync?.queue_pending as number) || 0,
			recentSyncs: (sync?.recent_syncs as number) || 0,
			successRate: (sync?.success_rate as number) || 0,
		},
		conflicts: {
			pending: (conflicts?.pending as number) || 0,
			resolved: (conflicts?.resolved as number) || 0,
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
		credentials: (data['credentials'] || []).map(transformCredential),
		total: data['total'] || 0,
	};
}

export function useCredentials(projectId: string) {
	return useQuery({
		queryKey: ["integrations", "credentials", projectId],
		queryFn: () => fetchCredentials(projectId),
		enabled: Boolean(projectId),
	});
}

export function useValidateCredential() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (credentialId: string) => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/credentials/${credentialId}/validate`,
				{
					method: "POST",
					headers: { "Content-Type": "application/json", ...getAuthHeaders() },
				},
			);
			if (!res.ok) {
				throw new Error(`Failed to validate credential: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			void queryClient.invalidateQueries({
				queryKey: ["integrations", "credentials"],
			});
		},
	});
}

export function useDeleteCredential() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (credentialId: string) => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/credentials/${credentialId}`,
				{ method: "DELETE", headers: getAuthHeaders() },
			);
			if (!res.ok) {
				throw new Error(`Failed to delete credential: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			void queryClient.invalidateQueries({
				queryKey: ["integrations", "credentials"],
			});
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
				method: "POST",
				headers: { "Content-Type": "application/json", ...getAuthHeaders() },
				body: JSON.stringify({
					project_id: data['projectId'],
					provider: data['provider'],
					redirect_uri: data['redirectUri'],
					scopes: data['scopes'],
					credential_scope: data['credentialScope'],
				}),
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
				method: "POST",
				headers: { "Content-Type": "application/json", ...getAuthHeaders() },
				body: JSON.stringify({
					code: data['code'],
					state: data['state'],
					redirect_uri: data['redirectUri'],
				}),
			});
			if (!res.ok) {
				throw new Error(`Failed to complete OAuth: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			void queryClient.invalidateQueries({
				queryKey: ["integrations", "credentials"],
			});
		},
	});
}

// ==================== Mappings ====================

async function fetchMappings(
	projectId: string,
	provider?: IntegrationProvider,
): Promise<{ mappings: IntegrationMapping[]; total: number }> {
	const params = new URLSearchParams({ project_id: projectId });
	if (provider) params.set("provider", provider);

	const res = await fetch(`${API_URL}/api/v1/integrations/mappings?${params}`, {
		headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() },
	});
	if (!res.ok) {
		throw new Error(`Failed to fetch mappings: ${res.status}`);
	}
	const data = await res.json();
	return {
		mappings: (data['mappings'] || []).map(transformMapping),
		total: data['total'] || 0,
	};
}

export function useMappings(projectId: string, provider?: IntegrationProvider) {
	return useQuery({
		queryKey: ["integrations", "mappings", projectId, provider],
		queryFn: () => fetchMappings(projectId, provider),
		enabled: Boolean(projectId),
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
				method: "POST",
				headers: { "Content-Type": "application/json", ...getAuthHeaders() },
				body: JSON.stringify({
					credential_id: data['credentialId'],
					project_id: data['projectId'],
					local_item_id: data['localItemId'],
					local_item_type: data['localItemType'],
					external_id: data['externalId'],
					external_type: data['externalType'],
					direction: data['direction'] || "bidirectional",
					external_url: data['externalUrl'],
					external_key: data['externalKey'],
					field_mappings: data['fieldMappings'],
					mapping_metadata: data['mappingMetadata'],
					sync_enabled: data['syncEnabled'] ?? true,
				}),
			});
			if (!res.ok) {
				throw new Error(`Failed to create mapping: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: ["integrations", "mappings"] });
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
					method: "PUT",
					headers: { "Content-Type": "application/json", ...getAuthHeaders() },
					body: JSON.stringify({
						direction: data['direction'],
						field_mappings: data['fieldMappings'],
						sync_enabled: data['syncEnabled'],
						status: data['status'],
					}),
				},
			);
			if (!res.ok) {
				throw new Error(`Failed to update mapping: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: ["integrations", "mappings"] });
		},
	});
}

export function useDeleteMapping() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (mappingId: string) => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/mappings/${mappingId}`,
				{ method: "DELETE", headers: getAuthHeaders() },
			);
			if (!res.ok) {
				throw new Error(`Failed to delete mapping: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: ["integrations", "mappings"] });
		},
	});
}

// ==================== Sync ====================

export function useSyncStatus(projectId: string) {
	return useQuery({
		queryKey: ["integrations", "sync", "status", projectId],
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
		enabled: Boolean(projectId),
		refetchInterval: 30000, // Refresh every 30 seconds
	});
}

export function useSyncQueue(
	projectId: string,
	status?: string,
	limit?: number,
) {
	return useQuery({
		queryKey: ["integrations", "sync", "queue", projectId, status, limit],
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
				items: (data['items'] || []).map(transformSyncQueueItem),
				total: data['total'] || 0,
			};
		},
		enabled: Boolean(projectId),
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
				method: "POST",
				headers: { "Content-Type": "application/json", ...getAuthHeaders() },
				body: JSON.stringify({
					mapping_id: data['mappingId'],
					credential_id: data['credentialId'],
					direction: data['direction'] || "pull",
					payload: data['payload'],
				}),
			});
			if (!res.ok) {
				throw new Error(`Failed to trigger sync: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: ["integrations", "sync"] });
		},
	});
}

// ==================== Conflicts ====================

export function useConflicts(projectId: string, status?: string) {
	return useQuery({
		queryKey: ["integrations", "conflicts", projectId, status],
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
				conflicts: (data['conflicts'] || []).map(transformConflict),
				total: data['total'] || 0,
			};
		},
		enabled: Boolean(projectId),
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
					method: "POST",
					headers: { "Content-Type": "application/json", ...getAuthHeaders() },
					body: JSON.stringify({
						resolution,
						merged_value: mergedValue,
					}),
				},
			);
			if (!res.ok) {
				throw new Error(`Failed to resolve conflict: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			void queryClient.invalidateQueries({
				queryKey: ["integrations", "conflicts"],
			});
		},
	});
}

// ==================== Stats ====================

export function useIntegrationStats(projectId: string) {
	return useQuery({
		queryKey: ["integrations", "stats", projectId],
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
		enabled: Boolean(projectId),
	});
}

// ==================== GitHub Discovery ====================

export function useGitHubRepos(
	credentialId: string,
	search?: string,
	page?: number,
) {
	return useQuery({
		queryKey: ["integrations", "github", "repos", credentialId, search, page],
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
				repos: (data['repos'] || []).map((r: Record<string, unknown>) => ({
					id: r.id,
					name: r.name,
					fullName: r.full_name,
					description: r.description,
					htmlUrl: r.html_url,
					private: r['private'],
					owner: {
						login: r['owner']?.login,
						avatarUrl: r['owner']?.avatar_url,
					},
					defaultBranch: r.default_branch,
					updatedAt: r.updated_at,
				})) as GitHubRepo[],
				page: data['page'],
				perPage: data['per_page'],
			};
		},
		enabled: Boolean(credentialId),
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
				issues: (data['issues'] || []).map((i: Record<string, unknown>) => ({
					id: i.id,
					number: i.number,
					title: i.title,
					state: i['state'],
					htmlUrl: i.html_url,
					body: i['body'],
					user: {
						login: i['user']?.login,
						avatarUrl: i['user']?.avatar_url,
					},
					labels: i['labels'] || [],
					assignees: i['assignees'] || [],
					createdAt: i.created_at,
					updatedAt: i.updated_at,
				})) as GitHubIssue[],
				page: data['page'],
				perPage: data['per_page'],
			};
		},
		enabled: Boolean(credentialId) && Boolean(owner) && Boolean(repo),
	});
}

export function useGitHubProjects(
	credentialId: string,
	owner: string,
	isOrg?: boolean,
) {
	return useQuery({
		queryKey: [
			"integrations",
			"github",
			"projects",
			credentialId,
			owner,
			isOrg,
		],
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
				projects: (data['projects'] || []).map((p: Record<string, unknown>) => ({
					id: p.id,
					title: p.title,
					description: p.description,
					url: p.url,
					closed: p['closed'],
					public: p['public'],
					createdAt: p.created_at,
					updatedAt: p.updated_at,
				})) as GitHubProject[],
			};
		},
		enabled: Boolean(credentialId) && Boolean(owner),
	});
}

// ==================== Linear Discovery ====================

export function useLinearTeams(credentialId: string) {
	return useQuery({
		queryKey: ["integrations", "linear", "teams", credentialId],
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
				teams: (data['teams'] || []).map((t: Record<string, unknown>) => ({
					id: t.id,
					name: t.name,
					key: t.key,
					description: t.description,
					icon: t['icon'],
					color: t['color'],
				})) as LinearTeam[],
			};
		},
		enabled: Boolean(credentialId),
	});
}

export function useLinearIssues(
	credentialId: string,
	teamId: string,
	first?: number,
) {
	return useQuery({
		queryKey: ["integrations", "linear", "issues", credentialId, teamId, first],
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
				issues: (data['issues'] || []).map((i: Record<string, unknown>) => ({
					id: i.id,
					identifier: i.identifier,
					title: i.title,
					description: i.description,
					state: i['state'],
					priority: i.priority,
					url: i.url,
					assignee: i['assignee'],
					labels: i['labels'] || [],
					createdAt: i.created_at,
					updatedAt: i.updated_at,
				})) as LinearIssue[],
			};
		},
		enabled: Boolean(credentialId) && Boolean(teamId),
	});
}

export function useLinearProjects(credentialId: string, first?: number) {
	return useQuery({
		queryKey: ["integrations", "linear", "projects", credentialId, first],
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
				projects: (data['projects'] || []).map((p: Record<string, unknown>) => ({
					id: p.id,
					name: p.name,
					description: p.description,
					state: p['state'],
					progress: p['progress'],
					url: p.url,
					startDate: p.start_date,
					targetDate: p.target_date,
				})) as LinearProject[],
			};
		},
		enabled: Boolean(credentialId),
	});
}
