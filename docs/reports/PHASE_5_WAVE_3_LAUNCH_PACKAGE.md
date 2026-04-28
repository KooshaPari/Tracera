# Phase 5: Wave 3 Launch Package
**Status:** READY FOR DEPLOYMENT AT T+20
**Trigger:** Gap 5.4 Phase 1 completion + signal received
**Target Deployment Time:** 2026-02-06 02:35 UTC (T+20 min)

---

## LAUNCH AUTHORIZATION

**Trigger Condition:**
```
When: Gap 5.4 (Temporal Snapshots) Phase 1 COMPLETE
Signal: "✅ Gap 5.4 Phase 1 DONE - activities.go + workflows.go ready"
Action: Deploy Wave 3 IMMEDIATELY (all 3 agents in parallel)
```

**Target Agent:** api-performance-implementer
**Tasks:** #20 (Gap 5.6), #21 (Gap 5.7), #22 (Gap 5.8)
**Wall-Clock Duration:** ~40 minutes (T+20 to T+60)
**Success Criteria:** 30+ tests passing + GPU performance targets met

---

## WAVE 3 OVERVIEW

**Three Critical Gaps (All Independent):**

| Gap | Agent | Task | Scope | Duration | Status |
|-----|-------|------|-------|----------|--------|
| **5.6** | api-performance-implementer | #20 | 15+ API endpoint tests | 40 min | Ready |
| **5.7** | api-performance-implementer | #21 | GPU compute shaders (WebGPU + WebGL) | 40 min | **CRITICAL PATH** |
| **5.8** | api-performance-implementer | #22 | Edge midpoint spatial indexing | 32 min | Ready |

**Execution Model:** 3 gaps execute in parallel (same agent, triple-task sprint)

---

## DETAILED BRIEFING

### Gap 5.6: API Endpoint Tests (15+ tests, 40 min)

**File:** `frontend/apps/web/src/__tests__/api/endpoints.test.ts` (currently skipped)
**Objective:** Re-enable 15+ CRUD endpoint tests + contract validation

**Implementation Steps:**

**Phase 1 (10 min): Test Setup**
- Remove `describe.skip` at line 21
- Extend `data.ts` with `mockEndpoints` array (20+ variants)
- Create response snapshots for contract validation
- Wire MSW handlers for all endpoint variants

**Phase 2 (10 min): Re-enable CRUD Tests**
- Un-skip 5 core CRUD tests (create, read, update, delete, list)
- Implement contract validation for each operation
- Add error case handling (400, 401, 403, 404, 500)

**Phase 3 (10 min): Advanced Tests**
- Un-skip 10+ advanced tests (filtering, pagination, sorting)
- Implement snapshot matching for responses
- Verify response structure consistency

**Phase 4 (10 min): Validation**
- Run full suite (15+ tests)
- 5x consecutive runs for flake detection
- Coverage validation (≥85%)

**Success Criteria:**
- [ ] 15+ tests passing
- [ ] Contract validation complete
- [ ] Snapshot diffs <2%
- [ ] Coverage ≥85%
- [ ] 5x flake-free runs

**Support Resources:**
- `/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md` (lines 1-220)
- Code sketches: lines 423-485
- Mock endpoint templates ready

---

### Gap 5.7: GPU Compute Shaders (WebGPU + WebGL, 40 min) ⭐ CRITICAL PATH

**File:** `frontend/apps/web/src/lib/gpuForceLayout.ts`
**Objective:** Implement WebGPU + WebGL compute shaders for 50-100x speedup

**Performance Target:**
- 10k nodes: <100ms (GPU) vs ~30s (CPU) = **~300x speedup target**
- 50k nodes: <500ms (GPU) vs >5min (CPU) = **~600x potential**
- Fallback chain: WebGPU → WebGL GPGPU → CPU (with warnings)

**Implementation Steps:**

