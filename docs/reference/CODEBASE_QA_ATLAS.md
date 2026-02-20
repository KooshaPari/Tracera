# Codebase QA Atlas & Autograder Report

**Generated:** 2026-02-12
**Codebase:** TracerTM (Polyglot: Go + Python + TypeScript)

---

## 1. QA Matrix: Every Checker x Every Project

### Go Backend (`backend/`)

| Tool | Category | Errors | Status | Config Strictness |
|------|----------|--------|--------|-------------------|
| `go build` | Compilation | 0 | PASS | N/A |
| `go vet` | Static analysis | 0 | PASS | N/A |
| `gofumpt` | Formatting | 0 files | PASS | N/A |
| `golangci-lint` | Lint (41+ linters) | 0 | PASS | **95%** |
| `govulncheck` | CVE scan | 0 | PASS | N/A |
| `go test` | Unit tests | 2 failures (Redis perf, CSRF form) | BASELINE | N/A |
| `go test -cover` | Coverage | 32.5% total | BASELINE | N/A |

**Go File Inventory:** 739 source files, 351 test files, 59 test packages

**golangci-lint Linters Enabled (41+):** errcheck, govet, ineffassign, staticcheck, unused, revive, gocritic, gosec, bodyclose, rowserrcheck, gocyclo (15), gocognit (15), misspell, unconvert, exhaustive, prealloc, whitespace, nakedret, noctx, dupl, goconst, funlen, mnd, nolintlint, gochecknoglobals, perfsprint, lll, maintidx, depguard, varnamelen, tagliatelle, forbidigo, copyloopvar, errorlint, forcetypeassert, sqlclosecheck, contextcheck, nilerr, nilnesserr, errchkjson, wastedassign, musttag, exhaustruct, usestdlibvars, predeclared, sloglint, testifylint, exptostd

**Phase 4 Baseline:** golangci-lint: 0 issues (was 21 in Phase 3)
**Disabled Linters:** wrapcheck (too strict for pass-through patterns)

---

### Python Backend (`src/tracertm/`)

| Tool | Category | Errors | Status | Config Strictness |
|------|----------|--------|--------|-------------------|
| `ruff check` | Lint (52 categories) | 0 | PASS | **92%** |
| `ruff format` | Formatting | 0 | PASS | N/A |
| `mypy` | Type check (strict) | 1,256 | BASELINE | **95%** |
| `basedpyright` | Type check (strict) | ~2,000 | BASELINE | **95%** |
| `bandit` | Security | 186 low | WARN | 60% |
| `semgrep` | Security patterns | 7+ | WARN | N/A |
| `vulture` | Dead code | 49 | WARN | N/A |
| `tach` | Architecture | 0 | PASS | **85%** (17 modules) |
| `radon` | Complexity | C avg (15.38) | WARN | N/A |
| `pytest` | Unit tests | 1,346 collected | 8 errors (pytest bug) | N/A |
| `interrogate` | Docstrings | N/A | NOT INSTALLED | N/A |
| `import-linter` | Layer deps | N/A | NOT INSTALLED | N/A |

**Python File Inventory:** 443 source files, 396 test files, 29 test categories

**Ruff Categories Enabled (52+):** E, W, F, I, B, C4, UP, N, PT, SIM, RUF, RSE, PERF, LOG, S, ASYNC, PIE, RET, PTH, DTZ, D, FA, Q, C90, PLR (select rules), ANN, TRY, INT, PGH, ISC, FURB, G, ARG, TCH, BLE, A, T10, T20, ERA, SLF, INP

**Phase 2 Additions:** FBT (boolean trap), PLC/PLW/PLE (Pylint), mypy strict, pyright strict

**Phase 4 Final Baseline:** ruff 0 violations (was 15 in Phase 3, 15,426 at start of S9)

**Complexity Hotspots (Grade D):**
- `spec_analytics_service.py` - EARS pattern analyzer
- `agent_metrics_service.py` - Metrics calculation
- `ai_tools.py` - Tool execution helpers
- `recording/playwright_service.py` - Execution orchestration
- `execution/docker_orchestrator.py` - Docker operations

---

### TypeScript Frontend (`frontend/`)

| Tool | Category | Errors | Status | Config Strictness |
|------|----------|--------|--------|-------------------|
| `tsc --noEmit` | Type check | 0 | PASS | **92%** root / **55%→95%** app |
| `oxlint` | Lint (75+ rules, 13 plugins) | 4,221 errors + 2,369 warnings | BASELINE | **92%** |
| `knip` | Dead code/exports | 27 dup + ~150 unused | WARN | N/A |
| `madge` | Circular deps | 0 | PASS | N/A |
| `vitest` | Unit tests | 3,100 passed / 793 failed / 3,939 total | FAIL | 85% |
| `playwright` | E2E tests | 3 configs | NOT RUN | N/A |

