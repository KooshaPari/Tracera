#!/bin/bash

# Bidirectional HTTP Clients - Test Script
# This script verifies the implementation of bidirectional HTTP clients

set -e

echo "🧪 Testing Bidirectional HTTP Clients Implementation"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "  Testing: $1... "
    if eval "$2" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo ""
echo "1️⃣  Checking File Existence"
echo "----------------------------"

run_test "Go Python client exists" "test -f backend/internal/clients/python_client.go"
run_test "Python Go client exists" "test -f src/tracertm/clients/go_client.py"
run_test "Go integration tests exist" "test -f backend/tests/integration/clients/python_integration_test.go"
run_test "Python integration tests exist" "test -f tests/integration/clients/test_go_integration.py"
run_test "Integration env file exists" "test -f .env.integration"
run_test "Documentation exists" "test -f backend/BIDIRECTIONAL_HTTP_CLIENTS.md"

echo ""
echo "2️⃣  Checking Go Code Compilation"
echo "-----------------------------------"

run_test "Go client compiles" "cd backend/internal/clients && go build -o /tmp/test_client ."
run_test "Go config compiles" "cd backend/internal/config && go build -o /tmp/test_config ."
run_test "Go infrastructure compiles" "cd backend/internal/infrastructure && go build -o /tmp/test_infra ."

echo ""
echo "3️⃣  Checking Python Code Syntax"
echo "----------------------------------"

run_test "Python client syntax valid" "python3 -m py_compile src/tracertm/clients/go_client.py"

echo ""
echo "4️⃣  Checking Dependencies"
echo "---------------------------"

run_test "Go retryablehttp installed" "cd backend && go list -m github.com/hashicorp/go-retryablehttp"
run_test "Go gobreaker installed" "cd backend && go list -m github.com/sony/gobreaker"
run_test "Python tenacity in pyproject.toml" "grep -q 'tenacity>=8.2.0' pyproject.toml"

echo ""
echo "5️⃣  Checking Configuration"
echo "----------------------------"

run_test "Config has PythonBackendURL" "grep -q 'PythonBackendURL' backend/internal/config/config.go"
run_test "Config has ServiceToken" "grep -q 'ServiceToken' backend/internal/config/config.go"
run_test "Env example has GO_BACKEND_URL" "grep -q 'GO_BACKEND_URL' backend/.env.example"
run_test "Env example has PYTHON_BACKEND_URL" "grep -q 'PYTHON_BACKEND_URL' backend/.env.example"
run_test "Env example has SERVICE_TOKEN" "grep -q 'SERVICE_TOKEN' backend/.env.example"

echo ""
echo "6️⃣  Checking Infrastructure Integration"
echo "------------------------------------------"

run_test "Infrastructure has PythonClient" "grep -q 'PythonClient.*clients.PythonServiceClient' backend/internal/infrastructure/infrastructure.go"
run_test "Infrastructure imports clients" "grep -q 'github.com/kooshapari/tracertm-backend/internal/clients' backend/internal/infrastructure/infrastructure.go"
run_test "Python main.py has go_client initialization" "grep -q 'GoBackendClient' src/tracertm/api/main.py"

echo ""
echo "7️⃣  Running Go Integration Tests"
echo "-----------------------------------"

if [ -d "backend/tests/integration/clients" ]; then
    cd backend/tests/integration/clients
    if go test -v 2>&1 | tee /tmp/go_test_output.txt; then
        echo -e "  ${GREEN}✓ Go integration tests passed${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "  ${RED}✗ Go integration tests failed${NC}"
        echo "  See /tmp/go_test_output.txt for details"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    cd - > /dev/null
else
    echo -e "  ${YELLOW}⚠ Go test directory not found${NC}"
fi

echo ""
echo "8️⃣  Running Python Integration Tests"
echo "---------------------------------------"

if command -v pytest &> /dev/null; then
    if pytest tests/integration/clients/test_go_integration.py -v 2>&1 | tee /tmp/python_test_output.txt; then
        echo -e "  ${GREEN}✓ Python integration tests passed${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "  ${RED}✗ Python integration tests failed${NC}"
        echo "  See /tmp/python_test_output.txt for details"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "  ${YELLOW}⚠ pytest not installed, skipping Python tests${NC}"
    echo "  Install with: pip install pytest pytest-aiohttp"
fi

echo ""
echo "=================================================="
echo "📊 Test Results Summary"
echo "=================================================="
echo -e "Total Tests:  ${TOTAL_TESTS}"
echo -e "Passed:       ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed:       ${RED}${FAILED_TESTS}${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "📚 Next Steps:"
    echo "  1. Update .env with your backend URLs"
    echo "  2. Start both backends:"
    echo "     - Go:     cd backend && go run main.go"
    echo "     - Python: cd src && uvicorn tracertm.api.main:app --reload --port 8000"
    echo "  3. Test connectivity with health checks"
    echo ""
    echo "📖 Documentation:"
    echo "  - Full Guide:  backend/BIDIRECTIONAL_HTTP_CLIENTS.md"
    echo "  - Quick Start: BIDIRECTIONAL_CLIENTS_QUICK_START.md"
    echo "  - Summary:     BIDIRECTIONAL_CLIENTS_IMPLEMENTATION_SUMMARY.md"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the errors above.${NC}"
    exit 1
fi
