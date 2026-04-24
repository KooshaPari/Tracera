#!/bin/bash
# Test Rate Limiting Implementation
# ==================================
# Verifies rate limiting is working correctly with the Redis-compatible runtime

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8080}"
REDIS_URL="${REDIS_URL:-redis://localhost:6379}"

echo "========================================="
echo "Rate Limiting Test Suite"
echo "========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check if the Redis-compatible runtime is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}✗ Redis-compatible runtime is not running${NC}"
    echo "  Start it with: bash scripts/shell/redis-if-not-running.sh"
    echo "  Or: make dev"
    exit 1
fi
echo -e "${GREEN}✓ Redis-compatible runtime is running${NC}"

# Check if backend is running
if ! curl -s "${API_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}✗ Backend is not running${NC}"
    echo "  Start backend with: make dev"
    exit 1
fi
echo -e "${GREEN}✓ Backend is running${NC}"

echo ""
echo "========================================="
echo "Test 1: Basic Rate Limiting"
echo "========================================="

# Test API endpoint (100 req/min, burst 10)
echo "Testing /api/v1/items endpoint (100 req/min, burst 10)..."

SUCCESS_COUNT=0
RATE_LIMITED_COUNT=0

for i in {1..15}; do
    RESPONSE=$(curl -s -w "\n%{http_code}" "${API_URL}/api/v1/items" 2>/dev/null || echo "000")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

    if [ "$HTTP_CODE" = "200" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo -e "  Request $i: ${GREEN}200 OK${NC}"
    elif [ "$HTTP_CODE" = "429" ]; then
        RATE_LIMITED_COUNT=$((RATE_LIMITED_COUNT + 1))
        echo -e "  Request $i: ${YELLOW}429 Too Many Requests${NC}"
    else
        echo -e "  Request $i: ${RED}$HTTP_CODE Error${NC}"
    fi

    # Small delay to avoid immediate bursts
    sleep 0.1
done

echo ""
echo "Results:"
echo "  Successful: $SUCCESS_COUNT"
echo "  Rate Limited: $RATE_LIMITED_COUNT"

if [ $SUCCESS_COUNT -ge 10 ] && [ $SUCCESS_COUNT -le 12 ]; then
    echo -e "${GREEN}✓ Test 1 Passed: Burst limit working correctly${NC}"
else
    echo -e "${RED}✗ Test 1 Failed: Expected 10-12 successful requests, got $SUCCESS_COUNT${NC}"
fi

echo ""
echo "========================================="
echo "Test 2: Rate Limit Headers"
echo "========================================="

echo "Checking for X-RateLimit-* headers..."

RESPONSE=$(curl -i -s "${API_URL}/api/v1/items" 2>/dev/null)
LIMIT_HEADER=$(echo "$RESPONSE" | grep -i "X-RateLimit-Limit:" | awk '{print $2}' | tr -d '\r')
REMAINING_HEADER=$(echo "$RESPONSE" | grep -i "X-RateLimit-Remaining:" | awk '{print $2}' | tr -d '\r')
RESET_HEADER=$(echo "$RESPONSE" | grep -i "X-RateLimit-Reset:" | awk '{print $2}' | tr -d '\r')

if [ -n "$LIMIT_HEADER" ] && [ -n "$REMAINING_HEADER" ] && [ -n "$RESET_HEADER" ]; then
    echo -e "${GREEN}✓ Test 2 Passed: Rate limit headers present${NC}"
    echo "  X-RateLimit-Limit: $LIMIT_HEADER"
    echo "  X-RateLimit-Remaining: $REMAINING_HEADER"
    echo "  X-RateLimit-Reset: $RESET_HEADER"
else
    echo -e "${RED}✗ Test 2 Failed: Rate limit headers missing${NC}"
fi

echo ""
echo "========================================="
echo "Test 3: Retry-After Header"
echo "========================================="

echo "Testing Retry-After header on rate limit exceeded..."

# Exhaust the burst limit
for i in {1..12}; do
    curl -s "${API_URL}/api/v1/items" > /dev/null 2>&1
done

# Next request should be rate limited
RESPONSE=$(curl -i -s "${API_URL}/api/v1/items" 2>/dev/null)
RETRY_AFTER=$(echo "$RESPONSE" | grep -i "Retry-After:" | awk '{print $2}' | tr -d '\r')

if [ -n "$RETRY_AFTER" ] && [ "$RETRY_AFTER" -gt 0 ]; then
    echo -e "${GREEN}✓ Test 3 Passed: Retry-After header present${NC}"
    echo "  Retry-After: ${RETRY_AFTER}s"
else
    echo -e "${YELLOW}⚠ Test 3 Warning: Retry-After header not found (may not be rate limited yet)${NC}"
fi

echo ""
echo "========================================="
echo "Test 4: Redis Backend Verification"
echo "========================================="

echo "Checking Redis for rate limit keys..."

# Count rate limit keys
KEY_COUNT=$(redis-cli --scan --pattern "ratelimit:*" 2>/dev/null | wc -l)

if [ "$KEY_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Test 4 Passed: Rate limit keys found in Redis${NC}"
    echo "  Key count: $KEY_COUNT"

    # Show sample keys
    echo "  Sample keys:"
    redis-cli --scan --pattern "ratelimit:*" 2>/dev/null | head -5 | sed 's/^/    /'
else
    echo -e "${YELLOW}⚠ Test 4 Warning: No rate limit keys in Redis${NC}"
    echo "  This might indicate in-memory mode is being used"
fi

echo ""
echo "========================================="
echo "Test 5: Different IP Isolation"
echo "========================================="

echo "Testing rate limit isolation between different IPs..."

# Use X-Forwarded-For header to simulate different IPs
IP1_SUCCESS=0
IP2_SUCCESS=0

for i in {1..12}; do
    RESPONSE=$(curl -s -w "%{http_code}" -H "X-Forwarded-For: 192.168.1.1" "${API_URL}/api/v1/items" 2>/dev/null)
    if [ "$RESPONSE" = "200" ]; then
        IP1_SUCCESS=$((IP1_SUCCESS + 1))
    fi
done

for i in {1..12}; do
    RESPONSE=$(curl -s -w "%{http_code}" -H "X-Forwarded-For: 192.168.1.2" "${API_URL}/api/v1/items" 2>/dev/null)
    if [ "$RESPONSE" = "200" ]; then
        IP2_SUCCESS=$((IP2_SUCCESS + 1))
    fi
done

if [ $IP1_SUCCESS -ge 10 ] && [ $IP2_SUCCESS -ge 10 ]; then
    echo -e "${GREEN}✓ Test 5 Passed: IPs have separate rate limits${NC}"
    echo "  IP 192.168.1.1 successful: $IP1_SUCCESS"
    echo "  IP 192.168.1.2 successful: $IP2_SUCCESS"
else
    echo -e "${RED}✗ Test 5 Failed: IP isolation not working${NC}"
    echo "  IP 192.168.1.1 successful: $IP1_SUCCESS (expected ~10)"
    echo "  IP 192.168.1.2 successful: $IP2_SUCCESS (expected ~10)"
fi

echo ""
echo "========================================="
echo "Test 6: Redis Memory Usage"
echo "========================================="

echo "Checking Redis memory usage..."

MEMORY_USED=$(redis-cli INFO memory 2>/dev/null | grep "used_memory_human:" | cut -d: -f2 | tr -d '\r')
MEMORY_PEAK=$(redis-cli INFO memory 2>/dev/null | grep "used_memory_peak_human:" | cut -d: -f2 | tr -d '\r')

echo "  Current memory: $MEMORY_USED"
echo "  Peak memory: $MEMORY_PEAK"

# Check evicted keys
EVICTED=$(redis-cli INFO stats 2>/dev/null | grep "evicted_keys:" | cut -d: -f2 | tr -d '\r')

if [ "$EVICTED" = "0" ]; then
    echo -e "${GREEN}✓ No keys evicted${NC}"
else
    echo -e "${YELLOW}⚠ $EVICTED keys evicted (consider increasing maxmemory)${NC}"
fi

echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo ""
echo "All tests completed!"
echo ""
echo "Next steps:"
echo "  1. Monitor Redis metrics: http://localhost:3000 (Grafana)"
echo "  2. View rate limit logs: tail -f backend/logs/app.log"
echo "  3. Check Redis keys: redis-cli --scan --pattern 'ratelimit:*'"
echo "  4. Monitor memory: redis-cli INFO memory"
echo ""
echo "For production deployment, see: docs/guides/rate-limiting-deployment.md"
