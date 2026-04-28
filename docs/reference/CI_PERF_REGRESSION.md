# Performance Regression Testing

**Quick Reference:** Run `vitest bench` (frontend) + `go test -bench` (backend), compare vs main baseline stored in git, fail if >10% regression. Store new baseline on main merge.

## Overview

The Performance Regression Testing workflow (`.github/workflows/perf-regression.yml`) automatically:

1. **Runs benchmarks** on both frontend and backend
2. **Compares against baseline** from main branch
3. **Fails CI if >20% regression detected** (critical threshold)
4. **Warns if 10-20% regression** (informational)
5. **Stores new baselines** when merged to main

This ensures performance doesn't degrade between releases.

## Workflow Triggers

| Trigger | Behavior |
|---------|----------|
| **Pull Request to main/develop** | Run benchmarks, compare vs main, fail if critical regression |
| **Push to main** | Run benchmarks, store new baseline, no comparison |
| **Push to develop** | Run benchmarks, compare vs develop baseline |

## Architecture

### Job 1: Backend Benchmarks (`backend-benchmarks`)

```bash
# Run Go benchmarks
go test -bench=. -benchmem -benchstat ./...
```

**Metrics collected:**
- `ns/op` (nanoseconds per operation) - lower is better
- `bytes/op` (memory allocation per operation) - lower is better
- `allocs/op` (allocations per operation) - lower is better

**Storage:**
- `backend/benchmark-output/current.json` - current run metrics
- `backend/benchmark-output/baseline.json` - main branch baseline (if available)
- `backend/BENCHMARK_REPORT.md` - formatted comparison report

### Job 2: Frontend Benchmarks (`frontend-benchmarks`)

```bash
# Run vitest benchmarks (from package.json script)
bun run test:performance:10k --reporter=json
```

**Metrics collected:**
- `mean` (mean execution time in seconds) - lower is better
- `hz` (operations per second) - higher is better
- `rme` (relative margin of error) - confidence in measurement

**Storage:**
- `frontend/apps/web/benchmark-output/current.json` - current run metrics
- `frontend/apps/web/benchmark-output/baseline.json` - main branch baseline (if available)
- `frontend/apps/web/BENCHMARK_REPORT.md` - formatted comparison report

### Job 3: Gating Decision (`gating-decision`)

Aggregates results and:
- ✅ **Passes** if no critical (>20%) regressions
- ⚠️ **Warns** if 10-20% regressions exist (non-blocking)
- ❌ **Fails** if >20% regressions detected (blocks merge)

### Job 4: Store Baseline (`store-baseline`)

**Only runs on push to main.** Commits new baseline metrics to `.github/perf-baselines/`:

```
.github/perf-baselines/
├── backend-baseline.json      # Latest backend benchmark baseline
├── frontend-baseline.json     # Latest frontend benchmark baseline
└── metadata.json              # Timestamp, commit hash, file references
```

## Regression Thresholds

| Threshold | Severity | CI Impact | Action |
|-----------|----------|-----------|--------|
| < 10% | ✅ Pass | Passes | No action needed |
| 10-20% | ⚠️ Warning | Passes | Review and consider optimization |
| > 20% | 🔴 Critical | **Fails** | Must fix before merge |

## Running Locally

### Backend Benchmarks

```bash
cd backend

# Run all benchmarks
go test -bench=. -benchmem -benchstat ./...

# Run specific benchmark
go test -bench=BenchmarkCreateItem -benchmem ./...

# Compare against baseline
go test -bench=. -benchmem ./... > current.txt
# (Compare with baseline.txt manually or via benchstat)
```

### Frontend Benchmarks

```bash
cd frontend/apps/web

# Run from package.json script
bun run test:performance:10k

# Or directly with vitest
bun run vitest bench src/__tests__/performance/10k-baseline.bench.ts --run

# With reporter options
bun run vitest bench src/__tests__/performance/ --reporter=json --run
```

## Benchmark Files

### Backend Benchmarks

Located in `backend/tests/`:
- `benchmark_test.go` - Item CRUD operation benchmarks
- `benchmarks/service_performance_benchmark_test.go` - Service-level benchmarks

### Frontend Benchmarks

Located in `frontend/apps/web/src/__tests__/performance/`:
- `10k-baseline.bench.ts` - 10,000 node graph rendering
- `benchmarks.test.ts` - Core component benchmarks
- `KanbanView.perf.test.tsx` - Kanban view performance
- `TreeView.perf.test.tsx` - Tree view performance

Additional benchmarks:
- `src/lib/__tests__/gpuForceLayout.benchmark.test.ts` - GPU force-directed layout
- `src/lib/__tests__/spatialIndex.benchmark.test.ts` - Spatial indexing performance

## Baseline Management

### Location

Baselines are stored in `.github/perf-baselines/`:

```json
// backend-baseline.json
[
  {
    "name": "CreateItem",
    "ops": 1000000,
    "ns_per_op": 1234,
    "bytes_per_op": 5678,
    "allocs_per_op": 90
  }
]

// frontend-baseline.json
[
  {
    "name": "10k-baseline",
    "hz": 15000,
    "mean": 0.000067,
    "median": 0.000065,
    "rme": 0.5
  }
]
```

### Updating Baselines

Baselines are **automatically updated** when code is merged to main:

1. PR benchmarks run and compare against baseline
2. If passed (no critical regressions), merge to main
3. `store-baseline` job captures new metrics
4. Commits baseline files to `.github/perf-baselines/`

### Manual Baseline Reset

If you need to manually reset baselines (e.g., after major infrastructure change):

