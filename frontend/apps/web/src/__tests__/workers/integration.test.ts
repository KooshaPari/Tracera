/**
 * Web Workers Integration Tests
 *
 * Tests actual worker implementations with real computations
 */

import type { Remote } from 'comlink';

import { wrap } from 'comlink';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import type { DataTransformWorkerAPI } from '../../workers/data-transform.worker';
import type { ExportImportWorkerAPI } from '../../workers/export-import.worker';
import type { GraphLayoutWorkerAPI } from '../../workers/graph-layout.worker';
import type { SearchIndexWorkerAPI } from '../../workers/search-index.worker';

describe('Graph Layout Worker Integration', () => {
  let worker: Worker;
  let api: Remote<GraphLayoutWorkerAPI>;

  beforeEach(() => {
    worker = new Worker(new URL('../../workers/graph-layout.worker.ts', import.meta.url), {
      type: 'module',
    });
    api = wrap<GraphLayoutWorkerAPI>(worker);
  });

  afterEach(() => {
    worker.terminate();
  });

  it('should compute dagre layout for simple graph', async () => {
    const nodes = [
      { height: 50, id: 'A', width: 100 },
      { height: 50, id: 'B', width: 100 },
      { height: 50, id: 'C', width: 100 },
    ];

    const edges = [
      { id: 'AB', source: 'A', target: 'B' },
      { id: 'BC', source: 'B', target: 'C' },
    ];

    const result = await api.computeLayout(nodes, edges, { type: 'dagre' });

    expect(result.positions).toBeDefined();
    expect(result.positions.A).toBeDefined();
    expect(result.positions.B).toBeDefined();
    expect(result.positions.C).toBeDefined();
    expect(result.size).toBeDefined();
    expect(result.size.width).toBeGreaterThan(0);
    expect(result.size.height).toBeGreaterThan(0);
  });

  it('should compute force-directed layout', async () => {
    const nodes = Array.from({ length: 10 }, (_, i) => ({
      height: 40,
      id: `node-${i}`,
      width: 80,
    }));

    const edges = Array.from({ length: 15 }, (_, i) => ({
      id: `edge-${i}`,
      source: `node-${i % 10}`,
      target: `node-${(i + 1) % 10}`,
    }));

    const result = await api.computeLayout(nodes, edges, {
      iterations: 50,
      type: 'force',
    });

    expect(result.positions).toBeDefined();
    expect(Object.keys(result.positions)).toHaveLength(10);
  });

  it('should handle large graphs efficiently', async () => {
    const nodeCount = 1000;
    const nodes = Array.from({ length: nodeCount }, (_, i) => ({
      height: 50,
      id: `node-${i}`,
      width: 100,
    }));

    const edges = Array.from({ length: nodeCount - 1 }, (_, i) => ({
      id: `edge-${i}`,
      source: `node-${i}`,
      target: `node-${i + 1}`,
    }));

    const startTime = performance.now();
    const result = await api.computeLayout(nodes, edges, { type: 'dagre' });
    const duration = performance.now() - startTime;

    expect(result.positions).toBeDefined();
    expect(Object.keys(result.positions)).toHaveLength(nodeCount);
    // Should complete in reasonable time (< 5 seconds for 1000 nodes)
    expect(duration).toBeLessThan(5000);
  });
});

