# CI Coverage Regression Detection

**Production-grade coverage regression detection** with automatic baseline tracking and PR reporting.

---

## Overview

The `coverage-regression.yml` workflow runs on every pull request and:

1. **Extracts coverage** for all three languages (Go, Python, TypeScript) from their native tools
2. **Compares against baseline** from the main branch
3. **Fails PR** if any project drops >2% coverage
4. **Posts detailed PR comment** with regression/improvement summary
5. **Updates baseline** when merging to main

### Key Features

- **Multi-language support**: Go (native), Python (coverage.py), TypeScript (vitest)
- **Granular reporting**: Per-package analysis with diff tables
- **Automatic baselines**: Stored as GitHub artifacts, updated on main branch pushes
- **PR comments**: Detailed tables with before/after comparisons
- **Configurable threshold**: 2% default, easily adjustable
- **No external services**: Uses native coverage tools + GitHub Actions only

---

## Workflow Triggers

```yaml
on:
  pull_request:
    branches: [ main, develop ]
    types: [ opened, synchronize, reopened ]
```

Runs on:
- PR creation
- New commits pushed to PR
- PR reopened after close

**Does NOT run on:** push to main (uses artifacts instead)

---

## Coverage Extraction

### Go Coverage

```bash
go test -v -race -coverprofile=coverage.out -covermode=atomic ./...
go tool cover -func=coverage.out
```

**Output format:** `package|percentage`

Example:
```
github.com/trace/internal/handlers|87.50
github.com/trace/internal/services|91.23
TOTAL|88.92
```

**Threshold:** Enforced per workflow (see **Enforcement** section)

---

### Python Coverage

```bash
pytest src/ tests/ --cov=src --cov-report=xml --cov-report=term
```

**Tool:** `coverage.py` (via pytest plugin)

**Output format:** XML parsed to `package|percentage`

Example:
```
src.tracertm.api|92.15
src.tracertm.services|88.50
TOTAL|90.45
```

**Threshold:** Hard-enforced in pytest config (see **Enforcement** section)

---

### TypeScript Coverage

```bash
bun run test -- --run --coverage
```

**Tool:** vitest with Istanbul coverage

**Output format:** Per-directory aggregation `directory|percentage`

Example:
```
components|85.30
hooks|88.75
utils|91.20
TOTAL|87.80
```

**Threshold:** Enforced in vitest config (see **Enforcement** section)

---

## Baseline Management

### Artifact Storage

Baselines are stored as GitHub workflow artifacts with 90-day retention:

| Language | Artifact Name | Path | Updated |
|----------|---------------|------|---------|
| **Go** | `go-coverage-baseline` | `backend/coverage-by-package.txt` | On main merge |
| **Python** | `python-coverage-baseline` | `python-coverage-by-package.txt` | On main merge |
| **TypeScript** | `typescript-coverage-baseline` | `frontend/frontend-coverage-by-package.txt` | On main merge |

### First Run (No Baseline)

On the first PR after deploying the workflow:
- Baseline is not found (fresh install)
- Workflow **continues without comparison** (no baseline = no regression)
- Comment posted: "ℹ No baseline found (first run on main branch)"
- Baseline is **created and stored** when PR merges to main

### Updating Baseline

When a PR merges to main:
1. Coverage is re-extracted for all three languages
2. Latest artifact with name `*-baseline` is **overwritten** with new coverage data
3. All subsequent PRs compare against this new baseline

**Manual baseline reset:**
```bash
# Delete old baseline artifacts in GitHub Actions
# New baseline will be created on next main merge
```

---

## Regression Detection

### Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Regression** | > 2% drop | ❌ PR fails |
| **Improvement** | > 0.5% gain | ✅ Highlighted in comment (top 5 only) |

**Rationale:**
- **2% threshold** balances safety (catch meaningful regressions) vs. noise (ignore minor fluctuations from test refactors)
- **0.5% improvement threshold** highlights progress without overwhelming comments

### Example: Detecting Regression

**Before (baseline):**
```
internal/handlers|87.50%
internal/services|91.23%
```

