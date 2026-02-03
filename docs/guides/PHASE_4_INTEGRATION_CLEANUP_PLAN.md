# Phase 4: Integration & Cleanup - Implementation Plan

**Created**: 2026-02-02
**Phase**: 4 (Integration & Cleanup)
**Status**: 🟡 READY FOR EXECUTION
**Dependencies**: Phase 3 Wave 1 Complete

---

## Executive Summary

Phase 4 focuses on **completing the complexity refactoring initiative** by integrating Phase 3 deliverables, extracting remaining high-complexity functions, and achieving final code quality targets. This phase bridges the gap between partial completion and production-ready, maintainable code.

**Core Objectives**:
1. Complete main.py module integration (startup, rate_limiting, websocket)
2. Extract remaining high-complexity Python functions (C901 > 15)
3. Address Python PLR0913 violations (>5 arguments)
4. Convert 10-15 additional Go tests to table-driven format
5. Achieve final code quality targets across all languages

**Strategic Approach**: Sequential phased execution with DAG-based dependencies to ensure zero regressions and smooth integration.

---

## Current Baseline (Phase 3 Exit State)

### Python Backend

| Metric | Current | Details |
|--------|---------|---------|
| **Total C901 Violations** | 138 | Down from 248 (44% reduction in Phase 3) |
| **main.py Line Count** | 10,574 | Target: <9,000 |
| **main.py C901 Count** | 17 violations | Top: list_links (53), startup_event (36), websocket (29) |
| **PLR0913 Violations** | 95 | Too many arguments (>5 params) |
| **Modules Created** | 3 | startup.py, rate_limiting.py, websocket.py (NOT integrated) |
| **Extracted Lines** | ~805 | In modules, not yet removed from main.py |

### Go Backend

| Metric | Current | Details |
|--------|---------|---------|
| **Test Files** | 250 | Total test files in backend |
| **funlen Violations** | Unknown | Need baseline run (golangci-lint not configured) |
| **Table-Driven Tests** | ~10-15% | Most tests still verbose format |
| **Code Duplication** | Reduced | Phase 3 eliminated distributed coordination dupl |

### Frontend

| Metric | Current | Status |
|--------|---------|--------|
| **jsx-max-depth** | Deferred | Phase 3 did not address frontend |
| **Complexity** | Unknown | Needs baseline measurement |

---

## Phase 4 Success Criteria

### Quantitative Targets

| Metric | Current | Target | Reduction |
|--------|---------|--------|-----------|
| **Python C901** | 138 | <70 | 50% additional |
| **main.py Lines** | 10,574 | <9,000 | 15% reduction |
| **main.py C901** | 17 | <8 | 53% reduction |
| **PLR0913** | 95 | <50 | 47% reduction |
| **Go Table Tests** | ~10-15% | ~30% | +15-20 files |
| **Go funlen** | Unknown | <30 violations | TBD after baseline |

### Qualitative Criteria

- ✅ All Phase 3 modules integrated and tested
- ✅ Zero test failures or regressions
- ✅ CI/CD pipeline green across all checks
- ✅ Test coverage maintained ≥85%
- ✅ No circular dependencies introduced
- ✅ All functions <50 lines (Go) or C901 <15 (Python)
- ✅ Documentation updated for new module structure

---

## Phased Work Breakdown Structure (WBS)

### Phase 4.1: Module Integration (CRITICAL PATH)

**Objective**: Integrate Phase 3 extracted modules into main.py
**Priority**: P0 (BLOCKING)
**Risk**: MEDIUM
**Estimated**: 5-8 tool calls, ~4-6 min wall clock

#### Workstreams

**WS-4.1.1: Pre-Integration Preparation**
- Task 4.1.1a: Backup main.py → `main.py.phase3.backup`
- Task 4.1.1b: Verify extracted modules import correctly
- Task 4.1.1c: Document current main.py structure (baseline C901, line count)
- **Depends On**: None
- **Deliverable**: Backup file, import verification report

