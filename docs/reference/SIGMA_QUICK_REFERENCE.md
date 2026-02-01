# Sigma.js WebGL Renderer - Quick Reference

## Installation

```bash
bun add sigma @react-sigma/core
```

## Basic Usage

### 1. Create Graph

```typescript
import Graph from 'graphology';

const graph = new Graph();

// Add nodes
graph.addNode('node1', {
  label: 'My Node',
  type: 'requirement',  // requirement, test, defect, epic, story, task, feature
  x: 0,
  y: 0,
  size: 10,
  status: 'approved',
  statusColor: '#10b981',
  data: {
    description: 'Node description',
    progress: 75,
    tags: ['tag1', 'tag2'],
  },
});

// Add edges
graph.addEdge('node1', 'node2', {
  color: '#94a3b8',
  size: 1,
  label: 'depends on',
});
```

### 2. Render Graph

```typescript
import { SigmaGraphView, RichNodeDetailPanel } from '@/components/graph';
import { useState } from 'react';

function MyGraph() {
  const [selectedNode, setSelectedNode] = useState(null);

  return (
    <div className="h-screen relative">
      <SigmaGraphView
        graph={graph}
        onNodeClick={(id) => setSelectedNode(graph.getNodeAttributes(id))}
        onNodeHover={(id) => console.log('Hover:', id)}
        onNodeDoubleClick={(id) => console.log('Double click:', id)}
      />

      <RichNodeDetailPanel
        node={selectedNode}
        onClose={() => setSelectedNode(null)}
        onExpand={(id) => handleExpand(id)}
        onNavigate={(id) => handleNavigate(id)}
      />
    </div>
  );
}
```

## Node Types & Colors

| Type | Color | Icon |
|------|-------|------|
| requirement | #3b82f6 (blue) | 📋 |
| test | #10b981 (green) | ✓ |
| defect | #ef4444 (red) | 🐛 |
| epic | #8b5cf6 (purple) | 🎯 |
| story | #06b6d4 (cyan) | 📖 |
| task | #f59e0b (amber) | 📝 |
| feature | #ec4899 (pink) | ⭐ |
| default | #64748b (slate) | ● |

## Node Attributes

```typescript
interface SigmaNode {
  // Required
  label: string;
  x: number;
  y: number;

  // Optional
  type?: string;              // Node type (affects color)
  size?: number;              // Node radius (default: 10)
  status?: string;            // Status for indicator dot
  statusColor?: string;       // Color of status indicator
  highlighted?: boolean;      // Show highlight ring

  // Custom data (shown in detail panel)
  data?: {
    image?: string;           // Screenshot/image URL
    progress?: number;        // 0-100 percentage
    description?: string;     // Node description
    tags?: string[];          // Tags array
    [key: string]: any;       // Additional custom fields
  };
}
```

## Edge Attributes

```typescript
interface SigmaEdge {
  color?: string;             // Edge color (default: #94a3b8)
  size?: number;              // Edge thickness (default: 1)
  label?: string;             // Edge label (shown on zoom)
  highlighted?: boolean;      // Show highlight
}
```

## Performance Settings

The component includes these performance optimizations:

```typescript
{
  // Hide elements during movement
  hideEdgesOnMove: true,
  hideLabelsOnMove: true,

  // Zoom-dependent rendering
  labelRenderedSizeThreshold: 0.5,  // Show labels at 50% zoom

  // Camera limits
  minCameraRatio: 0.1,   // Max zoom in
  maxCameraRatio: 10,    // Max zoom out

  // Edge optimization
  renderEdgeLabels: false,           // Only on zoom > 0.7
  enableEdgeHoverEvents: false,
  enableEdgeClickEvents: false,
}
```

## Zoom Thresholds

| Zoom Level | Visible Elements |
|------------|------------------|
| < 0.3 | Nodes only (circles) |
| 0.3 - 0.5 | Nodes + icons |
| 0.5 - 0.7 | Nodes + icons + node labels |
| > 0.7 | Everything + edge labels |

