# Skeleton and LOD Design — Skeletons for Everything, LOD by Distance, State-Based Variants

**Goal:** Plan skeletons for **everything** (views, lists, graph nodes, cards), with **varying LOD skeletons** (by distance/zoom) and **varying skeletons by state** (loading, errored, empty, normal). This doc defines scope, LOD levels, state matrix, and what’s already in place vs planned.

**Related:**
- [REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md](../research/REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md) — B3 LOD node type (simplified node when count/zoom is high).
- [RESEARCH_CANVAS_GRAPH_RENDERING.md](../research/RESEARCH_CANVAS_GRAPH_RENDERING.md) — LOD levels (VeryFar → VeryClose) and `determineLODLevel(zoom)`.
- `frontend/apps/web/src/lib/lazy-loading.tsx` — `ChunkLoadingSkeleton`, `ListLoadingSkeleton`, `ChunkErrorFallback`.

---

## 1. Scope — “Skeletons for Everything”

| Area | What we show | Loading skeleton | Error skeleton | Empty skeleton | LOD / distance |
|------|----------------|------------------|----------------|----------------|----------------|
| **Route / chunk** | Whole screen while lazy load | ✅ `ChunkLoadingSkeleton` | ✅ `ChunkErrorFallback` | — | — |
| **List / table** | Rows, filters | ✅ `ListLoadingSkeleton` | ⚠️ Ad-hoc or retry | Optional empty state | — |
| **View (graph, dashboard, etc.)** | Header + main content | ✅ Ad-hoc `Skeleton` blocks (e.g. GraphView, FlowGraphView) | ⚠️ Ad-hoc or none | View-specific empty | — |
| **Graph nodes** | Each node on canvas | ❌ No per-node loading | ❌ No per-node error | — | ⚠️ Planned (B3 LOD node type) |
| **Cards / items** | Item detail, thumbnails | ✅ `Skeleton` in ItemDetailView, ThumbnailPreview | ⚠️ Ad-hoc | Optional | — |

**Gaps:**
- **Graph node–level** loading skeleton (node data loading).
- **Graph node–level** error skeleton (node failed to load or errored).
- **LOD-by-distance** for graph nodes: varying representation by zoom (far = minimal, near = full).
- **Unified** error/empty skeletons for lists and cards (optional; many views already have ad-hoc).

**Planned:** Graph node LOD (B3 in performance doc) plus **node-level loading/error skeletons** and **LOD × state matrix** below.

---

## 2. LOD Levels (By Distance / Zoom)

Align with research: zoom determines how much detail we care about. Same entity can be shown at different **LOD skeletons** (simplified shapes when far).

| LOD level | Zoom range | Use when | Graph node representation (content) | Graph node representation (loading) | Graph node representation (error) |
|-----------|------------|----------|--------------------------------------|--------------------------------------|------------------------------------|
| **VeryFar** | &lt; 0.2 | User can’t read labels | Dot or 2–4 px circle (no label) | Tiny shimmer dot | Tiny red/error dot |
| **Far** | 0.2–0.5 | Labels not readable | Minimal pill (e.g. 8×4 px), no badges | Minimal pill skeleton (shimmer) | Minimal error pill |
| **Medium** | 0.5–1.0 | Some context | Compact pill (label only, no preview) | Compact pill skeleton | Compact error pill (icon + short message) |
| **Close** | 1.0–2.0 | Readable | Full pill (label + badges, no heavy preview) | Full pill–shaped skeleton | Full error pill/card |
| **VeryClose** | &gt; 2.0 | Full detail | Full node (all eye candy, previews, interactivity) | Full node–shaped skeleton | Full error card/callout |

**Implementation note:** LOD can be driven by (a) **zoom** only, (b) **zoom + node count** (e.g. force Medium/Far when node count &gt; 100), or (c) **viewport distance** (distance from node to viewport center). B3 in the performance doc uses (a)+(b). Distance-based (c) is optional for later.

---

## 3. States (Loading, Errored, Empty, Normal)

Every place that shows content can be in one of these states. Skeletons vary by state.