**Phase 1A (15 min): WebGPU Implementation**
1. Create `src/lib/gpu/webgpuCompute.ts` (400+ lines)
   - WGSL compute shader for Fruchterman-Reingold force layout
   - GPU device detection & initialization
   - Buffer management (node positions, velocities, edges)
   - Dispatch + synchronization logic

2. WGSL Shader Implementation:
```wgsl
@compute @workgroup_size(256)
fn calculate_forces(@builtin(global_invocation_id) id: vec3<u32>) {
  // 1. Load node data (position, velocity, mass)
  // 2. Calculate repulsion forces from all other nodes (O(n²))
  // 3. Apply edge attraction forces (O(edges))
  // 4. Apply gravity towards center
  // 5. Integrate velocity with damping
  // 6. Update position
  // 7. Store results back to buffer
}
```

3. Implement buffer lifecycle:
   - Create position/velocity buffers
   - Stage data uploads (CPU → GPU)
   - Sync after compute pass
   - Readback results (GPU → CPU)

4. Wire into `webgpuForceLayout()` at lines 219-230:
   - Detect WebGPU availability
   - Initialize compute context
   - Run force iteration loops
   - Return final node positions

**Phase 1B (15 min): WebGL GPGPU Fallback**
1. Create `src/lib/gpu/webglGpgpu.ts` (300+ lines)
   - Fragment shader for position updates
   - Texture-based position encoding
   - Framebuffer management
   - Readback pixel data as float arrays

2. GLSL Shader:
```glsl
#version 300 es
precision highp float;

uniform sampler2D u_positions;
uniform sampler2D u_edges;
uniform vec2 u_screenSize;

void main() {
  // 1. Decode position from texture coordinates
  // 2. Calculate forces from neighbors
  // 3. Integrate velocity
  // 4. Encode new position as color
  // 5. Output to framebuffer
}
```

3. Wire into `webglForceLayout()` at lines 242-253:
   - Fallback when WebGPU unavailable
   - Support WebGL 2.0 + OpenGL ES 3.0
   - 20-50x speedup for older devices

**Phase 2 (5 min): Error Handling & Fallback Chain**
- Detect WebGPU support, fallback to WebGL if unavailable
- Fallback to CPU with visible warning log
- Graceful degradation: never fail, always produce results

**Phase 3 (5 min): Testing**
- Compilation tests for shaders (verify WGSL/GLSL validity)
- Correctness validation (GPU output vs CPU reference)
- Performance benchmarks (10k, 50k, 100k nodes)
- Fallback chain testing

**Success Criteria:**
- [ ] WebGPU computes correctly
- [ ] WebGL fallback functional
- [ ] 10k nodes: <100ms (GPU)
- [ ] 50k+ nodes: <500ms (GPU)
- [ ] Fallback chain: WebGPU → WebGL → CPU
- [ ] Zero shader compilation errors

**Code Sketches:**
`/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md`
- Gap 5.7 Full Spec: lines 221-750
- WebGPU Implementation: lines 283-450
- WebGL GPGPU: lines 453-600
- Testing Strategy: lines 610-750

---

### Gap 5.8: Edge Midpoint Spatial Indexing (32 min)

**File:** `frontend/apps/web/src/lib/enhancedViewportCulling.ts`
**Objective:** Implement edge midpoint indexing + Cohen-Sutherland clipping for 98% culling accuracy

**Performance Target:**
- 98% culling accuracy (vs 85% current)
- <5% memory overhead
- <50ms for 5k edges
- 2-3x speedup for large graphs

**Implementation Steps:**

**Phase 1 (10 min): Edge Midpoint Calculation**
1. Add `calculateEdgeMidpoint()` function
   - Compute middle point between source/target nodes
   - Pre-cache midpoints for all edges
   - Store in optimized format (x, y, edge_id)

2. Add `indexEdgeMidpoints()` function
   - Build spatial grid of midpoints
   - Grid resolution: 256x256 cells (screen-aligned)
   - Per-cell edge lists for fast lookup

