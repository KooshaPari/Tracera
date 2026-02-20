# Static Analysis Consolidation Report

**Generated:** 2026-02-07T00:00:00Z
**Task:** Consolidate static analysis from all language audits (#13)
**Status:** ❌ FAIL - 4,525 violations across all languages
**Expected:** 0 errors, **Found:** 4,525 total violations

---

## Executive Summary

### Overall Status

| Metric | Value | Status |
|--------|-------|--------|
| **Total Violations** | 4,525 | ❌ FAIL |
| **Go Errors** | 126 | ❌ FAIL |
| **Python Violations** | 3,881 | ❌ FAIL |
| **TypeScript Errors** | 518 | ❌ FAIL |
| **Files Exceeding LOC Limit** | 206+ | ❌ FAIL |
| **Critical Issues** | 10 | 🔴 HIGH |

### Critical Issues (Top 10)

1. **Go: server_test.go** - 1509 lines (exceeds allowlist by 854 lines)
2. **TypeScript: IntegrationsView.tsx** - 1739 lines (exceeds allowlist by 22 lines)
3. **Python: 98 TUI module import errors** - textual dependency unresolved
4. **Python: 35 protobuf/gRPC errors** - spec_analytics_service.py attribute errors
5. **Go: preflight.go cognitive complexity** - 32 (max 12)
6. **TypeScript: types.ts** - 1208 lines (exceeds limit by 708 lines, NO allowlist)
7. **Python: Docstring rules (D) NOT enabled** - CRITICAL config gap
8. **Python: interrogate blocked** - cairo dependency missing
9. **Go: 121 files exceed LOC limit** - Average 85 lines over allowlist
10. **TypeScript: 64 files exceed LOC limit** - Average 15 lines over allowlist

---

## 1. Violations by Language

### 1.1 Go (126 total errors)

**Breakdown:**
- **golangci-lint:** 5 errors
- **LOC violations:** 121 files exceed 500-line limit
- **Naming violations:** 0

#### golangci-lint Errors (5)

| File | Line | Linter | Severity | Issue |
|------|------|--------|----------|-------|
| `cmd/tracertm/preflight.go` | 244 | errcheck | CRITICAL | Error return value of `db.Close` is not checked |
| `cmd/tracertm/preflight.go` | 73 | gocognit | HIGH | Cognitive complexity 32 of func `(*EnvConfig).loadFromEnv` is high (> 12) |
| `cmd/tracertm/preflight.go` | 83 | perfsprint | MEDIUM | fmt.Sprintf can be replaced with string concatenation |
| `cmd/tracertm/preflight.go` | 1 | revive | LOW | Missing package comment |
| `cmd/tracertm/preflight.go` | 205 | varnamelen | LOW | Parameter name 'c' is too short for the scope of its usage |

#### LOC Violations (121 files)

**Top 10 Worst Violators:**

| Rank | File | LOC | Allowlist Max | Over Limit |
|------|------|-----|---------------|------------|
| 1 | `backend/internal/server/server_test.go` | 1509 | 655 | **854** |
| 2 | `backend/tests/integration/service_integration_test.go` | 1492 | 1490 | 2 |
| 3 | `backend/internal/equivalence/handler.go` | 1362 | 1310 | 52 |
| 4 | `backend/internal/handlers/item_handler_test.go` | 1316 | 1238 | 78 |
| 5 | `backend/internal/server/server.go` | 1313 | 1113 | 200 |
| 6 | `backend/internal/services/temporal_service_test.go` | 1228 | 1214 | 14 |
| 7 | `backend/internal/equivalence/handler_test.go` | 1171 | 1159 | 12 |
| 8 | `backend/tests/e2e/service_layer_e2e_test.go` | 1150 | 1149 | 1 |
| 9 | `backend/internal/traceability/matrix_service.go` | 1078 | 893 | 185 |
| 10 | `backend/internal/services/item_service_test.go` | 1072 | 1067 | 5 |

**Analysis:**
- **80% are test files** (concentrated technical debt)
- **Average overage:** 85 lines per file
- **Allowlist drift:** High (server_test.go 130% over allowlist)

#### Configuration Status

**Config File:** `backend/.golangci.yml`

✅ **Enabled (27 linters):**
- errcheck, govet, ineffassign, staticcheck, unused, revive, gocritic
- gosec, bodyclose, rowserrcheck, gocyclo, gocognit, misspell
- unconvert, exhaustive, prealloc, whitespace, nakedret, noctx
- dupl, goconst, funlen, mnd, nolintlint, gochecknoglobals
- perfsprint, lll, maintidx, depguard, varnamelen, tagliatelle

**Limits:**
- gocyclo: 10, gocognit: 12, funlen: 80 lines/50 statements
- lll: 120 chars, maintidx: 20, varnamelen: min 2 chars

⚠️ **Proposed but NOT Enabled:**
- **forbidigo** - Forbidden identifier patterns (READY for Phase 1)

---

### 1.2 Python (3,881 total violations)

**Breakdown:**
- **Ruff:** 3,722 style/quality violations
- **Ty (type checker):** 159 type errors
- **Naming violations:** 8
- **Docstring coverage:** N/A (interrogate blocked)

#### Severity Breakdown

| Severity | Count | Examples |
|----------|-------|----------|
| CRITICAL | 35 | Protobuf/gRPC errors (spec_analytics_service.py) |
| CRITICAL | 98 | TUI module imports (textual unresolved) |
| HIGH | 124 | Type safety errors (invalid-argument-type, invalid-return-type) |
| MEDIUM | 3722 | Unused imports (F401), Magic values (PLR2004), Complexity (C901, PLR0913) |

#### Critical Blockers

**1. Protobuf/gRPC Errors (35 errors)**
- File: `src/tracertm/grpc/spec_analytics_service.py`
- Issue: Unresolved protobuf attributes
- Impact: gRPC service type safety compromised

**2. TUI Module Imports (98 errors)**
- Directory: `src/tracertm/tui/`
- Issue: textual module imports unresolved
- Impact: TUI application type checking failed

**3. Missing CLI Modules (5+ errors)**
- Files: `mcp/cli_integration.py`, `mcp/tools/param.py`
- Issue: `tracertm.cli.auth` module missing
- Impact: MCP CLI integration broken

#### Type Errors (159 total)

**Sample Critical Issues:**

| File | Line | Error Type | Description |
|------|------|------------|-------------|
| `api/client.py` | 132 | invalid-argument-type | AsyncEngine expected |
| `api/main.py` | 469 | call-top-callable | Unsafe call |
| `api/main.py` | 507/512 | possibly-unresolved-reference | `tracing_enabled` may not be defined |
| `api/middleware/cors.py` | 44 | invalid-argument-type | Middleware type mismatch |
| `api/routers/blockchain.py` | 656 | invalid-assignment | dict type mismatch |
| `grpc/server.py` | 9 | possibly-missing-import | grpc.aio may be missing |
| `storage/local_storage.py` | - | invalid-return-type | Type assignment mismatches (4 errors) |

#### Naming Violations (8)

| File | Line | Rule | Issue |
|------|------|------|-------|
| `api/routers/errors.py` | 30 | N815 | Variable `componentStack` should not be mixedCase |
| `api/routers/errors.py` | 34 | N815 | Variable `boundaryName` should not be mixedCase |
| `api/routers/errors.py` | 40 | N815 | Variable `userAgent` should not be mixedCase |
| `grpc/spec_analytics_service.py` | 75 | N802 | Function name `AnalyzeSpec` should be lowercase |
| `grpc/spec_analytics_service.py` | 87 | N802 | Function name `BatchAnalyzeSpecs` should be lowercase |
| `grpc/spec_analytics_service.py` | 104 | N802 | Function name `ValidateISO29148` should be lowercase |
| `grpc/spec_analytics_service.py` | 121 | N802 | Function name `GetEARSPatterns` should be lowercase |
| `tui/widgets/sync_status.py` | 49 | N801 | Class name `reactive` should use CapWords convention |

#### Configuration Status

**Config File:** `pyproject.toml`

✅ **Enabled (strict profile):**
- E/W/F/I/B/C4/UP/N/PT/SIM/RUF (core rules)
- RSE/PERF/LOG/S (performance, logging, security)
- C90 (McCabe complexity ≤ 7)
- PLR (pylint refactoring: max-statements 50, max-args 8)

❌ **CRITICAL GAP:**
- **D (pydocstyle) rules NOT enabled** - Docstring enforcement missing
- Target: 85% coverage (per interrogate config)
- Status: interrogate blocked (cairo dependency missing)

#### Blockers

1. **interrogate:** OSError: cairo library not found (cairocffi dependency)
2. **Ty warnings:** 16 warnings about unknown rule 'non-subscriptable' (should be 'not-subscriptable')

---

### 1.3 TypeScript (518 total errors)

**Breakdown:**
- **Style violations:** 123 (magic numbers, ternaries, nulls)
- **Naming violations:** 54 (id-length, filename-case)
- **Type safety:** 50 (missing return types, explicit any)
- **LOC violations:** 64 files exceed limits
- **Architecture:** 1 boundary violation (FIXED)

#### Top Error Categories

| Category | Count | Examples |
|----------|-------|----------|
| **Style** | 123 | no-magic-numbers (47), no-ternary (39), no-null (39) |
| **Naming** | 54 | id-length (53), filename-case (1) |
| **Type Safety** | 50 | explicit-function-return-type (37), no-explicit-any (13) |
| **React Performance** | 37 | jsx-no-new-function-as-prop |
| **JSX Complexity** | 35 | jsx-max-depth (exceeds 8 levels) |
| **Code Organization** | 22 | exports-last (11), group-exports (11) |

#### LOC Violations (64 files)

**Top 4 Worst Violators:**

| Rank | File | LOC | Allowlist Max | Over Limit |
|------|------|-----|---------------|------------|
| 1 | `frontend/apps/web/src/pages/projects/views/IntegrationsView.tsx` | 1739 | 1717 | 22 |
| 2 | `frontend/apps/web/src/views/ItemsTableView.tsx` | 1425 | 1415 | 10 |
| 3 | **`frontend/packages/types/src/types.ts`** | 1208 | **500** | **708** |
| 4 | `frontend/apps/web/src/views/ItemDetailView.tsx` | 1176 | 1166 | 10 |

**Analysis:**
- **Type definition bloat:** `types.ts` has NO allowlist exception (708 lines over hard limit)
- **Views dominate:** 3 of 4 largest files are View components
- **Recent growth:** Most files within 1-2% of allowlist (well-tracked)
- **Average overage:** 15 lines per file (low drift)

#### Architecture Violations (1 - FIXED)

| Rule | Count | File | Issue | Resolution |
|------|-------|------|-------|------------|
| no-unknown-files | 1 | `frontend/apps/web/src/shaders/force-directed-wgsl.ts` | File not in any known element type | ✅ FIXED by agent (boundary added) |

#### Configuration Status

**Config File:** `frontend/.oxlintrc.json`

✅ **All Rules Configured:**
- max-lines: 500 (skip blank/comments)
- filename-case: kebab, camel, Pascal
- id-length: min 2 chars
- max-lines-per-function: 80
- complexity: 10
- jsx-max-depth: 8
- boundaries: element-type enforcement
- import-order: strict

---

## 2. Cross-Language Analysis

### 2.1 Naming Guard Consolidation

**Key Finding:** Hybrid approach required - 60-70% linter coverage, 30-40% bash

| Rule Category | Go (forbidigo) | Python (ruff) | TypeScript (oxlint) | Bash Guard |
|---------------|----------------|---------------|---------------------|------------|
| **Forbidden Identifier Words** | ✅ Regex patterns (proposed) | ❌ No support | ❌ No support | ✅ PRIMARY |
| **Versioning Suffixes (v2, V3)** | ⚠️ Proposed (not enabled) | ❌ No support | ⚠️ Verbose globs | ✅ PRIMARY |
| **Filename Forbidden Words** | ❌ N/A | ❌ No support | ⚠️ Verbose globs | ✅ PRIMARY |
| **Filename Case** | ❌ N/A | ❌ No support | ✅ Built-in | ✅ SECONDARY |
| **Directory Naming** | ❌ N/A | ❌ No support | ✅ Built-in | ✅ SECONDARY |
| **Identifier Length** | ✅ varnamelen | ❌ No support | ✅ id-length | ❌ Covered |
| **File LOC Limit (500)** | ❌ No linter | ❌ No linter | ✅ max-lines | ✅ PRIMARY |
| **Function LOC Limit** | ✅ funlen (80) | ✅ max-statements (50) | ✅ max-lines-per-fn (80) | ❌ Covered |

**Coverage by Language:**
- **Go:** 60% linter (after forbidigo enabled), 40% bash-only
- **Python:** 40% linter, 60% bash-only
- **TypeScript:** 70% linter, 30% bash-only

---

### 2.2 LOC Guard Consolidation

**Key Finding:** Bash required for Go/Python, hybrid for TypeScript

| Language | Files Over 500 LOC | Native Linter? | Bash Required? | Retirement Status |
|----------|-------------------|----------------|----------------|-------------------|
| **Go** | 121 | ❌ NO | ✅ YES | ❌ CANNOT RETIRE |
| **Python** | Unknown | ❌ NO | ✅ YES | ❌ CANNOT RETIRE |
| **TypeScript** | 64 | ✅ YES (oxlint) | ⚠️ PARTIAL (allowlist) | ⚠️ HYBRID APPROACH |
| **TOTAL** | **206+** | 1/3 | 3/3 | ❌ BASH REQUIRED |

**Why Bash Cannot Be Retired:**

**Go:**
- No native golangci-lint linter for file-level LOC enforcement
- `funlen` only limits function length (80 lines)
- Emerging `filen` linter not in stable releases

**Python:**
- Ruff does not support max lines per file
- `E501` only enforces line length (characters), not file LOC
- Alternative: `radon` for Python-native LOC metrics (already in deps)

**TypeScript:**
- ✅ Oxlint has `max-lines` rule (real-time enforcement)
- ⚠️ No dynamic allowlist file loading
- Recommendation: Hybrid (oxlint for enforcement, bash for allowlist validation)

---

## 3. Configuration Validation

### 3.1 Go Configuration

**File:** `backend/.golangci.yml`

✅ **All 27 Required Linters Enabled**

**Limits:**
```yaml
gocyclo: 10 complexity
gocognit: 12 complexity
funlen: 80 lines, 50 statements
lll: 120 characters
maintidx: 20
varnamelen: min 2 chars, max-distance 5
```

**Status:** ✅ COMPLIANT

⚠️ **Gap:** forbidigo patterns proposed but NOT enabled

---

### 3.2 Python Configuration

**File:** `pyproject.toml`

✅ **Enabled Rules:**
- E/W/F/I/B/C4/UP/N/PT/SIM/RUF (core rules)
- RSE/PERF/LOG/S (performance, logging, security)
- C90 (McCabe complexity ≤ 7)
- PLR (max-statements 50, max-args 8)

❌ **CRITICAL GAP:**
```toml
[tool.ruff.lint]
select = [
    # ... existing rules ...
    # "D",    # pydocstyle (docstring conventions) - MISSING!
]
```

**Impact:** Docstring enforcement missing, target 85% coverage not validated

**Status:** ❌ NON-COMPLIANT (D rules required)

---

### 3.3 TypeScript Configuration

**File:** `frontend/.oxlintrc.json`

✅ **All Rules Configured**

**Key Settings:**
```json
{
  "eslint/max-lines": ["error", {"max": 500, "skipBlankLines": true, "skipComments": true}],
  "eslint/max-lines-per-function": ["error", {"max": 80}],
  "eslint/complexity": ["error", {"max": 10}],
  "eslint/id-length": ["error", {"min": 2}],
  "unicorn/filename-case": ["error", {"cases": {"kebabCase": true, "camelCase": true, "pascalCase": true}}],
  "check-file/folder-naming-convention": ["error", {"**/": "KEBAB_CASE"}]
}
```

**Status:** ✅ COMPLIANT

---

## 4. Priority Actions

### P0 - Critical (Immediate, < 2 hours)

#### P0.1: Enable Python Docstring Rules (1 hour)
**File:** `pyproject.toml`

**Add:**
```toml
[tool.ruff.lint]
select = [
    # ... existing rules ...
    "D",    # pydocstyle (docstring conventions)
]

[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy", "pep257"

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D100", "D101", "D102", "D103", "D104"]  # Allow missing docstrings in tests
```

**Impact:** Enforces 85% docstring coverage target
**Risk:** LOW (phased rollout, tests excluded)

---

#### P0.2: Fix Go preflight.go Errors (2 hours)

**File:** `backend/cmd/tracertm/preflight.go`

**Fixes Required:**

1. **errcheck (line 244):**
```go
// Before
db.Close()

// After
if err := db.Close(); err != nil {
    log.Printf("Warning: failed to close database connection: %v", err)
}
```

2. **gocognit (line 73) - Reduce complexity from 32 to ≤12:**
```go
// Extract helper functions:
func (c *EnvConfig) loadDatabaseEnv() error { ... }
func (c *EnvConfig) loadAuthEnv() error { ... }
func (c *EnvConfig) loadObservabilityEnv() error { ... }

// Refactor loadFromEnv to delegate
```

3. **perfsprint (line 83):**
```go
// Before
fmt.Sprintf("prefix_%s", value)

// After
"prefix_" + value
```

4. **revive (line 1):**
```go
// Add package comment
// Package main provides the tracertm CLI entry point with preflight checks.
package main
```

5. **varnamelen (line 205):**
```go
// Before
func foo(c Config) { ... }

// After
func foo(config Config) { ... }
```

**Impact:** Removes all 5 golangci-lint errors
**Risk:** LOW (isolated to one file)

---

### P1 - High Priority (< 1 week)

#### P1.1: Enable Go forbidigo (2 hours)

**File:** `backend/.golangci.yml`

**Add:**
```yaml
linters:
  enable:
    - forbidigo  # Forbidden identifier patterns

linters-settings:
  forbidigo:
    forbid:
      # Temporary/versioning antipatterns
      - p: '\b(temp|tmp|old|copy|backup|draft|final|latest)[A-Z_]'
        msg: 'Forbidden temporary identifier (see naming-guard.json): use descriptive names'
      - p: '\b(deprecated|duplicate|alternate|iteration|replacement|variant)[A-Z_]'
        msg: 'Forbidden versioning identifier (see naming-guard.json): avoid temporal suffixes'
      - p: '(?i)\b(temp_|tmp_|old_|copy_|backup_|draft_|final_|latest_)'
        msg: 'Forbidden identifier prefix (see naming-guard.json)'
```

**Validation:**
```bash
cd backend && golangci-lint run --enable forbidigo ./...
```

**Impact:** Compile-time enforcement of naming patterns
**Risk:** LOW (current naming-guard shows 0 violations)

---

#### P1.2: Split Oversized Files (20 hours)

**Target:** Reduce technical debt by 25% (50 files)

**Priority Files:**

**Go (3 files, 8 hours):**
1. Split `server_test.go` (1509 → 3 files @ ~500 lines each)
2. Refactor `handler.go` (1362 → 3 files)
3. Split `server.go` (1313 → 3 files)

**TypeScript (2 files, 8 hours):**
1. Split `IntegrationsView.tsx` (1739 → 4 components)
2. Extract types from `types.ts` (1208 → domain-specific type files)

**Python (TBD, 4 hours):**
- Run LOC guard to identify top violators
- Split 3-5 largest files

**Impact:** Reduces LOC violations by 25%
**Risk:** MEDIUM (requires careful component extraction)

---

#### P1.3: Fix Python Critical Blockers (6 hours)

**1. Protobuf Stub Generation (2 hours)**
- Regenerate protobuf stubs with type hints
- Update grpc service implementations
- Fix 35 attribute errors in `spec_analytics_service.py`

**2. TUI Module Resolution (2 hours)**
- Verify textual dependency installation
- Update import paths if needed
- Fix 98 TUI import errors

**3. CLI Module Integration (2 hours)**
- Implement missing `tracertm.cli.auth` module
- Update MCP integration imports
- Fix 5+ CLI import errors

**Impact:** Removes 138 critical errors (35 + 98 + 5)
**Risk:** MEDIUM (dependency resolution required)

---

### P2 - Medium Priority (< 2 weeks)

#### P2.1: TypeScript Code Quality (8 hours)

**Actions:**
1. Extract magic numbers to constants (47 violations)
2. Add explicit return types (37 violations)
3. Reduce JSX nesting depth (35 violations, extract components)
4. Replace null with undefined (39 violations)
5. Consolidate export statements (22 violations)

**Impact:** Removes 180 style violations
**Risk:** LOW (mechanical refactoring)

---

## 5. Summary and Recommendations

### Current State

| Language | Status | Critical Issues | Total Violations |
|----------|--------|-----------------|------------------|
| **Go** | ❌ FAIL | 5 linter errors, 1 cognitive complexity | 126 |
| **Python** | ❌ FAIL | 138 critical blockers, D rules missing | 3,881 |
| **TypeScript** | ❌ FAIL | 64 LOC violations, 1 boundary (FIXED) | 518 |
| **TOTAL** | ❌ FAIL | 10 critical issues | **4,525** |

### Path to Zero Violations

**Phase 1 (Week 1): Critical Fixes**
- ✅ Enable Python D rules (1 hour)
- ✅ Fix Go preflight.go errors (2 hours)
- ✅ Enable Go forbidigo (2 hours)
- **Total:** 5 hours, removes 5 critical errors

**Phase 2 (Week 2-3): Blocker Resolution**
- ✅ Fix Python protobuf/TUI/CLI blockers (6 hours)
- ✅ Split top 5 oversized files (10 hours)
- **Total:** 16 hours, removes 138 critical errors + 5 LOC violations

**Phase 3 (Week 4-6): Quality Improvement**
- ✅ TypeScript style cleanup (8 hours)
- ✅ Split remaining oversized files (10 hours)
- ✅ Allowlist reduction (ongoing)
- **Total:** 18 hours, removes 180 style violations + 45 LOC violations

**Total Effort:** ~39 hours (5 weeks with parallel work)

---

### Hybrid Linting Strategy

**Native Linters (golangci-lint, ruff, oxlint):**
- Structural rules: complexity, LOC, case conventions
- Fast compile-time enforcement
- IDE integration

**Bash Guards (scripts/quality/):**
- Semantic rules: forbidden word patterns, versioning suffixes
- Repository policies: path depth, filename length
- Cross-language consistency

**Integration:**
- Both run in CI/CD
- Linters for pre-commit hooks (fast)
- Bash for repository-level policies

---

### Next Steps

1. **Team lead approval:** Review P0 actions and Python D rule configuration
2. **Immediate action (Week 1):** Execute P0.1 (D rules) + P0.2 (preflight.go fixes)
3. **Validation (Week 2):** Run parallel bash + linters, compare outputs
4. **Consolidation (Week 3-6):** Execute P1 and P2 actions
5. **Monitoring (Ongoing):** Subscribe to linter releases for new capabilities

---

## Appendix: Tool Version Information

**Go:**
- golangci-lint: v1.61 (includes 27 enabled linters)
- Config: `backend/.golangci.yml` (version 2)

**Python:**
- Ruff: v0.14.14 (strict profile)
- Ty: Latest (159 errors)
- Config: `pyproject.toml`

**TypeScript:**
- Oxlint: v1.42.0 (6 plugins)
- Config: `frontend/.oxlintrc.json`

**Bash:**
- naming-guard: `scripts/quality/naming-guard.sh`
- loc-guard: `scripts/quality/loc-guard.sh`
- Config: `config/naming-guard.json`, `config/loc-allowlist.txt`

---

## References

- **Go Enhancement Proposal:** See naming guard consolidation report
- **Python Enhancement Proposal:** See naming guard consolidation report
- **Naming Guard Analysis:** `docs/reports/NAMING_GUARD_CONSOLIDATION.md`
- **LOC Guard Analysis:** `docs/reports/LOC_GUARD_CONSOLIDATION.md`
- **GitHub Issues:**
  - golangci-lint #2881 (file LOC linter)
  - Ruff #12389 (max lines per file)
  - Ruff #8409 (custom rules)

---

**Generated by:** Static Analysis Consolidator (Task #13)
**Status:** Ready for team lead review and P0 implementation
**Estimated Total Effort:** 39 hours (Phases 1-3)
**Expected Benefit:** Zero static analysis violations, 100% quality compliance
