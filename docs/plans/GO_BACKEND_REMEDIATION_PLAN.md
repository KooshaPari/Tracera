# Go Backend Coverage Remediation Plan
## Using Cursor (Gemini Flash) + Codex CLI Agents

**Current:** 27.6% coverage | **Target:** 85% coverage | **Gap:** 57.4%
**Execution:** 4 parallel work packages via AI agents (not subagents)
**Timeline:** 5-7 hours wall-clock with parallel execution

---

## AGENT ASSIGNMENT (Cursor/Codex/Gemini)

### Work Package 1: Fix Blockers (Codex - 30 min)
**Agent:** Codex CLI (gpt-5.2-codex, workspace-write)
**Scope:** Fix 3 blocking issues preventing test execution

**Command:**
```bash
~/.codex/skills/codex-subagent/scripts/run_codex_subagent.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend \
  --prompt "Fix 3 Go test blockers:
1. Fix services/* build failure (compilation error)
2. Fix search/cross_perspective_search_test.go panic (index out of range at line X)
3. Fix storybook/* assertion failures
Verify all 3,271 tests can execute: go test ./... -v" \
  --mode workspace-write \
  --model gpt-5.2-codex \
  --reasoning high &
```

**Success:** `go test ./...` runs without panics, 3,245/3,271 tests passing

---

