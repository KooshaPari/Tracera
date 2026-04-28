# Wave 3 Launch Briefing - T+60 Ready

**Orchestrator:** integration-tests-implementer
**Date:** 2026-02-06
**Current Status:** Checkpoint 3 (T+55) - Wave 2 Phase 2 progressing, Wave 3 ready
**Deployment Target:** T+60 (start all 3 tasks immediately)

---

## WAVE 3 OVERVIEW (3 Parallel Tasks)

All three tasks are **independent** and can execute in parallel. Each has different completion times.

### Task #20: Gap 5.6 - API Endpoints Re-enable
- **Duration:** 30 minutes (T+60 → T+90)
- **Owner:** api-performance-implementer
- **Scope:** Re-enable + implement 15+ API endpoint tests
- **Dependencies:** None (independent from #21, #22)

### Task #21: Gap 5.7 - GPU Compute Shaders ⭐ CRITICAL PATH
- **Duration:** 40 minutes (T+60 → T+100)
- **Owner:** api-performance-implementer
- **Scope:** WebGPU + WebGL GPGPU shaders (4 phases, 12+12+10+6 min)
- **Critical:** This task determines overall Phase 5 completion time
- **Dependencies:** None (independent from #20, #22)

### Task #22: Gap 5.8 - Spatial Indexing
- **Duration:** 30 minutes (T+60 → T+90)
- **Owner:** api-performance-implementer
- **Scope:** Edge midpoint spatial indexing for viewport culling
- **Dependencies:** None (independent from #20, #21)

---

## CRITICAL PATH EXPLANATION

**Why Gap 5.7 (GPU Shaders) is Critical:**

```
Timeline without GPU:
  Wave 1 complete: T+40
  Wave 2 complete: T+70
  Wave 3 Gates (ordered):
    - Gap 5.6: T+90
    - Gap 5.8: T+90
    - Gap 5.7: T+100 ← LONGEST TASK
  Phase 5 complete: T+100 (determined by longest task)

Timeline with GPU Parallel:
  Wave 1: T+40 ✅
  Wave 2: T+70 ✅
  Wave 3 (all parallel):
    - All 3 start T+60
    - All 3 finish: T+90 (Gaps 5.6, 5.8) + T+100 (Gap 5.7)
    - Phase 5 complete: T+100 (wait for longest = Gap 5.7)

One way to improve: If Gap 5.7 finishes early (before T+100), overall Phase 5 can finish earlier.
If Gap 5.7 is delayed (after T+100), overall Phase 5 is delayed.
```

**Therefore:**
- Start all 3 tasks immediately at T+60
- Monitor Gap 5.7 every 5 min (T+65, T+70, T+75, T+80, T+85)
- If Gap 5.7 Phase 1 (WebGPU) not 50% complete by T+72, escalate

---

## TASK #20: GAP 5.6 API ENDPOINTS (30 min)

### Phase 1: Re-enable API endpoint tests (8 min, T+60-68)
**Goal:** Identify which endpoint tests are currently skipped

**Files to modify:**
- `frontend/apps/web/src/__tests__/api/endpoints.test.ts` (or endpoints.comprehensive.test.ts)
- Change `it.skip` → `it` for existing tests
- Expected: 15+ tests (check current file)

**Acceptance:**
- All endpoint tests enabled (no `.skip`)
- No duplicate test names
- Compilation passing

### Phase 2: Tune endpoint implementations (12 min, T+68-80)
**Goal:** Get all tests passing

**Common fixes:**
- Update API response mocks if needed
- Verify endpoint paths match test expectations
- Add missing endpoints if found during testing

**Acceptance:**
- 15+/15+ tests passing
- 100% pass rate
- No timeouts

### Phase 3: Validation & integration (10 min, T+80-90)
**Goal:** Final checks

**Checklist:**
- Run 2× consecutive passes (verify not flaky)
- Coverage ≥85% for modified files
- No cross-test contamination

**Acceptance:**
- 100% pass, 2 consecutive runs
- Coverage maintained

---

## TASK #21: GAP 5.7 GPU COMPUTE SHADERS (40 min) ⭐ CRITICAL

### Phase 1: WebGPU Setup (12 min, T+60-72)
**Goal:** WebGPU hook + device detection + basic shader

**Create:**
- `frontend/apps/web/src/hooks/useGPUCompute.ts`
- `frontend/apps/web/src/shaders/force-directed.wgsl`

**Implementation:**
```typescript
// useGPUCompute.ts
- Detect WebGPU support (navigator.gpu)
- Get GPU adapter + device
- Create compute pipeline (WGSL shader)
- Manage compute buffers (position, velocity, forces)
- Expose compute function: (nodes, edges) → positions

// force-directed.wgsl (WGSL compute shader)
- Force calculation kernel (repulsion, attraction)
- Velocity integration
- Position update
- Handles 1000-100000 nodes
```

**Expected Deliverables:**
- ✅ Hook created and compiles
- ✅ WebGPU device detection working
- ✅ Shader compiles without WGSL errors
- ✅ Compute pipeline ready for Phase 2

**Success Criteria:**
- No TS errors in useGPUCompute.ts
- No WGSL shader compilation errors
- Device detection returns GPU or CPU fallback

---

### Phase 2: WebGL Fallback (12 min, T+72-84)
**Goal:** WebGL GPGPU fallback for non-WebGPU browsers

**Create:**
- `frontend/apps/web/src/shaders/force-directed.glsl`

**Implementation:**
```glsl
// force-directed.glsl (GLSL fragment shader)
- Ping-pong texture rendering (position texture → force texture → position texture)
- Force calculation via fragment shader
- Velocity integration
- Same algorithm as WebGPU (ensures equivalent output)
```

**Integration:**
- Detect WebGPU availability
- Use WebGPU if available, fallback to WebGL
- Ensure both produce same results (within floating-point tolerance)

**Expected Deliverables:**
- ✅ WebGL shader created and compiles
- ✅ Fallback detection working
- ✅ Both pipelines produce equivalent results

**Success Criteria:**
- No GLSL shader errors
- WebGL compute kernel tested with small test graph
- Fallback activates automatically on non-WebGPU browsers

---

### Phase 3: Performance Testing & Benchmarking (10 min, T+84-94)
**Goal:** Verify GPU delivers 50-100x speedup

**Benchmarks:**
```
Test: 10,000 nodes + 50,000 edges
CPU layout: ~30 seconds (expected)
GPU layout: <100ms (target: 50-100x faster)
Speedup ratio: 30,000ms / 100ms = 300x (stretch goal: 50-100x is success)
```

**Testing:**
- Create test graph (10k nodes, 50k edges)
- Time CPU layout (reference)
- Time GPU layout (WebGPU)
- Time GPU layout (WebGL fallback)
- Verify memory usage <5% increase
- Test browser compatibility (Chrome, Firefox, Safari, Edge)

**Expected Deliverables:**
- ✅ Benchmark results: GPU 50-100x faster than CPU
- ✅ Memory usage acceptable (<5% increase)
- ✅ Cross-browser compatibility verified

**Success Criteria:**
- 10k nodes render in <100ms (GPU)
- Memory usage stays below 1GB total
- All 4 browsers working

---

### Phase 4: Integration & Validation (6 min, T+94-100)
**Goal:** Wire GPU compute into SigmaGraphView

**Integration:**
- Import `useGPUCompute` into SigmaGraphView
- Replace CPU layout with GPU compute when available
- Add performance visualization (optional: FPS counter, compute time)
- Create test suite: `gpu-compute.perf.test.tsx`

**Testing:**
- Verify SigmaGraphView uses GPU when available
- Verify visual output identical to CPU version
- Verify fallback works on non-WebGPU browsers
- Create benchmark test (compare CPU vs GPU)

**Expected Deliverables:**
- ✅ GPU compute integrated into graph rendering
- ✅ Performance metrics collected
- ✅ Test suite created + passing
- ✅ Benchmark report (CPU vs GPU)

**Success Criteria:**
- Graph renders identically on GPU and CPU
- 50-100x speedup verified in benchmarks
- All tests passing
- No visual artifacts or rendering issues

---

## TASK #22: GAP 5.8 SPATIAL INDEXING (30 min)

### Phase 1: R-tree Implementation (12 min, T+60-72)
**Goal:** Build R-tree spatial index for viewport culling

**Create:**
- `frontend/apps/web/src/lib/spatial/r-tree.ts`

**Implementation:**
```typescript
// R-tree (or Quadtree alternative)
- Insert nodes with bounding boxes
- Query viewport region: nodes visible in [x1, y1, x2, y2]
- Remove nodes on deletion
- Rebuild on major changes

// API:
- insert(nodeId, bounds)
- query(viewport) → [nodeIds]
- remove(nodeId)
- rebuild(allNodes)
```

**Expected Deliverables:**
- ✅ R-tree implementation complete
- ✅ Basic insert/query/remove working
- ✅ Performance acceptable (queries in <50ms for 100k nodes)

---

### Phase 2: Viewport Culling Integration (12 min, T+72-84)
**Goal:** Use R-tree to cull invisible nodes

**Integration:**
- Query R-tree in SigmaGraphView on viewport change
- Only render visible nodes
- Skip rendering nodes outside viewport

**Expected Deliverables:**
- ✅ Culling reduces render cost for large graphs
- ✅ Smooth panning/zooming (no lag)
- ✅ Visual quality identical to non-culled version

---

### Phase 3: Testing & Optimization (6 min, T+84-90)
**Goal:** Verify performance gains + validate correctness

**Testing:**
- Verify culled view matches full render (visual test)
- Benchmark: 50k nodes with vs without culling
- Measure FPS improvement
- Test with 10k, 50k, 100k node graphs

**Expected Deliverables:**
- ✅ Test suite: `spatial-indexing.test.tsx`
- ✅ Performance gain measured: 20-40% FPS improvement expected
- ✅ Correctness verified (no missed nodes)

---

## WAVE 3 EXECUTION TIMELINE

```
T+60: All 3 tasks start in parallel
      ├─ Task #20 Phase 1 (API re-enable)
      ├─ Task #21 Phase 1 (WebGPU setup) ⭐ CRITICAL START
      └─ Task #22 Phase 1 (R-tree build)

T+65: CHECKPOINT - First progress check
      ├─ Gap 5.6: Expect 8-10 tests re-enabled
      ├─ Gap 5.7: Expect Phase 1 >25% complete (WebGPU hook created)
      └─ Gap 5.8: Expect R-tree basic structure done

T+70: CHECKPOINT - Phase 1-2 boundary check
      ├─ Gap 5.6: Expect Phase 2 active (implementations tuning)
      ├─ Gap 5.7: Expect Phase 1 ~70% complete (shader compiling)
      └─ Gap 5.8: Expect Phase 2 starting (viewport culling)

T+75: CHECKPOINT - Phase 2 midpoint check
      ├─ Gap 5.6: Expect Phase 2 >90% complete (test passes)
      ├─ Gap 5.7: Expect Phase 2 starting or ~25% complete (WebGL setup)
      └─ Gap 5.8: Expect Phase 2 ~50% complete (integration working)

T+80: CHECKPOINT - Approaching completion check
      ├─ Gap 5.6: Expect Phase 3 active (final validation)
      ├─ Gap 5.7: Expect Phase 2 ~75% complete (WebGL fallback)
      └─ Gap 5.8: Expect Phase 2 >90% complete (tests running)

T+90: EXPECTED - Gaps 5.6 & 5.8 complete
      ├─ Gap 5.6: ✅ DONE (15+ tests passing)
      ├─ Gap 5.8: ✅ DONE (spatial index integrated + tested)
      └─ Gap 5.7: Still running (Phase 2-3 active, Phase 4 pending)

T+100: EXPECTED - Gap 5.7 complete
      └─ Gap 5.7: ✅ DONE (GPU shaders validated, 50-100x speedup)
```

---

## CRITICAL MONITORING SCHEDULE

### Every 5 Minutes (T+60 through T+85)
Check: Is Gap 5.7 on schedule?

**T+65:** Phase 1 should be >25% (hook started)
**T+70:** Phase 1 should be ~70% (shader compiling)
**T+75:** Phase 2 should be starting (WebGL setup)
**T+80:** Phase 2 should be >75% (fallback working)

**If Behind:**
- At T+72: If Phase 1 <50% → Escalate immediately
- At T+75: If Phase 2 not started → Escalate with code help
- At T+85: If Phase 3 not started → Activate emergency parallel dev

### Escalation Triggers
```
IF Phase 1 <50% at T+72:
  → Escalate: "Gap 5.7 Phase 1 behind schedule - can provide WebGPU setup code?"
  → Provide reference from /docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md

IF Phase 2 not started by T+80:
  → Escalate: "Gap 5.7 Phase 2 delayed - GPU fallback code available"
  → Offer parallel WebGL development (can be done separately)

IF Phase 3 not started by T+90:
  → Escalate: "Gap 5.7 at risk - need emergency support"
  → Activate full context + code sketches
```

---

## WAVE 3 SUCCESS CRITERIA

### Gap 5.6 (API Endpoints)
- [ ] 15+/15+ tests passing
- [ ] 0 flakes (2 consecutive passes)
- [ ] Coverage ≥85%
- [ ] Completion: T+90 ✅

### Gap 5.7 (GPU Shaders) ⭐ CRITICAL
- [ ] Phase 1: WebGPU hook created + shader compiles
- [ ] Phase 2: WebGL fallback working + equivalent results
- [ ] Phase 3: 50-100x speedup verified in benchmarks
- [ ] Phase 4: GPU integrated into SigmaGraphView + tests passing
- [ ] Completion: T+100 ✅

### Gap 5.8 (Spatial Index)
- [ ] R-tree implementation complete + tested
- [ ] Viewport culling integrated + working
- [ ] 20-40% FPS improvement measured
- [ ] Correctness verified (no missed nodes)
- [ ] Completion: T+90 ✅

---

## WAVE 3 SUPPORT RESOURCES

**Reference Implementation Plans:**
- `/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md` (420+ lines, detailed code sketches)
  - Section 1: Gap 5.6 (lines 1-180)
  - Section 2: Gap 5.7 (lines 187-580) ⭐ DETAILED CODE SKETCHES
  - Section 3: Gap 5.8 (lines 581+)

**Code Sketches Available:**
- WebGPU hook pattern (useGPUCompute.ts)
- WGSL compute shader template (force-directed.wgsl)
- WebGL GPGPU fallback pattern (force-directed.glsl)
- R-tree insertion/query algorithms
- Viewport culling integration pattern

**Files to Create/Modify:**
- NEW: `/frontend/apps/web/src/hooks/useGPUCompute.ts`
- NEW: `/frontend/apps/web/src/shaders/force-directed.wgsl`
- NEW: `/frontend/apps/web/src/shaders/force-directed.glsl`
- MODIFY: `/frontend/apps/web/src/components/graph/SigmaGraphView.tsx`
- NEW: `/frontend/apps/web/src/__tests__/performance/gpu-compute.perf.test.tsx`
- NEW: `/frontend/apps/web/src/lib/spatial/r-tree.ts`
- NEW: `/frontend/apps/web/src/__tests__/lib/spatial-indexing.test.tsx`

---

## ORCHESTRATOR STANDING ORDERS (T+60-T+100)

1. **T+60:** Confirm all 3 tasks starting
2. **Every 5 min:** Check Gap 5.7 progress (especially T+60-T+85)
3. **T+70:** Create Checkpoint 4 briefing
4. **T+90:** Confirm Gaps 5.6 & 5.8 complete
5. **T+100:** Confirm Gap 5.7 complete → Trigger Wave 4 (final validation)

---

## WAVE 3 STATUS: 🟡 READY TO LAUNCH T+60

**Preparation Complete:**
- ✅ All 3 task descriptions finalized
- ✅ Critical path identified (Gap 5.7)
- ✅ Monitoring schedule established
- ✅ Escalation procedures ready
- ✅ Reference materials linked

**Launch Readiness:** 100%

**Expected Outcome:** All 3 tasks executing in parallel, Gap 5.7 determines T+100 completion

**Orchestrator Status:** 🟢 Ready to monitor and dispatch support as needed

---

**Next Action:** Deploy all 3 Wave 3 tasks at T+60. Begin 5-min progress monitoring on Gap 5.7 immediately.
