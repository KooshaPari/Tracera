# Graph Layouts Quick Reference Card

Print this for your desk!

---

## One-Minute Decision Guide

```
QUESTION: What layout should I use?

├─ "Show me my requirements"
│  └─ ANSWER: Flow Chart 🔄
│     Install: npm install @dagrejs/dagre
│     Hook: useLayout.ts
│     Time: 3-4 hours
│
├─ "Things are too messy"
│  └─ ANSWER: Hierarchical 🔗
│     Install: npm install elkjs
│     Hook: useELKLayout.ts
│     Time: 8 hours
│
├─ "Show me unexpected patterns"
│  └─ ANSWER: Organic 🌐
│     Install: npm install d3-force
│     Hook: useForceLayout.ts
│     Time: 8 hours
│
└─ "Brainstorm / Plan"
   └─ ANSWER: Mind Map 🧠
      (Future phase)
```

---

## Library Cheat Sheet

| Library | What It Does | Speed | Complexity | Best For |
|---|---|---|---|---|
| Dagre | Top-to-bottom layout | Very Fast | Low | Default choice |
| ELK | Super configurable layout | Fast | Medium-High | Complex graphs |
| D3-Force | Physics-based layout | Slow | Medium | Exploration |
| D3-Hierarchy | Tree layout | Very Fast | Low | Single root |

---

## Installation (Copy-Paste Ready)

```bash
# All at once
npm install @dagrejs/dagre elkjs d3-force @xyflow/react

# Minimal (MVP only)
npm install @dagrejs/dagre

# Incremental
npm install @dagrejs/dagre           # Week 1
npm install elkjs                    # Week 2
npm install d3-force                 # Week 2
npm install @xyflow/react            # Already have it
```

---

## Configuration Templates

### Flow Chart (Dagre - Most Common)
```javascript
{
  rankdir: 'TB',        // Top to Bottom
  nodesep: 80,          // Space between nodes
  ranksep: 100,         // Space between layers
}
```

### Horizontal (Dagre)
```javascript
{
  rankdir: 'LR',        // Left to Right
  nodesep: 80,
  ranksep: 100,
}
```

### Hierarchical (ELK)
```javascript
{
  'elk.algorithm': 'layered',
  'elk.direction': 'RIGHT',
  'elk.spacing.nodeNode': 80,
  'elk.layered.spacing.nodeNodeBetweenLayers': 100,
}
```

### Organic (D3-Force)
```javascript
{
  chargeStrength: -300,     // Repulsion
  linkDistance: 100,        // Spring length
  centerStrength: 0.1,      // Pull to center
  iterations: 300,          // Calculation steps
}
```

---

## Code Templates (Copy-Paste)

### Minimal Hook (Dagre)
```typescript
import dagre from '@dagrejs/dagre';

export const useLayout = () => {
  const layoutNodes = (nodes, edges, dir = 'TB') => {
    const g = new dagre.graphlib.Graph();
    g.setGraph({ rankdir: dir, nodesep: 80, ranksep: 100 });
    g.setDefaultEdgeLabel(() => ({}));
    nodes.forEach(n => g.setNode(n.id, { width: 150, height: 50 }));
    edges.forEach(e => g.setEdge(e.source, e.target));
    dagre.layout(g);
    return nodes.map(n => {
      const dn = g.node(n.id);
      return { ...n, position: { x: dn.x - 75, y: dn.y - 25 } };
    });
  };
  return { layoutNodes };
};
```

### UI Button Group
```typescript
function LayoutButtons() {
  const { setNodes, getNodes } = useReactFlow();
  const edges = useEdges();
  const { layoutNodes } = useLayout();

  return (
    <>
      <button onClick={() => setNodes(layoutNodes(getNodes(), edges, 'TB'))}>
        🔄 Flow Chart
      </button>
      <button onClick={() => setNodes(layoutNodes(getNodes(), edges, 'LR'))}>
        ↔️ Horizontal
      </button>
    </>
  );
}
```

---

## Naming Convention (Final)

### DO Use These Names
```
✓ "Flow Chart"        (instead of "Dagre TB")
✓ "Hierarchical"      (instead of "ELK Layered")
✓ "Organic Network"   (instead of "Force-Directed")
✓ "Mind Map"          (instead of "Radial Tree")
✓ "Tree"              (instead of "D3 Hierarchy")
```

### DON'T Use These Terms
```
✗ "Dagre"
✗ "Force-Directed Algorithm"
✗ "ELK.js"
✗ "Layered Graph Drawing"
✗ "Physics-Based Layout"
✗ "Sugiyama"
```

---

## Performance Quick Guide

| Nodes | Best Layout | Time |
|---|---|---|
| < 50 | Dagre | < 50ms |
| 50-500 | Dagre | < 200ms |
| 500-1K | ELK | < 500ms |
| 1K+ | Clustering + Dagre | < 1s |

**Rule of Thumb**: Start with Dagre, switch to ELK if it's slow.

---

## Common Issues & Fixes

| Problem | Solution |
|---|---|
| Nodes overlapping | ↑ nodesep, ranksep |
| Layout too slow | ↓ Use Dagre instead of ELK |
| Edges crossing too much | Use Hierarchical (ELK) |
| Things look boring | Try Organic layout |
| Graph won't fit on screen | ↑ Zoom out or implement clustering |

---

## File Checklist

Need to create these files:

