# 100k-Node Visualization Architecture Evolution

**Visual guide showing how the architecture evolves through each phase**

---

## Current Architecture (Phases 1-4 Complete)

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interaction                        │
│                  (Click, Pan, Zoom, Hover)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              VirtualizedGraphView Component                  │
│  • Manages viewport state                                    │
│  • Orchestrates hooks                                        │
│  • Renders React Flow                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┬──────────────┐
           ▼                           ▼              ▼
┌──────────────────┐      ┌────────────────┐  ┌─────────────┐
│ useVirtualization│      │  useGraphWorker│  │ LRU Cache   │
│ • Viewport       │      │  • Layout      │  │ • Positions │
│   culling        │      │    compute     │  │ • Groupings │
│ • LOD levels     │      │  • Web Worker  │  │ • 50MB max  │
│ • 60-80% reduc.  │      │  • Basic only  │  │ • 78% hits  │
└─────────┬────────┘      └────────┬───────┘  └──────┬──────┘
          │                        │                  │
          └────────────────────────┼──────────────────┘
                                   │
                                   ▼
          ┌──────────────────────────────────────────┐
          │           React Flow (DOM)               │
          │  • Rendering layer                       │
          │  • Node types: richPill, simplePill      │
          │  • Edge rendering                        │
          └──────────────────────────────────────────┘
                                   │
                                   ▼
          ┌──────────────────────────────────────────┐
          │              Browser DOM                 │
          │  • 10k nodes max (400 rendered)          │
          │  • 55-60 FPS                             │
          │  • 65-75MB memory                        │
          └──────────────────────────────────────────┘

Limitations:
- Linear O(n) viewport queries (15ms for 10k nodes)
- UI blocking during layout (280ms)
- DOM rendering ceiling at 10k nodes
- No hardware acceleration
```

---

## Phase 5: Spatial Indexing (Week 2)

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interaction                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              VirtualizedGraphView Component                  │
└────────────────────────┬────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┬──────────────┐
           ▼                           ▼              ▼
┌──────────────────┐      ┌────────────────┐  ┌─────────────┐
│ useVirtualization│      │  useGraphWorker│  │ LRU Cache   │
│ + R-Tree Index   │◄─────┤                │  │             │
│ • O(log n)       │      └────────────────┘  └─────────────┘
│   queries        │
│ • 0.5ms for      │
│   100k nodes     │
└─────────┬────────┘
          │                NEW ⭐
          ▼
┌─────────────────────────────────────────┐
│    GraphSpatialIndex (R-Tree)           │
│  • Bulk insert: O(n log n)              │
│  • Query: O(log n)                      │
│  • Update: O(log n)                     │
│  • Memory: +18MB for 100k nodes         │
└─────────┬───────────────────────────────┘
          │
          │        Parallel Index ⭐
          │             NEW
          ▼
┌─────────────────────────────────────────┐
│      Quadtree (Hierarchical)            │
│  • Node clustering                      │
│  • Spatial partitioning                 │
│  • Fast range queries                   │
│  • Memory: +10MB for 100k nodes         │
└─────────┬───────────────────────────────┘
          │
          └──────────┬──────────────────────
                     ▼
          ┌──────────────────────────────────────────┐
          │           React Flow (DOM)               │
          │  • Now receives pre-culled nodes         │
          │  • 30x faster viewport updates           │
          └──────────────────────────────────────────┘

Improvements:
✅ Viewport queries: 15ms → 0.5ms (30x faster)
✅ Supports 100k nodes (culled to ~1k visible)
✅ Incremental updates: <1ms
✅ Memory: +18MB (acceptable overhead)
```

---

## Phase 6: Web Worker Offloading (Week 4)

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interaction                        │
│                     (Non-blocking!)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              VirtualizedGraphView Component                  │
│  + Progress Indicator                                        │
│  + Cancellation Support                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┬──────────────┐
           ▼                           ▼              ▼
