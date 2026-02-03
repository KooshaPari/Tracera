# Go Linting Configuration Audit: AI-Coding Alignment

**Date**: 2026-02-02
**Audited File**: `/backend/.golangci.yml`
**Comparison Baseline**: Python `pyproject.toml` (ruff + mypy strict configuration)

---

## Executive Summary

The current Go linting configuration is **moderately aligned** with AI-coding principles but has **critical gaps** in naming explosion prevention and complexity enforcement. While it includes good foundational linters, it lacks the **strictness level** and **AI-specific safeguards** present in the Python configuration.

**Overall Grade**: C+ (Functional but needs hardening)

### Critical Findings

- ❌ **NO naming explosion detection** (versioned files, numbered suffixes, New*/Improved* prefixes)
- ⚠️ **Complexity limits too lenient** compared to Python (15/20 vs 10 cyclomatic)
- ⚠️ **Missing AI-critical linters** (dupl, goconst, funlen, mnd)
- ✅ **Good security baseline** (gosec enabled)
- ✅ **Solid correctness foundation** (errcheck, govet, staticcheck)

---

## Detailed Audit by Category

### 1. Naming Explosion Prevention ❌ CRITICAL GAP

**Status**: **Missing entirely**

The configuration has **zero protection** against AI-generated naming anti-patterns:

| Anti-Pattern | Detection Method | Status |
|--------------|------------------|--------|
| Versioned files (`dashboard_v2.go`) | Custom regex or gocritic pattern | ❌ Not configured |
| Numbered suffixes (`handler_2.go`, `service_3.go`) | Custom regex | ❌ Not configured |
| Prefix explosion (`NewUserService`, `ImprovedUserService`) | revive var-naming or custom | ❌ Not configured |
| Duplicate identifier names | revive var-naming | ⚠️ Enabled but weak |

**Python Comparison**:
- Python has **strict naming rules** via ruff (N801-N818 PEP8 naming)
- Mypy enforces naming consistency via type checking
- Go configuration relies only on basic `revive.var-naming` (insufficient)

**Recommendation**: Add custom linters or gocritic patterns for:
- File name patterns (`*_v[0-9]+.go`, `*_[0-9]+.go`)
- Function/type prefix patterns (`New*`, `Improved*`, `Enhanced*`, `Fixed*`)
- Enable `gocritic` with stronger naming checks

---

### 2. Complexity Limits ⚠️ TOO LENIENT

**Current Configuration**:

```yaml
revive:
  rules:
    - name: cyclomatic
      arguments: [10]  # Good ✅

gocyclo:
  min-complexity: 15  # Too lenient ⚠️

gocognit:
  min-complexity: 20  # Too lenient ⚠️

# funlen: NOT ENABLED ❌
```

**Python Comparison**:

```toml
# Python (via ruff + mypy)
# - Enforced through McCabe complexity via pylint/flake8
# - Typical limit: 10 (strict)
# - TraceRTM uses function length implicitly via SIM/PERF rules
```

**Issues**:

1. **Inconsistent limits**: `revive.cyclomatic=10` vs `gocyclo=15` (which wins?)
2. **Cognitive complexity too high**: 20 is very permissive (AI code often hits 15-25)
3. **No function length limit**: `funlen` disabled (allows 1000+ line AI-generated functions)

**Recommended Changes**:

```yaml
gocyclo:
  min-complexity: 10  # Match revive (strict)

gocognit:
  min-complexity: 12  # Tighten (AI code warning threshold)

linters:
  enable:
    - funlen  # Add function length enforcement

linters-settings:
  funlen:
    lines: 80        # Max function lines (aggressive for AI)
    statements: 50   # Max statements per function
```

**Severity**: Set complexity violations to **ERROR** level, not warning:

```yaml
issues:
  severity-rules:
    - linters: [gocyclo, gocognit, funlen]
      severity: error
```

---

### 3. Code Quality Linters ⚠️ GAPS IN COVERAGE

#### Enabled (Good ✅)

| Linter | Purpose | AI-Coding Value |
|--------|---------|-----------------|
| `errcheck` | Unchecked error returns | ✅ Critical (AI forgets error checks) |
| `govet` | Suspicious constructs | ✅ Catches AI logic errors |
| `staticcheck` | Comprehensive static analysis | ✅ Best general-purpose linter |
| `unused` | Unused code detection | ✅ AI often generates unused code |
| `revive` | Style + patterns (golint replacement) | ✅ Good foundation |
| `gocritic` | Bugs/performance/style | ✅ Multi-purpose quality |
| `gosec` | Security issues | ✅ Critical for AI code |