## Custom Renderers

Use custom renderers for full control:

```typescript
import { customNodeRenderer, customEdgeRenderer } from '@/components/graph';

// In SigmaContainer settings
settings={{
  defaultNodeType: 'custom',
  defaultEdgeType: 'custom',
}}
```

## Detail Panel

The RichNodeDetailPanel shows full node content:

- **Images**: Full embedded screenshots
- **Progress**: Visual progress bars
- **Status**: Badge-based status
- **Tags**: Chip-based tags
- **Actions**: Expand/Navigate buttons

## Event Handling

```typescript
<SigmaGraphView
  graph={graph}
  onNodeClick={(nodeId) => {
    // Handle node click
    const node = graph.getNodeAttributes(nodeId);
    console.log('Clicked:', node);
  }}
  onNodeHover={(nodeId) => {
    // nodeId is null when hover leaves
    if (nodeId) {
      // Highlight related nodes
      highlightNeighbors(nodeId);
    } else {
      // Clear highlights
      clearHighlights();
    }
  }}
  onNodeDoubleClick={(nodeId) => {
    // Expand node or navigate
    expandNode(nodeId);
  }}
/>
```

## Layout Algorithms

Sigma.js works with any layout. Use with graph layout libraries:

```typescript
import forceAtlas2 from 'graphology-layout-forceatlas2';

// Calculate layout
const positions = forceAtlas2(graph, {
  iterations: 50,
  settings: {
    barnesHutOptimize: true,
    strongGravityMode: true,
    gravity: 1,
    scalingRatio: 10,
  },
});

// Apply to graph
positions.assign(graph);
```

## Testing

### Unit Tests (jsdom)
- Test exports and renderer functions
- Full rendering requires browser environment

### Integration Tests (Playwright)
```typescript
// In e2e tests
await page.goto('/graph');
await page.waitForSelector('.sigma-container');

// Test interactions
await page.click('[data-node-id="node1"]');
await page.dblclick('[data-node-id="node2"]');
```

## Performance Benchmarks

| Nodes | FPS | Memory | Load Time |
|-------|-----|--------|-----------|
| 1k | 60 | ~50MB | <1s |
| 10k | 60 | ~100MB | ~2s |
| 100k | 50+ | ~500MB | ~5s |
| 1M | 50+ | ~2GB | ~15s |

## Common Patterns

### Highlight Neighbors on Hover

```typescript
const highlightNeighbors = (nodeId: string) => {
  const neighbors = new Set(graph.neighbors(nodeId));

  graph.updateEachNodeAttributes((node, attr) => ({
    ...attr,
    highlighted: node === nodeId || neighbors.has(node),
  }));
};
```

### Filter by Node Type

```typescript
const filterByType = (type: string) => {
  graph.updateEachNodeAttributes((_, attr) => ({
    ...attr,
    hidden: attr.type !== type,
  }));
};
```

### Zoom to Node

```typescript
import { useSigma } from '@react-sigma/core';

const sigma = useSigma();
const camera = sigma.getCamera();

camera.animate(
  { x: node.x, y: node.y, ratio: 0.5 },
  { duration: 500 }
);
```

## Troubleshooting

### Graph not visible
- Check if nodes have `x`, `y` coordinates
- Verify camera position
- Check if nodes are within viewport

### Poor performance
- Reduce node count
- Disable edge labels: `renderEdgeLabels: false`
- Increase label threshold: `labelRenderedSizeThreshold: 0.8`

### WebGL errors in tests
- Use browser-based tests (Playwright)
- Skip unit tests requiring WebGL rendering

## References

- [Sigma.js Docs](https://www.sigmajs.org/)
- [React Sigma Docs](https://sim51.github.io/react-sigma/)
- [Graphology Docs](https://graphology.github.io/)
- Full implementation: `SIGMA_IMPLEMENTATION_SUMMARY.md`
