# Benchmark Regression Gating - Quick Reference

**Effective Date**: 2026-02-06

---

## What It Does

Automatically detects performance regressions in Go backend benchmarks and blocks merging PRs that exceed regression thresholds.

## Thresholds

| Level | Threshold | Action |
|-------|-----------|--------|
| ✅ PASS | < 10% slower | OK, merge allowed |
| ⚠️ WARN | 10-20% slower | Warning, merge allowed |
| 🔴 CRITICAL | > 20% slower | FAIL, merge blocked |

## For PR Authors

### What to Expect

When you open a PR with Go backend changes:

1. **Benchmarks Run** - Automatically as part of CI
2. **Comparison** - Metrics compared against main branch baseline
3. **Report** - Results shown in "Benchmark Regression Comparison" check
4. **Action** -
   - ✅ Green check if < 10% slower
   - ⚠️ Yellow warning if 10-20% slower (still passes)
   - 🔴 Red failure if > 20% slower (blocks merge)

### If Your PR Fails Benchmarks

**Critical Regression (>20%)**

1. Review the detailed report in GitHub checks
2. Identify which benchmarks regressed
3. Analyze your code changes:
   - Did you add allocations?
   - Did you add loops or complexity?
   - Is there a lock contention issue?
4. Options:
   - Optimize the code
   - Revert the expensive change
   - Split into smaller, incremental PRs

**Example**: "BenchmarkCreateItem now 1250ns/op (was 1000ns/op = 25% slower)"

## For Backend Developers

### Running Benchmarks Locally

```bash
# Run all benchmarks
go test -bench=. -benchmem ./...

# Run specific benchmark
go test -bench=BenchmarkCreateItem -benchmem ./...

# More samples for accurate results
go test -bench=. -benchmem -benchtime=10s ./...

# Compare with baseline using benchstat
go test -bench=. -benchmem ./... | tee new.txt
# Then compare with previous baseline
```

### Understanding Metrics

- **ns/op**: Nanoseconds per operation (lower is faster)
- **B/op**: Bytes allocated per operation (lower is better)
- **allocs/op**: Number of allocations per operation (lower is better)
- **ops/sec**: Operations per second (higher is faster)

### Writing Good Benchmarks

Requirements:
- Function name must start with `Benchmark`
- File must end with `_test.go`
- Takes `*testing.B` parameter

Example:
```go
func BenchmarkMyFunction(b *testing.B) {
    for i := 0; i < b.N; i++ {
        MyFunction()
    }
}
```

### Improving Performance

**If a benchmark regresses:**

1. **Profile first**
   ```bash
   go test -bench=BenchmarkName -benchmem -cpuprofile=cpu.prof ./...
   go tool pprof cpu.prof
   ```

2. **Common issues**:
   - Unnecessary allocations → use pooling or stack allocation
   - Lock contention → reduce critical sections
   - Extra syscalls → batch operations
   - Algorithm complexity → use better algorithm

3. **Verify fix**:
   ```bash
   # Run benchmark multiple times to confirm
   for i in {1..5}; do go test -bench=BenchmarkName -benchmem ./...; done
   ```

## For Reviewers

### What to Check

When reviewing a PR with benchmark changes:

1. **Did benchmarks run?** ✅ Look for "Benchmark Regression Comparison" check
2. **What's the regression?** Check detailed report for percentages
3. **Is it acceptable?**
   - Improvements (negative %) are always good
   - < 10% regression is acceptable
   - 10-20% needs justification
   - > 20% should be rejected
4. **Code justification** - Did author explain the trade-off?

### Benchmark Regression Report

Located in GitHub PR checks, includes:

```
| Benchmark | Baseline | Current | Regression | Status |
| BenchmarkCreateItem | 1000 ns | 1050 ns | 5% | ✅ PASS |
| BenchmarkGetItem | 500 ns | 575 ns | 15% | ⚠️ WARN |
```

## Monitoring and Trends

### Track Benchmarks Over Time

```bash
# Run benchmark and save results
go test -bench=. -benchmem ./... > results-$(date +%Y%m%d).txt

# Compare multiple runs with benchstat
go tool benchstat results-*.txt
```

### Artifact Storage

Benchmark baselines are stored as GitHub artifacts:
- **Name**: `go-benchmark-baseline`
- **Retention**: 90 days
- **Updated**: After each PR merge to main

## Troubleshooting

### "Benchmark failed but I didn't change anything"

**Common causes**:
- System load affecting timing
- GC timing variance
- CPU frequency scaling

**Solution**:
- Re-run to confirm consistency
- Run with `-benchtime=10s` for larger sample
- Check machine load during test

### Benchmark "regressed" but code didn't change

**Possible causes**:
- Environmental variance (system load, CPU throttling)
- GC pressure changes
- Dependent library versions

**What to do**:
1. Run locally multiple times to check variance
2. Request re-run in CI
3. If consistent, investigate dependent libraries

### I want different thresholds for my benchmark

**Options**:
1. Contact team lead to adjust global thresholds
2. Add benchmark-specific overrides (planned feature)
3. Mark benchmark as "high-variance" (future enhancement)

## CI Checks

### Benchmark Step Details

In your PR's "Checks" tab:

**Benchmark Regression Comparison**
- ✅ **PASS** - No benchmarks exceed 20% regression
- ⚠️ **WARNING** - Some benchmarks 10-20% slower (passes CI)
- ❌ **FAIL** - Benchmarks > 20% slower (blocks merge)

Click "Details" to see full report with metrics.

## Quick Commands

```bash
# Run all benchmarks
make bench

# Run specific benchmark
make bench BENCH=CreateItem

# Show benchmark stats
go test -bench=. -benchmem -benchstat ./...

# Profile for optimization
go test -bench=. -cpuprofile=cpu.prof ./...
go tool pprof cpu.prof

# Compare against baseline
go test -bench=. -benchmem ./... > new.txt
benchstat old.txt new.txt
```

## Additional Resources

- Full documentation: `/docs/reports/PHASE_3_2_BENCHMARK_REGRESSION_GATING.md`
- Script location: `/backend/scripts/benchmark-comparison.sh`
- Test suite: `/backend/scripts/test-benchmark-comparison.sh`
- Go benchmarking guide: https://pkg.go.dev/testing#hdr-Benchmarks

---

**Last Updated**: 2026-02-06
**Maintained By**: Team Lead
