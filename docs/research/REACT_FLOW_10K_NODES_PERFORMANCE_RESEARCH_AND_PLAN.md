# React Flow 10k-Node Performance — Research and Plan

**Sources (researched):**
- [React Flow official: Performance](https://reactflow.dev/learn/advanced-use/performance)
- [Medium: The ultimate guide to optimize React Flow project performance](https://medium.com/@lukasz.jazwa_32493/the-ultimate-guide-to-optimize-react-flow-project-performance-42f4297b2b7b) (Łukasz Jaźwa, Jan 2025)
- [Synergy Codes: Guide to optimize React Flow project performance (ebook)](https://www.synergycodes.com/blog/guide-to-optimize-react-flow-project-performance) (same author; 5 hints + debugging)
- [Liam ERD: Tuning edge animations for optimal performance](https://liambx.com/blog/tuning-edge-animations-reactflow-optimal-performance) (Junki Saito, Jan 2025)
- Reddit r/reactjs: “How to make a 10,000 node graph performant” — *summary from user-provided thread copy (Section 1.5)*
- [xyflow/xyflow GitHub Issue #3044: My app so laggy when use 10k nodes](https://github.com/xyflow/xyflow/issues/3044) (May 2023)

**Goal:** Align our graph stack with best practices so large graphs (hundreds–low thousands of nodes/edges) stay smooth and we have a clear path toward 10k-node scale if needed.

**Our context / constraints:** We have **highly interactive** and **high eye-candy** nodes (type-specific visuals, previews, badges, rich content), plus **many nodes and many edges**. So we face the worst of both worlds: each node is expensive (DOM, re-renders, interactivity, visuals), and we have scale. That makes per-node cost and total count both critical; the main levers are **strict caps**, **LOD** (simplified nodes at scale or when zoomed out), and **edge simplification** so we never render “many heavy nodes + many fancy edges” at once.

---

## 1. Research Summary

### 1.1 React Flow official (reactflow.dev)

| Topic | Recommendation |
|-------|----------------|
| **Memoization** | Node/edge components: `React.memo` or declare outside parent. Functions passed to `<ReactFlow>`: `useCallback`. Objects (e.g. `defaultEdgeOptions`, `snapGrid`): `useMemo`. |
| **Store access** | Do **not** subscribe to full `nodes`/`edges` in components that don’t need them. Any change (e.g. drag) updates those arrays → every such subscriber re-renders. Keep derived state (e.g. selected IDs) in separate store fields so only selection changes trigger re-renders. |
| **Large trees** | Use `node.hidden` to show a limited set of nodes and expand on demand (collapse/expand) instead of rendering the full tree. |
| **Styles** | For very large graphs, simplify: reduce animations, shadows, gradients on nodes/edges. |
| **Further reading** | Synergy Codes guide, edge animation tuning, “5 Ways to Optimize React Flow in 10 minutes” (YouTube). |

### 1.2 Medium — “Ultimate guide” (Łukasz Jaźwa)

**Why React Flow is sensitive to performance**

- Node position updates → internal state refresh → anything that depends on `nodes`/`edges` re-renders.
- Heavy children inside `<ReactFlow>` or components that depend on the full nodes/edges array cause big FPS drops (e.g. 100 nodes: 60 FPS → 10 FPS with one non-memoized handler).

**Four areas (with benchmarks on 100-node diagram):**

1. **`<ReactFlow>` props**
   - All props must be stable: objects with `useMemo`, functions with `useCallback`.
   - Example: adding `onNodeClick={() => {}}` (new ref every render) dropped FPS to 10 (default nodes) and 2 (heavy nodes).
   - **Conclusion:** Memoize every prop passed to `<ReactFlow>`.

2. **Dependencies on `nodes` / `edges`**
   - **Bad:** In a node component, `useStore(state => state.nodes.filter(...))` — re-runs on every store update (e.g. every drag tick) → all nodes re-render.
   - **Good:** Store “selected nodes” (or selected IDs) in a separate store field; node components subscribe only to that. Selection updates only when selection actually changes.
   - **Alternative:** Use Zustand `useShallow` (or `createWithEqualityFn` + `shallow`) so selectors that return arrays/objects only change reference when contents change.

3. **Custom node/edge components**
   - Wrap custom nodes and edges in `React.memo`. In the article’s test, this largely restored FPS even with a non-memoized `onNodeClick`.
   - For “heavy” node content (e.g. DataGrid), wrap the inner content in `memo` as well so it doesn’t re-render on every node position update.

4. **Zustand store access**
   - Selecting multiple fields with `useStore(state => [state.a, state.b])` creates a new array every time → unnecessary re-renders.
   - Use `useShallow` or create the store with `createWithEqualityFn(..., shallow)` so array/object selectors are compared by value.

### 1.3 Synergy Codes (ebook / blog)

Same author as Medium; reinforces the same five areas with benchmarks (100 nodes, default vs “heavy” DataGrid content):

- **#1–#4:** Same as Medium (ReactFlow props memoization, avoid nodes/edges dependencies, memo node/edge components, Zustand useShallow / createWithEqualityFn).
- **#5:** Ebook teaser mentions two additional hints plus “how to debug” and “how to identify performance bottlenecks” — not fully visible without download; safe to assume they align with official docs (collapse/hidden, simplify styles, measure FPS).

**Takeaway:** Treat “five hints” as the core checklist; debugging/bottleneck identification is Phase C in our plan.

### 1.4 Liam ERD — Edge animations (liambx.com)

**Problem:** React Flow’s built-in edge animation uses CSS `stroke-dasharray` (and `stroke-dashoffset`). With hundreds of animated edges (e.g. 100+ tables, many relationships), this causes high CPU usage and frame drops. Chromium/svg.js issues confirm `stroke-dasharray` animation is a known bottleneck.

**Solution (Liam ERD):**
1. **Disable** React Flow’s `animated` prop on edges (no `stroke-dasharray`).
2. **Remove** `stroke-dasharray` from default edge styling entirely.
3. **Custom edge:** Use a `CustomEdge` that draws a static path (`BaseEdge`) and, only when needed (e.g. “highlighted”), animates **particles** along the path via SVG `<animateMotion>` with a small number of ellipses (e.g. 6) and a fixed duration (e.g. 6s). See [React Flow: Animated SVG Edge](https://reactflow.dev/components/edges/animated-svg-edge).

**Result:** Frame drops reduced (e.g. “5 frames at a time” → “2–3 frames” in their tests). Same “flow” feel with less CPU.

**Implication for us:** We already cap “animated” edges to ~20. For 10k-scale or if we want more “flow” without cost: consider a custom edge type that uses `<animateMotion>` particles only for highlighted/selected edges, and keep all other edges non-animated (no `stroke-dasharray`).

### 1.5 Reddit “10k node graph performant” — Thread summary

**Source:** [r/reactjs: How to make a 10,000 node graph performant](https://www.reddit.com/r/reactjs/comments/1epvcol/how_to_make_a_10000_node_graph_performant/) (1y ago). OP: notetaking app → shared knowledge graph (GraphRAG-style); using Neo4j nvl; laggy north of ~1k nodes; asking for libraries or techniques for 10k+ nodes.

**Attributed points from the thread:**

| Commenter | Point | Our relevance |
|-----------|--------|----------------|
| **Cannabat** | Most solutions will have perf issues at 10k. Ideas: (1) only render what is onscreen, (2) when zoomed out far enough that the user can’t read nodes, render a simplified version, (3) if using a canvas renderer, consider moving it to a web worker. | Viewport culling + LOD (simplified nodes when zoomed out) + worker for canvas. |
| **Cannabat** (follow-up) | Hierarchical LOD: instead of full content/interactivity, render a simplified version (e.g. plain rectangle). | Matches our “simplify node styles at scale” and collapse/expand. |
| **bzbub2** | The number of nodes is often not really the problem; it’s the **physics-based force layout simulations** (per-tick recompute). | Layout once, not every tick; precompute or run in worker. |
| **SolarNachoes** | WebGL can push millions of triangles with hardware acceleration. | Alternative stack for extreme scale (Phase D). |
| **vozome** | Product has 10k+ node graph, relatively smooth. Bottlenecks: (1) **Layout once** — don’t recompute positions continuously (every tick); no interactive repositioning that triggers full recompute. (2) **Canvas** (not WebGL): possible to draw tens of thousands of shapes without dropping a frame with **simplest composition** (no transparency, filters at scale). (3) Several **layered canvases** — some static, some more interactive. (4) **Only draw what’s on screen**; mini map; **level-of-detail** (only paint nodes/edges above a certain size). (5) Possible to draw ~30k shapes on canvas if needed. | Layout once, canvas, viewport culling, LOD, layered rendering. |
| **entropythagorean** | WebGL is almost certainly the right tool; **instanced drawing** for similar objects with slightly different properties (e.g. position). | Phase D option. |
| **CauliPicea** | Map with “locations of interest” (graph-like). React + SVG fine for hundreds, laggy at thousands. Tried viewport hiding and clustering; **un/hiding nodes in DOM was too time-expensive**. Would redo with **canvas**; **Konva.js** (20k nodes demo) caught their eye. | DOM churn (mount/unmount) costly; canvas or keep DOM set stable. |
| **KapiteinNekbaard** | Is there value in showing 1000+ points? Can the user make sense of it? Consider **grouping** or **multi-step selection** (filtering/ordering) instead of showing everything. | UX: grouping, filtering, progressive disclosure. |
| **bzbub2** (follow-up) | d3fc million-point demo (point cloud); **pre-calculated layout** (e.g. UMAP), not interactive. For graphs: **pre-calculate layout** (e.g. graphviz) rather than per-tick force layout. d3-force, cytoscape.js similarly strained with per-tick force. | Precompute layout; avoid continuous force simulation. |
| **yksvaan** | Use a **custom renderer** and keep it **outside of React**. | Decouple heavy rendering from React tree. |
| **Others** | react-force-graph, Sigma.js, React Three Fiber mentioned as options. | Alternative libraries for 3D or dedicated graph rendering. |

**Synthesis for our plan:**

- **Layout:** Do layout **once** (or on a subset in a worker); never per-tick force simulation at 10k scale. Precompute when possible (e.g. server or worker).
- **Rendering:** Only draw/render **what’s on screen**; LOD when zoomed out (simplified nodes/shapes). DOM mount/unmount (hide/show) can be expensive — prefer stable set + culling or canvas for very large sets.
- **Technology:** Canvas (simple composition, no transparency/filters at scale) can do tens of thousands of shapes; WebGL/instanced for millions. React + DOM has a lower ceiling; custom renderer “outside React” is a valid direction for 10k+.
- **UX:** Grouping, filtering, multi-step selection so the user isn’t overwhelmed; question whether showing 10k nodes at once is useful.

### 1.6 xyflow/xyflow GitHub Issue #3044 — “My app so laggy when use 10k nodes”

**Source:** [xyflow/xyflow#3044](https://github.com/xyflow/xyflow/issues/3044) (opened May 2023, closed). User: tuannguyenhoangit-droid.

**Setup:**
- 100×100 matrix → **10k nodes**; custom node type with **2 handles each** (source + target) → **20k handles**.
- Nodes: `type: 'point'`, `draggable: false`, `selectable: false`, 1×1 px, transparent; custom `Point` component wrapped in `React.memo`.
- Edges: `edges={[...edges, ...projectRuns, ...autoRuns]}`; `fitView`; `minZoom={0.5}`; `<Background variant="dots" />`.

**Reported:** App is laggy; asking for suggestions to improve performance.

**Takeaways for our plan:**
- **Same scale:** 10k nodes in React Flow is a reported pain point in the official repo; confirms that “10k in DOM” is a known ceiling.
- **Handle count:** 2 handles per node doubles the number of connection points React Flow manages (20k handles); each handle is DOM + internal state. Reducing handles or using a single handle type where possible can help.
- **Minimal nodes still lag:** Even with 1×1 transparent nodes and `React.memo`, 10k nodes + edges + fitView + background caused lag — reinforces that DOM count and store updates (e.g. on fitView) are the bottleneck, not node “heaviness” alone.
- **Alignment:** Our approach (cap rendered nodes/edges, viewport culling, LOD, progressive batching) is consistent with avoiding “render 10k at once”; the issue has no official “use this API” reply in the fetched page, but the problem statement validates prioritizing caps and culling.

---

## 2. Current Codebase vs Recommendations

| Recommendation | Our status | Notes |
|----------------|------------|--------|
| Node/edge components memoized | ✅ | `RichNodePill`, `EpicNode`, `RequirementNode`, `TestNode`, `ExpandableNode`, `QAEnhancedNode`, `NodeDetailPanel` use `memo`. |
| `nodeTypes` stable reference | ✅ | `nodeRegistry.ts` exports `nodeTypes` at module scope (not created inside component). |
| Callbacks passed to ReactFlow memoized | ⚠️ | FlowGraphViewInner passes `onNodesChange` / `onEdgesChange` from `useNodesState` / `useEdgesState` (stable). Other handlers (e.g. `onNodeClick`) need to be checked for stability. |
| No components subscribing to full `nodes`/`edges` | ⚠️ | Need to audit: any `useStore`/React Flow hooks that take full nodes/edges and are used in frequently re-rendering components. |
| Collapse/expand (hidden nodes) | ⚠️ | We have expand/collapse UX; ensure we use `hidden` and limit rendered set for very large trees. |
| Viewport / culling | ✅ | We use viewport culling (and enhanced LOD culling) and cap initial nodes/edges; progressive batching capped at 400 nodes. |
| Simple node/edge styles at scale | ⚠️ | We limit animated edges (e.g. 20); **we have heavy nodes** (interactive + eye candy) so LOD node type (simplified when count/zoom) is a priority. |
| Zustand `useShallow` / shallow store | ❓ | React Flow uses its own store; we don’t control it. Our own store usage (if any) should follow the same shallow-selector rules. |

---

## 3. Plan (Expanded)

### Phase A — Quick wins (no UX change)

**Reference:** React Flow docs, Synergy Codes / Medium #1–#3.

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| A1 | **Audit ReactFlow props in `FlowGraphViewInner`** | List every prop passed to `<ReactFlow>` (handlers, objects). Ensure every handler is `useCallback` with stable deps; every object (`defaultEdgeOptions`, `snapGrid`, `style`, `fitViewOptions`, etc.) is `useMemo` or module-level constant. Fix any that create new refs on render. | No handler/object prop is created inline; React DevTools or profiler shows no unnecessary parent re-renders from prop identity change. |
| A2 | **Audit store/hook usage** | Grep for `useStore`, `useNodes`, `useEdges`, and any selector that returns `nodes`, `edges`, or `nodes.filter(...)` / `edges.filter(...)`. In components that re-render often (e.g. inside ReactFlow tree, sidebar that shows selection), replace with: (a) separate state (e.g. `selectedNodeIds`), or (b) selector that returns primitives and use shallow comparison. | No hot-path component subscribes to full `nodes`/`edges`; selection/derived state lives in dedicated state or shallow selector. |
| A3 | **Heavy node content** | Identify node types that render heavy content (tables, long lists, rich previews). Wrap that inner content in `React.memo`; ensure props are stable (e.g. only `node.data` fields that change when that node’s data changes). | Heavy node content does not re-render on drag/pan/zoom of other nodes. |
| A4 | **Edge animation strategy (Liam ERD)** | Document current: we cap “animated” edges to ~20. Option: for “highlighted” or “selected” edges only, use a custom edge type with SVG `<animateMotion>` particles (per Liam ERD) instead of `animated: true` (stroke-dasharray). Keep all other edges non-animated. | Decision documented; if custom edge is implemented, no `stroke-dasharray` on bulk edges. |

---

### Phase B — Structural (enables 10k-scale)

**Reference:** React Flow “collapse large node trees”, Reddit inferred themes (virtualize, worker, lazy load).

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| B1 | **Formalize “window” of nodes/edges** | Decide and document: (1) Keep current model: cap at 200 nodes / 250 edges at data layer + viewport culling + MAX_RENDERED_NODES 400; or (2) Add explicit “viewport window”: only pass nodes (and edges between them) whose layout bounds intersect viewport + padding; update window on pan/zoom with debounce. Implement (2) only if we need true 10k-node support. | Decision doc; if (2), `nodes`/`edges` passed to ReactFlow are derived from viewport + padding. |
| B2 | **Collapse/expand and `hidden`** | For tree-like data (e.g. epic → feature → story), ensure “collapsed” nodes are not in the rendered set: either (a) set `hidden: true` on those nodes and rely on React Flow, or (b) exclude them from the `nodes`/`edges` arrays we pass. Align with MAX_RENDERED_NODES and progressive batching so we never run layout on 10k nodes. | Expanding a node reveals children; collapsing hides them; layout never runs on more than capped subset. |
| B3 | **LOD node type (heavy nodes + many nodes)** | We have **highly interactive and high eye-candy nodes** plus many nodes/edges, so per-node cost is high. Add a **simplified node type** used when (a) total node count &gt; threshold (e.g. 100), or (b) zoom &lt; threshold (zoomed out). Simplified type: minimal DOM (small pill + label only), no previews/badges, reduced hover/click. Map to `simplePill` (or compact `RichNodePill`) in `getNodeType` when LOD holds; keep full type for focused/selected or when count/zoom allows. **LOD × state (loading/error) skeletons:** see [SKELETON_AND_LOD_DESIGN.md](../guides/SKELETON_AND_LOD_DESIGN.md) (varying LOD skeletons by distance + loading/errored/other). | When graph is "at scale", nodes render as simple pills; zoom in or reduce count restores full node type. |
| B4 | **Layout at scale** | Options: (1) Keep layout on main thread on capped subset (current); (2) Move layout to Web Worker, post message with node/edge payload, apply positions in one batch; (3) Server-side precomputed layout for known large graphs, load by viewport. Evaluate (2) if layout becomes the bottleneck (e.g. &gt;500 nodes). | Decision doc; if (2), worker API and batch apply implemented and tested. |
| B5 | **Lazy load by viewport (optional)** | If we adopt a viewport window (B1), consider API support: e.g. `GET /items?project_id=…&viewport=…` or “load next slice” when user pans near boundary. Keeps initial payload small and aligns with “don’t load 10k at once” (Reddit theme). | If implemented, graph fetches only data for current viewport (or current window). |

---

### Phase C — Polish and monitoring

**Reference:** React Flow “simplify styles”, Liam ERD (edge animation), Synergy Codes “debug / identify bottlenecks”.

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| C1 | **Edge animation and styles at scale** | When node count or edge count exceeds a threshold (e.g. 500 nodes or 1000 edges), optionally: disable edge labels, set `animated: false` for all edges, or switch to simpler edge type (e.g. straight line). Optionally use custom particle edge only for “highlighted” edges (Phase A4). | No stroke-dasharray on large graphs; optional LOD for edge complexity. |
| C2 | **Performance budget and metrics** | Define a target (e.g. “≥ 30 FPS during pan/zoom with 2k nodes, 3k edges” or “time to first frame &lt; 2s for 500 nodes”). Optionally add a small dev-only FPS or timing logger when loading the graph view. | Target documented; optional dev metrics in place. |
| C3 | **Debugging and bottleneck identification** | Document how to profile: React DevTools (re-renders), Chrome Performance (layout/paint), and what to look for (store subscriptions, layout duration, edge count). Link to Synergy Codes ebook or internal runbook. | Short “Graph performance debugging” section in docs. |
| C4 | **Documentation** | Add a “Graph performance” section (e.g. in `docs/guides/` or README) that states: caps (200 nodes, 250 edges at data layer; 400 max rendered nodes); viewport culling thresholds; that we follow React Flow best practices (memoized components/props, no full nodes/edges in hot path, collapse/expand + hidden); and link to this research doc. | Discoverable doc for future maintainers. |

---

### Phase D — 10k-scale (if required)

**Reference:** Reddit inferred themes (virtualize, worker, canvas), React Flow stress example.

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| D1 | **Viewport-based node set** | Implement strict virtualization: only nodes whose position (after layout) falls in viewport + padding are in the `nodes` array passed to ReactFlow. Edges only between those nodes. Layout either (a) runs on a superset (e.g. visible + one hop) in worker, or (b) we use precomputed positions. | Pan/zoom updates node/edge set; never pass 10k nodes to ReactFlow. |
| D2 | **Layout in Web Worker** | Move ELK/Dagre (or equivalent) to a Web Worker; receive node/edge payload, return positions; main thread applies in one update. Use for layout subset (e.g. visible window) to avoid blocking UI. | Layout runs off main thread; UI stays responsive during layout. |
| D3 | **Canvas or hybrid (last resort)** | Only if DOM remains the bottleneck after D1–D2: explore canvas-based edge rendering or canvas overlay for “far” nodes (e.g. simple shapes), keeping DOM nodes only for “near” viewport. Large architectural change. | Documented POC or decision to defer. |

---

## 4. Reddit thread (summary in 1.5)

Section 1.5 contains an **attributed summary** of the r/reactjs thread “How to make a 10,000 node graph performant,” including: layout once (no per-tick force), only render on-screen, LOD when zoomed out, canvas/WebGL for scale, layered canvases, avoiding DOM mount/unmount churn, precomputed layout, and UX (grouping, filtering). The expanded plan (Phases B–D) aligns with these points.

---

## 5. Summary

- **Our context:** We have **highly interactive and high eye-candy nodes** plus **many nodes and many edges**. Per-node cost is high, so we must combine strict caps with **LOD** (simplified node type at scale or when zoomed out) and edge simplification so we never render “many heavy nodes + many fancy edges” at once.
- **Already in good shape:** Memoized node components, stable `nodeTypes`, viewport culling, progressive batching with caps (MAX_RENDERED_NODES 400), limited edge animation (~20), silent data caps (200 nodes, 250 edges).
- **Research added:** Synergy Codes (same 5 hints as Medium + debugging); Liam ERD (stroke-dasharray CPU cost, custom particle edge via `<animateMotion>`); Reddit thread summary (layout once, only render on-screen, LOD, canvas/WebGL, avoid DOM churn, precompute layout, grouping/filtering UX); xyflow #3044 (10k-node lag, 20k handles).
- **Plan expanded:** Phase A (quick wins: props audit, store audit, heavy content memo, edge animation strategy); Phase B (structural: window of nodes, collapse/hidden, **B3 LOD node type** for heavy nodes at scale, layout at scale, optional viewport API); Phase C (polish: edge styles at scale, perf budget, debugging doc, graph performance doc); Phase D (10k-scale: viewport-based node set, layout in worker, canvas/hybrid as last resort).
- **Next steps:** Execute Phase A (A1–A4), then Phase B (B1–**B3 LOD node type**–B4) as needed; Phase C for docs and optional metrics; Phase D only if product requires true 10k-node support.
- **Target:** Smooth interaction for hundreds–low thousands of nodes today despite heavy nodes; LOD node type (simple pills when count/zoom is high) is the main lever for “many interactive + eye-candy nodes + many edges”; clear path to 10k-node scale (viewport window + culling + optional worker layout + optional custom edge animation) without big UX change.

---

## 6. Source → Plan reference

| Source | Plan items |
|--------|------------|
| React Flow official | A1 (memoization), A2 (store), B2 (collapse/hidden), C1 (simplify styles) |
| Synergy Codes / Medium | A1–A3 (props, store, memo), A2 (Zustand useShallow), C3 (debugging) |
| Liam ERD | A4 (edge animation strategy), C1 (no stroke-dasharray at scale) |
| Reddit (thread summary) | B1 (viewport / only render on-screen), B2 (LOD / simplified nodes when zoomed out), B3 (layout once, worker, precompute), C1 (LOD), D1–D3 (viewport window, worker, canvas/WebGL); avoid DOM mount/unmount churn (stable set + culling). |
| React Flow Stress example | Reference: simple stress test with `initialElements(n, m)`; no virtualization. |
| xyflow/xyflow #3044 | Validates 10k-node lag in official repo; 20k handles (2 per node) as extra cost; reinforces B1 (caps/culling), C1 (minimize DOM/handles). |
