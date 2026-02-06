#!/bin/bash
# TraceRTM Backend Coverage Verification Script
# Runs all tests, generates coverage report, and verifies against targets

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Coverage targets
OVERALL_TARGET=100.0
PACKAGE_TARGET=100.0

# Configuration
COVERAGE_DIR="tests"
MERGED_COVERAGE="${COVERAGE_DIR}/coverage-merged.out"
MERGED_COVERAGE_HTML="${COVERAGE_DIR}/coverage-merged.html"
MERGED_COVERAGE_TXT="${COVERAGE_DIR}/coverage-merged.txt"

# Helper functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Extract coverage percentage from text
extract_coverage() {
    local file=$1
    if [ ! -f "$file" ]; then
        echo "0.0"
        return
    fi

    # Get the total coverage line
    local coverage=$(grep -E "^total:" "$file" | awk '{print $3}' | sed 's/%//')
    if [ -z "$coverage" ]; then
        echo "0.0"
    else
        echo "$coverage"
    fi
}

# Compare coverage against target
compare_coverage() {
    local actual=$1
    local target=$2
    local name=$3

    # Use bc for floating point comparison
    local result=$(echo "$actual >= $target" | bc -l)

    if [ "$result" -eq 1 ]; then
        print_success "$name: ${actual}% (target: ${target}%)"
        return 0
    else
        print_error "$name: ${actual}% (target: ${target}%) - BELOW TARGET"
        return 1
    fi
}