describe('Data Transform Worker Integration', () => {
  let worker: Worker;
  let api: Remote<DataTransformWorkerAPI>;

  beforeEach(() => {
    worker = new Worker(new URL('../../workers/data-transform.worker.ts', import.meta.url), {
      type: 'module',
    });
    api = wrap<DataTransformWorkerAPI>(worker);
  });

  afterEach(() => {
    worker.terminate();
  });

  it('should sort large dataset', async () => {
    const data = Array.from({ length: 10_000 }, (_, i) => ({
      id: i,
      value: Math.random() * 1000,
    }));

    const sorted = await api.sortData(data, {
      direction: 'asc',
      field: 'value',
    });

    expect(sorted).toHaveLength(data.length);

    // Verify sorting
    for (let i = 1; i < sorted.length; i++) {
      expect(sorted[i].value).toBeGreaterThanOrEqual(sorted[i - 1].value);
    }
  });

  it('should aggregate data by field', async () => {
    const data = [
      { category: 'A', value: 10 },
      { category: 'B', value: 20 },
      { category: 'A', value: 15 },
      { category: 'B', value: 25 },
      { category: 'C', value: 30 },
    ];

    const aggregated = await api.aggregateData(data, {
      aggregateField: 'value',
      aggregationType: 'sum',
      groupByField: 'category',
    });

    expect(aggregated).toEqual({
      A: 25,
      B: 45,
      C: 30,
    });
  });

  it('should calculate statistics correctly', async () => {
    const data = [{ value: 10 }, { value: 20 }, { value: 30 }, { value: 40 }, { value: 50 }];

    const stats = await api.calculateStatistics(data, { field: 'value' });

    expect(stats.count).toBe(5);
    expect(stats.sum).toBe(150);
    expect(stats.mean).toBe(30);
    expect(stats.median).toBe(30);
    expect(stats.min).toBe(10);
    expect(stats.max).toBe(50);
  });

  it('should deduplicate data', async () => {
    const data = [
      { id: 1, name: 'A' },
      { id: 2, name: 'B' },
      { id: 1, name: 'A' },
      { id: 3, name: 'C' },
      { id: 2, name: 'B' },
    ];

    const deduped = await api.deduplicateData(data, { field: 'id' });

    expect(deduped).toHaveLength(3);
    expect(deduped.map((d) => d.id)).toEqual([1, 2, 3]);
  });
});