**WS-4.1.2: Startup Module Integration**
- Task 4.1.2a: Add import `from tracertm.api.config.startup import startup_initialization`
- Task 4.1.2b: Replace `startup_event` function body (lines 688-906) with call to `startup_initialization(app)`
- Task 4.1.2c: Remove old helper functions (cache invalidation, etc.)
- Task 4.1.2d: Test startup sequence with all services
- **Depends On**: WS-4.1.1
- **Deliverable**: Integrated startup, -219 lines, C901 -1

**WS-4.1.3: Rate Limiting Module Integration**
- Task 4.1.3a: Add import `from tracertm.api.config.rate_limiting import enforce_rate_limit`
- Task 4.1.3b: Remove `enforce_rate_limit` function definition (lines 373-428)
- Task 4.1.3c: Verify rate limiting still works (unit test or manual)
- **Depends On**: WS-4.1.2
- **Deliverable**: Integrated rate limiting, -56 lines, C901 -2

**WS-4.1.4: WebSocket Module Integration**
- Task 4.1.4a: Add import `from tracertm.api.handlers.websocket import websocket_endpoint`
- Task 4.1.4b: Replace `websocket_endpoint` function (lines 1245-1323) with call to handler
- Task 4.1.4c: Test WebSocket auth and message loop
- **Depends On**: WS-4.1.3
- **Deliverable**: Integrated websocket, -79 lines, C901 -1

**WS-4.1.5: Integration Verification**
- Task 4.1.5a: Run full test suite (`make test` or `pytest`)
- Task 4.1.5b: Verify ruff C901 violations reduced (17 → 13)
- Task 4.1.5c: Check main.py line count (10,574 → ~10,220)
- Task 4.1.5d: Smoke test all endpoints (health, WebSocket, startup)
- **Depends On**: WS-4.1.4
- **Deliverable**: Test report, C901 verification, smoke test results

---

### Phase 4.2: High-Complexity Extraction (CRITICAL PATH)

**Objective**: Extract remaining C901 > 15 functions from main.py
**Priority**: P0
**Risk**: MEDIUM-HIGH
**Estimated**: 12-18 tool calls, ~10-15 min wall clock

#### Workstreams

**WS-4.2.1: Extract `list_links` (Complexity 53)**
- Task 4.2.1a: Create `src/tracertm/api/handlers/links.py`
- Task 4.2.1b: Extract `list_links` function (line 1620) → focused module
- Task 4.2.1c: Extract helper functions for link filtering, sorting, pagination
- Task 4.2.1d: Create 5-8 focused functions (target complexity <7 each)
- Task 4.2.1e: Integrate into main.py, update imports
- Task 4.2.1f: Test link listing endpoints
- **Depends On**: WS-4.1.5
- **Deliverable**: links.py module (~300-400 lines), C901 -1

**WS-4.2.2: Extract `_list_items_impl` (Complexity 27)**
- Task 4.2.2a: Create `src/tracertm/api/handlers/items.py`
- Task 4.2.2b: Extract `_list_items_impl` (line 1400) → focused module
- Task 4.2.2c: Extract item filtering, query building, pagination logic
- Task 4.2.2d: Create 4-6 focused functions (target complexity <7)
- Task 4.2.2e: Integrate into main.py, update callers
- Task 4.2.2f: Test item listing endpoints
- **Depends On**: WS-4.2.1
- **Deliverable**: items.py module (~200-300 lines), C901 -1

**WS-4.2.3: Extract `oauth_callback` (Complexity 16)**
- Task 4.2.3a: Create `src/tracertm/api/handlers/oauth.py`
- Task 4.2.3b: Extract `oauth_callback` (line 8351) → focused module
- Task 4.2.3c: Extract OAuth state validation, token exchange, redirect logic
- Task 4.2.3d: Create 3-5 focused functions
- Task 4.2.3e: Integrate into main.py
- Task 4.2.3f: Test OAuth flow (mock or real)
- **Depends On**: WS-4.2.2
- **Deliverable**: oauth.py module (~150-200 lines), C901 -1

**WS-4.2.4: Extract Remaining Functions (15 ≥ C901 ≥ 8)**
- Task 4.2.4a: Extract `list_github_repos` (C901: 15) → github.py
- Task 4.2.4b: Extract `api_health_check` (C901: 13) → health.py
- Task 4.2.4c: Extract `stream_chat` (C901: 12) → chat.py
- Task 4.2.4d: Integrate all modules into main.py
- Task 4.2.4e: Test all extracted endpoints
- **Depends On**: WS-4.2.3
- **Deliverable**: 3 modules (~300-400 lines total), C901 -3

