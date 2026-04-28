# Coverage Baseline CI Integration Guide

**Purpose:** Auto-update the coverage baseline document and detect regressions on every commit.

**Status:** Ready to integrate into `.github/workflows/ci.yml`

---

## Overview

The coverage baseline system provides:
1. **Auto-generated matrix** of coverage metrics across Go, Python, and TypeScript
2. **Regression detection** that blocks PRs with coverage drops > 0.1%
3. **Trend tracking** for measuring coverage velocity
4. **Machine-readable artifacts** for programmatic analysis

---

## Components

### 1. Baseline Document
**File:** `docs/reports/COVERAGE_BASELINE.md`

Auto-generated from CI artifacts. Contains:
- Current coverage metrics (by language, module, test type)
- Regression comparison vs previous baseline
- Coverage goals and gaps
- CI/CD configuration reference

**Maintained by:** GitHub Actions workflow (on main merge)
**Format:** Markdown with structured tables

### 2. Metrics Extraction Script
**File:** `scripts/extract_coverage_metrics.py`

Parses coverage artifacts and produces JSON:
- Per-module coverage breakdown
- Language-level aggregates
- Regression detection report
- Trend data for metrics

**Usage:**
```bash
# Extract from CI artifacts
python scripts/extract_coverage_metrics.py \
  --ci-artifacts-dir /artifacts/ \
  --output coverage-metrics.json

# Compare with baseline
python scripts/extract_coverage_metrics.py \
  --ci-artifacts-dir /artifacts/ \
  --compare coverage-baseline.json \
  --output regression-report.json
```

### 3. Baseline Update Script
**File:** `scripts/update-coverage-baseline.sh`

Updates the baseline document with latest metrics.

**Usage:**
```bash
bash scripts/update-coverage-baseline.sh
```

---

## Integration into GitHub Actions

### Step 1: Add Post-Test Coverage Extraction

Add this to `.github/workflows/ci.yml` after the language-specific test jobs:

```yaml
  # After python-tests, go-tests, and frontend-checks jobs complete
  aggregate-coverage-metrics:
    name: Aggregate Coverage Metrics
    runs-on: ubuntu-latest
    needs: [python-tests, go-tests, frontend-checks]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Download all coverage artifacts
        uses: actions/download-artifact@v4
        with:
          path: /artifacts/

      - name: Extract coverage metrics
        run: |
          python scripts/extract_coverage_metrics.py \
            --ci-artifacts-dir /artifacts/ \
            --output coverage-metrics.json \
            --format json

      - name: Upload coverage metrics
        uses: actions/upload-artifact@v4
        with:
          name: coverage-metrics
          path: coverage-metrics.json
          retention-days: 90
```

### Step 2: Add Regression Detection Job

Add regression detection for pull requests:

```yaml
  coverage-regression-check:
    name: Coverage Regression Detection
    runs-on: ubuntu-latest
    needs: [aggregate-coverage-metrics]
    if: github.event_name == 'pull_request'
    continue-on-error: false  # Fail on regression

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Download current metrics
        uses: actions/download-artifact@v4
        with:
          name: coverage-metrics
          path: /current/

      - name: Download baseline (from main)
        uses: actions/download-artifact@v4
        with:
          name: coverage-metrics
          path: /baseline/
        continue-on-error: true  # Baseline may not exist yet

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Run regression detection
        run: |
          python scripts/extract_coverage_metrics.py \
            --compare /baseline/coverage-metrics.json \
            --ci-artifacts-dir /current/ \
            --output regression-report.json \
            --format markdown \
            --threshold 0.1

          # Check if regressions were detected
          if grep -q "Regressions Detected" regression-report.json; then
            echo "## ❌ Coverage Regression Detected" >> $GITHUB_STEP_SUMMARY
            cat regression-report.json >> $GITHUB_STEP_SUMMARY
            exit 1
          else
            echo "## ✅ No Coverage Regressions" >> $GITHUB_STEP_SUMMARY
          fi

      - name: Comment PR with regression report
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('regression-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

### Step 3: Add Baseline Update Job (Main Branch Only)

Add baseline update on successful main branch merge:

```yaml
  update-coverage-baseline:
    name: Update Coverage Baseline
    runs-on: ubuntu-latest
    needs: [coverage-regression-check]
    if: github.ref == 'refs/heads/main' && success()

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Download coverage metrics
        uses: actions/download-artifact@v4
        with:
          name: coverage-metrics
          path: /metrics/

      - name: Extract baseline files
        run: |
          # Convert metrics JSON to pipe-delimited files
          python scripts/extract_coverage_metrics.py \
            --ci-artifacts-dir /metrics/ \
            --output coverage-metrics.json

          # Generate baseline files from artifacts
          python << 'EOF'
          import json

          with open('coverage-metrics.json') as f:
              data = json.load(f)

          # Extract per-language baselines
          for lang, metrics in data.get('metrics', {}).items():
              filename = f"{lang}-coverage-by-file.txt"
              with open(filename, 'w') as f:
                  for module, cov in metrics.items():
                      if not module.startswith('__'):
                          f.write(f"{module}|{cov}\n")
          EOF

      - name: Update baseline document
        run: bash scripts/update-coverage-baseline.sh

      - name: Commit and push updated baseline
        run: |
          git config user.name "GitHub Actions"
          git.config user.email "actions@github.com"

          git add docs/reports/COVERAGE_BASELINE.md
          git commit -m "docs: Auto-update coverage baseline" || true
          git push origin main
