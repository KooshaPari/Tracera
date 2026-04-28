# Phase 5: Dual-Wave Execution Coordination Plan

**Date:** 2026-02-06
**Status:** 🟢 Wave 1 LIVE, Wave 2 STAGED
**Strategy:** Parallel dual-wave execution for 90-120 min total completion

---

## Executive Summary

**Current State:**
- Wave 1 (Gaps 5.3-5.5): 3 agents executing in parallel, Phase 1 active
- Wave 2 (Gaps 5.6-5.8): 3 gaps fully analyzed, code sketches ready, awaiting agent assignment

**Recommendation:**
Assign Wave 2 agents immediately after Wave 1 Checkpoint 1 (T+15 min) for true 6-gap parallelization.

**Expected Outcome:**
- 90-120 min wall clock for all 6 gaps (vs 180+ sequential)
- 80+ tests unblocked and passing
- 100% acceptance criteria met per gap
- Zero idle time, maximum team utilization

---

## Wave 1: Gaps 5.3-5.5 (Live Now)

### Agents & Tasks

| Gap | Task | Agent | Files | Tests | Status |
|-----|------|-------|-------|-------|--------|
| 5.3 | #6, #9 | integration-tests-architect | handlers.ts, data.ts, setup.ts, app-integration.test.tsx | 8 | 🟢 Phase 1 |
| 5.4 | #7, #10 | general-purpose | activities.go, workflows.go, test_minio_snapshots.py, service.go | 1 | 🟢 Phase 1 |
| 5.5 | #8, #11 | general-purpose | testData.ts, api-mocks.ts, table-accessibility.a11y.spec.ts | 6 | 🟢 Phase 1 |

### Timeline & Checkpoints

```
T+0 min   [START] Wave 1 Phase 1
          - handlers.ts (3 endpoints)
          - activities.go (3 activities)
          - testData.ts (10 items)

T+15 min  [CHECKPOINT 1] Phase 1 Complete
          Reports expected:
          - Gap 5.3: "handlers & fixtures ready"
          - Gap 5.4: "activities & workflows ready"
          - Gap 5.5: "table data & handlers ready"

          Team lead action:
          ✓ Acknowledge all 3 agents
          ✓ Verify bun build + go build pass
          ✓ Clear agents to Phase 2
          ✓ ASSIGN WAVE 2 AGENTS (see below)

T+30 min  [CHECKPOINT 2] Phase 2 Complete
          Reports expected:
          - Gap 5.3: "cleanup & helpers ready"
          - Gap 5.4: "workflows ready"
          - Gap 5.5: "fixtures ready"

          Action: Clear to Phase 3

T+45 min  [CHECKPOINT 3] Phase 3 Complete
          Reports expected:
          - Gap 5.3: "8 tests re-enabled"
          - Gap 5.4: "1 test re-enabled"
          - Gap 5.5: "6 tests re-enabled"

          Action: Clear to Phase 4 (final validation)

T+60 min  [CHECKPOINT 4] Phase 4 Complete = WAVE 1 DONE
          Reports expected:
          - Gap 5.3: "8/8 passing, 5x flake-free, coverage ≥85%"
          - Gap 5.4: "1/1 passing, MinIO verified"
          - Gap 5.5: "6/6 passing, 5x flake-free, WCAG verified"

          Status: ✅ Wave 1 Complete (15/15 tests)
```

### Documentation

- **Live Tracker:** `/docs/reports/PHASE_5_3_5_5_LIVE_EXECUTION_TRACKER.md`
- **Master Plan:** `/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md` (742 lines)
- **Code Sketches:** Lines 423-651 in master plan

---

## Wave 2: Gaps 5.6-5.8 (Ready for Assignment)

### Agents & Tasks

