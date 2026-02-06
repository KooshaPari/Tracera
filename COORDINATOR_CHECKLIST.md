# Coordinator Checklist & Real-Time Monitoring

**Role:** Team Lead / Coordinator (managing Phase 1-5 execution)
**Team:** production-delivery-phase2
**Status:** 🟡 ACTIVE - Phase 1-2 executing

---

## Current Phase: Phase 1-2 Monitoring

### Phase 1 (T+0 to T+15) - Quick Wins

**Agents Deployed (3):**
- [ ] go-build-fixer (#45) - ⏳ Monitor
- [ ] auth-handlers-implementer (#46) - ⏳ Monitor
- [ ] operator-precedence-fixer (#47) - ⏳ Monitor

**At T+15 (15 minutes from now):**
- [ ] Wait for all 3 agents to send completion messages
- [ ] Verify no errors in Phase 1 outputs
- [ ] Check: Go build clean, auth handlers mocked, TS errors fixed
- [ ] If all success: Proceed to Phase 2
- [ ] If any fail: Investigate and re-dispatch

**Phase 1 Success Criteria:**
- ✅ quota_middleware.go builds without duplicate const error
- ✅ Auth handlers (login, logout, refresh, user) mocked and accessible
- ✅ UICodeTracePanel operator precedence fixed
- ✅ No new TS compilation errors introduced

---

### Phase 2 (T+15 to T+45) - GATE D Quality Checks

**Agents to Deploy at T+15 (6):**
- [ ] turbo-gitignore-fixer (#48)
- [ ] pytest-config-fixer (#49)
- [ ] protobuf-dependency-fixer (#50)
- [ ] unused-vars-cleaner (#51)
- [ ] docs-reorganizer (#52)
- [ ] naming-violations-fixer (#53)

**At T+45 (45 minutes from now):**
- [ ] Wait for all 6 agents to send completion messages
- [ ] Verify no errors in Phase 2 outputs
- [ ] RUN VALIDATION GATES (see below)
- [ ] If all gates pass: Prepare Phase 3 dispatch
- [ ] If any gate fails: Identify blockers and re-dispatch specific agents

**Phase 2 Success Criteria:**
- ✅ .turbo/daemon in .gitignore
- ✅ pytest.ini testpaths correct
- ✅ protobuf imported successfully
- ✅ 6 unused variables removed
- ✅ 8 markdown files moved to docs/
- ✅ 2 naming violations fixed
- ✅ `make validate` exits with code 0

---

## Validation Gates (After Phase 2)

### GATE A: TypeScript Compilation
**Command:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
tsc --noEmit 2>&1 | tail -30
```
**Expected Result:**
- 0 errors
- May have warnings (OK to ignore)

**If fails:** Identify specific TS errors and dispatch targeted fix agent

### GATE B: Dashboard Tests
**Command:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
bun run test -- src/__tests__/pages/Dashboard.test.tsx 2>&1 | tail -50
```
**Expected Result:**
- PASS (21/21 tests passing)
- May have warnings (OK to ignore)

**If fails:** Note which tests fail, they'll be addressed in Phase 4

### GATE C: Test Suite Threshold
**Command:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
bun run test:unit --coverage 2>&1 | grep -E "PASS|FAIL|passed|failed|pass rate" | tail -10
```
**Expected Result:**
- Pass rate ≥85%
- Total: 1700+ tests passing
- Coverage ≥80%

**If fails (currently at 84.2%):** Note specific test failures, Phase 3-4 work will address

### GATE D: Quality Checks
**Command:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
make validate 2>&1 | tail -50
```
**Expected Result:**
- Exit code 0
- No lint/quality errors
- All checks passing

**If fails:** Show specific failing checks and dispatch targeted fix

---

## Phase 1-2 Troubleshooting

### If Agent Doesn't Report in Time

**Wait time:**
- Phase 1 agent: Should report within 10 minutes max
- Phase 2 agent: Should report within 10 minutes max per task (30 min for 6 agents)

**If agent late:**
1. Wait 5 more minutes (network/timing variance)
2. Check agent logs if accessible
3. Re-dispatch with same task if needed
4. Skip and continue if task is non-critical

### If Phase 1 Agent Fails

**Example: go-build-fixer fails**
1. Read error message from agent
2. If "file not found": Verify path `backend/internal/middleware/quota_middleware.go`
3. If "duplicate const not at line 21": Search file for `healthEndpoint` const broadly
4. Re-dispatch with corrected line number or broader search

**Example: auth-handlers-implementer fails**
1. If "cannot find handlers.ts": Verify path `frontend/apps/web/src/__tests__/mocks/handlers.ts`
2. If "MSW setup not working": Provide simpler mock approach (just return 200 OK)
3. Re-dispatch with simpler implementation

### If Gate Fails (Most Likely: GATE C)

**GATE C likely to fail because:** Currently at 84.2%, need 85%+ (need 27 more tests)

**Action if GATE C fails:**
1. Note exact pass rate and count (e.g., 84.5% = 1,695/2,000)
2. Do NOT stop execution - continue to Phase 3
3. Phase 3 and Phase 4 work will improve test results
4. Re-check GATE C after Phase 3 completes
5. Phase 4 specifically targets test recovery

**Do NOT restart from Phase 1 just because GATE C is 84.2% → 85%** - that's expected and will improve

---

## Checkpoint & Handoff Procedures

### T+15 Handoff: Phase 1 → Phase 2

**When Phase 1 agents report (expected T+10-15):**

1. Read each agent's completion message
2. Verify: No errors, no blockers
3. Send acknowledgment:
   ```
   Great work Phase 1 team!
   - go-build-fixer: ✓
   - auth-handlers-implementer: ✓
   - operator-precedence-fixer: ✓

   Phase 2 agents, you're up next - standby for dispatch
   ```
4. Immediately dispatch Phase 2 agents (don't wait for manual gates)

### T+45 Handoff: Phase 2 → Phase 3 (Conditional)

**When Phase 2 agents report (expected T+40-45):**

1. Acknowledge Phase 2 completion
2. Run all 4 validation gates (takes ~5 min)
3. Evaluate results:
   - **All gates pass (A, B, C, D):** → GO to Phase 3 ✅
   - **GATE C fails:** → OK to GO to Phase 3 (will improve with phases 3-4)
   - **GATE A or B fails:** → STOP and fix before Phase 3
   - **GATE D fails:** → STOP and fix (it's the quality gate)

4. Send Phase 3 dispatch briefing (see below)

### T+50 Phase 3 Dispatch (If Gates Pass)

**Send comprehensive briefing to 9 agents:**

```
🚀 PHASE 3 DISPATCH: Production Blockers Remediation

Critical Path Alert: Phase 3.4 (Sync Engine) is 24h sequential task - highest risk/impact

Phase 3 Structure:
- T3.1: Auth system (1-2h) - Parallel
- T3.2: Handler registration (2h) - Parallel with T3.1
- T3.3: API type safety (3h) - Parallel with T3.1-3.2
- T3.4: Sync engine (24h CRITICAL PATH) - Sequential
  - Implement 4 TODO stubs in src/tracertm/storage/sync_engine.py
  - Checkpoints: Every 4h with git commits
  - Lines: 621, 704, 781, 813
- T3.5-7: Parallel with T3.4 (3-5h each)

Success Metric: All 4 sync TODOs implemented, 35+ tests passing, auth working end-to-end

Full plan: /docs/reports/PHASE_3_PRODUCTION_BLOCKERS_PLAN.md

Checkpoints:
- T+4h: T3.4.1 (change detection) complete
- T+8h: T3.4.2 (pull logic) complete
- T+12h: T3.4.3 (application logic) complete
- T+14h: T3.4.4 (conflicts) complete
- T+24h: All Phase 3 tasks complete

Report status every 4h to coordinator.
```

---

## Phase 3-5 Preparation

### Documents Ready for Phase 3+ Briefing

**Phase 3:**
- ✅ Full plan: `docs/reports/PHASE_3_PRODUCTION_BLOCKERS_PLAN.md`
- ✅ 9 agent team assignments (ready to dispatch)
- ✅ Critical file: `src/tracertm/storage/sync_engine.py`
- ✅ Success criteria and checkpoint schedule

**Phase 4:**
- ✅ Full plan: `docs/reports/PHASE_4_TEST_RECOVERY_PLAN.md`
- ✅ 12 agent deployment (4 parallel batches)
- ✅ 536 → 50 failing test target
- ✅ Specific files to fix and test batches

**Phase 5:**
- ✅ Full plan: `docs/reports/PHASE_5_DEFERRED_WORK_PLAN.md`
- ✅ 6 agent deployment (sequential micro-phases)
- ✅ Python TODOs, performance, security, deployment
- ✅ Production readiness checklist

---

## Real-Time Status Updates

### Update `REMEDIATION_EXECUTION_STATUS.md` at Each Checkpoint

**At T+15:**
- [ ] Update Phase 1 status: COMPLETE ✅
- [ ] Update Phase 2 status: EXECUTING 🟡
- [ ] Move to next section

**At T+45:**
- [ ] Update Phase 2 status: COMPLETE ✅
- [ ] Update gate results (A/B/C/D)
- [ ] Update Phase 3 status: DISPATCHED (if gates pass)
- [ ] Move to next section

**At T+24h (end of Phase 3):**
- [ ] Update Phase 3 status: COMPLETE ✅
- [ ] Report sync engine completion status
- [ ] Dispatch Phase 4 briefing
- [ ] Move to next section

**At T+56h (end of Phase 4):**
- [ ] Update Phase 4 status: COMPLETE ✅
- [ ] Report test pass rate
- [ ] Dispatch Phase 5 briefing
- [ ] Move to next section

**At T+82h (end of Phase 5):**
- [ ] Update Phase 5 status: COMPLETE ✅
- [ ] Run final validation (npm audit, safety check, make validate)
- [ ] Report: PRODUCTION READY ✅
- [ ] Move to deployment section

---

## Monitoring Rules

### What to Monitor

**Phase 1-2:** ✅ Straightforward - wait for agent messages

**Phase 3:** ⚠️ HIGH ATTENTION REQUIRED
- Monitor sync engine progress at T+4h intervals
- Check for blockers immediately
- Be ready to help break down stuck tasks
- Verify git commits at each checkpoint

**Phase 4:** ✅ Moderate attention
- Batches run in parallel (less interdependent)
- Monitor overall test pass rate
- Check that fixes are generalizing (not just one test)

**Phase 5:** ⚠️ HIGH ATTENTION REQUIRED
- Security phase (5.3) critical for production
- Deployment phase (5.4) can't have errors
- Be ready to escalate issues

### When to Intervene

**STOP execution if:**
- GATE A fails (TS compilation) - need to fix before proceeding
- GATE D fails (quality checks) - need to fix before proceeding
- Phase 3.4 (sync engine) stuck for >2h - need help

**OK to continue if:**
- GATE B fails (Dashboard tests) - will be fixed in Phase 4
- GATE C fails (test pass rate <85%) - will be fixed in Phases 3-4
- Some Phase 4 tests still failing - expected, working through them

---

## Communication Log

### Messages to Expect

**Phase 1 Agents (T+10-15):**
```
[go-build-fixer] Fixed quota_middleware.go:21 - SUCCESS
[auth-handlers-implementer] Added 4 auth handlers - SUCCESS
[operator-precedence-fixer] Fixed operator precedence - SUCCESS
```

**Phase 2 Agents (T+40-45):**
```
[turbo-gitignore-fixer] Added .turbo/daemon - SUCCESS
[pytest-config-fixer] Fixed pytest.ini - SUCCESS
[protobuf-dependency-fixer] Added protobuf dependency - SUCCESS
[unused-vars-cleaner] Removed 6 unused vars - SUCCESS
[docs-reorganizer] Moved 8 markdown files - SUCCESS
[naming-violations-fixer] Fixed 2 naming violations - SUCCESS
```

### Messages to Send

**At T+15:**
```
✅ PHASE 1 COMPLETE - All 3 agents successful
- Go build fixed
- Auth endpoints mocked
- TS errors resolved

Proceeding with Phase 2 (GATE D checks)
Expected completion: T+45
```

**At T+45:**
```
✅ PHASE 2 COMPLETE - All 6 agents successful
- Gitignore updated
- Pytest configured
- Dependencies fixed
- Variables cleaned
- Docs organized
- Naming corrected

Running validation gates...
```

**After Gates:**
```
Gate Results:
- GATE A (TS): PASS ✅
- GATE B (Dashboard): PASS ✅
- GATE C (Tests): PASS/MARGINALLY (will improve)
- GATE D (Quality): PASS ✅

Dispatching Phase 3 (Production Blockers) - 9 agents, 24h critical path
Expected completion: T+24h from now
```

---

## Emergency Procedures

### If Multiple Phase 1 Agents Fail

1. Stop Phase 2 dispatch
2. Diagnose common cause (e.g., path issue, environment problem)
3. Fix root cause
4. Re-dispatch all Phase 1 agents
5. Proceed to Phase 2 after success

### If Phase 3 Gets Completely Stuck

1. Identify which task is stuck (likely T3.4 sync engine)
2. Check if it's a code understanding issue (not agent fault)
3. Options:
   - Break task into smaller sub-tasks
   - Provide code examples from prior implementation
   - Skip that task and move to Phase 4 (less ideal)
4. Restart task with new approach

### If Production Gates All Fail

1. This is unlikely - gates should mostly pass
2. Investigate which gate failed
3. If multiple gates failed: May indicate environment issue
4. Check: Node version, Python version, build tools
5. Restart from Phase 1 with corrected environment

---

## Success Definition

### Phase 1-2 Complete = Ready for Phase 3
- ✅ All 9 agents reported success
- ✅ GATE A (TS): Passing
- ✅ GATE D (Quality): Passing
- ⚠️ GATE C (Tests): Can be marginal (85%+ ideal, but 84%+ acceptable)

### Phase 3 Complete = Ready for Phase 4
- ✅ Auth system functional
- ✅ Handlers registered
- ✅ API types defined
- ✅ Sync engine 4 TODOs done
- ✅ 35+ production tests passing

### Phase 4 Complete = Ready for Phase 5
- ✅ 95%+ test pass rate
- ✅ <50 failing tests
- ✅ ≥80% coverage
- ✅ No act() warnings

### Phase 5 Complete = Production Ready ✅
- ✅ 0 Python TODOs
- ✅ Dashboard N+1 fixed
- ✅ LCP <2.5s
- ✅ Security audit clean
- ✅ Deployment validated

---

## Key Numbers to Know

**Phase Timelines:**
- Phase 1: 10-15 min (currently executing)
- Phase 2: 30 min (queued for T+15)
- Phase 3: 24h wall-clock (dispatches after gates pass)
- Phase 4: 16h wall-clock (dispatches after Phase 3)
- Phase 5: 26h wall-clock (dispatches after Phase 4)
- **Total: ~75h wall-clock**

**Test Metrics:**
- Current: 84.2% pass rate (~1,895/2,240 tests)
- After Phase 1-2: Expected ~84-85%
- After Phase 3: Expected ~85-90%
- After Phase 4: Expected ~95%+
- Target: 95%+ with ≥80% coverage

**Production Blockers:**
- Phase 3 critical file: `src/tracertm/storage/sync_engine.py` (4 TODO stubs)
- Critical path: Phase 3.4 (24h) - blocks all downstream phases
- Success: All 4 TODOs implemented

---

**Coordinator Status:** 🟢 READY & MONITORING
**Current Time:** T+0 (Phase 1 just launched)
**Next Checkpoint:** T+15 (Phase 1 completion expected)

**Remember:** You have a comprehensive, well-structured plan. Trust the process. Escalate only when agents have genuine blockers.

---

**Document Version:** 1.0
**Created:** 2026-02-06 ~03:05 UTC
**Last Updated:** 2026-02-06 ~03:05 UTC
**Status:** ACTIVE - Coordinator Checklist Ready
