# TypeScript Frontend: 85/100 → 100/100 Execution Plan

**Current:** 85/100 (A-) | **Target:** 100/100 (A+) | **Gap:** 15 points
**Timeline:** 2-3 hours with 2 parallel agents
**Agent Assignment:** Cursor (gemini-3-flash) for all tracks

---

## PHASED WBS

### Phase 1: Fix Blockers (30 min)
**Goal:** Unblock CI failures

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| T1-01 | Fix apps/storybook threshold (90% with 0 tests) | - | Cursor | 5min | CI passes |
| T1-02 | Create apps/docs vitest.config.ts | - | Cursor | 10min | Config exists, 75% threshold |
| T1-03 | Verify all packages build | T1-01, T1-02 | Cursor | 15min | 0 build errors |

**Acceptance:** `bun test` runs across all 7 packages without threshold failures

### Phase 2: Coverage Gap Closure (90 min)
**Goal:** apps/web 90% threshold validation

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| T2-01 | Run coverage report for apps/web | T1-03 | Cursor | 10min | Coverage gaps identified |
| T2-02 | Add tests for GraphologyDataLayer (if <90%) | T2-01 | Cursor | 30min | ≥90% coverage |
| T2-03 | Add tests for WebSocket hooks (if <90%) | T2-01 | Cursor | 20min | ≥90% coverage |
| T2-04 | Add tests for Performance utilities (if <90%) | T2-01 | Cursor | 20min | ≥90% coverage |
| T2-05 | Add tests for Routes (if <90%) | T2-01 | Cursor | 10min | ≥90% coverage |

**Acceptance:** `bun test --coverage --project=web` shows ≥90% on all 4 metrics

### Phase 3: Test Pyramid Enhancement (60 min)
**Goal:** Add integration tests (0% → 5%)

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| T3-01 | Design 5 integration test scenarios | T1-03 | Cursor | 15min | Test plan documented |
| T3-02 | Create API integration tests (3 tests) | T3-01 | Cursor | 20min | API flows validated |
| T3-03 | Create state management integration (2 tests) | T3-01 | Cursor | 15min | Zustand flows validated |
| T3-04 | Verify test pyramid distribution | T3-02, T3-03 | Cursor | 10min | 70/15/5/10 achieved |

**Acceptance:** Test pyramid shows 5% integration tests

---

## DEPENDENCY DAG

```
Phase 1: T1-01 ─┐
         T1-02 ─┼→ T1-03
                │
Phase 2:        └→ T2-01 → [T2-02, T2-03, T2-04, T2-05] (parallel)
                              ↓
Phase 3:                   T3-01 → [T3-02, T3-03] (parallel) → T3-04
```

---

## AGENT EXECUTION COMMANDS

### Track 1: Blockers + Coverage (Cursor - 2h)
```bash
~/.claude/skills/cursor-agent/scripts/run_cursor.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend \
  --prompt "Fix TypeScript blockers and coverage gaps:
1. apps/storybook: Change threshold to 0% or add 10 tests (5 min)
2. apps/docs: Create vitest.config.ts with 75% threshold (10 min)
3. apps/web: Run coverage, add tests to reach 90% on all metrics (90 min)
Focus: GraphologyDataLayer, WebSocket hooks, Performance utils, Routes
Verify: bun test --coverage shows ≥90% for apps/web" \
  --mode workspace-write &
```

### Track 2: Test Pyramid (Cursor - 1h)
```bash
~/.claude/skills/cursor-agent/scripts/run_cursor.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend \
  --prompt "Add 5 integration tests to improve pyramid:
1. API client integration (3 tests): auth flow, CRUD operations, error handling
2. State management integration (2 tests): Zustand store workflows
Target: 5% integration tests in test pyramid
Verify: Test distribution shows 70/15/5/10" \
  --mode workspace-write &
```

---

## SUCCESS CRITERIA

**Phase 1:** ✅ All packages build, no threshold failures
**Phase 2:** ✅ apps/web ≥90% coverage on all metrics
**Phase 3:** ✅ 5% integration tests in pyramid

**Final Score:** **100/100 (A+)**

---

## TIMELINE

**Parallel Execution:**
- Track 1: 120 min
- Track 2: 60 min (can start immediately)

**Total Wall-Clock:** ~120 min (2 hours)

**Ready to launch.**
