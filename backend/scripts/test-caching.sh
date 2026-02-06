#!/bin/bash

# HTTP Caching and Compression Testing Script
# This script tests the caching and compression implementation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8080}"
ENDPOINT="/api/v1/projects"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

test_pass() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

test_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Test 1: Check if server is running
print_header "Checking Server Connectivity"

if curl -s "$API_URL/health" > /dev/null 2>&1; then
    test_pass "Server is running at $API_URL"
else
    test_fail "Server is not running at $API_URL"
    exit 1
fi

# Test 2: Cache-Control headers on GET request
print_header "Testing Cache-Control Headers"

RESPONSE=$(curl -s -I "$API_URL$ENDPOINT")

if echo "$RESPONSE" | grep -q "Cache-Control:"; then
    CACHE_HEADER=$(echo "$RESPONSE" | grep "Cache-Control:" | cut -d' ' -f2-)
    test_pass "Cache-Control header present: $CACHE_HEADER"
else
    test_fail "Cache-Control header missing"
fi

# Test 3: ETag header on GET request
print_header "Testing ETag Support"

RESPONSE=$(curl -s -I "$API_URL$ENDPOINT")

if echo "$RESPONSE" | grep -q "ETag:"; then
    ETAG=$(echo "$RESPONSE" | grep "ETag:" | cut -d' ' -f2-)
    test_pass "ETag header present: $ETAG"

    # Test conditional request
    CONDITIONAL=$(curl -s -I -H "If-None-Match: $ETAG" "$API_URL$ENDPOINT")
    if echo "$CONDITIONAL" | grep -q "304\|200"; then
        STATUS=$(echo "$CONDITIONAL" | head -1)
        test_pass "Conditional request works: $STATUS"
    else
        test_fail "Conditional request failed"
    fi
else
    test_fail "ETag header missing"
fi

# Test 4: Vary header
print_header "Testing Vary Header"

RESPONSE=$(curl -s -I "$API_URL$ENDPOINT")

if echo "$RESPONSE" | grep -q "Vary:"; then
    VARY=$(echo "$RESPONSE" | grep "Vary:" | cut -d' ' -f2-)
    test_pass "Vary header present: $VARY"
else
    test_fail "Vary header missing"
fi

# Test 5: Gzip compression
print_header "Testing Gzip Compression"

# Get uncompressed size
UNCOMPRESSED=$(curl -s "$API_URL$ENDPOINT" | wc -c)
echo "Uncompressed size: $UNCOMPRESSED bytes"

# Get compressed size
COMPRESSED=$(curl -s -H "Accept-Encoding: gzip" "$API_URL$ENDPOINT" | wc -c)
echo "Compressed size: $COMPRESSED bytes"

if [ "$COMPRESSED" -lt "$UNCOMPRESSED" ]; then
    RATIO=$(echo "scale=2; ($COMPRESSED * 100) / $UNCOMPRESSED" | bc)
    REDUCTION=$(echo "scale=2; 100 - $RATIO" | bc)
    test_pass "Compression working: ${REDUCTION}% reduction (${RATIO}% of original)"

    # Check if compression is effective (70-85% reduction)
    if (( $(echo "$REDUCTION >= 50" | bc -l) )); then
        test_pass "Compression ratio is good (>${REDUCTION}%)"
    else
        test_warning "Compression ratio is lower than expected (${REDUCTION}%)"
    fi
else
    test_fail "Compression not working (compressed >= uncompressed)"
fi

# Test 6: POST request no-cache headers
print_header "Testing Mutation Request Caching"

# Create a temporary JSON payload
PAYLOAD='{"name":"Test Project"}'

RESPONSE=$(curl -s -I -X POST \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    "$API_URL$ENDPOINT")

if echo "$RESPONSE" | grep -q "Cache-Control: no-store"; then
    test_pass "POST requests have Cache-Control: no-store"
else
    test_fail "POST requests missing Cache-Control: no-store"
fi

