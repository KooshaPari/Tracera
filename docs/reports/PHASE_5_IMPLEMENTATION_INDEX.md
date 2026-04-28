# Phase 5 Implementation Index

**Date:** 2026-02-05
**Status:** Planning & Delegation Complete
**Total Scope:** Close 6 critical gaps → 15 tests total
**Execution Model:** Parallel agent-driven implementation
**Est. Duration:** ~90 minutes (parallel)

---

## Quick Navigation

### Phase 5.3-5.5: First Wave (15 tests, 45-90 min)

| Gap | Tests | Status | Plan | Quick Start | Tracking |
|-----|-------|--------|------|-----------|----------|
| **5.3** Frontend Integration | 8 | Delegated | [Plan](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) | [QS](docs/guides/quick-start/PHASE_5_3_5_5_AGENT_QUICK_START.md) | Task #6, #9 |
| **5.4** Temporal Snapshot | 1 | Delegated | [Plan](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) | [QS](docs/guides/quick-start/PHASE_5_3_5_5_AGENT_QUICK_START.md) | Task #7, #10 |
| **5.5** E2E Accessibility | 6 | Delegated | [Plan](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) | [QS](docs/guides/quick-start/PHASE_5_3_5_5_AGENT_QUICK_START.md) | Task #8, #11 |

### Phase 5.6-5.8: Second Wave (15+ tests, ~45 min)

| Gap | Tests | Status | Plan | Quick Start | Tracking |
|-----|-------|--------|------|-----------|----------|
| **5.6** API Endpoints | 15+ | Planned | [Plan](docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md) | [Ref](docs/reference/PHASE_5_GAPS_QUICK_REFERENCE.md) | Task #20 |
| **5.7** GPU Shaders | 3+ | Planned | [Plan](docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md) | [Ref](docs/reference/PHASE_5_GAPS_QUICK_REFERENCE.md) | Task #21 |
| **5.8** Spatial Index | 1 | Planned | [Plan](docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md) | [Ref](docs/reference/PHASE_5_GAPS_QUICK_REFERENCE.md) | Task #22 |

---

## Wave 1: Phase 5.3-5.5 (15 tests)

### Master Documents
- **Comprehensive Plan:** [PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) (742 lines)
  - Full architecture for all 3 gaps
  - Code sketches & templates (lines 423-651)
  - Risk mitigation & testing strategy
  - Problem analysis & acceptance criteria

- **Orchestration Guide:** [PHASE_5_3_5_5_ORCHESTRATION.md](PHASE_5_3_5_5_ORCHESTRATION.md) (200+ lines)
  - Executive summary
  - Task routing & assignment strategy
  - Timeline & success metrics
  - Team lead checkpoints

- **Delegation Summary:** [PHASE_5_3_5_5_DELEGATION_SUMMARY.md](docs/reports/PHASE_5_3_5_5_DELEGATION_SUMMARY.md)
  - Delegation strategy executed
  - Artifacts created
  - Communication status
  - Progress tracking

- **Agent Quick Start:** [PHASE_5_3_5_5_AGENT_QUICK_START.md](docs/guides/quick-start/PHASE_5_3_5_5_AGENT_QUICK_START.md) (300+ lines)
  - One-pager per gap
  - Execution checklist
  - Validation commands
  - Code snippet templates

### Gap 5.3: Frontend Integration Tests (8 tests)

**Problem:** 8 skipped tests in `app-integration.test.tsx`

**Solution:** Extend MSW handlers, test fixtures, global cleanup, async utilities

**Files:**
```
frontend/apps/web/src/__tests__/
├── mocks/handlers.ts              → Add 3 endpoints
├── mocks/data.ts                  → Add fixtures
├── setup.ts                        → Add cleanup
├── helpers/async-test-helpers.ts  → NEW: utilities
└── integration/app-integration.test.tsx → Re-enable 8 tests
```

**Success:** 8/8 passing, 5x flake-free, ≥85% coverage

**Details:**
- [Implementation Plan](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) (lines 21-109)
- [Code Sketches](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) (lines 423-509)
- [Quick Start](docs/guides/quick-start/PHASE_5_3_5_5_AGENT_QUICK_START.md) (Gap 5.3 section)
- **Tasks:** #6 (tracking), #9 (agent assignment)
- **Est. Duration:** 60-90 minutes

### Gap 5.4: Temporal Snapshot Workflow (1 test)

**Problem:** 1 skipped test requiring Temporal environment

**Solution:** Create activities & workflows, set up test environment, integrate

