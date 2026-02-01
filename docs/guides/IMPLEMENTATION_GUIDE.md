# Canvas Graph Rendering - Implementation Guide

**Quick Reference for Development Team**

---

## Quick Start: Getting Started in 1 Hour

### 1. Choose Your Path

**Option A: Cytoscape WebGL (Recommended)**
```bash
# Install preview version
bun add cytoscape@3.31.0-pre

# Existing code works with renderer swap
cytoscape({
  renderer: { name: 'webgl' } // Change from 'canvas'
})
```

**Option B: Custom Canvas + Pixi.js**
```bash
bun add pixi.js
bun add -d @types/pixi.js
```

### 2. Minimal Culling Implementation (10 minutes)

```typescript
// viewport-culler.ts
export class SimpleViewportCuller {
  constructor(private edges: Edge[], private nodes: Node[]) {}

  getVisible(viewport: Viewport) {
    const visible = {
      nodes: this.nodes.filter(n => this.nodeInViewport(n, viewport)),
      edges: [] as Edge[]
    };

    const nodeIds = new Set(visible.nodes.map(n => n.id));
    visible.edges = this.edges.filter(e =>
      nodeIds.has(e.source) || nodeIds.has(e.target)
    );

    return visible;
  }

  private nodeInViewport(node: Node, v: Viewport) {
    return node.x >= v.x && node.x <= v.x + v.w &&
           node.y >= v.y && node.y <= v.y + v.h;
  }
}
```

### 3. Integrate with Current Cytoscape (20 minutes)

```typescript
// graph-view.tsx
const culler = new SimpleViewportCuller(edges, nodes);

cyRef.current.on('pan zoom', () => {
  const viewport = {
    x: -cyRef.current.pan().x / cyRef.current.zoom(),
    y: -cyRef.current.pan().y / cyRef.current.zoom(),
    w: cyRef.current.width() / cyRef.current.zoom(),
    h: cyRef.current.height() / cyRef.current.zoom(),
  };

  const { nodes: visibleNodes, edges: visibleEdges } = culler.getVisible(viewport);
  console.log(`Visible: ${visibleNodes.length}/${nodes.length}`);
});
```

**Result: 40-60% edge reduction with zero API changes**

---

## Common Tasks & Solutions

### Task 1: Add Basic Viewport Culling

**Time: 30 minutes**
**Impact: 40-60% edge reduction**

```typescript
// Add to existing Cytoscape component
const viewport = calculateViewport(cy);
const culledEdges = edges.filter(e => {
  const s = getNodePosition(e.source);
  const t = getNodePosition(e.target);

  return edgeVisible(s, t, viewport);
});

function edgeVisible(source, target, viewport) {
  // Edge visible if either endpoint is or edge crosses viewport
  return pointInViewport(source, viewport) ||
         pointInViewport(target, viewport) ||
         lineIntersectsViewport(source, target, viewport);
}
```

### Task 2: Switch to Cytoscape WebGL (When Available)

**Time: 15 minutes**
**Impact: 5x improvement**

```diff
  cytoscape({
    container: containerRef.current,
    elements: [...nodes, ...edges],
-   renderer: { name: 'canvas' },
+   renderer: { name: 'webgl' }, // Available in v3.31+
  });
```

### Task 3: Implement Spatial Index (R-Tree)

**Time: 4 hours**
**Impact: 30-50% memory savings**

Use existing library instead of building:

```bash
bun add rbush
```

```typescript
import RBush from 'rbush';

const rtree = new RBush();

// Insert nodes
for (const node of nodes) {
  rtree.insert({
    minX: node.x - node.width/2,
    minY: node.y - node.height/2,
    maxX: node.x + node.width/2,
    maxY: node.y + node.height/2,
    data: node,
  });
}

// Query viewport
const visible = rtree.search({
  minX: viewport.x,
  minY: viewport.y,
  maxX: viewport.x + viewport.width,
  maxY: viewport.y + viewport.height,
});
```

### Task 4: Add Edge Clustering at Low Zoom

**Time: 2 hours**
**Impact: Better visuals at zoom < 0.5**

```typescript
function clusterEdges(edges: Edge[], zoomLevel: number) {
  if (zoomLevel > 0.5) return edges; // No clustering

  const clusters = new Map<string, Edge[]>();

  for (const edge of edges) {
    const key = `${edge.source}-${edge.target}`;
    if (!clusters.has(key)) clusters.set(key, []);
    clusters.get(key)!.push(edge);
  }

  return Array.from(clusters.entries()).map(([key, group]) => {
    if (group.length > 1) {
      return {
        ...group[0],
        isCluster: true,
        count: group.length,
        opacity: Math.min(1, 0.3 * Math.log(group.length)),
      };
    }
    return group[0];
  });
}
```

### Task 5: Setup Performance Monitoring

**Time: 1 hour**
**Impact: Data-driven optimization**

