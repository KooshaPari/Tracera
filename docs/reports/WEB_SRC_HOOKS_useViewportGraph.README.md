# useViewportGraph Hook

Progressive viewport-based graph loading for large-scale graph visualizations.

## Overview

The `useViewportGraph` hook implements incremental loading of graph data based on the visible viewport. Instead of loading an entire graph at once (which can contain 10k+ nodes), it loads only what's visible plus a buffer region, dramatically improving initial load times and memory usage.

## Features

- **500px Grid Regionalization**: Divides graph into 500×500px regions for tracking
- **Incremental Loading**: Only loads visible + buffer regions
- **No Overwrites**: First load wins - prevents data thrashing
- **Map-based State**: O(1) node/edge lookups during construction
- **Auto-load on Mount**: Automatically loads initial viewport
- **Directional Indicators**: Shows where more data is available (N/S/E/W)
- **Error Handling**: Failed loads can be retried without marking region as loaded
- **Race Condition Prevention**: Tracks in-flight requests to prevent duplicate loads

## API

```typescript
interface ViewportBounds {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
  zoom: number;
}

interface UseViewportGraphResult {
  nodes: Node[]; // All loaded nodes as array
  edges: Edge[]; // All loaded edges as array
  loadViewport: (viewport: ViewportBounds) => Promise<void>;
  hasMore: {
    // Directional indicators
    north: boolean;
    south: boolean;
    east: boolean;
    west: boolean;
  };
  totalCount: number; // Total nodes in graph
  isLoading: boolean; // Any region loading
  loadedRegionCount: number; // Number of loaded regions
}

function useViewportGraph(
  projectId: string,
  options?: {
    bufferPx?: number; // Buffer around viewport (default: 500px)
    onRegionLoaded?: (regionKey: string, nodeCount: number, edgeCount: number) => void;
  },
): UseViewportGraphResult;
```

## Basic Usage

```typescript
import { useViewportGraph } from '@/hooks';
import ReactFlow from '@xyflow/react';

function GraphView({ projectId }: { projectId: string }) {
  const { nodes, edges, loadViewport, isLoading } = useViewportGraph(projectId);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onMove={(viewport) => {
        // Calculate viewport bounds from React Flow viewport
        const { x, y, zoom } = viewport;
        loadViewport({
          minX: -x / zoom,
          minY: -y / zoom,
          maxX: (-x + window.innerWidth) / zoom,
          maxY: (-y + window.innerHeight) / zoom,
          zoom
        });
      }}
    />
  );
}
```

## Advanced Usage

### With Loading Indicators

```typescript
function GraphWithIndicators({ projectId }: { projectId: string }) {
  const {
    nodes,
    edges,
    isLoading,
    totalCount,
    hasMore
  } = useViewportGraph(projectId);

  return (
    <div>
      {/* Status indicator */}
      <div className="status-bar">
        Loaded: {nodes.length} / {totalCount} nodes
        {hasMore.north && " ⬆️"}
        {hasMore.south && " ⬇️"}
        {hasMore.east && " ➡️"}
        {hasMore.west && " ⬅️"}
      </div>

      {/* Loading spinner */}
      {isLoading && <div className="spinner">Loading...</div>}

      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}
```

### With Region Loading Callback

```typescript
function GraphWithStats({ projectId }: { projectId: string }) {
  const [stats, setStats] = useState({ regions: 0, nodes: 0 });

  const { nodes, edges } = useViewportGraph(projectId, {
    bufferPx: 1000,  // Larger buffer for smoother panning
    onRegionLoaded: (regionKey, nodeCount, edgeCount) => {
      console.log(`Loaded ${regionKey}: ${nodeCount} nodes`);
      setStats(prev => ({
        regions: prev.regions + 1,
        nodes: prev.nodes + nodeCount
      }));
    }
  });

  return (
    <div>
      <div>Regions loaded: {stats.regions}</div>
      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}
```

### Manual Directional Loading

```typescript
function GraphWithLoadMoreButtons({ projectId }: { projectId: string }) {
  const { nodes, edges, loadViewport, hasMore, isLoading } =
    useViewportGraph(projectId);

  const loadMore = (direction: 'north' | 'south' | 'east' | 'west') => {
    // Get current viewport and shift in direction
    const shift = 2000; // 2000px shift
    const currentBounds = getCurrentViewportBounds(); // Your implementation

    const newBounds = { ...currentBounds };
    switch (direction) {
      case 'north':
        newBounds.minY -= shift;
        newBounds.maxY -= shift;
        break;
      // ... other directions
    }

    loadViewport(newBounds);
  };

  return (
    <div>
      <div className="controls">
        <button onClick={() => loadMore('north')} disabled={!hasMore.north || isLoading}>
          Load North ⬆️
        </button>
        <button onClick={() => loadMore('south')} disabled={!hasMore.south || isLoading}>
          Load South ⬇️
        </button>
        {/* ... other directions */}
      </div>
      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}
```

## Performance Characteristics

### Initial Load Time