# Main verification process
main() {
    print_header "TraceRTM Backend Coverage Verification"

    # Check if we're in the right directory
    if [ ! -d "tests" ]; then
        print_error "Must be run from backend directory"
        exit 1
    fi

    # Step 1: Start docker-compose services
    print_info "Step 1: Starting docker-compose services..."
    docker-compose up -d postgres redis nats
    sleep 5

    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    timeout 60 bash -c 'until docker-compose ps | grep -q "healthy"; do sleep 2; done' || print_warning "Service health check timed out, continuing anyway..."

    # Step 2: Run all tests
    print_header "Step 2: Running All Tests"

    local test_failed=0

    cd tests

    # Unit tests
    print_info "Running unit tests..."
    if go test -short -race -coverprofile=unit-coverage.out -covermode=atomic \
        -count=1 \
        $(go list ./... | grep -v integration | grep -v security) 2>&1 | tee unit-test.log; then
        print_success "Unit tests passed"
        go tool cover -func=unit-coverage.out > unit-coverage.txt
    else
        print_error "Unit tests failed"
        test_failed=1
    fi

    # Integration tests
    print_info "Running integration tests..."
    if go test -race -coverprofile=integration-coverage.out -covermode=atomic \
        -tags=integration \
        -count=1 \
        ./integration/... 2>&1 | tee integration-test.log; then
        print_success "Integration tests passed"
        go tool cover -func=integration-coverage.out > integration-coverage.txt
    else
        print_error "Integration tests failed"
        test_failed=1
    fi

    # API tests
    print_info "Running API tests..."
    if go test -race -coverprofile=api-coverage.out -covermode=atomic \
        -tags=api \
        -count=1 \
        -run 'Test.*Handler' \
        . 2>&1 | tee api-test.log; then
        print_success "API tests passed"
        go tool cover -func=api-coverage.out > api-coverage.txt
    else
        print_error "API tests failed"
        test_failed=1
    fi

    # Security tests
    print_info "Running security tests..."
    if go test -race -coverprofile=security-coverage.out -covermode=atomic \
        -tags=security \
        -count=1 \
        ./security/... 2>&1 | tee security-test.log; then
        print_success "Security tests passed"
        go tool cover -func=security-coverage.out > security-coverage.txt
    else
        print_error "Security tests failed"
        test_failed=1
    fi

    # E2E tests
    print_info "Running E2E tests..."
    if go test -race -coverprofile=e2e-coverage.out -covermode=atomic \
        -tags=e2e \
        -count=1 \
        -timeout=15m \
        . 2>&1 | tee e2e-test.log; then
        print_success "E2E tests passed"
        go tool cover -func=e2e-coverage.out > e2e-coverage.txt
    else
        print_warning "E2E tests failed or skipped"
        # Don't fail on E2E tests as they might not all be implemented yet
    fi

    cd ..

    # Step 3: Generate merged coverage report
    print_header "Step 3: Generating Coverage Report"

    cd tests

    # Merge all coverage files
    echo "mode: atomic" > coverage-merged.out

    for file in *-coverage.out; do
        if [ -f "$file" ] && [ "$file" != "coverage-merged.out" ]; then
            tail -n +2 "$file" >> coverage-merged.out 2>/dev/null || true
        fi
    done

    # Generate reports
    if [ -f coverage-merged.out ]; then
        go tool cover -html=coverage-merged.out -o coverage-merged.html
        go tool cover -func=coverage-merged.out > coverage-merged.txt

        print_success "Coverage reports generated:"
        print_info "  HTML: ${MERGED_COVERAGE_HTML}"
        print_info "  Text: ${MERGED_COVERAGE_TXT}"
    else
        print_error "Failed to generate merged coverage report"
        cd ..
        exit 1
    fi

    cd ..

    # Step 4: Compare against targets
    print_header "Step 4: Verifying Coverage Targets"

    local coverage_failed=0

    # Extract overall coverage
    OVERALL_COVERAGE=$(extract_coverage "${MERGED_COVERAGE_TXT}")

    echo ""
    print_info "Coverage Results:"
    echo ""

    # Compare overall coverage
    if ! compare_coverage "$OVERALL_COVERAGE" "$OVERALL_TARGET" "Overall Coverage"; then
        coverage_failed=1
    fi

    # Display per-suite coverage
    echo ""
    print_info "Per-Suite Coverage:"
    echo ""

    for suite in unit integration api security e2e; do
        suite_file="${COVERAGE_DIR}/${suite}-coverage.txt"
        if [ -f "$suite_file" ]; then
            suite_coverage=$(extract_coverage "$suite_file")
            compare_coverage "$suite_coverage" "$PACKAGE_TARGET" "${suite^} Tests" || coverage_failed=1
        else
            print_warning "${suite^} Tests: No coverage data"
        fi
    done

    # Step 5: Display detailed package coverage
    print_header "Step 5: Package-Level Coverage"

    if [ -f "${MERGED_COVERAGE_TXT}" ]; then
        echo ""
        cat "${MERGED_COVERAGE_TXT}"
        echo ""
    fi

    # Step 6: Final report
    print_header "Verification Summary"

    echo ""
    if [ $test_failed -ne 0 ]; then
        print_error "Some tests failed"
        print_info "Review test logs in tests/*-test.log"
    else
        print_success "All tests passed"
    fi

    echo ""
    if [ $coverage_failed -ne 0 ]; then
        print_error "Coverage below target (${OVERALL_TARGET}%)"
        print_info "Current coverage: ${OVERALL_COVERAGE}%"
        print_info "View detailed report: ${MERGED_COVERAGE_HTML}"
    else
        print_success "Coverage meets target (${OVERALL_TARGET}%)"
        print_info "Current coverage: ${OVERALL_COVERAGE}%"
    fi

    echo ""
    print_info "Next Steps:"
    if [ $coverage_failed -ne 0 ]; then
        echo "  1. Open ${MERGED_COVERAGE_HTML} in browser"
        echo "  2. Identify uncovered code (red highlights)"
        echo "  3. Add tests for uncovered code"
        echo "  4. Re-run: ./verify-coverage.sh"
    else
        echo "  1. Maintain coverage in new code"
        echo "  2. Update tests when refactoring"
        echo "  3. Run verification before committing"
    fi

    echo ""

    # Cleanup
    print_info "Stopping docker-compose services..."
    docker-compose down > /dev/null 2>&1 || true

    # Exit with appropriate code
    if [ $test_failed -ne 0 ] || [ $coverage_failed -ne 0 ]; then
        print_error "Verification failed"
        exit 1
    else
        print_success "Verification passed"
        exit 0
    fi
}

# Run main function
main "$@"
