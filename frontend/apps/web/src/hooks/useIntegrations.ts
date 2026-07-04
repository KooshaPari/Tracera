import * as reactQuery from '@tanstack/react-query';

import type { IntegrationProvider, MappingDirection } from '@tracertm/types';

import { API_URL, getAuthHeaders } from './integrationsApi';
import {
  transformConflict,
  transformCredential,
  transformMapping,
  transformStats,
  transformSyncQueueItem,
  transformSyncStatus,
} from './integrationTransforms';
import {
  useGitHubIssues,
  useGitHubProjects,
  useGitHubRepos,
  useLinearIssues,
  useLinearProjects,
  useLinearTeams,
} from './useIntegrationsDiscovery';

interface CredentialsResponse {
  credentials: ReturnType<typeof transformCredential>[];
  total: number;
}

interface MappingsResponse {
  mappings: ReturnType<typeof transformMapping>[];
  total: number;
}

interface SyncQueueResponse {
  items: ReturnType<typeof transformSyncQueueItem>[];
  total: number;
}

interface ConflictsResponse {
  conflicts: ReturnType<typeof transformConflict>[];
  total: number;
}

interface StartOAuthInput {
  projectId?: string;
  provider: IntegrationProvider;
  redirectUri: string;
  scopes?: string[];
  credentialScope?: 'project' | 'user';
}

interface StartOAuthResponse {
  auth_url: string;
}

interface CompleteOAuthInput {
  code: string;
  state: string;
  redirectUri: string;
}

interface CreateMappingInput {
  credentialId: string;
  localItemId: string;
  localItemType: string;
  projectId: string;
  externalId: string;
  externalType: string;
  direction?: MappingDirection | undefined;
  externalUrl?: string | undefined;
  externalKey?: string | undefined;
  fieldMappings?: Record<string, string> | undefined;
  mappingMetadata?: Record<string, unknown> | undefined;
  syncEnabled?: boolean | undefined;
}

interface UpdateMappingInput {
  mappingId: string;
  direction?: MappingDirection | undefined;
  fieldMappings?: Record<string, string> | undefined;
  syncEnabled?: boolean | undefined;
  status?: string;
}

interface TriggerSyncInput {
  mappingId?: string;
  credentialId?: string;
  direction?: string;
  payload?: Record<string, unknown>;
}

interface ResolveConflictInput {
  conflictId: string;
  resolution: 'local' | 'external' | 'merge' | 'skip';
  mergedValue?: unknown;
}

// ==================== Credentials ====================

async function fetchCredentials(projectId: string): Promise<CredentialsResponse> {
  const res = await fetch(`${API_URL}/api/v1/integrations/credentials?project_id=${projectId}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch credentials: ${res.status}`);
  }
  const data = await res.json();
  const credentials = (data['credentials'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    credentials: credentials.map((item) => transformCredential(item)),
    total: Number(data['total'] ?? 0),
  };
}

function useCredentials(projectId: string): reactQuery.UseQueryResult<CredentialsResponse> {
  return reactQuery.useQuery({
    enabled: projectId !== '',
    queryFn: async () => fetchCredentials(projectId),
    queryKey: ['integrations', 'credentials', projectId],
  });
}

function useValidateCredential(): reactQuery.UseMutationResult<unknown, Error, string> {
  return reactQuery.useMutation({
    mutationFn: async (credentialId: string) => {
      const res = await fetch(
        `${API_URL}/api/v1/integrations/credentials/${credentialId}/validate`,
        {
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
          method: 'POST',
        },
      );
      if (!res.ok) {
        throw new Error(`Failed to validate credential: ${res.status}`);
      }
      return res.json();
    },
  });
}

function useDeleteCredential(): reactQuery.UseMutationResult<unknown, Error, string> {
  return reactQuery.useMutation({
    mutationFn: async (credentialId: string) => {
      const res = await fetch(`${API_URL}/api/v1/integrations/credentials/${credentialId}`, {
        headers: getAuthHeaders(),
        method: 'DELETE',
      });
      if (!res.ok) {
        throw new Error(`Failed to delete credential: ${res.status}`);
      }
      return res.json();
    },
  });
}

// ==================== OAuth ====================

