#!/bin/bash

# Phase 2 Comprehensive Test Runner
# Runs all Phase 2 feature tests and generates coverage reports

set -e

echo "==================================="
echo "Phase 2 Test Suite Runner"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}WARNING: DATABASE_URL not set. Database integration tests will be skipped.${NC}"
    echo "Set DATABASE_URL to run all tests:"
    echo "  export DATABASE_URL='postgresql://user:pass@localhost:5432/tracertm_test'"
    echo ""
fi

# Create test output directory
mkdir -p test-results/coverage
mkdir -p test-results/reports

echo "==================================="
echo "1. Unit Tests"
echo "==================================="

# Event Sourcing Tests
echo -e "${GREEN}Running Event Sourcing Tests...${NC}"
cd backend
go test -v -race -coverprofile=../test-results/coverage/events.out ./internal/events/... 2>&1 | tee ../test-results/reports/events.log
echo ""

# Graph Tests
echo -e "${GREEN}Running Graph Algorithm Tests...${NC}"
go test -v -race -coverprofile=../test-results/coverage/graph.out ./internal/graph/... 2>&1 | tee ../test-results/reports/graph.log
echo ""

# Search Tests
echo -e "${GREEN}Running Search Tests...${NC}"
go test -v -race -coverprofile=../test-results/coverage/search.out ./internal/search/... 2>&1 | tee ../test-results/reports/search.log
echo ""

# WebSocket Tests
echo -e "${GREEN}Running WebSocket Tests...${NC}"
go test -v -race -coverprofile=../test-results/coverage/websocket.out ./internal/websocket/... 2>&1 | tee ../test-results/reports/websocket.log
echo ""

# Agent Coordination Tests
echo -e "${GREEN}Running Agent Coordination Tests...${NC}"
go test -v -race -coverprofile=../test-results/coverage/agents.out ./internal/agents/... 2>&1 | tee ../test-results/reports/agents.log
echo ""

echo "==================================="
echo "2. Integration Tests"
echo "==================================="

if [ -n "$DATABASE_URL" ]; then
    echo -e "${GREEN}Running Integration Tests...${NC}"
    go test -v -race -coverprofile=../test-results/coverage/integration.out ./tests/... 2>&1 | tee ../test-results/reports/integration.log
    echo ""
else
    echo -e "${YELLOW}Skipping integration tests (DATABASE_URL not set)${NC}"
    echo ""
fi

echo "==================================="
echo "3. Load Tests"
echo "==================================="

if [ -n "$DATABASE_URL" ]; then
    echo -e "${GREEN}Running Load Tests...${NC}"
    go test -v -timeout=30m ./tests/load/... 2>&1 | tee ../test-results/reports/load.log
    echo ""
else
    echo -e "${YELLOW}Skipping load tests (DATABASE_URL not set)${NC}"
    echo ""
fi

echo "==================================="
echo "4. Benchmarks"
echo "==================================="

echo -e "${GREEN}Running Benchmarks...${NC}"
go test -bench=. -benchmem ./internal/events/... ./internal/graph/... ./internal/search/... ./internal/websocket/... ./internal/agents/... 2>&1 | tee ../test-results/reports/benchmarks.log
echo ""

echo "==================================="
echo "5. Coverage Analysis"
echo "==================================="

echo -e "${GREEN}Generating Coverage Reports...${NC}"

# Merge coverage files
echo "mode: set" > ../test-results/coverage/combined.out
grep -h -v "mode: set" ../test-results/coverage/*.out >> ../test-results/coverage/combined.out 2>/dev/null || true

# Generate HTML coverage report
go tool cover -html=../test-results/coverage/combined.out -o ../test-results/coverage/coverage.html

# Calculate coverage percentage
COVERAGE=$(go tool cover -func=../test-results/coverage/combined.out | grep total | awk '{print $3}')
echo ""
echo -e "${GREEN}Total Coverage: $COVERAGE${NC}"
echo ""

# Generate coverage summary
go tool cover -func=../test-results/coverage/combined.out > ../test-results/reports/coverage_summary.txt

echo "Coverage by package:" | tee ../test-results/reports/coverage_by_package.txt
go tool cover -func=../test-results/coverage/combined.out | grep -E "^github.com" | awk '{print $1, $3}' | sort | tee -a ../test-results/reports/coverage_by_package.txt

cd ..

echo ""
echo "==================================="
echo "6. Test Summary"
echo "==================================="

# Count tests
TOTAL_TESTS=$(grep -r "^func Test" backend/internal backend/tests 2>/dev/null | wc -l | xargs)
PASSED_TESTS=$(grep -r "PASS" test-results/reports/*.log 2>/dev/null | grep -c "ok" || echo "0")

echo ""
echo "Test Statistics:"
echo "  Total Test Functions: $TOTAL_TESTS"
echo "  Test Runs Passed: $PASSED_TESTS"
echo "  Total Coverage: $COVERAGE"
echo ""

# Check if we met 80% coverage goal
COVERAGE_NUM=$(echo $COVERAGE | sed 's/%//')
if (( $(echo "$COVERAGE_NUM >= 80" | bc -l) )); then
    echo -e "${GREEN}✓ Coverage goal met (80%+)${NC}"
else
    echo -e "${YELLOW}⚠ Coverage below 80% goal${NC}"
fi

echo ""
echo "==================================="
echo "Test Results Location:"
echo "==================================="
echo "  Coverage Report: test-results/coverage/coverage.html"
echo "  Test Logs: test-results/reports/"
echo "  Coverage Data: test-results/coverage/"
echo ""

echo -e "${GREEN}All tests completed!${NC}"
