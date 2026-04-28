# Graph Visualization Libraries - Research Index

**Purpose:** Central index for all graph visualization library research
**Status:** Complete
**Last Updated:** 2026-02-01

---

## Research Documents

### Primary Documents

1. **[Comprehensive Comparison Matrix](./graph-libraries-comprehensive-comparison.md)** ⭐ MAIN DOCUMENT
   - Complete feature matrix for 15+ libraries
   - Performance tier classification
   - Migration complexity analysis
   - Hybrid architecture recommendations
   - ROI analysis and final recommendation
   - **Use for:** Architecture decisions, stakeholder presentations

2. **[Visual Decision Guide](./graph-libraries-decision-flowchart.md)**
   - One-page visual summary
   - Decision tree flowchart
   - Performance heat maps
   - Quick reference for meetings
   - **Use for:** Quick decisions, executive summaries

3. **[Implementation Checklist](../guides/quick-start/graph-library-implementation-checklist.md)**
   - 5-week implementation plan
   - Day-by-day tasks
   - Acceptance criteria
   - Risk mitigation
   - **Use for:** Project execution

---

## Supporting Research

### ReactFlow Optimization
- [ReactFlow 10k Nodes Research](./REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md)
  - Current performance analysis
  - Optimization techniques (Phase A-D)
  - LOD and viewport culling
  - Memory profiling

### WebGL/GPU Research
- [WebGL Graph Rendering (100k+)](./webgl-graph-rendering-100k.md)
  - PixiJS integration
  - Instanced rendering
  - Shader-based edges
  - Texture atlases
  - Hybrid rendering architecture

- [GPU Force Layout](../../frontend/apps/web/docs/architecture/gpu-force-layout.md)
  - WebGPU vs WebGL 2.0
  - Barnes-Hut algorithm on GPU
  - @antv/layout-gpu
  - GraphWaGu (state-of-the-art)

- [Web Worker Layout](../../frontend/apps/web/docs/architecture/web-worker-layout.md)
  - Off-main-thread computation
  - Comlink integration
  - Progressive layout
  - Performance benchmarks

### Sigma.js Specific
- [Sigma.js Evaluation](./sigma-js-evaluation.md)
  - Detailed feature analysis
  - Performance benchmarks
  - Migration effort estimate
  - Hybrid approach design

- [Sigma.js Quick Start](./sigma-js-quick-start.md)
  - Installation guide
  - Basic usage
  - Custom renderers
  - Event handling

- [Sigma.js Summary](./sigma-js-summary.md)
  - Executive summary
  - Key findings
  - Recommendation

- [Sigma Comparison Matrix](./sigma-comparison-matrix.md)
  - ReactFlow vs Sigma.js
  - Feature comparison
  - Cost-benefit analysis
  - Decision tree

---

## Quick Reference

### By Use Case

**Small Graphs (<10k nodes, rich interactions):**
- Current: ReactFlow ✅
- Optimize: [ReactFlow Performance Plan](./REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md)

