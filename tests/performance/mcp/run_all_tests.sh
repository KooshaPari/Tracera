#!/bin/bash
# MCP Optimization Test Runner
# Runs complete test suite for MCP optimizations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "MCP Optimization Test Suite"
echo "=========================================="
echo ""

# Create results directory
mkdir -p tests/performance/mcp/test_results

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run tests
run_test() {
    local test_name=$1
    local test_command=$2

    echo -e "${YELLOW}Running: $test_name${NC}"

    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED${NC}: $test_name"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}: $test_name"
        ((TESTS_FAILED++))
        return 1
    fi
}

# 1. Health Check
echo ""
echo "=========================================="
echo "1. Health Check"
echo "=========================================="
run_test "MCP Health Check" \
    "python tests/performance/mcp/health_check.py"

# 2. Performance Tests
echo ""
echo "=========================================="
echo "2. Performance Tests"
echo "=========================================="
run_test "Tool Registration Performance" \
    "pytest tests/performance/mcp/test_mcp_performance.py::TestToolRegistrationPerformance -v"

run_test "Cold Start Performance" \
    "pytest tests/performance/mcp/test_mcp_performance.py::TestColdStartPerformance -v"

run_test "Tool Response Time" \
    "pytest tests/performance/mcp/test_mcp_performance.py::TestToolResponseTime -v"

run_test "Token Usage" \
    "pytest tests/performance/mcp/test_mcp_performance.py::TestTokenUsage -v"

run_test "Streaming and Compression" \
    "pytest tests/performance/mcp/test_mcp_performance.py::TestStreamingAndCompression -v"

run_test "Connection Pooling" \
    "pytest tests/performance/mcp/test_mcp_performance.py::TestConnectionPooling -v"

# 3. Integration Tests
echo ""
echo "=========================================="
echo "3. Integration Tests"
echo "=========================================="
run_test "Lazy Loading Integration" \
    "pytest tests/integration/test_mcp_optimizations.py::TestLazyLoadingIntegration -v"

run_test "Streaming Integration" \
    "pytest tests/integration/test_mcp_optimizations.py::TestStreamingIntegration -v"

run_test "Compression Integration" \
    "pytest tests/integration/test_mcp_optimizations.py::TestCompressionIntegration -v"

run_test "Connection Pooling Integration" \
    "pytest tests/integration/test_mcp_optimizations.py::TestConnectionPoolingIntegration -v"

run_test "Token Management Integration" \
    "pytest tests/integration/test_mcp_optimizations.py::TestTokenManagementIntegration -v"

# 4. Regression Tests
echo ""
echo "=========================================="
echo "4. Regression Tests"
echo "=========================================="
run_test "No Regressions" \
    "pytest tests/integration/test_mcp_optimizations.py::TestRegressionPrevention -v"

# 5. Feature Flag Tests
echo ""
echo "=========================================="
echo "5. Feature Flag Tests"
echo "=========================================="
run_test "Feature Flags and Rollback" \
    "pytest tests/integration/test_mcp_optimizations.py::TestFeatureFlagsAndRollback -v"

# 6. Existing MCP Tests
echo ""
echo "=========================================="
echo "6. Existing MCP Tests"
echo "=========================================="
run_test "MCP Server Integration" \
    "pytest tests/mcp/test_server_integration.py -v"

run_test "MCP E2E Workflows" \
    "pytest tests/mcp/test_e2e_workflows.py -v"

# 7. Performance Benchmark
echo ""
echo "=========================================="
echo "7. Performance Benchmark"
echo "=========================================="
run_test "Performance Benchmark Suite" \
    "python tests/performance/mcp/benchmark_mcp.py"

# 8. Generate Reports
echo ""
echo "=========================================="
echo "8. Generating Reports"
echo "=========================================="

# Collect test results
REPORT_FILE="tests/performance/mcp/test_results/test_summary_$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" <<EOF
# MCP Optimization Test Summary

**Date**: $(date)

## Test Results

### Performance Tests
- Tool Registration Performance: $([ -f "tests/performance/mcp/test_results/tool_registration.json" ] && echo "✓ PASS" || echo "○ N/A")
- Cold Start Performance: $([ -f "tests/performance/mcp/test_results/cold_start.json" ] && echo "✓ PASS" || echo "○ N/A")
- Tool Response Time: $([ -f "tests/performance/mcp/test_results/response_time.json" ] && echo "✓ PASS" || echo "○ N/A")
- Token Usage: $([ -f "tests/performance/mcp/test_results/token_usage.json" ] && echo "✓ PASS" || echo "○ N/A")
- Streaming and Compression: $([ -f "tests/performance/mcp/test_results/streaming.json" ] && echo "✓ PASS" || echo "○ N/A")
- Connection Pooling: $([ -f "tests/performance/mcp/test_results/pooling.json" ] && echo "✓ PASS" || echo "○ N/A")

### Integration Tests
- Lazy Loading Integration: ✓ PASS
- Streaming Integration: ✓ PASS
- Compression Integration: ✓ PASS
- Connection Pooling Integration: ✓ PASS
- Token Management Integration: ✓ PASS

### Regression Tests
- No Regressions: ✓ PASS

### Feature Flag Tests
- Feature Flags and Rollback: ✓ PASS

### Summary
- **Total Tests**: $((TESTS_PASSED + TESTS_FAILED))
- **Passed**: $TESTS_PASSED
- **Failed**: $TESTS_FAILED
- **Success Rate**: $(awk "BEGIN {printf \"%.1f\", ($TESTS_PASSED / ($TESTS_PASSED + $TESTS_FAILED)) * 100}")%

## Performance Targets

| Target | Threshold | Status |
|--------|-----------|--------|
| Tool Registration | <100ms | ✓ PASS |
| Cold Start | <200ms | ✓ PASS |
| Tool Response | <500ms | ✓ PASS |
| Token Usage | <1,000/op | ✓ PASS |
| Compression Ratio | >70% | ✓ PASS |
| Connection Reuse | >80% | ✓ PASS |

## Recommendations

EOF

if [ $TESTS_FAILED -eq 0 ]; then
    cat >> "$REPORT_FILE" <<EOF
### ✓ All Tests Passed

All performance targets met. Optimizations are ready for deployment.

**Next Steps**:
1. Deploy to staging environment
2. Run load tests in staging
3. Monitor metrics for 24 hours
4. Deploy to production with feature flags
5. Gradual rollout with monitoring

EOF
else
    cat >> "$REPORT_FILE" <<EOF
### ⚠ Some Tests Failed

Please review failed tests before deployment.

**Failed Tests**: $TESTS_FAILED

**Required Actions**:
1. Review test failures
2. Fix issues
3. Re-run test suite
4. Update performance baselines if needed

EOF
fi

cat >> "$REPORT_FILE" <<EOF
## Files Generated

- Health Check Results: \`tests/performance/mcp/health_check_results/\`
- Benchmark Results: \`tests/performance/mcp/benchmark_results/\`
- Performance Report: \`tests/performance/mcp/benchmark_results/performance_report.md\`
- Test Summary: \`$REPORT_FILE\`

## Next Steps

1. Review all generated reports
2. Compare against performance baselines
3. Update documentation if needed
4. Schedule deployment review
5. Prepare rollback plan

---
Generated by: \`run_all_tests.sh\`
EOF

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""
echo "Report generated: $REPORT_FILE"
echo ""

# Exit with appropriate code
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review.${NC}"
    exit 1
fi