**Files:**
```
backend/
├── internal/temporal/activities.go     → NEW: 3 activities
├── internal/temporal/workflows.go      → NEW: workflow
├── internal/services/service.go        → Wire integration
└── tests/integration/test_minio_snapshots.py → Add test setup
```

**Success:** 1/1 passing, MinIO verified, metadata updated

**Details:**
- [Implementation Plan](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) (lines 114-234)
- [Code Sketches](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) (lines 511-621)
- [Quick Start](docs/guides/quick-start/PHASE_5_3_5_5_AGENT_QUICK_START.md) (Gap 5.4 section)
- **Tasks:** #7 (tracking), #10 (agent assignment)
- **Est. Duration:** 45-60 minutes

### Gap 5.5: E2E Accessibility Tests (6 tests)

**Problem:** 6 skipped tests requiring table data (7+ rows)

**Solution:** Create table test data, extend handlers, verify WCAG compliance

**Files:**
```
frontend/apps/web/e2e/
├── fixtures/testData.ts              → Add 7+ items
├── fixtures/api-mocks.ts             → Add handler
└── table-accessibility.a11y.spec.ts  → Re-enable 6 tests
```

**Success:** 6/6 passing, WCAG 2.1 AA compliant, keyboard nav verified

**Details:**
- [Implementation Plan](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) (lines 237-368)
- [Code Sketches](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md) (lines 623-651)
- [Quick Start](docs/guides/quick-start/PHASE_5_3_5_5_AGENT_QUICK_START.md) (Gap 5.5 section)
- **Tasks:** #8 (tracking), #11 (agent assignment)
- **Est. Duration:** 30-45 minutes

---

## Wave 2: Phase 5.6-5.8 (15+ tests)

### Master Documents
- **Comprehensive Plan:** [PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md](docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md) (500+ lines)
- **Quick Reference:** [PHASE_5_GAPS_QUICK_REFERENCE.md](docs/reference/PHASE_5_GAPS_QUICK_REFERENCE.md) (200 lines)

### Gap 5.6: API Endpoint Tests (15+ tests)
- **Task:** #20
- **Files:** endpoints.test.ts, handlers.ts, data.ts
- **Success:** All CRUD tests passing, snapshots validated, ≥85% coverage

### Gap 5.7: GPU Compute Shaders (3+ tests)
- **Task:** #21
- **Files:** NEW webgpu-compute.ts, webgl-compute.ts, gpuForceLayout.ts
- **Success:** WebGPU 50-100x speedup, WebGL 20-50x fallback, <100MB memory

### Gap 5.8: Spatial Indexing (1 test)
- **Task:** #22
- **Files:** enhancedViewportCulling.ts, edgeAggregation.test.ts
- **Success:** 98% culling accuracy, <5% memory overhead

---

## Execution Flow

### Setup Phase (5 min)
```
1. Team lead reviews plan
2. Agents claim tasks (#6-#11 for Wave 1, #20-#22 for Wave 2)
3. Agents read assigned gap documentation
```

### Wave 1 Execution (45-90 min parallel)
```
Agent A (Gap 5.3)          Agent B (Gap 5.4)          Agent C (Gap 5.5)
├─ Step 1: MSW Handlers    ├─ Step 1: Activities      ├─ Step 1: Table Data
├─ Step 2: Test Data       ├─ Step 2: Workflows       ├─ Step 2: Handlers
├─ Step 3: Global Cleanup  ├─ Step 3: Test Setup      ├─ Step 3: Fixture
├─ Step 4: Async Helpers   ├─ Step 4: Service Wire    ├─ Step 4: Re-enable
└─ Step 5: Re-enable Tests └─ Step 5: Run & Validate  └─ Step 5: WCAG Check

(All 3 run in parallel → 8/8 + 1/1 + 6/6 = 15/15 passing)
```

### Wave 1 Validation (10 min)
```
- Run all 15 tests 5x in succession (flake detection)
- Verify coverage ≥85%
- Create 3 comprehensive commits
```

### Wave 2 Execution (45 min parallel)
```
Similar parallel structure for Gaps 5.6-5.8
(Similar flow to Wave 1, independent of Wave 1)
```

---

## Task Management

### Wave 1 Tasks
| Task | Gap | Status | Duration |
|------|-----|--------|----------|
| #6 | 5.3 | in_progress | Tracking |
| #7 | 5.4 | in_progress | Tracking |
| #8 | 5.5 | in_progress | Tracking |
| #9 | 5.3 | in_progress | Agent assignment |
| #10 | 5.4 | in_progress | Agent assignment |
| #11 | 5.5 | in_progress | Agent assignment |

