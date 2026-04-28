# Cytoscape.js Quick Reference for TraceRTM

**Quick Links:**
- [Full Evaluation](/docs/research/cytoscape-js-evaluation.md)
- [Official Docs](https://js.cytoscape.org/)
- [Performance Test Page](https://cytoscape.org/js-perf/)

---

## Decision Matrix: Which Renderer?

```
Node Count     → Renderer              → Expected FPS  → Memory
─────────────────────────────────────────────────────────────────
0 - 5k         → ReactFlow             → 60 FPS        → <500MB
5k - 10k       → Cytoscape Canvas      → 30 FPS        → <1GB
10k - 30k      → Cytoscape Canvas      → 15-30 FPS     → <3GB
30k - 100k+    → Cytoscape WebGL       → 30+ FPS       → <6GB
```

## Installation

```bash
# Core libraries (already installed in TraceRTM)
bun add cytoscape@3.x.y react-cytoscapejs
bun add -d @types/cytoscape

# Layout extensions
bun add cytoscape-fcose cytoscape-dagre cytoscape-cola
```

## Basic React Component

```tsx
import CytoscapeComponent from 'react-cytoscapejs';
import Cytoscape from 'cytoscape';
import fcose from 'cytoscape-fcose';

Cytoscape.use(fcose);

function GraphView({ items, links }) {
  const elements = convertToElements(items, links);

  return (
    <CytoscapeComponent
      elements={elements}
      style={{ width: '100%', height: '600px' }}
      layout={{ name: 'fcose' }}
      stylesheet={[
        {
          selector: 'node',
          style: {
            'background-color': '#666',
            'label': 'data(label)',
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#ccc',
            'target-arrow-shape': 'triangle',
          }
        }
      ]}
    />
  );
}
```

## Data Conversion (ReactFlow → Cytoscape)

```typescript
function convertToElements(items: Item[], links: Link[]) {
  const nodes = items.map(item => ({
    data: {
      id: item.id,
      label: item.name,
      ...item.metadata,
    },
    position: { x: item.x || 0, y: item.y || 0 },
  }));

  const edges = links.map(link => ({
    data: {
      id: link.id,
      source: link.source_id,
      target: link.target_id,
      label: link.type,
    },
  }));

  return [...nodes, ...edges];
}
```

## Performance Optimization Checklist

```typescript
// Recommended configuration for large graphs
const optimizedConfig = {
  // Renderer settings
  pixelRatio: 1.0,              // ✅ 2x faster on retina
  hideEdgesOnViewport: true,    // ✅ Hide during pan/zoom
  textureOnViewport: true,      // ✅ Cache viewport
  hideLabelsOnViewport: true,   // ✅ Hide labels during interaction

  // WebGL renderer (for 30k+ nodes)
  renderer: {
    name: 'webgl',              // ✅ GPU acceleration
    textureSize: 2048,
    maxBatchSize: 1000,
  },

  // Styling (fastest options)
  stylesheet: [
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'min-zoomed-font-size': 12,  // ✅ Hide tiny labels
      }
    },
    {
      selector: 'edge',
      style: {
        'curve-style': 'haystack',   // ✅ Fastest edge type
        'opacity': 1.0,               // ✅ Opaque = 2x faster
      }
    }
  ]
};
```

## Layout Algorithm Selection

```typescript
function selectLayout(nodeCount: number, isDAG: boolean) {
  if (isDAG && nodeCount < 20000) {
    return { name: 'dagre' };        // Fast hierarchical
  }

  if (nodeCount < 1000) {
    return { name: 'fcose' };        // Best quality
  }

  if (nodeCount < 5000) {
    return { name: 'cose' };         // Balanced
  }

  // For large graphs: pre-calculate positions
  return { name: 'preset' };
}
```

## Common Patterns

### Batch Updates

```typescript
// ❌ Slow (multiple redraws)
items.forEach(item => {
  cy.getElementById(item.id).data('status', 'updated');
});

// ✅ Fast (single redraw)
cy.batch(() => {
  items.forEach(item => {
    cy.getElementById(item.id).data('status', 'updated');
  });
});
```

### Compound Nodes (Hierarchies)

```typescript
const elements = [
  // Parent
  { data: { id: 'epic-1', label: 'Epic' } },

  // Children
  { data: { id: 'story-1', label: 'Story', parent: 'epic-1' } },
  { data: { id: 'task-1', label: 'Task', parent: 'story-1' } },

  // Edges
  { data: { source: 'story-1', target: 'task-1' } },
];
```

### Access Cytoscape API

```tsx
function GraphWithAPI() {
  const cyRef = useRef<Cytoscape.Core>();

  return (
    <CytoscapeComponent
      cy={(cy) => {
        cyRef.current = cy;

        // Add event listeners
        cy.on('tap', 'node', (evt) => {
          const node = evt.target;
          console.log('Clicked:', node.id());
        });

        // Programmatic control
        cy.fit();
        cy.center();
      }}
    />
  );
}
```

## Performance Benchmarks (Reference)

**Canvas Renderer:**
```
1,200 nodes / 16,000 edges:  ~20 FPS
3,200 nodes / 68,000 edges:  ~3 FPS
```

**WebGL Renderer:**
```
1,200 nodes / 16,000 edges:  >100 FPS  (5x improvement)
3,200 nodes / 68,000 edges:  ~10 FPS   (3x improvement)
```

## Migration Effort Estimate

| Complexity | Duration | Scope |
|------------|----------|-------|
| **Low** | 1-2 days | Simple visualization, basic interactions |
| **Medium** | 3-5 days | Custom styling, filtering, multiple edge types |
| **High** | 1-2 weeks | Advanced features, compound nodes, 50k+ nodes |

**TraceRTM Estimate:** 1 week (medium-high complexity)

## When to Use Cytoscape vs ReactFlow

**Use ReactFlow if:**
- ✅ <10k nodes
- ✅ Need React component nodes
- ✅ Workflow/diagram editor
- ✅ Heavy customization needs

**Use Cytoscape.js if:**
- ✅ 10k-100k nodes
- ✅ Need graph algorithms
- ✅ Compound nodes (hierarchies)
- ✅ Advanced layouts
- ✅ Performance-critical

## Troubleshooting

**Problem:** Graph renders slowly on large datasets
**Solution:**
1. Enable WebGL renderer
2. Set `pixelRatio: 1.0`
3. Use `hideEdgesOnViewport: true`
4. Switch to `haystack` edge style

**Problem:** High memory usage
**Solution:**
1. Remove unused elements: `cy.elements().remove()`
2. Use batch operations
3. Implement progressive loading
4. Clear caches: `cy.reset()`

**Problem:** Layout takes too long
**Solution:**
1. Pre-calculate positions server-side
2. Use `preset` layout with positions
3. Switch from `fcose` to `dagre` for DAGs
4. Use `grid` as instant fallback

---

**See Full Documentation:** `/docs/research/cytoscape-js-evaluation.md`