**WS-4.2.5: Main.py Verification**
- Task 4.2.5a: Verify main.py line count (<9,500 lines)
- Task 4.2.5b: Verify main.py C901 count (<10 violations)
- Task 4.2.5c: Run full test suite (CI green)
- Task 4.2.5d: Update API documentation
- **Depends On**: WS-4.2.4
- **Deliverable**: main.py <9,500 lines, C901 <10, docs updated

---

### Phase 4.3: PLR0913 Remediation (PARALLEL with 4.2)

**Objective**: Reduce "too many arguments" violations by 50%
**Priority**: P1
**Risk**: LOW-MEDIUM
**Estimated**: 8-12 tool calls, ~6-10 min wall clock

#### Workstreams

**WS-4.3.1: Identify PLR0913 Hotspots**
- Task 4.3.1a: Run `ruff check --select PLR0913` with JSON output
- Task 4.3.1b: Categorize violations by severity (>8 args HIGH, >6 MEDIUM, >5 LOW)
- Task 4.3.1c: Prioritize top 20 functions
- **Depends On**: None (parallel with Phase 4.1)
- **Deliverable**: PLR0913 hotspot report (top 20 functions)

**WS-4.3.2: Apply Remediation Patterns**
- Task 4.3.2a: Pattern 1 - Introduce config objects (dataclasses/Pydantic models)
- Task 4.3.2b: Pattern 2 - Combine related args into grouped params
- Task 4.3.2c: Pattern 3 - Use dependency injection (FastAPI Depends)
- Task 4.3.2d: Refactor 20-25 functions (target 50% reduction: 95 → ~47)
- **Depends On**: WS-4.3.1
- **Deliverable**: PLR0913 violations reduced to <50

**WS-4.3.3: Validation**
- Task 4.3.3a: Re-run ruff PLR0913 check
- Task 4.3.3b: Verify no test failures
- Task 4.3.3c: Document refactoring patterns
- **Depends On**: WS-4.3.2
- **Deliverable**: Validation report, pattern documentation

---

### Phase 4.4: Go Test Conversion (PARALLEL)

**Objective**: Convert 10-15 Go tests to table-driven format
**Priority**: P2
**Risk**: LOW
**Estimated**: 6-10 tool calls, ~5-8 min wall clock

#### Workstreams

**WS-4.4.1: Identify Candidate Tests**
- Task 4.4.1a: Find verbose tests (>50 lines per test case)
- Task 4.4.1b: Find tests with repeated setup/teardown
- Task 4.4.1c: Prioritize 10-15 test files for conversion
- **Depends On**: None (parallel)
- **Deliverable**: Candidate test list (10-15 files)

**WS-4.4.2: Convert Tests**
- Task 4.4.2a: Convert 5 tests (Wave 1)
- Task 4.4.2b: Verify tests pass
- Task 4.4.2c: Convert 5-10 more tests (Wave 2)
- Task 4.4.2d: Verify all tests pass
- **Depends On**: WS-4.4.1
- **Deliverable**: 10-15 converted tests, CI green

**WS-4.4.3: Document Pattern**
- Task 4.4.3a: Create table-driven test pattern guide
- Task 4.4.3b: Add to developer onboarding docs
- **Depends On**: WS-4.4.2
- **Deliverable**: Test pattern guide

---

### Phase 4.5: Go funlen Baseline & Remediation (CONDITIONAL)

**Objective**: Establish Go funlen baseline and reduce violations
**Priority**: P2
**Risk**: LOW
**Estimated**: 4-8 tool calls, ~3-6 min wall clock

#### Workstreams

**WS-4.5.1: Establish Baseline**
- Task 4.5.1a: Configure golangci-lint for backend (funlen enabled)
- Task 4.5.1b: Run baseline: `golangci-lint run backend/ --enable funlen`
- Task 4.5.1c: Count violations, identify top offenders
- **Depends On**: None
- **Deliverable**: Baseline report (funlen violations count)

