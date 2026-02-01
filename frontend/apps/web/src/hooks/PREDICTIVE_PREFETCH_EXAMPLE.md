# Predictive Prefetch Integration Example

## Basic Usage with useViewportGraph

```typescript
import { useViewportGraph } from '@/hooks/useViewportGraph';
import { usePredictivePrefetch } from '@/hooks/usePredictivePrefetch';
import { useReactFlow } from '@xyflow/react';

function InfiniteGraphView({ projectId }: { projectId: string }) {
  const { getViewport } = useReactFlow();
  const viewport = getViewport();

  const { nodes, edges, loadViewport, isLoading } = useViewportGraph(projectId);

  // Enable predictive prefetching
  const { predictedViewport, velocity, isPanning } = usePredictivePrefetch({
    viewport: {
      x: viewport.x,
      y: viewport.y,
      zoom: viewport.zoom,
      width: window.innerWidth,
      height: window.innerHeight,
    },
    loadViewport,
    predictionHorizon: 500,  // Predict 500ms ahead
    velocityThreshold: 10,   // Min speed to trigger
  });

  return (
    <div className="relative h-full w-full">
      {/* Show velocity indicator during panning */}
      {isPanning && (
        <div className="absolute top-4 right-4 bg-blue-600 text-white px-3 py-1 rounded text-sm">
          Velocity: {Math.round(Math.sqrt(velocity.x ** 2 + velocity.y ** 2))} px/s
        </div>
      )}

      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}
```

## Advanced: Priority Loading

```typescript
function AdvancedGraphView({ projectId }: { projectId: string }) {
  const { getViewport } = useReactFlow();
  const viewport = getViewport();

  const { nodes, edges, loadViewport } = useViewportGraph(projectId);

  const { predictedViewport, isPredicting } = usePredictivePrefetch({
    viewport: {
      x: viewport.x,
      y: viewport.y,
      zoom: viewport.zoom,
      width: window.innerWidth,
      height: window.innerHeight,
    },
    loadViewport,
  });

  // Prioritize nodes in predicted viewport
  const prioritizedNodes = useMemo(() => {
    if (!predictedViewport) return nodes;

    return nodes.map(node => ({
      ...node,
      data: {
        ...node.data,
        priority: isNodeInPredictedViewport(
          {
            x: node.position.x,
            y: node.position.y,
            width: 100,
            height: 50,
          },
          predictedViewport
        ) ? 'high' : 'normal',
      },
    }));
  }, [nodes, predictedViewport]);

  return <ReactFlow nodes={prioritizedNodes} edges={edges} />;
}
```

## Custom Prediction Settings

```typescript
// Fast panning (aggressive prefetch)
usePredictivePrefetch({
  viewport,
  loadViewport,
  predictionHorizon: 1000,  // Predict 1 second ahead
  velocityThreshold: 5,     // Trigger at lower speeds
});

// Slow panning (conservative)
usePredictivePrefetch({
  viewport,
  loadViewport,
  predictionHorizon: 300,   // Predict 300ms ahead
  velocityThreshold: 20,    // Only trigger on fast panning
});
```

## Performance Metrics

```typescript
function GraphViewWithMetrics({ projectId }: { projectId: string }) {
  const { getViewport } = useReactFlow();
  const viewport = getViewport();

  const { loadViewport } = useViewportGraph(projectId);

  const { velocity, isPredicting, speed } = usePredictivePrefetch({
    viewport: {
      x: viewport.x,
      y: viewport.y,
      zoom: viewport.zoom,
      width: window.innerWidth,
      height: window.innerHeight,
    },
    loadViewport,
  });

  useEffect(() => {
    if (isPredicting) {
      console.log('Prefetch triggered:', {
        speed,
        direction: Math.atan2(velocity.y, velocity.x) * 180 / Math.PI,
      });
    }
  }, [isPredicting, velocity, speed]);

  return <ReactFlow ... />;
}
```

## Integration with GraphCache

```typescript
import { viewportToCacheKey } from '@/hooks/usePredictivePrefetch';

function CachedGraphView({ projectId }: { projectId: string }) {
  const { getViewport } = useReactFlow();
  const viewport = getViewport();

  const cacheRef = useRef(new Map());

  const loadViewportWithCache = useCallback((predicted: PredictedViewport) => {
    const cacheKey = viewportToCacheKey(predicted);

    // Check cache first
    if (cacheRef.current.has(cacheKey)) {
      return Promise.resolve(cacheRef.current.get(cacheKey));
    }

    // Fetch and cache
    return fetchGraphData(predicted).then(data => {
      cacheRef.current.set(cacheKey, data);
      return data;
    });
  }, []);

  const { predictedViewport } = usePredictivePrefetch({
    viewport: {
      x: viewport.x,
      y: viewport.y,
      zoom: viewport.zoom,
      width: window.innerWidth,
      height: window.innerHeight,
    },
    loadViewport: loadViewportWithCache,
  });

  return <ReactFlow ... />;
}
```
