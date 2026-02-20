import type * as TracerTypes from '@tracertm/types';

type ApiRecord = Record<string, unknown>;

const toNumber = (value: unknown): number => Number(value ?? 0);

const transformCredential = (data: ApiRecord): TracerTypes.IntegrationCredential => ({
  createdAt: data['created_at'] as string,
  credentialType: data['credential_type'] as TracerTypes.IntegrationCredential['credentialType'],
  expiresAt: data['expires_at'] as string | undefined,
  id: data['id'] as string,
  lastValidatedAt: data['last_validated_at'] as string | undefined,
  projectId: (data['project_id'] as string | undefined) ?? undefined,
  provider: data['provider'] as TracerTypes.IntegrationProvider,
  providerMetadata: data['provider_metadata'] as Record<string, unknown> | undefined,
  providerUserId: data['provider_user_id'] as string | undefined,
  scopes: (data['scopes'] as string[]) ?? [],
  status: data['status'] as TracerTypes.IntegrationCredential['status'],
  updatedAt: data['updated_at'] as string,
  validationError: data['validation_error'] as string | undefined,
});

const transformMapping = (data: ApiRecord): TracerTypes.IntegrationMapping => ({
  createdAt: data['created_at'] as string,
  credentialId: data['credential_id'] as string,
  direction: data['direction'] as TracerTypes.MappingDirection,
  externalId: data['external_id'] as string,
  externalKey: data['external_key'] as string | undefined,
  externalType: data['external_type'] as string,
  externalUrl: data['external_url'] as string | undefined,
  externalVersion: data['external_version'] as string | undefined,
  fieldMappings: data['field_mappings'] as Record<string, string> | undefined,
  fieldResolutionRules: data['field_resolution_rules'] as
    | Record<string, TracerTypes.ConflictResolutionStrategy>
    | undefined,
  id: data['id'] as string,
  lastSyncError: data['last_sync_error'] as string | undefined,
  lastSyncStatus: data['last_sync_status'] as string | undefined,
  lastSyncedAt: data['last_synced_at'] as string | undefined,
  localItemId: data['local_item_id'] as string,
  localItemType: data['local_item_type'] as string,
  localVersion: data['local_version'] as number | undefined,
  mappingMetadata: data['mapping_metadata'] as Record<string, unknown> | undefined,
  provider: data['provider'] as TracerTypes.IntegrationProvider,
  status: data['status'] as TracerTypes.IntegrationMapping['status'],
  syncEnabled: data['sync_enabled'] as boolean,
  updatedAt: data['updated_at'] as string,
});

const transformSyncQueueItem = (data: ApiRecord): TracerTypes.SyncQueueItem => ({
  completedAt: data['completed_at'] as string | undefined,
  createdAt: data['created_at'] as string,
  credentialId: data['credential_id'] as string,
  direction: data['direction'] as TracerTypes.MappingDirection,
  errorMessage: data['error_message'] as string | undefined,
  eventType: data['event_type'] as string,
  id: data['id'] as string,
  mappingId: data['mapping_id'] as string | undefined,
  maxRetries: data['max_retries'] as number,
  priority: data['priority'] as number,
  provider: data['provider'] as TracerTypes.IntegrationProvider,
  retryCount: data['retry_count'] as number,
  scheduledAt: data['scheduled_at'] as string,
  startedAt: data['started_at'] as string | undefined,
  status: data['status'] as TracerTypes.SyncQueueItem['status'],
});

const transformSyncLog = (data: ApiRecord): TracerTypes.SyncLog => ({
  completedAt: data['completed_at'] as string | undefined,
  createdAt: data['created_at'] as string,
  credentialId: data['credential_id'] as string,
  direction: data['direction'] as TracerTypes.MappingDirection,
  durationMs: data['duration_ms'] as number | undefined,
  errorMessage: data['error_message'] as string | undefined,
  eventType: data['event_type'] as string,
  id: data['id'] as string,
  itemsFailed: data['items_failed'] as number,
  itemsProcessed: data['items_processed'] as number,
  itemsSkipped: data['items_skipped'] as number,
  mappingId: data['mapping_id'] as string | undefined,
  provider: data['provider'] as TracerTypes.IntegrationProvider,
  startedAt: data['started_at'] as string,
  status: data['status'] as TracerTypes.SyncLog['status'],
});