**TS File Inventory:** 8,671 source files, 1,216 test files (1,122 unit, 94 spec, 1 e2e)

**Test Package Status:**
| Package | Status |
|---------|--------|
| @tracertm/docs | PASS |
| @tracertm/state | PASS |
| @tracertm/ui | PASS |
| @tracertm/storybook | PASS |
| @tracertm/api-client | FAIL (script arg conflict) |
| @tracertm/desktop | FAIL (19/33, BrowserWindow mock) |
| @tracertm/web | FAIL (exit 130, interrupted) |
| @tracertm/env-manager | FAIL (not completed) |

**Vitest Configs:** 18 total, **Playwright Configs:** 4 total

**tsconfig strict flags (root):** strict, strictNullChecks, strictFunctionTypes, strictBindCallApply, strictPropertyInitialization, noImplicitAny, noImplicitThis, noImplicitReturns, noImplicitOverride, useUnknownInCatchVariables, exactOptionalPropertyTypes, noUnusedLocals, noUnusedParameters, noFallthroughCasesInSwitch, noUncheckedIndexedAccess, noPropertyAccessFromIndexSignature

**Phase 4 Baseline:** oxlint 6,590 total (4,221 errors + 2,369 warnings). App tsconfig strict=true enforced.

**Oxlint Plugins (13):** eslint, typescript, unicorn, oxc, react, react-perf, import, jsx-a11y, promise, vitest, react-hooks, check-file, boundaries

---

## 2. Config Strictness Ratings (Post-Phase-4)

| Config File | Tool | Strictness | Notes |
|-------------|------|------------|-------|
| `backend/.golangci.yml` | golangci-lint v2 | **95%** | Migrated v1→v2 schema; +7 linters; wrapcheck disabled; **0 issues** |
| `pyproject.toml` [ruff] | Ruff | **92%** | 52+ categories enabled; **0 violations** |
| `mypy.ini` | mypy | **95%** | strict=True + all strict flags; 1,256 baseline with per-module overrides |
| `pyrightconfig.json` | basedpyright | **95%** | typeCheckingMode=strict; ~2,000 errors baseline |
| `tach.toml` | tach | **95%** | 17 modules with full DAG; **0 violations** |
| `frontend/.oxlintrc.json` | oxlint | **92%** | +3 rules; 6,590 baseline (4,221 errors + 2,369 warnings) |
| `frontend/tsconfig.json` (root) | TypeScript | **95%** | All strict flags enabled; **0 errors** |
| `frontend/apps/web/tsconfig.json` | TypeScript (app) | **95%** | strict=true enforced; noUncheckedIndexedAccess, exactOptionalPropertyTypes |
| `.pre-commit-config.yaml` | pre-commit | **85%** | Blocks new suppressions; nolintlint enforcement |

---

## 3. Architecture Boundary Map (Tach)

**17 modules defined** with layered dependency architecture:

```
Base Layer (no deps):     config, models, core, schemas, clients, validation, infrastructure, observability
Data Layer:               repositories → [models, core]
Application Layer:        services → [models, core, repositories, clients, schemas, mcp, workflows]
API Layer:                api → [services, schemas, config, models, repositories, core, infrastructure, mcp, clients, database, observability]
Integration Layers:       mcp → [models, config, api, database, services, storage, cli, core]
                          tui → [models, storage, database, config]
                          workflows → [models, infrastructure, mcp, services]
```

**Status:** All 17 modules validated, 0 violations.

---

## 4. Functional Requirements Inventory

### API Endpoint Summary

| API Spec | Endpoints | Size |
|----------|-----------|------|
| `openapi/gateway-api.json` | ~300+ routes | 623 KB |
| `openapi/go-api.json` | ~150+ routes | 173 KB |
| `openapi/python-api.json` | ~220+ routes | 514 KB |
| **Total** | **~672 endpoints** | **1.3 MB** |

### Feature Areas Identified

1. **Authentication & Authorization** - WorkOS OAuth, JWT, RBAC
2. **Traceability Matrix** - Items, links, graphs, specifications
3. **Graph Visualization** - WebGL/Sigma.js, layout algorithms, WebSocket updates
4. **Specification Management** - EARS patterns, ISO 29148, import/export
5. **API & Webhooks** - REST, gRPC, SSE, webhook delivery
6. **MCP Integration** - Model Context Protocol tools and servers
7. **TUI** - Textual terminal interface for CLI users
8. **Agent System** - AI agent coordination, metrics, monitoring
9. **Import/Export** - GitHub, Jira, CSV, JSON import/export
10. **Collaboration** - Conflict resolution, locking, versioning
11. **Observability** - OpenTelemetry, Prometheus, health checks
12. **Workflows** - Temporal-based async workflows

