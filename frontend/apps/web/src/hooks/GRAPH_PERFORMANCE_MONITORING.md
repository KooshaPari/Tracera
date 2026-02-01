# Graph Performance Monitoring

Comprehensive performance monitoring system for graph visualizations using the Performance API, React DevTools Profiler API, and custom metrics tracking.

## Overview

The `useGraphPerformanceMonitor` hook provides real-time performance insights for graph rendering optimizations:

- **FPS Tracking**: Frames per second during pan/zoom operations
- **Culling Effectiveness**: Node/Edge render counts vs totals
- **LOD Distribution**: Level of Detail usage across the graph
- **Cache Performance**: Hit rates for layout, grouping, and search caches
- **Timing Metrics**: Viewport load times and render durations
- **Memory Tracking**: JS heap usage (when available)

## Quick Start

### Basic Usage

```tsx
import { useGraphPerformanceMonitor } from "@/hooks/useGraphPerformanceMonitor";
import { useGraphCache } from "@/lib/graphCache";

function MyGraphComponent({ nodes, edges, visibleNodes, visibleEdges }) {
  const { getStats } = useGraphCache();

  const monitor = useGraphPerformanceMonitor({
    nodes,
    edges,
    visibleNodes,
    visibleEdges,
    cacheStats: getStats(),
    enabled: process.env.NODE_ENV === "development",
  });

  // Metrics are automatically logged to console every 5 seconds
  // Access current metrics: monitor.currentMetrics
  // View summary: monitor.getSummary()
}
```

### Integration with FlowGraphViewInner

The monitor is already integrated into `FlowGraphViewInner` and displays a performance overlay in development mode:

```tsx
// In FlowGraphViewInner.tsx
const performanceMonitor = useGraphPerformanceMonitor({
  nodes: items,
  edges: links,
  visibleNodes,
  visibleEdges: edgesForRendering,
  lodDistribution: {
    high: 10,
    medium: 20,
    low: 15,
    skeleton: 5,
  },
  cacheStats: getCacheStats(),
  enabled: process.env.NODE_ENV === "development",
  reportInterval: 5000,
  logToConsole: true,
  persistToStorage: true,
});

// Performance overlay is rendered in top-right panel (dev mode only)
```

## Configuration Options

### Hook Parameters

```typescript
interface UseGraphPerformanceMonitorConfig {
  // Graph data
  nodes: any[];              // Total nodes in graph
  edges: any[];              // Total edges in graph
  visibleNodes: any[];       // Currently rendered nodes
  visibleEdges: any[];       // Currently rendered edges

  // Optional metrics
  lodDistribution?: {
    high: number;            // Full detail nodes
    medium: number;          // Simplified nodes
    low: number;             // Minimal nodes
    skeleton?: number;       // Loading/error states
  };

  cacheStats?: {
    layout?: CacheStatistics;
    grouping?: CacheStatistics;
    search?: CacheStatistics;
  };

  // Monitoring control
  enabled?: boolean;                     // Default: true in dev, false in prod
  reportInterval?: number;               // Default: 5000ms
  logToConsole?: boolean;                // Default: true in dev
  persistToStorage?: boolean;            // Default: true in dev
  onMetricsUpdate?: (metrics) => void;   // Custom handler
}
```

### Return Value

```typescript
interface GraphPerformanceMonitor {
  currentMetrics: PerformanceMetrics | null;  // Latest snapshot
  history: PerformanceMetrics[];              // Historical data (last 50)
  reportMetrics: () => void;                  // Force immediate report
  reset: () => void;                          // Clear history and reset
  getSummary: () => string;                   // Human-readable summary
}
```

## Metrics Explained

### FPS (Frames Per Second)

Tracks rendering performance during interactions:

```typescript
fps: {
  current: 60,        // Current FPS
  average: 58,        // Average FPS (last 60 frames)
  min: 45,           // Minimum FPS observed
  max: 60,           // Maximum FPS observed
  samples: 60        // Number of frame samples
}
```

**Interpretation:**
- **55+ FPS**: Excellent performance (green)
- **30-55 FPS**: Acceptable performance (yellow)
- **< 30 FPS**: Poor performance, optimization needed (red)

### Node/Edge Culling

Measures viewport culling effectiveness:

