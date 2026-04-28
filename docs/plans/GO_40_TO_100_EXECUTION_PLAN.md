# Go Backend: 40/100 → 100/100 Execution Plan

**Current:** 40/100 (D+) | **Target:** 100/100 (A+) | **Gap:** 60 points
**Timeline:** 5-7 hours with 4 parallel agents
**Agent Assignment:** Cursor (gemini-3-flash) + Gemini CLI (gemini-3-flash)

---

## PHASED WBS

### Phase 1: Fix Blockers (30 min)
**Goal:** All 3,271 tests executable (+10 points)

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| G1-01 | Fix services/* build failure | - | Cursor | 15min | Compiles |
| G1-02 | Fix search panic (index out of range) | - | Cursor | 10min | No panics |
| G1-03 | Fix storybook assertions | - | Cursor | 5min | Tests pass |

**Acceptance:** `go test ./...` runs without panics, 3,245+ tests pass

### Phase 2: Add Critical Tests (90 min, +20 points)
**Goal:** agents/* from 0% → 85%, search/storage from low → 60%

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| G2-01 | Create agents/* unit tests (65 tests) | G1-03 | Cursor | 60min | 85% coverage |
| G2-02 | Create agents/* integration tests (15 tests) | G2-01 | Cursor | 30min | Workflows validated |
| G2-03 | Add search/* tests (100 tests) | G1-02 | Cursor | 45min | 60% → 85% |
| G2-04 | Add storage/* tests (120 tests) | G1-03 | Cursor | 45min | 18% → 85% |

**Acceptance:**
- agents/* coverage: 0% → 85%
- search/* coverage: 34% → 85%
- storage/* coverage: 18% → 85%
- Overall: 27.6% → 45%

### Phase 3: Boost Mid-Tier Packages (90 min, +15 points)
**Goal:** server, traceability, embeddings, integrations to 85%+

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| G3-01 | Add server/* tests (80 tests) | G2-04 | Cursor | 30min | 7% → 85% |
| G3-02 | Add traceability/* tests (90 tests) | G2-04 | Cursor | 30min | 7% → 85% |
| G3-03 | Boost embeddings/* tests (20 tests) | - | Cursor | 15min | 79% → 90% |
| G3-04 | Boost integrations/* tests (15 tests) | - | Cursor | 15min | 77% → 90% |

**Acceptance:** Overall coverage: 45% → 65%

### Phase 4: Rebalance Test Pyramid (120 min, +15 points)
**Goal:** 96/4/0 → 70/20/10 distribution

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| G4-01 | Identify 862 redundant unit tests | G3-04 | Gemini | 30min | Consolidation list |
| G4-02 | Consolidate redundant tests | G4-01 | Gemini | 30min | -862 unit tests |
| G4-03 | Create 535 integration tests | G4-01 | Gemini | 40min | +535 integration |
| G4-04 | Create 327 E2E tests | G4-01 | Gemini | 40min | +327 e2e tests |
| G4-05 | Verify pyramid distribution | G4-02, G4-03, G4-04 | Gemini | 10min | 70/20/10 achieved |

**Acceptance:** Test pyramid: 70% unit, 20% integration, 10% e2e
**Coverage:** 65% → 85%+ overall

---

## DEPENDENCY DAG

```
Phase 1: [G1-01, G1-02, G1-03] (parallel) → BLOCKER GATE
            ↓
Phase 2: G2-01 → G2-02
         G2-03 (parallel with G2-01)
         G2-04 (parallel with G2-01)
            ↓
Phase 3: [G3-01, G3-02, G3-03, G3-04] (all parallel)
            ↓
Phase 4: G4-01 → [G4-02, G4-03, G4-04] (parallel) → G4-05
```

---

## AGENT EXECUTION COMMANDS

### WP1: Fix Blockers (Cursor - 30 min)
```bash
~/.claude/skills/cursor-agent/scripts/run_cursor.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend \
  --prompt "Fix 3 Go test blockers:
1. services/* build failure (compilation error)
2. search/cross_perspective_search_test.go panic (index out of range)
3. storybook/* test assertion failures
Target: All 3,271 tests executable
Verify: go test ./... runs without panics" \
  --mode workspace-write &
```

### WP2: agents/* Tests (Cursor - 90 min)
```bash
~/.claude/skills/cursor-agent/scripts/run_cursor.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend \
  --prompt "Create comprehensive test suite for internal/agents/ (0% → 85%):
- 65 unit tests (coordinator, coordination, distributed_coordination, protocol, queue)
- 15 integration tests (coordinator workflows)
Target: 85%+ coverage
Verify: go test ./internal/agents/... -cover" \
  --mode workspace-write &
```

### WP3: Low Coverage Boost (Cursor - 90 min)
```bash
~/.claude/skills/cursor-agent/scripts/run_cursor.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend \
  --prompt "Boost 4 packages to 85%:
1. search/* (34% → 85%): +100 tests
2. storage/* (18% → 85%): +120 tests
3. server/* (7% → 85%): +80 tests
4. traceability/* (7% → 85%): +90 tests
Verify: go test ./internal/{package}/... -cover shows 85%+" \
  --mode workspace-write &
```

### WP4: Pyramid Rebalance (Gemini - 120 min)
```bash
~/.claude/skills/gemini-agent/scripts/run_gemini.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend \
  --prompt "Rebalance test pyramid (96/4/0 → 70/20/10):
1. Identify 862 redundant unit tests
2. Consolidate -862 unit tests
3. Create +535 integration tests
4. Create +327 E2E tests
Verify: go test ./... -v | grep distribution shows 70/20/10" &
```

---

## SUCCESS CRITERIA

**Phase 1:** ✅ 3,271 tests runnable (blocker gate passed)
**Phase 2:** ✅ agents/* at 85%, search/storage at 85%
**Phase 3:** ✅ server/traceability at 85%, overall at 65%
**Phase 4:** ✅ Pyramid 70/20/10, overall 85%+

**Final Score:** **100/100 (A+)**

---

## TIMELINE

**Parallel Execution:**
- WP1: 30 min (sequential blocker)
- WP2: 90 min (starts after WP1)
- WP3: 90 min (parallel with WP2)
- WP4: 120 min (parallel with WP2+3)

**Total Wall-Clock:** 30 + 120 = **150 min (2.5 hours)**

**Ready to launch.**
