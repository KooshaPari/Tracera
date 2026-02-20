#!/bin/bash
# Run CLI Optimization Test Suite
#
# This script runs all CLI optimization tests and generates reports.
# Usage: ./run_cli_optimization_tests.sh [options]
#
# Options:
#   --quick       Run quick tests only (no benchmarks)
#   --benchmarks  Run benchmarks only
#   --full        Run full test suite (default)
#   --report      Generate performance report
#   --baseline    Update performance baselines

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TESTS_DIR="${PROJECT_ROOT}/tests"

# Output files
REPORT_DIR="${SCRIPT_DIR}/reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${REPORT_DIR}/cli_optimization_report_${TIMESTAMP}.md"
BASELINE_FILE="${SCRIPT_DIR}/performance_baselines.json"

# Create report directory
mkdir -p "${REPORT_DIR}"

# Default mode
MODE="full"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            MODE="quick"
            shift
            ;;
        --benchmarks)
            MODE="benchmarks"
            shift
            ;;
        --full)
            MODE="full"
            shift
            ;;
        --report)
            MODE="report"
            shift
            ;;
        --baseline)
            MODE="baseline"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--quick|--benchmarks|--full|--report|--baseline]"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Change to project root
cd "${PROJECT_ROOT}"

# Print banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   TraceRTM CLI Optimization Test Suite                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_info "Mode: ${MODE}"
print_info "Project root: ${PROJECT_ROOT}"
print_info "Tests directory: ${TESTS_DIR}"

# Check dependencies
print_header "Checking Dependencies"

if ! command -v pytest &> /dev/null; then
    print_error "pytest not found. Please install: pip install pytest"
    exit 1
fi
print_success "pytest found"

if ! command -v python &> /dev/null; then
    print_error "python not found"
    exit 1
fi
print_success "python found: $(python --version)"

# Check for pytest plugins
MISSING_PLUGINS=()

if ! python -c "import pytest_benchmark" 2>/dev/null; then
    MISSING_PLUGINS+=("pytest-benchmark")
fi

if ! python -c "import psutil" 2>/dev/null; then
    MISSING_PLUGINS+=("psutil")
fi

