# ADR-0004: Graph Visualization Library

**Status:** Accepted
**Date:** 2026-01-30
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM v2 prioritizes graph-first visualization over tabular RTMs. The system needs to render:

1. **Traceability graphs:** Requirements → Features → Test Cases → Code
2. **Dependency graphs:** Hierarchical and cyclical dependencies
3. **Impact analysis:** "What breaks if I change X?" visualizations
4. **Coverage heat maps:** Visual coverage overlays on traceability graph
5. **Interactive editing:** Drag-and-drop nodes, create links visually

Graph requirements:
- **1000+ nodes:** Large projects have hundreds of requirements, thousands of test cases
- **10,000+ edges:** Dense traceability matrices
- **Real-time rendering:** <16ms frame time (60 FPS)
- **Layout algorithms:** Force-directed, hierarchical, DAG layouts
- **React integration:** Must work with React 19 + TanStack Router

## Decision

We will use **React Flow (xyflow)** as the primary graph visualization library.

## Rationale

### Technology Stack (from frontend/package.json)

```json
{
  "dependencies": {
    "@xyflow/react": "^12.8.0",  // React Flow v12 (latest)
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  }
}
```

### React Flow Advantages

- **React-first:** Built for React, not canvas/WebGL wrapper
- **Performance:** Handles 10,000+ nodes with virtualization
- **TypeScript:** Full type safety for nodes, edges, layouts
- **Built-in features:**
  - Minimap (overview)
  - Controls (zoom, pan, fit)
  - Background grid/dots
  - Edge types (straight, bezier, step, smooth-step)
  - Node types (default, input, output, custom)
- **Extensibility:** Custom nodes via React components
- **Layout plugins:** dagre, elk, d3-force integrations
- **Active development:** v12 released Dec 2024, monthly updates

### Architecture

```typescript
// Graph component structure
<ReactFlow
  nodes={nodes}            // Node data + positions
  edges={edges}            // Edge connections
  onNodesChange={...}      // Drag, delete, select
  onEdgesChange={...}      // Create, delete links
  onConnect={...}          // New link validation
  nodeTypes={customNodes}  // Requirement, TestCase, Feature nodes
  edgeTypes={customEdges}  // Traceability, Dependency edges
  fitView                  // Auto-fit to viewport
>
  <Background />
  <Controls />
  <MiniMap />
  <Panel position="top-right">
    <CoverageStats />
  </Panel>
</ReactFlow>
```

### Node Types

```typescript
// Custom node: Requirement
const RequirementNode: NodeComponent<RequirementData> = ({ data }) => (
  <div className="requirement-node">
    <Handle type="source" position="bottom" />
    <div className="node-header">
      <span className="node-id">{data.id}</span>
      <CoverageBadge coverage={data.coverage} />
    </div>
    <div className="node-title">{data.title}</div>
    <Handle type="target" position="top" />
  </div>
);
```

### Layout Strategy

**Auto-layout with ELK**
```typescript
import ELK from 'elkjs/lib/elk.bundled.js';

const elk = new ELK();

async function layoutGraph(nodes, edges) {
  const graph = {
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',        // Hierarchical
      'elk.direction': 'DOWN',           // Top-to-bottom
      'elk.spacing.nodeNode': '80',      // Node spacing
      'elk.layered.spacing.nodeNodeBetweenLayers': '100',
    },
    children: nodes.map(n => ({ id: n.id, width: 200, height: 80 })),
    edges: edges.map(e => ({ id: e.id, sources: [e.source], targets: [e.target] })),
  };

  const layout = await elk.layout(graph);

  // Apply positions to React Flow nodes
  return nodes.map(node => ({
    ...node,
    position: {
      x: layout.children.find(n => n.id === node.id).x,
      y: layout.children.find(n => n.id === node.id).y,
    },
  }));
}
```

## Alternatives Rejected

### Alternative 1: Sigma.js

- **Description:** WebGL-based graph library (fast rendering)
- **Pros:** Extremely fast (100k+ nodes), WebGL rendering, force-directed layouts
- **Cons:** Canvas-based (not React components), harder to customize nodes, less interactive editing
- **Why Rejected:** React Flow's component-based nodes are easier to style and extend. Sigma.js better for read-only graphs with huge node counts (not our primary use case).

### Alternative 2: Cytoscape.js