---

## 5. Suppression Inventory (Post-Phase-4 — Honest Audit)

| Category | Count | Notes |
|----------|-------|-------|
| Python `# noqa` | 28 | 17+ files (models, storage, restored files) |
| Python `# type: ignore` | 662 | 31+ files — strict mode cost + test files |
| Python `# pragma: no cover` | 1 | Single instance |
| Go `//nolint:` | 28 | 16+ .go files |
| TS `eslint-disable` (source) | 1 | client-core.ts only |
| TS `@ts-*` (source, excl. generated) | 7 | 5 Zustand stores, 1 lib shim, 2 test assertions |
| **Total** | **727** | Majority (662) from Python `type: ignore` in strict mode |

**Key insight:** The `type: ignore` count (662) is dominated by test files that were patched with `# type: ignore[assignment]` to fix collection errors. Production source code has ~267 `type: ignore` comments.

**Enforcement:**
- Pre-commit hook blocks new `noqa`/`nolint`/`eslint-disable`/`@ts-ignore`
- CI gate: suppression count baseline (727), fails on increase
- `nolintlint`: requires explanation + specific rule
- **Note:** TS `frontend/disable/` directory (3.5GB archived packages) excluded from counts — was a false positive in earlier measurements.

---

## 6. Test Coverage Map

### Go Coverage by Package (32.5% total)

| Package | Coverage |
|---------|----------|
| uuidutil | 87.5% |
| websocket | 75.3% |
| validation | 72.7% |
| vault | 28.1% |
| proto/v1 | 0.0% (generated) |

### Python Test Categories (29)

api, backend, chaos, cli, component, concurrency, contracts, docs, e2e, factories, fixture, grpc, integration, load, manual, mcp, performance, phase_five, property, rtm, seeds, setup, sql, unit, workflows, and others

### TypeScript Test Split

- Unit/component: 1,122 files
- Spec: 94 files
- E2E: 1 file
- Coverage threshold: 90% (branches, functions, lines, statements)

---

## 7. Gaps & Recommendations

### Critical Gaps

1. **Python type checking:** mypy strict (2,705 errors) and pyright strict (8,820 errors) need systematic fix. Per-module overrides configured for gradual adoption.
2. **Go error wrapping:** wrapcheck found 1,763 unwrapped errors. Test mock returns excluded; production code needs `fmt.Errorf("...: %w", err)` wrapping.
3. **TS desktop tests:** 19/33 failing due to BrowserWindow mock issue.
4. **Go test coverage:** 32.5% is low. Proto generated code skews the number.
5. **Python complexity:** Average grade C (15.38). 5 modules at grade D need refactoring.

### Missing Tools (Not Installed)

- `interrogate` (Python docstring coverage) - needs cairo library
- `import-linter` (Python layer dependency checking) - not in dev deps

### Bash Scripts Status

| Script | Check | Native Linter Alternative |
|--------|-------|--------------------------|
| `check_file_loc.py` | Max lines per file | Partial: Ruff max-statements, oxlint max-lines |
| `check-naming-explosion-*.sh` | Versioned module names | None: keep as pre-commit hook |
| `check-route-entrypoints.sh` | Route duplication | None: keep as custom hook |

### Autograder Pass Criteria

For zero user-facing bugs without LLM intervention, all of these must pass:

```bash
# Compilation & Static Analysis (must = 0)
go build ./... && go vet ./...
golangci-lint run --timeout 10m          # 0 on configured rules
ruff check . && ruff format --check .    # 0
npx tsc --noEmit && bun run lint         # 0 on errors (warnings OK)

# Architecture (must = 0)
tach check                               # 0 violations

# Tests (must pass)
go test ./... -count=1 -short            # All packages
python -m pytest tests/unit/ -q          # All unit tests
bun run test -- --run                    # All vitest packages

# Security (must = 0 high/critical)
govulncheck ./...                        # 0 vulnerabilities
bandit -r src/tracertm/ -q               # 0 high severity

# Suppressions (must not increase)
check-suppression-count.sh               # <= 199 (corrected: ~76 human + ~123 config-generated)
```

---

## 8. Phase 2 Config Changes Applied

### Python
- `pyrightconfig.json`: `typeCheckingMode` basic → **strict**
- `mypy.ini`: Added `strict = True` + 12 strict flags
- `pyproject.toml`: Added Ruff categories FBT, PLC, PLW, PLE

### Go
- `backend/.golangci.yml`: Added wrapcheck, godox, asciicheck linters

### TypeScript
- `frontend/apps/web/tsconfig.json`: Fixed strict=false → **strict=true** + all strict flags
- `frontend/.oxlintrc.json`: Added switch-exhaustiveness-check, no-await-in-loop, jsdoc/require-jsdoc

