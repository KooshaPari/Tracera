import type * as TracerTypes from '@tracertm/types';

type ApiRecord = Readonly<Record<string, unknown>>;

const INTEGRATION_PROVIDERS = ['github', 'github_projects', 'linear'] as const;
const CREDENTIAL_TYPES = ['oauth', 'pat', 'api_key'] as const;
const CREDENTIAL_STATUSES = ['active', 'expired', 'revoked', 'invalid', 'pending_reauth'] as const;
const MAPPING_DIRECTIONS = ['pull', 'push', 'bidirectional'] as const;
const MAPPING_STATUSES = ['active', 'paused', 'error', 'pending'] as const;
const SYNC_QUEUE_STATUSES = ['pending', 'processing', 'completed', 'failed', 'cancelled'] as const;
const CONFLICT_STATUSES = ['pending', 'resolved', 'skipped'] as const;
const CONFLICT_RESOLUTION_STRATEGIES = [
  'local_wins',
  'external_wins',
  'manual',
  'merge',
  'skip',
] as const;

const isRecord = (value: unknown): value is ApiRecord =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const isEnumValue = <Value extends string>(
  value: unknown,
  allowedValues: readonly Value[],
): value is Value => typeof value === 'string' && (allowedValues as readonly string[]).includes(value);

const toNumber = (value: unknown): number => Number(value ?? 0);

const readString = (record: ApiRecord, key: string): string => {
  const value = record[key];
  return typeof value === 'string' ? value : '';
};

const readOptionalString = (record: ApiRecord, key: string): string | undefined => {
  const value = record[key];
  return typeof value === 'string' ? value : undefined;
};

const readNumber = (record: ApiRecord, key: string): number => {
  const value = record[key];
  return typeof value === 'number' ? value : toNumber(value);
};

const readOptionalNumber = (record: ApiRecord, key: string): number | undefined => {
  const value = record[key];
  return typeof value === 'number' ? value : undefined;
};

const readBoolean = (record: ApiRecord, key: string): boolean => record[key] === true;

const readRecord = (record: ApiRecord, key: string): ApiRecord | undefined => {
  const value = record[key];
  return isRecord(value) ? value : undefined;
};

const readStringArray = (record: ApiRecord, key: string): string[] => {
  const value = record[key];
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter((item): item is string => typeof item === 'string');
};

const readRecordArray = (record: ApiRecord, key: string): ApiRecord[] => {
  const value = record[key];
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter((item): item is ApiRecord => isRecord(item));
};

const readUnknownRecord = (record: ApiRecord, key: string): Record<string, unknown> | undefined => {
  const value = readRecord(record, key);
  return value ? { ...value } : undefined;
};

const readStringRecord = (record: ApiRecord, key: string): Record<string, string> | undefined => {
  const value = readRecord(record, key);
  if (!value) {
    return undefined;
  }

  const filtered: [string, string][] = [];
  for (const [k, v] of Object.entries(value)) {
    if (typeof v === 'string') {
      filtered.push([k, v]);
    }
  }
  return Object.fromEntries(filtered) as Record<string, string>;
};

const readNumberRecord = (record: ApiRecord, key: string): Record<string, number> => {
  const value = readRecord(record, key);
  if (!value) {
    return {};
  }

  return Object.fromEntries(
    Object.entries(value).flatMap(([entryKey, entryValue]) =>
      typeof entryValue === 'number' ? [[entryKey, entryValue] as const] : [],
    ),
  );
};

const readConflictResolutionRecord = (
  record: ApiRecord,
  key: string,
): Record<string, TracerTypes.ConflictResolutionStrategy> | undefined => {
  const value = readRecord(record, key);
  if (!value) {
    return undefined;
  }

  return Object.fromEntries(
    Object.entries(value).flatMap(([entryKey, entryValue]) =>
      isEnumValue(entryValue, CONFLICT_RESOLUTION_STRATEGIES)
        ? [[entryKey, entryValue] as const]
        : [],
    ),
  );
};

const readEnum = <Value extends string>(
  record: ApiRecord,
  key: string,
  allowedValues: readonly Value[],
  fallback: Value,
): Value => {
  const value = record[key];
  return isEnumValue(value, allowedValues) ? value : fallback;
};

