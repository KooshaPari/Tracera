# Quick Start: Web Worker Graph Layout

## TL;DR

Web Workers move expensive graph layout computation off the main thread, keeping your UI at 60 FPS even with 100,000+ nodes.

**Key Benefit**: Users can interact with the UI during layout computation.

## 30-Second Setup

```typescript
import { useGraphLayoutWorker } from '@/hooks/useGraphLayoutWorker';

function MyGraph() {
  const { computeLayout, isReady } = useGraphLayoutWorker();

  useEffect(() => {
    if (isReady && nodes.length > 500) {
      computeLayout(nodes, edges, { algorithm: 'elk' })
        .then(result => applyPositions(result.positions));
    }
  }, [isReady, nodes, edges]);
}
```

## When to Use

| Nodes | Recommendation | Reason |
|-------|---------------|--------|
| <500 | Skip worker | Overhead outweighs benefit |
| 500-10k | Use worker | Maintains UI responsiveness |
| 10k+ | **Must use** | Prevents browser freezes |

## API Reference

### `useGraphLayoutWorker(options?)`

```typescript
interface UseGraphLayoutWorkerOptions {
  enabled?: boolean;        // default: true
  progressive?: boolean;    // default: true for >500 nodes
  batchSize?: number;       // default: 100
  timeout?: number;         // default: 30000ms
  onProgress?: (result: LayoutResult) => void;
}
```

**Returns:**
```typescript
{
  computeLayout: (nodes, edges, options) => Promise<LayoutResult>,
  isReady: boolean,
  isComputing: boolean,
  error: Error | null,
  progress: number,         // 0-1
  terminate: () => void
}
```

## Algorithms

| Algorithm | Complexity | Best For | Max Nodes |
|-----------|-----------|----------|-----------|
| `'grid'` | O(n) | Quick overview | 100,000+ |
| `'circular'` | O(n) | Peer relationships | 10,000 |
| `'radial'` | O(n+e) | Mind maps | 5,000 |
| `'dagre'` | O(n log n) | Simple DAGs | 10,000 |
| `'elk'` | O(n log n) | Complex DAGs | 50,000 |
| `'d3-force'` | O(n²) | Organic layouts | 1,000 |

## Examples

### Basic Layout

```typescript
const { computeLayout } = useGraphLayoutWorker();

const result = await computeLayout(nodes, edges, {
  algorithm: 'elk',
  direction: 'TB',
  nodeSep: 60,
  rankSep: 100
});

applyPositions(result.positions);
```

### Progressive Layout

```typescript
const { computeLayout, progress } = useGraphLayoutWorker({
  progressive: true,
  batchSize: 100,
  onProgress: (partial) => {
    // Apply partial results as they arrive
    applyPositions(partial.positions);
  }
});

// Show progress
<ProgressBar value={progress * 100} />
```

### With Loading State

```typescript
const { computeLayout, isComputing } = useGraphLayoutWorker();

const handleLayout = async () => {
  await computeLayout(nodes, edges, { algorithm: 'elk' });
};

return (
  <div>
    {isComputing && <Spinner />}
    <button onClick={handleLayout} disabled={isComputing}>
      Layout Graph
    </button>
  </div>
);
```

### Error Handling

```typescript
const { computeLayout, error } = useGraphLayoutWorker();

useEffect(() => {
  if (error) {
    toast.error('Layout failed, using fallback');
  }
}, [error]);

try {
  await computeLayout(nodes, edges, { algorithm: 'elk' });
} catch (err) {
  // Fallback is automatic, but you can handle errors
  console.error(err);
}
```

## Layout Options

```typescript
interface LayoutOptions {
  algorithm: 'dagre' | 'elk' | 'd3-force' | 'grid' | 'circular' | 'radial';

  // Direction (for dagre/elk)
  direction?: 'TB' | 'LR' | 'BT' | 'RL';

  // Spacing
  nodeSep?: number;        // default: 60
  rankSep?: number;        // default: 100
  marginX?: number;        // default: 40
  marginY?: number;        // default: 40

  // Node dimensions
  nodeWidth?: number;      // default: 200
  nodeHeight?: number;     // default: 120

  // Center point (for circular/radial)
  centerX?: number;        // default: 500
  centerY?: number;        // default: 400

  // Progressive layout
  progressive?: boolean;   // default: false
  batchSize?: number;      // default: 100
}
```

## Benchmarking