**After (PR):**
```
internal/handlers|85.30%  <- 2.20% DROP (fails, >2%)
internal/services|91.50%  <- 0.27% improvement (shown in comment)
```

**Result:** ❌ PR fails (handlers regression > 2% threshold)

---

## PR Comments

### Comment Format

Automatically posted to every PR with coverage changes:

#### Regressions Table

```markdown
### ❌ Regressions Detected (2)

| Language | Package | Before | After | Change |
|----------|---------|--------|-------|--------|
| Go | `internal/handlers` | 87.50% | 85.30% | -2.20% |
| Python | `src.api.routes` | 92.15% | 89.80% | -2.35% |

⚠️ **Action Required:** Coverage has regressed. Please add or fix tests to restore coverage.
```

#### Improvements Table

```markdown
### ✅ Improvements (3)

| Language | Package | Before | After | Change |
|----------|---------|--------|-------|--------|
| TypeScript | `components` | 85.30% | 88.75% | +3.45% |
| Go | `internal/services` | 91.23% | 91.50% | +0.27% |

(Shows top 5 improvements)
```

#### Success Case

```markdown
## 📊 Coverage Regression Report

✅ **No coverage regressions detected**

---
*Threshold: Changes >2% from baseline trigger failure*
```

### Comment Updates

- On **first push** to PR: Comment is **created**
- On **subsequent pushes**: Comment is **updated** (no duplicates)

---

## Integration with Main CI

### Relationship to `ci.yml`

**Separate workflows** with complementary roles:

