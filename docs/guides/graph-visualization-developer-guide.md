# Graph Visualization Developer Guide

## Overview

This guide provides technical documentation for developers working with TraceRTM's hybrid graph visualization system. It covers architecture, extension points, customization, and advanced patterns.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Extending the System](#extending-the-system)
4. [Custom Renderers](#custom-renderers)
5. [Layout Algorithms](#layout-algorithms)
6. [Performance Optimization](#performance-optimization)
7. [Testing Strategies](#testing-strategies)
8. [Common Patterns](#common-patterns)
9. [Anti-Patterns](#anti-patterns)
10. [Debugging Guide](#debugging-guide)

---

## Architecture Overview

### Hybrid Architecture

TraceRTM uses a dual-rendering architecture that automatically switches between ReactFlow and Sigma.js based on node count:

```
┌─────────────────────────────────────────────────────────┐
│                   HybridGraphView                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Node Count Check (threshold: 10,000)              │  │
│  └───────────────┬───────────────────────────────────┘  │
│                  │                                       │
│         ┌────────┴────────┐                             │
│         │                 │                             │
│    < 10,000         ≥ 10,000                            │
│         │                 │                             │
│  ┌──────▼──────┐   ┌──────▼───────────┐                │
│  │  ReactFlow  │   │  Sigma.js WebGL  │                │
│  │  (Canvas)   │   │  (WebGL)         │                │
│  └─────────────┘   └──────────────────┘                │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Data → Graphology Adapter → Graph Structure
                                       ↓
                          ┌────────────┴────────────┐
                          │                         │
                   ReactFlow Nodes/Edges    Sigma.js Graph
                          │                         │
                          ▼                         ▼
                   FlowGraphViewInner        SigmaGraphView
                          │                         │
                          └────────────┬────────────┘
                                       ▼
                               User Interactions
```

### Key Layers

1. **Data Layer** (Graphology)
   - Graph data structure
   - Clustering algorithms (Louvain)
   - Layout algorithms (ForceAtlas2, Dagre, ELK, etc.)

2. **Rendering Layer** (ReactFlow/Sigma.js)
   - ReactFlow: Rich nodes, full interactions (<10k)
   - Sigma.js: GPU-accelerated, simplified rendering (≥10k)

3. **Spatial Indexing** (R-tree)
   - O(log n) viewport culling
   - 416x speedup over O(n) iteration

4. **LOD System** (Level of Detail)
   - Distance-based node simplification
   - Progressive enhancement

---

## Core Components

### 1. HybridGraphView

**Location:** `/frontend/apps/web/src/components/graph/HybridGraphView.tsx`

**Purpose:** Main component that orchestrates threshold switching

**Key Props:**
```typescript
interface HybridGraphViewProps {
  nodes: Node[];
  edges: Edge[];
  config?: HybridGraphConfig;
  onNodeClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null) => void;
  showPerformanceOverlay?: boolean;
  performanceVariant?: 'compact' | 'detailed';
}
```

**Usage:**
```tsx
import { HybridGraphView } from '@/components/graph/HybridGraphView';

function MyGraph() {
  const { nodes, edges } = useGraphData();

  return (
    <HybridGraphView
      nodes={nodes}
      edges={edges}
      config={{ nodeThreshold: 10000 }}
      onNodeClick={(id) => console.log('Clicked:', id)}
      showPerformanceOverlay={true}
    />
  );
}
```

### 2. GraphologyAdapter

**Location:** `/frontend/apps/web/src/lib/graphology/adapter.ts`

**Purpose:** Bidirectional sync between ReactFlow and Graphology

**Key Methods:**
```typescript
class GraphologyDataAdapter {
  syncFromReactFlow(nodes: Node[], edges: Edge[]): void;
  toReactFlow(): { nodes: Node[]; edges: Edge[] };
  getGraph(): Graph;
  async cluster(): Promise<Map<string, number>>;
  async computeLayout(iterations?: number): Promise<void>;
}
```

**Example:**
```typescript
import { createGraphologyAdapter } from '@/lib/graphology/adapter';

const adapter = createGraphologyAdapter();
adapter.syncFromReactFlow(nodes, edges);

// Compute layout
await adapter.computeLayout(500);

// Get clustered data
const communities = await adapter.cluster();
```

### 3. GraphClustering

**Location:** `/frontend/apps/web/src/lib/graphology/clustering.ts`

**Purpose:** Louvain community detection and cluster graph creation

**Key Methods:**
```typescript
class GraphClustering {
  detectCommunities(graph: Graph): Map<string, number>;
  createClusterGraph(
    graph: Graph,
    communities: Map<string, number>
  ): ClusteringResult;
  expandCluster(
    clusterId: string,
    clusterGraph: Graph,
    originalGraph: Graph
  ): void;
}
```

**Example:**
```typescript
import { GraphClustering } from '@/lib/graphology/clustering';

const clustering = new GraphClustering();
const communities = clustering.detectCommunities(graph);
const { nodes, edges } = clustering.createClusterGraph(graph, communities);

// Result: 99%+ edge reduction for massive graphs
```

### 4. SigmaGraphView

**Location:** `/frontend/apps/web/src/components/graph/SigmaGraphView.tsx`

**Purpose:** WebGL rendering for 100k+ nodes

**Key Props:**
```typescript
interface SigmaGraphViewProps {
  graph: Graph;
  onNodeClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null) => void;
  selectedNodeId?: string | null;
  customNodeRenderer?: NodeDisplayData => void;
  customEdgeRenderer?: EdgeDisplayData => void;
}
```

### 5. R-tree Spatial Index

**Location:** `/frontend/apps/web/src/lib/spatialIndex.ts`

**Purpose:** O(log n) viewport culling

**Key Methods:**
```typescript
class GraphSpatialIndex {
  indexNodes(nodes: Array<{ id: string; position: Position }>): void;
  indexEdges(
    edges: Array<{ id: string; sourceId: string; targetId: string }>,
    nodePositions: Map<string, Position>
  ): void;
  queryViewport(viewport: ViewportBounds): {
    nodes: SpatialNode[];
    edges: SpatialEdge[];
  };
}
```

---

## Extending the System

### Adding a New Node Type

**1. Create Component:**

```tsx
// /frontend/apps/web/src/components/graph/MyCustomNode.tsx
import { memo } from 'react';
import type { NodeProps } from '@xyflow/react';

interface MyCustomNodeData {
  id: string;
  label: string;
  customField: string;
}

export const MyCustomNode = memo(function MyCustomNode({
  data
}: NodeProps<MyCustomNodeData>) {
  return (
    <div className="px-4 py-3 rounded-lg border bg-card">
      <div className="font-medium">{data.label}</div>
      <div className="text-sm text-muted-foreground">
        {data.customField}
      </div>
    </div>
  );
});
```

**2. Register in nodeRegistry:**

```typescript
// /frontend/apps/web/src/components/graph/nodeRegistry.ts
import { MyCustomNode } from './MyCustomNode';

export const nodeTypes = {
  myCustom: MyCustomNode,
  // ... existing types
};
```

**3. Use in graph:**

```typescript
const nodes = [
  {
    id: '1',
    type: 'myCustom', // Use your custom type
    position: { x: 0, y: 0 },
    data: {
      label: 'Custom Node',
      customField: 'My data',
    },
  },
];
```

### Adding LOD Variant

**For LOD-aware rendering:**

```typescript
// Update getNodeType in nodeRegistry.ts
export function getNodeType(itemType: string, context: NodeTypeContext): string {
  if (context.loadingState) return 'skeleton';
  if (context.isSelected || context.isFocused) return itemType;

  const { totalNodeCount, zoom, distance = 0 } = context;

  // Add your custom LOD logic
  if (itemType === 'myCustom') {
    if (totalNodeCount > 5000 || zoom < 0.5 || distance > 800) {
      return 'myCustomSimple'; // Your simple variant
    }
  }

  // ... rest of LOD logic
}
```

### Adding a New Layout Algorithm

**1. Create Layout Worker Function:**

```typescript
// /frontend/apps/web/src/workers/layoutWorker.ts
import { MyCustomLayout } from 'my-layout-library';

export async function computeMyCustomLayout(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  config: MyLayoutConfig
): Promise<LayoutNode[]> {
  const layout = new MyCustomLayout(config);

  // Build graph
  nodes.forEach(node => layout.addNode(node.id, node));
  edges.forEach(edge => layout.addEdge(edge.source, edge.target));

  // Compute
  await layout.run();

  // Extract positions
  return nodes.map(node => ({
    ...node,
    x: layout.getNodePosition(node.id).x,
    y: layout.getNodePosition(node.id).y,
  }));
}
```

**2. Register in LayoutSelector:**

```tsx
// /frontend/apps/web/src/components/graph/layouts/LayoutSelector.tsx
const LAYOUT_OPTIONS = [
  { value: 'myCustom', label: 'My Custom Layout' },
  // ... existing options
];
```

**3. Handle in useLayoutWorker:**

```typescript
// /frontend/apps/web/src/hooks/useLayoutWorker.ts
export function useLayoutWorker() {
  const computeLayout = async (algorithm: string, nodes, edges, config) => {
    switch (algorithm) {
      case 'myCustom':
        return await worker.computeMyCustomLayout(nodes, edges, config);
      // ... other cases
    }
  };
}
```

---

## Custom Renderers

### Custom Sigma.js Node Renderer

**Location:** `/frontend/apps/web/src/components/graph/sigma/customRenderers.ts`

**Example - Hexagon Nodes:**

```typescript
export function hexagonNodeRenderer(
  context: CanvasRenderingContext2D,
  data: NodeDisplayData,
  settings: any
): void {
  const { x, y, size, color } = data;

  // Draw hexagon
  context.beginPath();
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i;
    const px = x + size * Math.cos(angle);
    const py = y + size * Math.sin(angle);

    if (i === 0) {
      context.moveTo(px, py);
    } else {
      context.lineTo(px, py);
    }
  }
  context.closePath();

  context.fillStyle = color + '40';
  context.fill();
  context.strokeStyle = color;
  context.lineWidth = 2;
  context.stroke();
}
```

**Usage:**

```tsx
<SigmaGraphView
  graph={graph}
  customNodeRenderer={hexagonNodeRenderer}
/>
```

### Custom Edge Renderer

**Example - Dashed Edges:**

```typescript
export function dashedEdgeRenderer(
  context: CanvasRenderingContext2D,
  data: EdgeDisplayData,
  settings: any
): void {
  const { x1, y1, x2, y2, color, size } = data;

  context.beginPath();
  context.moveTo(x1, y1);
  context.lineTo(x2, y2);
  context.strokeStyle = color || '#94a3b8';
  context.lineWidth = size || 1;
  context.setLineDash([5, 5]); // Dashed pattern
  context.stroke();
  context.setLineDash([]); // Reset
}
```

---

## Layout Algorithms

### Available Algorithms

| Algorithm | Best For | Performance | Direction |
|-----------|----------|-------------|-----------|
| **Dagre** | Hierarchical DAGs | <1s @ 5k nodes | TB, LR, BT, RL |
| **ELK** | Complex hierarchies | 2-3s @ 5k nodes | TB, LR, BT, RL |
| **D3-Force** | Organic layouts | 5-10s @ 5k nodes | N/A (physics) |
| **Grid** | Structured data | <0.5s @ 10k nodes | TB, LR |
| **Circular** | Cycle visualization | <0.5s @ 10k nodes | N/A |
| **Radial** | Tree structures | <1s @ 5k nodes | N/A |

### Algorithm Selection Guide

**Use Dagre when:**
- Graph has clear hierarchy (requirements → tests)
- Need fast layout computation
- Direction matters (top-down, left-right)

**Use ELK when:**
- Complex nested hierarchies
- Multiple connected components
- Need advanced routing (orthogonal edges)

**Use D3-Force when:**
- No clear hierarchy
- Want organic, clustered appearance
- Can afford longer computation time

**Use Grid when:**
- Presenting tabular data
- Need perfect alignment
- Maximum performance required

### Custom Layout Configuration

**Dagre Example:**

```typescript
<HybridGraphView
  layoutAlgorithm="dagre"
  layoutConfig={{
    rankdir: 'LR',        // Left-to-right
    nodesep: 100,         // Horizontal spacing
    ranksep: 150,         // Vertical spacing
    align: 'UL',          // Upper-left alignment
  }}
/>
```

**ELK Example:**

```typescript
<HybridGraphView
  layoutAlgorithm="elk"
  layoutConfig={{
    'elk.direction': 'RIGHT',
    'elk.layered.spacing.nodeNodeBetweenLayers': 100,
    'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
  }}
/>
```

**D3-Force Example:**

```typescript
<HybridGraphView
  layoutAlgorithm="d3-force"
  layoutConfig={{
    strength: -300,       // Repulsion strength
    distance: 100,        // Link distance
    iterations: 500,      // Simulation steps
  }}
/>
```

---

## Performance Optimization

### 1. Viewport Culling Optimization

**Problem:** Rendering all nodes/edges even when off-screen

**Solution:** R-tree spatial indexing

```typescript
import { GraphSpatialIndex } from '@/lib/spatialIndex';

const spatialIndex = new GraphSpatialIndex();
spatialIndex.indexNodes(nodes);
spatialIndex.indexEdges(edges, nodePositions);

const visible = spatialIndex.queryViewport({
  x: viewport.x,
  y: viewport.y,
  width: window.innerWidth,
  height: window.innerHeight,
  zoom: viewport.zoom,
});

// visible.nodes and visible.edges contain only visible elements
```

**Impact:** 416x speedup (O(n) → O(log n))

### 2. LOD Optimization

**Problem:** Rich nodes with images/buttons slow at high counts

**Solution:** Progressive simplification

```typescript
function getNodeType(itemType: string, context: NodeTypeContext): string {
  const { totalNodeCount, zoom, distance, isSelected } = context;

  // Always render selected with full detail
  if (isSelected) return itemType;

  // Aggressive simplification at scale
  if (totalNodeCount > 5000 || zoom < 0.5 || distance > 800) {
    return 'simple'; // Minimal pill
  }

  // Medium detail
  if (totalNodeCount > 2000 || zoom < 0.8 || distance > 400) {
    return 'medium'; // Type indicator + label
  }

  // Full detail
  return itemType;
}
```

**Impact:** 70-85% DOM reduction, 60 FPS at 5000+ nodes

### 3. Edge LOD Optimization

**Problem:** Bezier edges with labels expensive at scale

**Solution:** Distance-based simplification

```typescript
import { getEdgeLODTier } from '@/lib/edgeLOD';

const lodTier = getEdgeLODTier(edgeMidpoint, viewportCenter, zoom);

const edgeStyle = {
  strokeWidth: lodTier.strokeWidth,  // 2 → 1.5 → 1 → 0
  opacity: lodTier.opacity,          // 1.0 → 0.8 → 0.5 → 0
  type: lodTier.pathType === 'bezier' ? 'smoothstep' : 'default',
  label: lodTier.showLabel ? edge.label : undefined,
};
```

**Impact:** 60%+ edge rendering time reduction

### 4. Clustering for Massive Graphs

**Problem:** 100k+ nodes overwhelm any rendering system

**Solution:** Louvain clustering

```typescript
import { GraphClustering } from '@/lib/graphology/clustering';

const clustering = new GraphClustering();
const communities = clustering.detectCommunities(graph);
const { nodes, edges } = clustering.createClusterGraph(graph, communities);

// nodes: ~100 clusters instead of 100,000 nodes
// edges: <100 inter-cluster edges instead of 200,000+ edges
```

**Impact:** 99.99% reduction (1M edges → <100 visible)

### 5. Web Worker Offloading

**Problem:** Layout computation freezes UI

**Solution:** Off-main-thread computation

```typescript
import { useLayoutWorker } from '@/hooks/useLayoutWorker';

const { computeLayout, isReady } = useLayoutWorker();

const laidOutNodes = await computeLayout(nodes, edges, 'dagre');
// UI remains responsive at 60 FPS during computation
```

**Impact:** Zero UI blocking, 5000+ node layouts in background

### 6. Memoization Strategy

**Critical memoizations:**

```typescript
// Node data transformation
const nodesForLayout = useMemo(() => {
  return visibleNodes.map(node => transformNode(node));
}, [visibleNodes]);

// Edge style caching
const edgeStyleCache = useMemo(() => {
  return new Map(LINK_STYLES.entries());
}, []); // Never re-create

// Spatial index update
useEffect(() => {
  spatialIndex.indexNodes(dagreLaidoutNodes);
}, [dagreLaidoutNodes]); // Only on layout change
```

### 7. Threshold Tuning

**Default:** 10,000 node threshold for WebGL

**Adjust based on:**
- Hardware (lower for mobile, higher for desktop)
- Node complexity (rich nodes → lower threshold)
- User preference

```typescript
<HybridGraphView
  config={{
    nodeThreshold: 8000, // More aggressive WebGL switch
    // or
    nodeThreshold: 15000, // Keep ReactFlow longer
  }}
/>
```

---

## Testing Strategies

### 1. Unit Tests

**Test LOD logic:**

```typescript
import { getNodeType } from '@/components/graph/nodeRegistry';

describe('LOD System', () => {
  it('should use SimplePill for high count', () => {
    const type = getNodeType('requirement', {
      totalNodeCount: 6000,
      zoom: 1.0,
      isSelected: false,
      isFocused: false,
      distance: 0,
    });

    expect(type).toBe('simple');
  });

  it('should always use full detail for selected', () => {
    const type = getNodeType('requirement', {
      totalNodeCount: 10000,
      zoom: 0.3,
      isSelected: true,
      isFocused: false,
      distance: 1000,
    });

    expect(type).toBe('requirement'); // Full detail
  });
});
```

**Test spatial indexing:**

```typescript
import { GraphSpatialIndex } from '@/lib/spatialIndex';

describe('GraphSpatialIndex', () => {
  it('should query viewport efficiently', () => {
    const index = new GraphSpatialIndex();
    const nodes = Array.from({ length: 10000 }, (_, i) => ({
      id: `node-${i}`,
      position: { x: Math.random() * 10000, y: Math.random() * 10000 },
    }));

    index.indexNodes(nodes);

    const start = performance.now();
    const result = index.queryViewport({
      x: 0, y: 0, width: 1000, height: 1000, zoom: 1,
    });
    const duration = performance.now() - start;

    expect(duration).toBeLessThan(10); // <10ms for 10k nodes
    expect(result.nodes.length).toBeGreaterThan(0);
    expect(result.nodes.length).toBeLessThan(nodes.length);
  });
});
```

### 2. Integration Tests

**Test hybrid switching:**

```typescript
import { render } from '@testing-library/react';
import { HybridGraphView } from '@/components/graph/HybridGraphView';

describe('HybridGraphView', () => {
  it('should use ReactFlow for <10k nodes', () => {
    const nodes = generateNodes(5000);
    const { container } = render(<HybridGraphView nodes={nodes} edges={[]} />);

    expect(container.querySelector('.react-flow')).toBeInTheDocument();
    expect(container.querySelector('.sigma-container')).not.toBeInTheDocument();
  });

  it('should use Sigma.js for ≥10k nodes', () => {
    const nodes = generateNodes(15000);
    const { container } = render(<HybridGraphView nodes={nodes} edges={[]} />);

    expect(container.querySelector('.sigma-container')).toBeInTheDocument();
    expect(container.querySelector('.react-flow')).not.toBeInTheDocument();
  });
});
```

### 3. Performance Tests

**Benchmark FPS:**

```typescript
import { measureFPS } from '@/lib/test-utils/performance';

describe('Performance Benchmarks', () => {
  it('should maintain 60 FPS at 10k nodes', async () => {
    const nodes = generateNodes(10000);
    const { container } = render(<HybridGraphView nodes={nodes} edges={[]} />);

    const fps = await measureFPS(container, {
      duration: 5000,
      interactions: ['pan', 'zoom'],
    });

    expect(fps).toBeGreaterThanOrEqual(60);
  });
});
```

### 4. E2E Tests

**Test real workflows:**

```typescript
import { test, expect } from '@playwright/test';

test('graph exploration workflow', async ({ page }) => {
  await page.goto('/projects/test-project/graph');

  // Initial load
  await expect(page.locator('.react-flow')).toBeVisible();

  // Click node
  await page.locator('[data-node-id="node-1"]').click();

  // Verify detail panel
  await expect(page.locator('[data-testid="node-detail-panel"]')).toBeVisible();

  // Pan to load more
  await page.mouse.move(500, 500);
  await page.mouse.down();
  await page.mouse.move(200, 200);
  await page.mouse.up();

  // Verify new nodes loaded
  const nodeCount = await page.locator('[data-node-id]').count();
  expect(nodeCount).toBeGreaterThan(200);
});
```

---

## Common Patterns

### Pattern 1: Lazy Loading with Skeleton States

```typescript
function GraphWithLoading() {
  const { data, isLoading } = useGraphData();

  if (isLoading) {
    return (
      <HybridGraphView
        nodes={skeletonNodes}
        edges={[]}
        config={{ forceReactFlow: true }}
      />
    );
  }

  return <HybridGraphView nodes={data.nodes} edges={data.edges} />;
}
```

### Pattern 2: Incremental Viewport Loading

```typescript
function IncrementalGraph() {
  const { loadViewport, nodes, edges } = useViewportGraph(projectId);
  const viewport = useReactFlow().getViewport();

  useEffect(() => {
    loadViewport({
      minX: viewport.x,
      minY: viewport.y,
      maxX: viewport.x + window.innerWidth / viewport.zoom,
      maxY: viewport.y + window.innerHeight / viewport.zoom,
      zoom: viewport.zoom,
    });
  }, [viewport, loadViewport]);

  return <HybridGraphView nodes={nodes} edges={edges} />;
}
```

### Pattern 3: Predictive Prefetching

```typescript
function PrefetchingGraph() {
  const { loadViewport, nodes, edges } = useViewportGraph(projectId);
  const viewport = useReactFlow().getViewport();

  usePredictivePrefetch(viewport, loadViewport);

  return <HybridGraphView nodes={nodes} edges={edges} />;
}
```

### Pattern 4: Cluster Drill-Down

```typescript
function ClusteredGraph() {
  const [expandedClusters, setExpandedClusters] = useState<Set<string>>(new Set());

  const handleClusterClick = async (clusterId: string) => {
    if (expandedClusters.has(clusterId)) {
      // Collapse
      setExpandedClusters(prev => {
        const next = new Set(prev);
        next.delete(clusterId);
        return next;
      });
    } else {
      // Expand
      const members = await fetchClusterMembers(clusterId);
      setExpandedClusters(prev => new Set(prev).add(clusterId));
      // Replace cluster node with member nodes
    }
  };

  return (
    <HybridGraphView
      nodes={nodes}
      edges={edges}
      onNodeClick={handleClusterClick}
    />
  );
}
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Reading All Nodes Upfront

**Bad:**
```typescript
// Loads entire 100k node graph into memory
const allNodes = await fetchAllNodes(projectId);
```

**Good:**
```typescript
// Load incrementally by viewport
const { nodes } = useViewportGraph(projectId);
```

### ❌ Anti-Pattern 2: No Memoization

**Bad:**
```typescript
function MyGraph() {
  const transformedNodes = nodes.map(n => transform(n)); // Re-runs every render

  return <HybridGraphView nodes={transformedNodes} edges={edges} />;
}
```

**Good:**
```typescript
function MyGraph() {
  const transformedNodes = useMemo(
    () => nodes.map(n => transform(n)),
    [nodes]
  );

  return <HybridGraphView nodes={transformedNodes} edges={edges} />;
}
```

### ❌ Anti-Pattern 3: Ignoring LOD

**Bad:**
```typescript
// Always render rich nodes, even at scale
<HybridGraphView
  nodes={nodes.map(n => ({ ...n, type: 'richNodePill' }))}
  edges={edges}
/>
```

**Good:**
```typescript
// Let LOD system determine node type
const nodesWithLOD = useMemo(() => {
  return nodes.map(node => {
    const type = getNodeType(node.type, {
      totalNodeCount: nodes.length,
      zoom: viewport.zoom,
      isSelected: selectedNodeId === node.id,
      distance: calculateDistance(node, viewportCenter),
    });
    return { ...node, type };
  });
}, [nodes, viewport, selectedNodeId]);
```

### ❌ Anti-Pattern 4: Synchronous Layout

**Bad:**
```typescript
// Blocks UI for 5+ seconds
const laidOutNodes = computeDagreLayout(nodes, edges);
```

**Good:**
```typescript
// Off-main-thread
const { computeLayout } = useLayoutWorker();
const laidOutNodes = await computeLayout(nodes, edges, 'dagre');
```

### ❌ Anti-Pattern 5: No Error Boundaries

**Bad:**
```typescript
// Entire app crashes if graph fails
<HybridGraphView nodes={nodes} edges={edges} />
```

**Good:**
```typescript
<ErrorBoundary fallback={<GraphErrorState />}>
  <HybridGraphView nodes={nodes} edges={edges} />
</ErrorBoundary>
```

---

## Debugging Guide

### Performance Issues

**Symptom:** Low FPS (<30 FPS)

**Debug steps:**

1. **Enable Performance Overlay:**
```tsx
<HybridGraphView showPerformanceOverlay={true} performanceVariant="detailed" />
```

2. **Check React DevTools Profiler:**
   - Look for expensive re-renders
   - Verify memoization working

3. **Check Chrome Performance Tab:**
   - Record 5 seconds of interaction
   - Look for long tasks (>50ms)
   - Check for layout thrashing

4. **Verify LOD Active:**
```typescript
console.log('LOD stats:', {
  total: nodes.length,
  simple: nodes.filter(n => n.type === 'simple').length,
  medium: nodes.filter(n => n.type === 'medium').length,
  rich: nodes.filter(n => n.type !== 'simple' && n.type !== 'medium').length,
});
```

### Memory Issues

**Symptom:** Browser crashes, >1GB memory

**Debug steps:**

1. **Check Memory Profiler:**
   - Take heap snapshot
   - Look for detached DOM nodes
   - Check for memory leaks in listeners

2. **Verify Spatial Index Cleanup:**
```typescript
useEffect(() => {
  spatialIndex.indexNodes(nodes);

  return () => {
    spatialIndex.clear(); // Cleanup
  };
}, [nodes]);
```

3. **Enable Clustering:**
```typescript
// Reduce node count by 99%+
const { nodes, edges } = useGraphClustering(originalNodes, originalEdges);
```

### WebGL Not Activating

**Symptom:** ReactFlow still rendering at 15k+ nodes

**Debug steps:**

1. **Check config:**
```typescript
// Ensure forceReactFlow is false
<HybridGraphView config={{ forceReactFlow: false }} />
```

2. **Check browser console:**
```javascript
// Should see automatic switch message
"Graph exceeds 10,000 nodes (15,234). Switching to WebGL mode."
```

3. **Verify WebGL support:**
```javascript
const canvas = document.createElement('canvas');
const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
console.log('WebGL supported:', !!gl);
```

### Nodes Not Loading

**Symptom:** Empty viewport after panning

**Debug steps:**

1. **Check network tab:**
   - Verify `/api/v1/projects/{id}/graph/viewport` returning data
   - Check for 500 errors

2. **Verify viewport bounds:**
```typescript
console.log('Viewport query:', {
  minX: viewport.x,
  minY: viewport.y,
  maxX: viewport.x + window.innerWidth / viewport.zoom,
  maxY: viewport.y + window.innerHeight / viewport.zoom,
});
```

3. **Check loaded regions:**
```typescript
console.log('Loaded regions:', loadedRegions);
console.log('Current viewport region:', regionKey);
```

### Edge Flicker

**Symptom:** Edges randomly disappearing/reappearing

**Solution:** Verify deterministic edge IDs

```typescript
// Bad: Random IDs
edges.map(e => ({ ...e, id: Math.random().toString() }));

// Good: FNV-1a hash
import { hashEdgeId } from '@/lib/enhancedViewportCulling';
edges.map(e => ({ ...e, id: hashEdgeId(e.sourceId, e.targetId) }));
```

---

## Advanced Topics

### GPU Force-Directed Layout (Future)

**WebGPU Compute Shaders for Barnes-Hut:**

```typescript
// Conceptual - WebGPU not yet implemented
async function computeForceLayoutGPU(nodes: Node[], edges: Edge[]) {
  const device = await navigator.gpu.requestAdapter().requestDevice();

  // Compute shader for force calculation
  const computeShader = device.createShaderModule({
    code: `
      @compute @workgroup_size(256)
      fn main(@builtin(global_invocation_id) id: vec3<u32>) {
        let nodeId = id.x;
        // Barnes-Hut force calculation on GPU
        // ...
      }
    `,
  });

  // Run layout computation on GPU
  // ...
}
```

### Real-Time Collaboration

**WebSocket sync for collaborative graph editing:**

```typescript
function CollaborativeGraph() {
  const { nodes, edges } = useRealtimeGraph(projectId);

  return (
    <HybridGraphView
      nodes={nodes}
      edges={edges}
      onNodeMove={(nodeId, position) => {
        // Broadcast to other users
        socket.emit('node:move', { nodeId, position });
      }}
    />
  );
}
```

### Machine Learning Layout

**ML-learned layouts for common patterns:**

```typescript
async function computeMLLayout(nodes: Node[], edges: Edge[]) {
  const graphEmbedding = await embedGraph(nodes, edges);
  const predictions = await model.predict(graphEmbedding);

  return nodes.map((node, i) => ({
    ...node,
    position: { x: predictions[i][0], y: predictions[i][1] },
  }));
}
```

---

## Resources

### Internal Documentation
- [User Guide](/docs/guides/graph-visualization-user-guide.md)
- [API Reference](/docs/reference/graph-api-reference.md)
- [Performance Benchmarks](/docs/reports/performance-benchmarks.md)

### External Libraries
- [ReactFlow Documentation](https://reactflow.dev)
- [Sigma.js Documentation](https://www.sigmajs.org)
- [Graphology Documentation](https://graphology.github.io)
- [RBush (R-tree)](https://github.com/mourner/rbush)
- [Comlink (Web Workers)](https://github.com/GoogleChromeLabs/comlink)

### Research Papers
- Louvain Method: "Fast unfolding of communities in large networks" (Blondel et al., 2008)
- ForceAtlas2: "ForceAtlas2, a Continuous Graph Layout Algorithm" (Jacomy et al., 2014)
- R-tree: "R-trees: A Dynamic Index Structure for Spatial Searching" (Guttman, 1984)

---

## Contributing

When contributing to the graph visualization system:

1. **Follow LOD principles** - Progressive enhancement always
2. **Test at scale** - Verify 10k+ node performance
3. **Measure impact** - Use performance overlay
4. **Document patterns** - Update this guide
5. **Maintain backward compatibility** - Feature flags for breaking changes

**Happy coding! 🚀**