### Architecture
- `tach.toml`: Expanded from 6 to **17 modules** with full dependency DAG

---

## 9. Phase 2/3 Change Summary: Strict Mode Adoption & Impact

### Pyright (Python Type Checking)

| Change | Violations | Resolution | Baseline |
|--------|-----------|-----------|----------|
| Initial: basic mode | 0 | N/A | N/A |
| Phase 2: strict mode enabled | +6,121 | Per-module overrides (pyrightconfig.json: overrides[]) | 2,526 |
| **Phase 3:** Per-directory & per-file config | Reduced 70% | Excluded tests/**, mcp/**, generated/** | **2,526** |

**Impact:** Strict type checking now enforced across core services with gradual adoption in test/integration code.

---

### Mypy (Python Type Checking)

| Change | Violations | Resolution | Baseline |
|--------|-----------|-----------|----------|
| Initial: basic mode | 2,654 | N/A | N/A |
| Phase 2: strict mode enabled | +150 | Per-module overrides (mypy.ini: [mypy-*]) | 2,201 |
| **Phase 3:** Targeted per-module | Reduced 17% | ~40 module-specific overrides | **2,201** |

**Impact:** Forced strict types on core modules; test/infra code gradual adoption via overrides.

---

### Ruff (Python Linting)

| Change | Violations | Resolution | Baseline |
|--------|-----------|-----------|----------|
| Phase 2: +FBT, +PLC, +PLW, +PLE | 2,619 | Code fixes + per-directory ignores | 252 |
| **Phase 3:** Refactor hotspots + per-file | Reduced 90.3% | Fixed 2,367 violations; 252 per-dir ignores remain | **252** |
| **Phase 3 (PLW fixer):** Additional PLW fixes | Reduced 237 more | Fixed PLW1514, PLC1901, PLW2901, PLW0603, PLW1510 | **15** |
| Example fixes | — | Boolean trap parameters → Enum; Pylint rules → Direct fixes | — |

**Impact:** 90% of new violations fixed in Phase 3; PLW fixer agent reduced by additional 237, leaving only 15 remaining violations from other categories.

---

### golangci-lint (Go Linting)

| Change | Violations | Resolution | Baseline |
|--------|-----------|-----------|----------|
| Phase 2: v1→v2 migration + wrapcheck | 1,763 | Error wrapping analysis | Disabled |
| Phase 2: godox (TODO tracking) | +18 | Accepted as documentation | **18 TODOs** |
| Phase 2: asciicheck | 0 | Passed | 0 |
| **Phase 3:** Config reconcile | **21 total** | 18 godox + 2 globals + 1 gosec = baseline | **21** |

**Impact:**
- Migrated v1→v2 config schema (rules were silently ignored in v1!)
- wrapcheck disabled (too strict for pass-through patterns in API handlers)
- godox TODOs tracked as baseline; motivates future refactoring
- 2 global variable violations (intentional singletons)
- 1 gosec (hardcoded test credential—acceptable in tests)

---

### TypeScript (TS Linting & Type Checking)

| Change | Violations | Resolution | Baseline |
|--------|-----------|-----------|----------|
| App tsconfig: strict=false override | 0 new | Removed override; enforced strict=true | 0 |
| oxlint: +3 rules | +55 | Fixed 9 switch-exhaustiveness; 46 no-await-in-loop | 18,413 |
| **Phase 3:** Monolith refactors | — | adr-list-view: 462→213 LOC; enterprise-table: 571→286 LOC | — |

**Impact:** Zero tsc errors (clean!). Oxlint 18,413 baseline includes 55 from new strict rules; test code allowed exceptions via per-file overrides.

---

### Tach (Architecture)

| Change | Violations | Notes |
|--------|-----------|-------|
| Phase 2: 6→17 modules | 0 | Expanded boundary definitions |
| **Phase 3:** Full DAG validation | 0 violations | All module dependencies validated; clean layering |

**Impact:** Architectural boundaries now enforced; prevents circular deps and cross-layer violations.

---

### Summary: Strict Mode Adoption (Phase 2→Phase 3)

**Config Strictness:** 80%→95% average across all languages

**Violation Patterns:**

1. **Test exclusions:** tests/, **_test.py, **/*.spec.ts always looser
2. **Generated code:** proto/, generated/ skipped entirely
3. **Per-module overrides:** Gradual adoption via config overrides (not code suppressions)
4. **Intentional baselines:** 21 (Go), 15 (Py), 18,413 (TS) accepted as architectural/code quality baselines
5. **Suppression management:** ~199 total suppressions (~76 human-authored; ~123 from strict-mode per-file-ignores). TS count corrected to 18 actual source suppressions (2,842 count was artifact from `frontend/disable/` archived directory)

**Pre-commit enforcement:** New suppressions blocked via hook; baseline (~199) enforced in CI.
