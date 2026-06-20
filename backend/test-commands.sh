#!/bin/bash
# TraceRTM Backend Test Commands
# Provides convenient commands for running different test suites

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Test functions
test_unit() {
    print_header "Running Unit Tests"
    cd tests
    go test -v -short -race -coverprofile=unit-coverage.out -covermode=atomic \
        -count=1 \
        $(go list ./... | grep -v integration | grep -v security) || return 1

    go tool cover -func=unit-coverage.out
    print_success "Unit tests completed"
    cd ..
}

test_integration() {
    print_header "Running Integration Tests"

    # Check if docker-compose services are running
    if ! docker-compose ps | grep -q "Up"; then
        print_info "Starting docker-compose services..."
        docker-compose up -d postgres redis nats

        # Wait for services to be healthy
        print_info "Waiting for services to be healthy..."
        sleep 5
    fi

    cd tests
    go test -v -race -coverprofile=integration-coverage.out -covermode=atomic \
        -tags=integration \
        -count=1 \
        ./integration/... || return 1

    go tool cover -func=integration-coverage.out
    print_success "Integration tests completed"
    cd ..
}

test_api() {
    print_header "Running API Tests"

    # Check if postgres is running
    if ! docker-compose ps postgres | grep -q "Up"; then
        print_info "Starting PostgreSQL..."
        docker-compose up -d postgres
        sleep 3
    fi

    cd tests
    go test -v -race -coverprofile=api-coverage.out -covermode=atomic \
        -tags=api \
        -count=1 \
        -run 'Test.*Handler' \
        . || return 1

    go tool cover -func=api-coverage.out
    print_success "API tests completed"
    cd ..
}

test_e2e() {
    print_header "Running E2E Tests"

    # Start all services
    print_info "Starting all docker-compose services..."
    docker-compose up -d

    # Wait for services
    print_info "Waiting for services to be healthy..."
    sleep 10

    cd tests
    go test -v -race -coverprofile=e2e-coverage.out -covermode=atomic \
        -tags=e2e \
        -count=1 \
        -timeout=15m \
        . || return 1

    go tool cover -func=e2e-coverage.out
    print_success "E2E tests completed"
    cd ..
}

test_security() {
    print_header "Running Security Tests"
    cd tests
    go test -v -race -coverprofile=security-coverage.out -covermode=atomic \
        -tags=security \
        -count=1 \
        ./security/... || return 1

    go tool cover -func=security-coverage.out
    print_success "Security tests completed"
    cd ..
}

test_all() {
    print_header "Running All Tests"

    # Start all services
    print_info "Starting all docker-compose services..."
    docker-compose up -d
    sleep 10

    local failed=0

    # Run all test suites
    test_unit || failed=$((failed + 1))
    test_integration || failed=$((failed + 1))
    test_api || failed=$((failed + 1))
    test_security || failed=$((failed + 1))
    test_e2e || failed=$((failed + 1))

    if [ $failed -eq 0 ]; then
        print_success "All test suites passed!"
        return 0
    else
        print_error "$failed test suite(s) failed"
        return 1
    fi
}

coverage_report() {
    print_header "Generating Coverage Report"

    cd tests

    # Merge all coverage files
    echo "mode: atomic" > coverage-merged.out

    for file in *-coverage.out; do
        if [ -f "$file" ]; then
            tail -n +2 "$file" >> coverage-merged.out
        fi
    done

    # Generate HTML report
    go tool cover -html=coverage-merged.out -o coverage-merged.html

    # Generate text report
    go tool cover -func=coverage-merged.out > coverage-merged.txt

    print_success "Coverage reports generated:"
    print_info "  HTML: tests/coverage-merged.html"
    print_info "  Text: tests/coverage-merged.txt"

    # Display summary
    echo ""
    tail -1 coverage-merged.txt

    cd ..
}

coverage_summary() {
    print_header "Coverage Summary"

    cd tests

    if [ ! -f coverage-merged.txt ]; then
        print_info "Generating coverage report first..."
        coverage_report
        return
    fi

    echo ""
    cat coverage-merged.txt

    cd ..
}

clean_coverage() {
    print_header "Cleaning Coverage Files"
    cd tests
    rm -f *-coverage.out *-coverage.html *-coverage.txt
    print_success "Coverage files cleaned"
    cd ..
}

show_help() {
    cat <<EOF
TraceRTM Backend Test Commands

Usage: ./test-commands.sh [command]

Commands:
  unit              Run unit tests with coverage
  integration       Run integration tests with docker-compose
  api               Run API tests with database
  e2e               Run E2E tests with full docker-compose setup
  security          Run security tests
  all               Run all tests with coverage
  coverage-report   Generate merged HTML coverage report
  coverage-summary  Show coverage summary
  clean             Clean coverage files
  help              Show this help message

Examples:
  ./test-commands.sh unit
  ./test-commands.sh integration
  ./test-commands.sh all
  ./test-commands.sh coverage-report

Environment Variables:
  DB_HOST           Database host (default: localhost)
  DB_PORT           Database port (default: 5432)
  DB_USER           Database user (default: tracertm)
  DB_PASSWORD       Database password (default: tracertm_password)
  DB_NAME           Database name (default: tracertm)
  REDIS_URL         Redis URL (default: redis://localhost:6379)
  NATS_URL          NATS URL (default: nats://localhost:4222)

EOF
}

# Main command dispatcher
main() {
    case "${1:-help}" in
        unit)
            test_unit
            ;;
        integration)
            test_integration
            ;;
        api)
            test_api
            ;;
        e2e)
            test_e2e
            ;;
        security)
            test_security
            ;;
        all)
            test_all
            ;;
        coverage-report)
            coverage_report
            ;;
        coverage-summary)
            coverage_summary
            ;;
        clean)
            clean_coverage
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
