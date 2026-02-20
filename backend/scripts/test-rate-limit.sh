#!/bin/bash
# Rate Limiting Test Script
# Tests the rate limiter by sending rapid requests to different endpoints

set -e

BASE_URL="${BASE_URL:-http://localhost:8080}"
HEALTH_ENDPOINT="$BASE_URL/health"
API_ENDPOINT="$BASE_URL/api/v1/projects"

echo "=================================================="
echo "Rate Limiting Test Script"
echo "=================================================="
echo ""
echo "Testing endpoint: $HEALTH_ENDPOINT"
echo "Testing endpoint: $API_ENDPOINT"
echo ""

# Test 1: Health endpoint should never be rate limited (uses skipper)
echo "Test 1: Health endpoint (should never be rate limited)"
echo "Sending 20 rapid requests to /health..."
for i in {1..20}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_ENDPOINT")
    if [ "$response" == "200" ]; then
        echo "  ✓ Request $i: $response OK"
    else
        echo "  ✗ Request $i: $response (unexpected)"
    fi
done
echo ""

# Test 2: API endpoint should be rate limited after exceeding default burst (10 requests)
echo "Test 2: API endpoint (should be rate limited after ~10 requests)"
echo "Sending 15 rapid requests to /api/v1/projects..."
success_count=0
rate_limited_count=0
for i in {1..15}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_ENDPOINT")
    if [ "$response" == "200" ] || [ "$response" == "404" ]; then
        success_count=$((success_count + 1))
        echo "  ✓ Request $i: $response OK (allowed)"
    elif [ "$response" == "429" ]; then
        rate_limited_count=$((rate_limited_count + 1))
        echo "  ⚠ Request $i: $response (rate limited - expected)"
    else
        echo "  ✗ Request $i: $response (unexpected)"
    fi
done
echo ""
echo "Results:"
echo "  Success: $success_count"
echo "  Rate limited: $rate_limited_count"
echo ""

if [ $rate_limited_count -gt 0 ]; then
    echo "✓ Rate limiting is working correctly!"
else
    echo "⚠ Warning: No requests were rate limited. This might be expected if"
    echo "  the server is not running or if limits are very high."
fi
echo ""

# Test 3: Check rate limit headers
echo "Test 3: Rate limit headers"
echo "Checking for rate limit headers in response..."
headers=$(curl -s -I "$API_ENDPOINT")
if echo "$headers" | grep -qi "X-RateLimit-Limit"; then
    echo "  ✓ X-RateLimit-Limit header present"
    echo "    $(echo "$headers" | grep -i "X-RateLimit-Limit")"
else
    echo "  ✗ X-RateLimit-Limit header missing"
fi
if echo "$headers" | grep -qi "X-RateLimit-Remaining"; then
    echo "  ✓ X-RateLimit-Remaining header present"
    echo "    $(echo "$headers" | grep -i "X-RateLimit-Remaining")"
else
    echo "  ✗ X-RateLimit-Remaining header missing"
fi
if echo "$headers" | grep -qi "X-RateLimit-Reset"; then
    echo "  ✓ X-RateLimit-Reset header present"
    echo "    $(echo "$headers" | grep -i "X-RateLimit-Reset")"
else
    echo "  ✗ X-RateLimit-Reset header missing"
fi
echo ""

echo "=================================================="
echo "Rate Limiting Configuration Summary"
echo "=================================================="
echo ""
echo "Backend (Go) Configuration:"
echo "  • Auth endpoints: 5 requests/min (strict, IP-based)"
echo "  • API endpoints: 100 requests/min (moderate)"
echo "  • Static assets: 1000 requests/min (loose)"
echo "  • Health checks: Unlimited (uses skipper)"
echo ""
echo "Gateway (Caddy) Configuration:"
echo "  • Global limit: 100 requests/min per IP"
echo "  • Acts as first line of defense against DDoS"
echo ""
echo "Multi-layer protection ensures both gateway-level"
echo "and application-level rate limiting."
echo ""
