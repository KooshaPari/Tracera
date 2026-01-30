import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	IntegrationCredential,
	IntegrationMapping,
	SyncQueueItem,
	SyncLog,
	SyncConflict,
	IntegrationStats,
	SyncStatusSummary,
	IntegrationProvider,
	MappingDirection,
	GitHubRepo,
	GitHubIssue,
	GitHubProject,
	LinearTeam,
	LinearIssue,
	LinearProject,
} from "@tracertm/types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformCredential(data: any): IntegrationCredential {
	return {
		id: data.id,
		projectId: data.project_id || undefined,
		provider: data.provider,
		credentialType: data.credential_type,
		status: data.status,
		scopes: data.scopes || [],
		providerUserId: data.provider_user_id,
		providerMetadata: data.provider_metadata,
		lastValidatedAt: data.last_validated_at,
		validationError: data.validation_error,
		expiresAt: data.expires_at,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
	};
}

function transformMapping(data: any): IntegrationMapping {
	return {
		id: data.id,
		credentialId: data.credential_id,
		provider: data.provider,
		direction: data.direction,
		localItemId: data.local_item_id,
		localItemType: data.local_item_type,
		externalId: data.external_id,
		externalType: data.external_type,
		externalUrl: data.external_url,
		externalKey: data.external_key,
		mappingMetadata: data.mapping_metadata,
		status: data.status,
		syncEnabled: data.sync_enabled,
		lastSyncedAt: data.last_synced_at,
		lastSyncStatus: data.last_sync_status,
		lastSyncError: data.last_sync_error,
		fieldMappings: data.field_mappings,
		fieldResolutionRules: data.field_resolution_rules,
		localVersion: data.local_version,
		externalVersion: data.external_version,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
	};
}

function transformSyncQueueItem(data: any): SyncQueueItem {
	return {
		id: data.id,
		credentialId: data.credential_id,
		mappingId: data.mapping_id,
		provider: data.provider,
		eventType: data.event_type,
		direction: data.direction,
		status: data.status,
		priority: data.priority,
		retryCount: data.retry_count,
		maxRetries: data.max_retries,
		errorMessage: data.error_message,
		scheduledAt: data.scheduled_at,
		startedAt: data.started_at,
		completedAt: data.completed_at,
		createdAt: data.created_at,
	};
}

function transformSyncLog(data: any): SyncLog {
	return {
		id: data.id,
		credentialId: data.credential_id,
		mappingId: data.mapping_id,
		provider: data.provider,
		eventType: data.event_type,
		direction: data.direction,
		status: data.status,
		itemsProcessed: data.items_processed,
		itemsFailed: data.items_failed,
		itemsSkipped: data.items_skipped,
		errorMessage: data.error_message,
		startedAt: data.started_at,
		completedAt: data.completed_at,
		durationMs: data.duration_ms,
		createdAt: data.created_at,
	};
}

function transformConflict(data: any): SyncConflict {
	return {
		id: data.id,
		mappingId: data.mapping_id,
		provider: data.provider,
		conflictType: data.conflict_type,
		fieldName: data.field_name,
		localValue: data.local_value,
		externalValue: data.external_value,
		localModifiedAt: data.local_modified_at,
		externalModifiedAt: data.external_modified_at,
		status: data.status,
		resolution: data.resolution,
		resolvedValue: data.resolved_value,
		resolvedBy: data.resolved_by,
		resolvedAt: data.resolved_at,
		createdAt: data.created_at,
	};
}

function transformSyncStatus(data: any): SyncStatusSummary {
	return {
		projectId: data.project_id,
		queue: data.queue,
		recentSyncs: (data.recent_syncs || []).map(transformSyncLog),
		providers: (data.providers || []).map((p: any) => ({
			provider: p.provider,
			status: p.status,
			lastValidated: p.last_validated,
		})),
	};
}

