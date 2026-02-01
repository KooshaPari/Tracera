# Performance Indicators - Usage Examples

Complete guide for using the performance monitoring components.

## Quick Start

### Compact Overlay

```typescript
import { PerformanceOverlay } from '@/components/graph/PerformanceOverlay';

function GraphView() {
  const { nodes, edges, visibleNodes, visibleEdges } = useGraph();

  return (
    <div className="relative w-full h-full">
      <Graph nodes={nodes} edges={edges} />

      <PerformanceOverlay
        nodeCount={nodes.length}
        edgeCount={edges.length}
        visibleNodeCount={visibleNodes.length}
        visibleEdgeCount={visibleEdges.length}
        position="top-right"
        variant="compact"
      />
    </div>
  );
}
```

### Detailed Stats Panel

```typescript
import { PerformanceOverlay } from '@/components/graph/PerformanceOverlay';

function GraphView() {
  return (
    <div className="relative w-full h-full">
      <Graph />

      <PerformanceOverlay
        nodeCount={1000}
        edgeCount={2000}
        visibleNodeCount={250}
        visibleEdgeCount={500}
        position="bottom-right"
        variant="detailed"
      />
    </div>
  );
}
```

## Individual Components

### FPS Monitor Hook

```typescript
import { useFPSMonitor } from '@/hooks/useFPSMonitor';

function MyComponent() {
  const fpsStats = useFPSMonitor(true);

  return (
    <div>
      <p>Current: {fpsStats.current.toFixed(1)} FPS</p>
      <p>Average: {fpsStats.average.toFixed(1)} FPS</p>
      <p>Min: {fpsStats.min.toFixed(1)} FPS</p>
      <p>Max: {fpsStats.max.toFixed(1)} FPS</p>
    </div>
  );
}
```

### Memory Monitor Hook

```typescript
import { useMemoryMonitor } from '@/hooks/useMemoryMonitor';

function MyComponent() {
  const memoryStats = useMemoryMonitor(true, 2000); // Update every 2s

  if (!memoryStats) {
    return <p>Memory API not available (Chrome only)</p>;
  }

  return (
    <div>
      <p>Used: {memoryStats.usedJSHeapSize.toFixed(1)} MB</p>
      <p>Total: {memoryStats.totalJSHeapSize.toFixed(1)} MB</p>
      <p>Limit: {memoryStats.jsHeapSizeLimit.toFixed(1)} MB</p>
      <p>Usage: {(memoryStats.usage * 100).toFixed(1)}%</p>
    </div>
  );
}
```

### Performance Stats Component

```typescript
import { PerformanceStats } from '@/components/graph/PerformanceStats';

function MyComponent() {
  return (
    <PerformanceStats
      fps={58.5}
      nodeCount={1000}
      edgeCount={2000}
      visibleNodeCount={250}
      visibleEdgeCount={500}
      memoryUsage={45.2}
      renderTime={12.5}
      variant="detailed"
    />
  );
}
```

### Performance Chart

```typescript
import { PerformanceChart } from '@/components/graph/PerformanceChart';
import { useFPSMonitor } from '@/hooks/useFPSMonitor';

function MyComponent() {
  const fpsStats = useFPSMonitor(true);

  return (
    <PerformanceChart
      fps={fpsStats.current}
      width={300}
      height={80}
    />
  );
}
```

## Advanced Usage

### Custom Performance Dashboard

```typescript
import { useFPSMonitor } from '@/hooks/useFPSMonitor';
import { useMemoryMonitor } from '@/hooks/useMemoryMonitor';
import { PerformanceStats } from '@/components/graph/PerformanceStats';
import { PerformanceChart } from '@/components/graph/PerformanceChart';

function CustomDashboard({ nodeCount, edgeCount, visibleCount, visibleEdgeCount }) {
  const fpsStats = useFPSMonitor(true);
  const memoryStats = useMemoryMonitor(true);

  return (
    <div className="flex gap-4">
      <PerformanceStats
        fps={fpsStats.current}
        nodeCount={nodeCount}
        edgeCount={edgeCount}
        visibleNodeCount={visibleCount}
        visibleEdgeCount={visibleEdgeCount}
        memoryUsage={memoryStats?.usedJSHeapSize}
        variant="detailed"
      />

      <div className="flex flex-col gap-2">
        <PerformanceChart fps={fpsStats.current} />
        <div className="text-xs text-muted-foreground">
          Avg: {fpsStats.average.toFixed(1)} FPS
        </div>
      </div>
    </div>
  );
}
```

### Conditional Performance Overlay