| State | Meaning | Typical skeleton / UI |
|-------|--------|-------------------------|
| **Loading** | Data or chunk is loading | Shimmer / pulse skeleton (shape matches final content where possible). |
| **Errored** | Load failed or item is in error state | Error placeholder (icon + short message, optional retry). |
| **Empty** | No data (e.g. no items in list) | Empty state (message + optional CTA). Optional “empty skeleton” is usually not used; we show a clear empty state instead. |
| **Normal** | Content loaded and valid | Full content (or LOD-reduced content when far). |

**Varying skeletons:** For each **context** (e.g. graph node, list row, card), we can define a skeleton **per state** (loading, error) and **per LOD** when applicable (graph nodes). So: **LOD × State → skeleton variant**.

---

## 4. LOD × State Matrix (Graph Nodes)

For **graph nodes** we want both LOD-by-distance and state-based skeletons.

|  | **Loading** | **Errored** | **Empty** (N/A per node) | **Normal** |
|--|-------------|-------------|---------------------------|------------|
| **VeryFar** | Tiny shimmer dot | Tiny error dot | — | Dot (no label) |
| **Far** | Minimal pill shimmer | Minimal error pill | — | Minimal pill (no label) |
| **Medium** | Compact pill skeleton (label placeholder) | Compact error pill (icon + “Error”) | — | Compact pill (label only) |
| **Close** | Full pill skeleton (label + badge placeholders) | Full error pill (message + retry) | — | Full pill (label + badges) |
| **VeryClose** | Full node skeleton (shape of RichNodePill / type-specific) | Full error card (message + retry) | — | Full node (all content) |

**Other contexts (lists, cards):** Usually no LOD; only state matters (loading skeleton, error fallback, empty state). List row: loading = row-shaped skeleton; error = row-level error + retry; empty = “No items” message.

---

## 5. What Exists vs What’s Planned

### 5.1 Already in place

- **Route/chunk:** `ChunkLoadingSkeleton`, `ChunkErrorFallback` (`lazy-loading.tsx`).
- **List/table:** `ListLoadingSkeleton`; many views use ad-hoc `Skeleton` grids for loading.
- **View-level graph:** `GraphView`, `GraphViewContainer`, `FlowGraphView`, `EnhancedGraphView` use full-view loading (header + large canvas `Skeleton`).
- **UI primitive:** `Skeleton` in `@tracertm/ui` (shimmer + pulse).
- **ThumbnailPreview:** Uses `Skeleton` while image loads.
- **Research:** LOD levels and `determineLODLevel(zoom)` in RESEARCH_CANVAS_GRAPH_RENDERING.md; B3 LOD node type in REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md.

### 5.2 Planned (skeletons for everything + LOD + state)

| Item | Description |
|------|-------------|
| **Graph node loading skeleton** | Per-node skeleton while node data is loading (shape matches LOD: dot / minimal pill / compact pill / full pill / full node). |
| **Graph node error skeleton** | Per-node error placeholder (icon + message, optional retry) at each LOD level (tiny dot → full card). |
| **LOD node type (B3)** | Simplified node type when zoom &lt; threshold or node count &gt; threshold: use compact/simple pill so “normal” content is already a lighter LOD; aligns with “varying LOD skeletons” (far = simple, near = full). |
| **LOD × state wiring** | When rendering a node: (1) resolve LOD from zoom (and optionally node count); (2) resolve state (loading / errored / normal); (3) pick skeleton or content from matrix (e.g. VeryFar + Loading → tiny shimmer dot). |
| **Unified list/card error** (3.2) | Implemented: `ListItemErrorFallback` and `CardErrorFallback` in `@/lib/lazy-loading`. Wired in AdvancedSearchView (search error) and LinksView (load error). |
| **Empty states** | Already present in many views; ensure graph has an explicit empty state when there are no nodes/edges. |

---

## 6. Summary

- **Skeletons for everything:** Route and list and view-level loading/error are covered; **graph node–level** loading and error skeletons are planned, plus optional standardization for list/card errors.
- **Varying LOD skeletons:** By **distance/zoom** we show different detail (VeryFar → VeryClose: dot → minimal pill → compact pill → full pill → full node). Same idea for loading and error: **varying skeletons** per LOD (e.g. loading at VeryFar = tiny shimmer dot; at VeryClose = full node-shaped skeleton).
- **Varying skeletons by state:** **Loading** (shimmer), **Errored** (error placeholder with optional retry), **Normal** (content, possibly LOD-reduced). Empty is handled by empty states, not a skeleton.
- **Matrix:** For graph nodes, **LOD × State** determines which skeleton or content we show; for lists/cards, **State** alone usually suffices.
- **Next steps:** Use the ordered implementation checklist in §7 below.