| Aspect | `coverage-regression.yml` | `ci.yml` |
|--------|--------------------------|---------|
| **Trigger** | PR only (opened, sync'd) | PR + push + release |
| **Focus** | Regression detection vs. baseline | Absolute thresholds |
| **Baselines** | Tracked per commit on main | Not tracked |
| **PR comment** | Yes, detailed table | Job step summary only |
| **Enforcement** | Fails PR if >2% regression | Hard thresholds (90% Go, 90% Py, 90% TS) |

**Both must pass:** PR requires both workflows to succeed.

### Data Flow

```
PR opened
  ↓
coverage-regression.yml runs:
  1. Extract coverage (Go/Python/TypeScript)
  2. Download baseline from main
  3. Compare & report
  4. Post PR comment
  ↓
ci.yml runs (parallel):
  1. Extract coverage
  2. Enforce hard thresholds (must be ≥90%)
  3. Upload to Codecov
  ↓
Both pass? → PR mergeable
```

---

## Enforcement

### Hard Thresholds (Blocking)

These are **enforced separately** in each language's test config and **must be met** regardless of baseline:

| Language | Tool | Threshold | Config | Blocks |
|----------|------|-----------|--------|--------|
| **Go** | `go test` + `golangci-lint` | Tracked (no fail) | ci.yml | No (tracking only) |
| **Python** | pytest `--cov-fail-under` | 90% | pyproject.toml | Yes |
| **TypeScript** | vitest thresholds | 90% | vitest.config.ts | Yes |

### Regression Thresholds (Relative)

**Enforced by coverage-regression.yml:**

- **Threshold:** 2% from baseline
- **Action:** Fails PR if exceeded
- **Message:** "Coverage regression detected. See PR comment for details."

### Combined Enforcement Example

```
Python code changes:
  - Hard threshold: Must be ≥90% (enforced in pytest)
  - Regression threshold: >2% from baseline

Example:
  Baseline: 92%
  PR coverage: 88%

  Evaluation:
  ✅ Meets hard threshold? (88% ≥ 90%) → NO, pytest fails
  ❌ Regression check: (92% - 88% = 4% > 2%) → FAILS

  Result: PR blocked (two reasons)
```

---

## Configuration

### Adjusting Thresholds

**Regression threshold** (2% default):

In `coverage-regression.yml`, line ~280:
```python
REGRESSION_THRESHOLD = 2.0  # Percentage points
```

Change to (e.g., 1.5% for stricter):
```python
REGRESSION_THRESHOLD = 1.5
```

**Hard thresholds** (90% default):

Python (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
addopts = "--cov-fail-under=90"
```

TypeScript (`frontend/apps/web/vitest.config.ts`):
```javascript
coverage: {
  lines: 90,
  functions: 90,
  branches: 90,
  statements: 90
}
```

---

## Troubleshooting

### Baseline Not Found

**Error:** "ℹ No baseline found (first run on main branch)"

**Cause:** Workflow just deployed, no baseline exists yet

**Fix:**
1. Merge the PR that added this workflow to main
2. Workflow runs on main, creates first baseline artifact
3. Next PR will compare against this baseline

### PR Fails: Regression Detected

**Error:** "Coverage regression detected. Some packages have lower coverage than baseline."

**Causes:**
1. New code without tests
2. Test changes that removed coverage
3. Refactor that exposed untested code

**Fix:**
1. Check PR comment for affected packages
2. Add tests for new code
3. Review test changes for completeness
4. Run locally: `go test ./... -cover`, `pytest --cov`, `bun test -- --coverage`

### Missing Baseline Artifacts

**Error:** Workflow runs but can't download baseline

**Cause:** Artifacts expired (>90 days) or never created

**Fix:**
1. Manually run `coverage-regression.yml` on main:
   ```bash
   # Via GitHub Actions UI: workflow_dispatch
   ```
2. Or merge a PR to main to auto-create baseline

### Coverage Extraction Failed

**Error:** "coverage-by-file.txt not found" or similar

**Cause:** Test failed before coverage generation

**Fix:**
1. Check workflow logs for test failures
2. Fix test errors first
3. Coverage extraction happens **after** tests pass

---

## Performance

### Execution Time

Typical run times on ubuntu-latest:

| Phase | Duration | Notes |
|-------|----------|-------|
| Checkout & setup | 30s | Cached dependencies |
| Go tests + coverage | 45s | `-race`, `-short` included |
| Python tests + coverage | 60s | Full pytest suite |
| TypeScript tests + coverage | 90s | All frontend apps |
| Baseline download | 10s | Artifact download |
| Coverage comparison | 5s | Python script |
| **Total** | ~240s (4 min) | Sequential, can parallelize |

### Optimization Tips

**Parallel test execution:**
- Go: Already parallelized with `-race`
- Python: Add `-n auto` flag to pytest (pytest-xdist)
- TypeScript: Already parallelized (bun default)

**Skip on non-test changes:**

Add path filters to workflow trigger:
```yaml
on:
  pull_request:
    paths:
      - 'src/**'
      - 'backend/**'
      - 'frontend/**'
      - '.github/workflows/coverage-regression.yml'
```

---

## Examples

### Example 1: Small Improvement

PR improves TypeScript component tests:

```markdown
## 📊 Coverage Regression Report

✅ **No coverage regressions detected**

### ✅ Improvements (1)

| Language | Package | Before | After | Change |
|----------|---------|--------|-------|--------|
| TypeScript | `components` | 85.30% | 87.25% | +1.95% |

---
*Threshold: Changes >2% from baseline trigger failure*
```

**Status:** ✅ Passes (improvement only)

---

### Example 2: Regression Caught

PR adds feature without tests:

```markdown
## 📊 Coverage Regression Report

### ❌ Regressions Detected (1)

| Language | Package | Before | After | Change |
|----------|---------|--------|-------|--------|
| Go | `internal/handlers` | 87.50% | 84.80% | -2.70% |

⚠️ **Action Required:** Coverage has regressed. Please add or fix tests to restore coverage.

---
*Threshold: Changes >2% from baseline trigger failure*
```

**Status:** ❌ Fails (regression > 2%)

---

### Example 3: Mixed Outcome

PR improves one package, regresses another:

```markdown
## 📊 Coverage Regression Report

### ❌ Regressions Detected (1)

| Language | Package | Before | After | Change |
|----------|---------|--------|-------|--------|
| Python | `src.api.routes` | 92.15% | 89.50% | -2.65% |

⚠️ **Action Required:** Coverage has regressed. Please add or fix tests to restore coverage.

### ✅ Improvements (1)

| Language | Package | Before | After | Change |
|----------|---------|--------|-------|--------|
| Python | `src.services.auth` | 88.30% | 90.10% | +1.80% |

---
*Threshold: Changes >2% from baseline trigger failure*
```

**Status:** ❌ Fails (regression in one package overrides improvements in another)

---

## Best Practices

### 1. Fix Regressions Immediately

If PR shows regression:
1. Run tests locally with coverage
2. Identify uncovered lines
3. Add tests for new code before fixing
4. Commit and re-push

### 2. Monitor Baseline Drift

Check baseline every release:
```bash
# Via GitHub Actions: Artifacts tab → {language}-coverage-baseline
# Expected: Stable or improving over time
```

If baseline consistently drops:
- Code quality decreasing
- Tests becoming less effective
- Consider stricter thresholds

### 3. Use as Promotion Gate

**Coverage regression = quality gate:**
- Block PRs with regressions
- Require tests for new code
- Celebrate improvements in PR comments

### 4. Review Bulk Changes

For refactors/migrations affecting coverage:
- Plan coverage adjustments
- Add tests alongside refactoring
- Avoid regression during code moves

---

## Integration Examples

### With Branch Protection Rules

GitHub Settings → Branches → main → Require status checks:

```
✅ coverage-regression.yml / coverage-regression
✅ ci.yml / python-tests
✅ ci.yml / go-tests
✅ ci.yml / frontend-checks
```

### With CI Badge

Add to README.md:

```markdown
![Coverage Regression](https://github.com/{org}/{repo}/actions/workflows/coverage-regression.yml/badge.svg)
```

### With External Tools

**Codecov integration** (in `ci.yml`):
```yaml
- uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

**Datadog/other APM:**
```yaml
- name: Report coverage to Datadog
  run: |
    curl -X POST https://api.datadoghq.com/api/v2/metrics \
      -H "DD-API-KEY: ${{ secrets.DD_API_KEY }}" \
      -d '{"series": [{"metric": "coverage.go", "points": [...]}]}'
```

---

## FAQ

### Q: Why separate coverage-regression.yml from ci.yml?

**A:**
- **Modularity:** Each workflow has clear responsibility
- **Performance:** Can run in parallel
- **Reusability:** coverage-regression can be copied to other repos
- **Clarity:** PR comment focused on regressions only

### Q: What if I want different thresholds per language?

**A:** Edit the comparison function in `coverage-regression.yml`:

```python
# Line ~280, adjust per-language thresholds:
GO_THRESHOLD = 2.0
PYTHON_THRESHOLD = 1.5  # Stricter for Python
TYPESCRIPT_THRESHOLD = 2.5  # Looser for TS
```

### Q: How do I know what the baseline is?

**A:** Check GitHub Actions artifacts:
1. Go to Actions → coverage-regression
2. Any successful run on main → Artifacts section
3. Download `{language}-coverage-baseline`

### Q: Can I manually update the baseline?

**A:** Yes, via GitHub Actions artifacts API:

```bash
# Delete old baseline
gh api repos/{owner}/{repo}/actions/artifacts \
  --jq '.artifacts[] | select(.name | contains("baseline"))' \
  -F per_page=100

# Force new baseline by re-running workflow on main
gh workflow run coverage-regression.yml --ref main
```

### Q: Why does the first PR fail with "No baseline"?

**A:** Workflow is installed but no baseline exists yet.
- First PR compares against (nothing) → skip comparison
- First PR merges to main → baseline created
- Second PR compares against baseline → regressions detected

### Q: Can I disable regression checking for a single PR?

**A:** Add label to PR (requires custom logic):

```yaml
if: '!contains(github.event.pull_request.labels.*.name, "skip-coverage-check")'
```

Or temporarily increase threshold in code:
```python
if github.event.pull_request.draft:
    REGRESSION_THRESHOLD = 10.0  # Skip for drafts
```

---

## See Also

- **CI Gates Reference:** `/docs/reference/CI_GATES_QUICK_REFERENCE.md`
- **Main CI Workflow:** `.github/workflows/ci.yml`
- **Coverage Tools:**
  - [Go coverage docs](https://pkg.go.dev/cmd/cover)
  - [coverage.py documentation](https://coverage.readthedocs.io/)
  - [vitest coverage guide](https://vitest.dev/guide/coverage.html)
