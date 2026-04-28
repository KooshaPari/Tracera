# CLI Optimization Testing & Validation Guide

## Overview

This guide covers comprehensive testing and validation of CLI optimizations including:
- Lazy loading mechanisms
- Command caching
- Performance monitoring
- Shell completion
- Alias systems

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Startup Time (cold) | < 500ms | `time rtm --version` |
| Startup Time (warm) | < 300ms | After caching |
| Memory Usage | < 50MB | RSS during startup |
| Command Execution | < 100ms | Help commands |
| Lazy Load Overhead | < 50ms | Module loading |
| Cache Hit Time | < 1ms | Cached retrieval |

## Test Suite Structure

```
tests/
├── performance/
│   ├── test_cli_startup.py           # Startup & memory tests
│   ├── test_cli_benchmarks.py        # Detailed benchmarks
│   ├── conftest.py                   # Shared fixtures
│   ├── performance_baselines.json    # Baseline metrics
│   ├── run_cli_optimization_tests.sh # Test execution script
│   └── CLI_OPTIMIZATION_ROLLBACK_PLAN.md
├── integration/
│   └── test_cli_integration.py       # Integration tests
└── unit/cli/
    └── [existing CLI tests]           # Regression tests
```

## Quick Start

### 1. Run All Tests

```bash
cd tests/performance
./run_cli_optimization_tests.sh --full
```

### 2. Run Specific Test Suites

```bash
# Startup performance tests only
pytest test_cli_startup.py -v

# Integration tests only
pytest ../integration/test_cli_integration.py -v

# Benchmarks only
pytest test_cli_benchmarks.py --benchmark-only
```

### 3. Generate Performance Report

```bash
./run_cli_optimization_tests.sh --report
```

## Detailed Test Descriptions

### 1. Startup Performance Tests (`test_cli_startup.py`)

#### Purpose
Ensure CLI meets startup time and memory targets.

#### Key Tests

**Cold Startup Test**
- Clears all caches
- Measures startup time with `--version`
- **Target:** < 500ms
- **Command:** `pytest test_cli_startup.py::test_cli_startup_time_cold`

**Warm Startup Test**
- Uses cached modules
- Measures startup with cache
- **Target:** < 500ms (should be faster than cold)
- **Command:** `pytest test_cli_startup.py::test_cli_startup_time_warm`

**Memory Usage Test**
- Tracks RSS memory during execution
- **Target:** < 50MB
- **Command:** `pytest test_cli_startup.py::test_cli_memory_usage`

**Memory Leak Test**
- Runs CLI multiple times
- Ensures memory doesn't grow
- **Target:** < 10MB growth across 5 runs
- **Command:** `pytest test_cli_startup.py::test_cli_memory_no_leaks`

**Command Performance Tests**
- Tests help command speed
- Tests command group loading
- **Target:** < 100ms per command
- **Command:** `pytest test_cli_startup.py -k "command"`

#### Running Startup Tests

```bash
# All startup tests
pytest test_cli_startup.py -v

# Specific test
pytest test_cli_startup.py::test_cli_startup_time_cold -v

# With performance tracking
pytest test_cli_startup.py -v --perf-tracker
```

### 2. Integration Tests (`test_cli_integration.py`)

#### Purpose
Verify lazy loading and optimizations don't break functionality.

#### Key Test Classes

**TestCommandGroups**
- Verifies all command groups load
- Tests: config, project, item, link, mcp, auth, test
- **Command:** `pytest test_cli_integration.py::TestCommandGroups -v`

**TestLazyLoading**
- Verifies lazy loader caches modules
- Tests module loading performance
- Tests cache clearing
- **Command:** `pytest test_cli_integration.py::TestLazyLoading -v`

**TestShellCompletion**
- Tests completion generation
- Verifies command listing
- **Command:** `pytest test_cli_integration.py::TestShellCompletion -v`

**TestAliasSystem**
- Tests MVP shortcuts
- Tests command variations
- **Command:** `pytest test_cli_integration.py::TestAliasSystem -v`

**TestErrorHandling**
- Tests graceful error handling
- Tests help always works
- **Command:** `pytest test_cli_integration.py::TestErrorHandling -v`

#### Running Integration Tests

```bash
# All integration tests
pytest ../integration/test_cli_integration.py -v

# Specific class
pytest ../integration/test_cli_integration.py::TestLazyLoading -v

# Specific test
pytest ../integration/test_cli_integration.py::TestLazyLoading::test_lazy_loader_module_caching -v
```

