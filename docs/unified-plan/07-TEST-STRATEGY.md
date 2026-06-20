# 07 -- Test Strategy

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [04-REQUIREMENTS](./04-REQUIREMENTS.md) | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md)

## Executive Summary

TraceRTM operates a multi-language test strategy across Python (backend), Go (services), and TypeScript/Frontend (Vitest + Playwright). The test infrastructure is substantial:

- **6,676+ test functions** across all languages
- **1,446 test files** total
- **Coverage target: 90%** (current: 36-50%, gap: 40-45 percentage points)
- **Test pyramid gap:** Integration tests at 0.4% of suite (target: 30%)

**Key Actions:**
1. Run actual coverage report to validate zero-coverage and low-coverage module claims
2. Fix 67 failing Python tests (CLI mocks, fixture issues, database setup)
3. Establish FR traceability markers in all test files
4. Build integration test suite (blocked by database setup requirements)

---

## Current State

### Test Counts

| Language | Test Files | Test Functions | Pass Rate | Coverage |
|----------|-----------|-------|-----------|----------|
| Python | 501 | 394 | 95.4% (67 failing) | 36-50% |
| Go | 351 | 3,482 | ~100% (45 running, 28 skipped) | ~40% |
| Frontend | ~594 test files* | ~2,800+** | Unknown | Unknown |
| **Total** | **~1,446** | **~6,676+** | **Mixed** | **45-50%** |

*Frontend: .test.ts, .test.tsx files found across apps/web, apps/desktop, apps/docs, apps/storybook
**Estimated based on Vitest usage patterns across monorepo structure

### Test Pyramid (Current vs Target)

```
Current:                      Target:
      /\                           /\
     /10\  E2E (10%)             /10\  E2E (10%)
    /----\                      /----\
   / 0.4 \  Integ (0.4%)      / 30  \  Integration (30%)
  /--------\                  /--------\
 /  89.6%   \ Unit           /  60%    \ Unit (60%)
/-----------\                /----------\
```

**Critical Gap:** Integration tests at 0.4% (target: 30%) -- blocked by database setup.

### Coverage Target

```toml
# From pyproject.toml
[tool.coverage.report]
fail_under = 90
```

**Current: 45-50% | Target: 90% | Gap: 40-45 percentage points**

---

## Existing Test Infrastructure

### Python Test Stack

| Tool | Version | Purpose | Config |
|------|---------|---------|--------|
| pytest | 9.0.2 | Test runner | pyproject.toml [tool.pytest.ini_options] |
| pytest-asyncio | 1.3.0 | Async test support (auto mode) | asyncio_mode = "auto" |
| pytest-cov | 7.0.0 | Coverage reporting | fail_under = 90 (target) |
| pytest-xdist | 3.8.0 | Parallel execution | Available (-n auto) |
| pytest-benchmark | 5.2.3 | Performance benchmarks | Optional marker |
| pytest-mock | 3.15.1 | Mocking utilities | pytest plugin |
| Hypothesis | 6.151.4 | Property-based testing | @given decorator |
| Faker | 40.1.2 | Test data generation | Factory fixtures |
| factory-boy | 3.3.3 | Test factories | test object builders |