```typescript
import { useGraphLayoutBenchmark } from '@/hooks/useGraphLayoutWorker';

const { benchmark } = useGraphLayoutBenchmark();

const result = await benchmark(
  nodes,
  edges,
  'elk',
  5  // iterations
);

console.log(`Average: ${result.avgTime}ms`);
console.log(`Min: ${result.minTime}ms`);
console.log(`Max: ${result.maxTime}ms`);
console.log(`Std Dev: ${result.stdDev}ms`);
```

## Performance Tips

### 1. Use Worker Threshold

```typescript
// Only use worker for large graphs
const shouldUseWorker = nodes.length > 500;

if (shouldUseWorker) {
  const { computeLayout } = useGraphLayoutWorker();
  await computeLayout(nodes, edges, { algorithm: 'elk' });
} else {
  // Use synchronous layout
  const positions = layoutSync(nodes, edges);
}
```

### 2. Choose Right Algorithm

```typescript
// For large graphs, prefer simple algorithms
const algorithm = nodes.length > 10000
  ? 'grid'      // O(n)
  : nodes.length > 1000
    ? 'dagre'   // O(n log n)
    : 'elk';    // O(n log n) but more features
```

### 3. Enable Progressive for Large Graphs

```typescript
const progressive = nodes.length > 1000;

const { computeLayout } = useGraphLayoutWorker({
  progressive,
  batchSize: 100
});
```

### 4. Clean Up Workers

```typescript
const { terminate } = useGraphLayoutWorker();

useEffect(() => {
  return () => {
    terminate();  // Clean up on unmount
  };
}, []);
```

## Common Issues

### Worker Not Starting

**Symptom**: `isReady` stays `false`

**Fix**:
```typescript
// Check browser console for errors
const { isReady, error } = useGraphLayoutWorker();

useEffect(() => {
  if (!isReady && error) {
    console.error('Worker initialization failed:', error);
  }
}, [isReady, error]);
```

### Still Experiencing Freezes

**Symptom**: UI freezes during layout

**Fix**:
```typescript
// Verify worker is actually being used
const { isComputing } = useGraphLayoutWorker();

useEffect(() => {
  console.log('Using worker:', isComputing);
}, [isComputing]);

// If false, check if worker is enabled
const { computeLayout } = useGraphLayoutWorker({
  enabled: true  // Explicitly enable
});
```

### Memory Issues

**Symptom**: Browser runs out of memory

**Fix**:
```typescript
// Use progressive layout with smaller batches
const { computeLayout } = useGraphLayoutWorker({
  progressive: true,
  batchSize: 50  // Smaller batches
});

// Or limit node count
const limitedNodes = nodes.slice(0, 50000);
```

## Scripts

```bash
# Run benchmark
bun run benchmark:layout

# Start Storybook (see demo)
bun run storybook
# Navigate to "Graph/Layout Worker Demo"

# Run tests (future)
bun test src/workers/__tests__/
```

## Resources

- **Full Documentation**: `docs/architecture/web-worker-layout.md`
- **Implementation Summary**: `WEB_WORKER_LAYOUT_IMPLEMENTATION.md`
- **Worker Source**: `src/workers/graphLayout.worker.ts`
- **Hook Source**: `src/hooks/useGraphLayoutWorker.ts`
- **Demo**: Storybook → "Graph/Layout Worker Demo"

## FAQ

**Q: When should I use workers?**
A: For graphs with 500+ nodes or when UI responsiveness is critical.

**Q: Is there performance overhead?**
A: Yes, 0.1-3% for computation, but main thread stays at 60 FPS.

**Q: What happens if worker fails?**
A: Automatic fallback to synchronous layout. No user-facing errors.

**Q: Can I use multiple workers?**
A: Yes, but one worker is usually sufficient. Browser limits apply.

**Q: How do I debug worker issues?**
A: Check `error` state and browser console. Worker errors are logged.

**Q: Can I customize layout algorithms?**
A: Yes, modify `src/workers/graphLayout.worker.ts` and add your algorithm.

## Next Steps

1. ✅ Install dependencies (`bun add -d comlink`)
2. ✅ Use hook in your component
3. ✅ Run benchmark (`bun run benchmark:layout`)
4. ✅ View demo in Storybook
5. 📝 Read full docs (`docs/architecture/web-worker-layout.md`)

---

**Need Help?** Check the full documentation or Storybook demo for more examples.