```typescript
import { PerformanceOverlay } from '@/components/graph/PerformanceOverlay';
import { useLocalStorage } from '@/hooks/useLocalStorage';

function GraphView() {
  const [showPerf, setShowPerf] = useLocalStorage('show-performance', false);

  return (
    <div className="relative w-full h-full">
      <Graph />

      {showPerf && (
        <PerformanceOverlay
          nodeCount={nodes.length}
          edgeCount={edges.length}
          visibleNodeCount={visibleNodes.length}
          visibleEdgeCount={visibleEdges.length}
        />
      )}

      <button onClick={() => setShowPerf(!showPerf)}>
        Toggle Performance
      </button>
    </div>
  );
}
```

### Performance-Based Warnings

```typescript
import { useFPSMonitor } from '@/hooks/useFPSMonitor';
import { Alert, AlertDescription } from '@/components/ui/alert';

function GraphView() {
  const fpsStats = useFPSMonitor(true);
  const showWarning = fpsStats.average < 30;

  return (
    <div>
      {showWarning && (
        <Alert variant="warning">
          <AlertDescription>
            Performance is degraded (avg {fpsStats.average.toFixed(1)} FPS).
            Consider reducing the number of visible nodes.
          </AlertDescription>
        </Alert>
      )}

      <Graph />
    </div>
  );
}
```

## Integration with Graph Components

### VirtualizedGraphView Integration

```typescript
import { VirtualizedGraphView } from '@/components/graph/VirtualizedGraphView';
import { PerformanceOverlay } from '@/components/graph/PerformanceOverlay';
import { useState } from 'react';

function GraphPage() {
  const [stats, setStats] = useState({
    total: 0,
    visible: 0,
    totalEdges: 0,
    visibleEdges: 0,
  });

  return (
    <div className="relative w-full h-full">
      <VirtualizedGraphView
        onStatsChange={(nodeCount, visibleCount, edgeCount, visibleEdgeCount) => {
          setStats({
            total: nodeCount,
            visible: visibleCount,
            totalEdges: edgeCount,
            visibleEdges: visibleEdgeCount,
          });
        }}
      />

      <PerformanceOverlay
        nodeCount={stats.total}
        edgeCount={stats.totalEdges}
        visibleNodeCount={stats.visible}
        visibleEdgeCount={stats.visibleEdges}
        variant="detailed"
      />
    </div>
  );
}
```

## Props Reference

### PerformanceStats

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| fps | number | required | Current frames per second |
| nodeCount | number | required | Total number of nodes |
| edgeCount | number | required | Total number of edges |
| visibleNodeCount | number | required | Number of visible nodes |
| visibleEdgeCount | number | required | Number of visible edges |
| memoryUsage | number | undefined | Memory usage in MB |
| renderTime | number | undefined | Render time in ms |
| variant | 'compact' \| 'detailed' | 'compact' | Display variant |

### PerformanceOverlay

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| nodeCount | number | required | Total number of nodes |
| edgeCount | number | required | Total number of edges |
| visibleNodeCount | number | required | Number of visible nodes |
| visibleEdgeCount | number | required | Number of visible edges |
| position | 'top-left' \| 'top-right' \| 'bottom-left' \| 'bottom-right' | 'top-right' | Overlay position |
| variant | 'compact' \| 'detailed' | 'compact' | Display variant |

### PerformanceChart

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| fps | number | required | Current FPS value |
| width | number | 200 | Chart width in pixels |
| height | number | 60 | Chart height in pixels |

### useFPSMonitor

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| enabled | boolean | true | Enable/disable monitoring |

Returns `FPSStats`:
- `current`: Current FPS
- `average`: Average FPS over last 60 frames
- `min`: Minimum FPS over last 60 frames
- `max`: Maximum FPS over last 60 frames

### useMemoryMonitor

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| enabled | boolean | true | Enable/disable monitoring |
| interval | number | 1000 | Update interval in ms |

Returns `MemoryStats | null`:
- `usedJSHeapSize`: Used heap in MB
- `totalJSHeapSize`: Total heap in MB
- `jsHeapSizeLimit`: Heap limit in MB
- `usage`: Usage ratio (0-1)

## Performance Tips

1. **Use Compact Variant by Default**: Only show detailed stats during development
2. **Disable in Production**: Consider disabling performance overlays in production builds
3. **Adjust Update Intervals**: Increase memory monitor interval to reduce overhead
4. **Conditional Rendering**: Only show performance indicators when needed
5. **Browser Support**: Memory monitoring only works in Chromium-based browsers

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| FPS Monitor | ✓ | ✓ | ✓ | ✓ |
| Memory Monitor | ✓ | ✗ | ✗ | ✓ |
| Performance Chart | ✓ | ✓ | ✓ | ✓ |
