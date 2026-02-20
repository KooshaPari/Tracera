# Sigma.js WebGL Renderer - Quick Reference

Fast reference guide for using Sigma.js WebGL renderer integration.

---

## Quick Start

### Basic Hybrid Graph (Auto-switching)

```tsx
import { HybridGraphViewEnhanced } from '@/components/graph';

<HybridGraphViewEnhanced
  nodes={nodes}
  edges={edges}
  onNodeClick={(id) => console.log(id)}
/>
```

**Result**: Automatic switching at 10k node threshold.

---

## Components

### HybridGraphViewEnhanced

Auto-switches between ReactFlow and Sigma.js WebGL.

**Props:**
```typescript
{
  nodes: Node[];
  edges: Edge[];
  onNodeClick?: (nodeId: string) => void;
  onNodeExpand?: (nodeId: string) => void;
  onNodeNavigate?: (nodeId: string) => void;
  config?: HybridGraphConfig;
  className?: string;
}
```

**Config:**
```typescript
{
  nodeThreshold?: number;    // Default: 10000
  forceReactFlow?: boolean;  // Force ReactFlow mode
  forceWebGL?: boolean;      // Force WebGL mode
}
```

### SigmaGraphViewEnhanced

Direct WebGL rendering (for advanced use cases).

**Props:**
```typescript
{
  graph: Graph;              // Graphology graph
  onNodeClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null) => void;
  onNodeDoubleClick?: (nodeId: string) => void;
  onBackgroundClick?: () => void;
  selectedNodeId?: string | null;
  hoveredNodeId?: string | null;
  performanceMode?: 'balanced' | 'performance' | 'quality';
  className?: string;
}
```

---

## Performance Modes

| Mode | Use Case | Features |
|------|----------|----------|
| `quality` | < 1k nodes | All features, best visuals |
| `balanced` | 1k-50k nodes | Optimized, good balance |
| `performance` | > 50k nodes | Maximum performance |

**Auto-selection:**
- System automatically chooses mode based on node count
- Override with `performanceMode` prop if needed

---

## Thresholds

```typescript
const THRESHOLDS = {
  WEBGL_SWITCH: 10_000,      // ReactFlow → WebGL
  PERFORMANCE_MODE: 50_000,   // Balanced → Performance
  WARNING: 8_000,             // Show threshold warning
};
```

---

## LOD (Level of Detail)

### Zoom Levels

| Zoom | LOD | Features |
|------|-----|----------|
| < 0.3 | Far | Simple circles |
| 0.3-1.0 | Medium | Circles + icons |
| >= 1.0 | Close | Full detail + labels |
| >= 1.5 | Very Close | All features + labels |
| >= 2.0 | Ultra Close | Edge labels visible |

### Implementation

```typescript
if (zoomRatio < 0.3) {
  // Render simple circle
} else if (zoomRatio < 1.0) {
  // Render circle + type icon
} else {
  // Render full detail + label
}
```

---

## Performance Targets

| Node Count | FPS | Initial Render | Memory |
|-----------|-----|---------------|--------|
| 10k | 60 | < 500ms | ~30 MB |
| 50k | 60 | < 2s | ~150 MB |
| 100k | 60 | < 5s | ~300 MB |

---

## Event Handling

### Supported Events

```typescript
// All events work in both ReactFlow and WebGL modes
onNodeClick(nodeId: string)
onNodeHover(nodeId: string | null)
onNodeDoubleClick(nodeId: string)
onBackgroundClick()
onNodeExpand(nodeId: string)
onNodeNavigate(nodeId: string)
```

### Event Flow

**ReactFlow Mode (< 10k nodes):**
1. Direct event handlers
2. Rich interactions available
3. Full HTML rendering

**WebGL Mode (>= 10k nodes):**
1. Sigma event system
2. Opens detail panel on click
3. Canvas-only rendering

---

## Camera Controls

### Settings

```typescript
{
  minCameraRatio: 0.05,      // Max zoom in
  maxCameraRatio: 20,        // Max zoom out
  zoomingRatio: 1.3,         // Zoom speed
  enableCamera: true,        // Enable pan/zoom
}
```

### Gestures

| Action | Desktop | Mobile |
|--------|---------|--------|
| Zoom | Mouse wheel | Pinch |
| Pan | Drag | Drag |
| Select | Click | Tap |
| Expand | Double-click | Double-tap |

---

## Rendering Optimizations

### Viewport Culling

```typescript
// Only render visible nodes (with 100px buffer)
const isVisible = (x, y, viewportWidth, viewportHeight) => (
  x >= -100 &&
  x <= viewportWidth + 100 &&
  y >= -100 &&
  y <= viewportHeight + 100
);
```

**Impact:**
- 10% visible = 10x faster rendering
- 5% visible = 20x faster rendering

### Edge Hiding

