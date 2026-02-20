/**
 * Tests for NDJSON parser utility
 */

import { describe, it, expect, vi } from 'vitest';

import {
  parseNDJSON,
  parseNDJSONWithProgress,
  collectNDJSON,
  batchNDJSON,
  filterNDJSON,
  mapNDJSON,
  calculateThroughput,
  type StreamingStats,
  type NDJSONProgressEvent,
  type NDJSONCompleteEvent,
} from '../ndjson-parser';

// Helper to create a mock Response with NDJSON data
function createNDJSONResponse(lines: string[]): Response {
  const ndjsonData = lines.join('\n') + '\n';
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(ndjsonData));
      controller.close();
    },
  });

  return new Response(stream, {
    headers: { 'Content-Type': 'application/x-ndjson' },
  });
}

describe('parseNDJSON', () => {
  it('should parse basic NDJSON stream', async () => {
    const lines = [
      '{"id": 1, "name": "Item 1"}',
      '{"id": 2, "name": "Item 2"}',
      '{"id": 3, "name": "Item 3"}',
    ];

    const response = createNDJSONResponse(lines);
    const items = [];

    for await (const item of parseNDJSON(response)) {
      items.push(item);
    }

    expect(items).toHaveLength(3);
    expect(items[0]).toEqual({ id: 1, name: 'Item 1' });
    expect(items[1]).toEqual({ id: 2, name: 'Item 2' });
    expect(items[2]).toEqual({ id: 3, name: 'Item 3' });
  });

  it('should handle empty lines', async () => {
    const lines = ['{"id": 1}', '', '{"id": 2}', '   ', '{"id": 3}'];

    const response = createNDJSONResponse(lines);
    const items = [];

    for await (const item of parseNDJSON(response)) {
      items.push(item);
    }

    expect(items).toHaveLength(3);
  });

  it('should handle chunked data', async () => {
    const encoder = new TextEncoder();
    const chunks = ['{"id": 1}\n', '{"id": 2', '}\n{"id": 3}\n'];

    const stream = new ReadableStream({
      start(controller) {
        for (const chunk of chunks) {
          controller.enqueue(encoder.encode(chunk));
        }
        controller.close();
      },
    });

    const response = new Response(stream);
    const items = [];

    for await (const item of parseNDJSON(response)) {
      items.push(item);
    }

    expect(items).toHaveLength(3);
  });

  it('should handle response without body', async () => {
    const response = new Response(null);

    const promise = (async () => {
      for await (const _item of parseNDJSON(response)) {
        // Should throw
      }
    })();

    await expect(promise).rejects.toThrow('Response body is null');
  });
});

describe('parseNDJSONWithProgress', () => {
  it('should track progress events', async () => {
    const lines = [
      '{"id": 1}',
      '{"type": "progress", "count": 1}',
      '{"id": 2}',
      '{"type": "complete", "total_count": 2}',
    ];

    const response = createNDJSONResponse(lines);
    const items: any[] = [];
    const progressEvents: any[] = [];
    const metadataEvents: any[] = [];

    for await (const item of parseNDJSONWithProgress(
      response,
      (stats) => progressEvents.push({ ...stats }),
      (metadata) => metadataEvents.push(metadata),
    )) {
      items.push(item);
    }

    expect(items).toHaveLength(2); // Only data items, not metadata
    expect(metadataEvents).toHaveLength(2); // Progress and complete events
    expect(metadataEvents[0].type).toBe('progress');
    expect(metadataEvents[1].type).toBe('complete');
  });

  it('should filter out metadata events', async () => {
    const lines = [
      '{"id": 1, "data": "item1"}',
      '{"type": "progress", "count": 1}',
      '{"id": 2, "data": "item2"}',
      '{"type": "section", "name": "nodes", "count": 2}',
      '{"id": 3, "data": "item3"}',
      '{"type": "complete", "total_count": 3}',
    ];

    const response = createNDJSONResponse(lines);
    const items: any[] = [];

    for await (const item of parseNDJSONWithProgress(response)) {
      items.push(item);
    }

    // Should only have data items, not metadata
    expect(items).toHaveLength(3);
    expect(items.every((item) => item.data)).toBe(true);
  });

  it('should handle error events', async () => {
    const lines = ['{"id": 1}', '{"type": "error", "error": "Something went wrong"}', '{"id": 2}'];

    const response = createNDJSONResponse(lines);
    const items: any[] = [];
    const errors: string[] = [];

    for await (const item of parseNDJSONWithProgress(response, (stats) => {
      errors.push(...stats.errors);
    })) {
      items.push(item);
    }

    expect(items).toHaveLength(2);
    expect(errors).toContain('Something went wrong');
  });
});