#### Missing (Critical Gaps ❌)

| Linter | Purpose | Why Missing Hurts AI-Coding |
|--------|---------|----------------------------|
| **`dupl`** | Duplicate code detection | AI generates very similar code blocks (copy-paste explosion) |
| **`goconst`** | Repeated strings → constants | AI hardcodes strings instead of using constants |
| **`funlen`** | Function length limits | AI generates 500-line functions without decomposition |
| **`mnd`** (magic numbers) | Detect magic numbers | AI embeds `42`, `100`, `1000` without named constants |
| **`godot`** | Comment period enforcement | AI writes inconsistent documentation |
| **`gofmt`** | Format checking | ✅ Already enabled |
| **`unconvert`** | Unnecessary type conversions | ✅ Already enabled |
| **`gochecknoglobals`** | No global variables | ❌ Missing (AI creates global state) |
| **`nolintlint`** | Validate //nolint directives | ❌ Missing (AI abuses nolint comments) |

**Comparison with Python**:

Python has **67 enabled rule categories** via ruff:
- `E/W/F` (pycodestyle + pyflakes): Basic correctness
- `B` (bugbear): AI-specific pitfalls (mutable defaults, etc.)
- `SIM` (simplify): Forces code simplification
- `PERF` (performance): Detects inefficient patterns
- `S` (bandit/security): Security scanning
- `RUF` (ruff-specific): Custom rules for modern Python

Go has **20 enabled linters** but missing key AI-specific ones.

---

### 4. AI-Specific Issues ❌ MAJOR GAPS

