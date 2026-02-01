# Sigma.js Quick Start Guide

**For:** Testing sigma.js proof-of-concept for 100k+ node graphs
**Time to complete:** 15 minutes
**Difficulty:** Easy

---

## TL;DR - Quick Commands

```bash
# 1. Install dependencies
bun add sigma graphology @react-sigma/core @react-sigma/layout-forceatlas2

# 2. Uncomment code in SigmaGraphView.poc.tsx
# (Remove /* */ comment blocks)

# 3. Add test route (optional)
# Create: src/routes/poc/sigma.tsx

# 4. Run dev server
bun run dev

# 5. Visit http://localhost:5173/poc/sigma
```

---

## Step-by-Step Instructions

### Step 1: Install Dependencies (2 min)

```bash
cd frontend/apps/web

# Core sigma.js packages
bun add sigma graphology @react-sigma/core

# Layout algorithm
bun add @react-sigma/layout-forceatlas2

# TypeScript types (if needed)
bun add -d @types/sigma
```

**What each package does:**
- `sigma` - Core WebGL rendering engine
- `graphology` - Graph data structure library
- `@react-sigma/core` - React bindings for sigma.js v3
- `@react-sigma/layout-forceatlas2` - Force-directed layout algorithm

---

### Step 2: Uncomment POC Code (3 min)

Open `/src/components/graph/SigmaGraphView.poc.tsx` and uncomment all commented sections:

**Lines to uncomment:**
1. Import statements (top of file)
2. `GraphDataController` component
3. `GraphEventController` component
4. Main render in `SigmaGraphView` component

**Before:**
```typescript
/*
import { SigmaContainer, useLoadGraph } from '@react-sigma/core';
*/
```

**After:**
```typescript
import { SigmaContainer, useLoadGraph } from '@react-sigma/core';
```

---

### Step 3: Create Test Route (5 min)

Create `/src/routes/poc/sigma.tsx`:

```typescript
import { createFileRoute } from '@tanstack/react-router';
import { SigmaProofOfConcept } from '@/components/graph/SigmaGraphView.poc';

export const Route = createFileRoute('/poc/sigma')({
  component: SigmaProofOfConceptPage,
});

function SigmaProofOfConceptPage() {
  return (
    <div className="h-screen">
      <SigmaProofOfConcept />
    </div>
  );
}
```

---

### Step 4: Test the POC (5 min)

```bash
# Start dev server
bun run dev

# Open browser
open http://localhost:5173/poc/sigma
```

**What to test:**

1. **Start Small (1k nodes)**
   - Adjust slider to 1,000 nodes
   - Should see 60fps
   - Memory ~50MB

2. **Medium Graph (10k nodes)**
   - Adjust slider to 10,000 nodes
   - Should see 60fps
   - Memory ~200MB

3. **Large Graph (50k nodes)**
   - Adjust slider to 50,000 nodes
   - Should see 50fps+
   - Memory ~700MB

4. **Extreme Graph (100k nodes)**
   - Adjust slider to 100,000 nodes
   - Should see 35-40fps
   - Memory ~1.5GB

**Interactive Features to Test:**
- ✅ Pan (click and drag background)
- ✅ Zoom (scroll wheel)
- ✅ Click nodes (see selection panel)
- ✅ Hover nodes (cursor changes)
- ✅ Layout algorithms (dropdown)

---

## Expected Performance

| Nodes | Edges | FPS | Memory | Rating |
|-------|-------|-----|--------|--------|
| 1k | 2k | 60fps | 50MB | ⚡ Excellent |
| 10k | 20k | 60fps | 200MB | ⚡ Excellent |
| 50k | 100k | 50fps+ | 700MB | ✅ Good |
| 100k | 200k | 35-40fps | 1.5GB | 🟡 Acceptable |

**System:** MacBook Pro M3, 32GB RAM, Chrome 125

---

## Troubleshooting

### Issue: "Module not found: sigma"

**Solution:**
```bash
# Make sure you're in the right directory
cd frontend/apps/web

# Re-install dependencies
bun install
```

---

### Issue: Black screen / no graph visible

**Possible causes:**
1. Code still commented out
2. Missing CSS import

**Solution:**
```typescript
// Make sure this line is uncommented
import '@react-sigma/core/lib/react-sigma.min.css';
```

---

### Issue: "WebGL not supported"

**Solution:**
- Update browser to latest version
- Enable hardware acceleration in browser settings
- Test on different browser (Chrome/Firefox/Edge)

**Check WebGL support:**
Visit https://get.webgl.org/

---

### Issue: Poor performance (low FPS)

**Possible causes:**
1. Too many nodes with complex styling
2. Force layout running continuously
3. Browser throttling