**Medium Graphs (10k-50k nodes, mixed interactions):**
- Recommended: Hybrid (ReactFlow + Sigma.js)
- See: [Comprehensive Comparison](./graph-libraries-comprehensive-comparison.md#4-hybrid-architecture-recommendations)

**Large Graphs (50k-100k nodes, exploration):**
- Recommended: Sigma.js or G6 WebGL
- See: [Performance Tier 2](./graph-libraries-comprehensive-comparison.md#tier-2-50k-100k-optimized)

**Very Large Graphs (100k+ nodes, force simulation):**
- Recommended: Cosmograph or custom PixiJS
- See: [Performance Tier 1](./graph-libraries-comprehensive-comparison.md#tier-1-100k-native)

### By Timeline

**2 weeks:** ReactFlow optimization
**5 weeks:** Hybrid (ReactFlow + Sigma.js) ⭐ RECOMMENDED
**8 weeks:** Full Sigma.js migration
**10 weeks:** Custom PixiJS solution

### By Budget

**$8k:** ReactFlow optimization
**$20k:** Hybrid approach ⭐ RECOMMENDED
**$32k:** Full Sigma.js
**$40k:** Custom PixiJS

---

## Decision Framework

### Step 1: Define Requirements
- [ ] Maximum expected node count?
- [ ] Need rich DOM interactions (forms, editing)?
- [ ] Read-only exploration or interactive editing?
- [ ] Development timeline available?
- [ ] Budget constraints?
- [ ] Risk tolerance?

### Step 2: Consult Decision Tree
See: [Visual Decision Guide - Decision Tree](./graph-libraries-decision-flowchart.md#decision-matrix-visual)

### Step 3: Review Comparison
See: [Comprehensive Comparison - Feature Matrix](./graph-libraries-comprehensive-comparison.md#2-complete-feature-matrix)

### Step 4: Evaluate ROI
See: [Comprehensive Comparison - ROI Analysis](./graph-libraries-comprehensive-comparison.md#8-roi-analysis)

### Step 5: Make Decision
Document decision with:
- Chosen approach
- Rationale
- Timeline
- Budget
- Acceptance criteria

---

## Library Summaries (Quick Reference)

### Tier 1: 100k+ Nodes (WebGL/GPU)

**Cosmograph**
- Max: 1M+ nodes
- Tech: WebGL + GPU Compute
- Best for: Massive force simulations
- Bundle: 120KB
- Effort: 8-10 weeks
- Risk: Very High

**Sigma.js**
- Max: 100k+ nodes
- Tech: WebGL
- Best for: Large static graphs
- Bundle: 80KB
- Effort: 6-8 weeks (full), 5 weeks (hybrid)
- Risk: Medium (full), Low (hybrid)

**PixiJS (custom)**
- Max: 1M+ nodes
- Tech: WebGL Instancing
- Best for: Custom solutions
- Bundle: 400KB
- Effort: 10+ weeks
- Risk: Very High

### Tier 2: 50k-100k Nodes

**G6 (WebGL mode)**
- Max: 100k nodes
- Tech: Canvas/WebGL
- Best for: Enterprise dashboards
- Bundle: 300KB
- Effort: 6-7 weeks
- Risk: Medium

**Cytoscape.js**
- Max: 100k nodes
- Tech: Canvas/WebGL
- Best for: Scientific viz
- Bundle: 200KB
- Effort: 6-8 weeks
- Risk: Medium

### Tier 3: 10k-50k Nodes

**ReactFlow (optimized)**
- Max: 10-15k nodes
- Tech: DOM + optimizations
- Best for: Current use case
- Bundle: 150KB
- Effort: 2 weeks
- Risk: Low

### Tier 4: <10k Nodes

**ReactFlow (current)**
- Max: 5-10k nodes
- Tech: DOM/SVG
- Best for: Interactive editing
- Bundle: 150KB
- Effort: 0 (no change)
- Risk: None

---

## Implementation Guides

### Hybrid Approach (RECOMMENDED)
See: [Implementation Checklist](../guides/quick-start/graph-library-implementation-checklist.md)

**Week-by-Week:**
1. Foundation (Graphology, threshold)
2. Integration Part 1 (events)
3. Integration Part 2 (renderers)
4. Optimization (LOD, performance)
5. Polish & Launch (docs, deploy)

### ReactFlow Optimization
See: [ReactFlow Research - Plan](./REACT_FLOW_10K_NODES_PERFORMANCE_RESEARCH_AND_PLAN.md#3-plan-expanded)

**Phase A:** Quick wins (memoization, store audit)
**Phase B:** Structural (viewport window, LOD)
**Phase C:** Polish (metrics, docs)
**Phase D:** 10k-scale (worker, canvas)

---

## Performance Benchmarks

### Current State (ReactFlow)
- 1k nodes: 60 FPS
- 5k nodes: 50 FPS
- 10k nodes: 30 FPS
- 20k nodes: 15 FPS (unusable)
- 50k nodes: Crashes

### Target State (Hybrid)
- <10k nodes: ReactFlow @ 50+ FPS
- 10k-50k nodes: Sigma.js @ 45+ FPS
- 50k-100k nodes: Sigma.js @ 30+ FPS
- Memory @ 100k: <1GB
- Bundle: <250KB (with code splitting)

---

## Key Findings

### What Works
✅ ReactFlow excellent for <10k with rich interactions
✅ WebGL/GPU required for 100k+ scale
✅ Hybrid approach balances performance and features
✅ Graphology enables library switching
✅ Code splitting mitigates bundle size

### What Doesn't Work
❌ DOM rendering beyond 10k nodes
❌ Force layouts on CPU for large graphs
❌ Continuous layout recomputation
❌ Heavy node content without LOD
❌ "Big bang" migration (too risky)

### Critical Success Factors
🎯 Threshold-based rendering (automatic switching)
🎯 Shared state layer (Graphology)
🎯 Progressive enhancement (lazy-load)
🎯 LOD system (zoom-based simplification)
🎯 Viewport culling (only render visible)
🎯 Component reuse (80%+ in hybrid)

---

## External Resources

### Libraries
- [ReactFlow](https://reactflow.dev/)
- [Sigma.js](https://www.sigmajs.org/)
- [Cosmograph](https://cosmograph.app/)
- [Graphology](https://graphology.github.io/)
- [G6](https://g6.antv.antgroup.com/)
- [PixiJS](https://pixijs.com/)
- [Cytoscape.js](https://js.cytoscape.org/)

### Technical References
- [WebGL Fundamentals](https://webglfundamentals.org/)
- [WebGPU Fundamentals](https://webgpufundamentals.org/)
- [GPU Gems 3](https://developer.nvidia.com/gpugems/gpugems3)
- [React Performance Guide](https://react.dev/learn/render-and-commit)

### Research Papers
- [GraphWaGu: GPU Powered Graph Layout](https://stevepetruzza.io/pubs/graphwagu-2022.pdf)
- [Exploiting GPUs for Fast Force-Directed Visualization](https://liacs.leidenuniv.nl/~takesfw/pdf/exploiting-gpus-fast.pdf)

---

## Contribution Guidelines

### Adding New Research
1. Create document in `/docs/research/`
2. Add entry to this index
3. Link from relevant sections
4. Update "Last Updated" date

### Updating Benchmarks
1. Run performance tests
2. Update benchmark tables
3. Document test conditions
4. Compare with previous results

### Proposing New Libraries
1. Create evaluation document
2. Run same benchmarks
3. Compare with existing options
4. Update comparison matrices

---

## Changelog

### 2026-02-01
- Created comprehensive comparison matrix
- Added visual decision guide
- Added implementation checklist
- Synthesized all existing research
- Added this index document

### 2026-01-31
- Completed Sigma.js evaluation
- GPU force layout research
- Web worker architecture
- ReactFlow optimization plan

---

## Contact

**Research Owner:** [TBD]
**Technical Lead:** [TBD]
**Last Review:** 2026-02-01
**Next Review:** 2026-03-01

---

**Document Status:** ✅ Complete and Current
**Recommended Action:** Proceed with Hybrid Approach (ReactFlow + Sigma.js)