| Gap | Task | Assignment | Files | Scope | Target |
|-----|------|-----------|-------|-------|--------|
| 5.6 | #20 | API Testing Agent | endpoints.test.ts, handlers.ts, data.ts | 15+ API tests | Tests passing, snapshots, coverage ≥85% |
| 5.7 | #21 | GPU Performance Agent | webgpu-compute.ts, webgl-compute.ts, gpuForceLayout.ts | WebGPU + WebGL compute | 50-100x speedup verified |
| 5.8 | #22 | Spatial Indexing Agent | enhancedViewportCulling.ts, edgeAggregation.test.ts | Edge midpoint indexing | 98% accuracy, <50ms for 5k edges |

### Timeline & Checkpoints

**Launch at T+15 min (after Wave 1 Checkpoint 1)**

```
T+15 min  [START] Wave 2 Phase 1
          ASSIGN agents to Tasks #20, #21, #22
          - Task #20: API Testing Agent → Gap 5.6
          - Task #21: GPU Performance Agent → Gap 5.7
          - Task #22: Spatial Indexing Agent → Gap 5.8

          Wave 2 Phase 1 execution:
          - Gap 5.6: Un-skip tests, setup fixtures
          - Gap 5.7: WebGPU module + baseline test
          - Gap 5.8: Spatial indexing setup

T+30 min  [CHECKPOINT 1] Wave 2 Phase 1 Complete
          Reports expected:
          - Gap 5.6: "test setup & fixtures ready"
          - Gap 5.7: "WebGPU baseline test ready"
          - Gap 5.8: "spatial indexing setup ready"

          Parallel with Wave 1 Checkpoint 2
          Action: Clear to Phase 2

T+45 min  [CHECKPOINT 2] Wave 2 Phase 2 Complete
          Reports expected:
          - Gap 5.6: "15+ tests passing"
          - Gap 5.7: "GPU compute shader working"
          - Gap 5.8: "spatial indexing algorithm verified"

          Parallel with Wave 1 Checkpoint 3
          Action: Clear to Phase 3

T+60 min  [CHECKPOINT 3] Wave 2 Phase 3 Complete
          Reports expected:
          - Gap 5.6: "snapshots validated"
          - Gap 5.7: "performance target achieved"
          - Gap 5.8: "edge case testing complete"

          Parallel with Wave 1 Checkpoint 4 (Wave 1 Done)
          Action: Clear to Phase 4 (final validation)

T+90 min  [CHECKPOINT 4] Wave 2 Phase 4 Complete = WAVE 2 DONE
          Reports expected:
          - Gap 5.6: "15+/15+ passing, snapshots validated, coverage ≥85%"
          - Gap 5.7: "Speedup verified: 50-100x, FPS target met"
          - Gap 5.8: "98% accuracy, <50ms verified, <5% memory overhead"

          Status: ✅ Wave 2 Complete (30+ tests + GPU + spatial)
```

### Documentation

- **Master Plan:** `/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md` (500+ lines)
- **Executive Summary:** `/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_EXECUTIVE_SUMMARY.md`
- **Quick Reference:** `/docs/reference/PHASE_5_GAPS_QUICK_REFERENCE.md` (200 lines)
- **Code Sketches:** Lines 423-651 in master plan

---

## Dual-Wave Execution Timeline

### Condensed Timeline (All Checkpoints)

```
T+0 min:   🟢 Wave 1 Phase 1 START
T+15 min:  ✅ Wave 1 Checkpoint 1 + 🟢 Wave 2 Phase 1 START
T+30 min:  ✅ Wave 1 Checkpoint 2 + ✅ Wave 2 Checkpoint 1
T+45 min:  ✅ Wave 1 Checkpoint 3 + ✅ Wave 2 Checkpoint 2
T+60 min:  ✅ Wave 1 COMPLETE (15/15) + ✅ Wave 2 Checkpoint 3
T+90 min:  ✅ Wave 2 COMPLETE (30+ + GPU + spatial)

TOTAL: ~90 min (vs 180+ sequential)
EFFICIENCY: 50% time savings with parallelization
```