```typescript
nodes: {
  total: 1000,           // Total nodes in graph
  rendered: 250,         // Nodes currently rendered
  culled: 750,          // Nodes culled (not rendered)
  cullingRatio: 75      // Percentage culled (higher is better)
}

edges: {
  total: 1500,
  rendered: 400,
  culled: 1100,
  cullingRatio: 73.3
}
```

**Interpretation:**
- **> 70% culling**: Excellent optimization
- **40-70% culling**: Good optimization
- **< 40% culling**: Limited benefit, consider disabling culling

### LOD Distribution

Shows how LOD (Level of Detail) is distributed across nodes:

```typescript
lod: {
  high: 50,       // Full detail (close to viewport center)
  medium: 100,    // Simplified detail (medium distance)
  low: 80,        // Minimal detail (far from viewport)
  skeleton: 20    // Loading/error states
}
```

**Interpretation:**
- More `high` nodes = more detail, higher GPU load
- More `low` nodes = less detail, better performance
- `skeleton` nodes indicate loading or error states

### Cache Hit Rates

Tracks cache effectiveness for expensive computations:

```typescript
cache: {
  layout: {
    hits: 80,
    misses: 20,
    hitRatio: 0.8,        // 80% hit rate
    totalRequests: 100
  },
  grouping: { ... },
  search: { ... },
  combined: {
    hits: 180,
    misses: 45,
    hitRatio: 0.8         // Overall cache effectiveness
  }
}
```

**Interpretation:**
- **> 80% hit rate**: Excellent caching
- **50-80% hit rate**: Good caching
- **< 50% hit rate**: Cache may need tuning or is under-utilized

### Timing Metrics

Measures rendering and computation durations:

```typescript
timing: {
  viewportLoadMs: 45,     // Time to render current viewport
  layoutComputeMs: 120,   // Time to compute layout
  cullingMs: 8,           // Time spent on viewport culling
  renderMs: 32            // Total render time
}
```

**Interpretation:**
- **< 16ms**: Excellent (60 FPS)
- **16-33ms**: Good (30-60 FPS)
- **> 33ms**: Slow, optimization needed

### Memory Usage

JS heap usage (available in Chrome/Edge):

```typescript
memory?: {
  usedJSHeapSize: 52428800,       // 50 MB
  totalJSHeapSize: 104857600,     // 100 MB
  jsHeapSizeLimit: 2147483648,    // 2 GB
  heapUsagePercent: 2.44          // 2.44% of limit
}
```

**Interpretation:**
- **< 5% usage**: Comfortable
- **5-10% usage**: Normal
- **> 10% usage**: Consider memory optimization

### Interaction State

Tracks user interactions:

```typescript
interaction: {
  isPanning: true,
  isZooming: false,
  panDuration: 1250,              // ms since pan started
  zoomDuration: 0,
  lastInteractionType: "pan"      // "pan" | "zoom" | "idle"
}
```

## Console Output

When `logToConsole` is enabled, metrics are logged every `reportInterval`:

```
[Graph Performance] 14:23:45
  FPS: 58 (avg: 56, min: 45, max: 60)
  Nodes: 250/1000 (75.0% culled)
  Edges: 400/1500 (73.3% culled)
  LOD: High=50 Med=100 Low=80 Skeleton=20
  Cache Hit Rate: 80.0% (180/225)
  Viewport Load: 45.2ms
  Memory: 50.0MB / 2048.0MB (2.4%)
```

## sessionStorage Persistence

Metrics are automatically persisted to `sessionStorage` for debugging:

```typescript
// Retrieve stored metrics
const stored = sessionStorage.getItem("trace_graph_performance_metrics");
const history = JSON.parse(stored);

// Last 100 metric snapshots are kept
console.log(history);
```

## React Profiler Integration

Track component render performance:

```tsx
import { Profiler } from "react";
import { createProfilerCallback } from "@/hooks/useGraphPerformanceMonitor";

const onRenderCallback = createProfilerCallback(
  "FlowGraphView",
  process.env.NODE_ENV === "development"
);

<Profiler id="FlowGraphView" onRender={onRenderCallback}>
  <FlowGraphViewInner {...props} />
</Profiler>
```

Profiler data is logged to console and stored in `sessionStorage`:

```
[Profiler: FlowGraphView]
  {
    id: "FlowGraphView",
    phase: "update",
    actualDuration: 12.5ms,
    baseDuration: 15.2ms,
    startTime: 1000.0,
    commitTime: 1012.5
  }
```

## Manual Performance Marks

Use `perfMark` for custom timing measurements:

```tsx
import { perfMark } from "@/hooks/useGraphPerformanceMonitor";

function expensiveOperation() {
  perfMark.start("layout-compute");

  // Expensive computation
  computeLayout();

  perfMark.end("layout-compute");
  // Logs: [Performance] layout-compute: 42.5ms
}
```

## Custom Handlers

Add custom metric processing:

```tsx
const monitor = useGraphPerformanceMonitor({
  nodes,
  edges,
  visibleNodes,
  visibleEdges,
  onMetricsUpdate: (metrics) => {
    // Send to analytics
    analytics.track("graph_performance", {
      fps: metrics.fps.current,
      cullingRatio: metrics.nodes.cullingRatio,
      cacheHitRate: metrics.cache.combined.hitRatio,
    });

    // Trigger alerts
    if (metrics.fps.current < 30) {
      console.warn("Low FPS detected!");
    }
  },
});
```

## Debugging Tips

### Low FPS

If FPS drops below 30:

1. Check culling ratios - should be > 70%
2. Check LOD distribution - reduce `high` detail nodes
3. Reduce animated edges (max 20)
4. Check memory usage - may need GC

### High Memory Usage

If heap usage > 10%:

1. Check cache sizes in `graphCache.ts`
2. Clear old entries: `clearAllCaches()`
3. Reduce history size (MAX_HISTORY_LENGTH)
4. Check for memory leaks in node data

### Poor Cache Hit Rate

If hit rate < 50%:

1. Increase cache size limits
2. Check cache key generation (may be too specific)
3. Verify prewarming is working
4. Check cache eviction strategy

## Production Considerations

The monitor is **disabled by default in production** to avoid overhead:

```typescript
// Automatic disabling
enabled: process.env.NODE_ENV === "development"

// Force enable in production (not recommended)
enabled: true
```

To enable in production for debugging:

1. Set `enabled: true` explicitly
2. Disable console logging: `logToConsole: false`
3. Use `onMetricsUpdate` to send to monitoring service
4. Increase `reportInterval` to reduce overhead (e.g., 30000ms)

## API Reference

### useGraphPerformanceMonitor

```typescript
function useGraphPerformanceMonitor(
  config: UseGraphPerformanceMonitorConfig
): GraphPerformanceMonitor
```

Main monitoring hook.

### createProfilerCallback

```typescript
function createProfilerCallback(
  monitorId: string,
  logToConsole?: boolean
): ProfilerOnRenderCallback
```

Creates React Profiler callback.

### perfMark

```typescript
const perfMark = {
  start: (name: string) => void;
  end: (name: string) => void;
};
```

Manual performance marking utilities.

## Example: Complete Integration

```tsx
import { useGraphPerformanceMonitor, perfMark } from "@/hooks/useGraphPerformanceMonitor";
import { useGraphCache } from "@/lib/graphCache";
import { Profiler } from "react";

function GraphComponent({ items, links }) {
  const { getStats } = useGraphCache();

  // Calculate visible items
  perfMark.start("viewport-culling");
  const { visibleNodes, visibleEdges } = calculateVisibleItems(items, links);
  perfMark.end("viewport-culling");

  // Monitor performance
  const monitor = useGraphPerformanceMonitor({
    nodes: items,
    edges: links,
    visibleNodes,
    visibleEdges,
    lodDistribution: calculateLODDistribution(visibleNodes),
    cacheStats: getStats(),
    enabled: process.env.NODE_ENV === "development",
    reportInterval: 5000,
    onMetricsUpdate: (metrics) => {
      if (metrics.fps.current < 30) {
        console.warn("Performance degraded!", metrics);
      }
    },
  });

  return (
    <Profiler id="GraphView" onRender={createProfilerCallback("GraphView")}>
      <div>
        {/* Performance overlay (dev only) */}
        {process.env.NODE_ENV === "development" && monitor.currentMetrics && (
          <PerformanceOverlay metrics={monitor.currentMetrics} />
        )}

        {/* Graph rendering */}
        <ReactFlow nodes={visibleNodes} edges={visibleEdges} />
      </div>
    </Profiler>
  );
}
```

## Related Documentation

- [Graph Caching](../../lib/graphCache.ts) - Cache configuration and usage
- [Viewport Culling](../../lib/viewportCulling.ts) - Culling implementation
- [LOD System](../utils/lod.ts) - Level of Detail logic
- [Performance Optimization Guide](../PERFORMANCE.md) - General optimization strategies