┌──────────────────┐      ┌────────────────┐  ┌─────────────┐
│ GraphSpatialIndex│      │useProgressiveLayout  │  LRU Cache   │
│                  │      │  NEW ⭐         │  │             │
└──────────────────┘      │ • Non-blocking │  └─────────────┘
                          │ • Progress     │
                          │   callbacks    │
                          │ • Batched      │
                          │   position     │
                          │   updates      │
                          └────────┬───────┘
                                   │
                                   │ postMessage()
                                   ▼
          ┌────────────────────────────────────────────┐
          │        Web Worker (Background Thread)      │
          │               NEW ⭐                        │
          │                                            │
          │  ┌──────────────────────────────────┐     │
          │  │  Enhanced Layout Worker          │     │
          │  │  • Dagre algorithm               │     │
          │  │  • ELK algorithm                 │     │
          │  │  • D3-Force simulation           │     │
          │  │  • Progress tracking             │     │
          │  │  • Cancellation support          │     │
          │  └──────────────────────────────────┘     │
          │                                            │
          │  ┌──────────────────────────────────┐     │
          │  │  Incremental Layout Manager      │     │
          │  │  NEW ⭐                           │     │
          │  │  • Track dirty nodes             │     │
          │  │  • Compute affected subgraph     │     │
          │  │  • Layout only changed portion   │     │
          │  │  • Merge with previous layout    │     │
          │  └──────────────────────────────────┘     │
          └────────────────────────────────────────────┘
                                   │
                                   │ postMessage(positions)
                                   ▼
          ┌──────────────────────────────────────────┐
          │     Progressive Position Application     │
          │  • Batch size: 1000 nodes                │
          │  • RAF-based (non-blocking)              │
          │  • 50ms for 100k nodes                   │
          └──────────────────────────────────────────┘
                                   │
                                   ▼
          ┌──────────────────────────────────────────┐
          │           React Flow (DOM)               │
          └──────────────────────────────────────────┘

Improvements:
✅ UI blocking: 2.5s → 0ms (infinite improvement!)
✅ Layout computation: 2.8s in background (acceptable)
✅ Progress indicator: Real-time updates
✅ Incremental updates: 100 nodes in <500ms
✅ User can pan/zoom during layout
```

---

## Phase 7: WebGL Rendering (Week 8)

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interaction                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           AdaptiveGraphView (Router)                         │
│                     NEW ⭐                                    │
│  Feature Flag: WEBGL_RENDERING                               │
│  Decision: nodeCount > 10k ? PixiGraphView : VirtualizedGraphView
└────────────────────────┬────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│ VirtualizedGraphView │    │   PixiGraphView      │
│ (< 10k nodes)        │    │   NEW ⭐             │
│ React Flow (DOM)     │    │   PixiJS (WebGL)     │
└──────────────────────┘    └──────────┬───────────┘
                                       │
                     ┌─────────────────┴────────────────┐
                     ▼                                  ▼
          ┌─────────────────────┐        ┌──────────────────────┐
          │ GraphSpatialIndex   │        │  useGraphWorker      │
          │ (Same as Phase 5)   │        │  (Same as Phase 6)   │
          └─────────┬───────────┘        └───────────┬──────────┘
                    │                                 │
                    └──────────────┬──────────────────┘
                                   │
                                   ▼
          ┌────────────────────────────────────────────┐
          │        PixiJS Application (WebGL)          │
          │                  NEW ⭐                     │
          │                                            │
          │  ┌──────────────────────────────────┐     │
          │  │   InstancedNodeRenderer          │     │
          │  │   • Single draw call for 100k    │     │
          │  │   • Vertex shader instancing     │     │
          │  │   • GPU buffer: Float32Array     │     │
          │  │   • Memory: +40MB (textures)     │     │
          │  │   • Render time: 8ms/frame       │     │
          │  └──────────────────────────────────┘     │
          │                                            │
          │  ┌──────────────────────────────────┐     │
          │  │   EdgeRenderer (WebGL)           │     │
          │  │   • LOD-based edge complexity    │     │
          │  │   • Bezier (high), Straight (low)│     │
          │  │   • Batch rendering              │     │
          │  │   • Render time: 6ms/frame       │     │
          │  └──────────────────────────────────┘     │
          │                                            │
          │  ┌──────────────────────────────────┐     │
          │  │   InteractionManager             │     │
          │  │   • Click detection via R-Tree   │     │
          │  │   • Hover via pointer events     │     │
          │  │   • Selection highlighting       │     │
          │  │   • World ↔ Screen transforms    │     │
          │  └──────────────────────────────────┘     │
          │                                            │
          │  ┌──────────────────────────────────┐     │
          │  │   CameraController               │     │
          │  │   • Zoom towards cursor          │     │
          │  │   • Smooth pan                   │     │
          │  │   • Velocity damping             │     │
          │  │   • Zoom limits (0.1 - 5x)       │     │
          │  └──────────────────────────────────┘     │
          └────────────────────────────────────────────┘
                                   │
                                   ▼
          ┌────────────────────────────────────────────┐
          │         GPU / Browser (WebGL Context)      │
          │  • Hardware-accelerated rendering          │
          │  • 100k nodes @ 60 FPS                     │
          │  • Memory: 140MB (vs 250MB DOM)            │
          └────────────────────────────────────────────┘
                                   │
                                   │ Optional: Hybrid Mode
                                   ▼
          ┌────────────────────────────────────────────┐
          │    DOM Overlay (for Rich Node Content)     │
          │  • WebGL renders edges                     │
          │  • DOM renders nodes with complex content  │
          │  • Best of both worlds                     │
          └────────────────────────────────────────────┘

Improvements:
✅ FPS: 12 → 58 (5x improvement)
✅ Render time: 85ms → 14ms per frame
✅ Memory: 250MB → 140MB (-40% reduction)
✅ Edge rendering: 60ms → 6ms
✅ Supports 100k nodes at 60 FPS
✅ Feature flag for safe rollout
```

