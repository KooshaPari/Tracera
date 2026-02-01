# useViewportGraph Hook - Quick Start Guide

Get started with progressive viewport-based graph loading in 5 minutes.

## Installation

The hook is already available in the codebase. No additional installation needed.

```typescript
import { useViewportGraph } from '@/hooks';
```

## Basic Usage (30 seconds)

```typescript
import { useViewportGraph } from '@/hooks';
import ReactFlow from '@xyflow/react';

function MyGraph({ projectId }: { projectId: string }) {
  const { nodes, edges } = useViewportGraph(projectId);

  return <ReactFlow nodes={nodes} edges={edges} />;
}
```

**That's it!** The hook auto-loads the initial viewport on mount.

## Add Loading Indicators (1 minute)

```typescript
function MyGraph({ projectId }: { projectId: string }) {
  const { nodes, edges, isLoading, totalCount } = useViewportGraph(projectId);

  return (
    <div>
      <div className="status">
        {isLoading ? "Loading..." : `${nodes.length} / ${totalCount} nodes`}
      </div>
      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}
```

## Add Viewport Tracking (2 minutes)

```typescript
import { useCallback } from 'react';
import { useReactFlow } from '@xyflow/react';

function MyGraph({ projectId }: { projectId: string }) {
  const { nodes, edges, loadViewport } = useViewportGraph(projectId);
  const reactFlowInstance = useReactFlow();

  const handleMove = useCallback((viewport) => {
    const { x, y, zoom } = viewport;
    const { width, height } = reactFlowInstance.getSize();

    loadViewport({
      minX: -x / zoom,
      minY: -y / zoom,
      maxX: (-x + width) / zoom,
      maxY: (-y + height) / zoom,
      zoom
    });
  }, [loadViewport, reactFlowInstance]);

  return <ReactFlow nodes={nodes} edges={edges} onMove={handleMove} />;
}
```

## Add Directional Indicators (3 minutes)

```typescript
function MyGraph({ projectId }: { projectId: string }) {
  const { nodes, edges, hasMore, totalCount } = useViewportGraph(projectId);

  return (
    <div>
      <div className="status">
        Loaded: {nodes.length} / {totalCount}
        <div className="indicators">
          {hasMore.north && "⬆️ More above"}
          {hasMore.south && "⬇️ More below"}
          {hasMore.east && "➡️ More right"}
          {hasMore.west && "⬅️ More left"}
        </div>
      </div>
      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}
```

## Add Region Loading Callback (5 minutes)

```typescript
import { useState } from 'react';

function MyGraph({ projectId }: { projectId: string }) {
  const [stats, setStats] = useState({ regions: 0, nodes: 0 });

  const { nodes, edges } = useViewportGraph(projectId, {
    bufferPx: 1000, // Larger buffer for smoother panning
    onRegionLoaded: (regionKey, nodeCount, edgeCount) => {
      console.log(`Loaded region ${regionKey}`);
      setStats(prev => ({
        regions: prev.regions + 1,
        nodes: prev.nodes + nodeCount
      }));
    }
  });

  return (
    <div>
      <div className="stats">
        Regions: {stats.regions} | Nodes: {stats.nodes}
      </div>
      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}
```

## Complete Example

```typescript
import { useCallback, useState } from 'react';
import { useViewportGraph } from '@/hooks';
import ReactFlow, { useReactFlow, ReactFlowProvider } from '@xyflow/react';

function GraphInner({ projectId }: { projectId: string }) {
  const reactFlowInstance = useReactFlow();
  const [stats, setStats] = useState({ regions: 0 });

  const {
    nodes,
    edges,
    loadViewport,
    isLoading,
    totalCount,
    hasMore,
    loadedRegionCount
  } = useViewportGraph(projectId, {
    bufferPx: 1000,
    onRegionLoaded: (regionKey) => {
      console.log(`Loaded ${regionKey}`);
      setStats(prev => ({ regions: prev.regions + 1 }));
    }
  });

  const handleMove = useCallback((viewport) => {
    const { x, y, zoom } = viewport;
    const { width, height } = reactFlowInstance.getSize();

    loadViewport({
      minX: -x / zoom,
      minY: -y / zoom,
      maxX: (-x + width) / zoom,
      maxY: (-y + height) / zoom,
      zoom
    });
  }, [loadViewport, reactFlowInstance]);

  return (
    <div className="graph-container">
      {/* Status Bar */}
      <div className="status-bar">
        <div>Loaded: {nodes.length} / {totalCount} nodes</div>
        <div>Regions: {loadedRegionCount}</div>
        {isLoading && <div className="spinner">Loading...</div>}
      </div>

      {/* Directional Indicators */}
      <div className="indicators">
        {hasMore.north && <div className="arrow north">⬆️</div>}
        {hasMore.south && <div className="arrow south">⬇️</div>}
        {hasMore.east && <div className="arrow east">➡️</div>}
        {hasMore.west && <div className="arrow west">⬅️</div>}
      </div>

      {/* Graph */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onMove={handleMove}
        fitView
      />
    </div>
  );
}

export function MyGraph({ projectId }: { projectId: string }) {
  return (
    <ReactFlowProvider>
      <GraphInner projectId={projectId} />
    </ReactFlowProvider>
  );
}
```

## Configuration Options

```typescript
useViewportGraph(projectId, {
  bufferPx: 500,        // Default: 500px buffer around viewport
  onRegionLoaded: (regionKey, nodeCount, edgeCount) => {
    // Called when a region finishes loading
  }
});
```

## Common Patterns

### Debounced Loading

```typescript
import { useDebouncedCallback } from 'use-debounce';

const debouncedLoad = useDebouncedCallback(loadViewport, 200);

<ReactFlow onMove={(vp) => debouncedLoad(calculateBounds(vp))} />
```

### Loading Overlay

```typescript
{isLoading && (
  <div className="loading-overlay">
    <div className="spinner" />
    Loading region...
  </div>
)}
```

### Progress Indicator

```typescript
<progress
  value={nodes.length}
  max={totalCount}
  className="loading-progress"
/>
```

## Performance Tips

1. **Use larger buffer for rapid panning**: `bufferPx: 1000`
2. **Debounce viewport changes**: Prevents excessive API calls
3. **Monitor `loadedRegionCount`**: Track memory usage
4. **Use `hasMore` for infinite scroll**: Show "load more" buttons

## Troubleshooting

### Nodes not appearing
- Check browser console for API errors
- Verify backend endpoint is available
- Ensure projectId is valid

### Duplicate loads
- Hook prevents duplicates automatically
- Check backend logs if still occurring
- Verify network tab shows only one request per region

### Performance issues
- Reduce `bufferPx` to minimize preloading
- Add debouncing to viewport changes
- Check backend response times

## Next Steps

- [Full Documentation](../useViewportGraph.README.md)
- [Advanced Examples](../useViewportGraph.example.tsx)
- [API Reference](../useViewportGraph.ts)

## Support

For issues or questions:
1. Check the [full README](../useViewportGraph.README.md)
2. Review [example implementations](../useViewportGraph.example.tsx)
3. Check test file for usage patterns