### Wave 2 Tasks
| Task | Gap | Status | Duration |
|------|-----|--------|----------|
| #20 | 5.6 | pending | Agent assignment |
| #21 | 5.7 | pending | Agent assignment |
| #22 | 5.8 | pending | Agent assignment |

---

## Success Metrics

### Wave 1 (Phase 5.3-5.5)
| Gap | Target | Current |
|-----|--------|---------|
| **5.3** | 8/8 tests passing | Pending agent execution |
| **5.4** | 1/1 test passing | Pending agent execution |
| **5.5** | 6/6 tests passing | Pending agent execution |
| **Overall** | 15/15 (100%) | Delegated |

### Global Requirements (all phases)
- **Coverage:** ≥85% maintained
- **Flakes:** 0 (5x runs required)
- **Compliance:** WCAG 2.1 AA for a11y tests
- **Commits:** Comprehensive messages with test logs

---

## Communication & Notifications

### Broadcast (2026-02-05)
✅ All teammates notified of Wave 1 execution strategy

### Direct Messages
✅ Team lead briefed on orchestration & success metrics

### Progress Tracking
- Task status via TaskUpdate
- Milestone messages via SendMessage
- Test output in commits

---

## Key Contacts & Roles

| Role | Person | Responsibility |
|------|--------|-----------------|
| **Coordinator** | integration-tests-implementer | Plan & delegate |
| **Team Lead** | team-lead | Approve, monitor, unblock |
| **Agent A** | TBD | Gap 5.3 (8 tests) |
| **Agent B** | TBD | Gap 5.4 (1 test) |
| **Agent C** | TBD | Gap 5.5 (6 tests) |

---

## Resource Links

### Documentation (Alphabetical)
- [Agent Quick Start](docs/guides/quick-start/PHASE_5_3_5_5_AGENT_QUICK_START.md)
- [Delegation Summary](docs/reports/PHASE_5_3_5_5_DELEGATION_SUMMARY.md)
- [Implementation Plan (5.3-5.5)](docs/reports/PHASE_5_3_5_5_IMPLEMENTATION_PLAN.md)
- [Implementation Plan (5.6-5.8)](docs/reports/PHASE_5_GAPS_5_6_5_7_5_8_IMPLEMENTATION_PLAN.md)
- [Orchestration Guide](PHASE_5_3_5_5_ORCHESTRATION.md)
- [Quick Reference (5.6-5.8)](docs/reference/PHASE_5_GAPS_QUICK_REFERENCE.md)

### Tests & Validation Commands

**Wave 1 - Gap 5.3:**
```bash
bun test -- app-integration.test.tsx --reporter=verbose --bail
for i in {1..5}; do bun test -- app-integration.test.tsx; done
```

**Wave 1 - Gap 5.4:**
```bash
make test-backend TEST_TEMPORAL=1 -k test_scheduled_snapshot_workflow
```

**Wave 1 - Gap 5.5:**
```bash
npx playwright test table-accessibility.a11y.spec.ts
npx playwright test table-accessibility.a11y.spec.ts --reporter=html
```

---

## Next Steps

### For Team Lead
1. **Review:** Master plans (Wave 1 & 2)
2. **Approve:** Task delegation strategy
3. **Signal:** Start execution (or agents auto-start)
4. **Monitor:** Task progress via TaskList
5. **Validate:** All 30+ tests passing at completion

### For Agents
1. **Claim:** Task #6-#11 (or wait for assignment)
2. **Read:** Assigned gap in quick-start guide
3. **Execute:** Step-by-step instructions
4. **Validate:** Run tests, verify success criteria
5. **Report:** Commit with comprehensive logs

### Completion Definition
- ✅ Wave 1: 15/15 tests passing (Phase 5.3-5.5)
- ✅ Wave 2: 15+ tests passing (Phase 5.6-5.8)
- ✅ Total: 30+ tests, ≥85% coverage
- ✅ All commits merged to main
- ✅ Phase 5 marked complete

---

## Status Summary

**Planning:** ✅ Complete
**Documentation:** ✅ Complete (1500+ lines)
**Task Routing:** ✅ Complete (6 tasks created)
**Communication:** ✅ Complete (broadcast + direct messages)
**Agent Readiness:** ✅ Ready for execution

**Current Status:** Awaiting agent execution

---

**Last Updated:** 2026-02-05
**Coordinator:** integration-tests-implementer (Claude Haiku 4.5)
**Expected Completion:** 2026-02-05 (~90 minutes from start)