---

## Phase 8: Advanced Techniques (Week 12)

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interaction                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           AdaptiveGraphView (Enhanced)                       │
│  + Clustering toggle                                         │
│  + Edge bundling strength slider                            │
│  + GPU layout option                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
          ┌────────────────────────────────────────┐
          │        PixiGraphView (Enhanced)        │
          └────────────────────┬───────────────────┘
                               │
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│GraphClusterMgr  │  │ EdgeBundler      │  │ GPUForceLayout   │
│     NEW ⭐      │  │     NEW ⭐       │  │     NEW ⭐       │
└─────────────────┘  └──────────────────┘  └──────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                    GraphClusterManager                             │
│                         NEW ⭐                                      │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  Louvain Community Detection                         │         │
│  │  • Input: 100k nodes, 250k edges                     │         │
│  │  • Output: 500-1000 clusters                         │         │
│  │  • Computation: <1s                                  │         │
│  │  • Library: graphology-communities-louvain           │         │
│  └──────────────────────────────────────────────────────┘         │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  Cluster Rendering Logic                             │         │
│  │  • zoom < 0.5: Show cluster super-nodes (500 nodes)  │         │
│  │  • zoom ≥ 0.5: Show individual nodes (100k nodes)    │         │
│  │  • Expand/collapse clusters on click                 │         │
│  │  • Inter-cluster edge aggregation                    │         │
│  └──────────────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼ (when zoomed out)
                    100k nodes → 500 clusters (200x reduction!)


┌────────────────────────────────────────────────────────────────────┐
│               ForceDirectedEdgeBundler                             │
│                         NEW ⭐                                      │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  Edge Grouping by Direction                          │         │
│  │  • Group parallel edges (8 directions)               │         │
│  │  • Min 3 edges per bundle                            │         │
│  └──────────────────────────────────────────────────────┘         │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  Control Point Computation                           │         │
│  │  • Force-directed relaxation (50 iterations)         │         │
│  │  • Bundle strength: 0.85 (configurable)              │         │
│  │  • Smooth Bezier curves through control points       │         │
│  └──────────────────────────────────────────────────────┘         │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  LOD Edge Rendering                                  │         │
│  │  • High zoom: Bundled Bezier curves                  │         │
│  │  • Low zoom: Straight lines                          │         │
│  └──────────────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    250k edges → 60% visual clutter reduction


┌────────────────────────────────────────────────────────────────────┐
│                    GPUForceLayout (WebGPU)                         │
│                         NEW ⭐                                      │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  GPU Buffers                                         │         │
│  │  • nodeBuffer: 100k × 16 bytes (x,y,vx,vy)           │         │
│  │  • edgeBuffer: 250k × 8 bytes (source,target)        │         │
│  │  • Memory: +30MB (GPU-side)                          │         │
│  └──────────────────────────────────────────────────────┘         │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  Compute Shader (WGSL)                               │         │
│  │  @compute @workgroup_size(256)                       │         │
│  │  • Coulomb repulsion: O(n²) per iteration            │         │
│  │  • Hooke's attraction: O(m) per iteration            │         │
│  │  • Velocity Verlet integration                       │         │
│  │  • Runs on GPU (massive parallelism)                │         │
│  └──────────────────────────────────────────────────────┘         │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  Iteration Loop                                      │         │
│  │  • 100 iterations for 100k nodes                     │         │
│  │  • Each iteration: ~40ms (GPU)                       │         │
│  │  • Total: 4.2s (vs 60s CPU!)                         │         │
│  │  • Non-blocking via async/await                      │         │
│  └──────────────────────────────────────────────────────┘         │
│                                                                    │
│  ┌──────────────────────────────────────────────────────┐         │
│  │  Fallback Chain                                      │         │
│  │  • Try: WebGPU (Chrome 113+)                         │         │
│  │  • Fallback 1: WebGL2 compute shaders               │         │
│  │  • Fallback 2: CPU (existing Web Worker)            │         │
│  └──────────────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    Force layout: 60s CPU → 4.2s GPU (14x faster!)