- **Description:** Scientific graph visualization library
- **Pros:** Mature (10+ years), many layout algorithms, large community
- **Cons:** jQuery-era API, harder React integration, heavier bundle (~500KB)
- **Why Rejected:** React Flow has better React integration and smaller bundle. Cytoscape's scientific focus (biological networks) is overkill for traceability graphs.

### Alternative 3: D3.js (force-directed graph)

- **Description:** Low-level D3 force simulation + SVG rendering
- **Pros:** Full control, flexible, well-documented
- **Cons:** Must build everything (zoom, pan, minimap, edge routing), complex React integration, more code to maintain
- **Why Rejected:** React Flow provides all needed features out-of-box. D3 is too low-level for this use case.

### Alternative 4: Mermaid.js

- **Description:** Text-based diagram library (flowcharts, sequence diagrams)
- **Pros:** Simple text syntax, auto-layout, widely used
- **Cons:** Static rendering (no drag-and-drop), limited interactivity, not designed for large graphs
- **Why Rejected:** TraceRTM needs interactive editing (drag nodes, create links). Mermaid is for static diagrams.

## Consequences

### Positive

- **Component-based nodes:** Use React components for custom node rendering (badges, icons, tooltips)
- **Type-safe:** TypeScript types for nodes, edges, events
- **Performance:** Virtualization handles 10,000+ nodes smoothly
- **Built-in features:** Minimap, controls, background grid included
- **Layout flexibility:** Can switch between force-directed, hierarchical, circular layouts
- **Edge routing:** Smart edge paths avoid node overlaps

### Negative

- **Bundle size:** ~150KB minified (acceptable for graph-heavy app)
- **Learning curve:** React Flow API requires understanding nodes/edges/handles
- **Layout computation:** Auto-layout for large graphs (1000+ nodes) can take 1-2 seconds
- **Memory:** Large graphs (5000+ nodes) use ~100MB RAM

### Neutral

- **Server-side rendering:** Not supported (client-side only) - acceptable for SPA
- **Mobile support:** Touch gestures work, but graph editing on mobile is difficult (design constraint, not library issue)

## Implementation

### Affected Components

- `frontend/packages/graph-viz/` - Shared graph components
- `frontend/apps/web/src/components/visualization/TraceabilityGraph.tsx` - Main graph view
- `frontend/apps/web/src/components/visualization/CoverageHeatMap.tsx` - Coverage overlay
- `frontend/apps/web/src/components/visualization/ImpactAnalysis.tsx` - Impact graph
- `frontend/apps/web/src/hooks/useGraphLayout.ts` - Layout algorithms

### Migration Strategy

**Phase 1: Basic Graph (Week 1)**
- Install @xyflow/react
- Create basic TraceabilityGraph component
- Implement Requirement, TestCase, Feature node types
- Force-directed layout (default)

**Phase 2: Layouts & Interactions (Week 2)**
- Add ELK hierarchical layout
- Implement drag-and-drop
- Link creation UI
- Minimap, controls, zoom

**Phase 3: Advanced Features (Week 3)**
- Coverage heat map overlay
- Impact analysis view
- Custom edge types (traceability, dependency)
- Export to PNG/SVG

### Rollout Plan

- **Phase 1:** Read-only graph view (no editing)
- **Phase 2:** Interactive editing (drag, link creation)
- **Phase 3:** Advanced visualizations (coverage, impact)

### Success Criteria

- [ ] Render 1000+ node graph in <2s
- [ ] 60 FPS during pan/zoom
- [ ] Drag-and-drop node repositioning
- [ ] Create links by dragging between node handles
- [ ] Auto-layout with hierarchical algorithm
- [ ] Export graph to PNG/SVG
- [ ] Coverage heat map overlay

## References

- [React Flow Documentation](https://reactflow.dev/)
- [React Flow Examples](https://reactflow.dev/examples)
- [ELK Layouting](https://www.eclipse.org/elk/)
- [ADR-0001: TraceRTM v2 Architecture](ADR-0001-tracertm-v2-architecture.md)
- [ADR-0011: Frontend Framework](ADR-0011-frontend-framework-architecture.md)

---

**Notes:**
- React Flow Pro (paid) adds features like node resizing, sub-flows
- Not needed for TraceRTM (free version sufficient)
- Custom layouts via `getLayoutedElements` function
- Graph state managed via Zustand store (frontend state management)