```

---

## Configuration in pyproject.toml

No additional configuration needed. Existing coverage tools are sufficient:

```toml
[tool.coverage.report]
fail_under = 90
precision = 2
show_missing = true
```

---

## Running Locally

### Extract Metrics from Local Test Run

```bash
# After running tests with coverage
python scripts/extract_coverage_metrics.py \
  --go backend/coverage.out \
  --python coverage.xml \
  --frontend frontend/apps/web/coverage-final.json \
  --output my-coverage.json \
  --verbose
```

### Compare with Baseline

```bash
# Get latest baseline from GitHub Actions
gh run download -n coverage-metrics-baseline

# Compare
python scripts/extract_coverage_metrics.py \
  --compare coverage-metrics-baseline.json \
  --ci-artifacts-dir . \
  --output regression-report.json \
  --format markdown
```

---

## Troubleshooting

### Issue: "No coverage artifacts found"

**Cause:** Test jobs didn't complete successfully or artifacts weren't uploaded.

**Solution:**
1. Check test job logs for failures
2. Verify artifact upload steps in workflow
3. Ensure artifact names match: `{language}-coverage-baseline`

### Issue: "Regression detected but it's a false positive"

**Cause:** Coverage fluctuates naturally; threshold may be too strict.

**Solution:**
1. Review the actual changes—did coverage really drop?
2. Check if tests were properly mocked/isolated
3. Consider increasing threshold temporarily: `--threshold 0.5`

### Issue: "Baseline document didn't update"

**Cause:** Main branch merge didn't trigger update job.

**Solution:**
1. Verify branch protection isn't blocking workflow
2. Check `secrets.GITHUB_TOKEN` permissions (requires `contents: write`)
3. Run manual update: `bash scripts/update-coverage-baseline.sh`

---

## Metrics & Data Dictionary

### JSON Structure

```json
{
  "timestamp": "2026-02-06T16:45:00Z",
  "metrics": {
    "go": {
      "module1": 88.4,
      "module2": 91.2,
      "__average__": 88.4,
      "__count__": 217
    },
    "python": { ... },
    "frontend": { ... }
  },
  "summary": {
    "go": {
      "language": "go",
      "average": 88.4,
      "total_files": 217,
      "threshold": 90,
      "status": "⚠️",
      "gap": -1.6,
      "modules": []
    },
    ...
  },
  "regressions": {
    "go": {
      "regressions": {
        "backend/internal/embeddings": {
          "baseline": 79.4,
          "current": 78.8,
          "delta": -0.6
        }
      },
      "improvements": { ... },
      "unchanged": { ... }
    }
  }
}
```

### Pipe-Delimited Format

Used in baseline artifact files for easy parsing:

```
backend/internal/handlers/item_handler.go|92.5
backend/internal/services/item_service.go|89.8
src/tracertm/models/item.py|97.2
...
```

---

## Coverage Goals by Language

| Language | Current | Target | Gap | Timeline |
|----------|---------|--------|-----|----------|
| Go | 88.4% | 90% | -1.6% | 2026-02-20 |
| Python | 87.8% | 90% | -2.2% | 2026-02-20 |
| TypeScript | 87.3% | 90% | -2.7% | 2026-02-28 |

---

## Next Steps

1. **Integrate regression detection** into `.github/workflows/ci.yml`
2. **Configure baseline auto-update** on main merges
3. **Set branch protection rule:** Require `coverage-regression-check` to pass
4. **Monitor trends** over time (weekly snapshots)
5. **Scale targets:** 95%+ for critical paths in Phase 4

---

## Related Files

- **Baseline Document:** `docs/reports/COVERAGE_BASELINE.md`
- **Extraction Script:** `scripts/extract_coverage_metrics.py`
- **Update Script:** `scripts/update-coverage-baseline.sh`
- **CI Workflow:** `.github/workflows/ci.yml`
- **Python Config:** `pyproject.toml`
- **Go Config:** `backend/.codecov.yml`
- **Frontend Config:** `frontend/apps/web/vitest.config.ts`

---

## Support & Questions

For questions about coverage metrics:
1. Check the baseline document for current metrics
2. Review regression detection rules (0.1% threshold)
3. See "Troubleshooting" section above
4. Open an issue with logs from GitHub Actions

---

**Status:** ✅ Ready to integrate

**Next Action:** Add regression detection and baseline update jobs to `.github/workflows/ci.yml`
