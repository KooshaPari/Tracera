# GraphologyDataLayer Quick Reference

## Installation

Already installed in the project:
```bash
graphology@^0.26.0
graphology-communities-louvain@^2.0.2
graphology-layout@^0.6.1
graphology-layout-forceatlas2@^0.10.1
graphology-metrics@^2.4.0
```

## Basic Usage

### Import
```typescript
import {
  createGraphologyDataLayer,
  getGraphologyDataLayer,
  resetGraphologyDataLayer,
} from '@/lib/graph';
```

### Create Instance
```typescript
// Create new instance
const dataLayer = createGraphologyDataLayer();

// Or use global singleton
const dataLayer = getGraphologyDataLayer();
```

### Initialize with Data
```typescript
import type { Node, Edge } from '@xyflow/react';

const nodes: Node[] = [...];
const edges: Edge[] = [...];

await dataLayer.initialize(nodes, edges);
```

## Core Operations

### Node Operations
```typescript
// Add node
dataLayer.addNode({
  id: 'node1',
  type: 'default',
  position: { x: 0, y: 0 },
  data: { label: 'My Node' },
});

// Update node
dataLayer.updateNode('node1', { color: '#ff0000' });

// Remove node
dataLayer.removeNode('node1');

// Get neighbors
const neighbors = dataLayer.getNeighbors('node1');

// Get degree
const degree = dataLayer.getNodeDegree('node1');
const inDegree = dataLayer.getNodeInDegree('node1');
const outDegree = dataLayer.getNodeOutDegree('node1');
```

### Edge Operations
```typescript
// Add edge
dataLayer.addEdge({
  id: 'edge1',
  source: 'node1',
  target: 'node2',
  type: 'default',
  data: { weight: 5 },
});

// Update edge
dataLayer.updateEdge('node1', 'node2', { weight: 10 });

// Remove edge
dataLayer.removeEdge('edge1');
```

## Layout Algorithms

### ForceAtlas2 (Recommended for large graphs)
```typescript
await dataLayer.computeLayout({
  algorithm: 'forceAtlas2',
  iterations: 500,
  settings: {
    gravity: 1,
    scalingRatio: 10,
    strongGravityMode: false,
    barnesHutOptimize: true,
    barnesHutTheta: 0.5,
  },
});
```

### Circular (Fast for any size)
```typescript
await dataLayer.computeLayout({
  algorithm: 'circular',
});
```

### Random (Testing/Debugging)
```typescript
await dataLayer.computeLayout({
  algorithm: 'random',
});
```

## Community Detection

```typescript
// Detect communities using Louvain
const communities = await dataLayer.detectCommunities();

// Get cached communities
const cached = dataLayer.getCommunities();

// Color nodes by community
communities.forEach((communityId, nodeId) => {
  const hue = (communityId * 137.5) % 360;
  dataLayer.updateNode(nodeId, {
    color: `hsl(${hue}, 70%, 60%)`,
  });
});
```

## Statistics

```typescript
const stats = dataLayer.getStats();

console.log({
  nodeCount: stats.nodeCount,
  edgeCount: stats.edgeCount,
  density: stats.density,
  diameter: stats.diameter,
  averageDegree: stats.averageDegree,
  communityCount: stats.communityCount,
});
```

## Performance Metrics

```typescript
const metrics = dataLayer.getPerformanceMetrics();

console.log({
  initializationTime: metrics.initializationTime,
  layoutTime: metrics.layoutTime,
  conversionTime: metrics.conversionTime,
  totalMemory: metrics.totalMemory,
  nodeCount: metrics.nodeCount,
  edgeCount: metrics.edgeCount,
});
```

## ReactFlow Integration

### Convert to ReactFlow
```typescript
const { nodes, edges } = dataLayer.toReactFlow();

<ReactFlow nodes={nodes} edges={edges} />
```

### Convert from ReactFlow
```typescript
const reactFlowNodes: Node[] = [...];
const reactFlowEdges: Edge[] = [...];

await dataLayer.initialize(reactFlowNodes, reactFlowEdges);
```

## Import/Export

### Export as JSON
```typescript
const json = dataLayer.exportJSON();
localStorage.setItem('graph', JSON.stringify(json));
```

### Import from JSON
```typescript
const json = JSON.parse(localStorage.getItem('graph'));
dataLayer.importJSON(json);
```

## Utilities

### Clear Graph
```typescript
dataLayer.clear();
```

### Reset Global Instance
```typescript
resetGraphologyDataLayer();
```

### Get Underlying Graphology Instance
```typescript
const graph = dataLayer.getGraph();

// Direct Graphology API access
graph.forEachNode((nodeId, attrs) => {
  console.log(nodeId, attrs);
});
```