---

## 7. Implementation Checklist (Ordered Tasks) — Perf + Skeleton/LOD

All items from [REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md](../research/REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md) are merged here. Execute in phase order.

### Phase 0 — Perf quick wins (no UX change)

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| A1 | **Audit ReactFlow props in FlowGraphViewInner** | Every handler `useCallback`, every object `useMemo` or module constant. No inline refs. | No unnecessary re-renders from prop identity. |
| A2 | **Audit store/hook usage** | No hot-path component subscribes to full `nodes`/`edges`; use `selectedNodeIds` or shallow selectors. | Selection/derived state in dedicated state or shallow selector. |
| A3 | **Heavy node content** | Wrap heavy inner content in `React.memo`; stable props. | Heavy node content does not re-render on drag/pan/zoom of others. |
| A4 | **Edge animation strategy** | Document: cap animated edges ~20; option custom particle edge for highlighted only (Liam ERD). | Decision documented; no `stroke-dasharray` on bulk edges. |

### Phase 1 — LOD foundation (graph nodes)

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| 1.1 | **LOD level helper** | `determineLODLevel(zoom[, nodeCount])` in graph utils; LOD enum (VeryFar … VeryClose). | Single source of truth; used by node type and skeleton selection. |
| 1.2 | **B3: Simplified node type at scale** | When LOD Far or coarser, or node count &gt; threshold: use `simplePill` (label only). Wire in `getNodeType`. | At scale, nodes render as simple pills; zoom in restores full type. |
| 1.3 | **LOD-aware node render path** | Each node receives `lodLevel` (in `data` or context from viewport zoom + count). | All nodes have current LOD for matrix. |

### Phase 2 — Perf structural (B1, B2, B4, B5)

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| B1 | **Formalize window of nodes/edges** | Decide: keep 200/250 caps + culling + 400 max rendered; or viewport window. Document. | Decision doc; if viewport window, implement. |
| B2 | **Collapse/expand and hidden** | Collapsed nodes not in rendered set (`hidden: true` or exclude from arrays). | Expand/collapse works; layout never on 10k. |
| B4 | **Layout at scale** | Decide: main thread (current), worker, or server precompute. Evaluate worker if &gt;500 nodes. | Decision doc; if worker, implement. |
| B5 | **Lazy load by viewport** (optional) | If B1 viewport window: API e.g. `GET …?viewport=…` or load-next-slice. | If implemented, graph fetches by viewport. |

### Phase 3 — Node-level loading and error skeletons

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| 2.1 | **Graph node loading skeleton** | LOD-shaped loading (dot → minimal pill → … → full node skeleton). | Node loading shows correct LOD skeleton. |
| 2.2 | **Graph node error skeleton** | LOD-shaped error placeholder (tiny dot → … → full card + retry). | Node error shows correct LOD error UI. |
| 2.3 | **Wire state per node** | Derive loading \| errored \| normal; (LOD, state) → skeleton or content. | LOD × state matrix wired. |

### Phase 4 — Perf polish and monitoring

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| C1 | **Edge animation/styles at scale** | At high node/edge count: disable labels, `animated: false`, or simpler edge type. | No stroke-dasharray on large graphs. |
| C2 | **Performance budget and metrics** | Target e.g. ≥30 FPS pan/zoom; optional dev FPS/timing logger. | Target documented; optional metrics. |
| C3 | **Debugging and bottlenecks** | Doc: React DevTools, Chrome Performance, what to look for. | "Graph performance debugging" section. |
| C4 | **Documentation** | "Graph performance" section: caps, culling, best practices, link to research doc. | Discoverable for maintainers. |

### Phase 5 — Skeleton/LOD polish

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| 3.1 | **Graph empty state** | Explicit empty state when no nodes/edges. | No blank canvas. |
| 3.2 | **Unified list/card error** (optional) | `ListItemErrorFallback` / `CardErrorFallback`; use in list/card views. | Consistent error placeholder. |
| 3.3 | **Docs and tests** | LOD × state in code; tests for LOD helper and node rendering. | Docs + tests. |

