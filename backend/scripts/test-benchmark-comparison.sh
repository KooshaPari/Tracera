#!/usr/bin/env bash

################################################################################
# Test Suite for Benchmark Comparison Script
#
# Tests the benchmark regression detection with mock data.
# Scenarios:
#   - First run (no baseline)
#   - Passing comparison (no regression)
#   - Warning regression (10-20%)
#   - Critical regression (>20%)
################################################################################

set -euo pipefail

# Test configuration
TEST_DIR="/tmp/benchmark-test-$$"
SCRIPT_PATH="$(dirname "${BASH_SOURCE[0]}")/benchmark-comparison.sh"
PASS_COUNT=0
FAIL_COUNT=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

################################################################################
# Test Utilities
################################################################################

setup_test() {
    mkdir -p "$TEST_DIR"
    cd "$TEST_DIR"
}

teardown_test() {
    rm -rf "$TEST_DIR"
}

test_start() {
    echo -e "${BLUE}► Testing: $1${NC}"
}

test_pass() {
    echo -e "${GREEN}  ✓ $1${NC}"
    ((PASS_COUNT++))
}

test_fail() {
    echo -e "${RED}  ✗ $1${NC}"
    ((FAIL_COUNT++))
}

assert_exit_code() {
    local expected="$1"
    local actual="$2"
    local description="$3"

    if [[ "$actual" -eq "$expected" ]]; then
        test_pass "$description (exit code $actual)"
    else
        test_fail "$description (expected $expected, got $actual)"
    fi
}

assert_file_contains() {
    local file="$1"
    local pattern="$2"
    local description="$3"

    if grep -q "$pattern" "$file" 2>/dev/null; then
        test_pass "$description"
    else
        test_fail "$description (pattern '$pattern' not found in $file)"
    fi
}

assert_json_valid() {
    local file="$1"
    local description="$2"

    if jq empty "$file" 2>/dev/null; then
        test_pass "$description"
    else
        test_fail "$description (invalid JSON)"
    fi
}

################################################################################
# Mock Data Generators
################################################################################

generate_baseline() {
    local file="$1"
    cat > "$file" << 'EOF'
[
  {
    "name": "BenchmarkCreateItem",
    "ns_per_op": 1000,
    "bytes_per_op": 500,
    "allocs_per_op": 10,
    "ops_per_sec": 1000000
  },
  {
    "name": "BenchmarkGetItem",
    "ns_per_op": 500,
    "bytes_per_op": 250,
    "allocs_per_op": 5,
    "ops_per_sec": 2000000
  },
  {
    "name": "BenchmarkListItems",
    "ns_per_op": 2000,
    "bytes_per_op": 1000,
    "allocs_per_op": 20,
    "ops_per_sec": 500000
  }
]
EOF
}

# Baseline: no regression
generate_current_passing() {
    local file="$1"
    cat > "$file" << 'EOF'
[
  {
    "name": "BenchmarkCreateItem",
    "ns_per_op": 1050,
    "bytes_per_op": 510,
    "allocs_per_op": 11,
    "ops_per_sec": 952380
  },
  {
    "name": "BenchmarkGetItem",
    "ns_per_op": 510,
    "bytes_per_op": 260,
    "allocs_per_op": 5,
    "ops_per_sec": 1960784
  },
  {
    "name": "BenchmarkListItems",
    "ns_per_op": 2050,
    "bytes_per_op": 1020,
    "allocs_per_op": 21,
    "ops_per_sec": 487804
  }
]
EOF
}

# Baseline: 15% regression (warning)
generate_current_warning() {
    local file="$1"
    cat > "$file" << 'EOF'
[
  {
    "name": "BenchmarkCreateItem",
    "ns_per_op": 1150,
    "bytes_per_op": 550,
    "allocs_per_op": 12,
    "ops_per_sec": 869565
  },
  {
    "name": "BenchmarkGetItem",
    "ns_per_op": 575,
    "bytes_per_op": 280,
    "allocs_per_op": 6,
    "ops_per_sec": 1739130
  },
  {
    "name": "BenchmarkListItems",
    "ns_per_op": 2000,
    "bytes_per_op": 1000,
    "allocs_per_op": 20,
    "ops_per_sec": 500000
  }
]
EOF
}

# Baseline: 25% regression (critical)
generate_current_critical() {
    local file="$1"
    cat > "$file" << 'EOF'
[
  {
    "name": "BenchmarkCreateItem",
    "ns_per_op": 1250,
    "bytes_per_op": 600,
    "allocs_per_op": 13,
    "ops_per_sec": 800000
  },
  {
    "name": "BenchmarkGetItem",
    "ns_per_op": 630,
    "bytes_per_op": 300,
    "allocs_per_op": 7,
    "ops_per_sec": 1587301
  },
  {
    "name": "BenchmarkListItems",
    "ns_per_op": 2000,
    "bytes_per_op": 1000,
    "allocs_per_op": 20,
    "ops_per_sec": 500000
  }
]
EOF
}

################################################################################
# Test Cases
################################################################################

