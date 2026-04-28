# Quad-tree Spatial Partitioning for Viewport Culling

## Overview

This document describes the quad-tree spatial indexing system for efficient viewport culling in large graphs (10k-100k+ nodes).

## Problem

The original LOD (Level of Detail) system used O(n) distance checks for every node on every frame:

```typescript
// O(n) - checks EVERY node
for (const node of allNodes) {
  const distance = calculateDistance(node.position, viewportCenter);
  const lodLevel = getLODForDistance(distance);
  // Apply LOD...
}
```

**Performance Impact:**
- 100k nodes: ~10ms per frame just for distance calculations
- Checked all nodes even though only ~500 are visible
- Caused frame drops during pan/zoom

## Solution: Quad-tree Spatial Partitioning

Quad-trees are a hierarchical spatial data structure that partitions 2D space into quadrants recursively.

### Data Structure

```
Root Node (covers entire graph space)
├── NW Quadrant (top-left)
│   ├── NW.NW
│   ├── NW.NE
│   ├── NW.SW
│   └── NW.SE
├── NE Quadrant (top-right)
├── SW Quadrant (bottom-left)
└── SE Quadrant (bottom-right)
```

### Algorithm

1. **Build Phase (O(n log n)):**
   - Insert all nodes into quad-tree
   - Tree automatically balances based on spatial distribution
   - Done once when nodes change

2. **Query Phase (O(log n)):**
   - Define viewport rectangle
   - Traverse tree, pruning entire subtrees that don't intersect viewport
   - Return only nodes in viewport + buffer zone

### Performance

| Operation | Old (O(n)) | New (O(log n)) | Improvement |
|-----------|-----------|----------------|-------------|
| 1k nodes  | ~0.1ms    | ~0.01ms        | 10x         |
| 10k nodes | ~1ms      | ~0.1ms         | 10x         |
| 100k nodes| ~10ms     | ~0.5ms         | 20x         |

**Key Insight:** Only computes LOD for ~100-500 visible nodes instead of all 100k.

## Implementation

### Core Components

#### 1. QuadTreeNodeIndex (`src/lib/quadTreeIndex.ts`)

Main spatial index class:

```typescript
const index = new QuadTreeNodeIndex();

// Build index (once or when nodes change)
index.build(nodes);

// Query viewport (every frame)
const viewport = { x: 0, y: 0, width: 1920, height: 1080 };
const visibleNodes = index.queryViewportWithBuffer(viewport, 200);
// Returns ~100-500 nodes instead of checking 100k
```

**Key Methods:**

- `build(nodes)` - Construct index (O(n log n))
- `queryViewport(rect)` - Rectangle query (O(log n))
- `queryViewportWithBuffer(rect, buffer)` - Query with buffer zone
- `findNearest(x, y)` - Nearest neighbor search
- `findWithinRadius(x, y, radius)` - Radial query
- `add(node)` - Add single node dynamically
- `updatePosition(id, x, y)` - Update node position

#### 2. useQuadTreeCulling Hook (`src/hooks/useQuadTreeCulling.ts`)

React integration for viewport culling:

```typescript
const { visibleNodes, visibleNodeIds, stats } = useQuadTreeCulling({
  nodes: allNodes,
  viewport: reactFlowViewport,
  bufferZone: 200,
  enabled: true,
});

// Use visibleNodes for LOD computation
// Use visibleNodeIds for fast "is visible?" checks
```

**Features:**

- Automatic index rebuild when nodes change
- Performance statistics
- Viewport tracking
- Buffer zone support

### Integration with FlowGraphViewInner

Replace distance checks with quad-tree queries:

```typescript
// OLD: O(n) distance check
const nodesForLayout = useMemo(() => {
  return allNodes.map(node => {
    const distance = calculateDistance(node.position, viewportCenter);
    const lodLevel = determineLODLevel(viewport.zoom, { distance });
    // ...
  });
}, [allNodes, viewport]);

// NEW: O(log n) quad-tree query
const { visibleNodes } = useQuadTreeCulling({
  nodes: allNodes,
  viewport,
  bufferZone: 200,
});

const nodesForLayout = useMemo(() => {
  // Only process visible nodes (~100-500 instead of 100k)
  return visibleNodes.map(node => {
    const lodLevel = determineLODLevel(viewport.zoom);
    // ...
  });
}, [visibleNodes, viewport]);
```

## Architecture

### Build Phase

```
Input: 100k nodes
  ↓
Convert to QuadTreeNode format
  ↓
d3-quadtree.addAll(nodes)  // O(n log n)
  ↓
Spatial index ready
```