**Phase 2 (10 min): Cohen-Sutherland Clipping Algorithm**
1. Implement `cohenSutherlandClip()` function
   - 4-bit outcodes for viewport classification
   - Iterative line clipping
   - Handles all edge cases (parallel, endpoint inside, etc.)
   - Returns visible segment or null if fully clipped

2. Apply to viewport culling:
   - Test edge midpoint against viewport
   - If outside: test endpoints
   - If both outside same region: reject (100% culled)
   - If partially visible: clip to viewport bounds

**Phase 3 (7 min): Integration & Optimization**
1. Integrate into rendering pipeline:
   - Pre-compute midpoints during graph load
   - Update midpoints only when nodes moved
   - Use grid lookup for O(1) viewport intersection test
   - Reduce draw calls by 50-80% on large graphs

2. Optimization:
   - GPU-friendly data layout
   - SIMD-compatible distance calculations
   - Batch edge culling (process 256 edges/iteration)

**Phase 4 (5 min): Validation & Benchmarking**
- Accuracy tests: verify 98% culling on standard graphs
- Performance tests: <50ms for 5k edges
- Memory overhead: <5% vs current
- Visual verification: no visible culling artifacts

**Success Criteria:**
- [ ] 98% culling accuracy achieved
- [ ] <5% memory overhead
- [ ] <50ms for 5k edges benchmark passing
- [ ] Cohen-Sutherland fully implemented
- [ ] Edge midpoint indexing functional
- [ ] Zero visual artifacts

**Code Sketches:**
`/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md`
- Gap 5.8 Full Spec: lines 751-1001
- Edge Midpoint: lines 803-880
- Cohen-Sutherland: lines 883-950
- Spatial Grid: lines 953-1001

---

## PARALLEL EXECUTION MODEL

**Timeline (T+20 to T+60):**
```
Phase 1 (T+20 to T+30): All 3 gaps Phase 1 parallel [10 min each]
  Gap 5.6: Test setup
  Gap 5.7: WebGPU implementation
  Gap 5.8: Edge midpoint calculation

Phase 2 (T+30 to T+40): All 3 gaps Phase 2 parallel [10 min each]
  Gap 5.6: CRUD tests re-enabled
  Gap 5.7: WebGL GPGPU fallback
  Gap 5.8: Cohen-Sutherland clipping

Phase 3 (T+40 to T+50): All 3 gaps Phase 3 parallel [10 min each]
  Gap 5.6: Advanced tests + snapshots
  Gap 5.7: Error handling + fallback chain
  Gap 5.8: Integration + optimization

Phase 4 (T+50 to T+60): All 3 gaps Phase 4 parallel [10 min each]
  Gap 5.6: Validation + flake testing
  Gap 5.7: Testing + benchmarking
  Gap 5.8: Validation + benchmarking
```

**Critical Path:** Gap 5.7 (GPU) - 40 min implementation
**All 3 gaps execute in parallel (same agent)** - total 40 min wall-clock

---

## WAVE 3 SUCCESS CRITERIA

### Overall
- [ ] 30+ tests implemented (15 + 10 + 8+)
- [ ] All tests passing
- [ ] 5x flake-free runs completed
- [ ] Coverage ≥85% maintained

### Gap 5.6 Specific
- [ ] 15+ API endpoint tests passing
- [ ] Contract validation complete
- [ ] 100% endpoint coverage
- [ ] Snapshot diffs <2%

### Gap 5.7 Specific (CRITICAL)
- [ ] WebGPU implementation complete
- [ ] WebGL GPGPU fallback functional
- [ ] 10k nodes: <100ms (GPU)
- [ ] 50-100x speedup verified
- [ ] 100k+ node support validated
- [ ] Fallback chain: WebGPU → WebGL → CPU

### Gap 5.8 Specific
- [ ] 98% culling accuracy achieved
- [ ] <5% memory overhead
- [ ] <50ms for 5k edges
- [ ] Cohen-Sutherland fully implemented

