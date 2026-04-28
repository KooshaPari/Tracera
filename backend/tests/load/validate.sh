#!/bin/bash
# Validation script for load testing suite
# Tests that k6 is installed and load tests can run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

section() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "$1"
    echo "═══════════════════════════════════════════════════════════"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

section "Load Testing Suite Validation"

# 1. Check k6 installation
section "1. Checking k6 Installation"

if command -v k6 &> /dev/null; then
    K6_VERSION=$(k6 version 2>&1 | head -n1)
    pass "k6 is installed: $K6_VERSION"
else
    fail "k6 is not installed"
    echo "   Install with: make install-k6"
    echo "   Or visit: https://k6.io/docs/get-started/installation/"
fi

# 2. Check test file exists
section "2. Checking Test Files"

if [ -f "service_load_test.js" ]; then
    pass "service_load_test.js exists"
else
    fail "service_load_test.js not found"
fi

# 3. Validate test file syntax
section "3. Validating Test File Syntax"

if command -v k6 &> /dev/null; then
    if k6 inspect service_load_test.js &> /dev/null; then
        pass "Test file syntax is valid"
    else
        fail "Test file syntax validation failed"
        k6 inspect service_load_test.js
    fi
else
    warn "Skipping syntax check (k6 not installed)"
fi

# 4. Check results directory
section "4. Checking Results Directory"

mkdir -p results
if [ -d "results" ]; then
    pass "Results directory exists"
else
    fail "Could not create results directory"
fi

# 5. Check backend availability
section "5. Checking Backend Server"

BASE_URL="${BASE_URL:-http://localhost:8080}"
echo "Testing: $BASE_URL/health"

if curl -f -s -o /dev/null "$BASE_URL/health" 2>/dev/null; then
    pass "Backend server is accessible at $BASE_URL"

    # Check health response
    HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
    echo "   Response: $HEALTH_RESPONSE"
else
    warn "Backend server is not running at $BASE_URL"
    echo "   This is optional for validation, but required for actual tests"
    echo "   Start backend with: cd ../../ && go run main.go"
fi

# 6. Check documentation
section "6. Checking Documentation"

if [ -f "README.md" ]; then
    pass "README.md exists"
else
    fail "README.md not found"
fi

if [ -f "../../docs/guides/LOAD_TESTING_GUIDE.md" ]; then
    pass "LOAD_TESTING_GUIDE.md exists"
else
    fail "LOAD_TESTING_GUIDE.md not found"
fi

# 7. Test scenario count
section "7. Counting Test Scenarios"

SCENARIO_COUNT=$(grep -c "executor: '" service_load_test.js || echo "0")
if [ "$SCENARIO_COUNT" -ge 6 ]; then
    pass "Found $SCENARIO_COUNT test scenarios"
else
    fail "Expected at least 6 scenarios, found $SCENARIO_COUNT"
fi

# List scenarios
echo ""
echo "Available scenarios:"
grep "executor: '" service_load_test.js | sed 's/^[[:space:]]*/   - /' | sed "s/executor: '//g" | sed "s/',//g" | sort -u

# 8. Dry run test (if k6 available)
section "8. Dry Run Test"

if command -v k6 &> /dev/null; then
    echo "Running dry-run validation..."

    # Create minimal test configuration for validation
    cat > /tmp/k6_validate.js <<'EOF'
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 1,
  duration: '1s',
  thresholds: {},
};

export default function() {
  // Minimal test - just validate script loads
}
EOF

    if k6 run /tmp/k6_validate.js &> /dev/null; then
        pass "Dry-run test passed"
    else
        fail "Dry-run test failed"
    fi

    rm -f /tmp/k6_validate.js
else
    warn "Skipping dry-run (k6 not installed)"
fi

# Summary
section "Validation Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=0
if [ "$TOTAL_TESTS" -gt 0 ]; then
    PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
fi

echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "Total tests:  $TOTAL_TESTS"
echo "Pass rate:    $PASS_RATE%"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Validation successful! Load testing suite is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start backend: cd ../../ && go run main.go"
    echo "  2. Run smoke test: make load-test-smoke"
    echo "  3. Run full suite: make load-test"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}✗ Validation failed. Please fix the issues above.${NC}"
    echo ""
    exit 1
fi
