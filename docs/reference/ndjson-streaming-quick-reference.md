# NDJSON Streaming Quick Reference

## Backend Endpoints

### Stream Items
```
GET /api/v1/items/stream?project_id={id}&limit={n}&offset={n}
```

### Stream Graph
```
GET /api/v1/graphs/{id}/stream
```

### Stream Export
```
GET /api/v1/export/{type}/stream?project_id={id}
```

## Frontend Hooks

### useStreamItems
```typescript
const { items, state, startStreaming, stopStreaming, reset } = useStreamItems();

startStreaming({ projectId: 'proj-123', limit: 1000 });
```

### useStreamGraph
```typescript
const { nodes, edges, state, startStreaming } = useStreamGraph();

startStreaming('graph-123', {
    onProgress: (stats) => console.log(stats),
    onMetadata: (meta) => console.log(meta)
});
```

### useStreamExport
```typescript
const { data, state, startExport, downloadAsFile } = useStreamExport();

startExport({ projectId: 'proj-123', type: 'json' });
downloadAsFile('export.json');
```

## API Functions

### Basic Streaming
```typescript
import { streamItems } from '@/api/streaming';

for await (const item of streamItems({ projectId: 'proj-123' })) {
    console.log(item);
}
```

### With Progress
```typescript
import { parseNDJSONWithProgress } from '@/lib/ndjson-parser';

for await (const item of parseNDJSONWithProgress(
    response,
    (stats) => console.log('Progress:', stats),
    (meta) => console.log('Metadata:', meta)
)) {
    console.log(item);
}
```

### Cancellable Stream
```typescript
import { createCancellableItemStream } from '@/api/streaming';

const { stream, cancel } = createCancellableItemStream({ projectId: 'proj-123' });

// Start streaming
(async () => {
    for await (const item of stream) {
        console.log(item);
    }
})();

// Cancel
cancel();
```

### Batch Processing
```typescript
import { loadItemsInBatches } from '@/api/streaming';

await loadItemsInBatches(
    { projectId: 'proj-123', batchSize: 50 },
    (batch) => processBatch(batch)
);
```

## Utility Functions

### Collect All
```typescript
import { collectNDJSON, parseNDJSON } from '@/lib/ndjson-parser';

const items = await collectNDJSON(parseNDJSON(response), 1000);
```

### Batch
```typescript
import { batchNDJSON } from '@/lib/ndjson-parser';

for await (const batch of batchNDJSON(stream, 50)) {
    console.log('Batch:', batch);
}
```

### Filter
```typescript
import { filterNDJSON } from '@/lib/ndjson-parser';

for await (const item of filterNDJSON(stream, item => item.active)) {
    console.log(item);
}
```

### Map
```typescript
import { mapNDJSON } from '@/lib/ndjson-parser';

for await (const id of mapNDJSON(stream, item => item.id)) {
    console.log(id);
}
```

## Components

### StreamingProgress
```tsx
import { StreamingProgress } from '@/components/StreamingProgress';

<StreamingProgress
    stats={state.stats}
    isStreaming={state.isStreaming}
    showThroughput
    showBytes
/>
```

### CompactStreamingProgress
```tsx
import { CompactStreamingProgress } from '@/components/StreamingProgress';

<CompactStreamingProgress
    stats={state.stats}
    isStreaming={state.isStreaming}
/>
```

### StreamingProgressBar
```tsx
import { StreamingProgressBar } from '@/components/StreamingProgress';

<StreamingProgressBar
    current={100}
    total={500}
    isStreaming={true}
/>
```

## Metadata Events

### Progress
```json
{"type": "progress", "count": 100, "offset": 100}
```

### Section
```json
{"type": "section", "name": "nodes", "count": 500}
```

### Complete
```json
{"type": "complete", "total_count": 500}
```

### Error
```json
{"type": "error", "error": "Error message"}
```

## Backend Implementation

### Stream Handler
```go
func (h *StreamHandler) StreamItems(c echo.Context) error {
    c.Response().Header().Set("Content-Type", "application/x-ndjson")
    writer := bufio.NewWriter(c.Response().Writer)
    defer writer.Flush()

    for _, item := range items {
        h.writeNDJSONLine(writer, item)
        if count%10 == 0 {
            writer.Flush()
        }
    }

    return nil
}
```

### Write NDJSON Line
```go
func (h *StreamHandler) writeNDJSONLine(writer *bufio.Writer, data interface{}) error {
    jsonData, err := json.Marshal(data)
    if err != nil {
        return err
    }
    writer.Write(jsonData)
    writer.WriteString("\n")
    return nil
}
```

## Performance Tips

1. **Batch Updates**: Update UI every 10-50 items
2. **Flush Frequency**: Flush writer every 10 items (backend)
3. **Virtual Scrolling**: Use for large lists
4. **Cancel on Unmount**: Clean up streams in useEffect
5. **Progress Throttling**: Update progress every 50 items

## Error Handling

### Frontend
```typescript
if (state.error) {
    console.error('Streaming error:', state.error);
    // Retry or show error message
}
```

### Backend
```go
errorLine := map[string]interface{}{
    "error": err.Error(),
    "type":  "error",
}
h.writeNDJSONLine(writer, errorLine)
```

## Testing

### Backend
```go
func TestStreamHandler_StreamItems(t *testing.T) {
    handler := NewStreamHandler(mockRepo, mockGraphSvc, mockExportSvc)
    req := httptest.NewRequest(http.MethodGet, "/api/v1/items/stream", nil)
    rec := httptest.NewRecorder()
    c := e.NewContext(req, rec)

    err := handler.StreamItems(c)

    assert.NoError(t, err)
    assert.Equal(t, "application/x-ndjson", rec.Header().Get("Content-Type"))
}
```

### Frontend
```typescript
it('should parse NDJSON stream', async () => {
    const response = createNDJSONResponse(['{"id": 1}', '{"id": 2}']);
    const items = [];

    for await (const item of parseNDJSON(response)) {
        items.push(item);
    }

    expect(items).toHaveLength(2);
});
```

## Common Patterns

### Progressive Loading
```typescript
useEffect(() => {
    if (projectId) {
        startStreaming({ projectId });
    }
}, [projectId]);
```

### Auto-retry
```typescript
const retry = async (fn: () => Promise<void>, attempts = 3) => {
    for (let i = 0; i < attempts; i++) {
        try {
            await fn();
            return;
        } catch (error) {
            if (i === attempts - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
};
```

### Cleanup
```typescript
useEffect(() => {
    return () => {
        stopStreaming();
    };
}, []);
```