### Query Phase (Every Frame)

```
React Flow Viewport Change
  ↓
Convert viewport to rectangle { x, y, width, height }
  ↓
quadTree.visit() with rectangle intersection test
  ↓ (prunes entire subtrees)
Return ~100-500 visible nodes
  ↓
Compute LOD only for visible nodes  // O(visible) << O(n)
  ↓
Render optimized nodes
```

## Memory Usage

- **Quadtree Structure:** ~4-8 bytes per node
- **Node Map:** ~40-60 bytes per node (for O(1) ID lookup)
- **Total:** ~50-70 bytes per node

For 100k nodes: ~5-7 MB (negligible)

## Trade-offs

### Advantages
- ✅ 10-20x faster viewport queries
- ✅ Scales logarithmically (O(log n))
- ✅ Efficient dynamic updates (add/remove nodes)
- ✅ Supports nearest neighbor queries
- ✅ Low memory overhead

### Disadvantages
- ⚠️ Initial build cost (O(n log n))
- ⚠️ Rebuild needed when many nodes change position
- ⚠️ Slightly more complex than linear scan

### When to Use

Use quad-tree culling when:
- ✅ Node count > 10,000
- ✅ Frequent viewport changes (pan/zoom)
- ✅ Nodes mostly static or update infrequently

Stick with O(n) when:
- ❌ Node count < 1,000
- ❌ Nodes update positions every frame
- ❌ Memory is extremely constrained

## Buffer Zone Strategy

Buffer zone prevents "popping" of nodes at viewport edges:

```typescript
// Without buffer: nodes pop in/out at exact viewport edge
const visibleNodes = index.queryViewport(viewport);

// With buffer: nodes fade in/out smoothly
const visibleNodes = index.queryViewportWithBuffer(viewport, 200);
```

**Recommended Buffer Sizes:**

| Zoom Level | Buffer (pixels) |
|------------|----------------|
| < 0.5      | 400            |
| 0.5 - 1.0  | 200            |
| > 1.0      | 100            |

## Hybrid Approach

Combine quad-tree culling with hierarchical LOD:

```typescript
// 1. Quad-tree: Cull to viewport (~500 nodes)
const { visibleNodes } = useQuadTreeCulling({ nodes, viewport });

// 2. Distance-based LOD: Only for visible nodes
const nodesWithLOD = visibleNodes.map(node => {
  const distance = calculateDistance(node.position, viewportCenter);
  const lodTier = getDistanceTier(distance);
  return { ...node, lodTier };
});

// 3. Hierarchical culling: Progressive detail reduction
const culledEdges = cullEdgesEnhanced(edges, nodesWithLOD, viewport);
```

## Benchmarks

Run benchmarks with:

```bash
bun test quadTreeCulling.benchmark.test.ts
```

### Expected Results (100k nodes)

```
=== Quad-tree Build ===
Build time: ~150ms (one-time cost)
Tree depth: 12-15 levels

=== Viewport Query ===
O(n) linear scan: ~10ms
Quad-tree query: ~0.5ms
Speedup: 20x

Visible nodes: 487 / 100,000
Culling ratio: 99.5%

=== Dynamic Updates ===
Add 100 nodes: ~1ms
Update 100 positions: ~1ms
```

## Future Optimizations

1. **Web Worker Integration**
   - Build quad-tree off main thread
   - Query in web worker
   - Further reduce main thread load

2. **Lazy Rebuilding**
   - Track "dirty" nodes
   - Only rebuild affected subtrees
   - Avoid full rebuild on minor changes

3. **Viewport Prediction**
   - Predict viewport movement
   - Pre-query next viewport
   - Eliminate query latency

4. **R-tree for Complex Shapes**
   - Switch to R-tree for non-point data
   - Better for nodes with varying sizes
   - Supports rotated rectangles

## References

- [d3-quadtree Documentation](https://github.com/d3/d3-quadtree)
- [Quadtrees on Wikipedia](https://en.wikipedia.org/wiki/Quadtree)
- [Spatial Indexing in Computer Graphics](https://www.cs.umd.edu/~mount/Papers/cgc99-smpack.pdf)

## Related Systems

- **LOD System:** `src/components/graph/utils/lod.ts`
- **Viewport Culling:** `src/lib/enhancedViewportCulling.ts`
- **Edge Culling:** `src/lib/edgeLOD.ts`
- **Virtualization:** `src/components/graph/VirtualizedGraphView.tsx`