### Parallel Checkpoint Monitoring

**Wave 1 Checkpoints:**
- T+15: Phase 1 → 2
- T+30: Phase 2 → 3
- T+45: Phase 3 → 4
- T+60: Complete

**Wave 2 Checkpoints (offset by 15 min):**
- T+30: Phase 1 → 2
- T+45: Phase 2 → 3
- T+60: Phase 3 → 4
- T+90: Complete

**No conflicts:** Different checkpoint times, can run in parallel

---

## Team Lead Actions

### At T+15 (Wave 1 Checkpoint 1)

**Priority 1: Acknowledge Wave 1**
```
"✅ Gap 5.3: Phase 1 complete - handlers & fixtures ready"
"✅ Gap 5.4: Phase 1 complete - activities & workflows ready"
"✅ Gap 5.5: Phase 1 complete - table data & handlers ready"
```

**Priority 2: Verify Compile Checks**
```bash
bun run build           # Should pass
go build ./internal/... # Should pass
```

**Priority 3: Clear Wave 1 to Phase 2**
```
"All Wave 1 agents proceed to Phase 2"
```

**Priority 4: ASSIGN WAVE 2 AGENTS (Critical)**
```
"Task #20 (Gap 5.6): Assign to API Testing Agent"
"Task #21 (Gap 5.7): Assign to GPU Performance Agent"
"Task #22 (Gap 5.8): Assign to Spatial Indexing Agent"
```

**Priority 5: Brief Wave 2 Agents**
- Point to: `/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md`
- Explain: Checkpoint protocol (T+30, T+45, T+60, T+90)
- Confirm: Code sketches available, support ready

### At T+30, T+45, T+60, T+90

**For Both Waves:**
1. Acknowledge reporting agents
2. Verify compile/test commands pass
3. Clear to next phase
4. Update task board status

---

## Success Criteria

### Wave 1 Success (by T+60)

**Gap 5.3 (8 tests):**
- ✅ 8/8 tests passing
- ✅ 5 consecutive runs without flakes
- ✅ Coverage ≥85%
- ✅ No console errors

**Gap 5.4 (1 test):**
- ✅ 1/1 test passing
- ✅ MinIO upload verified
- ✅ Metadata correctly updated
- ✅ Workflow retry logic working

**Gap 5.5 (6 tests):**
- ✅ 6/6 tests passing
- ✅ 5 consecutive runs without flakes
- ✅ WCAG 2.1 AA compliance verified (jest-axe)
- ✅ Keyboard navigation working

### Wave 2 Success (by T+90)

**Gap 5.6 (15+ tests):**
- ✅ 15+ tests passing
- ✅ API snapshots validated
- ✅ Coverage ≥85%
- ✅ CRUD operations verified

**Gap 5.7 (GPU Compute):**
- ✅ WebGPU module compiles
- ✅ WebGL GPGPU working
- ✅ Speedup measured: 50-100x for 10k+ nodes
- ✅ FPS target: ≥60 FPS maintained
- ✅ Memory: <200MB for 10k nodes

**Gap 5.8 (Spatial Indexing):**
- ✅ Edge midpoint indexing implemented
- ✅ Cohen-Sutherland clipping working
- ✅ Culling accuracy: ≥98%
- ✅ Performance: <50ms for 5k edges
- ✅ Memory overhead: <5%

### Overall Phase 5 Success (by T+90)

- ✅ 80+ tests unblocked and passing
- ✅ 100% acceptance criteria met per gap
- ✅ All CI/CD pipelines green
- ✅ All commits ready for main
- ✅ Performance targets verified
- ✅ Documentation updated

---

## Support Infrastructure

### For Wave 1 Agents

**Reference Documents:**
- `/docs/reports/PHASE_5_3_5_5_LIVE_EXECUTION_TRACKER.md` - Real-time status
- `/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md` - Master plan (742 lines)
- Code sketches: Lines 423-651