function useStartOAuth(): reactQuery.UseMutationResult<StartOAuthResponse, Error, StartOAuthInput> {
  return reactQuery.useMutation({
    mutationFn: async (data: StartOAuthInput) => {
      const res = await fetch(`${API_URL}/api/v1/integrations/oauth/start`, {
        body: JSON.stringify({
          credential_scope: data['credentialScope'],
          project_id: data['projectId'],
          provider: data['provider'],
          redirect_uri: data['redirectUri'],
          scopes: data['scopes'],
        }),
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        method: 'POST',
      });
      if (!res.ok) {
        throw new Error(`Failed to start OAuth: ${res.status}`);
      }
      const result: StartOAuthResponse = await res.json();
      return result;
    },
  });
}

function useCompleteOAuth(): reactQuery.UseMutationResult<unknown, Error, CompleteOAuthInput> {
  return reactQuery.useMutation({
    mutationFn: async (data: CompleteOAuthInput) => {
      const res = await fetch(`${API_URL}/api/v1/integrations/oauth/callback`, {
        body: JSON.stringify({
          code: data['code'],
          redirect_uri: data['redirectUri'],
          state: data['state'],
        }),
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        method: 'POST',
      });
      if (!res.ok) {
        throw new Error(`Failed to complete OAuth: ${res.status}`);
      }
      return res.json();
    },
  });
}

// ==================== Mappings ====================

async function fetchMappings(
  projectId: string,
  provider?: IntegrationProvider,
): Promise<MappingsResponse> {
  const params = new URLSearchParams({ project_id: projectId });
  if (provider !== undefined) {
    params.set('provider', provider);
  }

  const res = await fetch(`${API_URL}/api/v1/integrations/mappings?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch mappings: ${res.status}`);
  }
  const data = await res.json();
  const mappings = (data['mappings'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    mappings: mappings.map((item) => transformMapping(item)),
    total: Number(data['total'] ?? 0),
  };
}

function useMappings(
  projectId: string,
  provider?: IntegrationProvider,
): reactQuery.UseQueryResult<MappingsResponse> {
  return reactQuery.useQuery({
    enabled: projectId !== '',
    queryFn: async () => fetchMappings(projectId, provider),
    queryKey: ['integrations', 'mappings', projectId, provider],
  });
}

function useCreateMapping(): reactQuery.UseMutationResult<unknown, Error, CreateMappingInput> {
  return reactQuery.useMutation({
    mutationFn: async (data: CreateMappingInput) => {
      const res = await fetch(`${API_URL}/api/v1/integrations/mappings`, {
        body: JSON.stringify({
          credential_id: data['credentialId'],
          direction: data['direction'] ?? 'bidirectional',
          external_id: data['externalId'],
          external_key: data['externalKey'],
          external_type: data['externalType'],
          external_url: data['externalUrl'],
          field_mappings: data['fieldMappings'],
          local_item_id: data['localItemId'],
          local_item_type: data['localItemType'],
          mapping_metadata: data['mappingMetadata'],
          project_id: data['projectId'],
          sync_enabled: data['syncEnabled'] ?? true,
        }),
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        method: 'POST',
      });
      if (!res.ok) {
        throw new Error(`Failed to create mapping: ${res.status}`);
      }
      return res.json();
    },
  });
}

function useUpdateMapping(): reactQuery.UseMutationResult<unknown, Error, UpdateMappingInput> {
  return reactQuery.useMutation({
    mutationFn: async ({ mappingId, ...data }: UpdateMappingInput) => {
      const res = await fetch(`${API_URL}/api/v1/integrations/mappings/${mappingId}`, {
        body: JSON.stringify({
          direction: data['direction'],
          field_mappings: data['fieldMappings'],
          status: data['status'],
          sync_enabled: data['syncEnabled'],
        }),
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        method: 'PUT',
      });
      if (!res.ok) {
        throw new Error(`Failed to update mapping: ${res.status}`);
      }
      return res.json();
    },
  });
}

function useDeleteMapping(): reactQuery.UseMutationResult<unknown, Error, string> {
  return reactQuery.useMutation({
    mutationFn: async (mappingId: string) => {
      const res = await fetch(`${API_URL}/api/v1/integrations/mappings/${mappingId}`, {
        headers: getAuthHeaders(),
        method: 'DELETE',
      });
      if (!res.ok) {
        throw new Error(`Failed to delete mapping: ${res.status}`);
      }
      return res.json();
    },
  });
}

// ==================== Sync ====================

function useSyncStatus(
  projectId: string,
): reactQuery.UseQueryResult<ReturnType<typeof transformSyncStatus>> {
  return reactQuery.useQuery({
    enabled: projectId !== '',
    queryFn: async () => {
      const res = await fetch(
        `${API_URL}/api/v1/integrations/sync/status?project_id=${projectId}`,
        { headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() } },
      );
      if (!res.ok) {
        throw new Error(`Failed to fetch sync status: ${res.status}`);
      }
      const data = await res.json();
      return transformSyncStatus(data);
    },
    queryKey: ['integrations', 'sync', 'status', projectId],
    refetchInterval: 30_000, // Refresh every 30 seconds
  });
}