### 3. Benchmark Tests (`test_cli_benchmarks.py`)

#### Purpose
Detailed performance benchmarking for tracking over time.

#### Key Benchmark Categories

**Startup Benchmarks**
- Import time measurements
- Module loading overhead
- **Command:** `pytest test_cli_benchmarks.py::TestStartupBenchmarks --benchmark-only`

**Lazy Loading Benchmarks**
- First load vs cached load
- Multiple module loading
- **Command:** `pytest test_cli_benchmarks.py::TestLazyLoadingBenchmarks --benchmark-only`

**Cache Benchmarks**
- Set/get operation speed
- Cache hit vs miss
- Bulk operations
- **Command:** `pytest test_cli_benchmarks.py::TestCacheBenchmarks --benchmark-only`

**Command Execution Benchmarks**
- Help command timing
- Version command timing
- Command group loading
- **Command:** `pytest test_cli_benchmarks.py::TestCommandExecutionBenchmarks --benchmark-only`

#### Running Benchmarks

```bash
# All benchmarks
pytest test_cli_benchmarks.py --benchmark-only

# With statistics
pytest test_cli_benchmarks.py --benchmark-only --benchmark-verbose

# Save results
pytest test_cli_benchmarks.py --benchmark-only --benchmark-autosave

# Compare against baseline
pytest test_cli_benchmarks.py --benchmark-only --benchmark-compare=0001
```

## Test Execution Workflows

### Development Workflow

```bash
# 1. Make code changes
vim src/tracertm/cli/performance.py

# 2. Run quick tests
pytest test_cli_startup.py -k "not benchmark" -v

# 3. If passing, run integration tests
pytest ../integration/test_cli_integration.py -v

# 4. If all passing, run benchmarks
pytest test_cli_benchmarks.py --benchmark-only
```

### Pre-Commit Workflow

```bash
# Run quick validation
./run_cli_optimization_tests.sh --quick

# Check if performance targets met
pytest test_cli_startup.py::test_cli_startup_time_cold -v
pytest test_cli_startup.py::test_cli_memory_usage -v
```

### CI/CD Workflow

```bash
# Full test suite
./run_cli_optimization_tests.sh --full

# Generate report
./run_cli_optimization_tests.sh --report

# Update baselines (if approved)
./run_cli_optimization_tests.sh --baseline
```

### Release Workflow

```bash
# 1. Run full test suite
./run_cli_optimization_tests.sh --full

# 2. Generate performance report
./run_cli_optimization_tests.sh --report

# 3. Compare against baselines
pytest test_cli_benchmarks.py --benchmark-only --benchmark-compare

# 4. Update baselines for next release
./run_cli_optimization_tests.sh --baseline
```

## Performance Baselines

### Creating Initial Baseline

```bash
# Run benchmarks and save
pytest test_cli_benchmarks.py --benchmark-only --benchmark-autosave

# Update baseline file
./run_cli_optimization_tests.sh --baseline
```

### Baseline File Format

`performance_baselines.json`:
```json
{
  "cli_startup_cold_ms": 450,
  "cli_startup_warm_ms": 280,
  "cli_memory_mb": 42,
  "lazy_load_first_ms": 15,
  "lazy_load_cached_ms": 0.5,
  "cache_get_hit_ms": 0.3,
  "command_help_ms": 85
}
```

### Comparing Against Baseline

```bash
# Run with comparison
pytest test_cli_benchmarks.py --benchmark-only --benchmark-compare=baseline

# View differences
pytest test_cli_benchmarks.py --benchmark-only --benchmark-compare-fail=mean:10%
```

## Troubleshooting

### Tests Failing

#### Startup Time Exceeded

**Symptom:**
```
AssertionError: Cold startup too slow: 650ms > 500ms
```

**Investigation:**
```bash
# Profile imports
python -X importtime -m tracertm.cli.app --version 2>&1 | grep -E "import time"

# Check for heavy modules
pytest test_cli_startup.py::test_no_unnecessary_imports_at_startup -v
```

**Solutions:**
1. Move heavy imports to lazy loading
2. Reduce module-level imports
3. Use conditional imports
4. Check for circular imports

#### Memory Usage Exceeded

**Symptom:**
```
AssertionError: Memory usage too high: 65MB > 50MB
```