if [ ${#MISSING_PLUGINS[@]} -ne 0 ]; then
    print_warning "Missing plugins: ${MISSING_PLUGINS[*]}"
    print_info "Install with: pip install ${MISSING_PLUGINS[*]}"

    read -p "Install missing plugins now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install "${MISSING_PLUGINS[@]}"
        print_success "Plugins installed"
    else
        print_error "Cannot proceed without required plugins"
        exit 1
    fi
fi

# Run tests based on mode
case $MODE in
    quick)
        print_header "Running Quick Tests"

        print_info "Running startup tests..."
        pytest "${TESTS_DIR}/performance/test_cli_startup.py" \
            -v \
            --tb=short \
            -k "not benchmark" \
            || true

        print_info "Running integration tests..."
        pytest "${TESTS_DIR}/integration/test_cli_integration.py" \
            -v \
            --tb=short \
            || true

        print_success "Quick tests completed"
        ;;

    benchmarks)
        print_header "Running Benchmark Tests"

        print_info "Running CLI benchmarks..."
        pytest "${TESTS_DIR}/performance/test_cli_benchmarks.py" \
            -v \
            --benchmark-only \
            --benchmark-autosave \
            --benchmark-save-data \
            || true

        print_success "Benchmark tests completed"
        ;;

    full)
        print_header "Running Full Test Suite"

        # 1. Startup performance tests
        print_info "Phase 1: Startup Performance Tests"
        pytest "${TESTS_DIR}/performance/test_cli_startup.py" \
            -v \
            --tb=short \
            --junit-xml="${REPORT_DIR}/startup_tests.xml" \
            || true

        # 2. Integration tests
        print_info "Phase 2: Integration Tests"
        pytest "${TESTS_DIR}/integration/test_cli_integration.py" \
            -v \
            --tb=short \
            --junit-xml="${REPORT_DIR}/integration_tests.xml" \
            || true

        # 3. Benchmark tests
        print_info "Phase 3: Benchmark Tests"
        pytest "${TESTS_DIR}/performance/test_cli_benchmarks.py" \
            -v \
            --benchmark-only \
            --benchmark-autosave \
            --junit-xml="${REPORT_DIR}/benchmark_tests.xml" \
            || true

        # 4. Existing CLI tests (regression)
        print_info "Phase 4: Regression Tests (Existing CLI Tests)"
        pytest "${TESTS_DIR}/unit/cli/" \
            -v \
            --tb=short \
            -k "not slow" \
            --junit-xml="${REPORT_DIR}/regression_tests.xml" \
            || true

        print_success "Full test suite completed"
        ;;

    baseline)
        print_header "Updating Performance Baselines"

        print_info "Running benchmarks to establish baseline..."
        pytest "${TESTS_DIR}/performance/test_cli_benchmarks.py" \
            -v \
            --benchmark-only \
            --benchmark-autosave \
            --benchmark-save-data

        # Extract benchmark data and update baseline file
        if [ -d ".benchmarks" ]; then
            print_info "Extracting benchmark data..."

            # Find latest benchmark file
            LATEST_BENCHMARK=$(find .benchmarks -name "*.json" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")

            if [ -n "$LATEST_BENCHMARK" ]; then
                print_info "Latest benchmark: ${LATEST_BENCHMARK}"

                # Simple extraction (could be more sophisticated)
                cp "${LATEST_BENCHMARK}" "${BASELINE_FILE}"
                print_success "Baseline updated: ${BASELINE_FILE}"
            else
                print_warning "No benchmark data found"
            fi
        fi

        print_success "Baseline update completed"
        ;;

    report)
        print_header "Generating Performance Report"

        # Check if we have test results
        if [ ! -d "${REPORT_DIR}" ] || [ -z "$(ls -A ${REPORT_DIR}/*.xml 2>/dev/null)" ]; then
            print_warning "No test results found. Running tests first..."
            $0 --full
        fi

        # Generate report
        {
            echo "# CLI Optimization Test Report"
            echo ""
            echo "Generated: $(date)"
            echo ""
            echo "## Summary"
            echo ""

            # Count test results
            if [ -f "${REPORT_DIR}/startup_tests.xml" ]; then
                STARTUP_TESTS=$(grep -o 'tests="[0-9]*"' "${REPORT_DIR}/startup_tests.xml" | head -1 | grep -o '[0-9]*')
                STARTUP_FAILURES=$(grep -o 'failures="[0-9]*"' "${REPORT_DIR}/startup_tests.xml" | head -1 | grep -o '[0-9]*')
                echo "- Startup Tests: ${STARTUP_TESTS} (${STARTUP_FAILURES} failures)"
            fi

            if [ -f "${REPORT_DIR}/integration_tests.xml" ]; then
                INTEGRATION_TESTS=$(grep -o 'tests="[0-9]*"' "${REPORT_DIR}/integration_tests.xml" | head -1 | grep -o '[0-9]*')
                INTEGRATION_FAILURES=$(grep -o 'failures="[0-9]*"' "${REPORT_DIR}/integration_tests.xml" | head -1 | grep -o '[0-9]*')
                echo "- Integration Tests: ${INTEGRATION_TESTS} (${INTEGRATION_FAILURES} failures)"
            fi

            echo ""
            echo "## Performance Targets"
            echo ""
            echo "| Metric | Target | Status |"
            echo "|--------|--------|--------|"
            echo "| Startup Time | < 500ms | ⏱ Check startup_tests.xml |"
            echo "| Memory Usage | < 50MB | 📊 Check startup_tests.xml |"
            echo "| Command Time | < 100ms | ⚡ Check integration_tests.xml |"
            echo ""
            echo "## Benchmark Results"
            echo ""

            if [ -f "${SCRIPT_DIR}/benchmark_results.json" ]; then
                echo "See \`benchmark_results.json\` for detailed metrics."
            else
                echo "No benchmark data available. Run with --benchmarks flag."
            fi

            echo ""
            echo "## Test Files"
            echo ""
            echo "- \`test_cli_startup.py\`: Startup performance tests"
            echo "- \`test_cli_integration.py\`: Integration and functionality tests"
            echo "- \`test_cli_benchmarks.py\`: Detailed benchmarking"
            echo ""
            echo "## Next Steps"
            echo ""
            echo "1. Review failed tests in XML reports"
            echo "2. Check benchmark results against baselines"
            echo "3. Address any performance regressions"
            echo "4. Update documentation if needed"
            echo ""
            echo "## Rollback Plan"
            echo ""
            echo "See \`CLI_OPTIMIZATION_ROLLBACK_PLAN.md\` for detailed rollback procedures."

        } > "${REPORT_FILE}"

        print_success "Report generated: ${REPORT_FILE}"

        # Display report
        if command -v bat &> /dev/null; then
            bat "${REPORT_FILE}"
        elif command -v cat &> /dev/null; then
            cat "${REPORT_FILE}"
        fi
        ;;
esac

# Summary
print_header "Test Run Summary"

print_info "Reports directory: ${REPORT_DIR}"
print_info "Baseline file: ${BASELINE_FILE}"

if [ -f "${REPORT_FILE}" ]; then
    print_info "Report file: ${REPORT_FILE}"
fi

# Check for failures
FAILED=0
if [ -d "${REPORT_DIR}" ]; then
    for xml in "${REPORT_DIR}"/*.xml; do
        if [ -f "$xml" ]; then
            FAILURES=$(grep -o 'failures="[0-9]*"' "$xml" | grep -o '[0-9]*' || echo "0")
            if [ "$FAILURES" -gt 0 ]; then
                FAILED=$((FAILED + FAILURES))
            fi
        fi
    done
fi

echo ""
if [ $FAILED -eq 0 ]; then
    print_success "All tests passed! ✨"
    exit 0
else
    print_error "${FAILED} test(s) failed"
    print_info "Check XML reports in ${REPORT_DIR} for details"
    exit 1
fi