describe('collectNDJSON', () => {
  it('should collect all items into array', async () => {
    const lines = ['{"id": 1}', '{"id": 2}', '{"id": 3}'];

    const response = createNDJSONResponse(lines);
    const stream = parseNDJSON(response);
    const items = await collectNDJSON(stream);

    expect(items).toHaveLength(3);
    expect(items[0]).toEqual({ id: 1 });
  });

  it('should respect maxItems limit', async () => {
    const lines = ['{"id": 1}', '{"id": 2}', '{"id": 3}', '{"id": 4}', '{"id": 5}'];

    const response = createNDJSONResponse(lines);
    const stream = parseNDJSON(response);
    const items = await collectNDJSON(stream, 3);

    expect(items).toHaveLength(3);
  });
});

describe('batchNDJSON', () => {
  it('should batch items', async () => {
    const lines = ['{"id": 1}', '{"id": 2}', '{"id": 3}', '{"id": 4}', '{"id": 5}'];

    const response = createNDJSONResponse(lines);
    const stream = parseNDJSON(response);
    const batches: any[][] = [];

    for await (const batch of batchNDJSON(stream, 2)) {
      batches.push(batch);
    }

    expect(batches).toHaveLength(3);
    expect(batches[0]).toHaveLength(2);
    expect(batches[1]).toHaveLength(2);
    expect(batches[2]).toHaveLength(1); // Remaining item
  });

  it('should handle empty stream', async () => {
    const response = createNDJSONResponse([]);
    const stream = parseNDJSON(response);
    const batches: any[][] = [];

    for await (const batch of batchNDJSON(stream, 2)) {
      batches.push(batch);
    }

    expect(batches).toHaveLength(0);
  });
});

describe('filterNDJSON', () => {
  it('should filter items', async () => {
    const lines = [
      '{"id": 1, "active": true}',
      '{"id": 2, "active": false}',
      '{"id": 3, "active": true}',
    ];

    const response = createNDJSONResponse(lines);
    const stream = parseNDJSON<{ id: number; active: boolean }>(response);
    const filtered: any[] = [];

    for await (const item of filterNDJSON(stream, (item) => item.active)) {
      filtered.push(item);
    }

    expect(filtered).toHaveLength(2);
    expect(filtered[0].id).toBe(1);
    expect(filtered[1].id).toBe(3);
  });
});

describe('mapNDJSON', () => {
  it('should map items', async () => {
    const lines = ['{"id": 1, "value": 10}', '{"id": 2, "value": 20}', '{"id": 3, "value": 30}'];

    const response = createNDJSONResponse(lines);
    const stream = parseNDJSON<{ id: number; value: number }>(response);
    const mapped: number[] = [];

    for await (const value of mapNDJSON(stream, (item) => item.value * 2)) {
      mapped.push(value);
    }

    expect(mapped).toEqual([20, 40, 60]);
  });

  it('should handle async mapper', async () => {
    const lines = ['{"id": 1}', '{"id": 2}'];

    const response = createNDJSONResponse(lines);
    const stream = parseNDJSON<{ id: number }>(response);
    const mapped: string[] = [];

    for await (const value of mapNDJSON(stream, async (item) => `Item ${item.id}`)) {
      mapped.push(value);
    }

    expect(mapped).toEqual(['Item 1', 'Item 2']);
  });
});

describe('calculateThroughput', () => {
  it('should calculate throughput metrics', () => {
    const stats: StreamingStats = {
      bytesReceived: 1024 * 1024, // 1 MB
      itemsReceived: 1000,
      startTime: Date.now() - 2000, // 2 seconds ago
      endTime: Date.now(),
      errors: [],
    };

    const throughput = calculateThroughput(stats);

    expect(throughput.itemsPerSecond).toBeCloseTo(500, 0); // ~500 items/sec
    expect(throughput.megabytesPerSecond).toBeCloseTo(0.5, 1); // ~0.5 MB/sec
    expect(throughput.totalDurationMs).toBeCloseTo(2000, 100);
  });

  it('should handle ongoing streams', () => {
    const stats: StreamingStats = {
      bytesReceived: 1024,
      itemsReceived: 10,
      startTime: Date.now() - 1000,
      errors: [],
    };

    const throughput = calculateThroughput(stats);

    expect(throughput.itemsPerSecond).toBeGreaterThan(0);
    expect(throughput.bytesPerSecond).toBeGreaterThan(0);
  });
});
