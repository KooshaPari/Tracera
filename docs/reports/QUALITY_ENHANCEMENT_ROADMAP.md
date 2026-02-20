# Quality Enhancement Roadmap: Cross-Language Consolidation

**Generated:** 2026-02-07
**Task:** Enhancement Roadmap Consolidation (Task #15)
**Status:** COMPLETE

---

## Executive Summary

**Total Enhancements:** 15+ proposed across 3 languages
**Quick Wins:** 2 critical actions (2-3 hours total implementation)
**Migration Potential:** 40-70% to native linters (language-dependent)
**Bash Retirement:** ❌ **NOT FEASIBLE** - Hybrid approach required

### Critical Findings

- **Go:** 60% migratable (forbidigo for naming patterns)
- **Python:** 40% migratable (D rules for docstrings - CRITICAL blocker)
- **TypeScript:** 70% migratable (already at max linter capacity)
- **Cross-language:** File LOC and forbidden word patterns MUST stay in bash
- **Technical Debt:** 206+ files exceed LOC limits, 4,525+ linter violations

---

## 1. Phase 1: Immediate Wins (Week 1 - 2-3 Hours)

### 🔴 CRITICAL: Python Docstring Rules (1 Hour)

**Priority:** HIGHEST - Unblocks 85% coverage target

**Problem:** Ruff D (pydocstyle) rules NOT enabled despite 85% target in `[tool.interrogate]`

**Current State:**
```toml
[tool.interrogate]
fail-under = 85  # Target exists but not enforced

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", ..., "Q"]  # NO D rules!
```

**Solution:** Add D rules with phased rollout

**Implementation:**
```toml
# pyproject.toml
[tool.ruff.lint]
select = [
    # ... existing rules ...
    "D",    # pydocstyle (docstring conventions) - NEW
]

[tool.ruff.lint.pydocstyle]
convention = "google"  # Google-style docstrings

[tool.ruff.lint.per-file-ignores]
"tests/**" = [
    # ... existing ignores ...
    "D100", "D101", "D102", "D103", "D104",  # Missing docstrings in tests
]
"**/__init__.py" = ["F401", "F403", "D104"]  # Allow missing package docstrings
"**/conftest.py" = ["F401", "S101", "PT018", "D100", "D103"]  # Fixtures
"scripts/**" = ["D100", "D103"]  # Utility code
```

**Phased Rollout:**
1. Phase 1a: Enable D for `src/tracertm/api/` (public API)
2. Phase 1b: Enable D for `src/tracertm/services/` (business logic)
3. Phase 1c: Enable D for remaining `src/` modules

**Impact:**
- Unblocks docstring enforcement (interrogate blocked by cairocffi)
- Fast pre-commit checking (ruff is Rust-based)
- Programmatic enforcement via `ruff check`
- Replaces need for external `interrogate` tool

**Validation:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
# Baseline
ruff check --select D --statistics

# Phased test
ruff check src/tracertm/api/ --select D
```

**Effort:** 1 hour (config + validation)

---

### 🟡 HIGH: Go Forbidigo Rules (1-2 Hours)

**Priority:** HIGH - Migrate naming enforcement to linter

**Problem:** Forbidden identifier patterns in bash, not in golangci-lint

**Current State:**
- 31 enabled linters in `.golangci.yml`
- Bash `naming-guard.json` enforces forbidden words
- 0 current naming violations (clean baseline)

**Solution:** Add `forbidigo` linter with regex patterns

**Implementation:**
```yaml
# backend/.golangci.yml
linters:
  enable:
    # ... existing 31 linters ...
    - forbidigo  # NEW: Forbidden identifier patterns

linters-settings:
  forbidigo:
    forbid:
      # Temporary/versioning antipatterns
      - p: '\b(temp|tmp|old|copy|backup|draft|final|latest)[A-Z_]'
        msg: 'Forbidden temporary identifier (see naming-guard.json): use descriptive names'

      - p: '\b(deprecated|duplicate|alternate|iteration|replacement|variant)[A-Z_]'
        msg: 'Forbidden versioning identifier (see naming-guard.json): avoid temporal suffixes'

      # Snake_case prefixes
      - p: '(?i)\b(temp_|tmp_|old_|copy_|backup_|draft_|final_|latest_|deprecated_)'
        msg: 'Forbidden identifier prefix (see naming-guard.json)'

    analyze_types: true
    exclude_godoc_examples: true

issues:
  exclude-rules:
    # ... existing exclusions ...

    # NEW: Allow test file exceptions
    - path: _test\.go
      linters:
        - forbidigo

    # NEW: Allow domain-specific "backup" usage with justification
    - text: "backup.*benchmark"
      linters:
        - forbidigo
```

**Impact:**
- Compile-time enforcement (vs post-commit bash)
- IDE integration via golangci-lint LSP
- Per-line suppression via `//nolint:forbidigo` with justification
- All rules in `.golangci.yml` (no external JSON config)

**Validation:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend
# Test forbidigo only
golangci-lint run --enable forbidigo --disable-all ./...

# Test all rules (including forbidigo)
golangci-lint run
```

**Effort:** 1-2 hours (implementation + testing)

---

### ✅ COMPLETE: TypeScript Already at Max

**Status:** No additional linter changes needed

**Fixes Applied:**
1. ✅ Shaders boundary: FIXED (added `shaders` element to `.oxlintrc.json`)
2. ✅ Filename case: FIXED (`useGPUCompute.ts` → `use-gpu-compute.ts`)
3. ✅ Oxlint configuration: Already comprehensive (6 plugins, max-lines enforcement)

**Remaining Violations:** 54 naming (53 id-length, 1 filename-case resolved)

**Action:** Keep bash for forbidden pattern enforcement (v2, V3, new_, old_)

**Reason:** Oxlint requires 50+ glob patterns for what bash does in 1 regex line

**Effort:** 0 hours (no changes needed)

---

## 2. Hybrid Approach Strategy

### Enforcement Matrix

| Rule Category | Go | Python | TypeScript | Winner |
|---------------|----|---------|-----------|----|
| **Forbidden Identifier Words** | forbidigo (regex) | ❌ No support | ❌ No support | Linter (Go only) |
| **Versioning Suffixes (v2, V3)** | forbidigo | ❌ No support | ⚠️ Verbose globs | Bash |
| **Docstring Coverage** | N/A | D rules | N/A | Linter (Python) |
| **File LOC Limit (500)** | ❌ No linter | ❌ No linter | max-lines | Bash (Go/Python) |
| **Function LOC** | funlen (80) | PLR0915 (50) | max-lines-per-fn (80) | Linter (all) |
| **Path Depth (10 levels)** | ❌ No linter | ❌ No linter | ❌ No linter | Bash (only) |

### What CAN Migrate to Linters

**Go (60% coverage):**
- ✅ Forbidden identifiers (forbidigo)
- ✅ Identifier length (varnamelen - already enabled)
- ✅ Function LOC (funlen - already enabled)
- ✅ Complexity (gocyclo, gocognit - already enabled)

**Python (40% coverage):**
- ✅ Docstring coverage (D rules - NEEDS ENABLING)
- ✅ Function complexity (C90, PLR - already enabled)
- ❌ Forbidden identifiers (no ruff support)
- ❌ File LOC (no ruff support)

**TypeScript (70% coverage):**
- ✅ File LOC (max-lines - already enabled)
- ✅ Filename case (unicorn/filename-case - already enabled)
- ✅ Directory naming (check-file/folder-naming-convention - already enabled)
- ✅ Identifier length (eslint/id-length - already enabled)
- ❌ Forbidden patterns (no regex support, requires 50+ globs)

### What MUST Stay in Bash

| Bash Rule | Reason | Migratable? |
|-----------|--------|-------------|
| **File LOC (Go/Python)** | No linter available | ⏰ Monitor `filen` (Go), radon (Python) |
| **Forbidden Word Patterns** | Regex flexibility vs verbose globs | ❌ NO - 1 regex > 50 globs |
| **Path Depth** | File system policy, outside linter scope | ❌ NO - Not a code quality metric |
| **Filename/Directory Length** | Repository organization policy | ❌ NO - Not a code quality metric |
| **Allowlist Management** | Requires stateful tracking and exceptions | ❌ NO - Cross-file analysis |

---

## 3. Phase 2: Quality Debt (Weeks 2-4 - 40-60 Hours)

### Technical Debt Summary

**Total Violations:** 4,731 across 3 languages

| Language | LOC Violations | Linter Violations | Type Errors | Total |
|----------|----------------|-------------------|-------------|-------|
| **Go** | 121 files (over 500 LOC) | 5 (golangci-lint) | 0 | 126 |
| **Python** | Unknown | 3,722 (ruff) | 159 (ty) | 3,881+ |
| **TypeScript** | 64 files (over 500 LOC) | 54 (oxlint) | 0 | 118 |
| **TOTAL** | 185+ files | 3,781 | 159 | 4,125+ |

---

### 2.1: Split Oversized Files (206+ Files)

**Priority:** MEDIUM (Technical debt reduction)

**Critical Files by Language:**

**Go (121 files):**
1. `server_test.go`: 1509 lines (allowlist 655) → **854 lines over**
2. `service_integration_test.go`: 1492 lines (allowlist 1490) → 2 over
3. `handler.go`: 1362 lines (allowlist 1310) → 52 over
4. `item_handler_test.go`: 1316 lines (allowlist 1238) → 78 over
5. `server.go`: 1313 lines (allowlist 1113) → 200 over

**Action:** Split test files first (80% are test files)
- Extract table-driven tests into separate files
- Extract helper functions into `testutil/` package
- Target: 3 files @ ~500 lines each per large test

**Python (Unknown):**
- No LOC data in static analysis (requires bash scan)
- Estimate 20-40 files exceed 500 LOC
- Action: Run `scripts/quality/loc-guard.sh src/` to generate report

**TypeScript (64 files):**
1. `IntegrationsView.tsx`: 1739 lines (allowlist 1717) → 22 over
2. `ItemsTableView.tsx`: 1425 lines (allowlist 1415) → 10 over
3. `types.ts`: 1208 lines (NO allowlist) → **708 lines over hard limit**
4. `ItemDetailView.tsx`: 1176 lines (allowlist 1166) → 10 over

**Action:** Extract components and types
- Split `types.ts` into domain-specific type files
- Extract view components into smaller files
- Target: All files < 500 LOC (remove from allowlist)

**Estimated Effort:** 10-15 tool calls per large file × 206 files = **40-60 hours**

---

### 2.2: Fix Linter Violations (3,781 Issues)

**Go (5 issues):**
- Already at 99.9% compliance
- Quick fixes (1-2 hours)

**Python (3,722 issues):**
- Ruff violations (medium priority)
- Focus on high-severity first (S, E, F)
- Estimated: 20-30 hours (bulk fixes with ruff --fix)

**TypeScript (54 issues):**
- 53 id-length violations (single-letter vars)
- 1 filename-case (RESOLVED)
- Estimated: 2-4 hours (rename variables)

**Total Estimated Effort:** 23-36 hours

---

### 2.3: Address Test Infrastructure Blockers

**MSW GraphQL (Frontend):**
- 29 tests blocked by ESM/CommonJS compatibility
- Graceful fallback in `setup.ts` (tests run without MSW)
- Action: Monitor MSW releases for vitest jsdom fix

**Go E2E Tests:**
- 0% e2e coverage (integration tests exist, but no true e2e)
- Action: Add Playwright or Testcontainers-based e2e tests
- Estimated: 8-12 hours

**Python Test Coverage:**
- pytest-cov blocked by cairocffi dependency
- Action: Enable ruff D rules (replaces interrogate)
- Estimated: 1 hour (Phase 1)

**Total Estimated Effort:** 9-13 hours

---

## 4. Phase 3: Coverage Improvement (Ongoing)

### Coverage Targets by Language

| Language | Current Coverage | Target | Gap | Priority |
|----------|------------------|--------|-----|----------|
| **Go** | 33% | 85% | **+52 points** | HIGH |
| **Python** | N/A (blocked) | 85% | Unblock first | CRITICAL |
| **TypeScript** | Unknown | 85% | Measure first | MEDIUM |

---

### Go Coverage (33% → 85%)

**Current State:**
- Unit tests: Good coverage for handlers, services
- Integration tests: 1492 lines in single file
- E2E tests: 0% coverage

**Actions:**
1. Add table-driven tests for uncovered paths
2. Mock external dependencies (NATS, Temporal)
3. Add e2e tests with Testcontainers
4. Use `go test -cover -coverprofile=coverage.out` for baselines

**Estimated Effort:** 30-40 hours (test development)

---

### Python Coverage (Unblock → 85%)

**Current State:**
- Coverage tool blocked by cairocffi dependency
- interrogate configured (85% target) but not running
- Ruff D rules NOT enabled

**Actions:**
1. ✅ Enable ruff D rules (Phase 1 - 1 hour)
2. Fix cairocffi dependency (or replace interrogate)
3. Run pytest-cov: `pytest --cov=src/tracertm --cov-report=html`
4. Add missing docstrings and tests

**Estimated Effort:** 20-30 hours (after D rules enabled)

---

### TypeScript Coverage (Measure → 85%)

**Current State:**
- Desktop tests: 4 tests (main.test.ts, preload.test.ts)
- No coverage measurement in CI/CD
- MSW blocks 29 tests (HTTP mocking)

**Actions:**
1. Fix desktop tests (vitest config)
2. Add vitest coverage plugin
3. Measure baseline: `bun run vitest --coverage`
4. Add missing component tests

**Estimated Effort:** 15-25 hours

---

## 5. Bash Script Evolution

### Keep: File Metrics and Repository Policies

**Bash-Only Responsibilities (Permanent):**
- File-level LOC limits (Go, Python - no linter support)
- Path depth enforcement (all languages)
- Forbidden word patterns (Python, TypeScript - verbose in linters)
- Filename/directory length limits (repository policy)
- Allowlist management (cross-file analysis)

**Why Bash is Required:**
1. **File system concerns:** Path depth, filename length are repo policies, not code quality
2. **Stateful tracking:** Allowlists require historical data and exceptions
3. **Cross-file analysis:** LOC guard compares files against allowlist database
4. **Reporting:** Bash generates sorted violation reports for triage

---

### Enhance: Parallel Execution and Better Error Messages

**Current Limitations:**
- Sequential execution (slow on large codebases)
- Generic error messages (not actionable)
- No linter integration (bash runs after linters)

**Proposed Enhancements:**
```bash
# scripts/quality/loc-guard.sh
# Add parallel processing with GNU parallel
find backend -name "*.go" | parallel --jobs 8 check_loc_limit {}

# Better error messages
echo "ERROR: server_test.go (1509 lines) exceeds limit (500) by 854 lines"
echo "  Allowlist max: 655 (also exceeded by 854 lines)"
echo "  Action: Split into separate test files OR update allowlist with justification"
echo "  Reference: docs/guides/quality.md#splitting-test-files"
```

**Estimated Effort:** 4-6 hours

---

### Integrate: Linter-First, Bash-Fallback Strategy

**Proposed CI/CD Flow:**
```bash
# Makefile quality target (optimized)
quality-go:
	@echo "Go: Linter checks..."
	cd backend && golangci-lint run  # includes forbidigo (Phase 1)
	@echo "Go: File-level LOC checks..."
	scripts/quality/loc-guard.sh backend/

quality-python:
	@echo "Python: Linter checks..."
	ruff check src/  # includes D rules (Phase 1)
	ty check
	@echo "Python: File-level LOC checks..."
	scripts/quality/loc-guard.sh src/

quality-typescript:
	@echo "TypeScript: Linter checks..."
	cd frontend && bun run oxlint  # includes max-lines
	@echo "TypeScript: Allowlist validation..."
	scripts/quality/loc-guard.sh frontend/ --allowlist-only
```

**Key Changes:**
1. Linters run first (fast, compile-time)
2. Bash runs for non-linter checks only
3. TypeScript bash is allowlist-only (oxlint handles LOC)

**Estimated Effort:** 2-3 hours (Makefile updates)

---

### Document: Why Bash is Required

**Update Documentation:**
- `CLAUDE.md` - Add hybrid linting strategy section
- `docs/guides/quality.md` - Explain linter limitations
- `config/naming-guard.json` - Add header comment with scope
- `config/loc-guard.json` - Document allowlist management

**Content:**
```markdown
## Hybrid Linting Strategy

### Why Both Linters and Bash?

**Native Linters (golangci-lint, ruff, oxlint):**
- ✅ Structural rules: complexity, LOC, case conventions
- ✅ Fast compile-time enforcement
- ✅ IDE integration (LSP)
- ✅ Per-line suppression with justification

**Bash Guards (scripts/quality/):**
- ✅ Semantic rules: forbidden word patterns, versioning suffixes
- ✅ Repository policies: path depth, filename length
- ✅ Cross-language consistency
- ✅ Allowlist management (stateful tracking)

### No Alternative to Bash For:
1. File-level LOC limits (Go, Python - no linter available)
2. Path depth enforcement (outside linter scope)
3. Forbidden word patterns (regex flexibility vs verbose globs)
4. Allowlist management (requires cross-file analysis)
```

**Estimated Effort:** 1-2 hours

---

## 6. Implementation Estimates

### Phase 1: Immediate Wins (Week 1)
- **Python D rules:** 1 hour (config + phased rollout)
- **Go forbidigo:** 1-2 hours (implementation + testing)
- **TypeScript:** 0 hours (already at max)
- **Total:** **2-3 hours**

### Phase 2: Quality Debt (Weeks 2-4)
- **Split 206+ files:** 40-60 hours (10-15 calls/file)
- **Fix 3,781 linter violations:** 23-36 hours
- **Test infrastructure:** 9-13 hours
- **Total:** **72-109 hours**

### Phase 3: Coverage Improvement (Ongoing)
- **Go (33% → 85%):** 30-40 hours
- **Python (unblock → 85%):** 20-30 hours (after D rules)
- **TypeScript (measure → 85%):** 15-25 hours
- **Total:** **65-95 hours**

### Phase 4: Bash Evolution (Weeks 5-6)
- **Parallel execution:** 4-6 hours
- **Linter integration:** 2-3 hours
- **Documentation:** 1-2 hours
- **Total:** **7-11 hours**

---

## 7. Total Roadmap Summary

### By Phase

| Phase | Timeline | Effort | Priority | Impact |
|-------|----------|--------|----------|--------|
| **Phase 1: Quick Wins** | Week 1 | 2-3 hours | 🔴 CRITICAL | Unblock 85% targets |
| **Phase 2: Quality Debt** | Weeks 2-4 | 72-109 hours | 🟡 HIGH | Reduce violations |
| **Phase 3: Coverage** | Ongoing | 65-95 hours | 🟡 HIGH | Meet 85% targets |
| **Phase 4: Bash Evolution** | Weeks 5-6 | 7-11 hours | 🟢 MEDIUM | Optimize enforcement |
| **TOTAL** | 6 weeks | **146-218 hours** | - | Full quality compliance |

### By Language

| Language | Linter Enhancements | Bash Required? | Coverage Gap | Estimated Effort |
|----------|---------------------|----------------|--------------|------------------|
| **Go** | Enable forbidigo (1-2h) | ✅ YES (LOC, path depth) | +52 points | 31-42 hours |
| **Python** | Enable D rules (1h) | ✅ YES (LOC, naming, path depth) | Unblock first | 21-31 hours |
| **TypeScript** | None (0h) | ⚠️ PARTIAL (allowlist) | Unknown | 15-25 hours |

---

## 8. Risk Assessment

### Low Risk
- **Phase 1 Quick Wins:** Production-ready linters, zero violations baseline, easy rollback
- **Bash retention:** Keeping bash guards eliminates migration risk

### Medium Risk
- **Bash deprecation timing:** Must ensure linters catch all patterns before removing bash
- **Mitigation:** Run in parallel for 2-4 weeks (Phase 2 validation)

### High Risk
- **Coverage improvement:** Requires significant test development (65-95 hours)
- **Mitigation:** Phased rollout, continuous monitoring

### No Risk
- **LOC/path depth migration:** Not attempting (bash designed for this)

---

## 9. Recommendations

### Immediate Actions (This Week)

1. **Enable Python D Rules (1 hour)** 🔴 CRITICAL
   - Unblocks 85% docstring coverage target
   - Replaces blocked interrogate tool
   - Phased rollout: api/ → services/ → all

2. **Enable Go Forbidigo (1-2 hours)** 🟡 HIGH
   - Migrate naming enforcement to linter
   - Compile-time enforcement + IDE integration
   - Zero violations baseline (safe)

3. **Document Hybrid Approach (1 hour)** 🟢 MEDIUM
   - Update `CLAUDE.md`, `docs/guides/quality.md`
   - Explain why bash is required
   - Clarify linter limitations

**Total Week 1 Effort:** 3-4 hours

---

### Short-Term (Weeks 2-4)

1. **Parallel Validation (Week 2):** Run bash + linters in parallel, compare outputs
2. **Begin File Splitting (Weeks 2-3):** Focus on test files first (80% of violations)
3. **Fix Bulk Linter Violations (Week 3-4):** Use `ruff --fix` for auto-fixable issues
4. **Simplify Bash Config (Week 4):** Remove redundant checks now covered by linters

**Total Weeks 2-4 Effort:** 72-109 hours

---

### Long-Term (Ongoing)

1. **Coverage Improvement:** Meet 85% targets for all languages
2. **Monitor Linter Releases:** Subscribe to golangci-lint, ruff, oxlint for new features
3. **Allowlist Reduction:** Quarterly refactoring sprints (reduce by 10% per quarter)
4. **Zero Allowlist Target:** All files < 500 LOC (no exceptions)

**Timeline:** 6+ months (continuous improvement)

---

## 10. Success Metrics

### Phase 1 Completion
- ✅ Python D rules enabled (85% docstring coverage target)
- ✅ Go forbidigo enabled (compile-time naming enforcement)
- ✅ Documentation updated (hybrid approach explained)
- ✅ CI/CD updated (linter-first, bash-fallback)

### Phase 2 Completion
- ✅ 206+ files split (all < 500 LOC)
- ✅ 3,781 linter violations fixed
- ✅ Test infrastructure unblocked
- ✅ Bash config simplified (redundant checks removed)

### Phase 3 Completion
- ✅ Go: 85% coverage (from 33%)
- ✅ Python: 85% coverage (from N/A)
- ✅ TypeScript: 85% coverage (from unknown)
- ✅ All tests passing in CI/CD

### Phase 4 Completion
- ✅ Bash scripts optimized (parallel execution)
- ✅ Linter integration complete (linter-first strategy)
- ✅ Documentation comprehensive (no ambiguity)
- ✅ Quality gates automated (no manual checks)

---

## 11. References

### Proposal Documents
- `.quality/logs/go-enhancement-proposal.md` - Forbidigo solution
- `.quality/logs/python-enhancement-proposal.md` - D rules critical
- `.quality/logs/typescript-enhancement-proposal.md` - Hybrid approach
- `docs/reports/NAMING_GUARD_CONSOLIDATION.md` - Cross-language naming
- `docs/reports/LOC_GUARD_CONSOLIDATION.md` - Cross-language LOC

### External Resources
- [forbidigo GitHub](https://github.com/ashanbrown/forbidigo)
- [golangci-lint discussion #2881](https://github.com/golangci/golangci-lint/discussions/2881)
- [Ruff Settings Documentation](https://docs.astral.sh/ruff/settings/)
- [Ruff Issue #12389](https://github.com/astral-sh/ruff/issues/12389)
- [Oxlint Rules Reference](https://oxc.rs/docs/guide/usage/linter.html)

---

## 12. Next Steps

1. **Team Lead Approval:** Review Phase 1 configurations (Python D rules, Go forbidigo)
2. **Week 1 Execution:** Implement Phase 1 quick wins (2-3 hours)
3. **Validation (Week 2):** Run bash + linters in parallel for parity check
4. **Phase 2 Planning:** Prioritize file splitting (focus on test files)
5. **Continuous Monitoring:** Subscribe to linter releases, track coverage progress

---

**Generated by:** Enhancement Roadmap Consolidator (Task #15)
**Status:** Ready for team lead approval and Phase 1 implementation
**Expected Benefit:** Compile-time enforcement, IDE integration, 85% coverage targets, reduced technical debt
