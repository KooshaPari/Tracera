import type { Item } from '@tracertm/types';

import type { DimensionEntry, ItemLink, TimelineEvent } from './types';

type MetadataEntry = [string, unknown];

const EM_DASH = '–';
const UNKNOWN_LABEL = 'Unknown';
const DEFAULT_VIEW_TYPE = 'feature';

const SHORT_ID_LENGTH = 8;
const SORT_DESCENDING = -1;
const SORT_ASCENDING = 1;

const INTEGRATION_KEYS = new Set<string>([
  'external_system',
  'external_id',
  'external_key',
  'external_url',
  'repo_full_name',
  'issue_number',
  'state',
  'labels',
  'projectId',
  'team_id',
  'identifier',
  'url',
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  if (value === null) {
    return false;
  }
  return typeof value === 'object';
}

function readNonEmptyString(value: unknown): string | undefined {
  if (typeof value !== 'string') {
    return;
  }
  const trimmed = value.trim();
  if (trimmed.length === 0) {
    return;
  }
  return trimmed;
}

function readStringParam(params: unknown, key: string): string | undefined {
  if (!isRecord(params)) {
    return;
  }
  return readNonEmptyString(params[key]);
}

function objectToString(value: object): string {
  return String(Object.prototype.toString.call(value));
}

function formatPrimitive(value: Exclude<unknown, object>): string {
  if (typeof value === 'string') {
    return value;
  }
  if (typeof value === 'number' || typeof value === 'boolean' || typeof value === 'bigint') {
    return String(value);
  }
  if (typeof value === 'symbol') {
    return value.description ?? value.toString();
  }
  if (typeof value === 'function') {
    return '[function]';
  }
  return EM_DASH;
}

function formatObjectValue(value: object): string {
  try {
    return JSON.stringify(value);
  } catch {
    return objectToString(value);
  }
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return EM_DASH;
  }
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (typeof value === 'object') {
    return formatObjectValue(value);
  }
  return formatPrimitive(value);
}

function defaultViewTypeFromParams(viewTypeParam: string | undefined, itemView: unknown): string {
  const fromParam = readNonEmptyString(viewTypeParam);
  if (fromParam !== undefined) {
    return fromParam.toLowerCase();
  }
  if (typeof itemView === 'string') {
    const normalized = readNonEmptyString(itemView);
    if (normalized !== undefined) {
      return normalized.toLowerCase();
    }
  }
  return DEFAULT_VIEW_TYPE;
}

function buildItemLink(projectId: string | undefined, viewType: string, id: string): string {
  if (projectId === undefined) {
    return '/projects';
  }
  return `/projects/${projectId}/views/${viewType}/${id}`;
}

function shortId(id: string): string {
  return `${id.slice(0, SHORT_ID_LENGTH)}…`;
}

function metadataEntries(item: Item | undefined): MetadataEntry[] {
  if (!item) {
    return [];
  }
  const { metadata } = item;
  if (metadata === null || metadata === undefined) {
    return [];
  }
  if (!isRecord(metadata)) {
    return [];
  }
  return Object.entries(metadata);
}

function filterMetadata(entries: MetadataEntry[], query: string): MetadataEntry[] {
  const trimmed = query.trim();
  if (trimmed.length === 0) {
    return entries;
  }
  const needle = trimmed.toLowerCase();
  return entries.filter(([key, value]) => {
    const haystack = `${key} ${formatValue(value)}`.toLowerCase();
    return haystack.includes(needle);
  });
}

function splitMetadata(entries: MetadataEntry[]): {
  integration: MetadataEntry[];
  general: MetadataEntry[];
} {
  const integration: MetadataEntry[] = [];
  const general: MetadataEntry[] = [];
  for (const entry of entries) {
    const [key] = entry;
    if (INTEGRATION_KEYS.has(key)) {
      integration.push(entry);
    } else {
      general.push(entry);
    }
  }
  return { integration, general };
}

function dimensionEntries(item: Item | undefined): DimensionEntry[] {
  if (!item) {
    return [];
  }
  const dims = item.dimensions;
  if (dims === null || dims === undefined) {
    return [];
  }

  const entries: DimensionEntry[] = [];
  const baseEntries: readonly [string, unknown][] = [
    ['Maturity', dims.maturity],
    ['Complexity', dims.complexity],
    ['Risk', dims.risk],
    ['Coverage', dims.coverage],
  ];
  for (const [label, value] of baseEntries) {
    if (value !== undefined) {
      entries.push([label, value]);
    }
  }
  if (dims.custom !== undefined && isRecord(dims.custom)) {
    for (const [key, value] of Object.entries(dims.custom)) {
      entries.push([key, value]);
    }
  }
  return entries;
}