Edges automatically hidden during:
- Pan operations
- Zoom operations
- Camera movements

**Re-enabled:**
- On interaction end
- After 200ms delay

### Adaptive Rendering

```typescript
// Based on node count
if (nodeCount > 50_000) {
  nodeType = 'fast';           // Simple rendering
  hideEdgesOnMove = true;      // Always hide edges
  labelThreshold = 1.5;        // Show labels later
}
```

---

## Type Icons

```typescript
const ICONS = {
  requirement: '📋',
  feature: '⭐',
  epic: '🎯',
  story: '📖',
  task: '📝',
  bug: '🐛',
  test: '✓',
  api: '🔌',
  database: '🗄️',
  code: '💻',
  wireframe: '🎨',
  ui_component: '🧩',
  page: '📄',
  security: '🔒',
  performance: '⚡',
};
```

---

## Status Colors

```typescript
const STATUS_COLORS = {
  done: '#10b981',         // Green
  in_progress: '#f59e0b',  // Orange
  todo: '#64748b',         // Gray
  blocked: '#ef4444',      // Red
  cancelled: '#94a3b8',    // Light gray
};
```

---

## Common Patterns

### Force WebGL Mode

```tsx
<HybridGraphViewEnhanced
  nodes={nodes}
  edges={edges}
  config={{ forceWebGL: true }}
/>
```

### Custom Threshold

```tsx
<HybridGraphViewEnhanced
  nodes={nodes}
  edges={edges}
  config={{ nodeThreshold: 15_000 }}
/>
```

### Performance Mode

```tsx
<SigmaGraphViewEnhanced
  graph={graph}
  performanceMode="performance"
/>
```

### With Detail Panel

```tsx
<HybridGraphViewEnhanced
  nodes={nodes}
  edges={edges}
  onNodeClick={(id) => {
    // Detail panel opens automatically in WebGL mode
    console.log('Selected:', id);
  }}
  onNodeExpand={(id) => {
    // Expand node hierarchy
    loadChildren(id);
  }}
/>
```

---

## Troubleshooting

### Low FPS

**Problem**: FPS < 30 with large graph

**Solutions:**
1. Enable performance mode: `performanceMode="performance"`
2. Reduce node count: Filter or paginate
3. Check browser: WebGL 2.0 required
4. Disable edge labels: `renderEdgeLabels: false`

### Transition Lag

**Problem**: Slow transition between modes

**Solution:**
```tsx
config={{
  nodeThreshold: 12_000  // Add buffer zone
}}
```

### Missing Features in WebGL

**Problem**: Can't see node images/progress bars

**Solution**: Click nodes to open detail panel (automatic in WebGL mode)

### Memory Issues

**Problem**: High memory usage with 100k+ nodes

**Solutions:**
1. Use streaming/pagination
2. Enable aggressive culling
3. Reduce edge count
4. Use simpler node types

---

## Testing

### Unit Tests

```bash
bun test src/__tests__/components/graph/SigmaGraphView.enhanced.unit.test.tsx
```

### E2E Tests

```bash
# Performance tests
bun test:e2e e2e/sigma-performance.spec.ts

# Transition tests
bun test:e2e e2e/sigma-transition.spec.ts
```

---

## Browser Support

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | 56+ | ✅ Full |
| Firefox | 51+ | ✅ Full |
| Safari | 15+ | ✅ Full |
| Edge | 79+ | ✅ Full |

**Requires**: WebGL 2.0

---

## Performance Tips

### DO ✅

- Use hybrid mode (automatic switching)
- Enable viewport culling
- Hide edges during pan/zoom
- Use LOD for large graphs
- Paginate very large graphs (> 100k)

### DON'T ❌

- Render all 100k nodes at once without pagination
- Keep edges visible during pan (FPS drop)
- Use rich HTML nodes in WebGL mode
- Disable camera controls (confusing UX)
- Force quality mode on large graphs

---

## Migration from Basic Version

```diff
- import { HybridGraphView } from '@/components/graph';
+ import { HybridGraphViewEnhanced } from '@/components/graph';

  <HybridGraphView
    nodes={nodes}
    edges={edges}
+   config={{ nodeThreshold: 10_000 }}
  />
```

**Benefits:**
- 2-5x faster rendering
- Smooth transitions
- Better LOD system
- Performance monitoring
- Automatic optimization

---

## Related Documentation

- [Complete Implementation Report](../reports/TASK_103_SIGMA_WEBGL_INTEGRATION_COMPLETE.md)
- [Performance Benchmarks](../reports/TASK_103_SIGMA_WEBGL_INTEGRATION_COMPLETE.md#performance-results)
- [Architecture Decisions](../reports/TASK_103_SIGMA_WEBGL_INTEGRATION_COMPLETE.md#architecture-decisions)

---

**Last Updated**: February 1, 2026
**Version**: 1.0.0
**Status**: Production Ready
