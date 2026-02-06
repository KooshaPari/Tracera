# useViewportGraph Hook - Quick Reference

## Import

```typescript
import { useViewportGraph, useViewportGraphArrays, type ViewportBounds } from '@/hooks';
```

## Basic Usage

```typescript
const { nodes, edges, loadViewport, isLoading } = useViewportGraph(projectId);

// Convert Maps to Arrays for React Flow
const { nodes: nodeArray, edges: edgeArray } = useViewportGraphArrays(nodes, edges);

// In viewport change handler
const handleViewportChange = (viewport: ViewportBounds) => {
  loadViewport(viewport);
};
```

## API

### Hook Signature

```typescript
useViewportGraph(
  projectId: string,
  options?: {
    bufferPx?: number;  // Default: 500
    onRegionLoaded?: (regionKey, nodeCount, edgeCount) => void;
  }
): UseViewportGraphResult
```

### Return Type

```typescript
interface UseViewportGraphResult {
  nodes: Map<string, Node>;              // All loaded nodes
  edges: Map<string, Edge>;              // All loaded edges
  loadedRegions: Set<string>;            // Cached region keys
  loadViewport: (viewport) => Promise<void>;  // Load viewport data
  isLoading: boolean;                    // Loading state
  clearCache: () => void;                // Clear all cached data
  getNode: (id: string) => Node | undefined;  // O(1) lookup
  getEdge: (id: string) => Edge | undefined;  // O(1) lookup
}
```

### ViewportBounds Type

```typescript
interface ViewportBounds {
  minX: number;    // Left edge
  minY: number;    // Top edge
  maxX: number;    // Right edge
  maxY: number;    // Bottom edge
  zoom: number;    // Current zoom level
}
```

## Complete Example

```typescript
import { useCallback } from 'react';
import ReactFlow, { useReactFlow } from '@xyflow/react';
import { useViewportGraph, useViewportGraphArrays } from '@/hooks';

function GraphView({ projectId }: { projectId: string }) {
  // Initialize hook
  const {
    nodes: nodeMap,
    edges: edgeMap,
    loadViewport,
    isLoading,
    clearCache
  } = useViewportGraph(projectId, {
    bufferPx: 500,
    onRegionLoaded: (key, nodes, edges) => {
      console.log(`Loaded region ${key}: ${nodes} nodes, ${edges} edges`);
    }
  });

  // Convert to arrays
  const { nodes, edges } = useViewportGraphArrays(nodeMap, edgeMap);

  // Get React Flow instance
  const reactFlow = useReactFlow();

  // Handle viewport changes
  const handleMove = useCallback(() => {
    const { x, y, zoom } = reactFlow.getViewport();
    const { width, height } = reactFlow.getSize();

    const minX = -x / zoom;
    const minY = -y / zoom;
    const maxX = minX + width / zoom;
    const maxY = minY + height / zoom;

    loadViewport({ minX, minY, maxX, maxY, zoom });
  }, [reactFlow, loadViewport]);

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onMove={handleMove}
        fitView
      >
        {isLoading && <LoadingIndicator />}
      </ReactFlow>
    </div>
  );
}
```

## Performance Tips

### 1. Buffer Size
- **Small (200px)**: Minimal memory, more API calls
- **Medium (500px)**: Balanced (default)
- **Large (1000px)**: Smoother panning, more memory

### 2. Cache Management
```typescript
// Clear cache when switching projects
useEffect(() => {
  clearCache();
}, [projectId, clearCache]);

// Periodic cleanup for long sessions
useEffect(() => {
  const interval = setInterval(() => {
    if (nodeMap.size > 10000) {
      clearCache();
    }
  }, 5 * 60 * 1000); // Every 5 minutes

  return () => clearInterval(interval);
}, [nodeMap.size, clearCache]);
```

### 3. Debounce Viewport Changes
```typescript
const debouncedLoadViewport = useMemo(
  () => debounce(loadViewport, 150),
  [loadViewport]
);
```

## Region System

### Grid Calculation
- Grid size: 500px
- Region key: `{Math.floor(x/500)},{Math.floor(y/500)}`

### Examples
| Viewport Position | Region Key |
|-------------------|------------|
| (0-499, 0-499)    | "0,0"      |
| (500-999, 0-499)  | "1,0"      |
| (0-499, 500-999)  | "0,1"      |
| (1000-1499, 500-999) | "2,1"   |

## Common Patterns

### Pattern 1: Loading Indicator
```typescript
{isLoading && (
  <div className="absolute top-4 right-4 bg-black/80 text-white px-4 py-2 rounded">
    Loading region...
  </div>
)}
```

### Pattern 2: Stats Display
```typescript
const stats = useMemo(() => ({
  nodes: nodeMap.size,
  edges: edgeMap.size,
  regions: loadedRegions.size
}), [nodeMap.size, edgeMap.size, loadedRegions.size]);

return (
  <div>Loaded: {stats.nodes} nodes, {stats.edges} edges</div>
);
```

### Pattern 3: Refresh Button
```typescript
<button onClick={clearCache}>
  Refresh Graph
</button>
```

## Troubleshooting

### Issue: Duplicate API Calls
**Solution**: Hook prevents this automatically via `loadingRegionsRef`

### Issue: Memory Usage Too High
**Solutions**:
1. Reduce `bufferPx`
2. Call `clearCache()` periodically
3. Consider implementing LRU eviction

### Issue: Slow Loading
**Solutions**:
1. Increase `bufferPx` to preload more
2. Debounce viewport changes
3. Optimize backend endpoint

## Backend Requirements

### Endpoint
```
POST /api/v1/projects/{projectId}/graph/viewport
```

### Request
```json
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

### Response
```json
{
  "nodes": [
    { "id": "node-1", "position": { "x": 100, "y": 100 }, "data": {...} }
  ],
  "edges": [
    { "id": "edge-1", "source": "node-1", "target": "node-2" }
  ],
  "metadata": {
    "regionKey": "0,0",
    "totalNodesInRegion": 150,
    "totalEdgesInRegion": 200
  }
}
```

## Testing

### Unit Tests
```bash
bun test src/hooks/__tests__/useViewportGraph.test.ts
```

### Manual Testing Checklist
1. Load large graph (10k+ nodes)
2. Pan around - verify progressive loading
3. Return to visited region - verify no re-fetch
4. Clear cache - verify data removed
5. Check network tab - only visible regions fetched
6. Test different zoom levels
7. Test rapid panning - no duplicate requests

## See Also

- [useViewportGraph.example.tsx](../../apps/web/src/hooks/useViewportGraph.example.tsx) - Full examples
- [useGraphs.ts](../../apps/web/src/hooks/useGraphs.ts) - Standard graph loading
- [useViewportCulling.ts](../../apps/web/src/hooks/useViewportCulling.ts) - Edge culling
- [Phase 4 Task 4.1 Part 2 Completion](../reports/phase_four-task4.1-part2-completion.md) - Full report
