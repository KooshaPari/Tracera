# CLI Optimization Performance Tests

## Quick Start

### Install Dependencies

```bash
# From project root
pip install pytest pytest-benchmark psutil
```

### Run Tests

```bash
# From project root directory
cd tests/performance

# Run all CLI optimization tests
./run_cli_optimization_tests.sh --full

# Run quick tests only
./run_cli_optimization_tests.sh --quick

# Run benchmarks only
./run_cli_optimization_tests.sh --benchmarks

# Generate performance report
./run_cli_optimization_tests.sh --report
```

### Run Individual Test Files

```bash
# From project root
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Startup tests
pytest tests/performance/test_cli_startup.py -v

# Integration tests
pytest tests/integration/test_cli_integration.py -v

# Benchmarks
pytest tests/performance/test_cli_benchmarks.py --benchmark-only
```

## Test Suite Overview

### 1. Startup Performance Tests (`test_cli_startup.py`)

Tests CLI startup time, memory usage, and performance.

**Key Tests:**
- Cold startup time (< 500ms)
- Warm startup time (< 300ms)
- Memory usage (< 50MB)
- Memory leak detection
- Command execution speed
- Lazy loading performance

**Run:**
```bash
pytest tests/performance/test_cli_startup.py -v
```

### 2. Integration Tests (`test_cli_integration.py`)

Tests that optimizations don't break functionality.

**Key Tests:**
- Command group loading
- Lazy loading mechanisms
- Shell completion
- Alias system
- Error handling
- Cache behavior

**Run:**
```bash
pytest tests/integration/test_cli_integration.py -v
```

### 3. Benchmark Tests (`test_cli_benchmarks.py`)

Detailed performance benchmarking for tracking over time.

**Key Tests:**
- Import timing
- Lazy loading performance
- Cache operations
- Command execution
- Comparative analysis

**Run:**
```bash
pytest tests/performance/test_cli_benchmarks.py --benchmark-only
```

## Performance Targets

| Metric | Target | Test |
|--------|--------|------|
| Startup Time (cold) | < 500ms | test_cli_startup_time_cold |
| Startup Time (warm) | < 300ms | test_cli_startup_time_warm |
| Memory Usage | < 50MB | test_cli_memory_usage |
| Command Execution | < 100ms | test_command_group_help_performance |
| Lazy Load Overhead | < 50ms | test_lazy_loading_performance |
| Cache Hit Time | < 1ms | test_command_cache |

## Documentation

- [Complete Testing Guide](./CLI_OPTIMIZATION_TEST_GUIDE.md) - Comprehensive guide to all tests
- [Rollback Plan](./CLI_OPTIMIZATION_ROLLBACK_PLAN.md) - Procedures for rolling back optimizations
- [Implementation Summary](./CLI_OPTIMIZATION_IMPLEMENTATION_SUMMARY.md) - Overview of implementation

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running from project root and PYTHONPATH is set:

```bash
cd /path/to/tracertm
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
pytest tests/performance/test_cli_startup.py -v
```

### Missing Dependencies

Install all required dependencies:

```bash
pip install pytest pytest-benchmark pytest-asyncio psutil
```

### Tests Timing Out

Some tests measure real CLI execution and may take time. Increase timeout if needed:

```bash
pytest tests/performance/test_cli_startup.py -v --timeout=60
```

### Benchmark Comparison Fails

If comparing against baselines and they don't exist:

```bash
# Create initial baseline
./run_cli_optimization_tests.sh --baseline
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run CLI Performance Tests
  run: |
    pip install pytest pytest-benchmark psutil
    cd tests/performance
    ./run_cli_optimization_tests.sh --full
```

### Pre-Commit Hook

```bash
#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
pytest tests/performance/test_cli_startup.py -k "not benchmark" -v
```

## Maintenance

### Update Baselines

After verified performance improvements:

```bash
./run_cli_optimization_tests.sh --baseline
git add performance_baselines.json
git commit -m "Update CLI performance baselines"
```

### Review Performance Trends

Check benchmark history:

```bash
pytest tests/performance/test_cli_benchmarks.py --benchmark-only --benchmark-compare
```

## Support

For issues or questions:
1. Check [Test Guide](./CLI_OPTIMIZATION_TEST_GUIDE.md) troubleshooting section
2. Review test output for specific failures
3. Check [Rollback Plan](./CLI_OPTIMIZATION_ROLLBACK_PLAN.md) if optimizations cause issues
