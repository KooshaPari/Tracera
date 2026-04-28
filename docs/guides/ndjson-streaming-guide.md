# NDJSON Streaming Guide

## Overview

NDJSON (Newline Delimited JSON) streaming enables efficient transfer of large datasets by streaming data line-by-line instead of loading everything into memory at once.

## Features

- **Memory Efficient**: Streams data incrementally without loading entire datasets
- **Progress Tracking**: Real-time progress updates during streaming
- **Cancellable**: Abort streaming operations at any time
- **Error Handling**: Graceful error handling with detailed error messages
- **Type Safe**: Full TypeScript support with type inference

## Architecture

### Backend (Go)

The backend uses Go's `bufio.Writer` to stream NDJSON responses:

```go
// Stream handler
func (h *StreamHandler) StreamItems(c echo.Context) error {
    c.Response().Header().Set("Content-Type", "application/x-ndjson")
    writer := bufio.NewWriter(c.Response().Writer)
    defer writer.Flush()

    // Stream items line by line
    for item := range items {
        h.writeNDJSONLine(writer, item)
        if count % 10 == 0 {
            writer.Flush() // Flush periodically
        }
    }
}
```

### Frontend (TypeScript)

The frontend uses Web Streams API for parsing:

```typescript
async function* parseNDJSON(response: Response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (line.trim()) yield JSON.parse(line);
        }
    }
}
```

## Backend API Endpoints

### Stream Items

**Endpoint**: `GET /api/v1/items/stream`

**Query Parameters**:
- `project_id` (optional): Filter by project
- `limit` (optional): Maximum number of items
- `offset` (optional): Starting offset

**Response Format**:
```ndjson
{"id": "1", "title": "Item 1", "type": "requirement"}
{"id": "2", "title": "Item 2", "type": "feature"}
{"type": "progress", "count": 2, "offset": 2}
{"id": "3", "title": "Item 3", "type": "task"}
{"type": "complete", "total_count": 3}
```

### Stream Graph Data

**Endpoint**: `GET /api/v1/graphs/:id/stream`

**Response Format**:
```ndjson
{"type": "section", "name": "nodes", "count": 100}
{"type": "node", "data": {"id": "n1", "label": "Node 1"}}
{"type": "node", "data": {"id": "n2", "label": "Node 2"}}
{"type": "progress", "section": "nodes", "count": 50, "total": 100}
{"type": "section", "name": "edges", "count": 50}
{"type": "edge", "data": {"source": "n1", "target": "n2"}}
{"type": "complete", "nodes": 100, "edges": 50}
```

### Stream Export

**Endpoint**: `GET /api/v1/export/:type/stream`

**Path Parameters**:
- `type`: Export format (`json` or `csv`)

**Query Parameters**:
- `project_id` (required): Project to export

**Response Format**:
```ndjson
{"type": "export", "format": "json", "project_id": "proj-123"}
{"type": "item", "data": {...}}
{"type": "item", "data": {...}}
{"type": "progress", "count": 100}
{"type": "complete", "count": 250}
```

## Frontend Usage

### Basic Streaming

```typescript
import { streamItems } from '@/api/streaming';

// Simple iteration
for await (const item of streamItems({ projectId: 'proj-123' })) {
    console.log('Received item:', item);
}
```

### With Progress Tracking

```typescript
import { useStreamItems } from '@/hooks/useStreaming';
import { StreamingProgress } from '@/components/StreamingProgress';

function MyComponent() {
    const { items, state, startStreaming } = useStreamItems();

    return (
        <>
            <button onClick={() => startStreaming({ projectId: 'proj-123' })}>
                Start Streaming
            </button>

            <StreamingProgress
                stats={state.stats}
                isStreaming={state.isStreaming}
                showThroughput
            />

            <div>Received {items.length} items</div>
        </>
    );
}
```

### Cancellable Streaming

```typescript
import { createCancellableItemStream } from '@/api/streaming';

const { stream, cancel } = createCancellableItemStream({ projectId: 'proj-123' });

// Start streaming
(async () => {
    for await (const item of stream) {
        console.log(item);
    }
})();

// Cancel later
setTimeout(() => cancel(), 5000);
```

### Batch Processing

```typescript
import { loadItemsInBatches } from '@/api/streaming';

await loadItemsInBatches(
    { projectId: 'proj-123', batchSize: 50 },
    async (batch) => {
        // Process batch of 50 items
        await processBatch(batch);
    }
);
```

### Progressive Graph Loading

```typescript
import { loadGraphProgressive } from '@/api/streaming';

await loadGraphProgressive(
    'graph-123',
    {
        onProgress: (stats) => console.log(stats),
        onMetadata: (meta) => console.log(meta)
    },
    {
        onNodesReceived: (nodes) => {
            // Update graph with new nodes
            updateGraphNodes(nodes);
        },
        onEdgesReceived: (edges) => {
            // Update graph with new edges
            updateGraphEdges(edges);
        }
    }
);
```

