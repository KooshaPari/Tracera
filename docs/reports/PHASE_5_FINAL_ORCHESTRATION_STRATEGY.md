# Phase 5: Final Orchestration Strategy - 3-Wave Parallel Execution

**Date:** 2026-02-06 (Session 3 - Continuous Execution)
**Status:** 🟢 READY FOR LAUNCH
**Timeline:** T+0 to T+90 minutes (90 min wall-clock, 40% faster than sequential)
**Target:** 65+ tests across 8 gaps (Quality: 97-98/100)

---

## EXECUTIVE SUMMARY

Phase 5 implements a **3-wave parallel execution strategy** to close 8 critical gaps with maximum efficiency:

- **Wave 1:** Visual Regression & OAuth (Gaps 5.1-5.2) - 17+ tests, T+0-40
- **Wave 2:** Frontend Integration (Gaps 5.3-5.5) - 15 tests, T+0-60
- **Wave 3:** Performance Layer (Gaps 5.6-5.8) - 30+ tests, T+20-90
- **Wave 4:** Validation & Finalization - T+60+

**Efficiency:** 90 min wall-clock vs 150-180 min sequential = **40% faster**

---

## ORCHESTRATOR ROLE

**Primary Orchestrator:** integration-tests-implementer
**Responsibilities:**
- Coordinate 3-wave parallel execution
- Monitor all checkpoints (T+15, T+30, T+45, T+60, T+75, T+90)
- Manage agent communication (direct messages + broadcasts)
- Deploy waves and escalate blockers
- Trigger Wave 4 validation at T+60+
- Generate Phase 5 completion report

**NOT an implementer** - coordinates agents, doesn't write code for individual gaps

---

## WAVE STRUCTURE & ASSIGNMENTS

### Wave 1: Visual Regression & OAuth (Gaps 5.1-5.2)

**Agent:** visual-regression-implementer
**Tasks:** #13, #14, #15, #16, #17 (5 subtasks)

**Gap 5.1: WebGL Visual Regression Testing**
- Task #13: Un-skip 4 SigmaGraphView unit tests (10 min)
- Task #14: Create 13+ Playwright visual regression specs (20 min)
- Deliverable: 17 tests total
- Reference: implementation-plan.md lines 21-109

**Gap 5.2: OAuth Event Publisher**
- Task #15: Create OAuth event publisher + NATS (25 min)
- Task #16: Configure NATS JetStream Consumer (optional, 15 min)
- Task #17: Wire OAuth handler to event publisher (optional, 10 min)
- Deliverable: 1 publisher test + setup

**Timeline:** T+0 to T+40 (40 min)
**Tests Target:** 17+ (no cross-dependencies with Wave 2)
**Status:** ⏳ READY FOR ASSIGNMENT NOW

---

### Wave 2: Frontend Integration (Gaps 5.3-5.5)

**Agents:** integration-tests-architect, general-purpose (2 agents)
**Tasks:** #6 (Gap 5.3), #7 (Gap 5.4), #8 (Gap 5.5)