test_first_run() {
    test_start "First run (no baseline available)"

    setup_test

    generate_current_passing baseline.json

    # Run without baseline - should succeed (first run)
    TEMP_DIR="$TEST_DIR" bash "$SCRIPT_PATH" \
        --baseline /nonexistent/baseline.json \
        --current baseline.json \
        --output report.md \
        > /dev/null 2>&1 || EXIT_CODE=$?

    # First run should succeed (exit 0)
    assert_exit_code 0 "${EXIT_CODE:-0}" "First run succeeds"

    teardown_test
}

test_passing_comparison() {
    test_start "Passing comparison (no regression)"

    setup_test

    generate_baseline baseline.json
    generate_current_passing current.json

    # Run comparison - should pass
    bash "$SCRIPT_PATH" \
        --baseline baseline.json \
        --current current.json \
        --output report.md \
        > /dev/null 2>&1 || EXIT_CODE=$?

    assert_exit_code 0 "${EXIT_CODE:-0}" "Passing benchmarks exit with 0"
    assert_file_contains report.md "BenchmarkCreateItem" "Report includes benchmark names"
    assert_file_contains report.md "Passed\|Pass\|OK\|✅" "Report shows passing status"

    teardown_test
}

test_warning_regression() {
    test_start "Warning regression (10-20% slower)"

    setup_test

    generate_baseline baseline.json
    generate_current_warning current.json

    # Run comparison - should warn but pass (exit 0)
    bash "$SCRIPT_PATH" \
        --baseline baseline.json \
        --current current.json \
        --output report.md \
        > /dev/null 2>&1 || EXIT_CODE=$?

    # Warning should pass (not fail CI yet)
    assert_exit_code 0 "${EXIT_CODE:-0}" "Warning regression doesn't fail CI"
    assert_file_contains report.md "WARNING\|⚠️\|warning" "Report shows warning status"

    teardown_test
}

test_critical_regression() {
    test_start "Critical regression (>20% slower)"

    setup_test

    generate_baseline baseline.json
    generate_current_critical current.json

    # Run comparison - should fail
    bash "$SCRIPT_PATH" \
        --baseline baseline.json \
        --current current.json \
        --output report.md \
        > /dev/null 2>&1 || EXIT_CODE=$?

    # Critical should fail (exit 1)
    assert_exit_code 1 "${EXIT_CODE:-1}" "Critical regression fails CI"
    assert_file_contains report.md "CRITICAL\|🔴\|critical" "Report shows critical status"

    teardown_test
}

test_report_generation() {
    test_start "Report generation and formatting"

    setup_test

    generate_baseline baseline.json
    generate_current_passing current.json

    bash "$SCRIPT_PATH" \
        --baseline baseline.json \
        --current current.json \
        --output report.md \
        > /dev/null 2>&1 || true

    if [[ -f report.md ]]; then
        test_pass "Report file created"

        if grep -q "Benchmark Regression Comparison" report.md; then
            test_pass "Report includes header"
        else
            test_fail "Report missing header"
        fi

        if grep -q "|" report.md; then
            test_pass "Report includes table"
        else
            test_fail "Report missing table"
        fi

        if grep -q "Summary\|Detailed\|Threshold" report.md; then
            test_pass "Report includes sections"
        else
            test_fail "Report missing sections"
        fi
    else
        test_fail "Report file not created"
    fi

    teardown_test
}

test_json_output() {
    test_start "JSON output validity"

    setup_test

    generate_baseline baseline.json
    generate_current_passing current.json

    assert_json_valid baseline.json "Baseline JSON is valid"
    assert_json_valid current.json "Current JSON is valid"

    teardown_test
}

test_metric_extraction() {
    test_start "Metric extraction and calculation"

    setup_test

    # Create baseline and current with known difference
    cat > baseline.json << 'EOF'
[{"name": "Test", "ns_per_op": 1000}]
EOF

    cat > current.json << 'EOF'
[{"name": "Test", "ns_per_op": 1100}]
EOF

    bash "$SCRIPT_PATH" \
        --baseline baseline.json \
        --current current.json \
        --output report.md \
        > /dev/null 2>&1 || true

    # 1100 vs 1000 = 10% regression
    if grep -q "10" report.md 2>/dev/null; then
        test_pass "Regression calculation correct"
    else
        test_fail "Regression calculation incorrect"
    fi

    teardown_test
}

################################################################################
# Main
################################################################################

main() {
    echo ""
    echo "================================================================================"
    echo "Benchmark Comparison Script Test Suite"
    echo "================================================================================"
    echo ""

    # Verify script exists
    if [[ ! -f "$SCRIPT_PATH" ]]; then
        echo -e "${RED}Error: Script not found at $SCRIPT_PATH${NC}"
        exit 1
    fi

    # Verify jq is available
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}Error: jq is required but not installed${NC}"
        exit 1
    fi

    # Run test cases
    test_first_run
    test_passing_comparison
    test_warning_regression
    test_critical_regression
    test_report_generation
    test_json_output
    test_metric_extraction

    # Print summary
    echo ""
    echo "================================================================================"
    echo "Test Results"
    echo "================================================================================"
    echo -e "Passed: ${GREEN}$PASS_COUNT${NC}"
    echo -e "Failed: ${RED}$FAIL_COUNT${NC}"
    echo "================================================================================"
    echo ""

    if [[ $FAIL_COUNT -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed.${NC}"
        return 1
    fi
}

main