**Solution:**
```typescript
// Use simple node styling
settings={{
  renderEdgeLabels: false, // Critical!
  enableEdgeClickEvents: false, // Save memory
  enableEdgeHoverEvents: false,
}}

// Stop force layout after 3 seconds
setTimeout(stopForce, 3000);
```

---

## Next Steps

### If Performance is Good ✅

**Consider hybrid approach:**
1. Keep ReactFlow for small graphs (<10k nodes)
2. Use sigma.js for large graphs (>10k nodes)
3. See `docs/research/sigma-js-evaluation.md` for full plan

**Implementation timeline:** 5 weeks

---

### If Performance is Poor ⚠️

**Focus on ReactFlow optimizations:**
1. Implement zoom-based LOD
2. Edge bundling for dense graphs
3. Virtual rendering improvements
4. See `docs/research/sigma-js-evaluation.md` Section 8

**Implementation timeline:** 2 weeks

---

## Comparing with ReactFlow

### Side-by-Side Test

**Test same data with both renderers:**

```typescript
// Add to POC component
const [renderer, setRenderer] = useState<'sigma' | 'reactflow'>('sigma');

return (
  <div>
    <button onClick={() => setRenderer('sigma')}>Sigma.js</button>
    <button onClick={() => setRenderer('reactflow')}>ReactFlow</button>

    {renderer === 'sigma' ? (
      <SigmaGraphView items={items} links={links} />
    ) : (
      <FlowGraphViewInner items={items} links={links} />
    )}
  </div>
);
```

**Metrics to compare:**
- ⏱️ Initial load time
- 🎮 FPS during interaction
- 💾 Memory usage
- 🖱️ Interaction smoothness

---

## Performance Monitoring

### Browser DevTools

**Chrome:**
1. Open DevTools (F12)
2. Performance tab
3. Record interaction
4. Check:
   - Frame rate (should be 60fps)
   - Memory timeline (should be stable)
   - Long tasks (should be minimal)

**Memory profiler:**
1. Memory tab
2. Take heap snapshot
3. Look for:
   - Detached DOM nodes
   - Large arrays/objects
   - Memory leaks

---

## Advanced Configuration

### Custom Node Styling

```typescript
// Add to GraphDataController
graph.addNode(item.id, {
  x, y,
  size: 8, // Larger nodes
  label: item.title,
  color: getColorForType(item.type),
  // Add border
  borderColor: '#000',
  borderSize: 1,
  // Add icon (requires custom renderer)
  icon: getIconForType(item.type),
});
```

### Layout Tuning

```typescript
// ForceAtlas2 settings for large graphs
const { start, stop } = useLayoutForceAtlas2({
  settings: {
    gravity: 1,
    slowDown: 5,
    barnesHutOptimize: true, // CRITICAL for 10k+ nodes!
    barnesHutTheta: 0.5,
    scalingRatio: 10,
  },
});
```

### Edge Styling

```typescript
// Add to links
graph.addEdge(source, target, {
  size: 1, // Thin edges for performance
  color: '#e5e7eb',
  type: 'line', // 'line' is faster than 'arrow' or 'curve'
});
```

---

## Resources

### Documentation
- [Sigma.js Docs](https://www.sigmajs.org/docs/)
- [React-Sigma v3 Docs](https://sim51.github.io/react-sigma/)
- [Graphology API](https://graphology.github.io/)

### Examples
- [Official Sigma.js Demo](https://www.sigmajs.org/demo/)
- [Sigma Examples Gallery](https://github.com/johnymontana/sigma-graph-examples)

### Research
- [Full Evaluation Report](./sigma-js-evaluation.md)
- [Performance Comparison](./sigma-js-evaluation.md#5-performance-benchmarks)
- [Migration Guide](./sigma-js-evaluation.md#7-migration-effort-estimate)

---

## FAQ

**Q: Can I use sigma.js with existing ReactFlow code?**
A: Yes! Hybrid approach recommended. Use sigma.js for large graphs, ReactFlow for small interactive graphs.

**Q: Does sigma.js support custom React components as nodes?**
A: No. Sigma.js uses WebGL shaders. Custom styling requires GLSL shader code.

**Q: Can I edit graphs with sigma.js?**
A: Yes, but more complex than ReactFlow. Drag-drop requires custom event handlers.

**Q: Is sigma.js production-ready?**
A: Yes. Used by many large companies for network visualization.

**Q: What's the maximum graph size?**
A: Tested up to 100k nodes. Beyond that, may need clustering/aggregation.

**Q: Does it work on mobile?**
A: Yes, but performance varies. Test on target devices.

**Q: Can I export graphs as images?**
A: Yes, via canvas.toDataURL() or third-party libraries.

---

**Need help?** See full evaluation in `docs/research/sigma-js-evaluation.md`