**WS-4.5.2: Remediate Top Violations (IF violations > 30)**
- Task 4.5.2a: Extract helper functions for top 10-15 long functions
- Task 4.5.2b: Re-run funlen check
- Task 4.5.2c: Target <30 violations
- **Depends On**: WS-4.5.1
- **Deliverable**: funlen <30 violations

---

### Phase 4.6: Final Verification & Documentation (FINAL)

**Objective**: Verify all targets met, update documentation
**Priority**: P0 (BLOCKING COMPLETION)
**Risk**: LOW
**Estimated**: 4-6 tool calls, ~3-5 min wall clock

#### Workstreams

**WS-4.6.1: Final Metrics Collection**
- Task 4.6.1a: Run Python complexity checks (C901, PLR0913, PLR0912, PLR0915)
- Task 4.6.1b: Run Go linting (funlen, gocyclo, dupl)
- Task 4.6.1c: Collect main.py line count and C901 count
- Task 4.6.1d: Generate final metrics report
- **Depends On**: WS-4.2.5, WS-4.3.3, WS-4.4.2, WS-4.5.2
- **Deliverable**: Final metrics report

**WS-4.6.2: Test Suite Validation**
- Task 4.6.2a: Run full Python test suite
- Task 4.6.2b: Run full Go test suite
- Task 4.6.2c: Verify coverage ≥85%
- Task 4.6.2d: CI/CD pipeline green (all checks pass)
- **Depends On**: WS-4.6.1
- **Deliverable**: Test report, coverage report, CI status

**WS-4.6.3: Documentation Updates**
- Task 4.6.3a: Update API architecture docs (new module structure)
- Task 4.6.3b: Update developer onboarding guide
- Task 4.6.3c: Create Phase 4 completion report
- Task 4.6.3d: Update CHANGELOG.md
- **Depends On**: WS-4.6.2
- **Deliverable**: Updated docs, completion report

---

## Dependency DAG (Directed Acyclic Graph)

```
Phase 4.1: Module Integration (CRITICAL PATH)
├─ 4.1.1 (Prep) → 4.1.2 (Startup) → 4.1.3 (Rate Limit) → 4.1.4 (WebSocket) → 4.1.5 (Verify)
                                                                                    ↓
Phase 4.2: High-Complexity Extraction (CRITICAL PATH)                               ↓
└─ 4.2.1 (list_links) → 4.2.2 (_list_items) → 4.2.3 (oauth) → 4.2.4 (others) → 4.2.5 (Verify)
                                                                                    ↓
Phase 4.3: PLR0913 Remediation (PARALLEL)                                          ↓
├─ 4.3.1 (Identify) → 4.3.2 (Refactor) → 4.3.3 (Verify) ────────────────────────→ ┐
                                                                                    │
Phase 4.4: Go Tests (PARALLEL)                                                     │
├─ 4.4.1 (Identify) → 4.4.2 (Convert) → 4.4.3 (Document) ───────────────────────→ ┤
                                                                                    │
Phase 4.5: Go funlen (PARALLEL, CONDITIONAL)                                       │
├─ 4.5.1 (Baseline) → 4.5.2 (Remediate IF needed) ──────────────────────────────→ ┤
                                                                                    ↓
Phase 4.6: Final Verification (FINAL, BLOCKS COMPLETION)                           ↓
└─ 4.6.1 (Metrics) → 4.6.2 (Tests) → 4.6.3 (Docs) ────────────────────────────→ DONE
```

### Execution Strategy

**Wave 1: Critical Path (Sequential)**
- Launch: WS-4.1.1 → 4.1.5 (Module Integration)
- Duration: ~4-6 min wall clock
- Blocker: Must complete before Wave 2

**Wave 2: Main Extraction + Parallel Work (Mixed)**
- Launch: WS-4.2.1 (sequential), WS-4.3.1 (parallel), WS-4.4.1 (parallel), WS-4.5.1 (parallel)
- Duration: ~12-18 min wall clock
- Strategy: Critical path (4.2.x) runs sequentially; PLR0913, Go tests, funlen run in parallel