const transformConflict = (data: ApiRecord): TracerTypes.SyncConflict => ({
  conflictType: data['conflict_type'] as TracerTypes.SyncConflict['conflictType'],
  createdAt: data['created_at'] as string,
  externalModifiedAt: data['external_modified_at'] as string,
  externalValue: data['external_value'],
  fieldName: data['field_name'] as string,
  id: data['id'] as string,
  localModifiedAt: data['local_modified_at'] as string,
  localValue: data['local_value'],
  mappingId: data['mapping_id'] as string,
  provider: data['provider'] as TracerTypes.IntegrationProvider,
  resolution: data['resolution'] as TracerTypes.SyncConflict['resolution'] | undefined,
  resolvedAt: data['resolved_at'] as string | undefined,
  resolvedBy: data['resolved_by'] as string | undefined,
  resolvedValue: data['resolved_value'],
  status: data['status'] as TracerTypes.SyncConflict['status'],
});

const transformSyncStatus = (data: ApiRecord): TracerTypes.SyncStatusSummary => ({
  projectId: data['project_id'] as string,
  providers: ((data['providers'] as ApiRecord[]) ?? []).map((provider) => ({
    lastValidated: (provider['last_validated'] as string | undefined) ?? undefined,
    provider: provider['provider'] as TracerTypes.IntegrationProvider,
    status: provider['status'] as TracerTypes.CredentialStatus,
  })),
  queue: data['queue'] as TracerTypes.SyncStatusSummary['queue'],
  recentSyncs: ((data['recent_syncs'] as ApiRecord[]) ?? []).map((sync) => transformSyncLog(sync)),
});

const buildConflictStats = (
  conflicts: ApiRecord | undefined,
): TracerTypes.IntegrationStats['conflicts'] => ({
  pending: toNumber(conflicts?.pending),
  resolved: toNumber(conflicts?.resolved),
});

const buildMappingsStats = (
  mappings: ApiRecord | undefined,
): TracerTypes.IntegrationStats['mappings'] => ({
  active: toNumber(mappings?.active),
  byProvider: (mappings?.by_provider as Record<string, number>) ?? {},
  total: toNumber(mappings?.total),
});

const buildProviderStats = (data: ApiRecord): TracerTypes.IntegrationStats['providers'] => {
  const providers = (data['providers'] as ApiRecord[] | undefined) ?? [];
  return providers.map((provider) => ({
    credentialType: provider['credential_type'] as TracerTypes.CredentialType,
    provider: provider['provider'] as TracerTypes.IntegrationProvider,
    status: provider['status'] as TracerTypes.CredentialStatus,
  }));
};

const buildSyncStats = (sync: ApiRecord | undefined): TracerTypes.IntegrationStats['sync'] => ({
  queuePending: toNumber(sync?.queue_pending),
  recentSyncs: toNumber(sync?.recent_syncs),
  successRate: toNumber(sync?.success_rate),
});

const transformStats = (data: ApiRecord): TracerTypes.IntegrationStats => {
  const mappings = data['mappings'] as ApiRecord | undefined;
  const sync = data['sync'] as ApiRecord | undefined;
  const conflicts = data['conflicts'] as ApiRecord | undefined;

  return {
    conflicts: buildConflictStats(conflicts),
    mappings: buildMappingsStats(mappings),
    projectId: data['project_id'] as string,
    providers: buildProviderStats(data),
    sync: buildSyncStats(sync),
  };
};

export {
  transformConflict,
  transformCredential,
  transformMapping,
  transformStats,
  transformSyncLog,
  transformSyncQueueItem,
  transformSyncStatus,
};
