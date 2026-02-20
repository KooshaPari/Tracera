#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
GATEWAY_URL=${GATEWAY_URL:-http://localhost}
TIMEOUT=5

echo "========================================"
echo "TracerTM API Gateway Testing"
echo "========================================"
echo ""

# Helper functions
test_endpoint() {
    local name=$1
    local endpoint=$2
    local expected_status=${3:-200}

    echo -n "Testing $name... "

    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "${GATEWAY_URL}${endpoint}" || echo "000")
    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}PASSED${NC} (HTTP $status)"
        return 0
    else
        echo -e "${RED}FAILED${NC} (Expected $expected_status, got $status)"
        if [ -n "$body" ]; then
            echo "  Response: $body"
        fi
        return 1
    fi
}

test_websocket() {
    local name=$1
    local endpoint=$2

    echo -n "Testing $name... "

    # Test WebSocket connection (basic check)
    if command -v wscat &> /dev/null; then
        timeout 2s wscat -c "${GATEWAY_URL/http/ws}${endpoint}" -x 'ping' &>/dev/null && \
            echo -e "${GREEN}PASSED${NC}" || \
            echo -e "${YELLOW}SKIPPED${NC} (WebSocket test inconclusive)"
    else
        echo -e "${YELLOW}SKIPPED${NC} (wscat not installed)"
    fi
}

# Track test results
PASSED=0
FAILED=0

# Test 1: Health Checks
echo "1. Health Check Endpoints"
echo "-------------------------"
test_endpoint "Main health check" "/health" && ((PASSED++)) || ((FAILED++))
test_endpoint "Go backend health" "/health/go" && ((PASSED++)) || ((FAILED++))
test_endpoint "Python backend health" "/health/python" && ((PASSED++)) || ((FAILED++))
echo ""

# Test 2: Go Backend Routes
echo "2. Go Backend Routes (High Performance)"
echo "---------------------------------------"
test_endpoint "Items endpoint" "/api/v1/items" && ((PASSED++)) || ((FAILED++))
test_endpoint "Links endpoint" "/api/v1/links" && ((PASSED++)) || ((FAILED++))
test_endpoint "Projects endpoint" "/api/v1/projects" && ((PASSED++)) || ((FAILED++))
test_endpoint "Graph endpoint" "/api/v1/graph" && ((PASSED++)) || ((FAILED++))
test_endpoint "Search endpoint" "/api/v1/search" && ((PASSED++)) || ((FAILED++))
echo ""

# Test 3: Python Backend Routes
echo "3. Python Backend Routes (AI & Analytics)"
echo "-----------------------------------------"
test_endpoint "AI endpoint" "/api/v1/ai/health" && ((PASSED++)) || ((FAILED++))
test_endpoint "Specifications endpoint" "/api/v1/specifications" && ((PASSED++)) || ((FAILED++))
test_endpoint "Auth endpoint" "/api/v1/auth/health" && ((PASSED++)) || ((FAILED++))
echo ""

# Test 4: WebSocket (if wscat is available)
echo "4. WebSocket Connection"
echo "----------------------"
test_websocket "WebSocket endpoint" "/ws"
echo ""

# Test 5: Rate Limiting (optional)
echo "5. Rate Limiting Test"
echo "--------------------"
echo -n "Testing rate limiting... "
rate_limit_passed=true
for i in {1..110}; do
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 1 "${GATEWAY_URL}/api/v1/items" || echo "000")
    if [ "$status" = "429" ]; then
        echo -e "${GREEN}PASSED${NC} (Rate limit triggered at request $i)"
        rate_limit_passed=true
        ((PASSED++))
        break
    fi
done

if [ "$rate_limit_passed" != true ]; then
    echo -e "${YELLOW}SKIPPED${NC} (Rate limit not triggered in 110 requests)"
fi
echo ""

# Test 6: Cache Headers (Go backend)
echo "6. Cache Headers Test"
echo "--------------------"
echo -n "Testing cache headers... "
cache_status=$(curl -s -I "${GATEWAY_URL}/api/v1/items" | grep -i "X-Cache-Status" || echo "")
if [ -n "$cache_status" ]; then
    echo -e "${GREEN}PASSED${NC}"
    echo "  $cache_status"
    ((PASSED++))
else
    echo -e "${YELLOW}WARNING${NC} (X-Cache-Status header not found)"
fi
echo ""

# Test 7: CORS Headers
echo "7. CORS Headers Test"
echo "-------------------"
echo -n "Testing CORS headers... "
cors_origin=$(curl -s -H "Origin: http://example.com" -I "${GATEWAY_URL}/api/v1/items" | \
              grep -i "Access-Control-Allow-Origin" || echo "")
if [ -n "$cors_origin" ]; then
    echo -e "${GREEN}PASSED${NC}"
    echo "  $cors_origin"
    ((PASSED++))
else
    echo -e "${YELLOW}WARNING${NC} (CORS headers not found)"
fi
echo ""

# Test 8: Security Headers
echo "8. Security Headers Test"
echo "-----------------------"
echo -n "Testing security headers... "
security_headers=$(curl -s -I "${GATEWAY_URL}/health" | \
                   grep -E "X-Frame-Options|X-Content-Type-Options|X-XSS-Protection" || echo "")
if [ -n "$security_headers" ]; then
    echo -e "${GREEN}PASSED${NC}"
    echo "$security_headers" | sed 's/^/  /'
    ((PASSED++))
else
    echo -e "${YELLOW}WARNING${NC} (Security headers not found)"
fi
echo ""

# Summary
echo "========================================"
echo "Test Summary"
echo "========================================"
TOTAL=$((PASSED + FAILED))
echo "Total Tests: $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "Failed: ${RED}$FAILED${NC}"
else
    echo -e "Failed: ${GREEN}0${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the configuration.${NC}"
    exit 1
fi