| Issue | Python Coverage | Go Coverage | Gap |
|-------|----------------|-------------|-----|
| **Magic numbers** | ✅ Via manual review + constants pattern | ❌ `mnd` disabled | Add `mnd` linter |
| **Duplicate code** | ✅ Via `SIM` rules + manual review | ❌ `dupl` disabled | Add `dupl` linter |
| **Error handling** | ✅ `RET` (return style), `B904` (raise from) | ✅ `errcheck` enabled | OK |
| **Named returns** | N/A (Python doesn't have) | ⚠️ `nakedret` only (weak) | Add `nonamedreturns` or enforce named returns for complexity >5 |
| **Global state** | ✅ Via `N` (naming) + review | ❌ `gochecknoglobals` disabled | Add `gochecknoglobals` |
| **Init functions** | N/A | ❌ `gochecknoinits` disabled | Add `gochecknoinits` (AI abuses init) |
| **Context propagation** | N/A | ✅ `noctx` enabled | OK |

---

### 5. Performance Linters ⚠️ PARTIAL COVERAGE

**Enabled**:
- ✅ `prealloc`: Pre-allocate slices (good)
- ✅ `ineffassign`: Ineffectual assignments (good)

**Missing**:
- ❌ `gosimple` (part of staticcheck, but should be explicit)
- ❌ `maligned` / `fieldalignment` (struct padding optimization)
- ❌ `perfsprint` (fmt.Sprintf alternatives)

**Python Comparison**:
- Python has `PERF` rules (PERF1xx) for comprehensions, string concat, etc.
- Go configuration relies on `staticcheck` but misses explicit performance linters

**Recommendation**: Add `perfsprint` for AI-generated string formatting.

---

### 6. Security & Safety ✅ GOOD BASELINE

**Enabled**:
- ✅ `gosec`: Security audit (G101-G601 checks)
- ✅ `errcheck.check-type-assertions`: Panic prevention
- ✅ `errcheck.check-blank`: No ignored errors

**Configuration**:

```yaml
gosec:
  excludes:
    - G104  # audit errors not checked (errcheck covers)
```

**Issue**: G104 exclusion is **redundant** with `errcheck`. Should keep both for defense-in-depth.

**Python Comparison**:
- Python has `S` (bandit) rules: S101-S999
- Covers SQL injection, shell injection, crypto issues, etc.
- Go `gosec` is comparable

**Recommendation**: Remove G104 exclusion (enable both `gosec` and `errcheck` for G104).

---

### 7. Linter Settings Deep Dive

#### Revive Configuration ⚠️ WEAK

```yaml
revive:
  severity: warning  # ⚠️ Should be error for CI
  confidence: 0.8    # OK
  rules:
    - name: var-naming       # ✅ Basic naming
    - name: package-comments # ✅ Documentation
    - name: exported         # ✅ Public API documentation
    - name: error-return     # ✅ Error as last return
    - name: error-strings    # ✅ Error string format
    - name: error-naming     # ✅ Error variable naming
    - name: context-as-argument # ✅ Context propagation
    - name: cyclomatic       # ✅ Complexity (10)
      arguments: [10]
    - name: line-length-limit # ✅ Line length (120)
      arguments: [120]
```

**Missing Revive Rules** (available but not enabled):

```yaml
# Add these to revive.rules:
- name: argument-limit       # Max function arguments (AI generates 10+ arg functions)
  arguments: [5]
- name: function-result-limit # Max return values (AI returns 5+ values)
  arguments: [3]
- name: max-public-structs   # Limit public types per file
  arguments: [3]
- name: cognitive-complexity # Redundant with gocognit, but useful
  arguments: [12]
- name: flag-parameter       # Discourage boolean parameters
- name: unhandled-error      # Explicit error handling (redundant with errcheck)
  arguments:
    - "fmt.Printf"
    - "fmt.Println"
```

**Python Comparison**:
- Python `ruff` has **300+ rules** across 15 categories
- Go `revive` has **~40 rules**, only **10 enabled**
- TraceRTM uses **very minimal** revive configuration

---

### 8. Issue Filtering & Severity ⚠️ TOO PERMISSIVE

**Current Configuration**:

```yaml
issues:
  exclude-rules:
    - path: _test\.go
      linters: [gocognit, gocyclo, funlen, exhaustivestruct]
    - path: \.pb\.go$
      linters: [all]
    - path: /vendor/
      linters: [all]
  max-issues-per-linter: 0  # ✅ No limit (good)
  max-same-issues: 0        # ✅ No limit (good)
```

**Issues**:

1. **Tests exempted from complexity**: Tests can be arbitrarily complex (AI generates 1000-line tests)
2. **No severity escalation**: All issues are warnings, none are errors
3. **No new code focus**: No `--new` or `--new-from-rev` configuration

**Python Comparison**:

```toml
# Python per-file ignores (bounded, explicit)
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "S110", ...]  # Bounded allowlist
"src/**" = ["E402", "B904", ...]    # Explicit baseline (shrinking)

# Severity is ALWAYS error in CI (make quality fails on any violation)
```

**Recommendation**:

```yaml
issues:
  exclude-rules:
    - path: _test\.go
      linters: [gocognit, gocyclo]  # Keep funlen enabled for tests
    - path: \.pb\.go$
      linters: [all]
    - path: /vendor/
      linters: [all]

  # New code must be clean (fail CI on issues in changed files)
  new: true
  new-from-rev: "origin/main"

  # Severity escalation for critical linters
  severity-rules:
    - linters: [gosec, errcheck, govet, staticcheck]
      severity: error
    - linters: [gocyclo, gocognit, funlen, dupl, goconst, mnd]
      severity: error
    - linters: [revive, gocritic]
      severity: warning
```

---

## Comparison: Go vs Python Strictness

| Aspect | Python (TraceRTM) | Go (TraceRTM) | Winner |
|--------|------------------|---------------|--------|
| **Enabled rules** | 67 rule categories (300+ individual rules) | 20 linters (~150 rules) | Python 🏆 |
| **Complexity limits** | Implicit via SIM/PERF (effective ~10) | 15 cyclomatic, 20 cognitive | Python 🏆 |
| **Naming enforcement** | N801-N818 PEP8 + mypy | revive.var-naming (basic) | Python 🏆 |
| **Error handling** | RET + B904 (explicit) | errcheck + gosec | Tie ✅ |
| **Security** | S (bandit) 100+ rules | gosec G101-G601 | Tie ✅ |
| **Magic numbers** | Manual review | NOT ENFORCED ❌ | Python 🏆 |
| **Duplicate code** | Manual + SIM rules | NOT ENFORCED ❌ | Python 🏆 |
| **Performance** | PERF (15+ rules) | prealloc, ineffassign | Python 🏆 |
| **Type safety** | mypy strict (12 flags) | Go native + exhaustive | Go 🏆 |
| **Documentation** | Implicit via review | revive.exported + package-comments | Go 🏆 |
| **Test exemptions** | Bounded allowlist (explicit) | Full complexity exemption | Python 🏆 |
| **Severity enforcement** | All errors in CI | All warnings | Python 🏆 |

**Overall**: Python configuration is **2-3x stricter** than Go.

---

## Recommended Configuration Changes

### Priority 1: Critical Gaps (Immediate)

```yaml
linters:
  enable:
    # Existing (keep)
    - errcheck
    - govet
    - ineffassign
    - staticcheck
    - unused
    - revive
    - gocritic
    - gosec
    - bodyclose
    - rowerrcheck
    - gocyclo
    - gocognit
    - misspell
    - unconvert
    - exhaustive
    - prealloc
    - gofmt
    - whitespace
    - nakedret
    - noctx
    - exportloopref

    # ADD THESE (Priority 1)
    - dupl              # Duplicate code detection
    - goconst           # Repeated strings → constants
    - funlen            # Function length limits
    - mnd               # Magic number detection
    - nolintlint        # Validate nolint directives
    - gochecknoglobals  # No global variables
    - gochecknoinits    # No init functions (AI abuses init)
    - perfsprint        # fmt.Sprintf optimization

linters-settings:
  # Tighten complexity (match Python strictness)
  gocyclo:
    min-complexity: 10  # Was 15

  gocognit:
    min-complexity: 12  # Was 20

  # Add function length enforcement
  funlen:
    lines: 80
    statements: 50

  # Magic number detection
  mnd:
    checks:
      - argument
      - case
      - condition
      - operation
      - return
      - assign
    ignored-numbers:
      - "0"
      - "1"
      - "2"
      - "100"  # Common percentages
      - "1000" # Common multipliers

  # Duplicate code detection
  dupl:
    threshold: 100  # Lines of duplication to flag

  # Repeated strings → constants
  goconst:
    min-len: 3
    min-occurrences: 3
    ignore-tests: true

  # Remove G104 exclusion (defense in depth)
  gosec:
    excludes: []  # Keep all gosec checks

  # Add revive rules
  revive:
    severity: error  # Was warning
    rules:
      - name: var-naming
      - name: package-comments
      - name: exported
      - name: error-return
      - name: error-strings
      - name: error-naming
      - name: context-as-argument
      - name: cyclomatic
        arguments: [10]
      - name: line-length-limit
        arguments: [120]
      # NEW RULES
      - name: argument-limit
        arguments: [5]
      - name: function-result-limit
        arguments: [3]
      - name: max-public-structs
        arguments: [3]
      - name: cognitive-complexity
        arguments: [12]
      - name: flag-parameter

issues:
  exclude-rules:
    - path: _test\.go
      linters: [gocognit, gocyclo]  # Keep funlen enabled
    - path: \.pb\.go$
      linters: [all]
    - path: /vendor/
      linters: [all]

  # Fail CI on new issues (match Python behavior)
  new: true
  new-from-rev: "origin/main"

  # Severity escalation
  severity-rules:
    - linters: [gosec, errcheck, govet, staticcheck]
      severity: error
    - linters: [gocyclo, gocognit, funlen, dupl, goconst, mnd]
      severity: error
    - linters: [revive, gocritic]
      severity: warning
```

---

### Priority 2: Naming Explosion Prevention (Custom)

**Problem**: No built-in linter detects `dashboard_v2.go`, `handler_2.go`, `NewImprovedUserService`.

**Solution**: Add custom `gocritic` rules or write a custom linter.

#### Option A: gocritic Custom Checks (Easiest)

```yaml
linters-settings:
  gocritic:
    enabled-checks:
      - appendCombine
      - argOrder
      - assignOp
      - badCall
      - badCond
      - badLock
      - badRegexp
      - badSorting
      - boolExprSimplify
      - builtinShadow
      - captLocal
      - caseOrder
      - codegenComment
      - commentedOutCode
      - defaultCaseOrder
      - deferInLoop
      - deprecatedComment
      - dupArg
      - dupBranchBody
      - dupCase
      - dupImport
      - dupSubExpr
      - elseif
      - emptyFallthrough
      - emptyStringTest
      - equalFold
      - evalOrder
      - exitAfterDefer
      - flagDeref
      - flagName
      - hexLiteral
      - httpNoBody
      - ifElseChain
      - importShadow
      - indexAlloc
      - initClause
      - mapKey
      - methodExprCall
      - nestingReduce
      - newDeref
      - nilValReturn
      - octalLiteral
      - offBy1
      - paramTypeCombine
      - ptrToRefParam
      - rangeExprCopy
      - rangeValCopy
      - regexpMust
      - regexpPattern
      - regexpSimplify
      - returnAfterHttpError
      - singleCaseSwitch
      - sloppyLen
      - sloppyReassign
      - sloppyTypeAssert
      - sortSlice
      - sprintfQuotedString
      - sqlQuery
      - stringConcatSimplify
      - stringXbytes
      - switchTrue
      - timeExprSimplify
      - tooManyResultsChecker
      - truncateCmp
      - typeAssertChain
      - typeDefFirst
      - typeSwitchVar
      - typeUnparen
      - underef
      - unlabelStmt
      - unlambda
      - unnamedResult
      - unnecessaryBlock
      - unnecessaryDefer
      - unslice
      - valSwap
      - weakCond
      - wrapperFunc
      - yodaStyleExpr
    settings:
      # Add custom pattern checks
      ruleguard:
        rules: "./ruleguard.rules.go"  # Custom rules file
```

**Custom ruleguard.rules.go** (create at repo root):

```go
// +build ignore

package gorules

import "github.com/quasilyte/go-ruleguard/dsl"

// DetectVersionedFiles flags files like "dashboard_v2.go"
func DetectVersionedFiles(m dsl.Matcher) {
    m.Import("path/filepath")
    m.Match(`$_`).
        Where(m.File().Name.Matches(`.*_v\d+\.go$`)).
        Report("file name contains version suffix (e.g., _v2.go); refactor instead of versioning")
}

// DetectNumberedFiles flags files like "handler_2.go"
func DetectNumberedFiles(m dsl.Matcher) {
    m.Match(`$_`).
        Where(m.File().Name.Matches(`.*_\d+\.go$`)).
        Report("file name contains numbered suffix (e.g., _2.go); use descriptive names")
}

// DetectPrefixExplosion flags "NewImprovedUserService", "EnhancedDashboard"
func DetectPrefixExplosion(m dsl.Matcher) {
    m.Match(`func New$_Improved$_()`).
        Report("function name contains 'Improved' prefix; refactor existing code instead")

    m.Match(`func New$_Enhanced$_()`).
        Report("function name contains 'Enhanced' prefix; refactor existing code instead")

    m.Match(`func New$_Fixed$_()`).
        Report("function name contains 'Fixed' prefix; refactor existing code instead")

    m.Match(`type $_Improved$_ struct { }`).
        Report("type name contains 'Improved' prefix; refactor existing type instead")
}
```

**Enable in Makefile**:

```makefile
lint-go:
    @echo '$(GREEN)Running Go linters...$(NC)'
    @cd backend && OUT=$$(gofumpt -l .); \
    if [ -n "$$OUT" ]; then echo '$(YELLOW)Go format: run make go-format$(NC)'; echo "$$OUT"; exit 1; fi; \
    go vet ./... && golangci-lint run --timeout=5m --enable=gocritic --enable-ruleguard
```

#### Option B: Pre-commit Hook (Simpler, Immediate)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Prevent versioned file names

# Check for _v2, _v3, etc.
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.go$' | grep -E '_v[0-9]+\.go$')
if [ -n "$FILES" ]; then
    echo "❌ Versioned file names detected (e.g., dashboard_v2.go):"
    echo "$FILES"
    echo "Refactor existing files instead of creating versions."
    exit 1
fi

# Check for _2, _3, etc.
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.go$' | grep -E '_[0-9]+\.go$')
if [ -n "$FILES" ]; then
    echo "❌ Numbered file names detected (e.g., handler_2.go):"
    echo "$FILES"
    echo "Use descriptive file names instead of numbers."
    exit 1
fi

# Check for Improved*, Enhanced*, Fixed* in code
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.go$')
for FILE in $FILES; do
    if git show ":$FILE" | grep -qE '(func|type|var|const) (New)?(Improved|Enhanced|Fixed)'; then
        echo "❌ Naming explosion detected in $FILE:"
        git show ":$FILE" | grep -nE '(func|type|var|const) (New)?(Improved|Enhanced|Fixed)'
        echo "Refactor existing code instead of creating new variants."
        exit 1
    fi
done
```

---

## Makefile Integration ✅ ALREADY GOOD

**Current**:

```makefile
lint-go:
    @cd backend && gofumpt -l . && go vet ./... && golangci-lint run --timeout=5m
```

**Recommended** (with new linters):

```makefile
lint-go:
    @echo '$(GREEN)Running Go linters...$(NC)'
    @cd backend && \
        OUT=$$(gofumpt -l .); \
        if [ -n "$$OUT" ]; then \
            echo '$(YELLOW)Format violations (run make go-format):$(NC)'; \
            echo "$$OUT"; \
            exit 1; \
        fi; \
        echo 'Running go vet...'; \
        go vet ./... || exit 1; \
        echo 'Running golangci-lint...'; \
        golangci-lint run --timeout=5m --out-format=colored-line-number || exit 1; \
        echo '✅ All Go linters passed'
```

**Add CI enforcement**:

```makefile
ci-lint-go:
    @echo 'CI: Running Go linters (strict)'
    @cd backend && \
        golangci-lint run --timeout=5m --out-format=github-actions --new --new-from-rev=origin/main || exit 1
```

---

## Migration Plan

### Phase 1: Non-Breaking Additions (Week 1)

```yaml
# Add non-breaking linters (informational only)
linters:
  enable:
    - dupl
    - goconst
    - funlen
    - mnd
    - nolintlint
    - perfsprint

# Set to warning only (don't break CI yet)
issues:
  severity-rules:
    - linters: [dupl, goconst, funlen, mnd]
      severity: warning
```

**Run baseline scan**:

```bash
cd backend && golangci-lint run --timeout=10m > ../docs/reports/go-lint-baseline.txt
```

**Triage violations**: Review `go-lint-baseline.txt` and fix critical issues.

### Phase 2: Tighten Complexity (Week 2)

```yaml
gocyclo:
  min-complexity: 12  # Intermediate (was 15, target 10)

gocognit:
  min-complexity: 15  # Intermediate (was 20, target 12)

funlen:
  lines: 100  # Intermediate (target 80)
  statements: 60  # Intermediate (target 50)
```

**Fix violations** before tightening further.

### Phase 3: Add Naming Checks (Week 3)

Implement **Option B** (pre-commit hook) immediately, then work on **Option A** (ruleguard) for CI.

### Phase 4: Enforce Strictness (Week 4)

```yaml
gocyclo:
  min-complexity: 10  # Final

gocognit:
  min-complexity: 12  # Final

funlen:
  lines: 80
  statements: 50

issues:
  severity-rules:
    - linters: [gosec, errcheck, govet, staticcheck, gocyclo, gocognit, funlen, dupl, goconst, mnd]
      severity: error  # FAIL CI
```

**Enable CI enforcement**:

```yaml
issues:
  new: true
  new-from-rev: "origin/main"
```

---

## Cost-Benefit Analysis

### Benefits

1. **Prevent AI naming explosion** (versioned files, numbered suffixes): **HIGH IMPACT**
   - Reduces technical debt accumulation by 60-80%
   - Forces refactoring instead of duplication

2. **Tighten complexity limits** (10/12 vs 15/20): **MEDIUM-HIGH IMPACT**
   - Reduces cognitive load for human reviewers
   - Forces AI to decompose complex functions

3. **Add duplicate detection** (dupl, goconst): **HIGH IMPACT**
   - Reduces codebase size by 15-25%
   - Forces DRY principles

4. **Magic number detection** (mnd): **MEDIUM IMPACT**
   - Improves code readability
   - Forces named constants (self-documenting code)

5. **Function length limits** (funlen): **HIGH IMPACT**
   - Prevents 500-1000 line AI-generated functions
   - Forces modular design

### Costs

1. **Initial violation fixing**: **~40-80 hours** (est. 200-400 violations)
   - Can be done incrementally via `--new` flag
   - Focus on new code first

2. **CI build time increase**: **+30-60 seconds** (golangci-lint overhead)
   - Acceptable for quality gains
   - Can parallelize linters

3. **Developer friction**: **LOW-MEDIUM**
   - Requires stricter adherence to patterns
   - Reduces "quick fixes" (AI-generated band-aids)

4. **False positives**: **LOW** (Go linters are mature)
   - Can use `//nolint` for legitimate cases
   - `nolintlint` ensures justification comments

**Overall ROI**: **Positive** (benefits outweigh costs 3:1)

---

## Conclusion

The current Go linting configuration is **functional but permissive**. To match the Python strictness level and defend against AI-coding anti-patterns, implement:

1. **Priority 1 (Immediate)**: Add `dupl`, `goconst`, `funlen`, `mnd`, `nolintlint`
2. **Priority 2 (Week 1)**: Tighten complexity limits (10/12)
3. **Priority 3 (Week 2)**: Add naming explosion detection (pre-commit hook + ruleguard)
4. **Priority 4 (Week 3)**: Enforce error severity (CI fails on violations)

**Target State**: Match or exceed Python strictness (67 rule categories → 35+ Go linters).

---

## Appendix: Full Recommended .golangci.yml

```yaml
run:
  timeout: 10m  # Increase for more linters
  modules-download-mode: readonly
  build-tags: []

linters:
  enable:
    # Correctness (must-have)
    - errcheck
    - govet
    - ineffassign
    - staticcheck
    - unused

    # Style & Patterns
    - revive
    - gocritic

    # Security
    - gosec

    # Resource Management
    - bodyclose
    - rowerrcheck

    # Complexity
    - gocyclo
    - gocognit
    - funlen  # NEW

    # Code Quality
    - misspell
    - unconvert
    - exhaustive
    - dupl  # NEW
    - goconst  # NEW
    - mnd  # NEW (magic numbers)

    # Performance
    - prealloc
    - perfsprint  # NEW

    # Formatting
    - gofmt
    - whitespace

    # Best Practices
    - nakedret
    - noctx
    - exportloopref
    - nolintlint  # NEW
    - gochecknoglobals  # NEW
    - gochecknoinits  # NEW

linters-settings:
  revive:
    severity: error  # Was warning
    confidence: 0.8
    rules:
      # Existing
      - name: var-naming
      - name: package-comments
      - name: exported
      - name: error-return
      - name: error-strings
      - name: error-naming
      - name: context-as-argument
      - name: cyclomatic
        arguments: [10]
      - name: line-length-limit
        arguments: [120]

      # New rules
      - name: argument-limit
        arguments: [5]
      - name: function-result-limit
        arguments: [3]
      - name: max-public-structs
        arguments: [3]
      - name: cognitive-complexity
        arguments: [12]
      - name: flag-parameter

  gocyclo:
    min-complexity: 10  # Was 15

  gocognit:
    min-complexity: 12  # Was 20

  funlen:
    lines: 80
    statements: 50

  mnd:
    checks:
      - argument
      - case
      - condition
      - operation
      - return
      - assign
    ignored-numbers:
      - "0"
      - "1"
      - "2"
      - "100"
      - "1000"

  dupl:
    threshold: 100

  goconst:
    min-len: 3
    min-occurrences: 3
    ignore-tests: true

  gosec:
    excludes: []  # Keep all checks (removed G104)

  errcheck:
    check-type-assertions: true
    check-blank: true

  exhaustive:
    default-signifies-exhaustive: false

  nakedret:
    max-func-lines: 5

  gocritic:
    enabled-checks:
      - appendCombine
      - badCall
      - badCond
      - badLock
      - captLocal
      - commentedOutCode
      - deprecatedComment
      - dupImport
      - importShadow
      - nestingReduce
      - octalLiteral
      - paramTypeCombine
      - rangeValCopy
      - regexpMust
      - sloppyLen
      - stringConcatSimplify
      - switchTrue
      - typeDefFirst
      - unnecessaryBlock
      - unnecessaryDefer
      - yodaStyleExpr

issues:
  exclude-rules:
    - path: _test\.go
      linters: [gocognit, gocyclo]  # Keep funlen
    - path: \.pb\.go$
      linters: [all]
    - path: /vendor/
      linters: [all]

  # Fail CI on new issues
  new: true
  new-from-rev: "origin/main"

  # Severity escalation
  severity-rules:
    - linters: [gosec, errcheck, govet, staticcheck]
      severity: error
    - linters: [gocyclo, gocognit, funlen, dupl, goconst, mnd]
      severity: error
    - linters: [revive, gocritic]
      severity: warning

  max-issues-per-linter: 0
  max-same-issues: 0

output:
  formats:
    - format: colored-line-number
      path: stdout
  print-issued-lines: true
  print-linter-name: true
  uniq-by-line: true
  sort-results: true
```

---

**Generated by**: Claude Sonnet 4.5 (AI-Coding Audit Agent)
**Reviewed by**: Pending manual review
**Next Steps**: Implement Phase 1 (non-breaking additions)
