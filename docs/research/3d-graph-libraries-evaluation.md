# 3D Graph Visualization Libraries: Comprehensive Evaluation for 100k+ Nodes

**Status:** Research Complete
**Date:** 2026-02-01
**Scope:** Evaluation of 3D graph visualization capabilities for large-scale traceability networks

---

## Executive Summary

This research evaluates 3D graph visualization libraries, specifically the [react-force-graph](https://github.com/vasturiano/react-force-graph) family and [3d-force-graph](https://github.com/vasturiano/3d-force-graph), for handling 100k+ nodes in TraceRTM's traceability matrix use case.

**Key Finding:** **2D visualization with WebGL acceleration is superior to 3D for traceability matrices** due to occlusion issues, interaction complexity, and the fundamentally planar nature of requirement relationships.

**Recommendation:** Continue with ReactFlow + WebGL Canvas optimization (current approach) rather than migrating to 3D visualization.

---

## Table of Contents

1. [Library Ecosystem Overview](#library-ecosystem-overview)
2. [Performance Analysis](#performance-analysis)
3. [2D vs 3D Trade-Off Analysis](#2d-vs-3d-trade-off-analysis)
4. [100k+ Node Strategy](#100k-node-strategy)
5. [Use Case Fit Assessment](#use-case-fit-assessment)
6. [Implementation Complexity](#implementation-complexity)
7. [Recommendations](#recommendations)

---

## Library Ecosystem Overview

### React-Force-Graph Family

The [react-force-graph](https://github.com/vasturiano/react-force-graph) suite provides React bindings for force-directed graph visualization across multiple rendering modes:

| Component | Rendering | Technology | Use Case |
|-----------|-----------|------------|----------|
| **react-force-graph-2d** | 2D Canvas | HTML5 Canvas | Fast, simple graphs (< 5k nodes) |
| **react-force-graph-3d** | 3D WebGL | Three.js | Spatial relationships (< 10k nodes) |
| **react-force-graph-vr** | VR | A-Frame | [Immersive analytics](https://wear-studio.com/vr-ar-data-visualization/) |
| **react-force-graph-ar** | AR | AR.js | Augmented data exploration |

**Source:** [React Force Graph Repository](https://github.com/vasturiano/react-force-graph)

### Core Technologies

#### 3D Force Graph
- **Library ID:** `/vasturiano/3d-force-graph`
- **Technology:** [ThreeJS/WebGL](https://threejs.org/) for 3D rendering
- **Physics Engine:** [d3-force-3d](https://github.com/vasturiano/d3-force-3d) or ngraph
- **Code Snippets:** 110 high-quality examples
- **Source Reputation:** High

#### Force Simulation
- **Library ID:** `/vasturiano/d3-force-3d`
- **Algorithm:** Barnes-Hut approximation with oct-trees
- **Dimensions:** Supports 1D, 2D, or 3D via `numDimensions`
- **Backwards Compatibility:** Drop-in replacement for d3-force (v3.0.0)

**Sources:**
- [3D Force Graph Documentation](https://vasturiano.github.io/3d-force-graph/)
- [D3 Force 3D GitHub](https://github.com/vasturiano/d3-force-3d)

---

## Performance Analysis

### Canvas vs WebGL Benchmarks

Research from [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12061801/) and [SpringerOpen](https://vciba.springeropen.com/articles/10.1186/s42492-025-00193-y) provides systematic benchmarks:

#### Scale Thresholds (2015 MacBook baseline)

| Rendering | Max Nodes | Max Edges | FPS Threshold | Notes |
|-----------|-----------|-----------|---------------|-------|
| **SVG** | 2,000 | 2,000 | < 30 FPS @ 10k | DOM overhead |
| **Canvas** | 5,000 | 5,000 | < 30 FPS @ 10k | Good for < 5k |
| **WebGL** | 10,000+ | 11,000+ | 60 FPS @ 10k | GPU acceleration |

**100k Node Performance:**
- **D3-Canvas:** Can generate 100k nodes (10:1 edge ratio) in < 15 minutes
- **D3-WebGL:** Can generate 100k nodes (10:1 edge ratio) in < 15 minutes
- **WebGL Advantage:** [10x performance improvement](https://cambridge-intelligence.com/visualizing-graphs-webgl/) over Canvas
- **Real-world:** WebGL can render [100,000+ elements smoothly](https://dev3lop.com/real-time-dashboard-performance-webgl-vs-canvas-rendering-benchmarks/) on desktop GPU

**Sources:**
- [Graph Visualization Efficiency Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12061801/)
- [Comparing Canvas vs WebGL Performance](https://digitaladblog.com/2025/05/21/comparing-canvas-vs-webgl-for-javascript-chart-performance/)
- [Real-Time Dashboard Performance Benchmarks](https://dev3lop.com/real-time-dashboard-performance-webgl-vs-canvas-rendering-benchmarks/)

#### Frame Rate Comparison

```
Metric              | Canvas    | WebGL
--------------------|-----------|----------
Initialization      | 15ms      | 40ms
Frame Time          | 1.2ms     | 0.01ms
Interaction FPS     | < 30      | 60
10k Elements        | Choppy    | Smooth
100k Elements       | N/A       | Feasible
```

**Sources:**
- [SVG vs Canvas vs WebGL 2025](https://www.svggenie.com/blog/svg-vs-canvas-vs-webgl-performance-2025)
- [Comparing Web Graphics Technologies](https://tapflare.com/articles/web-graphics-comparison-canvas-svg-webgl)

### Three.js Instanced Rendering Performance

For 100k+ nodes, instanced rendering is critical. Research from [ACM Digital Library](https://dl.acm.org/doi/fullHtml/10.1145/3665318.3677171) and [Three.js forum](https://discourse.threejs.org/t/instancedmesh-lod-1-million-instances/70748) shows:

#### Instancing Approaches

1. **InstancedMesh** (Recommended)
   - Single draw call for repeated geometry
   - Matrix transformations per instance
   - [3000% FPS improvement](https://dl.acm.org/doi/fullHtml/10.1145/3665318.3677171) on laptop/desktop hardware
   - Supports [1 million instances](https://discourse.threejs.org/t/instancedmesh-lod-1-million-instances/70748) with BVH optimization

2. **InstancedBufferGeometry**
   - Manual control over instance attributes
   - Lower-level API
   - Maximum flexibility

#### LOD Implementation

```javascript
// Example from 3d-force-graph with custom Three.js objects
const Graph = new ForceGraph3D(document.getElementById('3d-graph'))
  .nodeThreeObject(({ id }) => new THREE.Mesh(
    new THREE.SphereGeometry(5),
    new THREE.MeshLambertMaterial({
      color: Math.round(Math.random() * Math.pow(2, 24)),
      transparent: true,
      opacity: 0.75
    })
  ))
  .graphData(gData);
```

**LOD + Instancing Benefits:**
- Distance-based geometry switching
- Frustum culling (only render visible)
- Occlusion culling (hide blocked objects)
- [1300% larger datasets](https://dl.acm.org/doi/fullHtml/10.1145/3665318.3677171) visualized interactively

**Sources:**
- [Instanced Rendering of 3D Glyphs with LOD](https://dl.acm.org/doi/fullHtml/10.1145/3665318.3677171)
- [InstancedMesh LOD with 1M Instances](https://discourse.threejs.org/t/instancedmesh-lod-1-million-instances/70748)
- [Rendering 100k Spheres with Instancing](https://velasquezdaniel.com/blog/rendering-100k-spheres-instantianing-and-draw-calls/)
- [Three.js Instanced Rendering Guide](https://waelyasmina.net/articles/instanced-rendering-in-three-js/)

### Force Simulation Stabilization

#### D3-Force-3D vs D3-Force

Both libraries use similar optimization techniques:

| Feature | d3-force (2D) | d3-force-3d (3D) |
|---------|---------------|------------------|
| Spatial Index | Quadtree | Quad/Oct-tree |
| Algorithm | Barnes-Hut | Barnes-Hut |
| Complexity | O(n log n) | O(n log n) |
| Stabilization | Decay-based | Decay-based |

**Stabilization Time:**
- Higher decay → faster convergence, risk local minima
- Lower decay → slower convergence, better layout
- **3D adds ~30-50% overhead** vs 2D due to extra dimension

**Source:** [D3 Force 3D Documentation](https://github.com/vasturiano/d3-force-3d)

---

## 2D vs 3D Trade-Off Analysis

### When 3D Helps Comprehension

Recent research from [arXiv](https://www.arxiv.org/pdf/2508.00950) and [SpringerLink](https://link.springer.com/chapter/10.1007/978-3-030-01388-2_2) identifies scenarios where 3D visualization provides value:

#### Proven Benefits

1. **Hierarchical Depth Visualization**
   - Family tree structures
   - Organizational charts
   - Software package dependencies

2. **Network Topology Exploration**
   - [10x improvement](https://www.mdpi.com/2073-431X/13/8/189) in path-finding for skilled observers
   - 1000-node graphs navigable with <10% error rate
   - Requires motion + stereoscopic depth cues

3. **Temporal Dimensions**
   - Time-series evolution of graphs
   - Version history visualization

4. **Community Detection**
   - [S3D projections show advantages](https://www.frontiersin.org/journals/virtual-reality/articles/10.3389/frvir.2023.1155628/full) for complex structures
   - Cluster identification in dense networks

**Sources:**
- [Investigating Crossing Perception in 3D Graphs](https://www.arxiv.org/pdf/2508.00950)
- [Force-Directed Immersive 3D Network Visualization](https://www.mdpi.com/2073-431X/13/8/189)
- [Transforming Graph Data from 2D to AR 3D](https://www.frontiersin.org/journals/virtual-reality/articles/10.3389/frvir.2023.1155628/full)

### When 3D Hinders Comprehension

#### Critical Problems

1. **Occlusion Issues**
   - Unlike 2D edge crossings, 3D suffers from **node occlusion**
   - [Information loss](https://www.frontiersin.org/journals/virtual-reality/articles/10.3389/frvir.2023.1155628/full) when nodes hide behind others
   - Perspective-dependent edge crossing artifacts
   - No clear "optimal viewpoint" for all data

2. **Depth Perception Challenges**
   - Monocular displays lack true depth
   - Requires motion parallax or stereoscopy
   - Eye tracking complications in S3D
   - [Perspective dependency](https://www.collaborative-ai.org/publications/zhang25_gd.pdf) affects readability

3. **Interaction Complexity**
   - Camera navigation (orbit, pan, zoom) has steep learning curve
   - Selecting specific nodes difficult in dense graphs
   - Edge tracing harder than in 2D
   - [2D superior for answering time](https://link.springer.com/article/10.1007/s12650-024-01033-6)

4. **Cognitive Load**
   - 3D requires spatial reasoning
   - Mental rotation overhead
   - Multiple viewpoints needed for comprehension
   - Users prefer 2D for familiar tasks

**Sources:**
- [Towards Better Understanding of Graph Perception in Immersive Environments](https://www.collaborative-ai.org/publications/zhang25_gd.pdf)
- [Comparative Study of 2D vs 3D Charts in VR](https://link.springer.com/article/10.1007/s12650-024-01033-6)
- [Immersive Analytics: Reconsidering 3D Value](https://link.springer.com/chapter/10.1007/978-3-030-01388-2_2)

#### Traceability Matrix Specific Issues

For TraceRTM's use case:

❌ **Requirements relationships are fundamentally planar**
- Parent-child hierarchies (tree structure)
- Dependency links (DAG structure)
- Test coverage (bipartite graph)
- No inherent 3D spatial component

❌ **Critical tasks require precise node inspection**
- Reading requirement text
- Checking test coverage status
- Verifying link types
- Occlusion makes this impossible

❌ **Workflow emphasizes breadth over depth**
- Scanning for gaps in coverage
- Tracing impact across layers
- Matrix views (2D by definition)

❌ **Regulatory compliance documentation**
- Auditors need clear, unambiguous views
- 3D introduces interpretation ambiguity

---

## 100k+ Node Strategy

### Current TraceRTM Implementation

Based on `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/components/graph/VirtualizedGraphView.tsx`:

```typescript
// LOD Levels
const customNodeTypes = {
  richPill: RichNodePill,        // High detail: full metadata
  mediumPill: MediumNodePill,     // Medium: ID + label
  simplifiedPill: SimplifiedNodePill, // Low: ID only
  qaEnhanced: QAEnhancedNode,     // QA metrics
} as const;

// Viewport-based culling
const { visibleNodeIds, lodLevel, metrics } = useVirtualization(
  nodePositions,
  viewport,
  {
    enableLOD: enableVirtualization,
    nodeWidth: 200,
    nodeHeight: 120,
    padding: 300,
  },
);

// Only render visible nodes
const initialNodes = dagreLaidoutNodes
  .filter((node) => visibleNodeIds.has(node.id))
  .map((node) => ({
    ...node,
    type: lodLevel === "high" ? "richPill"
        : lodLevel === "medium" ? "mediumPill"
        : "simplifiedPill",
  }));
```

**Strengths:**
✅ Viewport culling (only render visible)
✅ Three-tier LOD (high/medium/low)
✅ ReactFlow (mature 2D library)
✅ DAG-aware layouts (flow-chart, hierarchy)

### 3D Alternative Strategy

If pursuing 3D (not recommended), would require:

#### 1. LOD in 3D Space

```javascript
// Distance-based LOD with 3d-force-graph
const Graph = new ForceGraph3D(element)
  .nodeThreeObject((node) => {
    const distance = camera.position.distanceTo(node.position);

    // Three LOD levels based on camera distance
    if (distance < 500) {
      return createDetailedMesh(node); // Full geometry
    } else if (distance < 2000) {
      return createMediumMesh(node);   // Simplified geometry
    } else {
      return createBillboardSprite(node); // 2D sprite
    }
  });
```

#### 2. Frustum Culling

Three.js provides automatic frustum culling:
- Objects outside camera view are not rendered
- Built into WebGLRenderer
- No manual implementation needed

#### 3. Instanced Rendering

```javascript
// For nodes of same type, use InstancedMesh
const geometry = new THREE.SphereGeometry(5);
const material = new THREE.MeshLambertMaterial();
const instancedMesh = new THREE.InstancedMesh(geometry, material, 100000);

// Update instance matrices
nodes.forEach((node, i) => {
  const matrix = new THREE.Matrix4();
  matrix.setPosition(node.x, node.y, node.z);
  instancedMesh.setMatrixAt(i, matrix);
});
instancedMesh.instanceMatrix.needsUpdate = true;
```

**Drawbacks:**
- All instances share same material/geometry
- Custom node styles require multiple InstancedMesh objects
- TraceRTM nodes have diverse appearances (types, states)

#### 4. Particle Systems

For extreme scale (1M+ nodes), use THREE.Points:
- Single draw call
- Billboard sprites facing camera
- Minimal interaction capabilities

**Not suitable for TraceRTM:** Requires detailed node inspection.

---

## Use Case Fit Assessment

### TraceRTM Requirements

| Requirement | 2D Fit | 3D Fit | Winner |
|-------------|--------|--------|--------|
| **100k+ nodes** | ✅ WebGL + virtualization | ✅ Instanced rendering | Tie |
| **Precise node selection** | ✅ Clear click targets | ❌ Depth ambiguity | 2D |
| **Text readability** | ✅ Always face-on | ❌ Angled perspectives | 2D |
| **Matrix view** | ✅ Native 2D concept | ❌ Forced into 3D | 2D |
| **Hierarchy visualization** | ✅ DAG layouts | ⚠️ Better depth cues | 2D |
| **Edge tracing** | ✅ Clear paths | ❌ Occlusion | 2D |
| **Audit compliance** | ✅ Unambiguous | ❌ Interpretable | 2D |
| **Learning curve** | ✅ Familiar | ❌ Camera navigation | 2D |

### Alternative Libraries Considered

#### Reagraph
- **Library ID:** `/reaviz/reagraph`
- **Technology:** WebGL for React
- **Benchmark Score:** 92.6 (highest)
- **Layouts:** Force 2D/3D, Circular, Tree, Hierarchical, Radial
- **Advantage:** More built-in layouts than react-force-graph
- **Limitation:** Still 3D for 3D mode

**Source:** [Reagraph Documentation](https://reagraph.dev/)

#### R3F ForceGraph
- **Library ID:** `/vasturiano/r3f-forcegraph`
- **Technology:** React-Three-Fiber
- **Advantage:** Declarative Three.js with React
- **Limitation:** 3D-only

---

## Implementation Complexity

### Current 2D Approach (ReactFlow)

**Complexity:** ⭐⭐ (Medium)

**What's Working:**
- Mature library with extensive documentation
- React-first API
- Built-in controls, minimap, background
- Type-safe with TypeScript
- Custom node components (already built)
- DAG-aware layouts

**Already Implemented:**
```typescript
// VirtualizedGraphView.tsx - 642 lines
- Viewport culling
- Three-tier LOD
- DAG layouts (flow-chart, hierarchy)
- Custom node types (RichPill, QAEnhanced)
- Detail panel
- Performance metrics display
```

**To Reach 100k:**
- [ ] Optimize Canvas rendering (offscreen canvas)
- [ ] Web Worker for layout computation
- [ ] Reduce edge rendering (adaptive edge LOD)
- [ ] Lazy load node metadata

**Estimated Effort:** 2-3 weeks

### 3D Approach (3d-force-graph)

**Complexity:** ⭐⭐⭐⭐ (High)

**From Scratch:**
- [ ] Replace ReactFlow with 3d-force-graph
- [ ] Implement camera controls (orbit, pan, zoom)
- [ ] Build custom LOD system
- [ ] Create Three.js node geometries
- [ ] Handle occlusion (transparency, outline rendering)
- [ ] Implement depth-based selection
- [ ] Build custom detail panel (HTML overlay)
- [ ] Add viewpoint presets for common tasks
- [ ] User testing for navigation UX

**Known Issues:**
- User reports: [5k nodes = lag](https://github.com/vasturiano/react-force-graph/issues/223)
- User reports: [117k nodes = WebGL crash](https://github.com/vasturiano/react-force-graph/issues/202)
- No built-in matrix view
- Difficult to integrate with existing UI components

**Estimated Effort:** 8-12 weeks + ongoing UX refinement

**Sources:**
- [Performance Optimization Issue #223](https://github.com/vasturiano/react-force-graph/issues/223)
- [Large Dataset Performance Issue #202](https://github.com/vasturiano/react-force-graph/issues/202)

---

## VR/AR Capabilities

### WebXR Support

The react-force-graph-vr component uses [A-Frame](https://aframe.io/) for immersive visualization:

```javascript
import ForceGraphVR from 'react-force-graph-vr';

<ForceGraphVR
  graphData={data}
  nodeLabel="id"
  nodeAutoColorBy="group"
/>
```

**Features:**
- WebXR Device API access
- No app store required (web-based)
- Oculus Quest, HTC Vive, etc. support
- Hand tracking and controller input

**Use Cases:**
- Geospatial data (smart cities, telecom)
- Professional training
- Data science exploratory analysis
- Remote collaboration

**Sources:**
- [Working with Graphs in AR/VR](https://www.yworks.com/blog/graphs-in-ar-vr)
- [Immersive Analytics Overview](https://wear-studio.com/vr-ar-data-visualization/)
- [WebXR Explained](https://immersive-web.github.io/webxr/explainer.html)

### Viability for TraceRTM

❌ **Not Recommended:**
- VR hardware not standard in enterprise ALM environments
- Auditors/stakeholders need accessible views
- No evidence VR improves traceability tasks
- Expensive overhead (headsets, training)

**Exception:** Research/demo purposes for stakeholder presentations.

---

## Recommendations

### Primary Recommendation: Continue with 2D + WebGL

**Rationale:**
1. **Traceability matrices are inherently 2D** (requirements ↔ tests)
2. **Occlusion is fatal** for audit-critical node inspection
3. **ReactFlow is mature and well-tested** for this use case
4. **Implementation is 80% complete** (VirtualizedGraphView.tsx)
5. **Performance targets achievable** via WebGL Canvas optimization

**Action Items:**
- [ ] Migrate ReactFlow renderer to WebGL Canvas (vs DOM)
- [ ] Implement offscreen canvas for node rendering
- [ ] Move force simulation to Web Worker
- [ ] Add adaptive edge LOD (hide low-priority edges at distance)
- [ ] Benchmark with synthetic 100k node dataset

**Expected Outcome:** 60 FPS with 100k nodes, viewport culling.

### Alternative Use Cases for 3D

Consider 3D visualization for **separate features** (not replacing main view):

#### 1. Hierarchical Project Explorer
- Folder structure in 3D space
- Module dependencies as spatial relationships
- **Example:** [Neo4j 3D Graph](https://neo4j.com/developer-blog/visualizing-graphs-in-3d-with-webgl/)

#### 2. Temporal Version Browser
- Version history along Z-axis
- Branch exploration in 3D
- Time-travel visualization

#### 3. Impact Radius Visualization
- Requirement changes radiate outward in 3D
- Affected components in concentric spheres
- Research/demo feature

**Implementation:** Add as secondary view, not primary traceability matrix.

### Monitoring & Benchmarking

**Metrics to Track:**
```typescript
interface PerformanceMetrics {
  visibleNodeCount: number;    // After culling
  totalNodeCount: number;       // In dataset
  fps: number;                  // Target: 60
  renderTime: number;           // Per frame (ms)
  layoutTime: number;           // Force simulation (ms)
  lodLevel: 'high' | 'medium' | 'low';
}
```

**Thresholds:**
- 60 FPS: Excellent
- 30-60 FPS: Acceptable
- <30 FPS: Requires optimization

---

## Appendix: Code Examples

### A. 3D Force Graph with Image Nodes

```javascript
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';

const Graph = () => (
  <ForceGraph3D
    graphData={data}
    nodeThreeObject={({ img }) => {
      const texture = new THREE.TextureLoader().load(`/imgs/${img}`);
      texture.colorSpace = THREE.SRGBColorSpace;
      const material = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(material);
      sprite.scale.set(12, 12);
      return sprite;
    }}
  />
);
```

### B. 2D Canvas with Auto-Pause

```javascript
import ForceGraph2D from 'react-force-graph-2d';

<ForceGraph2D
  graphData={data}
  autoPauseRedraw={true}  // Pause when simulation stops
  nodeCanvasObject={(node, ctx) => {
    ctx.fillStyle = node.color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
    ctx.fill();
  }}
/>
```

### C. LOD with Distance Culling

```javascript
// VirtualizedGraphView approach (current)
const { visibleNodeIds, lodLevel } = useVirtualization(
  nodePositions,
  viewport,
  { enableLOD: true, padding: 300 }
);

const nodes = allNodes
  .filter(n => visibleNodeIds.has(n.id))
  .map(n => ({
    ...n,
    type: lodLevel === 'high' ? 'detailed' : 'simplified'
  }));
```

---

## References

### Primary Sources

1. [React Force Graph Repository](https://github.com/vasturiano/react-force-graph)
2. [3D Force Graph Documentation](https://vasturiano.github.io/3d-force-graph/)
3. [D3 Force 3D](https://github.com/vasturiano/d3-force-3d)
4. [Reagraph High-Performance WebGL](https://reagraph.dev/)

### Performance Research

5. [Graph Visualization Efficiency of Popular Libraries](https://pmc.ncbi.nlm.nih.gov/articles/PMC12061801/)
6. [SpringerOpen Graph Visualization Study](https://vciba.springeropen.com/articles/10.1186/s42492-025-00193-y)
7. [Visualizing Graphs with WebGL (KeyLines)](https://cambridge-intelligence.com/visualizing-graphs-webgl/)
8. [Canvas vs WebGL Performance Comparison](https://digitaladblog.com/2025/05/21/comparing-canvas-vs-webgl-for-javascript-chart-performance/)
9. [Real-Time Dashboard Benchmarks](https://dev3lop.com/real-time-dashboard-performance-webgl-vs-canvas-rendering-benchmarks/)

### Three.js Optimization

10. [Instanced Rendering of 3D Glyphs with LOD](https://dl.acm.org/doi/fullHtml/10.1145/3665318.3677171)
11. [InstancedMesh LOD 1M Instances](https://discourse.threejs.org/t/instancedmesh-lod-1-million-instances/70748)
12. [Rendering 100k Spheres with Instancing](https://velasquezdaniel.com/blog/rendering-100k-spheres-instantianing-and-draw-calls/)
13. [React Three Fiber Scaling Performance](https://docs.pmnd.rs/react-three-fiber/advanced/scaling-performance)
14. [Three.js Best Practices 2026](https://www.utsubo.com/blog/threejs-best-practices-100-tips)

### 2D vs 3D UX Research

15. [Investigating Crossing Perception in 3D Graphs](https://www.arxiv.org/pdf/2508.00950)
16. [Graph Perception in Immersive Environments](https://www.collaborative-ai.org/publications/zhang25_gd.pdf)
17. [Comparative Study 2D vs 3D Charts in VR](https://link.springer.com/article/10.1007/s12650-024-01033-6)
18. [User-Preferred Perspectives for 3D Graphs](https://arxiv.org/html/2506.09212)
19. [Transforming Graphs from 2D to AR 3D](https://www.frontiersin.org/journals/virtual-reality/articles/10.3389/frvir.2023.1155628/full)
20. [Immersive Analytics: Reconsidering 3D Value](https://link.springer.com/chapter/10.1007/978-3-030-01388-2_2)
21. [Force-Directed Immersive 3D Visualization](https://www.mdpi.com/2073-431X/13/8/189)

### WebXR and VR

22. [Working with Graphs in AR/VR](https://www.yworks.com/blog/graphs-in-ar-vr)
23. [Immersive Analytics Data Visualization](https://wear-studio.com/vr-ar-data-visualization/)
24. [WebXR Device API Explained](https://immersive-web.github.io/webxr/explainer.html)
25. [Top VR AR XR Use Cases 2026](https://threejsresources.com/vr/blog/top-vr-ar-xr-use-cases-in-2026-building-immersive-experiences-that-deliver-real-value)

### Comparison Articles

26. [JavaScript Graph Libraries Comparison](https://www.cylynx.io/blog/a-comparison-of-javascript-graph-network-visualisation-libraries/)
27. [SVG vs Canvas vs WebGL 2025](https://www.svggenie.com/blog/svg-vs-canvas-vs-webgl-performance-2025)
28. [Comparing Web Graphics Technologies](https://tapflare.com/articles/web-graphics-comparison-canvas-svg-webgl)

---

**Document Status:** ✅ Complete
**Next Steps:** Review with team, decide on 2D optimization roadmap
**Decision Required:** Approve continued 2D approach vs pivot to 3D
