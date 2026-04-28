# Web Workers Quick Reference

## Import Workers

```typescript
import {
  useGraphLayoutWorker,
  useDataTransformWorker,
  useExportImportWorker,
  useSearchIndexWorker,
  useWorkerSupport,
} from '@/hooks/useWorker';
```

## Basic Usage

```typescript
// 1. Initialize worker
const { worker, status, createProgressCallback } = useGraphLayoutWorker();

// 2. Check if ready
if (!worker || !status.isReady) return;

// 3. Create progress callback (optional)
const onProgress = createProgressCallback();

// 4. Call worker method
const result = await worker.computeLayout(nodes, edges, options, onProgress);

// 5. Use result
console.log('Positions:', result.positions);
```

## Worker APIs

### Graph Layout Worker

```typescript
// Dagre layout
const result = await worker.computeLayout(nodes, edges, {
  type: 'dagre',
  direction: 'TB', // TB, LR, BT, RL
  nodeSep: 60,
  rankSep: 100,
});

// Force-directed layout
const result = await worker.computeLayout(nodes, edges, {
  type: 'force',
  iterations: 100,
});
```

### Data Transform Worker

```typescript
// Sort
const sorted = await worker.sortData(data, 'field', 'asc');

// Aggregate
const aggregated = await worker.aggregateData(
  data,
  'groupField',
  'valueField',
  'sum' // sum, avg, min, max, count
);

// Statistics
const stats = await worker.calculateStatistics(data, 'field');
// Returns: { count, sum, mean, median, stdDev, min, max }

// Deduplicate
const unique = await worker.deduplicateData(data, 'field');

// Join
const joined = await worker.joinData(
  leftData,
  rightData,
  'id',
  'userId',
  'inner' // inner, left, right, outer
);
```

### Export/Import Worker

```typescript
// Export to NDJSON
const ndjson = await worker.generateNDJSON(data);

// Import from NDJSON
const data = await worker.parseNDJSON<MyType>(ndjson);

// Export to CSV
const csv = await worker.generateCSV(data, {
  delimiter: ',',
  includeHeader: true,
  columns: ['id', 'name', 'value'],
});

// Import from CSV
const data = await worker.parseCSV(csv, {
  hasHeader: true,
  delimiter: ',',
});

// Validate data
const { valid, invalid } = await worker.validateData(data, {
  required: ['id', 'name'],
  types: { id: 'number', name: 'string' },
  nullable: ['description'],
});
```

### Search Index Worker

```typescript
// Build index
const index = await worker.buildIndex(documents, {
  title: 2.0,   // Field weight
  content: 1.0,
});

// Search
const results = await worker.search(index, 'query text', {
  fuzzy: true,
  maxDistance: 2,
  fields: ['title', 'content'],
  limit: 20,
});

// Auto-suggest
const suggestions = await worker.autoSuggest(index, 'prefix', 10);

// Update index
const updatedIndex = await worker.updateIndex(index, [
  { id: '4', action: 'add', document: newDoc },
  { id: '2', action: 'remove' },
]);

// Get stats
const stats = await worker.getIndexStats(index);
// Returns: { documentCount, termCount, avgTermsPerDocument }
```

## Progress Tracking

```typescript
const { worker, status, createProgressCallback } = useGraphLayoutWorker();

const onProgress = createProgressCallback();

await worker.computeLayout(nodes, edges, options, onProgress);

// Monitor progress
console.log(`Progress: ${status.progress}%`);

// Show progress bar
<div className="w-full bg-gray-200">
  <div
    className="bg-blue-500 h-2"
    style={{ width: `${status.progress}%` }}
  />
</div>
```

## Feature Detection

```typescript
const { supported, checked } = useWorkerSupport();

if (checked && !supported) {
  console.warn('Web Workers not supported');
  // Use fallback
}
```

## Fallback Strategy

```typescript
import { useWorkerSupport } from '@/hooks/useWorker';

const { supported } = useWorkerSupport();

const processData = async (data: any[]) => {
  if (supported) {
    // Use worker
    const { worker } = useDataTransformWorker();
    return await worker?.sortData(data, 'field', 'asc');
  } else {
    // Fallback to main thread
    return [...data].sort((a, b) => a.field - b.field);
  }
};
```

## Error Handling

