import * as ReactQuery from '@tanstack/react-query';

import { client } from '@/api/client';
import { QUERY_CONFIGS, queryKeys } from '@/lib/queryConfig';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

type GraphNode = Record<string, unknown>;
type GraphLink = Record<string, unknown>;

interface GraphSummary {
  id: string;
  name: string;
  graphType: string;
  description?: string | null | undefined;
  rootItemId?: string | null | undefined;
  graphVersion?: number | undefined;
  graphRules?: Record<string, unknown> | undefined;
  metadata?: Record<string, unknown> | undefined;
}

interface GraphProjection {
  graph?: GraphSummary | undefined;
  nodes: GraphNode[];
  links: GraphLink[];
}

type UnknownRecord = Record<string, unknown>;

const isRecord = (value: unknown): value is UnknownRecord =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const hasText = (value: string | undefined): value is string =>
  typeof value === 'string' && value.length > 0;

const pickValue = (record: UnknownRecord, keys: readonly string[]): unknown => {
  for (const key of keys) {
    const candidate = record[key];
    if (candidate !== undefined) {
      return candidate;
    }
  }
  return undefined;
};

const pickString = (record: UnknownRecord, keys: readonly string[], fallback = ''): string => {
  const value = pickValue(record, keys);
  return typeof value === 'string' ? value : fallback;
};

const pickNullableString = (
  record: UnknownRecord,
  keys: readonly string[],
): string | null | undefined => {
  const value = pickValue(record, keys);
  if (typeof value === 'string') {
    return value;
  }
  if (value === null) {
    return null;
  }
  return undefined;
};

const pickNumber = (record: UnknownRecord, keys: readonly string[]): number | undefined => {
  const value = pickValue(record, keys);
  return typeof value === 'number' ? value : undefined;
};

const pickRecord = (
  record: UnknownRecord,
  keys: readonly string[],
): Record<string, unknown> | undefined => {
  const value = pickValue(record, keys);
  return isRecord(value) ? value : undefined;
};

const normalizeGraphSummary = (record: UnknownRecord): GraphSummary => ({
  description: pickNullableString(record, ['description']),
  graphRules: pickRecord(record, ['graph_rules', 'graphRules']),
  graphType: pickString(record, ['graph_type', 'graphType']),
  graphVersion: pickNumber(record, ['graph_version', 'graphVersion']),
  id: pickString(record, ['id']),
  metadata: pickRecord(record, ['metadata', 'graph_metadata', 'graphMetadata']),
  name: pickString(record, ['name']),
  rootItemId: pickNullableString(record, ['root_item_id', 'rootItemId']),
});

const toRecordArray = (value: unknown): UnknownRecord[] => {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((entry) => isRecord(entry));
};

async function fetchGraphs(projectId: string): Promise<GraphSummary[]> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/graphs`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch graphs');
  }
  const payload: unknown = await res.json();
  const payloadRecord = isRecord(payload) ? payload : undefined;
  const graphs = toRecordArray(payloadRecord?.['graphs']);
  return graphs.map((graph) => normalizeGraphSummary(graph));
}

async function fetchGraphProjection(
  projectId: string,
  graphId?: string,
  graphType?: string,
): Promise<GraphProjection> {
  const params = new URLSearchParams();
  if (hasText(graphId)) {
    params.set('graph_id', graphId);
  }
  if (hasText(graphType)) {
    params.set('graph_type', graphType);
  }
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/graph?${params}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch graph projection');
  }
  const payload: unknown = await res.json();
  const payloadRecord = isRecord(payload) ? payload : undefined;
  const graphRecord = isRecord(payloadRecord?.['graph']) ? payloadRecord['graph'] : undefined;
  return {
    graph: graphRecord ? normalizeGraphSummary(graphRecord) : undefined,
    links: toRecordArray(payloadRecord?.['links']),
    nodes: toRecordArray(payloadRecord?.['nodes']),
  };
}

const useGraphs = (projectId?: string): ReactQuery.UseQueryResult<GraphSummary[]> =>
  ReactQuery.useQuery<GraphSummary[]>({
    queryKey: hasText(projectId) ? queryKeys.graph.full(projectId) : ['graphs'],
    queryFn: async () => fetchGraphs(projectId ?? ''),
    enabled: hasText(projectId),
    ...QUERY_CONFIGS.graph, // Graph data is expensive, cache longer
  });

const useGraphProjection = (
  projectId?: string,
  graphId?: string,
  graphType?: string,
): ReactQuery.UseQueryResult<GraphProjection> =>
  ReactQuery.useQuery<GraphProjection>({
    queryKey: hasText(projectId)
      ? [...queryKeys.graph.full(projectId), graphId, graphType]
      : ['graph', graphId, graphType],
    queryFn: async () => fetchGraphProjection(projectId ?? '', graphId, graphType),
    enabled: hasText(projectId) && (hasText(graphId) || hasText(graphType)),
    ...QUERY_CONFIGS.graph, // Graph projections are expensive, cache longer
  });

export {
  useGraphProjection,
  useGraphs,
  type GraphLink,
  type GraphNode,
  type GraphProjection,
  type GraphSummary,
};