**Investigation:**
```bash
# Profile memory
python -m memory_profiler src/tracertm/cli/app.py

# Check for memory leaks
pytest test_cli_startup.py::test_cli_memory_no_leaks -v
```

**Solutions:**
1. Clear caches appropriately
2. Use weak references where possible
3. Ensure proper cleanup in context managers
4. Check for retained references

#### Command Too Slow

**Symptom:**
```
AssertionError: config help too slow: 150ms > 100ms
```

**Investigation:**
```bash
# Time command execution
time rtm config --help

# Profile with cProfile
python -m cProfile -s cumtime -m tracertm.cli.app config --help
```

**Solutions:**
1. Lazy load command modules
2. Cache command help text
3. Optimize command registration
4. Reduce validation overhead

### Benchmark Regressions

**Symptom:**
```
Performance regression detected: 25% slower than baseline
```

**Investigation:**
```bash
# Compare specific benchmarks
pytest test_cli_benchmarks.py::test_benchmark_import_cli_app --benchmark-only --benchmark-compare

# Check git diff for changes
git diff HEAD~1 src/tracertm/cli/
```

**Solutions:**
1. Revert recent changes
2. Profile specific slow operations
3. Review code for inefficiencies
4. Update baseline if intentional

## Advanced Usage

### Custom Performance Tracking

```python
from tests.performance.conftest import measure_time, assert_performance

def test_my_operation():
    with measure_time("my_operation", threshold_ms=100) as timing:
        # Your operation here
        result = perform_operation()

    # Timing info available in timing dict
    print(f"Operation took: {timing['elapsed_ms']:.2f}ms")
```

### Creating New Benchmarks

```python
def test_benchmark_new_feature(benchmark):
    """Benchmark a new feature."""

    def operation_to_benchmark():
        # Your code here
        return result

    result = benchmark(operation_to_benchmark)

    # Assertions
    assert result is not None
    assert benchmark.stats["mean"] < 0.1  # < 100ms
```

### Parameterized Performance Tests

```python
@pytest.mark.parametrize("count", [10, 100, 1000])
def test_operation_scalability(count, perf_tracker):
    """Test operation scales linearly."""
    start = time.perf_counter()

    for i in range(count):
        perform_operation(i)

    elapsed_ms = (time.perf_counter() - start) * 1000
    perf_tracker.record(f"operation_{count}", elapsed_ms, count)

    # Should scale linearly
    assert elapsed_ms / count < 10  # < 10ms per operation
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: CLI Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-benchmark psutil

      - name: Run performance tests
        run: |
          cd tests/performance
          ./run_cli_optimization_tests.sh --full

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: performance-reports
          path: tests/performance/reports/
```

## Best Practices

### Writing Performance Tests

1. **Isolate what you're measuring**
   - Clear caches before tests
   - Use fixtures for setup
   - Measure only the operation

2. **Set realistic thresholds**
   - Based on user experience
   - Consider CI environment overhead
   - Allow some variance

3. **Make tests deterministic**
   - Avoid network calls
   - Mock external dependencies
   - Use fixed seeds for randomness

4. **Document what you're testing**
   - Clear test names
   - Comments explaining thresholds
   - Reference requirements

### Maintaining Baselines

1. **Update baselines when:**
   - Major refactoring complete
   - Performance improvements verified
   - Hardware/environment changes

2. **Don't update baselines when:**
   - Tests randomly fail
   - Unclear why performance changed
   - Regressions not investigated

3. **Review baseline changes:**
   - Require approval for baseline updates
   - Document reason for change
   - Compare before/after metrics

## Reporting

### Generate Full Report

```bash
./run_cli_optimization_tests.sh --report
```

### Report Contents

1. **Executive Summary**
   - Pass/fail status
   - Performance targets met
   - Comparison to baseline

2. **Detailed Results**
   - Individual test results
   - Benchmark statistics
   - Memory profiles

3. **Recommendations**
   - Areas for improvement
   - Potential optimizations
   - Rollback considerations

4. **Trend Analysis**
   - Performance over time
   - Regression detection
   - Improvement tracking

## References

- [Rollback Plan](./CLI_OPTIMIZATION_ROLLBACK_PLAN.md)
- [Performance Baselines](./performance_baselines.json)
- [Benchmark Results](./benchmark_results.json)
- [Test Execution Script](./run_cli_optimization_tests.sh)