---

## DEPLOYMENT SEQUENCE (When Triggered)

**Step 1: Acknowledge Receipt**
```
✅ Wave 3 LAUNCH AUTHORIZED
Trigger received: Gap 5.4 Phase 1 complete
Time: T+20 (02:35 UTC)
Deploying all 3 tasks to api-performance-implementer
```

**Step 2: Send Triple-Task Brief**
Provide full briefing with:
- Task #20 complete spec
- Task #21 complete spec + GPU documentation
- Task #22 complete spec
- All code sketches (lines 423-1001)
- Testing + validation strategy

**Step 3: Execute Tasks**
- api-performance-implementer launches all 3 tasks immediately
- All 3 gaps execute in parallel (same agent, staggered workloads)
- Team lead monitors for phase checkpoints at T+30, T+40, T+50

**Step 4: Checkpoint Monitoring (Every 10 min)**
- T+30: Phase 2 checkpoint (all 3 gaps Phase 2 complete)
- T+40: Phase 3 checkpoint (all 3 gaps Phase 3 complete)
- T+50: Phase 4 checkpoint (all 3 gaps Phase 4 complete)
- T+60: Final validation (all 30+ tests passing)

**Step 5: Final Commit + Wave 4 Trigger**
When all tasks complete:
- Create 1 comprehensive commit: "feat: implement Gap 5.6-5.8 (API endpoints + GPU shaders + spatial indexing)"
- Trigger Wave 4 (validation phase)
- Prepare Phase 5 final report

---

## COORDINATOR ACTIONS

**At T+20 (Trigger):**
- [ ] Receive "Gap 5.4 Phase 1 complete" signal
- [ ] Update status: "✅ Wave 3 LAUNCHING"
- [ ] Message api-performance-implementer with full launch package
- [ ] Start T+20-T+60 monitoring timeline

**At T+30:**
- [ ] Monitor incoming Gap 5.6/5.7/5.8 Phase 2 completion reports
- [ ] Verify all three gaps on schedule
- [ ] Checkpoint 2 acknowledgment

**At T+40:**
- [ ] Verify Phase 3 completion (advanced tests, GPU fallback, integration)
- [ ] Monitor Wave 2 Phase 4 completion (should finish T+60-65)

**At T+50:**
- [ ] Verify Phase 4 start (final validation + benchmarking)
- [ ] Prepare Wave 4 validation brief (if Wave 2 complete)

**At T+60:**
- [ ] Verify all 30+ Wave 3 tests passing
- [ ] Confirm GPU performance targets (10k nodes <100ms)
- [ ] Confirm spatial indexing accuracy (98% culling)
- [ ] Prepare final commit

---

## SUPPORT RESOURCES (Ready Now)

✅ Complete documentation available:
1. **PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md** (31KB, 1000+ lines)
   - Full technical specs for all 3 gaps
   - Code sketches (lines 423-1001)
   - Testing strategy + validation

2. **PHASE_5_GAPS_5_6_5_7_5_8_EXECUTIVE_SUMMARY.md** (15KB, 432 lines)
   - High-level overview of each gap
   - Problem analysis + solutions
   - Success metrics

3. **Code Sketches Ready:**
   - Gap 5.6: endpoints.test.ts modifications + snapshots
   - Gap 5.7: WebGPU shader + WebGL GPGPU
   - Gap 5.8: Spatial grid + Cohen-Sutherland

---

## STATUS: 🟢 WAVE 3 READY FOR DEPLOYMENT

**All components prepared:**
- ✅ Technical specs complete
- ✅ Code sketches ready
- ✅ Test strategy documented
- ✅ Success criteria defined
- ✅ Resource allocation confirmed

**Awaiting trigger:** Gap 5.4 Phase 1 completion (expected T+15-20)

**Next:** Deploy to api-performance-implementer at T+20