```typescript
try {
  const result = await worker.computeLayout(nodes, edges, options);
} catch (error) {
  console.error('Worker failed:', error);
  // Handle error or use fallback
}
```

## Transferable Objects

```typescript
import { WorkerPool, TaskPriority } from '@/workers/WorkerPool';

const buffer = new ArrayBuffer(1024);

await pool.executeTask(
  'process',
  { buffer },
  {
    transferables: [buffer], // Zero-copy transfer
  }
);

// After transfer, buffer is detached
console.log(buffer.byteLength); // 0
```

## Worker Pool (Advanced)

```typescript
import { WorkerPool, TaskPriority } from '@/workers/WorkerPool';

// Create pool
const pool = new WorkerPool({
  minWorkers: 2,
  maxWorkers: 8,
  idleTimeout: 30000,
  workerFactory: () => new Worker(
    new URL('./my-worker.ts', import.meta.url),
    { type: 'module' }
  ),
});

// Execute task
const result = await pool.executeTask(
  'compute',
  { data: largeDataset },
  {
    priority: TaskPriority.HIGH,
    timeout: 60000,
    onProgress: (p) => console.log(`${p}%`),
  }
);

// Get statistics
const stats = pool.getStats();
console.log(`Workers: ${stats.busyWorkers}/${stats.totalWorkers}`);
console.log(`Queue: ${stats.queuedTasks}`);

// Cleanup
pool.terminate();
```

## Common Patterns

### Large Graph Layout

```typescript
const { worker, status } = useGraphLayoutWorker();

if (nodes.length > 100) {
  // Use worker for large graphs
  const result = await worker.computeLayout(nodes, edges, {
    type: 'dagre',
  });
  applyLayout(result.positions);
} else {
  // Direct computation for small graphs
  computeLayoutSync(nodes, edges);
}
```

### Streaming Export

```typescript
const { worker } = useExportImportWorker();

// Export in chunks
const chunkSize = 1000;
const chunks = [];

for (let i = 0; i < data.length; i += chunkSize) {
  const chunk = data.slice(i, i + chunkSize);
  const ndjson = await worker.generateNDJSON(chunk);
  chunks.push(ndjson);
}

const fullExport = chunks.join('\n');
```

### Progressive Search Index

```typescript
const { worker } = useSearchIndexWorker();

// Build initial index
let index = await worker.buildIndex(documents);

// Update incrementally
const newDoc = { id: 'new', fields: { text: 'New document' } };
index = await worker.updateIndex(index, [
  { id: 'new', action: 'add', document: newDoc },
]);
```

## Performance Tips

1. **Use workers for >100 items** - Overhead not worth it for small datasets
2. **Batch operations** - Group multiple operations into one worker call
3. **Use transferables** - For large binary data (ArrayBuffer, ImageData)
4. **Monitor progress** - Show feedback for operations >1 second
5. **Set timeouts** - Prevent hanging operations
6. **Cache results** - Worker computations can be expensive

## Testing

```bash
# Run unit tests
bun test src/__tests__/workers/WorkerPool.test.ts

# Run integration tests
bun test src/__tests__/workers/integration.test.ts

# Run all worker tests
bun test src/__tests__/workers/
```

## Debugging

```typescript
// Enable worker debugging in Chrome DevTools
// 1. Open DevTools > Sources
// 2. Look for worker threads in sidebar
// 3. Set breakpoints in worker code

// Add logging
console.log('Worker processing:', data);

// Check worker status
console.log('Worker ready:', status.isReady);
console.log('Worker error:', status.error);
```

## Troubleshooting

### Worker not loading
**Problem**: `Worker not initialized`
**Solution**: Check file path and module type:
```typescript
new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' })
```

### Serialization error
**Problem**: `Cannot clone object`
**Solution**: Only pass serializable data (no functions, DOM nodes, circular refs)

### Worker hangs
**Problem**: No response from worker
**Solution**: Set timeout:
```typescript
const result = await pool.executeTask('compute', data, {
  timeout: 30000, // 30 second timeout
});
```

## See Also

- [Complete Guide](./web-workers-guide.md)
- [Examples](../../frontend/apps/web/src/components/examples/WorkerExample.tsx)
- [API Reference](../../frontend/apps/web/src/workers/)
