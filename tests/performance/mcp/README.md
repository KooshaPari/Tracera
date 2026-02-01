# MCP Optimization Testing & Validation

Comprehensive test suite for MCP (Model Context Protocol) server optimizations.

## Overview

This directory contains all tests, benchmarks, and tools for validating MCP optimizations:

- **Performance Tests**: Verify performance targets are met
- **Integration Tests**: Ensure optimizations work correctly together
- **Benchmarks**: Compare before/after performance
- **Health Checks**: Verify system health
- **Rollback Plan**: Emergency procedures

## Quick Start

### Run All Tests

```bash
./run_all_tests.sh
```

This runs:
1. Health checks
2. Performance tests
3. Integration tests
4. Regression tests
5. Benchmarks
6. Report generation

### Run Specific Tests

```bash
# Performance tests only
pytest test_mcp_performance.py -v

# Integration tests only
pytest ../integration/test_mcp_optimizations.py -v

# Health check
./health_check.py

# Benchmark suite
./benchmark_mcp.py
```

## Performance Targets

| Metric | Target | Test |
|--------|--------|------|
| Tool Registration | <100ms | `TestToolRegistrationPerformance` |
| Cold Start | <200ms | `TestColdStartPerformance` |
| Tool Response | <500ms | `TestToolResponseTime` |
| Token Usage | <1,000/op | `TestTokenUsage` |
| Compression | >70% | `TestStreamingAndCompression` |
| Connection Reuse | >80% | `TestConnectionPooling` |

## Test Files

### Performance Tests

**`test_mcp_performance.py`** - Core performance tests

- `TestToolRegistrationPerformance`: Lazy loading, registration speed
- `TestColdStartPerformance`: Server startup time
- `TestToolResponseTime`: Tool execution speed
- `TestTokenUsage`: Token budget compliance
- `TestStreamingAndCompression`: Streaming and compression efficiency
- `TestConnectionPooling`: Connection pool performance
- `TestEndToEndPerformance`: Complete request-response cycle

### Integration Tests

**`../integration/test_mcp_optimizations.py`** - Integration tests

- `TestLazyLoadingIntegration`: Lazy loading with real tools
- `TestStreamingIntegration`: Streaming in real scenarios
- `TestCompressionIntegration`: Compression with real data
- `TestConnectionPoolingIntegration`: Pool under concurrent load
- `TestTokenManagementIntegration`: Token optimization in practice
- `TestFeatureFlagsAndRollback`: Feature flag toggling
- `TestRegressionPrevention`: No functionality broken
- `TestPerformanceComparison`: Before/after comparison

### Benchmark Suite

**`benchmark_mcp.py`** - Performance benchmarking

Runs comprehensive benchmarks:
- Tool registration (baseline vs optimized)
- Tool lookup
- Simple tool execution
- Complex tool execution
- Large response generation

Generates:
- `benchmark_results/mcp_benchmark_results.json`
- `benchmark_results/performance_report.md`

### Health Check

**`health_check.py`** - System health verification

Checks:
- Server running
- Tool registration working
- Lazy loading enabled/disabled
- Tool metadata accessible
- Async operations working
- Performance within thresholds
- Environment variables correct
- Memory usage reasonable
- Error logs clean

Generates:
- `health_check_results/health_check_results.json`

### Test Runner

**`run_all_tests.sh`** - Comprehensive test execution

Runs all tests in order:
1. Health check
2. Performance tests (6 test classes)
3. Integration tests (5 test classes)
4. Regression tests
5. Feature flag tests
6. Existing MCP tests
7. Benchmark suite
8. Report generation

Generates:
- `test_results/test_summary_YYYYMMDD_HHMMSS.md`

## Environment Variables

Configure optimizations via environment variables:

```bash
# Enable/disable optimizations
export TRACERTM_MCP_LAZY_LOADING=true       # Lazy load tools
export TRACERTM_MCP_COMPRESSION=true        # Compress responses
export TRACERTM_MCP_STREAMING=true          # Stream large responses
export TRACERTM_MCP_TOKEN_OPTIMIZATION=true # Optimize token usage
export TRACERTM_MCP_CONNECTION_POOL_SIZE=10 # Connection pool size

# For baseline comparison (no optimizations)
export TRACERTM_MCP_LAZY_LOADING=false
export TRACERTM_MCP_COMPRESSION=false
export TRACERTM_MCP_STREAMING=false
export TRACERTM_MCP_TOKEN_OPTIMIZATION=false
export TRACERTM_MCP_CONNECTION_POOL_SIZE=0
```

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-asyncio psutil

# Or use project dependencies
pip install -e ".[test]"
```

### Run Full Suite

```bash
# Run everything
./run_all_tests.sh

# Results in:
# - tests/performance/mcp/test_results/
# - tests/performance/mcp/benchmark_results/
# - tests/performance/mcp/health_check_results/
```

### Run Performance Tests

```bash
# All performance tests
pytest test_mcp_performance.py -v

# Specific test class
pytest test_mcp_performance.py::TestToolRegistrationPerformance -v

# Specific test
pytest test_mcp_performance.py::TestToolRegistrationPerformance::test_tool_registration_under_100ms -v

# With performance tracking
pytest test_mcp_performance.py -v --benchmark-only
```

### Run Integration Tests

```bash
# All integration tests
pytest ../integration/test_mcp_optimizations.py -v

# Specific test class
pytest ../integration/test_mcp_optimizations.py::TestLazyLoadingIntegration -v
```

### Run Health Check

```bash
# Interactive health check
./health_check.py

# Save results only
./health_check.py > /dev/null