**Support Available:**
- Real-time checkpoint monitoring
- Code sketch references for blockers
- Validation command reference
- Escalation procedures

### For Wave 2 Agents

**Reference Documents:**
- `/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md` - Master plan (500+ lines)
- `/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_EXECUTIVE_SUMMARY.md` - Quick start
- `/docs/reference/PHASE_5_GAPS_QUICK_REFERENCE.md` - Checklists

**Support Available:**
- Checkpoint protocol (same as Wave 1)
- Code sketches for WebGPU, GPU compute, spatial indexing
- Performance verification procedures
- Escalation procedures

---

## Risk Mitigation

### Wave 1 Risks (Currently Executing)

| Risk | Mitigation |
|------|-----------|
| Test flakes from async timing | Async helpers library, explicit waits |
| Global state pollution | Global cleanup in afterEach |
| Fixture data inconsistency | Central mockData source |
| MinIO unavailable | Mock S3 adapter fallback |
| WCAG compliance gaps | Template-based test items |

### Wave 2 Risks (Upcoming)

| Risk | Mitigation |
|------|-----------|
| WebGPU not available | Canvas 2D fallback, shader compilation check |
| GPU memory overrun | Memory profiling, edge case testing |
| Spatial indexing accuracy | Test against known coordinates, tolerance tuning |
| Performance regression | Baseline measurements, before/after comparison |
| Browser compatibility | Graceful degradation, feature detection |

---

## Escalation Procedures

### If Agent Reports Blocker

**During Any Checkpoint:**
1. Agent reports blocker with context (gap, phase, error)
2. Team lead acknowledges and gathers details
3. I (coordinator) provide code sketch references
4. If unresolved after 5 min, escalate to tech lead
5. Other agents proceed (no blocking)

### If Validation Fails

**Compile Errors:**
1. Run: `git status` (verify expected files modified)
2. Run: `bun run build` / `go build` (get error details)
3. Reference code sketches for fix
4. Retry compile check

**Test Failures:**
1. Run individual test with verbose output
2. Check test fixtures loaded correctly
3. Verify mock handlers registered
4. Check for async/await issues
5. Reference code sketches for patterns

---

## Communication Protocol

### Checkpoint Reports (Every 15 min)

**Format:**
```
[Gap X] Phase N complete - [deliverables] ready
```

**Example:**
```
Gap 5.3 Phase 1 complete - handlers & fixtures ready
Gap 5.6 Phase 2 complete - 15+ tests passing
```

### Blocker Reports (Immediate)

**Format:**
```
[Gap X] Phase N blocker: [issue] - [attempted fix]
Requesting: [help type]
```

**Example:**
```
Gap 5.4 Phase 2 blocker: MinIO connection timeout - retried with 30s timeout
Requesting: mock S3 adapter reference from code sketches
```

### Completion Reports (Final)

**Format:**
```
[Gap X] Phase 4 COMPLETE - [count]/[count] tests passing, [verifications] verified
```

**Example:**
```
Gap 5.7 Phase 4 COMPLETE - GPU compute verified, 75x speedup achieved, performance target met
```

---

## Summary

✅ **Wave 1:** Live & executing (3 agents, Phase 1 active)
✅ **Wave 2:** Ready & documented (3 gaps, awaiting assignment at T+15)
✅ **Infrastructure:** Checkpoint protocols, code sketches, support ready
✅ **Timeline:** 90 min total (vs 180+ sequential)
✅ **Efficiency:** 50% time savings with dual-wave parallelization

**Next Action:** At T+15, acknowledge Wave 1 Checkpoint 1, then immediately assign Wave 2 agents to Tasks #20, #21, #22.

---

**Document Created:** 2026-02-06
**Status:** Ready for dual-wave execution
**Recommendation:** Launch Wave 2 at T+15 for optimal parallelization
