# Phase 1-2 Remediation Execution (Session 3)

**Initiated:** 2026-02-06 ~03:00 UTC
**Status:** 9 parallel agents executing
**Target:** Achieve GATE C (85%+ tests) + GATE D (quality checks) clearance in 45 minutes

## Execution Timeline

### Phase 1: Quick Wins (T+0 to T+15 min)
**Agents (3 parallel):**
- `go-build-fixer` (#45): Fix quota_middleware.go:21 duplicate const
- `auth-handlers-implementer` (#46): Add 4 auth MSW handlers (login, logout, refresh, user)
- `operator-precedence-fixer` (#47): Fix UICodeTracePanel.test.tsx:471-475 operator precedence

**Expected Completion:** T+15 min
**Success Metric:** All 3 agents report completion without errors

### Phase 2: GATE D Quality Checks (T+15 to T+45 min)
**Agents (6 parallel):**
- `turbo-gitignore-fixer` (#48): Add .turbo/daemon to .gitignore
- `pytest-config-fixer` (#49): Fix pytest.ini testpaths
- `protobuf-dependency-fixer` (#50): Add protobuf to Python dependencies
- `unused-vars-cleaner` (#51): Remove 6 unused imports/variables
- `docs-reorganizer` (#52): Move 8 markdown files to docs/ subdirectories
- `naming-violations-fixer` (#53): Fix 2 naming violations

**Expected Completion:** T+45 min
**Success Metric:** All 6 agents report completion, `make validate` exits with code 0

## Validation Gates (After Phase 2)

### GATE A: TypeScript Compilation
```bash
cd frontend/apps/web && tsc --noEmit
# Expected: 0 errors
```

### GATE B: Dashboard Tests
```bash
cd frontend/apps/web && bun run test -- src/__tests__/pages/Dashboard.test.tsx
# Expected: 21/21 passing
```

### GATE C: Test Suite Threshold
```bash
cd frontend/apps/web && bun run test:unit --coverage
# Expected: ≥85% pass rate (currently at 84.2%, need 27+ tests)
```

### GATE D: Quality Checks
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace && make validate
# Expected: exit code 0
```

## Next Phase (Phase 3) - Ready for Dispatch

Once Phase 1-2 complete and gates pass, immediately dispatch **Phase 3 agents**:

### Phase 3: Production Blockers (Critical Path)
**Team Size:** 9 sonnet agents (with 1 critical-path sequenced)
**Duration:** 24h wall-clock (with parallelization)

**Execution Model:**
- Phase 3.1: Auth system (1-2h) - Parallel
- Phase 3.2: Handler registration (2h) - Parallel with 3.1
- Phase 3.3: API type safety (3h) - Parallel with 3.1-3.2
- **Phase 3.4: Sync engine (24h) - CRITICAL PATH, sequential**
- Parallel work during 3.4: Frontend types (3h), Route implementations (4h), Integration tests (5h)

**Critical File:** `src/tracertm/storage/sync_engine.py` lines 621, 704, 781, 813 (4 TODO stubs)

## Communication Protocol

**From agents to coordinator:**
- Report completion status in message summary (5-10 words)
- Include any blockers or anomalies
- Mark task as completed when done

**From coordinator to agents:**
- Acknowledge each completion
- Dispatch next phase when gates pass
- Provide critical path guidance for Phase 3

## Monitoring Checkpoints

- **T+15:** Phase 1 completion - verify 3 agents done
- **T+30:** Phase 2 halfway - check progress on longer tasks
- **T+45:** Phase 2 completion - run validation gates
- **T+50:** Phase 3 dispatch (if gates pass) - send briefing to all 9 agents

## Rollback Strategy

If any Phase 1-2 agent fails:
1. Identify which task failed
2. Manually verify the issue
3. Re-dispatch with corrected instructions
4. Restart validation

All changes are locally committed after Phase 2 completion with tag: `v0.2.0-remediation-phase-1-2`

---

**Status:** LIVE - Waiting for agent messages at T+15, T+45 checkpoints