**Wave 3: Final Verification (Sequential)**
- Launch: WS-4.6.1 → 4.6.3 (Final Verification)
- Duration: ~3-5 min wall clock
- Blocker: Must complete all Wave 2 workstreams

---

## Timeline & Effort Estimates

### Agent-Led Estimates (Aggressive)

| Phase | Workstreams | Tool Calls | Wall Clock | Parallel Agents |
|-------|-------------|------------|------------|-----------------|
| **4.1** | 5 | 5-8 | 4-6 min | 1 (sequential) |
| **4.2** | 5 | 12-18 | 10-15 min | 1 (sequential) |
| **4.3** | 3 | 8-12 | 6-10 min | 1 (parallel) |
| **4.4** | 3 | 6-10 | 5-8 min | 1 (parallel) |
| **4.5** | 2 | 4-8 | 3-6 min | 1 (parallel) |
| **4.6** | 3 | 4-6 | 3-5 min | 1 (sequential) |
| **Total** | 21 | 39-62 | 31-50 min | 1-4 concurrent |

### Wall Clock Breakdown

**Sequential Execution** (1 agent, no parallelization):
- Best Case: 31 min
- Worst Case: 50 min
- Expected: ~40 min

**Parallel Execution** (3-4 agents, Waves 2 parallel):
- Best Case: 17 min (4.1 + 4.2 + max(4.3, 4.4, 4.5) + 4.6)
- Worst Case: 34 min
- Expected: ~25 min

**Recommended**: Parallel execution with 3 agents (Wave 2)

---

## Risk Assessment & Mitigation

### High Risks

**Risk 1: Main.py Integration Breaks Endpoints**
- **Probability**: MEDIUM (30%)
- **Impact**: HIGH (API downtime)
- **Mitigation**:
  - Backup main.py before each integration step
  - Smoke test after each module integration
  - Rollback immediately on test failure
  - Use feature branch, not main
- **Contingency**: Revert to backup, debug in isolation

**Risk 2: Circular Dependencies Introduced**
- **Probability**: LOW (15%)
- **Impact**: MEDIUM (import errors)
- **Mitigation**:
  - Test imports after each extraction
  - Follow module dependency rules (handlers → config → core)
  - Use `pytest --collect-only` to detect import cycles
- **Contingency**: Refactor module boundaries

**Risk 3: Test Failures After Refactoring**
- **Probability**: MEDIUM (25%)
- **Impact**: MEDIUM (CI red, blocks merge)
- **Mitigation**:
  - Run tests after each workstream
  - Maintain 100% test pass rate gate
  - Fix failing tests immediately before proceeding
- **Contingency**: Rollback individual workstream

### Medium Risks

**Risk 4: PLR0913 Refactoring Changes API Signatures**
- **Probability**: LOW (20%)
- **Impact**: MEDIUM (breaking changes)
- **Mitigation**:
  - Only refactor internal functions (not public APIs)
  - Use backward-compatible patterns (default args, **kwargs)
  - Document signature changes
- **Contingency**: Revert or add deprecation warnings

**Risk 5: Go Test Conversion Introduces Logic Errors**
- **Probability**: LOW (10%)
- **Impact**: LOW (tests fail, easy to fix)
- **Mitigation**:
  - Verify test output matches before/after conversion
  - Run tests after each conversion batch
- **Contingency**: Revert test file, retry conversion

### Low Risks

**Risk 6: Documentation Outdated**
- **Probability**: LOW (10%)
- **Impact**: LOW (confusion, no production impact)
- **Mitigation**: Update docs in Phase 4.6
- **Contingency**: Add TODOs, update in Phase 5

---

## Success Metrics & DoD

### Definition of Done (DoD)

**Phase 4.1: Module Integration**
- [x] All 3 modules integrated (startup, rate_limiting, websocket)
- [x] main.py line count reduced by ~350 lines
- [x] C901 violations reduced by 4 (17 → 13)
- [x] All tests pass
- [x] No import errors

**Phase 4.2: High-Complexity Extraction**
- [x] 6 modules created (links, items, oauth, github, health, chat)
- [x] main.py line count <9,000
- [x] main.py C901 <8 violations
- [x] All extracted endpoints tested
- [x] CI green