# Results saved to:
# health_check_results/health_check_results.json
```

### Run Benchmark

```bash
# Full benchmark suite
./benchmark_mcp.py

# Results in:
# - benchmark_results/mcp_benchmark_results.json
# - benchmark_results/performance_report.md
```

## Interpreting Results

### Performance Test Results

Tests use pytest and report:
- **PASSED**: Met performance threshold
- **FAILED**: Exceeded threshold or error occurred

Example output:
```
✓ test_tool_registration_under_100ms PASSED
  Registered 50 tools in 45.23ms

✗ test_cold_start_under_200ms FAILED
  Cold start took 215.34ms (threshold: 200ms)
```

### Benchmark Results

Benchmarks generate JSON and Markdown reports:

**JSON** (`mcp_benchmark_results.json`):
```json
{
  "timestamp": 1706659200,
  "results": [...],
  "comparisons": [
    {
      "benchmark_name": "tool_registration",
      "baseline_ms": 500.0,
      "optimized_ms": 45.0,
      "improvement_percent": 91.0,
      "baseline_tokens": 1200,
      "optimized_tokens": 800,
      "token_reduction_percent": 33.3
    }
  ]
}
```

**Markdown** (`performance_report.md`):
- Executive summary
- Detailed results table
- Performance targets status
- Recommendations

### Health Check Results

Health check outputs:
- ✓ Check passed
- ✗ Check failed
- ⚠ Warning

Example:
```
✓ Server Running
  Status: PASS
  Duration: 12.34ms
  Message: OK

⚠ Lazy Loading
  Status: WARN
  Duration: 5.67ms
  Message: Lazy loading enabled but module already loaded
```

## Performance Baselines

Expected performance (with optimizations):

| Operation | Baseline (no opt) | Optimized | Improvement |
|-----------|-------------------|-----------|-------------|
| Tool Registration | 500ms | <100ms | 80%+ |
| Cold Start | 800ms | <200ms | 75%+ |
| Simple Tool | 150ms | <100ms | 33%+ |
| Complex Tool | 600ms | <500ms | 17%+ |
| Large Response | 2000ms | <1000ms | 50%+ |

## Rollback Testing

Test rollback procedures:

```bash
# 1. Run with optimizations
export TRACERTM_MCP_LAZY_LOADING=true
./run_all_tests.sh

# 2. Disable optimizations
export TRACERTM_MCP_LAZY_LOADING=false
./health_check.py

# 3. Verify functionality maintained
pytest test_mcp_performance.py::TestRegressionPrevention -v

# 4. Re-enable
export TRACERTM_MCP_LAZY_LOADING=true
./health_check.py
```

See `ROLLBACK_PLAN.md` for detailed procedures.

## Continuous Integration

### GitHub Actions Example

```yaml
name: MCP Performance Tests

on: [push, pull_request]

jobs:
  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12

      - name: Install dependencies
        run: |
          pip install -e ".[test]"

      - name: Run health check
        run: |
          cd tests/performance/mcp
          ./health_check.py

      - name: Run performance tests
        run: |
          pytest tests/performance/mcp/test_mcp_performance.py -v

      - name: Run integration tests
        run: |
          pytest tests/integration/test_mcp_optimizations.py -v

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: tests/performance/mcp/test_results/
```

## Troubleshooting

### Tests Failing

**Tool registration timeout**:
- Check lazy loading is enabled: `echo $TRACERTM_MCP_LAZY_LOADING`
- Verify registry imports correctly
- Check for circular imports

**Performance threshold exceeded**:
- Check system load: `top`, `htop`
- Verify no other processes consuming resources
- Run benchmark to establish new baseline

**Health check warnings**:
- Review environment variables
- Check module loading behavior
- Verify optimization flags are set

### Benchmark Issues

**Benchmark taking too long**:
- Reduce iterations: Edit `benchmark_mcp.py`, set `iterations=5`
- Run specific benchmarks only
- Use faster hardware

**Results inconsistent**:
- Ensure system is idle
- Run multiple times and average
- Check for background processes

### Integration Test Failures

**Feature flag tests failing**:
- Verify environment variables can be set
- Check no system-level overrides
- Test in clean environment

**Regression tests failing**:
- Review recent code changes
- Check if optimization broke functionality
- Compare with baseline behavior

## File Structure

```
tests/performance/mcp/
├── README.md                    # This file
├── ROLLBACK_PLAN.md            # Rollback procedures
├── test_mcp_performance.py     # Performance tests
├── benchmark_mcp.py            # Benchmark suite
├── health_check.py             # Health check script
├── run_all_tests.sh            # Test runner
├── __init__.py                 # Package init
├── test_results/               # Test output
├── benchmark_results/          # Benchmark output
└── health_check_results/       # Health check output
```

## Contributing

When adding new optimizations:

1. **Add performance test** in `test_mcp_performance.py`
2. **Add integration test** in `test_mcp_optimizations.py`
3. **Update benchmark** in `benchmark_mcp.py`
4. **Add health check** in `health_check.py`
5. **Update rollback plan** in `ROLLBACK_PLAN.md`
6. **Document** in this README

## References

- MCP Server Implementation: `src/tracertm/mcp/server.py`
- Tool Registry: `src/tracertm/mcp/registry.py`
- Existing MCP Tests: `tests/mcp/`
- Performance Tests Framework: `tests/performance/conftest.py`

## Support

For issues or questions:
1. Check this README
2. Review `ROLLBACK_PLAN.md`
3. Run health check: `./health_check.py`
4. Check test output in `test_results/`
5. Contact MCP team lead