```bash
# Run benchmarks locally
cd backend && go test -bench=. -benchmem ./... > /tmp/backend.json
cd frontend/apps/web && vitest bench --run --reporter=json > /tmp/frontend.json

# Commit new baselines
git add .github/perf-baselines/
git commit -m "chore: reset performance baselines"
git push origin main
```

## Interpreting Results

### Backend Report Example

```markdown
# Backend Benchmark Report

## Summary

| Category | Count | Status |
|----------|-------|--------|
| ✅ Passed (<10%) | 45 | Good |
| ⚠️ Warning (10-20%) | 2 | Check |
| 🔴 Critical (>20%) | 0 | Fail |
| 🆕 New Benchmarks | 1 | Track |

## Critical Regressions

(None)

## Warnings

| Benchmark | Baseline (ns/op) | Current (ns/op) | Regression |
|-----------|------------------|-----------------|------------|
| QueryItems | 1,234,567 | 1,356,789 | 10.0% |
```

**Action:** Review QueryItems implementation for optimization opportunities.

### Frontend Report Example

```markdown
# Frontend Benchmark Report

## Summary

| Category | Count | Status |
|----------|-------|--------|
| ✅ Passed (<10%) | 8 | Good |
| ⚠️ Warning (10-20%) | 0 | Check |
| 🔴 Critical (>20%) | 1 | Fail |
| 🆕 New Benchmarks | 0 | Track |

## Critical Regressions

| Benchmark | Baseline (ms) | Current (ms) | Regression |
|-----------|---------------|--------------|------------|
| 10k-baseline | 66.67 | 82.50 | 23.8% |
```

**Action:** Must fix graph rendering before merge. Investigate component memoization, virtualization, or GPU utilization.

## GitHub UI Integration

### Pull Request Checks

Workflow shows as required status check:
- ✅ `performance-regression-testing` passes
- ❌ `performance-regression-testing` fails (blocks merge)

Reports appear in:
1. **Checks tab** - Full logs and artifacts
2. **Job Summary** - Formatted benchmark comparison
3. **Artifacts** - Raw JSON for programmatic analysis

### Artifacts

Generated artifacts (30-day retention):
- `backend-benchmarks/` - Backend metrics and report
- `frontend-benchmarks/` - Frontend metrics and report
- `perf-baselines/` (main only) - Baseline files for next PR

## Debugging

### Benchmark Fails but Locally Passes

**Cause:** GitHub Actions runners often have different performance characteristics.

**Solution:**
1. Check artifacts for exact regression values
2. Run on similar system or Docker container
3. If 15-20% range, likely system variance - retry
4. If >25%, real regression - optimize code

### No Baseline on First Run

**Expected behavior** on initial PR:
- Baselines don't exist yet
- Workflow stores current metrics as baseline
- Comparison skipped
- No pass/fail determination

On subsequent PRs:
- New baselines available for comparison
- Regression detection begins

### Missing Benchmark Output

**Cause:** Benchmark compilation error or test framework issue.

**Solution:**
1. Check job logs for Go/Node errors
2. Run benchmark locally: `bun run test:performance:10k`
3. Verify Go dependencies: `go mod download`
4. Check Node dependencies: `bun install --frozen-lockfile`

## Advanced Configuration

### Changing Thresholds

Edit `.github/workflows/perf-regression.yml`:

```yaml
# In comparison step, change THRESHOLD_WARN and THRESHOLD_CRITICAL
THRESHOLD_WARN = 10      # Yellow warning
THRESHOLD_CRITICAL = 20  # Red critical (fails CI)
```

### Adding New Benchmarks

**Backend:**
1. Add test function: `func BenchmarkNewTest(b *testing.B) { ... }`
2. Run workflow - new benchmark automatically captured
3. Baseline updated on main merge

**Frontend:**
1. Create `*.bench.ts` file with vitest benchmark
2. Include in `test:performance:10k` script
3. Run workflow - automatically detected

### Excluding Benchmarks

In vitest `defineConfig`:
```ts
test: {
  exclude: [
    '**/*.benchmark.test.ts',    // Skip benchmarks in default test run
    '**/*.perf.test.tsx'
  ]
}
```

## CI/CD Integration

### Workflow Dependencies

```
setup (detect branch)
  ├─ backend-benchmarks
  ├─ frontend-benchmarks
  └─ gating-decision (final pass/fail)
      └─ store-baseline (main only)
```

### Concurrency

- Single run per branch (older runs canceled)
- Main merges queue to preserve baseline order
- PRs run immediately

### Artifact Cleanup

- PR artifacts: 30 days
- Main baseline artifacts: 90 days

## Troubleshooting

### Q: Workflow is slow

**A:** Benchmarks intentionally run many iterations for accuracy. Typical times:
- Backend: 3-5 minutes
- Frontend: 5-10 minutes
- Total: ~15 minutes

### Q: Baseline not updating after main merge

**A:** Check `.github/perf-baselines/` directory exists and files are committed:
```bash
git log --oneline -- .github/perf-baselines/ | head -5
```

### Q: False positive regression (variance in measurements)

**A:** Benchmark variance is normal (2-5% is expected). Solutions:
1. Retry: Re-run PR workflow if <10% regression
2. Increase iterations: Modify benchmark `b.N` value
3. Increase threshold: If consistent pattern in CI vs local

### Q: How to ignore a specific benchmark?

**A:** Add benchmark to exclude pattern:
```ts
// In vitest.config.ts
exclude: [
  '**/*.benchmark.test.ts',
  'src/__tests__/performance/slow-benchmark.ts'  // Exclude specific
]
```

## References

- Backend benchmarking: `backend/scripts/benchmark-comparison.sh`
- Frontend vitest docs: https://vitest.dev/api/
- Go testing: https://golang.org/cmd/go#hdr-Test_packages