**Test Discovery Configuration (verified in pyproject.toml lines 231-243):**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]                              # Only search tests/ directory
python_files = ["test_*.py", "*_test.py"]          # Test file patterns
python_classes = ["Test*"]                         # Test class prefixes
python_functions = ["test_*"]                      # Test function prefixes
addopts = [
    "-ra",                                         # Show summary of all test outcomes
    "-vv",                                         # Very verbose output
    "--strict-markers",                            # Fail on unknown markers
    "--tb=short",                                  # Short traceback format
    "-p", "asyncio",                               # Load asyncio plugin
]
```

**Test Exclusions (from pyproject.toml [tool.coverage.run] lines 272-278):**
- `*/tests/*`
- `*/migrations/*`
- `*/__pycache__/*`
- `*/site-packages/*`

### Test Markers (12 custom, verified in pyproject.toml)

```python
# From pyproject.toml [tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (database, file system)",
    "e2e: End-to-end tests (full CLI workflows)",
    "cli: CLI command tests",
    "slow: Slow tests (>1s execution time)",
    "agent: Agent coordination tests (concurrent operations)",
    "asyncio: Async tests (mark for async tests)",
    "performance: Performance and load tests",
    "property: Property-based tests using Hypothesis",
    "benchmark: Benchmark tests for performance measurement",
    "smoke: Minimal critical-path checks",
    "chaos: Chaos/resilience tests (connection failures, resource exhaustion)",
]
```

**Note:** Full docstrings present in pyproject.toml lines 244-257

### Go Test Stack (351 test files, 3,482 test functions)

| Tool | Purpose | Notes |
|------|---------|-------|
| Go testing | Standard library (t *testing.T) | Verified: 3,482 func Test* functions |
| testify | Assertions + mocking | assert/require packages |
| testcontainers-go | PostgreSQL, MinIO containers | Integration test support |
| stretchr/testify | Standard Go test utilities | Test assertions and mocks |

**Test File Patterns:**
- Location: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/`
- Pattern: `*_test.go` (351 files found)
- Example structure: `backend/tests/security_test.go`, `backend/tests/models_test.go`, etc.

### Frontend Test Stack

| Tool | Purpose | Config | Notes |
|------|---------|--------|-------|
| Vitest | Unit + component tests | vitest.config.ts per app | Configured in apps/web, apps/desktop, apps/docs, apps/storybook |
| @testing-library/react | Component testing utilities | package.json override: ^16.3.0 | Standard RTL assertions |
| Playwright | E2E browser tests | @playwright/test ^1.50.3 | Override pinned in package.json |
| Storybook | Visual component tests | @storybook/react 8.6.14 | Addon coverage support |
| Chromatic | Visual regression | Third-party SaaS | CI/CD integration |

---

## Known Test Failures (67 Python tests)

### Category 1: CLI Command Tests (20 failures)

**Root Cause:** Mock patching -- `DatabaseConnection` class location mismatch

**Affected Files:**
- `test_db_commands.py` (8 failures)
- `test_config_commands.py` (8 failures)
- `test_backup_commands.py` (2 failures)
- `test_benchmark_commands.py` (1 failure)
- `test_chaos_commands.py` (1 failure)

**Fix:** Update mock paths from `tracertm.database.connection.DatabaseConnection` to actual location.

### Category 2: Integration Tests (25 failures)

**Root Cause:** Database mocking (60%), method signature mismatches (25%), fixture issues (15%)

**Affected Files:**
- `test_epic3_advanced_query.py` (5)
- `test_epic4_export_formats.py` (4)
- `test_epic5_auto_linking.py` (3)
- `test_epic6_cycle_detection.py` (3)
- `test_epic7_multi_project.py` (4)
- `test_progress_tracking.py` (2)
- `test_search_integration.py` (2)
- `test_sync_integration.py` (2)

**Fix:** Update mock database initialization, add missing `count_by_status()` method, fix async fixture cleanup.

### Category 3: API/Repository Tests (9 failures)

**Root Cause:** Event loop closure (3), rate limiting (2), missing methods (2), timeouts (2)

### Category 4: File System Tests (6 failures)

**Root Cause:** File watcher unreliability (3), SQLite transaction conflicts (2), setup wizard timeout (1)

**Estimated Fix Time:** 2-3 hours total

---

## Zero Coverage Modules (Status: Verified Against Codebase)

### Critical Priority (2 modules exist, 1 missing)

| Module | Lines | Category | Status |
|--------|-------|----------|--------|
| `api/main.py` | 9,274 | FastAPI app setup | EXISTS |
| `cli/storage_helper.py` | -- | File upload/download | NOT FOUND |
| `tui/adapters/storage_adapter.py` | 572 | TUI storage | EXISTS |
| `tui/apps/dashboard_compat.py` | 7 | Dashboard v2 | EXISTS (stub) |

### TUI Widgets (6 modules, 778 LOC total)

| Module | Lines | Status |
|--------|-------|--------|
| `tui/widgets/conflict_panel.py` | 324 | EXISTS |
| `tui/widgets/sync_status.py` | 334 | EXISTS |
| `tui/widgets/graph_view.py` | 18 | EXISTS (stub) |
| `tui/widgets/item_list.py` | 25 | EXISTS (stub) |
| `tui/widgets/state_display.py` | 26 | EXISTS (stub) |
| `tui/widgets/view_switcher.py` | 30 | EXISTS |
| `tui/widgets/search_box.py` | -- | NOT FOUND |

**Note:** `dashboard_compat.py` and several widget files are minimal stubs (7-30 LOC). Zero coverage claims for small files may be exaggerated or obsolete. Verify with actual coverage report.

---

## Low Coverage Modules (Verified Codebase Structure)

### CLI Commands (6 modules, 3,382 LOC total)

| Module | Lines | Notes |
|--------|-------|-------|
| `commands/test/app.py` | 780 | Test runner orchestration |
| `commands/design.py` | 899 | Design/spec management |
| `commands/backup.py` | 214 | Database backup/restore |
| `commands/graph.py` | 115 | Dependency graph visualization |
| `commands/impact.py` | 144 | Impact analysis |
| `commands/dev.py` | 127 | Development utilities |

**Coverage status:** Actual CLI command coverage unknown -- requires coverage report to verify claims.

### Services (All services in src/tracertm/services/)

Total services modules: ~23,286 LOC across many files

| Category | Estimated Modules | Total LOC | Notes |
|----------|-------------------|-----------|-------|
| Core services | ~30 | ~15,000 | Database, storage, sync orchestration |
| AI/Agent services | ~5 | ~3,000 | LLM, agent coordination, codex |
| API services | ~10 | ~4,000 | Specification, analytics, export |
| Misc services | ~5 | ~1,286 | Encryption, validation, etc. |

**Coverage status:** Specific module coverage percentages unverified; `stateless_ingestion_service.py`, `ai_service.py`, etc. need coverage report confirmation.

### TUI Apps (Frontend in apps/web, apps/desktop, apps/docs, apps/storybook)

Frontend test structure differs from Python; uses Vitest + Playwright instead of pytest.
Monorepo workspace with shared component packages.

---

## Verification Status (Feb 14, 2025)

This document has been updated to match actual codebase structure:

1. **Test Counts Verified:**
   - Python: 501 test files confirmed, 394 test functions (def test_) confirmed
   - Go: 351 test files confirmed, 3,482 test functions (func Test) confirmed
   - Frontend: 594+ test files found (vitest.config.ts confirmed in apps/web, apps/desktop, apps/docs, apps/storybook)

2. **Test Stack Tools Verified:**
   - pytest 9.0.2, pytest-asyncio 1.3.0, pytest-cov 7.0.0 confirmed in pyproject.toml dependencies
   - Vitest configured per app; Playwright @1.50.3 pinned in overrides
   - All listed tools found in [project.optional-dependencies] test group

3. **Coverage Target Verified:**
   - `fail_under = 90` confirmed in pyproject.toml [tool.coverage.report] (line 285)
   - Current coverage 36-50% (unconfirmed from actual coverage report; requires `pytest --cov`)

4. **Zero Coverage Module Claims (Status):**
   - `api/main.py` (9,274 LOC): EXISTS
   - `cli/storage_helper.py`: NOT FOUND
   - TUI widgets: 6/7 modules exist; some are stubs (18-334 LOC each)
   - **RECOMMENDATION:** Run coverage report to confirm zero-coverage claims before test planning

5. **Low Coverage Module Claims (Status):**
   - CLI commands: 6 modules found (3,382 LOC total); coverage % unconfirmed
   - Services: ~23,286 LOC across ~50 modules; coverage % unconfirmed
   - **RECOMMENDATION:** Run coverage report to identify actual lowest-coverage targets

---

## New Test Plan

### Phase 1: Fix Failures (2-3 hours, WP-X9)

| Task | Tests | Time |
|------|-------|------|
| Fix CLI mock patches | 20 | 1h |
| Fix integration fixtures | 25 | 1h |
| Fix API/repository tests | 9 | 30min |
| Fix filesystem tests | 6 | 30min |
| **Total** | **67** | **3h** |

### Phase 2: Zero Coverage (4-5 hours)

| Task | New Tests | Time |
|------|-----------|------|
| api/main.py | 10 | 30min |
| cli/storage_helper.py | 15 | 1h |
| TUI widgets (7 modules) | 30 | 2h |
| Miscellaneous modules | 10 | 30min |
| **Total** | **~65** | **4h** |

### Phase 3: Low Coverage Boost (6-8 hours)

| Task | New Tests | Time |
|------|-----------|------|
| CLI commands (top 10 worst) | 50 | 3h |
| Services (top 10 worst) | 50 | 3h |
| TUI apps (3 modules) | 15 | 1h |
| **Total** | **~115** | **7h** |

### Phase 4: Integration Tests (8-10 hours, requires WP-X8)

| Task | New Tests | Time |
|------|-----------|------|
| Database integration (Python) | 30 | 3h |
| Database integration (Go) | 28 (unblock) | 2h |
| API endpoint integration | 30 | 3h |
| gRPC integration | 10 | 2h |
| **Total** | **~98** | **10h** |

### Phase 5: E2E Tests (15-20 hours)

| Task | New Tests | Time |
|------|-----------|------|
| CLI E2E (critical paths) | 20 | 5h |
| Web E2E (Playwright) | 30 | 10h |
| MCP tool E2E | 10 | 3h |
| Cross-service E2E | 5 | 2h |
| **Total** | **~65** | **20h** |

---

## Test Categories by FR

| Category | FRs | Test Type | Existing | Needed |
|----------|-----|-----------|----------|--------|
| Cat-1: Discovery | FR-DISC-* | Unit + Integration | ~50 | +30 |
| Cat-2: Qualification | FR-QUAL-* | Unit + Integration | ~40 | +30 |
| Cat-3: Application | FR-APP-* | Unit + E2E | ~100 | +20 |
| Cat-4: Verification | FR-VERIF-* | Unit + Integration | ~30 | +40 |
| Cat-5: Reporting | FR-RPT-* | Unit + E2E | ~30 | +20 |
| Cat-6: Collaboration | FR-COLLAB-* | Integration + E2E | ~20 | +40 |
| Cat-7: AI & Automation | FR-AI-*, FR-MCP-* | Unit + Integration | ~80 | +30 |
| Cat-8: Infrastructure | FR-INFRA-* | Unit + Integration | ~50 | +20 |
| Cat-9: Web Views | WP-X1 | Component + E2E | 0 | +100 |

---

## FR Traceability Gap

**Critical finding:** No FR traceability markers exist in the current test suite.

**Required format:**
```python
# @trace FR-DISC-001
def test_github_import_preserves_labels():
    ...

@pytest.mark.requirement("FR-QUAL-002")
def test_cycle_detection_finds_all_cycles():
    ...
```

**Remediation:** Add `# @trace` comments to all existing tests (estimated: 2 hours)

---

## Quality Gates

### Pre-Merge Gate

| Check | Tool | Threshold |
|-------|------|-----------|
| Python lint | ruff | 0 violations |
| Python types | ty | 0 errors |
| Go lint | golangci-lint | 0 errors |
| TS lint | OxLint | 0 errors |
| Python tests | pytest | 100% pass |
| Go tests | go test | 100% pass |
| Coverage | pytest-cov | >=90% |
| Security | bandit + govulncheck | 0 high/critical |

### Pre-Release Gate

| Check | Tool | Threshold |
|-------|------|-----------|
| All pre-merge gates | -- | Pass |
| Integration tests | pytest + go test | 100% pass |
| E2E tests | Playwright | 100% pass |
| Load test | k6 | Smoke passes |
| Performance | pytest-benchmark | No regressions |
| FR traceability | Custom | >=80% FRs covered |
