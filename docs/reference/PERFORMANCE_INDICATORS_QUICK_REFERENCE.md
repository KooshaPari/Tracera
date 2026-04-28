# Performance Indicators - Quick Reference

## Quick Start

### 1. Add Compact Overlay to Graph

```typescript
import { PerformanceOverlay } from '@/components/graph';

<div className="relative w-full h-full">
  <GraphView />
  <PerformanceOverlay
    nodeCount={nodes.length}
    edgeCount={edges.length}
    visibleNodeCount={visibleNodes.length}
    visibleEdgeCount={visibleEdges.length}
  />
</div>
```

### 2. Show Detailed Stats Panel

```typescript
import { PerformanceStats } from '@/components/graph';

<PerformanceStats
  fps={fps}
  nodeCount={1000}
  edgeCount={2000}
  visibleNodeCount={250}
  visibleEdgeCount={500}
  variant="detailed"
/>
```

### 3. Monitor FPS in Real-Time

```typescript
import { useFPSMonitor } from '@/hooks';

const fpsStats = useFPSMonitor(true);
console.log(`FPS: ${fpsStats.current.toFixed(1)}`);
```

### 4. Track Memory Usage

```typescript
import { useMemoryMonitor } from '@/hooks';

const memory = useMemoryMonitor(true);
if (memory) {
  console.log(`Memory: ${memory.usedJSHeapSize.toFixed(1)} MB`);
}
```

## Components

### PerformanceStats

**Props:**

- `fps: number` - Current FPS
- `nodeCount: number` - Total nodes
- `edgeCount: number` - Total edges
- `visibleNodeCount: number` - Visible nodes
- `visibleEdgeCount: number` - Visible edges
- `memoryUsage?: number` - Memory in MB (optional)
- `renderTime?: number` - Render time in ms (optional)
- `variant?: 'compact' | 'detailed'` - Display style (default: 'compact')

**Variants:**

- **Compact**: Badge with FPS + node count + culling %
- **Detailed**: Card with progress bars and all metrics

### PerformanceOverlay

**Props:**

- `nodeCount: number` - Total nodes
- `edgeCount: number` - Total edges
- `visibleNodeCount: number` - Visible nodes
- `visibleEdgeCount: number` - Visible edges
- `position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'` - Position (default: 'top-right')
- `variant?: 'compact' | 'detailed'` - Display style (default: 'compact')

**Features:**

- Auto-integrates FPS and memory monitoring
- Positioned absolute overlay
- Non-intrusive design

### PerformanceChart

**Props:**

- `fps: number` - Current FPS value
- `width?: number` - Chart width in px (default: 200)
- `height?: number` - Chart height in px (default: 60)

**Features:**

- Real-time FPS history
- Color-coded trends (green/yellow/red)
- Canvas-based for performance
- Rolling 60-frame window

## Hooks

### useFPSMonitor

```typescript
const fpsStats = useFPSMonitor(enabled: boolean);

// Returns:
{
  current: number;  // Current FPS
  average: number;  // Average over 60 frames
  min: number;      // Minimum FPS
  max: number;      // Maximum FPS
}
```

**Features:**

- Uses requestAnimationFrame
- 60-frame rolling window
- Automatic cleanup
- Can be enabled/disabled

### useMemoryMonitor

```typescript
const memory = useMemoryMonitor(enabled: boolean, interval?: number);

// Returns MemoryStats | null:
{
  usedJSHeapSize: number;    // Used heap in MB
  totalJSHeapSize: number;   // Total heap in MB
  jsHeapSizeLimit: number;   // Heap limit in MB
  usage: number;             // Usage ratio (0-1)
}
```

**Features:**

- Chrome/Edge only (returns null elsewhere)
- Configurable update interval (default: 1000ms)
- Graceful fallback

## FPS Color Coding

| FPS Range | Color  | Meaning                |
| --------- | ------ | ---------------------- |
| ≥ 55      | Green  | Excellent performance  |
| 30-54     | Yellow | Acceptable performance |
| < 30      | Red    | Poor performance       |

## Common Patterns

### Conditional Display (Dev Only)

```typescript
const isDev = import.meta.env.DEV;

{isDev && (
  <PerformanceOverlay
    nodeCount={nodes.length}
    edgeCount={edges.length}
    visibleNodeCount={visible.length}
    visibleEdgeCount={visibleEdges.length}
  />
)}
```

### User-Toggleable

```typescript
const [showPerf, setShowPerf] = useLocalStorage('show-perf', false);

{showPerf && <PerformanceOverlay {...props} />}
```

### Performance Warning

```typescript
const fpsStats = useFPSMonitor(true);
const showWarning = fpsStats.average < 30;

{showWarning && (
  <Alert>Performance degraded. Consider reducing node count.</Alert>
)}
```

### Custom Dashboard

```typescript
const fpsStats = useFPSMonitor(true);
const memory = useMemoryMonitor(true);

<div className="grid grid-cols-2 gap-4">
  <PerformanceStats
    fps={fpsStats.current}
    nodeCount={1000}
    edgeCount={2000}
    visibleNodeCount={250}
    visibleEdgeCount={500}
    memoryUsage={memory?.usedJSHeapSize}
    variant="detailed"
  />
  <PerformanceChart fps={fpsStats.current} />
</div>
```

## Position Options

```typescript
// Top-right (default)
<PerformanceOverlay position="top-right" {...props} />

// Top-left
<PerformanceOverlay position="top-left" {...props} />

// Bottom-right
<PerformanceOverlay position="bottom-right" {...props} />

// Bottom-left
<PerformanceOverlay position="bottom-left" {...props} />
```

## Browser Support

| Feature           | Chrome | Firefox | Safari | Edge |
| ----------------- | ------ | ------- | ------ | ---- |
| FPS Monitor       | ✅     | ✅      | ✅     | ✅   |
| Memory Monitor    | ✅     | ❌      | ❌     | ✅   |
| Performance Chart | ✅     | ✅      | ✅     | ✅   |

## Performance Tips

1. **Use Compact Variant**: Less visual overhead
2. **Disable in Production**: Add conditional rendering
3. **Adjust Memory Interval**: Increase to 2000ms+ to reduce overhead
4. **Position Wisely**: Avoid blocking important UI
5. **Monitor Conditionally**: Only enable when debugging

## Files

### Components

- `src/components/graph/PerformanceStats.tsx`
- `src/components/graph/PerformanceOverlay.tsx`
- `src/components/graph/PerformanceChart.tsx`

### Hooks

- `src/hooks/useFPSMonitor.ts`
- `src/hooks/useMemoryMonitor.ts`

### Documentation

- `src/components/graph/PERFORMANCE_INDICATORS_EXAMPLE.md`

### Tests

- `src/__tests__/components/graph/PerformanceIndicators.test.tsx`

### Stories

- `src/components/graph/__stories__/PerformanceIndicators.stories.tsx`

## Storybook

```bash
bun run storybook
```

Navigate to: **Graph/Performance Indicators**

Stories available:

- Compact/Detailed Stats
- High/Medium/Low Performance
- Chart Variations
- Overlay Positions
- Live Monitoring
- Complete Dashboard
- Stress Tests
- Comparison Views

## Testing

```bash
bun test src/__tests__/components/graph/PerformanceIndicators.test.tsx
```

Test coverage:

- Component rendering
- FPS color classification
- Culling calculations
- Hook behavior
- Integration scenarios