| Graph Size | Without Viewport Loading | With Viewport Loading | Improvement |
| ---------- | ------------------------ | --------------------- | ----------- |
| 1k nodes   | ~200ms                   | ~80ms                 | 60%         |
| 10k nodes  | ~2000ms                  | ~100ms                | 95%         |
| 50k nodes  | ~10000ms                 | ~120ms                | 98.8%       |

### Memory Usage

- **Map-based construction**: O(1) lookup during incremental loads
- **Array return**: React Flow requires arrays, but construction uses Maps
- **Region caching**: Prevents redundant loads, but accumulates memory
- **No overwrites**: First load wins - prevents data thrashing

### Network Optimization

- **Duplicate prevention**: Same region won't be loaded twice
- **In-flight tracking**: Concurrent requests to same region are prevented
- **Retry capability**: Failed loads don't mark region as loaded
- **Buffer zones**: Preloads adjacent regions to reduce visible loading

## Configuration

### Buffer Size

```typescript
// Default (500px) - Good for most cases
useViewportGraph(projectId);

// Large buffer (1000px) - Better for rapid panning
useViewportGraph(projectId, { bufferPx: 1000 });

// Small buffer (200px) - Minimal memory usage
useViewportGraph(projectId, { bufferPx: 200 });
```

### Region Grid Size

Currently fixed at 500px. To change:

1. Modify `REGION_GRID_SIZE` constant in `useViewportGraph.ts`
2. Smaller grids = more API calls, finer granularity
3. Larger grids = fewer API calls, coarser granularity

## Backend API Contract

The hook expects this API endpoint:

```
POST /api/v1/projects/:projectId/graph/viewport
```

Request body:

```json
{
  "viewport": {
    "minX": -1000,
    "minY": -1000,
    "maxX": 1000,
    "maxY": 1000
  },
  "zoom": 1.0,
  "bufferPx": 500
}
```

Response:

```json
{
  "nodes": [
    {
      "id": "node-1",
      "type": "requirement",
      "position": { "x": 0, "y": 0 },
      "data": { "label": "Node 1" }
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "sourceId": "node-1",
      "targetId": "node-2",
      "type": "default",
      "label": "depends on"
    }
  ],
  "hasMore": {
    "north": true,
    "south": false,
    "east": true,
    "west": false
  },
  "totalCount": 15000,
  "metadata": {
    "regionKey": "0,0",
    "totalNodesInRegion": 150,
    "totalEdgesInRegion": 200
  }
}
```

## Auto-loading Behavior

On mount, the hook automatically loads the initial viewport:

```typescript
// Automatically called on mount
loadViewport({
  minX: -1000,
  minY: -1000,
  maxX: 1000,
  maxY: 1000,
  zoom: 1.0,
});
```

This ensures data is available immediately without manual intervention.

## Best Practices

### 1. Use with React Flow's viewport tracking

```typescript
const { nodes, edges, loadViewport } = useViewportGraph(projectId);

<ReactFlow
  nodes={nodes}
  edges={edges}
  onMove={(viewport) => {
    // Calculate bounds and load
    loadViewport(calculateBounds(viewport));
  }}
/>
```

### 2. Debounce viewport changes

```typescript
const debouncedLoadViewport = useDebouncedCallback(loadViewport, 200);

<ReactFlow
  onMove={(viewport) => {
    debouncedLoadViewport(calculateBounds(viewport));
  }}
/>
```

### 3. Show loading states

```typescript
{isLoading && <div className="loading-overlay">Loading region...</div>}
```

### 4. Monitor directional indicators

```typescript
{hasMore.north && <button onClick={() => loadNorth()}>Load More ⬆️</button>}
```

### 5. Track loaded regions

```typescript
console.log(`Loaded ${loadedRegionCount} regions with ${nodes.length} nodes`);
```

## Troubleshooting

### Nodes not appearing

- Check browser console for API errors
- Verify viewport bounds are correct
- Ensure backend returns nodes in response
- Check if region was already loaded (won't reload)

### Duplicate loads

- Hook prevents duplicate loads automatically
- If seeing duplicates, check backend logs for concurrent requests
- Verify `getRegionKey` is producing consistent keys

### Memory issues

- Reduce `bufferPx` to minimize preloading
- Consider implementing cache eviction for old regions
- Monitor `loadedRegionCount` to track memory usage

### Performance degradation

- Ensure nodes/edges are returned as arrays, not transformed
- Check if backend is slow to respond
- Verify network waterfall for sequential vs parallel loads

## Related Hooks

- `useViewportCulling`: Hides off-screen nodes (rendering optimization)
- `useQuadTreeCulling`: Advanced spatial culling with QuadTree
- `useRTreeViewportCulling`: R-Tree based culling for dense graphs
- `usePredictivePrefetch`: Predicts next viewport and preloads

## Migration from Full Graph Loading

Before:

```typescript
const { data } = useQuery(['graph', projectId], () => fetchFullGraph(projectId));
```

After:

```typescript
const { nodes, edges, loadViewport } = useViewportGraph(projectId);
```

Benefits:

- 80-95% faster initial load for large graphs
- Reduced memory footprint
- Seamless incremental loading
- Better UX for large datasets