Combined Rendering Pipeline:
────────────────────────────────────────────────────────────────────

   100k nodes, 250k edges
        │
        ├─ zoom < 0.5? → Clustering → 500 cluster nodes
        │                                  │
        │                                  ▼
        ├─ Edge bundling enabled? → Bundle → 60% clutter reduction
        │                                         │
        │                                         ▼
        ├─ Force layout needed? → GPU compute → 4.2s (vs 60s CPU)
        │                                      │
        │                                      ▼
        ├─ Viewport culling (R-Tree) ────→ ~1k visible nodes
        │                                      │
        │                                      ▼
        └───────────────────────────────→ PixiJS WebGL Rendering
                                                │
                                                ▼
                                          60 FPS @ 100k+ nodes!

Final Performance:
✅ FPS: 60 (sustained)
✅ Memory: 180-200MB
✅ Layout: 4.2s (GPU) vs 60s (CPU)
✅ Visual clutter: -60%
✅ Supports: 100k+ nodes
```

---

## Comparison: Before vs After

### Architecture Complexity

```
Phase 1-4 (Before):          Phases 5-8 (After):
──────────────────          ───────────────────

Simple                      Complex
↓                           ↓
User                        User
↓                           ↓
VirtualizedGraphView        AdaptiveGraphView (Router)
↓                           ↓
useVirtualization           Feature Flag Decision
↓                           ├─ <10k: VirtualizedGraphView
React Flow (DOM)            └─ ≥10k: PixiGraphView
↓                                    ├─ GraphSpatialIndex (R-Tree)
Browser (60 FPS @10k)                ├─ useProgressiveLayout (Worker)
                                     ├─ GraphClusterManager (Louvain)
                                     ├─ EdgeBundler (Force-directed)
                                     ├─ GPUForceLayout (WebGPU)
                                     └─ PixiJS (WebGL)
                                          ├─ InstancedNodeRenderer
                                          ├─ EdgeRenderer (LOD)
                                          ├─ InteractionManager
                                          └─ CameraController
                                               ↓
                                          Browser (60 FPS @100k+)

Layers: 4                   Layers: 12
Techniques: 4               Techniques: 10
Complexity: Low             Complexity: High
Max Nodes: 10k              Max Nodes: 100k+
```

### Performance Metrics Evolution

```
Metric            │ Phase 1-4 │ +Phase 5 │ +Phase 6 │ +Phase 7 │ +Phase 8
──────────────────┼───────────┼──────────┼──────────┼──────────┼──────────
Max Nodes         │    10k    │   20k    │   50k    │  100k    │  100k+
FPS (100k nodes)  │    12     │   25     │   30     │   58     │   60
Viewport Query    │   15ms    │  0.5ms   │  0.5ms   │  0.5ms   │  0.5ms
Layout Time       │ 280ms(B)  │ 280ms(B) │ 2.8s(NB) │ 2.8s(NB) │ 4.2s(NB)*
Render Time/Frame │   85ms    │  50ms    │  40ms    │  14ms    │  14ms
Memory Usage      │   65MB    │  83MB    │  95MB    │  140MB   │  180MB
UI Blocking       │  280ms    │ 280ms    │   0ms    │   0ms    │   0ms

Legend:
(B) = Blocking
(NB) = Non-blocking
* = GPU-accelerated (vs 60s CPU)
```

---

## Technology Stack Evolution

```
Phase 1-4            Phase 5              Phase 6              Phase 7              Phase 8
──────────           ───────              ───────              ───────              ───────

React Flow           + RBush              + Enhanced           + PixiJS             + graphology
useVirtualization    + R-Tree             Worker               + WebGL              + Louvain
LOD System           + Quadtree           + Incremental        + Instancing         + d3-force
LRU Cache                                 Layout Mgr           + Shaders            + WebGPU
Progressive                               + Progress                                + Compute
Batching                                  Tracking                                  Shaders
```

---

## Migration Path Summary

```
Week 0-2:   10k baseline → 20k (Phase 5: Spatial Index)
Week 2-4:   20k → 50k (Phase 6: Web Workers)
Week 4-8:   50k → 100k (Phase 7: WebGL)
Week 8-12:  100k → 100k+ (Phase 8: Advanced)

Progressive enhancement:
✅ Backward compatible at each phase
✅ Feature flags for safe rollout
✅ Graceful degradation
✅ Zero breaking changes
```

---

**Created:** 2026-01-31
**Last Updated:** 2026-01-31
**Next Review:** After Phase 5 completion

**For more details, see:**
- [100k-node-visualization-roadmap.md](./100k-node-visualization-roadmap.md)
- [TECHNIQUE_QUICK_REFERENCE.md](./TECHNIQUE_QUICK_REFERENCE.md)
- [ROADMAP_SUMMARY.md](./ROADMAP_SUMMARY.md)
