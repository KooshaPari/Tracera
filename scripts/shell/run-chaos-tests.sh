#!/usr/bin/env bash
#
# Chaos Engineering Test Runner
#
# Runs chaos tests with Toxiproxy, manages proxy lifecycle,
# and generates comprehensive reports.

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
TOXIPROXY_SCRIPT="$(dirname "$0")/toxiproxy-setup.sh"
RECOVERY_TARGET="${RECOVERY_TIME_TARGET:-30}"
TEST_DIR="tests/chaos"
REPORT_DIR="chaos-reports"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $*"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."

    # Check if pytest is available
    if ! command -v pytest &> /dev/null; then
        log_error "pytest not found. Please install: pip install pytest"
        exit 1
    fi

    # Check if services are running
    if ! pg_isready -h localhost -p 5432 -q; then
        log_warn "PostgreSQL not running. Starting services..."
        make dev &
        sleep 10
    fi

    log_info "Prerequisites check complete"
}

# Setup Toxiproxy
setup_toxiproxy() {
    log_step "Setting up Toxiproxy..."

    if [ ! -x "$TOXIPROXY_SCRIPT" ]; then
        log_error "Toxiproxy setup script not found: $TOXIPROXY_SCRIPT"
        exit 1
    fi

    # Start Toxiproxy
    "$TOXIPROXY_SCRIPT" start

    # Verify it's running
    if ! curl -sf http://localhost:8474/version &> /dev/null; then
        log_error "Toxiproxy failed to start"
        exit 1
    fi

    local version
    version=$(curl -s http://localhost:8474/version)
    log_info "Toxiproxy running (version: $version)"
}

# Run chaos tests
run_chaos_tests() {
    local test_file="${1:-}"

    log_step "Running chaos tests..."

    mkdir -p "$REPORT_DIR"

    local pytest_args=(
        "$TEST_DIR"
        -v
        --tb=short
        --maxfail=5
        "--junitxml=${REPORT_DIR}/chaos-junit.xml"
        "--html=${REPORT_DIR}/chaos-report.html"
        --self-contained-html
    )

    # If specific test file provided
    if [ -n "$test_file" ]; then
        pytest_args=("${TEST_DIR}/${test_file}" "${pytest_args[@]:1}")
    fi

    # Set environment variables
    export TOXIPROXY_HOST="localhost"
    export TOXIPROXY_PORT="8474"
    export RECOVERY_TIME_TARGET="$RECOVERY_TARGET"

    # Run tests
    if pytest "${pytest_args[@]}"; then
        log_info "✓ All chaos tests passed"
        return 0
    else
        log_error "✗ Some chaos tests failed"
        return 1
    fi
}

# Generate summary report
generate_report() {
    log_step "Generating summary report..."

    local report_file="${REPORT_DIR}/chaos-summary.txt"

    {
        echo "=========================================="
        echo "Chaos Engineering Test Summary"
        echo "=========================================="
        echo "Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
        echo "Recovery Target: ${RECOVERY_TARGET}s"
        echo "=========================================="
        echo ""

        if [ -f "${REPORT_DIR}/chaos-junit.xml" ]; then
            local total failures errors
            total=$(grep -oP 'tests="\K[0-9]+' "${REPORT_DIR}/chaos-junit.xml" | head -1 || echo "0")
            failures=$(grep -oP 'failures="\K[0-9]+' "${REPORT_DIR}/chaos-junit.xml" | head -1 || echo "0")
            errors=$(grep -oP 'errors="\K[0-9]+' "${REPORT_DIR}/chaos-junit.xml" | head -1 || echo "0")
            passed=$((total - failures - errors))

            echo "Test Results:"
            echo "  Total:    $total"
            echo "  Passed:   $passed"
            echo "  Failed:   $failures"
            echo "  Errors:   $errors"
            echo ""

            if [ "$failures" -eq 0 ] && [ "$errors" -eq 0 ]; then
                echo "Status: ✓ ALL TESTS PASSED"
            else
                echo "Status: ✗ TESTS FAILED"
            fi
        else
            echo "No test results found"
        fi

        echo ""
        echo "=========================================="
        echo "Reports generated in: $REPORT_DIR"
        echo "  - JUnit XML: chaos-junit.xml"
        echo "  - HTML Report: chaos-report.html"
        echo "  - Summary: chaos-summary.txt"
        echo "=========================================="
    } | tee "$report_file"

    log_info "Summary report saved to $report_file"
}

# Cleanup
cleanup() {
    log_step "Cleaning up..."

    # Stop Toxiproxy
    "$TOXIPROXY_SCRIPT" stop || true

    # Clean up temporary files
    find /tmp -name "toxiproxy*.tmp" -delete 2>/dev/null || true

    log_info "Cleanup complete"
}

# Main execution
main() {
    local test_file="${1:-}"

    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║      Chaos Engineering Test Runner                ║"
    echo "║      Recovery Target: ${RECOVERY_TARGET}s                       ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""

    # Set up cleanup trap
    trap cleanup EXIT

    check_prerequisites
    setup_toxiproxy
    run_chaos_tests "$test_file"
    generate_report

    echo ""
    log_info "Chaos testing complete!"
    echo ""
}

# Show usage
usage() {
    cat << EOF
Usage: $0 [TEST_FILE]

Runs chaos engineering tests using Toxiproxy.

Arguments:
  TEST_FILE   Optional specific test file to run (e.g., test_network_latency.py)

Environment Variables:
  RECOVERY_TIME_TARGET    Recovery time SLA in seconds (default: 30)

Examples:
  # Run all chaos tests
  $0

  # Run specific test file
  $0 test_network_latency.py

  # Run with custom recovery target
  RECOVERY_TIME_TARGET=20 $0

  # Run and view HTML report
  $0 && open chaos-reports/chaos-report.html
EOF
}

# Parse arguments
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 0
fi

main "$@"