function transformStats(data: any): IntegrationStats {
	return {
		projectId: data.project_id,
		providers: (data.providers || []).map((p: any) => ({
			provider: p.provider,
			status: p.status,
			credentialType: p.credential_type,
		})),
		mappings: {
			total: data.mappings?.total || 0,
			active: data.mappings?.active || 0,
			byProvider: data.mappings?.by_provider || {},
		},
		sync: {
			queuePending: data.sync?.queue_pending || 0,
			recentSyncs: data.sync?.recent_syncs || 0,
			successRate: data.sync?.success_rate || 0,
		},
		conflicts: {
			pending: data.conflicts?.pending || 0,
			resolved: data.conflicts?.resolved || 0,
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
			headers: { "X-Bulk-Operation": "true" },
		},
	);
	if (!res.ok) {
		throw new Error(`Failed to fetch credentials: ${res.status}`);
	}
	const data = await res.json();
	return {
		credentials: (data.credentials || []).map(transformCredential),
		total: data.total || 0,
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
					headers: { "Content-Type": "application/json" },
				},
			);
			if (!res.ok) {
				throw new Error(`Failed to validate credential: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
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
				{ method: "DELETE" },
			);
			if (!res.ok) {
				throw new Error(`Failed to delete credential: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
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
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					project_id: data.projectId,
					provider: data.provider,
					redirect_uri: data.redirectUri,
					scopes: data.scopes,
					credential_scope: data.credentialScope,
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
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					code: data.code,
					state: data.state,
					redirect_uri: data.redirectUri,
				}),
			});
			if (!res.ok) {
				throw new Error(`Failed to complete OAuth: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			queryClient.invalidateQueries({
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
		headers: { "X-Bulk-Operation": "true" },
	});
	if (!res.ok) {
		throw new Error(`Failed to fetch mappings: ${res.status}`);
	}
	const data = await res.json();
	return {
		mappings: (data.mappings || []).map(transformMapping),
		total: data.total || 0,
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
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					credential_id: data.credentialId,
					project_id: data.projectId,
					local_item_id: data.localItemId,
					local_item_type: data.localItemType,
					external_id: data.externalId,
					external_type: data.externalType,
					direction: data.direction || "bidirectional",
					external_url: data.externalUrl,
					external_key: data.externalKey,
					field_mappings: data.fieldMappings,
					mapping_metadata: data.mappingMetadata,
					sync_enabled: data.syncEnabled ?? true,
				}),
			});
			if (!res.ok) {
				throw new Error(`Failed to create mapping: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["integrations", "mappings"] });
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
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						direction: data.direction,
						field_mappings: data.fieldMappings,
						sync_enabled: data.syncEnabled,
						status: data.status,
					}),
				},
			);
			if (!res.ok) {
				throw new Error(`Failed to update mapping: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["integrations", "mappings"] });
		},
	});
}

export function useDeleteMapping() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (mappingId: string) => {
			const res = await fetch(
				`${API_URL}/api/v1/integrations/mappings/${mappingId}`,
				{ method: "DELETE" },
			);
			if (!res.ok) {
				throw new Error(`Failed to delete mapping: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["integrations", "mappings"] });
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
				{ headers: { "X-Bulk-Operation": "true" } },
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
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch sync queue: ${res.status}`);
			}
			const data = await res.json();
			return {
				items: (data.items || []).map(transformSyncQueueItem),
				total: data.total || 0,
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
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					mapping_id: data.mappingId,
					credential_id: data.credentialId,
					direction: data.direction || "pull",
					payload: data.payload,
				}),
			});
			if (!res.ok) {
				throw new Error(`Failed to trigger sync: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["integrations", "sync"] });
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
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch conflicts: ${res.status}`);
			}
			const data = await res.json();
			return {
				conflicts: (data.conflicts || []).map(transformConflict),
				total: data.total || 0,
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
					headers: { "Content-Type": "application/json" },
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
			queryClient.invalidateQueries({
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
				{ headers: { "X-Bulk-Operation": "true" } },
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
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch GitHub repos: ${res.status}`);
			}
			const data = await res.json();
			return {
				repos: (data.repos || []).map((r: any) => ({
					id: r.id,
					name: r.name,
					fullName: r.full_name,
					description: r.description,
					htmlUrl: r.html_url,
					private: r.private,
					owner: {
						login: r.owner?.login,
						avatarUrl: r.owner?.avatar_url,
					},
					defaultBranch: r.default_branch,
					updatedAt: r.updated_at,
				})) as GitHubRepo[],
				page: data.page,
				perPage: data.per_page,
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
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch GitHub issues: ${res.status}`);
			}
			const data = await res.json();
			return {
				issues: (data.issues || []).map((i: any) => ({
					id: i.id,
					number: i.number,
					title: i.title,
					state: i.state,
					htmlUrl: i.html_url,
					body: i.body,
					user: {
						login: i.user?.login,
						avatarUrl: i.user?.avatar_url,
					},
					labels: i.labels || [],
					assignees: i.assignees || [],
					createdAt: i.created_at,
					updatedAt: i.updated_at,
				})) as GitHubIssue[],
				page: data.page,
				perPage: data.per_page,
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
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch GitHub projects: ${res.status}`);
			}
			const data = await res.json();
			return {
				projects: (data.projects || []).map((p: any) => ({
					id: p.id,
					title: p.title,
					description: p.description,
					url: p.url,
					closed: p.closed,
					public: p.public,
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
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch Linear teams: ${res.status}`);
			}
			const data = await res.json();
			return {
				teams: (data.teams || []).map((t: any) => ({
					id: t.id,
					name: t.name,
					key: t.key,
					description: t.description,
					icon: t.icon,
					color: t.color,
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
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch Linear issues: ${res.status}`);
			}
			const data = await res.json();
			return {
				issues: (data.issues || []).map((i: any) => ({
					id: i.id,
					identifier: i.identifier,
					title: i.title,
					description: i.description,
					state: i.state,
					priority: i.priority,
					url: i.url,
					assignee: i.assignee,
					labels: i.labels || [],
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
				{ headers: { "X-Bulk-Operation": "true" } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch Linear projects: ${res.status}`);
			}
			const data = await res.json();
			return {
				projects: (data.projects || []).map((p: any) => ({
					id: p.id,
					name: p.name,
					description: p.description,
					state: p.state,
					progress: p.progress,
					url: p.url,
					startDate: p.start_date,
					targetDate: p.target_date,
				})) as LinearProject[],
			};
		},
		enabled: Boolean(credentialId),
	});
}
