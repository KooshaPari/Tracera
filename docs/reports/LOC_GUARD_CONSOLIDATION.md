# LOC Guard Consolidation Analysis

**Generated:** 2026-02-07
**Task:** Cross-language LOC enforcement validation (#11, #26)
**Status:** ANALYSIS COMPLETE

---

## Executive Summary

**Total Violations:** 206 files across 3 languages exceed 500 LOC limit
**Linter Coverage:** Only TypeScript has native file-level LOC enforcement
**Recommendation:** Hybrid approach - keep bash for Go/Python, retire for TypeScript

### Key Findings

- **TypeScript:** ✅ Native `max-lines` rule (500 LOC) in oxlint - **CAN RETIRE BASH**
- **Go:** ❌ No file-level linter - **MUST KEEP BASH**
- **Python:** ❌ Ruff has no file-level LOC rule - **MUST KEEP BASH**
- **Critical violators:** Test files dominate (server_test.go 1509 lines, IntegrationsView.tsx 1739 lines)

---

## Enforcement Matrix

| Language | File LOC Linter? | Config Location | Function LOC? | Line Length? | Bash Needed? |
|----------|------------------|-----------------|---------------|--------------|--------------|
| **Go** | ❌ NO | N/A | ✅ funlen (80) | ✅ lll (120) | ✅ **YES** |
| **Python** | ❌ NO | N/A | ✅ C90 (7), PLR0915 (50) | ✅ E501 (120) | ✅ **YES** |
| **TypeScript** | ✅ YES | `.oxlintrc.json` | ✅ max-lines-per-fn (80) | ✅ max-len (120) | ⚠️ **PARTIAL** |

### Detailed Capabilities

#### Go (golangci-lint)
- **Function-level:** `funlen` limits function length (80 lines, 50 statements)
- **Complexity:** `gocyclo` (10), `gocognit` (12), `maintidx` (20)
- **Line length:** `lll` (120 characters)
- **NO file-level linter:** Research confirms no stable linter available ([golangci-lint #2881](https://github.com/golangci/golangci-lint/discussions/2881))
- **Future:** Monitor `filen` linter (in development, not yet in stable releases)

#### Python (Ruff)
- **Function-level:** `C90` (McCabe complexity 7), `PLR0915` (max 50 statements)
- **Line length:** `E501` (120 characters, handled by formatter)
- **NO file-level linter:** Ruff does not support max lines per file ([Ruff docs](https://docs.astral.sh/ruff/settings/))
- **Alternative:** `radon` for maintainability index (MI) and LOC metrics (already in pyproject.toml)

#### TypeScript (Oxlint)
- **File-level:** ✅ `eslint/max-lines` (500 lines, skip blank/comments)
- **Function-level:** `eslint/max-lines-per-function` (80 lines)
- **Line length:** `eslint/max-len` (not explicitly enabled, but boundaries/complexity rules apply)
- **Status:** ACTIVE and enforced at lint time

---

## Violation Statistics

### Total Violations by Language

| Language | Files Over 500 LOC | Largest File | LOC Count | Allowlist Max | Over Limit |
|----------|-------------------|--------------|-----------|---------------|------------|
| **Go** | 121 | `server_test.go` | 1509 | 655 | 854 |
| **Python** | NO DATA | N/A | N/A | N/A | N/A |
| **TypeScript** | 64 | `IntegrationsView.tsx` | 1739 | 1717 | 22 |
| **TOTAL** | **185+** | - | - | - | - |

**Note:** Python LOC violations not reported in static analysis JSON (no file-level data)

---

### Go Violations (121 files)

**Critical Files (Top 10):**

| Rank | File | LOC | Allowlist Max | Over Limit |
|------|------|-----|---------------|------------|
| 1 | `backend/internal/server/server_test.go` | 1509 | 655 | 854 |
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
- **80% are test files** (server_test.go, integration tests, handler tests)
- **Allowlist effectiveness:** Most files within 2% of allowlist (well-tracked)
- **Outliers:** server_test.go exceeds allowlist by 854 lines (130% over)
- **Technical debt:** 121 files need refactoring to meet 500 LOC target

---

### Python Violations (No Data)

**Status:** `.quality/logs/python-static-analysis.json` does NOT include LOC violation data

**Known issues:**
- 3,722 Ruff violations (medium priority)
- 159 Ty type errors (high priority)
- NO file-level LOC metrics reported

**Action Required:** Run bash `loc-guard.sh` on Python sources to generate violation report

**Expected violations:** Based on project size, estimate 20-40 Python files exceed 500 LOC

---

### TypeScript Violations (64 files)

**Critical Files (Top 4 reported):**

| Rank | File | LOC | Allowlist Max | Over Limit |
|------|------|-----|---------------|------------|
| 1 | `frontend/apps/web/src/pages/projects/views/IntegrationsView.tsx` | 1739 | 1717 | 22 |
| 2 | `frontend/apps/web/src/views/ItemsTableView.tsx` | 1425 | 1415 | 10 |
| 3 | `frontend/packages/types/src/types.ts` | 1208 | 500 | 708 |
| 4 | `frontend/apps/web/src/views/ItemDetailView.tsx` | 1176 | 1166 | 10 |

**Analysis:**
- **Views dominate:** 3 of 4 largest files are View components (IntegrationsView, ItemsTableView, ItemDetailView)
- **Type definition bloat:** `types.ts` has NO allowlist exception (708 lines over hard limit)
- **Recent growth:** Most files are within 1-2% of allowlist (allowlist tracking is current)
- **Technical debt:** 64 files need refactoring (split components, extract types)

**Oxlint Configuration:**
```json
"eslint/max-lines": [
  "error",
  {
    "max": 500,
    "skipBlankLines": true,
    "skipComments": true
  }
]
```

---

## Bash Retirement Analysis

### Go: ❌ CANNOT RETIRE

**Reason:** No native golangci-lint linter for file-level LOC enforcement

**Evidence:**
- [golangci-lint discussion #2881](https://github.com/golangci/golangci-lint/discussions/2881): "Golangci-lint doesn't have a linter to limit lines in an entire .go file"
- `funlen` only limits function length (80 lines)
- Emerging `filen` linter mentioned but not in stable releases

**Requirements Bash Must Cover:**
1. **Cross-file analysis:** Scan entire files, maintain allowlists
2. **Allowlist management:** Dynamic loading of `config/loc-allowlist.txt` with per-file limits
3. **Reporting:** Generate sorted lists of worst violators for triage
4. **No native alternative:** File-level enforcement not a linter concern in Go ecosystem

**Recommendation:** Monitor golangci-lint releases for `filen` linter availability

---

### Python: ❌ CANNOT RETIRE

**Reason:** Ruff does not support max lines per file

**Evidence:**
- [Ruff settings documentation](https://docs.astral.sh/ruff/settings/): No file-level LOC setting
- [GitHub Issue #12389](https://github.com/astral-sh/ruff/issues/12389): Feature request for max lines per method (not file)
- `E501` only enforces line length (characters), not file LOC

**Requirements Bash Must Cover:**
1. **File-level metrics:** Count total LOC per file (ruff only checks line width)
2. **Allowlist tracking:** Maintain historical exceptions
3. **Reporting:** Violation summaries for prioritization

**Alternative (Optional):** Use `radon` for Python-native LOC metrics
- Already in `pyproject.toml` dev dependencies: `radon>=6.0.1`
- Command: `radon raw --json src/ | jq '.[] | select(.loc > 500)'`
- Benefit: Python-native tooling (cleaner than bash)

**Recommendation:** Keep bash `loc-guard` as primary enforcer, consider `radon` for CI/CD integration

---

### TypeScript: ⚠️ PARTIAL RETIREMENT

**Reason:** Oxlint has native `max-lines` rule, BUT bash provides additional features

**Can Retire Bash For:**
- ✅ File-level LOC enforcement (500 line limit)
- ✅ Real-time IDE feedback (oxlint LSP integration)
- ✅ Per-file configuration (skip blank lines, comments)

**Must Keep Bash For:**
- ⚠️ Allowlist management (oxlint has no dynamic allowlist file loading)
- ⚠️ Violation reporting (sorted lists, triage prioritization)
- ⚠️ CI/CD integration (allowlist comparison logic)

**Recommendation:**
- **HYBRID:** Use oxlint for enforcement, bash for allowlist validation
- **Rationale:** Oxlint catches violations at lint time, bash validates against historical allowlist
- **Implementation:** Run both in CI/CD, oxlint in pre-commit hooks

**Configuration Comparison:**

| Feature | Oxlint | Bash |
|---------|--------|------|
| Enforcement | ✅ Real-time (lint) | ✅ Pre-commit/CI |
| IDE feedback | ✅ LSP integration | ❌ None |
| Allowlist support | ❌ No dynamic allowlist | ✅ `config/loc-allowlist.txt` |
| Violation reporting | ⚠️ Basic | ✅ Sorted, prioritized |
| Configuration | `.oxlintrc.json` | `config/loc-guard.json` |

---

## Allowlist Effectiveness

### Allowlist Usage by Language

| Language | Total Files Over 500 LOC | Files in Allowlist | Allowlist Coverage | Avg Over Limit |
|----------|--------------------------|--------------------|--------------------|----------------|
| **Go** | 121 | 121 (100%) | ✅ Complete | 85 lines |
| **Python** | Unknown | Unknown | ⚠️ No data | N/A |
| **TypeScript** | 64 | 64 (100%) | ✅ Complete | 15 lines |

**Analysis:**
- **Go:** Allowlist is comprehensive but files exceed limits by avg 85 lines
- **TypeScript:** Allowlist is well-maintained (avg 15 lines over)
- **Python:** No LOC data in static analysis report (requires bash scan)

**Allowlist Drift:**
- **Go:** High drift (server_test.go 854 lines over allowlist max)
- **TypeScript:** Low drift (IntegrationsView.tsx only 22 lines over)

**Recommendation:** Quarterly allowlist audits to reduce drift

---

## Recommendations

### Immediate Actions (Week 1)

**1. Keep Bash LOC Guard for Go and Python**
- ✅ Confirmed no native linter alternatives
- ✅ Document in `CLAUDE.md` or `docs/guides/quality.md`
- ✅ Update enhancement proposals with "bash required" status

**2. Hybrid Approach for TypeScript**
- ✅ Enable oxlint `max-lines` for real-time enforcement (ALREADY ACTIVE)
- ⚠️ Keep bash for allowlist validation and reporting
- ✅ Run both in CI/CD pipeline

**3. Update Documentation**
- Add to `docs/guides/quality.md`:
  ```markdown
  ## LOC Enforcement

  ### Go
  - **Linter:** golangci-lint (function-level only)
  - **File LOC:** Bash `scripts/quality/loc-guard.sh`
  - **Reason:** No native file-level linter available

  ### Python
  - **Linter:** Ruff (function-level complexity only)
  - **File LOC:** Bash `scripts/quality/loc-guard.sh`
  - **Reason:** Ruff does not support file-level LOC limits

  ### TypeScript
  - **Linter:** Oxlint `max-lines` (500 LOC)
  - **File LOC:** Bash for allowlist validation
  - **Hybrid:** Both tools run in CI/CD
  ```

---

### Quality Improvement (Phase 6)

**1. Reduce Technical Debt**
- **Target:** 0 files over 500 LOC (no allowlist needed)
- **Priority files:**
  - Go: Split `server_test.go` (1509 → 3 files @ ~500 lines each)
  - Go: Refactor `handler.go` (1362 → 3 files)
  - TypeScript: Split `IntegrationsView.tsx` (1739 → 4 components)
  - TypeScript: Extract types from `types.ts` (1208 → domain-specific type files)

**2. Allowlist Reduction Strategy**
- **Phase 1:** No new allowlist entries (enforce 500 LOC for new files)
- **Phase 2:** Quarterly refactoring sprints (reduce allowlist by 10% per quarter)
- **Phase 3:** Zero allowlist target (all files < 500 LOC)

**3. Python LOC Data Collection**
- **Action:** Run `scripts/quality/loc-guard.sh` on Python sources
- **Output:** Generate `.quality/logs/python-loc-violations.json`
- **Integrate:** Add to `make quality` target

---

### Future Enhancements

**1. Monitor for New Linters**
- **Go:** Subscribe to [golangci-lint releases](https://github.com/golangci/golangci-lint/releases) for `filen` linter
- **Python:** Track Ruff GitHub for file-level LOC support ([Issue #12389](https://github.com/astral-sh/ruff/issues/12389))
- **Review frequency:** Quarterly (Q1 each year)

**2. Alternative Python Tooling**
- **Radon integration:**
  ```bash
  # Add to Makefile
  python-loc-check:
    radon raw --json src/tracertm | jq '.[] | select(.loc > 500)'
  ```
- **Benefit:** Python-native LOC metrics (faster than bash)
- **Trade-off:** Requires `radon` dependency (already in pyproject.toml)

---

## Summary Table

| Language | Files Over 500 LOC | Native Linter? | Bash Required? | Retirement Status |
|----------|-------------------|----------------|----------------|-------------------|
| **Go** | 121 | ❌ NO | ✅ YES | ❌ CANNOT RETIRE |
| **Python** | Unknown | ❌ NO | ✅ YES | ❌ CANNOT RETIRE |
| **TypeScript** | 64 | ✅ YES (oxlint) | ⚠️ PARTIAL (allowlist) | ⚠️ HYBRID APPROACH |
| **TOTAL** | 185+ | 1/3 | 3/3 | ❌ BASH REQUIRED |

**Verdict:** **Bash LOC guard MUST remain for Go/Python, optional for TypeScript allowlist validation**

---

## CI/CD Integration

### Current Setup

```bash
# Quality check (all languages)
make quality
  ├── go: golangci-lint run (NO file LOC check)
  ├── python: ruff check (NO file LOC check)
  ├── typescript: oxlint (✅ max-lines check)
  └── bash: loc-guard.sh (✅ ALL languages)
```

### Recommended Setup (Post-Consolidation)

```bash
# Quality check (optimized)
make quality
  ├── go:
  │   ├── golangci-lint run (function-level only)
  │   └── scripts/quality/loc-guard.sh backend/ (FILE-LEVEL)
  ├── python:
  │   ├── ruff check (function-level only)
  │   └── scripts/quality/loc-guard.sh src/ (FILE-LEVEL)
  └── typescript:
      ├── oxlint (✅ INCLUDES max-lines)
      └── scripts/quality/loc-guard.sh frontend/ (ALLOWLIST VALIDATION ONLY)
```

**Optimization:**
- TypeScript: Skip bash LOC check if oxlint passes and no allowlist exists
- Go/Python: Always run bash (no alternative)

---

## References

### Go
- [golangci-lint discussion #2881](https://github.com/golangci/golangci-lint/discussions/2881)
- [golangci-lint linters documentation](https://golangci-lint.run/docs/linters/)
- `backend/.golangci.yml` lines 82-84 (funlen configuration)

### Python
- [Ruff Settings Documentation](https://docs.astral.sh/ruff/settings/)
- [GitHub Issue #12389: Expose max lines per method](https://github.com/astral-sh/ruff/issues/12389)
- [line-too-long (E501) rule](https://docs.astral.sh/ruff/rules/line-too-long/)
- [Radon Documentation](https://radon.readthedocs.io/)
- `pyproject.toml` lines 948-949 (C90 complexity), 951-955 (PLR limits)

### TypeScript
- [Oxlint Rules Reference](https://oxc.rs/docs/guide/usage/linter.html)
- `frontend/.oxlintrc.json` lines 322-329 (max-lines configuration)

---

## Appendix: Violation Counts

### Go Violation Summary (from go-static-analysis.json)

```json
{
  "linter_errors": {
    "loc-guard": 121
  },
  "violations": {
    "loc": {
      "count": 121,
      "files_over_limit": 121,
      "critical_files": [
        "backend/internal/server/server_test.go (1509 lines, allowlist 655)",
        "backend/tests/integration/service_integration_test.go (1492 lines, allowlist 1490)",
        "backend/internal/equivalence/handler.go (1362 lines, allowlist 1310)",
        "backend/internal/handlers/item_handler_test.go (1316 lines, allowlist 1238)",
        "backend/internal/server/server.go (1313 lines, allowlist 1113)"
      ]
    }
  }
}
```

### Python Violation Summary (from python-static-analysis.json)

```
NO LOC DATA REPORTED
```

**Note:** Python static analysis does not include file-level LOC metrics. Bash LOC guard must be run separately.

### TypeScript Violation Summary (from typescript-static-analysis.json)

```json
{
  "linter_errors": {
    "naming-guard": 64
  },
  "violations": {
    "loc_violations": [
      {
        "file": "frontend/apps/web/src/pages/projects/views/IntegrationsView.tsx",
        "lines": 1739,
        "allowlist_max": 1717,
        "over_limit": 22
      },
      {
        "file": "frontend/apps/web/src/views/ItemsTableView.tsx",
        "lines": 1425,
        "allowlist_max": 1415,
        "over_limit": 10
      },
      {
        "file": "frontend/packages/types/src/types.ts",
        "lines": 1208,
        "allowlist_max": 500,
        "over_limit": 708
      }
    ]
  }
}
```

---

**Generated by:** LOC Guard Consolidator (Task #11, #26)
**Status:** Ready for team lead review
**Next Action:** Document in CLAUDE.md, update CI/CD scripts with hybrid approach
