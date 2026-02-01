# Graph Performance — Caps, Window, Layout, LOD

**Goal:** Document decisions for node/edge caps, viewport window, collapse/hidden, and layout at scale (B1, B2, B4, B5).

**Related:** [REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md](../research/REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md), [SKELETON_AND_LOD_DESIGN.md](./SKELETON_AND_LOD_DESIGN.md).

---

## B1 — Window of nodes/edges

**Decision:** Keep **current model**. We do **not** implement a strict viewport window (only nodes whose layout bounds intersect viewport + padding).

**Current model:**
- **Data layer (GraphView):** Cap at **200 nodes** and **250 edges** (`MAX_NODES`, `MAX_EDGES`). `visibleItems` = `items.slice(0, MAX_NODES)`; `visibleLinks` = edges between those nodes, sliced to `MAX_EDGES`. No "load more" or counts shown.
- **Rendering (FlowGraphViewInner):** Viewport culling when `visibleLinks.length > 200`; enhanced LOD culling when `visibleLinks.length >= 500`. Progressive node batching with **MAX_RENDERED_NODES = 400**.
- **LOD:** When node count ≥ 100, nodes use simplified type (`simplePill`). Zoom-based LOD is in node `data.lodLevel` for future loading/error skeletons.

**D1 Viewport window (implemented):** When node count > 100, we only pass nodes whose position is inside viewport + padding (200 flow units). Viewport bounds are updated on pan/zoom (`onMoveEnd`). Edges are filtered to those between nodes in the viewport window. Initial viewport is set after first layout (300ms) so we don’t wait for user move.

---

## B2 — Collapse/expand and hidden

**Current behavior:**
- **expandedNodes:** Drives per-node **UI expand** (e.g. expand preview in RichNodePill). It does **not** remove nodes from the rendered set.
- **Rendered set:** All nodes up to the caps (visibleNodes from filteredNodes, capped by MAX_RENDERED_NODES) are in the set we pass to React Flow. We do not set `node.hidden` or exclude nodes by tree collapse.

**Decision:** Keep current behavior. **Tree collapse** (e.g. epic → feature → story: collapsed parent hides children from the graph) is **deferred**. When we add it:
- Either set `hidden: true` on collapsed descendants and rely on React Flow, or
- Exclude collapsed descendants from the `nodes`/`edges` arrays we pass (e.g. filter visibleNodes by "visible in tree" so layout never runs on 10k nodes).

---

## B4 — Layout at scale

**Decision:** Keep layout on the **main thread** on the capped subset (current). We do **not** move layout to a Web Worker or server yet.

**Current:** DAG layout (Dagre/ELK-style) runs in `useDAGLayout` on `nodesForLayout` (capped visible nodes) and `visibleLinks`. Layout runs when layout type, node set, or edge set changes.

**D2 Layout in worker (implemented):** When node count > 150 and layout is ELK (flow-chart, timeline, tree), layout runs in a Web Worker (`graphLayout.worker.ts`). Main thread posts nodes/edges/options and receives positions; applies in one update. Falls back to main-thread ELK if Worker is unavailable.

**Future:** Server-side precomputed layout for known large graphs remains optional.

---

## D3 — Canvas / hybrid rendering (implemented)

When zoom is at Far or VeryFar (zoom &lt; 0.5) and node count &gt; 50, far-LOD nodes are drawn on a canvas overlay instead of as DOM nodes. React Flow receives no nodes (or only near-LOD nodes); a canvas layer draws small circles for each far node using the same viewport transform. This reduces DOM count when zoomed out and keeps pan/zoom responsive. Canvas is `pointer-events-none` so interaction goes to React Flow.

---

## B5 — Lazy load by viewport (optional)

**Decision:** **Not implemented.** We do not fetch data by viewport (e.g. `GET /items?project_id=…&viewport=…`) or "load next slice" on pan.

**Current:** Graph fetches items and links with fixed pagination (e.g. first 200 items, first 250 edges); caps are applied client-side.

**Future:** If we adopt a viewport window (B1), we could add API support to fetch only data for the current viewport or a "window" around it.

---

## C2 — Performance budget and metrics

**Targets (informal):**
- **Initial render:** Graph visible within ~2s on mid-range devices after data load.
- **Pan/zoom:** ≥ 30 FPS during interaction; aim for 55+ FPS when possible.
- **Caps:** 200 nodes / 250 edges (data); up to 400 nodes rendered (viewport culling).

**Optional dev tooling:**
- In development, `FlowGraphViewInner` can show a small FPS/timing panel when `NODE_ENV === "development"` and a performance monitor is enabled (see `GRAPH_PERFORMANCE_MONITORING.md`).
- No formal performance budget gates in CI today; consider adding Lighthouse or custom FPS assertions if regressions appear.

---

## C3 — Debugging and bottleneck identification

**Profiling techniques:**
1. **Chrome DevTools Performance:** Record while panning/zooming; look for long tasks, layout thrash, or excessive React commits.
2. **React DevTools Profiler:** Identify components re-rendering on pan/zoom; ensure node components are memoized and stable props are used (see A1–A3).
3. **React Flow:** Avoid `useStore` in hot paths; prefer `selectedNodeId` + derived state. Check that `nodeTypes` and callback props (`onNodeClick`, etc.) are stable (e.g. `useMemo` / `useCallback`).
4. **Edge animation:** If FPS drops, verify animated edge count is capped (C1: 0 at scale, else max 20). See [GRAPH_EDGE_ANIMATION_STRATEGY.md](./GRAPH_EDGE_ANIMATION_STRATEGY.md).
5. **Layout:** If layout runs too often or takes >100ms, inspect `useDAGLayout` dependencies and consider deferring worker layout (B4).

---

## C4 — Graph performance: caps, culling, best practices

**Caps and culling (quick reference):**

| Layer | Cap / behavior |
|-------|-----------------|
| Data (GraphView) | 200 nodes, 250 edges; no "load more" UI. |
| Rendering | Viewport culling when links > 200; enhanced LOD culling when links ≥ 500; max 400 nodes rendered. |
| At scale (500+ nodes or 1000+ edges) | No edge animation; no edge labels (C1). |
| Node count ≥ 100 | Simplified node type (`simplePill`); zoom-based LOD in `data.lodLevel`. |

**Best practices:**
- Keep ReactFlow props stable: `proOptions`, `onNodeClick`, `onFitView`, etc. via `useMemo`/`useCallback`.
- Heavy node content (e.g. image/iframe preview) in a memoized sub-component to avoid re-renders on pan/zoom.
- Do not use React Flow `useStore` in a way that subscribes the whole tree to store changes; use explicit selection/derived state.
- Prefer LOD-shaped loading/error skeletons (see [SKELETON_AND_LOD_DESIGN.md](./SKELETON_AND_LOD_DESIGN.md)) so empty/loading states stay cheap at high zoom-out.

---

## Summary

| Item | Decision |
|------|----------|
| B1 Window | Keep 200/250 caps + culling + 400 max rendered; viewport window deferred. |
| B2 Collapse/hidden | expandedNodes = UI expand only; tree collapse deferred. |
| B4 Layout | Main thread on capped subset; worker/server deferred. |
| B5 Viewport API | Not implemented; optional future. |
| C2 Budget | Informal: ~2s initial, ≥30 FPS; optional dev FPS panel. |
| C3 Profiling | Chrome Performance, React Profiler, stable props, edge cap. |
| C4 Best practices | Stable props, memoized heavy content, no hot-path useStore, LOD skeletons. |
