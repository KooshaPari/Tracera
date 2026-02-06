/**
 * NDJSON (Newline Delimited JSON) Parser for streaming large datasets
 *
 * Usage:
 * ```typescript
 * const response = await fetch('/api/v1/items/stream');
 * for await (const item of parseNDJSON(response)) {
 *   console.log(item);
 * }
 * ```
 */

export interface NDJSONProgressEvent {
  type: 'progress';
  count: number;
  offset?: number;
  section?: string;
  total?: number;
}

export interface NDJSONCompleteEvent {
  type: 'complete';
  total_count?: number;
  count?: number;
  nodes?: number;
  edges?: number;
}

export interface NDJSONErrorEvent {
  type: 'error';
  error: string;
}

export interface NDJSONSectionEvent {
  type: 'section';
  name: string;
  count: number;
}

export type NDJSONMetadata =
  | NDJSONProgressEvent
  | NDJSONCompleteEvent
  | NDJSONErrorEvent
  | NDJSONSectionEvent;

export interface StreamingStats {
  bytesReceived: number;
  itemsReceived: number;
  startTime: number;
  endTime?: number;
  errors: string[];
}

/**
 * Parse NDJSON stream from a Response object
 * @param response - Fetch API Response object
 * @yields Parsed JSON objects from each line
 */
export async function* parseNDJSON<T = any>(response: Response): AsyncGenerator<T, void, unknown> {
  if (!response.body) {
    throw new Error('Response body is null');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        // Process any remaining data in buffer
        if (buffer.trim()) {
          try {
            yield JSON.parse(buffer) as T;
          } catch (err) {
            console.error('Failed to parse final NDJSON line:', err);
          }
        }
        break;
      }

      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Split by newlines
      const lines = buffer.split('\n');

      // Keep the last incomplete line in buffer
      buffer = lines.pop() || '';

      // Parse and yield each complete line
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed) {
          try {
            yield JSON.parse(trimmed) as T;
          } catch (err) {
            console.error('Failed to parse NDJSON line:', err, 'Line:', trimmed);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Parse NDJSON stream with progress tracking
 * @param response - Fetch API Response object
 * @param onProgress - Optional progress callback
 * @param onMetadata - Optional metadata callback for non-data events
 * @yields Parsed JSON objects (excluding metadata events)
 */
export async function* parseNDJSONWithProgress<T = any>(
  response: Response,
  onProgress?: (stats: StreamingStats) => void,
  onMetadata?: (metadata: NDJSONMetadata) => void,
): AsyncGenerator<T, void, unknown> {
  const stats: StreamingStats = {
    bytesReceived: 0,
    itemsReceived: 0,
    startTime: Date.now(),
    errors: [],
  };

  for await (const item of parseNDJSON<T | NDJSONMetadata>(response)) {
    // Update stats
    stats.bytesReceived += JSON.stringify(item).length;
    stats.itemsReceived++;

    // Handle metadata events
    if (typeof item === 'object' && item !== null && 'type' in item) {
      const metadata = item as NDJSONMetadata;

      switch (metadata.type) {
        case 'progress':
          if (onProgress) {
            onProgress({ ...stats });
          }
          if (onMetadata) {
            onMetadata(metadata);
          }
          continue; // Don't yield progress events

        case 'complete':
          stats.endTime = Date.now();
          if (onProgress) {
            onProgress({ ...stats });
          }
          if (onMetadata) {
            onMetadata(metadata);
          }
          continue; // Don't yield complete events

        case 'error':
          stats.errors.push(metadata.error);
          if (onMetadata) {
            onMetadata(metadata);
          }
          continue; // Don't yield error events

        case 'section':
          if (onMetadata) {
            onMetadata(metadata);
          }
          continue; // Don't yield section events

        default:
          // Regular data item, yield it
          yield item as T;
      }
    } else {
      // Regular data item without type field
      yield item as T;
    }
  }

  // Final stats update
  stats.endTime = Date.now();
  if (onProgress) {
    onProgress(stats);
  }
}

/**
 * Fetch and parse NDJSON stream
 * @param url - URL to fetch
 * @param options - Fetch options
 * @yields Parsed JSON objects
 */
export async function* fetchNDJSON<T = any>(
  url: string,
  options?: RequestInit,
): AsyncGenerator<T, void, unknown> {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/x-ndjson',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  yield* parseNDJSON<T>(response);
}

/**
 * Collect all items from NDJSON stream into an array
 * @param stream - NDJSON stream generator
 * @param maxItems - Optional maximum number of items to collect
 * @returns Array of collected items
 */
export async function collectNDJSON<T = any>(
  stream: AsyncGenerator<T, void, unknown>,
  maxItems?: number,
): Promise<T[]> {
  const items: T[] = [];
  let count = 0;

  for await (const item of stream) {
    items.push(item);
    count++;

    if (maxItems && count >= maxItems) {
      break;
    }
  }

  return items;
}

/**
 * Create a cancellable NDJSON stream
 * @param url - URL to fetch
 * @param options - Fetch options
 * @returns Object with stream generator and cancel function
 */
export function createCancellableNDJSONStream<T = any>(url: string, options?: RequestInit) {
  const abortController = new AbortController();

  const stream = fetchNDJSON<T>(url, {
    ...options,
    signal: abortController.signal,
  });

  return {
    stream,
    cancel: () => abortController.abort(),
  };
}

/**
 * Batch NDJSON stream items
 * @param stream - NDJSON stream generator
 * @param batchSize - Size of each batch
 * @yields Arrays of items
 */
export async function* batchNDJSON<T = any>(
  stream: AsyncGenerator<T, void, unknown>,
  batchSize: number,
): AsyncGenerator<T[], void, unknown> {
  let batch: T[] = [];

  for await (const item of stream) {
    batch.push(item);

    if (batch.length >= batchSize) {
      yield batch;
      batch = [];
    }
  }

  // Yield remaining items
  if (batch.length > 0) {
    yield batch;
  }
}

/**
 * Filter NDJSON stream
 * @param stream - NDJSON stream generator
 * @param predicate - Filter function
 * @yields Filtered items
 */
export async function* filterNDJSON<T = any>(
  stream: AsyncGenerator<T, void, unknown>,
  predicate: (item: T) => boolean,
): AsyncGenerator<T, void, unknown> {
  for await (const item of stream) {
    if (predicate(item)) {
      yield item;
    }
  }
}

/**
 * Map NDJSON stream
 * @param stream - NDJSON stream generator
 * @param mapper - Map function
 * @yields Mapped items
 */
export async function* mapNDJSON<T = any, U = any>(
  stream: AsyncGenerator<T, void, unknown>,
  mapper: (item: T) => U | Promise<U>,
): AsyncGenerator<U, void, unknown> {
  for await (const item of stream) {
    yield await mapper(item);
  }
}

/**
 * Calculate streaming throughput
 * @param stats - Streaming statistics
 * @returns Throughput metrics
 */
export function calculateThroughput(stats: StreamingStats) {
  const duration = (stats.endTime || Date.now()) - stats.startTime;
  const durationSeconds = duration / 1000;

  return {
    itemsPerSecond: stats.itemsReceived / durationSeconds,
    bytesPerSecond: stats.bytesReceived / durationSeconds,
    megabytesPerSecond: stats.bytesReceived / durationSeconds / 1024 / 1024,
    totalDurationMs: duration,
  };
}
