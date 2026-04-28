#!/bin/bash
# Test runner script for Pheno SDK hexagonal architecture

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Pheno SDK Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${YELLOW}>>> $1${NC}"
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Parse command line arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-true}"

# Run specific test types
case "$TEST_TYPE" in
    "unit")
        print_section "Running Unit Tests"
        pytest tests/unit -v -m unit
        ;;

    "integration")
        print_section "Running Integration Tests"
        pytest tests/integration -v -m integration
        ;;

    "e2e")
        print_section "Running End-to-End Tests"
        pytest tests/e2e -v -m e2e
        ;;

    "domain")
        print_section "Running Domain Layer Tests"
        pytest tests/unit/domain -v -m domain
        ;;

    "application")
        print_section "Running Application Layer Tests"
        pytest tests/unit/application -v -m application
        ;;

    "adapters")
        print_section "Running Adapter Tests"
        pytest tests/integration/adapters -v -m adapters
        ;;

    "fast")
        print_section "Running Fast Tests"
        pytest -v -m fast
        ;;

    "slow")
        print_section "Running Slow Tests"
        pytest -v -m slow
        ;;

    "smoke")
        print_section "Running Smoke Tests"
        pytest -v -m smoke
        ;;

    "all")
        print_section "Running All Tests"

        # Run unit tests
        print_section "1. Unit Tests"
        pytest tests/unit -v -m unit || { print_error "Unit tests failed"; exit 1; }
        print_success "Unit tests passed"

        # Run integration tests
        print_section "2. Integration Tests"
        pytest tests/integration -v -m integration || { print_error "Integration tests failed"; exit 1; }
        print_success "Integration tests passed"

        # Generate coverage report
        if [ "$COVERAGE" = "true" ]; then
            print_section "3. Coverage Report"
            pytest --cov=src/pheno --cov-report=html --cov-report=term-missing --cov-fail-under=90
            print_success "Coverage report generated in htmlcov/"
        fi
        ;;

    "coverage")
        print_section "Running Tests with Coverage"
        pytest --cov=src/pheno --cov-report=html --cov-report=term-missing --cov-report=xml
        print_success "Coverage report generated"
        echo ""
        echo "HTML report: htmlcov/index.html"
        echo "XML report: coverage.xml"
        ;;

    "watch")
        print_section "Running Tests in Watch Mode"
        pytest-watch -- -v
        ;;

    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: $0 [test_type] [coverage]"
        echo ""
        echo "Test types:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  e2e          - Run end-to-end tests only"
        echo "  domain       - Run domain layer tests"
        echo "  application  - Run application layer tests"
        echo "  adapters     - Run adapter tests"
        echo "  fast         - Run fast tests only"
        echo "  slow         - Run slow tests only"
        echo "  smoke        - Run smoke tests only"
        echo "  coverage     - Run tests with coverage report"
        echo "  watch        - Run tests in watch mode"
        echo ""
        echo "Coverage:"
        echo "  true         - Generate coverage report (default)"
        echo "  false        - Skip coverage report"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All tests completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
