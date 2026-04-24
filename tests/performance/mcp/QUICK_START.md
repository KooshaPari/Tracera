# MCP Optimization Testing - Quick Start

## 5-Minute Quick Start

### 1. Run All Tests (Recommended)

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/tests/performance/mcp
./run_all_tests.sh
```

**Output**: Complete test summary with pass/fail status

### 2. Health Check Only

```bash
./health_check.py
```

**Output**: System health status with ✓/✗/⚠ indicators

### 3. Performance Tests Only

```bash
pytest test_mcp_performance.py -v
```

**Output**: 18 performance tests with timing

### 4. Benchmark Suite

```bash
./benchmark_mcp.py
```

**Output**:
- `benchmark_results/mcp_benchmark_results.json`
- `benchmark_results/performance_report.md`

## Common Commands

### Run Specific Test

```bash
# Tool registration performance
pytest test_mcp_performance.py::TestToolRegistrationPerformance -v

# Cold start performance
pytest test_mcp_performance.py::TestColdStartPerformance -v

# Integration tests
pytest ../integration/test_mcp_optimizations.py::TestLazyLoadingIntegration -v
```

### Enable/Disable Optimizations

```bash
# Enable all optimizations
export TRACERTM_MCP_LAZY_LOADING=true
export TRACERTM_MCP_COMPRESSION=true
export TRACERTM_MCP_STREAMING=true
export TRACERTM_MCP_TOKEN_OPTIMIZATION=true
export TRACERTM_MCP_CONNECTION_POOL_SIZE=10

# Disable all optimizations (baseline)
export TRACERTM_MCP_LAZY_LOADING=false
export TRACERTM_MCP_COMPRESSION=false
export TRACERTM_MCP_STREAMING=false
export TRACERTM_MCP_TOKEN_OPTIMIZATION=false
export TRACERTM_MCP_CONNECTION_POOL_SIZE=0
```

### Rollback

```bash
# Quick rollback (disable all optimizations)
export TRACERTM_MCP_LAZY_LOADING=false
export TRACERTM_MCP_COMPRESSION=false
export TRACERTM_MCP_STREAMING=false
export TRACERTM_MCP_TOKEN_OPTIMIZATION=false
export TRACERTM_MCP_CONNECTION_POOL_SIZE=0

systemctl restart tracertm-mcp
./health_check.py
```

## Performance Targets

| Metric | Target | Command to Test |
|--------|--------|-----------------|
| Tool Registration | <100ms | `pytest test_mcp_performance.py::TestToolRegistrationPerformance::test_tool_registration_under_100ms -v` |
| Cold Start | <200ms | `pytest test_mcp_performance.py::TestColdStartPerformance::test_cold_start_under_200ms -v` |
| Tool Response | <500ms | `pytest test_mcp_performance.py::TestToolResponseTime -v` |
| Token Usage | <1,000/op | `pytest test_mcp_performance.py::TestTokenUsage -v` |

## File Locations

```
tests/performance/mcp/
├── test_mcp_performance.py     # Performance tests
├── benchmark_mcp.py            # Benchmark suite
├── health_check.py             # Health checker
├── run_all_tests.sh            # Run everything
├── test_results/               # Test output
├── benchmark_results/          # Benchmark output
└── health_check_results/       # Health check output
```

## Quick Troubleshooting

**Tests failing?**
```bash
# Check environment
./health_check.py

# Run with verbose output
pytest test_mcp_performance.py -v -s
```

**Performance too slow?**
```bash
# Check system resources
top

# Run benchmark to establish baseline
./benchmark_mcp.py
```

**Need to rollback?**
```bash
# See ROLLBACK_PLAN.md
cat ROLLBACK_PLAN.md
```

## Next Steps

1. ✅ Run `./run_all_tests.sh` to verify everything works
2. ✅ Review `test_results/test_summary_*.md`
3. ✅ Check `benchmark_results/performance_report.md`
4. ✅ Read `README.md` for detailed documentation
5. ✅ Read `ROLLBACK_PLAN.md` before deployment

## Expected Results

All tests should pass with these improvements:

- **Tool Registration**: 80%+ faster (<100ms vs ~500ms)
- **Cold Start**: 75%+ faster (<200ms vs ~800ms)
- **Token Usage**: 33%+ reduction
- **Network**: 70%+ compression savings

## Support

- **Documentation**: `README.md`
- **Rollback**: `ROLLBACK_PLAN.md`
- **Index**: `MCP_OPTIMIZATION_TEST_INDEX.md`
- **Health Check**: `./health_check.py`