**Phase 4.3: PLR0913 Remediation**
- [x] PLR0913 violations <50 (from 95)
- [x] Refactoring patterns documented
- [x] No breaking changes (tests pass)

**Phase 4.4: Go Tests**
- [x] 10-15 tests converted to table-driven
- [x] All tests pass
- [x] Pattern guide created

**Phase 4.5: Go funlen**
- [x] Baseline established
- [x] Violations <30 (if baseline >30)

**Phase 4.6: Final Verification**
- [x] Python C901 <70 (from 138, 50% reduction)
- [x] main.py <9,000 lines (from 10,574, 15% reduction)
- [x] PLR0913 <50 (from 95, 47% reduction)
- [x] Go funlen <30
- [x] Test coverage ≥85%
- [x] CI/CD green
- [x] Documentation updated
- [x] Completion report published

---

## Rollback & Contingency

### Per-Phase Rollback

**Phase 4.1**: Revert to `main.py.phase3.backup`
**Phase 4.2**: Revert individual module integrations (git revert per commit)
**Phase 4.3**: Revert PLR0913 refactoring (git revert batch)
**Phase 4.4**: Revert test conversions (git revert per test file)
**Phase 4.5**: Revert funlen fixes (git revert batch)

### Emergency Rollback

**Trigger**: Critical test failures, production incident, or >10% coverage drop
**Action**:
1. Immediately revert all Phase 4 commits
2. Restore from `main.py.phase3.backup`
3. Run full test suite to verify stability
4. Document root cause
5. Re-plan Phase 4 with adjusted scope

---

## Agent Delegation Strategy

### Recommended Agent Assignments

**Agent 1: Integration Lead** (Sequential)
- Phases: 4.1, 4.2, 4.6
- Role: Critical path execution, module integration, final verification
- Estimated: 22-32 tool calls, ~17-26 min wall clock

**Agent 2: PLR0913 Specialist** (Parallel)
- Phase: 4.3
- Role: Argument refactoring, config object introduction
- Estimated: 8-12 tool calls, ~6-10 min wall clock

**Agent 3: Go Test Engineer** (Parallel)
- Phases: 4.4, 4.5
- Role: Test conversion, funlen remediation
- Estimated: 10-18 tool calls, ~8-14 min wall clock

### Agent Coordination

**Wave 1**: Agent 1 only (4.1)
**Wave 2**: Agents 1, 2, 3 (parallel: 4.2 critical path, 4.3, 4.4, 4.5)
**Wave 3**: Agent 1 only (4.6)

---

## Monitoring & Reporting

### Real-Time Metrics

**Track**:
- Python C901 count (per commit)
- main.py line count (per integration)
- PLR0913 count (per batch)
- Test pass rate (after each workstream)
- CI status (continuous)

**Tools**:
- `ruff check --select C901,PLR0913 --statistics`
- `wc -l src/tracertm/api/main.py`
- `pytest --cov=src --cov-report=term`
- GitHub Actions CI dashboard

### Checkpoints

**Checkpoint 1**: After Phase 4.1 (Module Integration)
- Verify: C901 reduced, tests pass, no import errors
- Go/No-Go: Proceed to Phase 4.2

**Checkpoint 2**: After Phase 4.2 (High-Complexity Extraction)
- Verify: main.py <9,000 lines, C901 <8, endpoints tested
- Go/No-Go: Proceed to Phase 4.6

**Checkpoint 3**: After Wave 2 (Parallel Workstreams)
- Verify: All parallel workstreams complete, CI green
- Go/No-Go: Proceed to Phase 4.6

**Checkpoint 4**: Final (Phase 4.6)
- Verify: All targets met, docs updated, completion report ready
- Decision: Close Phase 4, proceed to Phase 5 (if exists) or production

---

## Phase 4 Deliverables

### Code Artifacts

1. **Integrated Modules** (3): startup.py, rate_limiting.py, websocket.py
2. **New Modules** (6): links.py, items.py, oauth.py, github.py, health.py, chat.py
3. **Refactored main.py**: <9,000 lines, C901 <8
4. **Converted Go Tests**: 10-15 table-driven tests
5. **PLR0913 Fixes**: ~45-48 functions refactored

