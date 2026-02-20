# Incremental Graph Loading with Streaming

This guide explains the incremental graph loading system that enables smooth, progressive loading of large graphs using NDJSON streaming.

## Overview

The incremental graph loading system provides:

- **NDJSON Streaming**: Server streams nodes and edges in newline-delimited JSON format
- **Progressive Loading**: Graph renders as data arrives, no waiting for full dataset
- **Progress Tracking**: Real-time progress updates with estimated completion time
- **Predictive Prefetch**: Automatically prefetches adjacent viewports based on pan direction
- **Memory Efficiency**: Batch rendering with configurable chunk sizes
- **Cancellable Operations**: Abort loading at any time

## Architecture

### Backend Components

#### 1. Graph Stream Handler (Go)

Location: `backend/internal/handlers/graph_stream_handler.go`

**Endpoints:**

- `POST /api/v1/projects/:project_id/graph/stream` - Stream viewport graph data
- `POST /api/v1/projects/:project_id/graph/stream/prefetch` - Prefetch adjacent viewports
- `GET /api/v1/projects/:project_id/graph/stream/stats` - Get streaming statistics

**Features:**

- Chunks data into configurable batch sizes (default: 50 items)
- Streams nodes first, then edges
- Includes progress updates with each chunk
- Supports cancellation via context
- Flushes data immediately for low latency

#### 2. Stream Response Format

Each line in the NDJSON stream is a `StreamChunk`:

```json
{
  "type": "metadata|node|edge|progress|complete|error",
  "data": { /* chunk-specific data */ },
  "progress": {
    "current": 100,
    "total": 500,
    "percentage": 20.0,
    "stage": "nodes|edges|complete"
  },
  "timestamp": 1234567890
}
```

**Chunk Types:**

- `metadata` - Initial metadata about the stream (total counts, estimated time)
- `node` - Single graph node
- `edge` - Single graph edge
- `progress` - Progress update (sent periodically)
- `complete` - Stream complete marker
- `error` - Error occurred

### Frontend Components

#### 1. IncrementalGraphBuilder

Location: `frontend/apps/web/src/lib/graph/IncrementalGraphBuilder.ts`

**Purpose**: Core library for building graphs incrementally from streaming data.

**Key Features:**

- Parses NDJSON streams
- Manages node and edge maps
- Batches updates for rendering efficiency
- Tracks progress and metadata
- Supports cancellation

**Usage:**

```typescript
import { IncrementalGraphBuilder } from '@/lib/graph/IncrementalGraphBuilder';

const builder = new IncrementalGraphBuilder({
  batchSize: 10,
  batchDelay: 16, // ~60fps

  onProgress: (progress) => {
    console.log(`${progress.percentage}% complete`);
  },

  onNode: (node) => {
    // Add node to graph
  },

  onEdge: (edge) => {
    // Add edge to graph
  },

  onComplete: (result) => {
    console.log('Graph loaded:', result);
  },
});

// Load from streaming endpoint
await builder.loadFromStream(url, viewportRequest);
```

#### 2. useIncrementalGraph Hook

Location: `frontend/apps/web/src/hooks/useIncrementalGraph.ts`

**Purpose**: React hook for managing incremental graph loading state.

**Features:**

- Automatic state management
- Viewport-based loading
- Predictive prefetch with caching
- Progress tracking
- Error handling

**Usage:**

```typescript
import { useIncrementalGraph } from '@/hooks/useIncrementalGraph';

function MyGraphComponent({ projectId, viewport }) {
  const {
    state,
    loadGraph,
    loadViewport,
    prefetchDirection,
    abort,
  } = useIncrementalGraph({
    projectId,
    viewport,
    enablePrefetch: true,
  });

  // state.nodes - Array of loaded nodes
  // state.edges - Array of loaded edges
  // state.progress - Current loading progress
  // state.isLoading - Loading state
  // state.error - Error if any

  return (
    <div>
      {state.isLoading && (
        <div>Loading: {state.progress?.percentage}%</div>
      )}
      <GraphRenderer nodes={state.nodes} edges={state.edges} />
    </div>
  );
}
```

#### 3. GraphLoadingProgress Component