## React Hook

### Custom Hook
```typescript
import { useGraphologyLayer } from '@/lib/graph/GraphologyDataLayer.example';

function MyComponent() {
  const {
    nodes,
    edges,
    loading,
    stats,
    initialize,
    computeLayout,
    detectCommunities,
    addNode,
    addEdge,
    clear,
  } = useGraphologyLayer();

  // Use in component
  return (
    <div>
      <button onClick={() => computeLayout({ algorithm: 'forceAtlas2' })}>
        Layout
      </button>
      <ReactFlow nodes={nodes} edges={edges} />
    </div>
  );
}
```

## Performance Tips

### For Large Graphs (10k+ nodes)
1. Use `circular` layout for initial positioning
2. Enable Barnes-Hut optimization for ForceAtlas2
3. Reduce iterations for faster computation
4. Use incremental updates instead of full reinitialization

### For Real-time Updates
1. Use `addNode` and `addEdge` for incremental changes
2. Avoid calling `toReactFlow()` on every update
3. Batch updates when possible

### Memory Management
1. Call `clear()` when switching graphs
2. Use `resetGraphologyDataLayer()` for full cleanup
3. Monitor `getPerformanceMetrics().totalMemory`

## Common Patterns

### Initialize and Layout
```typescript
async function setupGraph(nodes: Node[], edges: Edge[]) {
  const dataLayer = createGraphologyDataLayer();

  await dataLayer.initialize(nodes, edges);
  await dataLayer.computeLayout({
    algorithm: 'forceAtlas2',
    iterations: 500,
  });

  return dataLayer.toReactFlow();
}
```

### Community-based Coloring
```typescript
async function colorByCommunity(dataLayer: GraphologyDataLayer) {
  const communities = await dataLayer.detectCommunities();

  communities.forEach((communityId, nodeId) => {
    const hue = (communityId * 137.5) % 360;
    dataLayer.updateNode(nodeId, {
      color: `hsl(${hue}, 70%, 60%)`,
      community: communityId,
    });
  });

  return dataLayer.toReactFlow();
}
```

### Incremental Building
```typescript
const dataLayer = createGraphologyDataLayer();

// Start with empty graph
await dataLayer.initialize([], []);

// Add nodes incrementally
for (const node of newNodes) {
  dataLayer.addNode(node);
}

// Add edges incrementally
for (const edge of newEdges) {
  dataLayer.addEdge(edge);
}

// Compute layout once
await dataLayer.computeLayout({ algorithm: 'circular' });
```

## Error Handling

```typescript
try {
  await dataLayer.initialize(nodes, edges);
  await dataLayer.computeLayout({ algorithm: 'forceAtlas2' });
} catch (error) {
  console.error('Graph operation failed:', error);
  // Fallback to simple layout
  await dataLayer.computeLayout({ algorithm: 'circular' });
}
```

## Type Definitions

### Node Attributes
```typescript
interface GraphologyNodeData {
  id: string;
  label: string;
  type: string;
  x: number;
  y: number;
  size?: number;
  color?: string;
  [key: string]: any;
}
```

### Edge Attributes
```typescript
interface GraphologyEdgeData {
  id: string;
  label?: string;
  type?: string;
  weight?: number;
  color?: string;
  [key: string]: any;
}
```

### Layout Options
```typescript
interface LayoutOptions {
  algorithm?: 'forceAtlas2' | 'circular' | 'random';
  iterations?: number;
  settings?: {
    gravity?: number;
    scalingRatio?: number;
    strongGravityMode?: boolean;
    slowDown?: number;
    barnesHutOptimize?: boolean;
    barnesHutTheta?: number;
  };
}
```

## Performance Benchmarks

| Operation | 1k nodes | 10k nodes | 100k nodes |
|-----------|----------|-----------|------------|
| Initialize | ~50ms | ~880ms | ~8s |
| ForceAtlas2 | ~11ms | ~200ms | N/A* |
| Circular | ~1ms | ~5ms | ~8ms |
| Conversion | ~2ms | ~20ms | ~200ms |
| Communities | ~5ms | ~50ms | ~500ms |

*Use circular or reduce iterations for 100k+ nodes

## See Also

- Full examples: `frontend/apps/web/src/lib/graph/GraphologyDataLayer.example.tsx`
- Tests: `frontend/apps/web/src/lib/graph/__tests__/GraphologyDataLayer.test.ts`
- Benchmarks: `frontend/apps/web/src/lib/graph/__tests__/GraphologyDataLayer.benchmark.test.ts`
- Completion Report: `docs/reports/task-101-graphology-integration-complete.md`