### Documentation

1. **Phase 4 Completion Report** (docs/reports/PHASE_4_COMPLETION_REPORT.md)
2. **Module Architecture Guide** (docs/guides/API_MODULE_STRUCTURE.md)
3. **PLR0913 Refactoring Patterns** (docs/reference/PYTHON_ARG_PATTERNS.md)
4. **Go Table-Driven Test Guide** (docs/reference/GO_TABLE_TESTS.md)
5. **Updated CHANGELOG.md** (Phase 4 section)

### Reports

1. **Final Metrics Report**: Before/after comparison
2. **Test Coverage Report**: Per-module coverage
3. **CI Status Report**: All checks green
4. **Integration Test Report**: Smoke test results

---

## Success Indicators

### Green Flags (Proceed)

- ✅ All tests pass after each workstream
- ✅ C901 count decreasing steadily
- ✅ main.py line count <9,000
- ✅ No import errors
- ✅ CI green
- ✅ Coverage ≥85%

### Yellow Flags (Caution)

- ⚠️ 1-2 test failures (fixable in <10 min)
- ⚠️ Minor import warnings (not errors)
- ⚠️ Coverage 80-84% (acceptable, needs improvement)

### Red Flags (Rollback)

- 🛑 >3 test failures
- 🛑 Circular import errors
- 🛑 Coverage <80%
- 🛑 Production incident related to changes
- 🛑 Critical endpoint broken

---

## Post-Phase 4 Roadmap

### Phase 5 (If Needed): Polish & Optimization

**Potential Scope**:
- Extract remaining C901 violations (8-15 range)
- Address remaining PLR violations (PLR0912, PLR0915)
- Frontend complexity refactoring (jsx-max-depth)
- Performance optimization (if needed)

### Production Readiness

**After Phase 4**:
- Code quality targets met
- Maintainability significantly improved
- Technical debt reduced by 60-70%
- Ready for production deployment

---

## Appendix

### A: File Structure (Post-Phase 4)

```
src/tracertm/api/
├── main.py                    # ~8,500-9,000 lines, C901 <8
├── config/
│   ├── __init__.py
│   ├── startup.py             # Startup initialization
│   └── rate_limiting.py       # Rate limiting enforcement
└── handlers/
    ├── __init__.py
    ├── websocket.py           # WebSocket handler
    ├── links.py               # Link listing (list_links)
    ├── items.py               # Item listing (_list_items_impl)
    ├── oauth.py               # OAuth callback
    ├── github.py              # GitHub repos (list_github_repos)
    ├── health.py              # Health check
    └── chat.py                # Chat streaming
```

### B: Complexity Reduction Summary

| Function | Before | After | Reduction |
|----------|--------|-------|-----------|
| startup_event | 36 | 5 | 86% |
| websocket_endpoint | 29 | 5 | 83% |
| list_links | 53 | <7 | 87% (est.) |
| _list_items_impl | 27 | <7 | 74% (est.) |
| oauth_callback | 16 | <7 | 56% (est.) |
| enforce_rate_limit | 12-14 | 5 | 60-64% |
| list_github_repos | 15 | <7 | 53% (est.) |
| api_health_check | 13 | <7 | 46% (est.) |
| stream_chat | 12 | <7 | 42% (est.) |

### C: Key Commands

**Python Complexity Check**:
```bash
ruff check --select C901,PLR0913 --statistics
```

**Main.py Line Count**:
```bash
wc -l src/tracertm/api/main.py
```

**Go Linting**:
```bash
golangci-lint run backend/ --enable funlen,gocyclo,dupl
```

**Test Suite**:
```bash
pytest --cov=src --cov-report=term
make test
```

**CI Status**:
```bash
gh pr checks
# or GitHub Actions dashboard
```

---

**Document Status**: 🟢 FINAL
**Phase 4 Status**: 🟡 READY FOR EXECUTION
**Next Action**: Launch Wave 1 (Phase 4.1)
**Owner**: BMAD Master / Tech Lead
**Estimated Completion**: 25-40 min wall clock (agent-led)