```typescript
class PerformanceMonitor {
  private metrics = {
    frameCount: 0,
    fps: 0,
    lastTime: performance.now(),
  };

  tick() {
    this.metrics.frameCount++;
    const now = performance.now();
    const elapsed = now - this.metrics.lastTime;

    if (elapsed >= 1000) {
      this.metrics.fps = this.metrics.frameCount;
      this.metrics.frameCount = 0;
      this.metrics.lastTime = now;

      console.log(`FPS: ${this.metrics.fps}, Memory: ${(performance.memory?.usedJSHeapSize || 0) / 1e6}MB`);
    }
  }

  getMetrics() {
    return {
      fps: this.metrics.fps,
      memory: performance.memory?.usedJSHeapSize || 0,
    };
  }
}

// In render loop
const monitor = new PerformanceMonitor();
requestAnimationFrame(() => monitor.tick());
```

---

## Decision Tree: Which Optimization to Add First

```
Is your graph > 50k edges?
├─ NO → Try viewport culling first (40-60% improvement)
│   └─ Still too slow? → Add spatial indexing
│       └─ Still too slow? → Switch to WebGL
│
└─ YES → Switch to WebGL immediately
    └─ Still not smooth? → Add viewport culling + spatial indexing
        └─ Still rough at extreme zoom? → Add LOD system
```

---

## Performance Benchmarking Guide

### Setup: Create Test Graphs

```typescript
// test-graphs.ts
export function generateTestGraph(edgeCount: number) {
  const nodeCount = Math.sqrt(edgeCount) * 2;
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  // Create nodes in grid
  const gridSize = Math.ceil(Math.sqrt(nodeCount));
  for (let i = 0; i < nodeCount; i++) {
    nodes.push({
      id: `node_${i}`,
      x: (i % gridSize) * 200,
      y: Math.floor(i / gridSize) * 200,
      size: 10,
    });
  }

  // Create random edges
  for (let i = 0; i < edgeCount; i++) {
    const source = Math.floor(Math.random() * nodeCount);
    const target = Math.floor(Math.random() * nodeCount);

    edges.push({
      id: `edge_${i}`,
      source: `node_${source}`,
      target: `node_${target}`,
      color: '#ccc',
    });
  }

  return { nodes, edges };
}
```

### Run Benchmarks

```typescript
// benchmark.ts
async function benchmark(graphSize: number) {
  const { nodes, edges } = generateTestGraph(graphSize);

  // Warm-up
  render(<GraphVisualization nodes={nodes} edges={edges} />);
  await sleep(1000);

  // Measure
  const metrics = {
    renderTime: 0,
    fps: 0,
    memory: 0,
  };

  performance.mark('render-start');
  render(<GraphVisualization nodes={nodes} edges={edges} />);
  performance.mark('render-end');

  metrics.renderTime = performance.measure('render-start', 'render-end').duration;
  metrics.memory = performance.memory?.usedJSHeapSize || 0;
  metrics.fps = await measureFPS();

  return metrics;
}

async function measureFPS(duration = 5000) {
  let frameCount = 0;
  const startTime = performance.now();

  return new Promise<number>(resolve => {
    const measureFrame = () => {
      frameCount++;
      const elapsed = performance.now() - startTime;

      if (elapsed < duration) {
        requestAnimationFrame(measureFrame);
      } else {
        resolve(frameCount / (duration / 1000));
      }
    };

    requestAnimationFrame(measureFrame);
  });
}

// Run tests
for (const size of [10000, 50000, 100000]) {
  const result = await benchmark(size);
  console.table({
    'Edge Count': size,
    'Render Time (ms)': result.renderTime.toFixed(2),
    'FPS': result.fps.toFixed(1),
    'Memory (MB)': (result.memory / 1e6).toFixed(0),
  });
}
```

**Expected Output with Optimizations:**

```
Edge Count│Render Time (ms)│FPS  │Memory (MB)
-----------|-----------------|-----|----------
10000      │16.2             │60   │80
50000      │18.5             │58   │150
100000     │19.1             │52   │280
```

---

## Debugging Common Issues

### Problem: Graph Rendering All Edges

**Check:**
1. Viewport culling enabled?
2. Spatial index properly configured?
3. Edge visibility calculation correct?

**Debug:**
```typescript
const visible = culler.getVisible(viewport);
console.log(`Visible edges: ${visible.edges.length}/${edges.length} = ${(visible.edges.length/edges.length*100).toFixed(1)}%`);
```

**Expected:** > 60% culled at medium zoom

### Problem: Interaction Latency on Pan

**Check:**
1. Culling running on every pan event?
2. Spatial index queries optimized?
3. Render blocking user input?

**Debug:**
```typescript
performance.mark('pan-start');
updateViewport(newViewport);
performance.mark('pan-end');
console.log(`Pan update: ${performance.measure('pan-start', 'pan-end').duration.toFixed(2)}ms`);
```

**Expected:** < 5ms for viewport update

### Problem: Memory Continues Growing

**Check:**
1. Canvas still holding references to old edges?
2. Event listeners not cleaned up?
3. Spatial index not garbage collected?