**Gap 5.3: Frontend Integration Tests (Task #6)**
- Owner: integration-tests-architect
- Scope: MSW handlers (3+ endpoints), test data, async helpers, global cleanup
- Phases: 5 sequential (handlers → data → cleanup → helpers → re-enable)
- Tests: 8 integration tests
- Timeline: 50 min (4 phases × 10-12 min)
- Checkpoint: Phase 1 done by T+15

**Gap 5.4: Temporal Snapshot Workflow (Task #7)**
- Owner: general-purpose
- Scope: activities.go (3 activities), workflows.go, service integration, test execution
- Phases: 4 sequential (activities → workflows → service → test)
- Tests: 1 temporal snapshot test
- Timeline: 50 min (4 phases × 12-13 min)
- Critical: This test's completion (~T+50) triggers Wave 3 deployment

**Gap 5.5: E2E Accessibility Tests (Task #8)**
- Owner: general-purpose
- Scope: tableTestItems (7+ items), API handlers, fixture setup, WCAG validation
- Phases: 4 sequential (data → handlers → fixtures → validation)
- Tests: 6 accessibility tests
- Timeline: 50 min (4 phases × 12-13 min)
- Compliance: WCAG 2.1 AA

**Overall Timeline:** T+0 to T+60 (60 min)
**Tests Target:** 15 total (8 + 1 + 6)
**Status:** 🟡 EXECUTING Phase 1 NOW

---

### Wave 3: Performance Layer (Gaps 5.6-5.8)

**Agent:** api-performance-implementer
**Tasks:** #20 (Gap 5.6), #21 (Gap 5.7), #22 (Gap 5.8)

**Gap 5.6: API Endpoints Testing (Task #20)**
- Scope: 15+ endpoint tests, contract validation, snapshots
- Phases: 4 sequential (setup → CRUD → advanced → validation)
- Timeline: 40 min (4 phases × 10 min)
- Tests: 15+ endpoint tests
- Deliverable: Contract-validated API tests

**Gap 5.7: GPU Compute Shaders (Task #21) ⭐ CRITICAL PATH**
- Scope: WebGPU + WebGL compute shaders, Fruchterman-Reingold layout
- Phases: 4 sequential
  - Phase 1 (12 min): WebGPU setup (useGPUCompute hook + WGSL shader)
  - Phase 2 (12 min): WebGL fallback (GLSL fragment shaders, texture ping-pong)
  - Phase 3 (10 min): Performance testing (10k nodes benchmark)
  - Phase 4 (6 min): Integration (SigmaGraphView wiring)
- Timeline: 40 min (longest task - determines Wave 3 completion)
- Performance Target: 50-100x speedup (10k nodes <100ms vs ~30s CPU)
- Tests: Benchmarks + integration tests

**Gap 5.8: Spatial Indexing Optimization (Task #22)**
- Scope: Edge midpoint spatial indexing, Cohen-Sutherland clipping, viewport culling
- Phases: 4 sequential
  - Phase 1 (8 min): Spatial index structure (EdgeSpatialIndex class)
  - Phase 2 (8 min): Visibility computation (line clipping algorithm)
  - Phase 3 (10 min): Performance optimization (5k edge benchmark)
  - Phase 4 (6 min): Integration (SigmaGraphView edge rendering)
- Timeline: 32 min
- Optimization Target: 98% culling accuracy, <5% memory overhead, <50ms for 5k edges
- Tests: Spatial indexing + integration tests

**Trigger Gate:** Gap 5.4 test passes (~T+50) = GPU work unblocked
**Deployment Signal:** "WAVE 3 START: All gates clear, begin parallel execution"
**Timeline:** T+20 (trigger) to T+90 (completion), 70 min active execution
**Tests Target:** 30+ (15 + benchmarks + 8)
**Status:** 🟡 STAGED for T+20 deployment

---

### Wave 4: Validation & Finalization

**Coordinator:** integration-tests-implementer (orchestrator)
**Scope:** Flake-free verification, coverage validation, final commits
**Timeline:** T+60 onwards (30 min)
**Status:** ⏳ STANDBY (trigger at T+60 when Wave 2 complete)

---

## CHECKPOINT PROTOCOL (6 CHECKPOINTS)

### Checkpoint 1: T+15 (Wave 2 Phase 1 Validation)
**Focus:** Validate Wave 2 Phase 1 completion across all 3 gaps

**Reports Expected From:**
- Gap 5.3 (integration-tests-architect): MSW handlers (3+ endpoints), test fixtures
- Gap 5.4 (general-purpose): activities.go (3 activities), workflows skeleton
- Gap 5.5 (general-purpose): tableTestItems array (7+ items), API handlers

**Validation Criteria:**
- [ ] Files created/modified confirmed in each report
- [ ] Compilation: bun build, go build, python import all pass
- [ ] Blockers: 0 (or solutions provided)
- [ ] Ready for Phase 2: YES

**Action If Success:**
- Send Phase 2 briefings to all 3 agents
- Clear to proceed to Phase 2 (cleanup, test setup, service wiring)

**Action If Failure:**
- Escalate blockers with code solutions from implementation-plan.md
- Provide direct guidance to fix issues

**Parallel Status:**
- Wave 1: ~10/17 tests executing normally
- Wave 3: Staged and ready

---

### Checkpoint 2: T+30 (Wave 2 Phase 2-3 + Wave 3 Phase 1)
**Focus:** Monitor all 3 waves actively executing

**Expected Status:**
- Wave 1: ~16/17 tests (final tests executing)
- Wave 2: 4-8 tests passing (Phase 2-3 active)
- Wave 3: Phase 1 >50% (fixtures, handlers ready)

**Validation:**
- [ ] No blocking dependencies between waves
- [ ] Critical path (Gap 5.7): Phase 1 started, hook skeleton created
- [ ] Tests compiling without errors

**Action:** Continue monitoring

---

### Checkpoint 3: T+45 (Wave 2 Phase 3-4 + Wave 3 Phase 2)
**Focus:** Wave 2 nearing completion, Wave 3 Phase 2 active

**Expected Status:**
- Wave 1: 17+ tests delivered ✅
- Wave 2: 12-15 tests passing (advanced tests executing)
- Wave 3: Phase 1 complete, Phase 2 starting (WebGL fallback)

**Validation:**
- [ ] Wave 2 approaching completion (most tests passing)
- [ ] Gap 5.7: Phase 1-2 transition, shader compilation verified

**Action:** Prepare Wave 4 validation setup

---

### Checkpoint 4: T+60 (Wave 2 Complete + Wave 3 Phase 2-3)
**Focus:** Wave 2 delivery, Wave 3 mid-execution

**Expected Status:**
- Wave 1: 17+ tests ✅
- Wave 2: 15/15 tests ✅ COMPLETE
- Wave 3: Phase 2-3 active (GPU Phase 2, spatial Phase 2)

**Action:** Trigger Wave 4 validation preparation

---

### Checkpoint 5: T+75 (Wave 3 Phase 3-4)
**Focus:** Wave 3 final phases executing

**Expected Status:**
- Wave 1: 17+ tests (done)
- Wave 2: 15 tests (done)
- Wave 3: Phase 3-4 (performance validation, integration)

**Validation:**
- [ ] GPU performance: 10k nodes benchmark validation
- [ ] Spatial accuracy: 5k edge culling benchmarks
- [ ] All integration tests executing

**Action:** Prepare final commits

---

### Checkpoint 6: T+90 (Phase 5 COMPLETE)
**Focus:** Final delivery and quality validation

**Expected Status:**
- Wave 1: 17+ tests ✅
- Wave 2: 15 tests ✅
- Wave 3: 30+ tests ✅
- **Total: 65+ tests**

**Quality Validation:**
- [ ] Coverage: ≥85% across all gaps
- [ ] Quality Score: 97-98/100
- [ ] Flake-free: 5x consecutive test runs
- [ ] Performance: GPU 50-100x, spatial <50ms
- [ ] WCAG: 2.1 AA compliant (Gap 5.5)

**Action:** Generate Phase 5 completion report

---

## CRITICAL PATH ANALYSIS

**Longest Task:** Gap 5.7 (GPU Compute Shaders) = 40 minutes

**Why Critical:**
- Starts at T+20 (after Gap 5.4 test completes)
- Expected completion: T+60 (when combined with Wave 2)
- Determines overall Phase 5 finish time

**Breakdown:**
- Phase 1 (12 min): T+20-32 (WebGPU setup)
- Phase 2 (12 min): T+32-44 (WebGL fallback)
- Phase 3 (10 min): T+44-54 (Performance testing)
- Phase 4 (6 min): T+54-60 (Integration)

**Monitoring Points:**
- T+25: Phase 1 >25% (device detection, buffer setup)
- T+32: Phase 1 complete, Phase 2 starting
- T+44: Phase 2 complete, Phase 3 starting
- T+60: All phases complete, performance targets verified

**Risk Mitigation:**
- If behind by >5 min at any checkpoint: Escalate immediately
- Provide direct code solutions from implementation-plan.md
- Consider parallel WebGPU + WebGL shader development

---

## AGENT COMMUNICATION PROTOCOL

### Direct Messages (For Individual Agents)
**Used for:**
- Phase completion acknowledgments
- Phase briefings (next phase instructions)
- Blocker escalations with solutions
- Status inquiries

**Format:**
```
"✅ Checkpoint X ACKNOWLEDGED - Phase Y complete/ready
[Phase Y+1 scope and next steps]
Reference: implementation-plan.md lines [X-Y]"
```

### Broadcast Messages (For All Teams)
**Used for:**
- Wave deployments (e.g., "WAVE 3 START")
- Critical status updates (timeline risk)
- Final completion announcement

**Frequency:** Minimal (only major milestones)

### Message Frequency
- **Checkpoints (every 15 min):** Validation + acknowledgment
- **Between checkpoints:** Monitor for blockers, respond immediately
- **No message:** If all agents executing normally

---

## SUCCESS CRITERIA (FINAL DELIVERY)

### By T+90 Completion

**Wave 1 (Gaps 5.1-5.2):**
- ✅ 4 WebGL unit tests passing
- ✅ 13+ Playwright visual regression tests
- ✅ 1 OAuth event publisher test
- ✅ Commit with 17+ tests and documentation

**Wave 2 (Gaps 5.3-5.5):**
- ✅ 8 integration tests (Gap 5.3)
- ✅ 1 temporal snapshot test (Gap 5.4)
- ✅ 6 accessibility tests (Gap 5.5 - WCAG 2.1 AA compliant)
- ✅ All 15 tests passing

**Wave 3 (Gaps 5.6-5.8):**
- ✅ 15+ API endpoint tests (Gap 5.6)
- ✅ GPU compute shaders (Gap 5.7) with:
  - WebGPU hook + WGSL compute shader
  - WebGL fallback (GLSL fragment shaders)
  - Performance: 10k nodes <100ms (50-100x speedup)
- ✅ Spatial indexing (Gap 5.8) with:
  - EdgeSpatialIndex class + R-tree
  - 98% culling accuracy
  - <5% memory overhead
  - <50ms for 5k edges
- ✅ 30+ tests total

**Quality Metrics:**
- ✅ Coverage: ≥85% across all 8 gaps
- ✅ Quality Score: 97-98/100
- ✅ Flake-Free: 5x consecutive runs without failures
- ✅ Performance: All targets met

**Documentation:**
- ✅ 5 comprehensive commits (one per gap family)
- ✅ Phase 5 completion report
- ✅ Lessons learned documented

---

## RESOURCE STAGING

All implementation plans, code sketches, and reference docs are staged and accessible:

**Master Plans (500+ lines each):**
- `/docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md` (Gaps 5.3-5.5)
- `/docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md` (Gaps 5.6-5.8)

**Quick References (200+ lines):**
- `/docs/reference/PHASE_5_GAPS_QUICK_REFERENCE.md`
- `/docs/guides/PHASE_5_GAPS_IMPLEMENTATION_QUICK_START.md`

**Code Sketches (Full Implementation Templates):**
- Gap 5.1-5.2: 100+ lines (visual specs, event publisher)
- Gap 5.3: 90 lines (handlers, data, cleanup, async helpers)
- Gap 5.4: 120 lines (activities, workflows, service integration)
- Gap 5.5: 130 lines (table data, handlers, WCAG validation)
- Gap 5.6: 60 lines (fixtures, handlers, snapshots)
- Gap 5.7: 90 lines (WebGPU + WebGL shader implementation)
- Gap 5.8: 80 lines (spatial index, line clipping, benchmarks)

**Status:** Agents can self-serve implementations from docs

---

## ORCHESTRATION SUMMARY

**Role:** Orchestrator, NOT implementer
**Responsibility:** Coordinate 3-wave parallel execution, manage checkpoints, escalate blockers
**Timeline:** 90 minutes wall-clock (40% faster than sequential)
**Delivery:** 65+ tests across 8 gaps, quality 97-98/100

**Next Immediate Action:** Team lead assign Wave 1 agents (visual-regression-implementer to tasks #13-17) NOW for true 3-wave parallelization.

---

**PHASE 5 READY FOR LAUNCH** 🚀

