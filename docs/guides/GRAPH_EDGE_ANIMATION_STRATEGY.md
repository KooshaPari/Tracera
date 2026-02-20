# Graph Edge Animation Strategy (A4)

**Goal:** Document how we handle edge animation for performance and optionally use a custom particle edge for highlighted edges only.

---

## Current behavior

- **FlowGraphViewInner:** We cap **animated** edges at **20** (`maxAnimatedEdges = 20`). Only the first 20 edges that are `depends_on` or `blocks` get `animated: true`; all others get `animated: false`. This avoids GPU/CPU overload from many simultaneous CSS animations.
- **Style:** Animated edges use React Flow’s default animated edge (e.g. `stroke-dasharray` / `stroke-dashoffset`). Dashed edges use `strokeDasharray: "5,5"`.
- **Other views:** FlowGraphView, VirtualizedGraphView, PageInteractionFlow use similar patterns (animated for certain link types, sometimes disabled for large graphs).

---

## Why cap animation?

- **Liam ERD / Chromium:** Animating many edges with `stroke-dasharray` is a known CPU bottleneck. With 100+ animated edges, frame rate can drop.
- **Our stance:** We keep bulk edges non-animated and limit animated edges to ~20 so the graph stays smooth.

---

## Optional future: custom particle edge (Liam ERD pattern)

- **Idea:** For **highlighted** or **selected** edges only, use a custom edge type that animates **particles** along the path via SVG `<animateMotion>`, instead of `animated: true` (stroke-dasharray).
- **Benefit:** Same “flow” feel for the few edges the user cares about, without the cost of animating many edges.
- **Reference:** [Liam ERD – Tuning edge animations](https://liambx.com/blog/tuning-edge-animations-reactflow-optimal-performance); [React Flow – Animated SVG Edge](https://reactflow.dev/components/edges/animated-svg-edge).
- **Implementation:** Add a custom edge type (e.g. `particleEdge`) that draws a static path with `BaseEdge` and, when “highlighted”, renders a small number of ellipses with `<animateMotion>` along the path. Use this type only for edges in a “highlighted” or “selected” set; keep all other edges with `animated: false` and no `stroke-dasharray` animation.

---

## Decision

- **Current:** Cap at 20 animated edges; no `stroke-dasharray` on the rest. No custom particle edge yet.
- **If we add “highlight path”:** Prefer a custom particle edge for highlighted edges only; do not increase the number of edges using `animated: true` / stroke-dasharray.

---

## Related

- [REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md](../research/REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md) — Phase A4, Phase C1.
- [SKELETON_AND_LOD_DESIGN.md](./SKELETON_AND_LOD_DESIGN.md) — Checklist Phase 0 (A4).