### Work Package 2: agents/* Subsystem Tests (Cursor - 90 min)
**Agent:** Cursor Agent (Gemini 2.5 Flash, agent mode)
**Scope:** Add tests for 68 untested functions in agents/* (currently 0% coverage)

**Files:**
- `internal/agents/coordinator.go`
- `internal/agents/coordination.go`
- `internal/agents/distributed_coordination.go`
- `internal/agents/protocol.go`
- `internal/agents/queue.go`

**Cursor Command:**
```bash
# Launch Cursor agent in background mode
cursor agent \
  --task "Create comprehensive test suite for backend/internal/agents/*.go subsystem. Currently 0% coverage on 68 functions. Add:
- 65 unit tests covering all public methods
- 15 integration tests for coordinator workflows
Target: 85%+ coverage on agents/* subsystem.
Files: coordinator.go, coordination.go, distributed_coordination.go, protocol.go, queue.go
Verify: go test ./internal/agents/... -coverprofile=agents-coverage.out && go tool cover -func=agents-coverage.out" \
  --model gemini-2.5-flash \
  --mode background \
  --branch go-agents-tests
```

**Success:** agents/* coverage 0% → 85%+, 80 new tests created

---

### Work Package 3: Low Coverage Packages (Cursor - 90 min)
**Agent:** Cursor Agent (Gemini 2.5 Flash, parallel tracks)
**Scope:** Boost coverage for 4 low-coverage packages

**Targets:**
- search/* (34% → 85%, +51% gap)
- storage/* (18% → 85%, +67% gap)
- server/* (7% → 85%, +78% gap)
- traceability/* (7% → 85%, +78% gap)

**Cursor Command:**
```bash
cursor agent \
  --task "Boost test coverage for 4 low-coverage Go packages:
1. internal/search (34% → 85%): Add +100 unit tests for query builders, filters
2. internal/storage (18% → 85%): Add +120 unit tests for CRUD operations
3. internal/server (7% → 85%): Add +80 unit tests for HTTP handlers
4. internal/traceability (7% → 85%): Add +90 unit tests for link management
Total: +390 tests needed.
Verify each package: go test ./internal/{package}/... -cover" \
  --model gemini-2.5-flash \
  --mode background \
  --branch go-coverage-boost
```

**Success:** All 4 packages at 85%+, 390 new tests

---

### Work Package 4: Rebalance Test Pyramid (Gemini CLI - 120 min)
**Agent:** Gemini CLI (gemini-2.5-flash, code transformation)
**Scope:** Rebalance from 96/4/0 to 70/20/10 distribution

**Current:**
- Unit: 3,151 tests (96%)
- Integration: 120 tests (4%)
- E2E: 0 tests (0%)

**Target:**
- Unit: 2,289 tests (70%) - **Consolidate -862**
- Integration: 655 tests (20%) - **Add +535**
- E2E: 327 tests (10%) - **Add +327**

**Gemini Command:**
```bash
gemini chat --codebase-index \
  "Rebalance Go test pyramid in backend/.

Phase 1 (40 min): Identify 862 redundant unit tests for consolidation
- Focus on: Duplicate table tests, repeated edge cases, redundant mocks
- Output: List of tests to consolidate

Phase 2 (40 min): Create 535 integration tests
- Cross-package workflows (auth + session + db)
- API endpoint flows (handler + repository + db)
- Event streaming (NATS + handlers)

Phase 3 (40 min): Create 327 E2E tests
- Full user workflows (signup → project create → item CRUD)
- OAuth flows end-to-end
- WebSocket real-time updates
- Graph operations

Deliverable: Rebalanced test suite with 70/20/10 distribution
Verify: go test ./... -v | grep -E 'unit|integration|e2e' | wc -l"
```

**Success:** Test pyramid at 70/20/10, total tests ~3,271 (same count, different distribution)

---

## PARALLEL EXECUTION STRATEGY

**Timeline:**
```
T+0:    Launch WP1 (Codex - blockers)
T+30:   WP1 complete → Launch WP2 (Cursor - agents tests)
T+30:   Launch WP3 (Cursor - low coverage) - parallel with WP2
T+30:   Launch WP4 (Gemini - pyramid) - parallel with WP2+3

Wall-clock:
├─ WP1: 30 min (sequential)
├─ WP2: 90 min ┐
├─ WP3: 90 min ├─ PARALLEL (max 120 min)
└─ WP4: 120 min┘

Total: 30 + 120 = 150 minutes (2.5 hours)
```

---

## AGENT CONFIGURATION

### Codex Settings
```bash
--mode workspace-write
--model gpt-5.2-codex (strong model for debugging)
--reasoning high (complex fixes)
```

### Cursor Settings
```bash
--model gemini-2.5-flash (fast, efficient)
--mode background (parallel execution)
--branch go-{task-name} (isolated work)
```

### Gemini Settings
```bash
gemini-2.5-flash (speed for large transformations)
--codebase-index (repo-wide understanding)
chat mode (interactive for complex restructuring)
```

---

## SUCCESS CRITERIA

**After WP1 (Blockers Fixed):**
- ✅ All 3,271 tests can execute
- ✅ No panics or build failures
- ✅ 3,245+ tests passing

**After WP2 (agents/* Tests):**
- ✅ agents/* coverage: 0% → 85%
- ✅ +80 new tests created
- ✅ Coverage overall: 27.6% → ~35%

**After WP3 (Low Coverage Boost):**
- ✅ search, storage, server, traceability all at 85%+
- ✅ +390 new tests created
- ✅ Coverage overall: ~35% → ~60%

**After WP4 (Pyramid Rebalance):**
- ✅ Test distribution: 70/20/10 (unit/integration/e2e)
- ✅ +862 tests consolidated, +862 tests added (integration+e2e)
- ✅ Coverage overall: ~60% → **85%+** ✅

---

## MONITORING & VALIDATION

**After each work package:**
```bash
# Coverage check
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out | grep total

# Test pyramid check
go test ./... -v | grep -oE '\(unit\)|\(integration\)|\(e2e\)' | sort | uniq -c

# Passing rate
go test ./... -json | jq -r 'select(.Action=="pass" or .Action=="fail") | .Action' | sort | uniq -c
```

---

## DELIVERABLES

**Documentation (Already Created):**
- `/docs/reports/BACKEND_GO_QUALITY_AUDIT_2026-02-06.md` (512 lines)
- `/docs/reports/COVERAGE_AUDIT_EXECUTIVE_SUMMARY.md` (348 lines)
- `/docs/reference/BACKEND_COVERAGE_QUICK_REFERENCE.md` (178 lines)

**Code (To Be Created by Agents):**
- WP1: Fixed blocker files (3 files)
- WP2: agents/*_test.go files (5 new files, 80 tests)
- WP3: */low_coverage_test.go files (4 packages, 390 tests)
- WP4: Rebalanced test suite (862 consolidations, 862 additions)

---

## EXECUTION CHECKLIST

- [ ] **T+0:** Launch WP1 (Codex blocker fixes)
- [ ] **T+30:** Verify WP1 complete (all tests runnable)
- [ ] **T+30:** Launch WP2 (Cursor agents/* tests) in background
- [ ] **T+30:** Launch WP3 (Cursor low coverage) in background
- [ ] **T+30:** Launch WP4 (Gemini pyramid) in chat mode
- [ ] **T+150:** Verify all work packages complete
- [ ] **T+150:** Run final coverage report
- [ ] **T+150:** Confirm 85%+ coverage achieved

---

**READY TO EXECUTE:** All work packages defined, agents identified, commands ready.

Next: Launch WP1 immediately, then WP2-4 in parallel at T+30.