const transformCredential = (data: ApiRecord): TracerTypes.IntegrationCredential => ({
  createdAt: readString(data, 'created_at'),
  credentialType: readEnum(data, 'credential_type', CREDENTIAL_TYPES, 'oauth'),
  expiresAt: readOptionalString(data, 'expires_at'),
  id: readString(data, 'id'),
  lastValidatedAt: readOptionalString(data, 'last_validated_at'),
  projectId: readOptionalString(data, 'project_id'),
  provider: readEnum(data, 'provider', INTEGRATION_PROVIDERS, 'github'),
  providerMetadata: readUnknownRecord(data, 'provider_metadata'),
  providerUserId: readOptionalString(data, 'provider_user_id'),
  scopes: readStringArray(data, 'scopes'),
  status: readEnum(data, 'status', CREDENTIAL_STATUSES, 'active'),
  updatedAt: readString(data, 'updated_at'),
  validationError: readOptionalString(data, 'validation_error'),
});

const transformMapping = (data: ApiRecord): TracerTypes.IntegrationMapping => ({
  createdAt: readString(data, 'created_at'),
  credentialId: readString(data, 'credential_id'),
  direction: readEnum(data, 'direction', MAPPING_DIRECTIONS, 'pull'),
  externalId: readString(data, 'external_id'),
  externalKey: readOptionalString(data, 'external_key'),
  externalType: readString(data, 'external_type'),
  externalUrl: readOptionalString(data, 'external_url'),
  externalVersion: readOptionalString(data, 'external_version'),
  fieldMappings: readStringRecord(data, 'field_mappings'),
  fieldResolutionRules: readConflictResolutionRecord(data, 'field_resolution_rules'),
  id: readString(data, 'id'),
  lastSyncError: readOptionalString(data, 'last_sync_error'),
  lastSyncStatus: readOptionalString(data, 'last_sync_status'),
  lastSyncedAt: readOptionalString(data, 'last_synced_at'),
  localItemId: readString(data, 'local_item_id'),
  localItemType: readString(data, 'local_item_type'),
  localVersion: readOptionalNumber(data, 'local_version'),
  mappingMetadata: readUnknownRecord(data, 'mapping_metadata'),
  provider: readEnum(data, 'provider', INTEGRATION_PROVIDERS, 'github'),
  status: readEnum(data, 'status', MAPPING_STATUSES, 'active'),
  syncEnabled: readBoolean(data, 'sync_enabled'),
  updatedAt: readString(data, 'updated_at'),
});

const transformSyncQueueItem = (data: ApiRecord): TracerTypes.SyncQueueItem => ({
  completedAt: readOptionalString(data, 'completed_at'),
  createdAt: readString(data, 'created_at'),
  credentialId: readOptionalString(data, 'credential_id'),
  direction: readEnum(data, 'direction', MAPPING_DIRECTIONS, 'pull'),
  errorMessage: readOptionalString(data, 'error_message'),
  eventType: readString(data, 'event_type'),
  id: readString(data, 'id'),
  mappingId: readOptionalString(data, 'mapping_id'),
  maxRetries: readNumber(data, 'max_retries'),
  priority: readNumber(data, 'priority'),
  provider: readEnum(data, 'provider', INTEGRATION_PROVIDERS, 'github'),
  retryCount: readNumber(data, 'retry_count'),
  scheduledAt: readOptionalString(data, 'scheduled_at'),
  startedAt: readOptionalString(data, 'started_at'),
  status: readEnum(data, 'status', SYNC_QUEUE_STATUSES, 'pending'),
});