## Metadata Events

NDJSON streams include metadata events for progress tracking:

### Progress Event
```json
{
    "type": "progress",
    "count": 100,
    "offset": 100,
    "section": "nodes",
    "total": 500
}
```

### Section Event
```json
{
    "type": "section",
    "name": "nodes",
    "count": 500
}
```

### Complete Event
```json
{
    "type": "complete",
    "total_count": 500,
    "nodes": 500,
    "edges": 250
}
```

### Error Event
```json
{
    "type": "error",
    "error": "Database connection failed"
}
```

## Performance Optimization

### Backend

1. **Batch Size**: Use appropriate batch sizes (default: 100)
2. **Flush Frequency**: Flush writer every 10 items
3. **Context Cancellation**: Check context for client disconnection

```go
// Check for cancellation
select {
case <-ctx.Done():
    return ctx.Err()
default:
}

// Flush periodically
if count%10 == 0 {
    writer.Flush()
}
```

### Frontend

1. **Batch Updates**: Update UI in batches, not on every item
2. **Virtual Scrolling**: Use virtual scrolling for large lists
3. **Debouncing**: Debounce progress updates

```typescript
// Update UI every 10 items
if (receivedItems.length % 10 === 0) {
    setItems([...receivedItems]);
}
```

## Error Handling

### Backend Errors

Errors are sent as NDJSON lines:

```go
errorLine := map[string]interface{}{
    "error": err.Error(),
    "type":  "error",
}
h.writeNDJSONLine(writer, errorLine)
```

### Frontend Error Recovery

```typescript
const { items, state, startStreaming } = useStreamItems();

if (state.error) {
    // Handle error
    console.error('Streaming error:', state.error);

    // Retry logic
    setTimeout(() => startStreaming(options), 1000);
}
```

## Testing

### Backend Tests

```go
func TestStreamHandler_StreamItems(t *testing.T) {
    // Create test handler
    handler := NewStreamHandler(mockRepo, mockGraphSvc, mockExportSvc)

    // Create test request
    req := httptest.NewRequest(http.MethodGet, "/api/v1/items/stream", nil)
    rec := httptest.NewRecorder()
    c := e.NewContext(req, rec)

    // Execute
    err := handler.StreamItems(c)

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, "application/x-ndjson", rec.Header().Get("Content-Type"))
}
```

### Frontend Tests

```typescript
import { parseNDJSON } from '@/lib/ndjson-parser';

it('should parse NDJSON stream', async () => {
    const lines = [
        '{"id": 1}',
        '{"id": 2}',
    ];
    const response = createNDJSONResponse(lines);
    const items = [];

    for await (const item of parseNDJSON(response)) {
        items.push(item);
    }

    expect(items).toHaveLength(2);
});
```

## Best Practices

1. **Use Streaming for Large Datasets**: Datasets > 1000 items
2. **Show Progress Indicators**: Always show progress for better UX
3. **Implement Cancellation**: Allow users to cancel long operations
4. **Handle Errors Gracefully**: Show error messages and retry options
5. **Optimize Batch Sizes**: Balance between performance and memory
6. **Test with Large Data**: Test with realistic data volumes
7. **Monitor Performance**: Track throughput and latency metrics

## Common Use Cases

### 1. Large Item Lists

```typescript
const { items, state, startStreaming } = useStreamItems();

<StreamingProgress stats={state.stats} isStreaming={state.isStreaming} />
<VirtualList items={items} />
```

### 2. Graph Visualization

```typescript
const { nodes, edges, state, startStreaming } = useStreamGraph();

// Progressive rendering
useEffect(() => {
    if (nodes.length > 0) {
        renderGraph(nodes, edges);
    }
}, [nodes, edges]);
```

### 3. Data Export

```typescript
const { data, state, startExport, downloadAsFile } = useStreamExport();

startExport({ projectId: 'proj-123', type: 'json' });
// When complete
downloadAsFile('export.json');
```

## Troubleshooting

### Stream Not Starting

- Check network connectivity
- Verify API endpoint availability
- Check browser console for errors

### Slow Streaming

- Increase backend batch size
- Reduce frontend update frequency
- Check network bandwidth

### Memory Issues

- Implement virtual scrolling
- Clear old items from memory
- Reduce batch sizes

### Incomplete Data

- Check for network interruptions
- Verify complete event received
- Check error events in stream

## References

- [NDJSON Specification](http://ndjson.org/)
- [Web Streams API](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API)
- [Echo Framework - Streaming](https://echo.labstack.com/guide/response/)