function buildCreatedEvent(item: Item, createdAt: string): TimelineEvent {
  let statusLabel = UNKNOWN_LABEL;
  if (typeof item.status === 'string') {
    statusLabel = item.status;
  }
  return {
    label: 'Item created',
    timestamp: createdAt,
    detail: `Status: ${statusLabel}`,
  };
}

function buildUpdatedEvent(item: Item, updatedAt: string): TimelineEvent {
  return {
    label: 'Item updated',
    timestamp: updatedAt,
    detail: `v${String(item.version)}`,
  };
}

function buildVersionBumpEvent(item: Item, updatedAt: string): TimelineEvent {
  return {
    label: 'Version bump',
    timestamp: updatedAt,
    detail: `Now at v${String(item.version)}`,
  };
}

function buildExternalSyncEvent(
  updatedAt: string,
  integrationEntriesList: MetadataEntry[],
): TimelineEvent {
  let foundSystemValue = false;
  let systemValue: unknown = undefined;
  for (const [key, value] of integrationEntriesList) {
    if (key === 'external_system') {
      systemValue = value;
      foundSystemValue = true;
      break;
    }
  }

  let detail = 'Integration data attached';
  if (foundSystemValue) {
    detail = `System: ${formatValue(systemValue)}`;
  }

  return {
    label: 'External sync',
    timestamp: updatedAt,
    detail,
  };
}

function buildTimelineEvents(
  item: Item | undefined,
  integrationEntriesList: MetadataEntry[],
): TimelineEvent[] {
  if (!item) {
    return [];
  }
  const events: TimelineEvent[] = [];

  const createdAt = readNonEmptyString(item.createdAt);
  if (createdAt !== undefined) {
    events.push(buildCreatedEvent(item, createdAt));
  }

  const updatedAt = readNonEmptyString(item.updatedAt);
  if (updatedAt !== undefined) {
    events.push(buildUpdatedEvent(item, updatedAt));
  }

  if (typeof item.version === 'number' && item.version > 1 && updatedAt !== undefined) {
    events.push(buildVersionBumpEvent(item, updatedAt));
  }

  if (integrationEntriesList.length > 0 && updatedAt !== undefined) {
    events.push(buildExternalSyncEvent(updatedAt, integrationEntriesList));
  }

  return [...events].toSorted((first, second) => {
    if (first.timestamp < second.timestamp) {
      return SORT_DESCENDING;
    }
    if (first.timestamp > second.timestamp) {
      return SORT_ASCENDING;
    }
    return 0;
  });
}

function createdAtLabel(item: Item | undefined): string {
  const value = readNonEmptyString(item?.createdAt);
  if (value === undefined) {
    return UNKNOWN_LABEL;
  }
  return new Date(value).toLocaleDateString();
}

function updatedAtLabel(item: Item | undefined): string {
  const value = readNonEmptyString(item?.updatedAt);
  if (value === undefined) {
    return UNKNOWN_LABEL;
  }
  return new Date(value).toLocaleString();
}

function readLinksFromResponse(data: unknown): ItemLink[] {
  if (!isRecord(data)) {
    return [];
  }
  const { links } = data;
  if (!Array.isArray(links)) {
    return [];
  }
  const results: ItemLink[] = [];
  for (const entry of links) {
    if (isRecord(entry)) {
      const { id, type, sourceId, targetId } = entry;
      const safeId = readNonEmptyString(id);
      const safeType = readNonEmptyString(type);
      const safeSourceId = readNonEmptyString(sourceId);
      const safeTargetId = readNonEmptyString(targetId);
      if (
        safeId !== undefined &&
        safeType !== undefined &&
        safeSourceId !== undefined &&
        safeTargetId !== undefined
      ) {
        results.push({
          id: safeId,
          type: safeType,
          sourceId: safeSourceId,
          targetId: safeTargetId,
        });
      }
    }
  }
  return results;
}

export {
  buildItemLink,
  buildTimelineEvents,
  createdAtLabel,
  defaultViewTypeFromParams,
  dimensionEntries,
  filterMetadata,
  formatValue,
  metadataEntries,
  readLinksFromResponse,
  readNonEmptyString,
  readStringParam,
  shortId,
  splitMetadata,
  updatedAtLabel,
};