**Debug:**
```typescript
// After pan/zoom cycle
console.log(`Memory: ${(performance.memory?.usedJSHeapSize || 0) / 1e6}MB`);
// Should be stable, not increasing

// Check for leaks
chrome devtools -> Memory -> Take heap snapshot
```

### Problem: WebGL Rendering Black/White

**Check:**
1. WebGL context lost?
2. Shaders compiled?
3. Viewport culling too aggressive?

**Debug:**
```typescript
const renderer = new PIXI.Renderer();
console.log(`WebGL: ${renderer.gl?.isContextLost() ? 'LOST' : 'OK'}`);
```

---

## Feature Flags for Safe Rollout

```typescript
// feature-flags.ts
export const featureFlags = {
  canvasRendering: useEnvFlag('CANVAS_RENDERING', false),
  viewportCulling: useEnvFlag('VIEWPORT_CULLING', true),
  spatialIndexing: useEnvFlag('SPATIAL_INDEXING', false),
  lodSystem: useEnvFlag('LOD_SYSTEM', false),
};

// Usage in component
export function GraphVisualization(props) {
  if (featureFlags.canvasRendering) {
    return <CanvasGraphVisualization {...props} />;
  }

  return <CytoscapeGraphVisualization {...props} />;
}

// Environment control
// .env.production
CANVAS_RENDERING=false      # Start disabled
VIEWPORT_CULLING=true       # Enabled by default
```

---

## Testing Checklist

- [ ] Viewport culling reduces edges 60-80%
- [ ] 50k edges run at 55+ FPS
- [ ] 100k edges run at 45+ FPS
- [ ] No memory leaks over 10 minute session
- [ ] Click/hover interactions < 16ms latency
- [ ] Pan smooth without stuttering
- [ ] Zoom smooth over 0.1x to 4x range
- [ ] Browser back/forward works correctly
- [ ] Mobile performance acceptable
- [ ] Accessibility features work (keyboard nav, etc.)

---

## Recommended Library Versions

```json
{
  "dependencies": {
    "cytoscape": "^3.31.0",
    "rbush": "^4.0.1",
    "pixi.js": "^8.0.0"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

---

## Sample Test File

```typescript
// graph-rendering.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { generateTestGraph } from './test-graphs';
import { ViewportCuller } from './viewport-culler';

describe('Graph Rendering Optimization', () => {
  let culler: ViewportCuller;

  beforeEach(() => {
    const { nodes, edges } = generateTestGraph(50000);
    culler = new ViewportCuller(edges, nodes);
  });

  it('should cull 70-90% of off-screen edges', () => {
    const viewport = {
      x: 0, y: 0, width: 500, height: 500,
      zoom: 1,
      padding: 100,
    };

    const visible = culler.getVisible(viewport);
    const culledPercentage = (1 - visible.edges.length / 50000) * 100;

    expect(culledPercentage).toBeGreaterThan(70);
    expect(culledPercentage).toBeLessThan(90);
  });

  it('should complete culling in < 5ms', () => {
    const viewport = {
      x: 0, y: 0, width: 1000, height: 1000,
      zoom: 1,
      padding: 200,
    };

    const start = performance.now();
    culler.getVisible(viewport);
    const duration = performance.now() - start;

    expect(duration).toBeLessThan(5);
  });

  it('should handle viewport edge cases', () => {
    // Empty viewport
    let visible = culler.getVisible({
      x: -10000, y: -10000, width: 100, height: 100,
      zoom: 1,
      padding: 50,
    });
    expect(visible.edges.length).toBe(0);

    // Full viewport
    visible = culler.getVisible({
      x: -1000, y: -1000, width: 10000, height: 10000,
      zoom: 1,
      padding: 5000,
    });
    expect(visible.edges.length).toBeGreaterThan(40000);
  });
});
```

---

## Performance Optimization Checklist

- [ ] **Week 1:** Establish baseline performance metrics
- [ ] **Week 2:** Implement viewport culling
- [ ] **Week 3:** Add spatial indexing (R-Tree)
- [ ] **Week 4:** Integrate WebGL rendering (if Cytoscape v3.31 available)
- [ ] **Week 5:** Implement LOD system
- [ ] **Week 6:** Add edge clustering
- [ ] **Week 7:** Optimize rendering pipeline
- [ ] **Week 8:** Performance testing at 100k edges
- [ ] **Week 9:** User acceptance testing
- [ ] **Week 10:** Gradual rollout with feature flags
- [ ] **Week 11:** Monitor production metrics
- [ ] **Week 12:** Retrospective and optimization

---

## Contacts & Resources

**Internal:**
- Performance Team: [slack:#performance]
- Frontend Lead: [frontend-lead@company]

**External:**
- Cytoscape.js Issues: https://github.com/cytoscape/cytoscape.js/issues
- Sigma.js Docs: https://www.sigmajs.org
- Pixi.js Community: https://discord.gg/pixijs

---

**Last Updated:** 2026-01-29
**Status:** READY FOR IMPLEMENTATION
**Next Review:** Upon v3.31 Cytoscape release or Week 1 milestone