### Phase 6 — 10k-scale (if required)

| # | Task | Details | Acceptance |
|---|------|---------|------------|
| D1 | **Viewport-based node set** | Only nodes in viewport + padding in `nodes`; edges between them. | Never pass 10k nodes to ReactFlow. |
| D2 | **Layout in Web Worker** | ELK/Dagre in worker; main thread applies positions once. | Layout off main thread. |
| D3 | **Canvas or hybrid** (last resort) | Canvas for far nodes or edges if DOM still bottleneck. | POC or decision to defer. |

### Dependency order (summary)

```
Phase 0: A1 → A2 → A3 → A4
Phase 1: 1.1 → 1.2 → 1.3
Phase 2: B1 → B2 ; B4 ; B5(opt)
Phase 3: 2.1 + 2.2 → 2.3
Phase 4: C1 ; C2 ; C3 ; C4
Phase 5: 3.1 ; 3.2(opt) ; 3.3
Phase 6 (if needed): D1 → D2 ; D3(opt)
```

### Status (started)

- **A1** — Done: ReactFlow props memoized (`proOptions`, MiniMap `nodeColor`, `handleFit`, `handleReset`, `handleFocusNode`, `noop` for optional callback).
- **A2** — Done: Audited; no `useStore` in frontend; selection/derived state use `selectedNodeId` + `useMemo` (e.g. `selectedNode`, `incomingLinks`/`outgoingLinks` from `graphIndices`). No hot-path component subscribes to full `nodes`/`edges`.
- **1.1** — Done: `determineLODLevel`, `LODLevel`, `shouldUseSimplifiedNode`, `LOD_NODE_COUNT_THRESHOLD` in `frontend/apps/web/src/components/graph/utils/lod.ts`; exported from `utils/index.ts`.
- **1.2 B3** — Done: `SimpleNodePill` component; `simplePill` in nodeRegistry; `getNodeTypeWithLOD(itemType, nodeData, { nodeCount })` returns `"simplePill"` when `nodeCount >= LOD_NODE_COUNT_THRESHOLD` (100); FlowGraphViewInner uses `getNodeTypeWithLOD` when building `nodesForLayout`. At 100+ visible nodes, graph renders simple pills (label only); fewer nodes restore full type.
- **A3** — Done: `RichNodePillPreviewBlock` (memo) in RichNodePill for heavy content (preview image + widget iframe); props are stable so it does not re-render on pan/zoom of other nodes.
- **A4** — Done: [GRAPH_EDGE_ANIMATION_STRATEGY.md](./GRAPH_EDGE_ANIMATION_STRATEGY.md) documents cap at 20 animated edges, no stroke-dasharray on bulk edges, optional custom particle edge for highlighted only.
- **1.3** — Done: `lodLevel` computed from `determineLODLevel(zoom, { nodeCount })` and passed in each node’s `data.lodLevel` in FlowGraphViewInner; `RichNodeData.lodLevel` added. Nodes have access to current LOD for loading/error skeleton selection later.
- **B1** — Done: [GRAPH_PERFORMANCE.md](./GRAPH_PERFORMANCE.md) documents decision to keep 200/250 caps + culling + 400 max rendered; viewport window deferred.
- **B2** — Done: GRAPH_PERFORMANCE.md documents expandedNodes = UI expand only; tree collapse deferred; when we add it, use hidden or exclude collapsed descendants.
- **B4** — Done: GRAPH_PERFORMANCE.md documents layout on main thread; worker/server deferred; evaluate worker if >500 nodes.
- **B5** — Done: GRAPH_PERFORMANCE.md states viewport API not implemented; optional future.
- **2.1** — Done: NodeLoadingSkeleton (LOD-shaped); registered as nodeLoading.
- **2.2** — Done: NodeErrorSkeleton (LOD-shaped); registered as nodeError.
- **2.3** — Done: getNodeTypeWithLOD returns nodeLoading/nodeError when data.loading/data.error; FlowGraphViewInner uses getNodeTypeWithLOD and passes data.lodLevel.

---