Location: `frontend/apps/web/src/components/graph/GraphLoadingProgress.tsx`

**Purpose**: UI components for displaying loading progress.

**Variants:**

- `GraphLoadingProgress` - Full card with detailed stats
- `GraphLoadingProgressCompact` - Compact inline progress bar
- `GraphLoadingProgressInline` - Minimal progress indicator

**Usage:**

```typescript
import { GraphLoadingProgress } from '@/components/graph/GraphLoadingProgress';

<GraphLoadingProgress
  progress={state.progress}
  metadata={state.metadata}
  isLoading={state.isLoading}
  onCancel={abort}
/>
```

#### 4. StreamingGraphView Component

Location: `frontend/apps/web/src/components/graph/StreamingGraphView.tsx`

**Purpose**: Complete example of streaming graph view with pan/zoom.

**Features:**

- Pan and zoom support
- Real-time progress display
- Viewport-based loading
- Predictive prefetch
- SVG rendering

## Usage Examples

### Basic Streaming Load

```typescript
// Backend endpoint
POST /api/v1/projects/my-project/graph/stream
Content-Type: application/json

{
  "viewport": {
    "minX": 0,
    "minY": 0,
    "maxX": 1000,
    "maxY": 1000
  },
  "zoom": 1.0,
  "bufferPx": 500
}
```

```typescript
// Frontend
const { state, loadGraph } = useIncrementalGraph({
  projectId: 'my-project',
  viewport: { minX: 0, minY: 0, maxX: 1000, maxY: 1000 },
});

useEffect(() => {
  loadGraph();
}, []);
```

### Viewport-Based Loading

```typescript
const [viewport, setViewport] = useState(initialViewport);

const { state, loadViewport } = useIncrementalGraph({
  projectId,
  viewport,
});

// When user pans to new viewport
const handlePan = (newViewport) => {
  setViewport(newViewport);
  loadViewport(newViewport);
};
```

### Predictive Prefetch

```typescript
const { prefetchDirection } = useIncrementalGraph({
  projectId,
  viewport,
  enablePrefetch: true,
  prefetchDirection: 'east', // Direction user is panning
  prefetchVelocity: 500, // Pixels per second
});

// Prefetch happens automatically based on pan direction
// Data is cached for smooth transitions
```

### Custom Chunk Processing

```typescript
import { parseNDJSON } from '@/lib/graph/IncrementalGraphBuilder';

const response = await fetch(streamUrl, {
  method: 'POST',
  body: JSON.stringify(viewportRequest),
});

for await (const chunk of parseNDJSON(response)) {
  switch (chunk.type) {
    case 'metadata':
      console.log('Stream metadata:', chunk.data);
      break;
    case 'node':
      addNodeToGraph(chunk.data);
      break;
    case 'edge':
      addEdgeToGraph(chunk.data);
      break;
    case 'complete':
      console.log('Stream complete');
      break;
  }
}
```

## Performance Optimization

### Backend Optimization

1. **Chunk Size Tuning**
   - Small graphs (< 100 nodes): 25-50 chunk size
   - Medium graphs (100-1000 nodes): 50-100 chunk size
   - Large graphs (> 1000 nodes): 100-500 chunk size

2. **Database Indexing**
   - Ensure indexes on `position_x` and `position_y` for spatial queries
   - Use composite indexes for `(project_id, position_x, position_y)`

3. **Connection Pooling**
   - Configure adequate database connection pool size
   - Use connection timeout settings

### Frontend Optimization

1. **Batch Rendering**
   - Use `batchSize` and `batchDelay` to control render frequency
   - Default: 10 items per batch, 16ms delay (~60fps)

2. **Viewport Culling**
   - Only request nodes within viewport + buffer
   - Typical buffer: 500-1000 pixels

3. **Prefetch Cache Management**
   - Cache limited to 8 adjacent viewports
   - LRU eviction strategy

## Configuration

### Backend Configuration

```go
// Customize chunk size via query parameter
GET /api/v1/projects/:project_id/graph/stream?chunk_size=100
```

### Frontend Configuration