const transformSyncLog = (data: ApiRecord): TracerTypes.SyncLog => ({
  completedAt: readOptionalString(data, 'completed_at'),
  createdAt: readString(data, 'created_at'),
  credentialId: readOptionalString(data, 'credential_id'),
  direction: readEnum(data, 'direction', MAPPING_DIRECTIONS, 'pull'),
  durationMs: readOptionalNumber(data, 'duration_ms'),
  errorMessage: readOptionalString(data, 'error_message'),
  eventType: readString(data, 'event_type'),
  id: readString(data, 'id'),
  itemsFailed: readNumber(data, 'items_failed'),
  itemsProcessed: readNumber(data, 'items_processed'),
  itemsSkipped: readNumber(data, 'items_skipped'),
  mappingId: readOptionalString(data, 'mapping_id'),
  provider: readEnum(data, 'provider', INTEGRATION_PROVIDERS, 'github'),
  startedAt: readOptionalString(data, 'started_at'),
  status: readString(data, 'status'),
});

const transformConflict = (data: ApiRecord): TracerTypes.SyncConflict => ({
  conflictType: readString(data, 'conflict_type'),
  createdAt: readString(data, 'created_at'),
  externalModifiedAt: readOptionalString(data, 'external_modified_at'),
  externalValue: data['external_value'],
  fieldName: readOptionalString(data, 'field_name'),
  id: readString(data, 'id'),
  localModifiedAt: readOptionalString(data, 'local_modified_at'),
  localValue: data['local_value'],
  mappingId: readString(data, 'mapping_id'),
  provider: readEnum(data, 'provider', INTEGRATION_PROVIDERS, 'github'),
  resolution: readOptionalString(data, 'resolution'),
  resolvedAt: readOptionalString(data, 'resolved_at'),
  resolvedBy: readOptionalString(data, 'resolved_by'),
  resolvedValue: data['resolved_value'],
  status: readEnum(data, 'status', CONFLICT_STATUSES, 'pending'),
});

const transformSyncStatus = (data: ApiRecord): TracerTypes.SyncStatusSummary => {
  const queue = readRecord(data, 'queue');

  return {
    projectId: readString(data, 'project_id'),
    providers: readRecordArray(data, 'providers').map((provider) => ({
      lastValidated: readOptionalString(provider, 'last_validated'),
      provider: readEnum(provider, 'provider', INTEGRATION_PROVIDERS, 'github'),
      status: readEnum(provider, 'status', CREDENTIAL_STATUSES, 'active'),
    })),
    queue: {
      completed: toNumber(queue?.['completed']),
      failed: toNumber(queue?.['failed']),
      pending: toNumber(queue?.['pending']),
      processing: toNumber(queue?.['processing']),
    },
    recentSyncs: readRecordArray(data, 'recent_syncs').map((sync) => transformSyncLog(sync)),
  };
};

const buildConflictStats = (
  conflicts: ApiRecord | undefined,
): TracerTypes.IntegrationStats['conflicts'] => ({
  pending: toNumber(conflicts?.['pending']),
  resolved: toNumber(conflicts?.['resolved']),
});

const buildMappingsStats = (
  mappings: ApiRecord | undefined,
): TracerTypes.IntegrationStats['mappings'] => ({
  active: toNumber(mappings?.['active']),
  byProvider: mappings ? readNumberRecord(mappings, 'by_provider') : {},
  total: toNumber(mappings?.['total']),
});

const buildProviderStats = (data: ApiRecord): TracerTypes.IntegrationStats['providers'] => {
  const providers = readRecordArray(data, 'providers');
  return providers.map((provider) => ({
    credentialType: readEnum(provider, 'credential_type', CREDENTIAL_TYPES, 'oauth'),
    provider: readEnum(provider, 'provider', INTEGRATION_PROVIDERS, 'github'),
    status: readEnum(provider, 'status', CREDENTIAL_STATUSES, 'active'),
  }));
};

const buildSyncStats = (sync: ApiRecord | undefined): TracerTypes.IntegrationStats['sync'] => ({
  queuePending: toNumber(sync?.['queue_pending']),
  recentSyncs: toNumber(sync?.['recent_syncs']),
  successRate: toNumber(sync?.['success_rate']),
});

const transformStats = (data: ApiRecord): TracerTypes.IntegrationStats => {
  const mappings = readRecord(data, 'mappings');
  const sync = readRecord(data, 'sync');
  const conflicts = readRecord(data, 'conflicts');

  return {
    conflicts: buildConflictStats(conflicts),
    mappings: buildMappingsStats(mappings),
    projectId: readString(data, 'project_id'),
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