function useSyncQueue(
  projectId: string,
  status?: string,
  limit?: number,
): reactQuery.UseQueryResult<SyncQueueResponse> {
  return reactQuery.useQuery({
    enabled: projectId !== '',
    queryFn: async () => {
      const params = new URLSearchParams({ project_id: projectId });
      if (status !== undefined) {
        params.set('status', status);
      }
      if (limit !== undefined) {
        params.set('limit', String(limit));
      }

      const res = await fetch(`${API_URL}/api/v1/integrations/sync/queue?${params}`, {
        headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch sync queue: ${res.status}`);
      }
      const data = await res.json();
      const items = (data['items'] as Record<string, unknown>[] | undefined) ?? [];
      return {
        items: items.map((item) => transformSyncQueueItem(item)),
        total: Number(data['total'] ?? 0),
      };
    },
    queryKey: ['integrations', 'sync', 'queue', projectId, status, limit],
  });
}

function useTriggerSync(): reactQuery.UseMutationResult<unknown, Error, TriggerSyncInput> {
  return reactQuery.useMutation({
    mutationFn: async (data: TriggerSyncInput) => {
      const res = await fetch(`${API_URL}/api/v1/integrations/sync/trigger`, {
        body: JSON.stringify({
          credential_id: data['credentialId'],
          direction: data['direction'] ?? 'pull',
          mapping_id: data['mappingId'],
          payload: data['payload'],
        }),
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        method: 'POST',
      });
      if (!res.ok) {
        throw new Error(`Failed to trigger sync: ${res.status}`);
      }
      return res.json();
    },
  });
}

// ==================== Conflicts ====================

function useConflicts(
  projectId: string,
  status?: string,
): reactQuery.UseQueryResult<ConflictsResponse> {
  return reactQuery.useQuery({
    enabled: projectId !== '',
    queryFn: async () => {
      const params = new URLSearchParams({ project_id: projectId });
      if (status !== undefined) {
        params.set('status', status);
      }

      const res = await fetch(`${API_URL}/api/v1/integrations/conflicts?${params}`, {
        headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch conflicts: ${res.status}`);
      }
      const data = await res.json();
      const conflictsData = (data['conflicts'] as Record<string, unknown>[] | undefined) ?? [];
      return {
        conflicts: conflictsData.map((item) => transformConflict(item)),
        total: Number(data['total'] ?? 0),
      };
    },
    queryKey: ['integrations', 'conflicts', projectId, status],
  });
}

function useResolveConflict(): reactQuery.UseMutationResult<unknown, Error, ResolveConflictInput> {
  return reactQuery.useMutation({
    mutationFn: async ({ conflictId, resolution, mergedValue }: ResolveConflictInput) => {
      const res = await fetch(`${API_URL}/api/v1/integrations/conflicts/${conflictId}/resolve`, {
        body: JSON.stringify({
          merged_value: mergedValue,
          resolution,
        }),
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        method: 'POST',
      });
      if (!res.ok) {
        throw new Error(`Failed to resolve conflict: ${res.status}`);
      }
      return res.json();
    },
  });
}

// ==================== Stats ====================

function useIntegrationStats(
  projectId: string,
): reactQuery.UseQueryResult<ReturnType<typeof transformStats>> {
  return reactQuery.useQuery({
    enabled: projectId !== '',
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/v1/integrations/stats?project_id=${projectId}`, {
        headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
      });
      if (!res.ok) {
        throw new Error(`Failed to fetch integration stats: ${res.status}`);
      }
      const data = await res.json();
      return transformStats(data);
    },
    queryKey: ['integrations', 'stats', projectId],
  });
}

export {
  useCompleteOAuth,
  useConflicts,
  useCreateMapping,
  useCredentials,
  useDeleteCredential,
  useDeleteMapping,
  useGitHubIssues,
  useGitHubProjects,
  useGitHubRepos,
  useIntegrationStats,
  useLinearIssues,
  useLinearProjects,
  useLinearTeams,
  useMappings,
  useResolveConflict,
  useStartOAuth,
  useSyncQueue,
  useSyncStatus,
  useTriggerSync,
  useUpdateMapping,
  useValidateCredential,
};