```typescript
const { state } = useIncrementalGraph({
  projectId: 'my-project',
  viewport: myViewport,

  // Streaming options
  chunkSize: 50,              // Items per batch
  bufferPx: 500,              // Viewport buffer in pixels

  // Prefetch options
  enablePrefetch: true,       // Enable predictive prefetch
  prefetchDirection: 'east',  // Direction to prefetch
  prefetchVelocity: 0,        // Pan velocity (px/s)

  // API options
  apiBaseUrl: '/api/v1',      // Custom API base URL
});
```

## Error Handling

### Network Errors

```typescript
const { state, loadGraph } = useIncrementalGraph({ ... });

if (state.error) {
  // Handle error
  console.error('Graph load failed:', state.error);

  // Retry
  loadGraph();
}
```

### Stream Interruption

```typescript
const { abort } = useIncrementalGraph({ ... });

// User cancels or navigates away
useEffect(() => {
  return () => {
    abort(); // Clean up ongoing stream
  };
}, []);
```

### Partial Data Recovery

The incremental builder maintains all successfully loaded nodes/edges even if stream is interrupted:

```typescript
const { state } = useIncrementalGraph({ ... });

// Even with errors, partial data is available
console.log(`Loaded ${state.nodes.length} nodes before error`);
```

## Testing

### Backend Tests

```go
func TestStreamGraphIncremental(t *testing.T) {
    // Test streaming endpoint
    // Verify NDJSON format
    // Check chunk ordering
    // Test cancellation
}
```

### Frontend Tests

```typescript
describe('IncrementalGraphBuilder', () => {
  it('parses NDJSON stream correctly', async () => {
    const builder = new IncrementalGraphBuilder({ ... });
    const result = await builder.loadFromStream(mockUrl, mockRequest);

    expect(result.nodes.size).toBe(expectedNodeCount);
    expect(result.edges.size).toBe(expectedEdgeCount);
  });

  it('handles stream interruption gracefully', async () => {
    const builder = new IncrementalGraphBuilder({ ... });

    // Start loading
    const promise = builder.loadFromStream(url, request);

    // Abort after 100ms
    setTimeout(() => builder.abort(), 100);

    await expect(promise).rejects.toThrow('AbortError');

    // Verify partial data is retained
    const stats = builder.getStats();
    expect(stats.nodeCount).toBeGreaterThan(0);
  });
});
```

## Monitoring

### Backend Metrics

- Stream duration per project
- Chunk sizes and counts
- Connection timeouts
- Error rates

### Frontend Metrics

- Time to first chunk
- Total load time
- Prefetch hit rate
- Render frame rate

## Best Practices

1. **Always use viewport-based loading** - Don't load entire graph at once
2. **Enable predictive prefetch** - Improves perceived performance
3. **Set appropriate buffer sizes** - Balance prefetch vs. data transfer
4. **Monitor progress** - Provide user feedback during loading
5. **Handle errors gracefully** - Retry with exponential backoff
6. **Clean up on unmount** - Always abort ongoing streams
7. **Use batch rendering** - Prevent UI freezing on large datasets
8. **Cache prefetch data** - Reuse data for smooth panning

## Troubleshooting

### Issue: Slow streaming

**Causes:**
- Large chunk sizes
- Slow database queries
- Network latency

**Solutions:**
- Reduce chunk size
- Add database indexes
- Enable compression

### Issue: High memory usage

**Causes:**
- Loading too much data at once
- Not cleaning up old viewports
- Large prefetch cache

**Solutions:**
- Reduce viewport size
- Implement viewport cleanup
- Limit prefetch cache size

### Issue: Choppy rendering

**Causes:**
- Too frequent batch updates
- Synchronous rendering
- Large chunk sizes

**Solutions:**
- Increase `batchDelay`
- Use React.memo or useMemo
- Reduce `batchSize`

## Related Documentation

- [Graph Viewport API](./GRAPH_VIEWPORT_API.md)
- [WebSocket Real-Time Updates](./WEBSOCKET_REALTIME.md)
- [Performance Optimization](./PERFORMANCE_OPTIMIZATION.md)
- [Frontend Graph Components](../reference/GRAPH_COMPONENTS.md)
