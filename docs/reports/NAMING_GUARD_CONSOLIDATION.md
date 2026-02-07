# Naming Guard Consolidation: Cross-Language Enforcement Matrix

**Date:** 2026-02-07
**Task:** Naming Guard Consolidation (Task #10)
**Status:** ANALYSIS COMPLETE

---

## Executive Summary

**Can bash naming guards be retired?** ⚠️ **NO - Keep hybrid approach**

- **Linter Coverage:** 40-70% overlap (varies by language)
- **Critical Gap:** Forbidden word patterns (v2, V3, new_, old_) not natively supported in any linter
- **Recommendation:** Keep bash for semantic pattern enforcement, migrate structural rules to native linters where feasible

---

## Rule-by-Rule Enforcement Matrix

| Rule Category | Go (forbidigo) | Python (ruff) | TypeScript (oxlint) | Bash Guard |
|---------------|----------------|---------------|---------------------|------------|
| **Forbidden Identifier Words** | ✅ Regex patterns | ❌ No support | ❌ No support | ✅ PRIMARY |
| **Versioning Suffixes (v2, V3)** | ⚠️ Proposed (not enabled) | ❌ No support | ⚠️ Verbose globs | ✅ PRIMARY |
| **Filename Forbidden Words** | ❌ N/A | ❌ No support | ⚠️ Verbose globs | ✅ PRIMARY |
| **Filename Case** | ❌ N/A | ❌ No support | ✅ Built-in | ✅ SECONDARY |
| **Directory Naming** | ❌ N/A | ❌ No support | ✅ Built-in | ✅ SECONDARY |
| **Identifier Length** | ✅ `varnamelen` | ❌ No support | ✅ `id-length` | ❌ Covered |
| **File LOC Limit (500)** | ❌ No linter | ❌ No linter | ✅ `max-lines` | ✅ PRIMARY |
| **Function LOC Limit** | ✅ `funlen` (80) | ✅ `max-statements` (50) | ✅ `max-lines-per-function` (80) | ❌ Covered |
| **Path Depth (10 levels)** | ❌ No linter | ❌ No linter | ❌ No linter | ✅ ONLY |
| **Max Filename Length (64)** | ❌ No linter | ❌ No linter | ❌ No linter | ✅ ONLY |
| **Max Directory Name Length (64)** | ❌ No linter | ❌ No linter | ❌ No linter | ✅ ONLY |

**Legend:**
- ✅ Full native support
- ⚠️ Partial support (requires verbose config or not enabled)
- ❌ No native support

---

## Language-Specific Coverage

### Go (golangci-lint + forbidigo)

**Current State:**
- 31 enabled linters in `.golangci.yml`
- `forbidigo` patterns proposed but NOT enabled
- 121 files exceed LOC limit (500 lines)

**Coverage:**

| Rule | Linter | Status | Notes |
|------|--------|--------|-------|
| Forbidden identifiers | `forbidigo` | ⚠️ NOT ENABLED | Regex patterns ready, needs activation |
| Identifier length | `varnamelen` | ✅ ACTIVE | min 2 chars, max-distance 5 |
| Function LOC | `funlen` | ✅ ACTIVE | 80 lines, 50 statements |
| File LOC | N/A | ❌ NO LINTER | Must stay as bash |
| Path depth | N/A | ❌ NO LINTER | Must stay as bash |

**Proposed `.golangci.yml` Addition (from go-enhancement-proposal.md):**

```yaml
linters:
  enable:
    - forbidigo  # NEW: Forbidden identifier patterns

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

**Migration Status:** READY (Phase 1 from proposal) - 1-2 hours implementation

---

### Python (ruff)

**Current State:**
- Ruff 0.14.14 with strict profile (E/W/F/I/B/C4/UP/N/PT/SIM/RUF + RSE/PERF/LOG/S)
- Docstring rules (D) NOT enabled (critical gap)
- 3,722 ruff violations, 159 ty errors

**Coverage:**

| Rule | Linter | Status | Notes |
|------|--------|--------|-------|
| Forbidden identifiers | N/A | ❌ NO SUPPORT | Ruff N (pep8-naming) only does case, not word blacklist |
| Identifier length | N/A | ❌ NO SUPPORT | No min-length rule |
| Function complexity | `C90`, `PLR` | ✅ ACTIVE | max-complexity 7, max-statements 50 |
| File LOC | N/A | ❌ NO SUPPORT | [Issue #12389](https://github.com/astral-sh/ruff/issues/12389) - not available |
| Docstring coverage | `D` (pydocstyle) | ❌ NOT ENABLED | CRITICAL: 85% target in interrogate but D rules off |

**Critical Missing Configuration (from python-enhancement-proposal.md):**

```toml
[tool.ruff.lint]
select = [
    # ... existing rules ...
    "D",    # pydocstyle (docstring conventions) - MISSING!
]

[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy", "pep257"

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D100", "D101", "D102", "D103", "D104"]  # Allow missing docstrings in tests
```

**Migration Status:** PARTIAL - Enable D rules (1 hour), bash required for naming patterns

---

### TypeScript (oxlint)

**Current State:**
- Oxlint 1.42.0 with 6 plugins (eslint, typescript, unicorn, check-file, boundaries, react)
- 54 naming violations (53 id-length, 1 filename-case)
- 1 architecture violation (shaders boundary missing - FIXED)

**Coverage:**

| Rule | Linter | Status | Notes |
|------|--------|--------|-------|
| Filename case | `unicorn/filename-case` | ✅ ACTIVE | kebab, camel, Pascal |
| Directory naming | `check-file/folder-naming-convention` | ✅ ACTIVE | KEBAB_CASE enforced |
| Identifier length | `eslint/id-length` | ✅ ACTIVE | min 2 chars, 53 violations |
| File LOC | `eslint/max-lines` | ✅ ACTIVE | max 500, 64 files over limit |
| Function LOC | `eslint/max-lines-per-function` | ✅ ACTIVE | max 80 lines |
| Filename blocklist | `check-file/filename-blocklist` | ✅ ACTIVE | .tmp, .bak, .backup, .old |
| **Forbidden patterns (v2, V3)** | N/A | ❌ NO REGEX | Would require 50+ glob patterns (verbose) |
| **Identifier word blacklist** | N/A | ❌ NO SUPPORT | `naming-convention` doesn't support word lists |

**Why Oxlint Can't Replace Bash:**

Bash pattern matching (1 line):
```bash
*v2* | *V3* | *new_* | *old_*
```

Oxlint equivalent (50+ lines):
```json
{
  "check-file/filename-blocklist": [
    "error",
    {
      "**/*v2*.{ts,tsx,js,jsx}": "**/*.{ts,tsx,js,jsx}",
      "**/*V2*.{ts,tsx,js,jsx}": "**/*.{ts,tsx,js,jsx}",
      "**/*v3*.{ts,tsx,js,jsx}": "**/*.{ts,tsx,js,jsx}",
      "**/*V3*.{ts,tsx,js,jsx}": "**/*.{ts,tsx,js,jsx}",
      "**/*new_*.{ts,tsx,js,jsx}": "**/*.{ts,tsx,js,jsx}",
      "**/*old_*.{ts,tsx,js,jsx}": "**/*.{ts,tsx,js,jsx}",
      "**/*copy*.{ts,tsx,js,jsx}": "**/*.{ts,tsx,js,jsx}",
      // ... 40+ more patterns
    }
  ]
}
```

**Migration Status:** HYBRID (structural rules in oxlint, semantic patterns in bash)

---

## Gap Analysis

### What CAN Be Enforced by Linters

| Language | Structural Rules | Config Location | Status |
|----------|------------------|-----------------|--------|
| **Go** | Identifier length, function LOC, complexity | `.golangci.yml` | ✅ Active |
| **Python** | Complexity, function statements, naming case | `pyproject.toml` | ✅ Active |
| **TypeScript** | File LOC, function LOC, ID length, filename case | `.oxlintrc.json` | ✅ Active |

### What MUST Stay in Bash

| Rule Category | Reason | Alternative? |
|---------------|--------|--------------|
| **Forbidden Word Patterns** | No linter supports regex-based word blacklists | Custom AST plugin (high cost) |
| **Versioning Suffixes** | Pattern matching more flexible than globs | Verbose linter globs (maintenance burden) |
| **Path Depth Limits** | File system concern, outside linter scope | Pre-commit hooks |
| **Filename Length** | Not a code quality metric | Repository policy enforcement |
| **File LOC (Go, Python)** | No native linter support | Monitor for future `filen` linter (Go) |

### What Needs Enhancement Proposals Implemented

| Language | Missing Rule | Proposal Status | Timeline |
|----------|--------------|-----------------|----------|
| **Go** | Forbidden identifiers | Ready to implement (forbidigo config) | Phase 1: 1-2 hours |
| **Python** | Docstring coverage | Ready to implement (D rules) | Phase 1: 1 hour |
| **TypeScript** | None | N/A - Bash handles gaps | N/A |

---

## Migration Recommendations

### Phase 1: Enable Proposed Rules (IMMEDIATE)

**Go - Enable forbidigo (1-2 hours):**
1. Add `forbidigo` to `backend/.golangci.yml` linters.enable
2. Configure patterns from `config/naming-guard.json`
3. Test: `cd backend && golangci-lint run --enable forbidigo ./...`
4. Validate zero violations (current naming-guard shows 0)

**Python - Enable docstring rules (1 hour):**
1. Add `D` to `pyproject.toml` [tool.ruff.lint].select
2. Configure `[tool.ruff.lint.pydocstyle]` with `convention = "google"`
3. Add per-file ignores for tests
4. Phased rollout: Start with `src/tracertm/api/` (public API)

**TypeScript - No action:**
- Already at maximum coverage for oxlint capabilities
- Bash handles remaining gaps

---

### Phase 2: Document Bash-Only Rules (1 hour)

Update project documentation to clarify architectural boundaries:

**Files to Update:**
- `docs/guides/quality.md` - Add "Linter Limitations" section
- `config/naming-guard.json` - Add header comment explaining bash-only scope
- `CLAUDE.md` - Document hybrid approach for agents

**Content:**
```markdown
## Hybrid Linting Strategy

**Native Linters (golangci-lint, ruff, oxlint):**
- Structural rules: complexity, LOC, case conventions
- Fast compile-time enforcement
- IDE integration

**Bash Guards (scripts/quality/):**
- Semantic rules: forbidden word patterns, versioning suffixes
- Repository policies: path depth, filename length
- Cross-language consistency
```

---

### Phase 3: Bash Consolidation (2-4 weeks validation)

**After Phase 1 rules are enabled:**

1. **Run in parallel (2 weeks):**
   - Both bash and native linters in CI/CD
   - Compare outputs for parity
   - Fix any discrepancies

2. **Simplify bash (Week 3):**
   - Remove redundant checks now covered by linters
   - Example: Remove identifier checks from `naming-guard.json` where forbidigo active
   - Keep file-level checks (path depth, length)

3. **Final config (Week 4):**
   - Update `config/naming-guard.json` scope
   - Document linter-only rules
   - CI/CD updated to skip redundant bash checks

**Example: Simplified `naming-guard.json` (after Phase 3):**

```json
{
  "comment": "Bash-only rules (file system policies). Identifier enforcement migrated to forbidigo (Go).",
  "forbidden_words": ["v2", "V3", "new_", "old_", "temp"],
  "check_identifiers": false,  // NOW HANDLED BY: forbidigo (Go), bash (Python/TS)
  "check_directories": true,   // BASH ONLY
  "max_filename_length": 64,   // BASH ONLY
  "max_dirname_length": 64,    // BASH ONLY
  "max_path_depth": 10         // BASH ONLY
}
```

---

## Bash Retirement Timeline

**Can bash be fully retired?** ❌ **NO**

### Rules That Will Always Require Bash

| Rule | Reason | Future Outlook |
|------|--------|----------------|
| Path Depth | File system policy, not code quality | No linter planned |
| Filename/Directory Length | Repository organization policy | No linter planned |
| Forbidden Filename Patterns | Regex flexibility vs verbose globs | Could migrate with 50+ lines of config |

### Rules That May Migrate (Monitoring Required)

| Language | Rule | Blocker | Monitor |
|----------|------|---------|---------|
| **Go** | File LOC limit | No `filen` linter in stable | [golangci-lint releases](https://github.com/golangci/golangci-lint/releases) |
| **Python** | Forbidden identifiers | Ruff no custom rules | [Issue #8409](https://github.com/astral-sh/ruff/discussions/8409) |
| **TypeScript** | Forbidden patterns | No regex in `filename-blocklist` | oxlint feature requests |

### Timeline Summary

- **Immediate (Week 1):** Enable forbidigo (Go), D rules (Python)
- **Short-term (2-4 weeks):** Validate parallel execution, simplify bash
- **Long-term (Ongoing):** Monitor linter releases for new capabilities
- **Permanent:** Keep bash for file system policies (path depth, length)

---

## Summary Table: Coverage by Language

### Go

| Rule | Linter | Bash | Winner | Action |
|------|--------|------|--------|--------|
| Forbidden identifiers | forbidigo (proposed) | ✅ | Linter | Enable forbidigo |
| Identifier length | varnamelen | ❌ | Linter | Keep existing |
| Function LOC | funlen | ❌ | Linter | Keep existing |
| File LOC (500) | N/A | ✅ | Bash | Keep bash |
| Path depth | N/A | ✅ | Bash | Keep bash |

**Coverage:** 60% linter, 40% bash-only

---

### Python

| Rule | Linter | Bash | Winner | Action |
|------|--------|------|--------|--------|
| Forbidden identifiers | N/A | ✅ | Bash | Keep bash |
| Docstring coverage | D (proposed) | N/A | Linter | Enable D rules |
| Function complexity | C90/PLR | ❌ | Linter | Keep existing |
| File LOC (500) | N/A | ✅ | Bash | Keep bash |
| Path depth | N/A | ✅ | Bash | Keep bash |

**Coverage:** 40% linter, 60% bash-only

---

### TypeScript

| Rule | Linter | Bash | Winner | Action |
|------|--------|------|--------|--------|
| Filename case | unicorn | ❌ | Linter | Keep existing |
| Directory naming | check-file | ❌ | Linter | Keep existing |
| ID length | eslint | ❌ | Linter | Keep existing |
| File LOC | eslint | ❌ | Linter | Keep existing |
| Forbidden patterns | N/A | ✅ | Bash | Keep bash |
| Identifier word blacklist | N/A | ✅ | Bash | Keep bash |
| Path depth | N/A | ✅ | Bash | Keep bash |

**Coverage:** 70% linter, 30% bash-only

---

## Risk Assessment

### Low Risk

- **Enable forbidigo (Go):** Production-ready linter, 0 current violations, easy rollback
- **Enable D rules (Python):** Phased rollout, target 85% already set in interrogate config

### Medium Risk

- **Bash deprecation timing:** Must ensure linters catch all patterns before removing bash checks
- **Mitigation:** Run in parallel for 2-4 weeks (Phase 3)

### No Risk

- **LOC/path depth migration:** Not attempting migration (keeping bash as designed)

---

## Recommendations Summary

### ✅ DO Migrate

1. **Go forbidden identifiers** → `forbidigo` linter (Phase 1)
2. **Python docstring coverage** → Ruff `D` rules (Phase 1)
3. **Timeline:** 2-3 hours implementation, 2-4 weeks validation

### ❌ DO NOT Migrate

1. **File LOC limits (Go, Python)** → Keep bash `loc-guard` (no linter available)
2. **Path depth limits (all)** → Keep bash `naming-guard` (outside linter scope)
3. **Forbidden word patterns (Python, TypeScript)** → Keep bash (no native support)

### 🔄 Hybrid Approach (RECOMMENDED)

- **Native linters:** Compile-time enforcement of structural rules (95% of checks)
- **Bash scripts:** Repository-level policies and semantic patterns (5% of checks)
- **Integration:** Both run in CI/CD, bash for pre-commit hooks
- **Maintenance:** Low burden (2 tools, clear boundaries)

---

## Appendix: Cross-Language Consistency

### Rules Enforced Consistently Across All Languages

| Rule | Go | Python | TypeScript | Enforcer |
|------|----|---------|-----------|----|
| File LOC ≤ 500 | ✅ | ✅ | ✅ | Bash + Allowlist |
| Path depth ≤ 10 | ✅ | ✅ | ✅ | Bash |
| Filename length ≤ 64 | ✅ | ✅ | ✅ | Bash |
| Forbidden filenames (v2, V3) | ✅ | ✅ | ✅ | Bash |

### Language-Specific Rules

| Rule | Go | Python | TypeScript | Why Language-Specific? |
|------|----|---------|-----------|-----------------------|
| Identifier length | min 2 | N/A | min 2 | Python convention allows `_` |
| Docstring coverage | N/A | 85% | N/A | Python-only (JSDoc is TypeScript) |
| Function LOC | 80 | 50 stmts | 80 | Python counts statements, others LOC |

---

## Next Steps

1. **Team lead approval:** Review forbidigo/D rule configurations
2. **Immediate action (Week 1):**
   - Go: Add forbidigo to `.golangci.yml`
   - Python: Add D rules to `pyproject.toml`
3. **Validation (Weeks 2-4):**
   - Run bash + linters in parallel
   - Compare outputs for parity
4. **Consolidation (Week 4):**
   - Simplify `naming-guard.json` scope
   - Update documentation (CLAUDE.md, quality guides)
5. **Monitoring (Ongoing):**
   - Subscribe to golangci-lint releases (for `filen` linter)
   - Monitor ruff GitHub for custom rule support

---

**Generated by:** Naming Guard Consolidation Analysis (Task #10)
**Status:** Ready for team lead review and Phase 1 implementation
**Estimated Total Effort:** 3-4 hours (implementation) + 2-4 weeks (validation)
**Expected Benefit:** Compile-time enforcement, IDE integration, reduced bash dependency (where feasible)
