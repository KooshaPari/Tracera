/**
 * Streaming API client for large data transfers using NDJSON
 */

import type { NDJSONMetadata, StreamingStats } from '../lib/ndjson-parser';
import type { Item } from './types';

import { createCancellableNDJSONStream, parseNDJSONWithProgress } from '../lib/ndjson-parser';

const API_BASE = '/api/v1';
const DEFAULT_BATCH_SIZE = 50;
const PROGRESS_UPDATE_INTERVAL = 10;
const ZERO = 0;

interface StreamItemsOptions {
  projectId?: string;
  limit?: number;
  offset?: number;
  onProgress?: (stats: StreamingStats) => void;
  onMetadata?: (metadata: NDJSONMetadata) => void;
}

interface StreamGraphOptions {
  onProgress?: (stats: StreamingStats) => void;
  onMetadata?: (metadata: NDJSONMetadata) => void;
}

interface StreamExportOptions {
  projectId: string;
  type: 'json' | 'csv';
  onProgress?: (stats: StreamingStats) => void;
  onMetadata?: (metadata: NDJSONMetadata) => void;
}

interface GraphStreamNode {
  type: 'node';
  data: unknown;
}

interface GraphStreamEdge {
  type: 'edge';
  data: unknown;
}

type GraphStreamItem = GraphStreamNode | GraphStreamEdge;

interface GraphStreamCallbacks {
  onNodesReceived?: (nodes: unknown[]) => void | Promise<void>;
  onEdgesReceived?: (edges: unknown[]) => void | Promise<void>;
}

interface CancellableNDJSONStream<ItemType> {
  stream: AsyncGenerator<ItemType, void, unknown>;
  cancel: () => void;
}

const buildItemsQueryParams = (options: StreamItemsOptions): URLSearchParams => {
  const params = new URLSearchParams();

  if (options.projectId !== undefined) {
    params.append('project_id', options.projectId);
  }
  if (options.limit !== undefined) {
    params.append('limit', options.limit.toString());
  }
  if (options.offset !== undefined) {
    params.append('offset', options.offset.toString());
  }

  return params;
};

const buildItemsStreamUrl = (options: StreamItemsOptions): string =>
  `${API_BASE}/items/stream?${buildItemsQueryParams(options).toString()}`;

const buildExportStreamUrl = (options: StreamExportOptions): string => {
  const params = new URLSearchParams({
    project_id: options.projectId,
  });

  return `${API_BASE}/export/${options.type}/stream?${params.toString()}`;
};