```
✓ src/hooks/useLayout.ts          (Dagre)
✓ src/hooks/useELKLayout.ts       (ELK - optional Week 2)
✓ src/hooks/useForceLayout.ts     (Force - optional Week 2)
✓ src/components/LayoutSelector.tsx
✓ src/components/LayoutSelector.css
✓ src/components/DiagramContainer.tsx
✓ src/config/layoutPresets.ts
✓ src/__tests__/layouts.test.ts
```

---

## React Flow Integration Pattern

```typescript
import ReactFlow, { useNodesState, useEdgesState } from '@xyflow/react';
import LayoutSelector from './LayoutSelector';

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <LayoutSelector />  {/* Add this */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
      >
        {/* rest of reactflow */}
      </ReactFlow>
    </div>
  );
}
```

---

## Feature Comparison

| Feature | Dagre | ELK | D3-Force | Notes |
|---|---|---|---|---|
| Easy to implement | ✓✓✓ | ✓ | ✓ | Dagre is simplest |
| Handles DAGs | ✓✓ | ✓✓✓ | ✗ | ELK best for complex |
| Fast | ✓✓✓ | ✓✓ | ✓ | Dagre is fastest |
| Deterministic | ✓✓✓ | ✓✓ | ✗ | Dagre is consistent |
| Beautiful | ✓ | ✓✓✓ | ✓✓ | ELK looks best |
| Configurable | ✓ | ✓✓✓ | ✓✓ | ELK has 100+ options |
| Handles 1000s | ✓ | ✓✓ | ✗ | Not D3-Force |

---

## UI Layout Selector Code

```tsx
<div style={{display: 'flex', gap: '10px', padding: '12px'}}>
  <button onClick={flowChart}>🔄 Flow Chart</button>
  <button onClick={hierarchical}>🔗 Hierarchical</button>
  <button onClick={organic}>🌐 Organic</button>
  <button onClick={mindmap}>🧠 Mind Map</button>
</div>
```

---

## Testing Sanity Check

```typescript
// All tests should pass
✓ layoutNodes returns array
✓ All nodes have position
✓ Nodes have x and y >= 0
✓ No nodes overlapping (except force layout)
✓ Edges connect to valid nodes
✓ Layout time < 1000ms
```

---

## Keyboard Shortcuts (Proposed)

```
F         → Flow Chart
H         → Hierarchical
O         → Organic
M         → Mind Map
T         → Tree

+/-       → Zoom in/out
0         → Fit to screen
Space     → Pan
```

---

## Color-Coded Priority

🔴 **MUST DO (Week 1)**
- [ ] Implement Dagre (useLayout.ts)
- [ ] Create LayoutSelector UI
- [ ] Test with sample graphs

🟡 **SHOULD DO (Week 2)**
- [ ] Add ELK (useELKLayout.ts)
- [ ] Add D3-Force (useForceLayout.ts)
- [ ] User testing

🟢 **NICE TO HAVE (Week 3+)**
- [ ] Clustering
- [ ] Mind Map layout
- [ ] Performance optimization
- [ ] Mobile responsive

---

## Troubleshooting Flowchart

```
Layout looks bad?
├─ Nodes overlapping?
│  └─ Increase nodesep & ranksep
├─ Too many crossings?
│  └─ Use Hierarchical (ELK)
├─ Too slow?
│  └─ Use Dagre instead
└─ Too chaotic?
   └─ Try Organic for exploration
```

---

## One-Page Implementation Plan

### Week 1 (Dagre)
- Day 1-2: useLayout.ts hook
- Day 3: LayoutSelector component
- Day 4: Integration testing
- Day 5: Documentation

### Week 2 (ELK + Force)
- Day 1-2: useELKLayout.ts hook
- Day 3: useForceLayout.ts hook
- Day 4: Add to UI selector
- Day 5: User testing

### Week 3 (Polish)
- Day 1-2: Performance optimization
- Day 3: Clustering (if needed)
- Day 4-5: Testing & refinement

---

## Links to Full Docs

- **Implementation Details**: See LAYOUT_IMPLEMENTATION_GUIDE.md
- **User Documentation**: See LAYOUT_USER_GUIDE.md
- **Executive Summary**: See LAYOUT_RECOMMENDATIONS_SUMMARY.md
- **Full Research**: See GRAPH_LAYOUT_RESEARCH.md
- **This Index**: See GRAPH_LAYOUTS_INDEX.md

---

## Key Metrics to Track

```
After Implementation, Measure:
✓ Time to understand (target: < 2 min)
✓ Performance (target: < 200ms)
✓ User adoption (target: 70% use default)
✓ Satisfaction (target: > 4/5 stars)
✓ Feature usage (target: 40% switch layouts)
```

---

## Quick Decision Tree

```
START
├─ First time? → USE: Flow Chart
├─ Messy graph? → USE: Hierarchical
├─ Exploring? → USE: Organic
├─ Planning? → USE: Mind Map
└─ Single root? → USE: Tree
```

---

## Bottom Line

1. **MVP**: Just use Dagre (Flow Chart) - Done in 2-3 weeks
2. **Phase 1**: Add ELK and Force-based - Done in 4-5 weeks total
3. **Scale**: Use clustering for 1000+ nodes
4. **Name Everything Intuitively**: Users don't know "Dagre"

---

## Print This Card & Share!

- Engineering team
- Product team
- Design team
- Stakeholders

**Keep it as reference during implementation!**

---

*Last Updated: January 2026*
*Print Date: ___________*