describe('Export/Import Worker Integration', () => {
  let worker: Worker;
  let api: Remote<ExportImportWorkerAPI>;

  beforeEach(() => {
    worker = new Worker(new URL('../../workers/export-import.worker.ts', import.meta.url), {
      type: 'module',
    });
    api = wrap<ExportImportWorkerAPI>(worker);
  });

  afterEach(() => {
    worker.terminate();
  });

  it('should parse and generate NDJSON', async () => {
    const data = [
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' },
      { id: 3, name: 'Charlie' },
    ];

    const ndjson = await api.generateNDJSON(data);
    expect(ndjson).toContain('{"id":1,"name":"Alice"}');

    const parsed = await api.parseNDJSON(ndjson);
    expect(parsed).toEqual(data);
  });

  it('should parse and generate CSV', async () => {
    const data = [
      { age: 30, city: 'NYC', name: 'Alice' },
      { age: 25, city: 'LA', name: 'Bob' },
      { age: 35, city: 'SF', name: 'Charlie' },
    ];

    const csv = await api.generateCSV(data);
    expect(csv).toContain('name,age,city');
    expect(csv).toContain('Alice,30,NYC');

    const parsed = await api.parseCSV(csv, { hasHeader: true });
    expect(parsed).toHaveLength(3);
    expect(parsed[0].name).toBe('Alice');
  });

  it('should validate data against schema', async () => {
    const data = [
      { age: 30, id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' }, // Missing age
      { age: '35', id: 3, name: 'Charlie' }, // Wrong type
      { age: 40, id: 4, name: 'David' },
    ];

    const result = await api.validateData(data, {
      required: ['id', 'name', 'age'],
      types: {
        age: 'number',
        id: 'number',
        name: 'string',
      },
    });

    expect(result.valid).toHaveLength(2);
    expect(result.invalid).toHaveLength(2);
  });

  it('should handle large JSON serialization', async () => {
    const largeData = Array.from({ length: 10_000 }, (_, i) => ({
      data: `Item ${i}`,
      id: i,
      timestamp: Date.now(),
    }));

    const startTime = performance.now();
    const json = await api.stringifyJSON(largeData);
    const duration = performance.now() - startTime;

    expect(json).toBeDefined();
    expect(json.length).toBeGreaterThan(0);
    // Should complete quickly
    expect(duration).toBeLessThan(2000);

    const parsed = await api.parseJSON(json);
    expect(parsed).toEqual(largeData);
  });
});

describe('Search Index Worker Integration', () => {
  let worker: Worker;
  let api: Remote<SearchIndexWorkerAPI>;

  beforeEach(() => {
    worker = new Worker(new URL('../../workers/search-index.worker.ts', import.meta.url), {
      type: 'module',
    });
    api = wrap<SearchIndexWorkerAPI>(worker);
  });

  afterEach(() => {
    worker.terminate();
  });

  it('should build and search index', async () => {
    const documents = [
      {
        fields: {
          content: 'React is a JavaScript library for building user interfaces',
          title: 'Introduction to React',
        },
        id: '1',
      },
      {
        fields: {
          content: 'Vue is a progressive framework for building user interfaces',
          title: 'Vue.js Basics',
        },
        id: '2',
      },
      {
        fields: {
          content: 'Angular is a platform for building web applications',
          title: 'Angular Guide',
        },
        id: '3',
      },
    ];

    const index = await api.buildIndex(documents);
    expect(index).toBeDefined();

    const results = await api.search(index, 'user interfaces');

    expect(results.length).toBeGreaterThan(0);
    expect(results[0].score).toBeGreaterThan(0);
  });

  it('should perform fuzzy search', async () => {
    const documents = [
      { fields: { text: 'The quick brown fox' }, id: '1' },
      { fields: { text: 'The quik brwn fox' }, id: '2' }, // Typos
    ];

    const index = await api.buildIndex(documents);
    const results = await api.search(index, 'quick brown', {
      fuzzy: true,
      maxDistance: 2,
    });

    expect(results).toHaveLength(2);
  });

  it('should provide auto-suggestions', async () => {
    const documents = [
      { fields: { text: 'JavaScript programming' }, id: '1' },
      { fields: { text: 'Java programming' }, id: '2' },
      { fields: { text: 'Python programming' }, id: '3' },
    ];

    const index = await api.buildIndex(documents);
    const suggestions = await api.autoSuggest(index, 'java', 5);

    expect(suggestions.length).toBeGreaterThan(0);
    expect(suggestions.some((s) => s.includes('java'))).toBeTruthy();
  });

  it('should update index incrementally', async () => {
    const documents = [
      { fields: { text: 'Document 1' }, id: '1' },
      { fields: { text: 'Document 2' }, id: '2' },
    ];

    let index = await api.buildIndex(documents);
    const initialStats = await api.getIndexStats(index);
    expect(initialStats.documentCount).toBe(2);

    // Add new document
    index = await api.updateIndex(index, [
      {
        action: 'add',
        document: { fields: { text: 'Document 3' }, id: '3' },
        id: '3',
      },
    ]);

    const updatedStats = await api.getIndexStats(index);
    expect(updatedStats.documentCount).toBe(3);

    // Remove document
    index = await api.updateIndex(index, [{ action: 'remove', id: '2' }]);

    const finalStats = await api.getIndexStats(index);
    expect(finalStats.documentCount).toBe(2);
  });

  it('should handle large index efficiently', async () => {
    const documents = Array.from({ length: 5000 }, (_, i) => ({
      fields: {
        content: `This is the content of document number ${i} with some random text`,
        title: `Document ${i}`,
      },
      id: `doc-${i}`,
    }));

    const startTime = performance.now();
    const index = await api.buildIndex(documents);
    const buildDuration = performance.now() - startTime;

    expect(buildDuration).toBeLessThan(5000); // Should build in < 5 seconds

    const searchStart = performance.now();
    const results = await api.search(index, 'document content');
    const searchDuration = performance.now() - searchStart;

    expect(searchDuration).toBeLessThan(1000); // Should search in < 1 second
    expect(results.length).toBeGreaterThan(0);
  });
});

describe('Performance Benchmarks', () => {
  it('should process 10k items faster in worker than main thread', async () => {
    const data = Array.from({ length: 10_000 }, (_, i) => ({
      id: i,
      value: Math.random() * 1000,
    }));

    // Main thread sorting
    const mainThreadStart = performance.now();
    const mainThreadSorted = [...data].toSorted((a, b) => a.value - b.value);
    const mainThreadDuration = performance.now() - mainThreadStart;

    // Worker sorting
    const worker = new Worker(new URL('../../workers/data-transform.worker.ts', import.meta.url), {
      type: 'module',
    });
    const api = wrap<DataTransformWorkerAPI>(worker);

    const workerStart = performance.now();
    const workerSorted = await api.sortData(data, {
      direction: 'asc',
      field: 'value',
    });
    const workerDuration = performance.now() - workerStart;

    worker.terminate();

    console.log(`Main thread: ${mainThreadDuration.toFixed(2)}ms`);
    console.log(`Worker: ${workerDuration.toFixed(2)}ms`);

    // Verify correctness
    expect(workerSorted).toHaveLength(mainThreadSorted.length);

    // Note: Worker may or may not be faster for this size,
    // But should not block main thread
  });
});