const fetchNDJSONResponse = async (url: string): Promise<Response> => {
  const response = await fetch(url, {
    headers: {
      Accept: 'application/x-ndjson',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response;
};

const shouldUpdateProgress = (count: number): boolean => count % PROGRESS_UPDATE_INTERVAL === ZERO;

const maybeUpdateNodes = async (
  nodes: unknown[],
  callbacks: GraphStreamCallbacks,
): Promise<void> => {
  if (shouldUpdateProgress(nodes.length) && callbacks.onNodesReceived) {
    await callbacks.onNodesReceived([...nodes]);
  }
};

const maybeUpdateEdges = async (
  edges: unknown[],
  callbacks: GraphStreamCallbacks,
): Promise<void> => {
  if (shouldUpdateProgress(edges.length) && callbacks.onEdgesReceived) {
    await callbacks.onEdgesReceived([...edges]);
  }
};

const flushGraphUpdates = async (
  nodes: unknown[],
  edges: unknown[],
  callbacks: GraphStreamCallbacks,
): Promise<void> => {
  if (callbacks.onNodesReceived) {
    await callbacks.onNodesReceived(nodes);
  }
  if (callbacks.onEdgesReceived) {
    await callbacks.onEdgesReceived(edges);
  }
};

/**
 * Stream items from the backend
 * @param options - Streaming options
 * @yields Items as they arrive
 */
const streamItems = async function* streamItems(
  options: StreamItemsOptions = {},
): AsyncGenerator<Item, void, unknown> {
  const response = await fetchNDJSONResponse(buildItemsStreamUrl(options));
  yield* parseNDJSONWithProgress<Item>(response, options.onProgress, options.onMetadata);
};

/**
 * Stream graph data (nodes and edges)
 * @param graphId - Graph ID
 * @param options - Streaming options
 * @yields Graph nodes and edges
 */
const streamGraph = async function* streamGraph(
  graphId: string,
  options: StreamGraphOptions = {},
): AsyncGenerator<GraphStreamItem, void, unknown> {
  const url = `${API_BASE}/graphs/${graphId}/stream`;
  const response = await fetchNDJSONResponse(url);
  yield* parseNDJSONWithProgress<GraphStreamItem>(response, options.onProgress, options.onMetadata);
};

/**
 * Stream export data
 * @param options - Export options
 * @yields Export data items
 */
const streamExport = async function* streamExport(
  options: StreamExportOptions,
): AsyncGenerator<unknown, void, unknown> {
  const response = await fetchNDJSONResponse(buildExportStreamUrl(options));
  yield* parseNDJSONWithProgress(response, options.onProgress, options.onMetadata);
};

/**
 * Create a cancellable item stream
 * @param options - Streaming options
 * @returns Stream and cancel function
 */
const createCancellableItemStream = (
  options: StreamItemsOptions = {},
): CancellableNDJSONStream<Item> => {
  const url = buildItemsStreamUrl(options);
  return createCancellableNDJSONStream<Item>(url);
};

/**
 * Create a cancellable graph stream
 * @param graphId - Graph ID
 * @returns Stream and cancel function
 */
const createCancellableGraphStream = (
  graphId: string,
): CancellableNDJSONStream<GraphStreamItem> => {
  const url = `${API_BASE}/graphs/${graphId}/stream`;
  return createCancellableNDJSONStream<GraphStreamItem>(url);
};

/**
 * Create a cancellable export stream
 * @param options - Export options
 * @returns Stream and cancel function
 */
const createCancellableExportStream = (
  options: StreamExportOptions,
): CancellableNDJSONStream<unknown> => createCancellableNDJSONStream(buildExportStreamUrl(options));

/**
 * Load items with streaming and batching
 * @param options - Streaming options
 * @param batchCallback - Called for each batch of items
 */
const loadItemsInBatches = async (
  options: StreamItemsOptions & { batchSize?: number },
  batchCallback: (items: Item[]) => void | Promise<void>,
): Promise<void> => {
  const batchSize = options.batchSize ?? DEFAULT_BATCH_SIZE;
  let batch: Item[] = [];

  for await (const item of streamItems(options)) {
    batch.push(item);

    if (batch.length >= batchSize) {
      await batchCallback(batch);
      batch = [];
    }
  }

  // Process remaining items
  if (batch.length > ZERO) {
    await batchCallback(batch);
  }
};

/**
 * Load graph data with streaming and progressive rendering
 * @param graphId - Graph ID
 * @param options - Streaming options
 * @param callbacks - Callbacks for nodes and edges
 */
const loadGraphProgressive = async (
  graphId: string,
  options: StreamGraphOptions,
  callbacks: GraphStreamCallbacks,
): Promise<void> => {
  const nodes: unknown[] = [];
  const edges: unknown[] = [];

  for await (const item of streamGraph(graphId, options)) {
    if (item.type === 'node') {
      nodes.push(item.data);
      await maybeUpdateNodes(nodes, callbacks);
    } else if (item.type === 'edge') {
      edges.push(item.data);
      await maybeUpdateEdges(edges, callbacks);
    }
  }

  await flushGraphUpdates(nodes, edges, callbacks);
};

export {
  createCancellableExportStream,
  createCancellableGraphStream,
  createCancellableItemStream,
  loadGraphProgressive,
  loadItemsInBatches,
  streamExport,
  streamGraph,
  streamItems,
  type GraphStreamItem,
  type StreamExportOptions,
  type StreamGraphOptions,
  type StreamItemsOptions,
};