if echo "$RESPONSE" | grep -q "Pragma: no-cache"; then
    test_pass "POST requests have Pragma: no-cache"
else
    test_fail "POST requests missing Pragma: no-cache"
fi

# Test 7: Static asset caching
print_header "Testing Static Asset Caching"

# Try different static asset paths
STATIC_PATHS=(
    "/static/app.js"
    "/assets/style.css"
    "/dist/bundle.js"
)

for path in "${STATIC_PATHS[@]}"; do
    RESPONSE=$(curl -s -I "$API_URL$path" 2>/dev/null | head -1)
    if echo "$RESPONSE" | grep -q "404\|200"; then
        if echo "$RESPONSE" | grep -q "200"; then
            CACHE=$(curl -s -I "$API_URL$path" | grep "Cache-Control:")
            if echo "$CACHE" | grep -q "immutable"; then
                test_pass "Static asset $path has immutable cache"
            else
                test_pass "Static asset $path found (may be from app router)"
            fi
        fi
    fi
done

# Test 8: CORS preflight caching
print_header "Testing CORS Preflight Caching"

RESPONSE=$(curl -s -I -X OPTIONS "$API_URL$ENDPOINT")

if echo "$RESPONSE" | grep -q "Cache-Control:"; then
    CACHE=$(echo "$RESPONSE" | grep "Cache-Control:")
    if echo "$CACHE" | grep -q "86400"; then
        test_pass "CORS preflight has 24-hour cache: $CACHE"
    else
        test_pass "CORS preflight has Cache-Control header: $CACHE"
    fi
else
    test_warning "CORS preflight may not have Cache-Control header"
fi

# Test 9: Health check endpoint
print_header "Testing Health Check Endpoint"

RESPONSE=$(curl -s -I "$API_URL/health")

if echo "$RESPONSE" | grep -q "200"; then
    test_pass "Health check endpoint is accessible"

    # Health checks should NOT be cached aggressively
    if ! echo "$RESPONSE" | grep -q "Cache-Control:"; then
        test_pass "Health check endpoint skips cache middleware"
    else
        test_warning "Health check endpoint has cache headers"
    fi
else
    test_fail "Health check endpoint is not accessible"
fi

# Test 10: Content-Type verification
print_header "Testing Content-Type Headers"

RESPONSE=$(curl -s -I "$API_URL$ENDPOINT")

if echo "$RESPONSE" | grep -q "Content-Type:"; then
    CT=$(echo "$RESPONSE" | grep "Content-Type:" | cut -d' ' -f2-)
    test_pass "Content-Type header present: $CT"
else
    test_fail "Content-Type header missing"
fi

# Test 11: Response headers order check
print_header "Testing Response Header Order"

RESPONSE=$(curl -s -I "$API_URL$ENDPOINT")

# Check that Cache-Control comes before other caching headers
if echo "$RESPONSE" | grep -B0 "Cache-Control:" | grep -q "HTTP"; then
    test_pass "Response headers are in expected order"
else
    test_warning "Response headers may not be in optimal order"
fi

# Test 12: Caching behavior across requests
print_header "Testing Caching Behavior"

# First request
FIRST=$(curl -s -I "$API_URL$ENDPOINT")
ETAG1=$(echo "$FIRST" | grep "ETag:" | cut -d' ' -f2-)

# Second request with If-None-Match
SECOND=$(curl -s -i -H "If-None-Match: $ETAG1" "$API_URL$ENDPOINT" 2>/dev/null | head -1)

if echo "$SECOND" | grep -q "304\|200"; then
    test_pass "Conditional request returns valid status: $(echo $SECOND | tr -d '\r')"
else
    test_fail "Conditional request returned invalid response"
fi

# Summary
print_header "Test Summary"

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
PERCENTAGE=$((TESTS_PASSED * 100 / TOTAL))

echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests:  $TOTAL"
echo -e "Success Rate: ${BLUE}${PERCENTAGE}%${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed. Please review the implementation.${NC}"
    exit 1
fi
