#!/bin/bash
# Test viewport API endpoints

set -e

# Configuration
API_BASE="${API_BASE:-http://localhost:8080/api/v1}"
PROJECT_ID="${PROJECT_ID:-test-project-id}"

echo "🚀 Testing Viewport API Endpoints"
echo "=================================="
echo "API Base: $API_BASE"
echo "Project ID: $PROJECT_ID"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Get viewport bounds
echo "📍 Test 1: Get Viewport Bounds"
echo "Endpoint: GET $API_BASE/graph/viewport/$PROJECT_ID/bounds"
BOUNDS_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE/graph/viewport/$PROJECT_ID/bounds")
HTTP_CODE=$(echo "$BOUNDS_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$BOUNDS_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Status: 200 OK${NC}"
    echo "Response:"
    echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${RED}✗ Status: $HTTP_CODE${NC}"
    echo "Response: $RESPONSE_BODY"
fi
echo ""

# Test 2: Query viewport with small bounds
echo "📊 Test 2: Query Viewport (Small Bounds)"
echo "Endpoint: POST $API_BASE/graph/viewport/$PROJECT_ID"
VIEWPORT_REQUEST='{
  "viewport": {
    "minX": 0,
    "minY": 0,
    "maxX": 1920,
    "maxY": 1080
  },
  "zoom": 1.0,
  "bufferPx": 500
}'

echo "Request:"
echo "$VIEWPORT_REQUEST" | jq '.'
echo ""

VIEWPORT_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "$API_BASE/graph/viewport/$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d "$VIEWPORT_REQUEST")
HTTP_CODE=$(echo "$VIEWPORT_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$VIEWPORT_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Status: 200 OK${NC}"
    echo "Response Summary:"
    echo "$RESPONSE_BODY" | jq '{
      nodeCount: (.nodes | length),
      edgeCount: (.edges | length),
      hasMore: .hasMore,
      totalCount: .totalCount,
      viewport: .viewport
    }' 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${RED}✗ Status: $HTTP_CODE${NC}"
    echo "Response: $RESPONSE_BODY"
fi
echo ""

# Test 3: Query viewport with large bounds (full graph)
echo "🌍 Test 3: Query Viewport (Large Bounds)"
LARGE_VIEWPORT_REQUEST='{
  "viewport": {
    "minX": -10000,
    "minY": -10000,
    "maxX": 10000,
    "maxY": 10000
  },
  "zoom": 0.1,
  "bufferPx": 1000
}'

echo "Request:"
echo "$LARGE_VIEWPORT_REQUEST" | jq '.'
echo ""

LARGE_VIEWPORT_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "$API_BASE/graph/viewport/$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d "$LARGE_VIEWPORT_REQUEST")
HTTP_CODE=$(echo "$LARGE_VIEWPORT_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$LARGE_VIEWPORT_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Status: 200 OK${NC}"
    echo "Response Summary:"
    echo "$RESPONSE_BODY" | jq '{
      nodeCount: (.nodes | length),
      edgeCount: (.edges | length),
      hasMore: .hasMore,
      totalCount: .totalCount
    }' 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${RED}✗ Status: $HTTP_CODE${NC}"
    echo "Response: $RESPONSE_BODY"
fi
echo ""

# Test 4: Invalid request (missing viewport)
echo "❌ Test 4: Invalid Request (Missing Viewport)"
INVALID_REQUEST='{"zoom": 1.0}'
INVALID_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "$API_BASE/graph/viewport/$PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d "$INVALID_REQUEST")
HTTP_CODE=$(echo "$INVALID_RESPONSE" | tail -1)

if [ "$HTTP_CODE" -eq 400 ]; then
    echo -e "${GREEN}✓ Correctly rejected with 400 Bad Request${NC}"
else
    echo -e "${YELLOW}⚠ Expected 400, got $HTTP_CODE${NC}"
fi
echo ""

echo "=================================="
echo "✅ Viewport API Tests Complete"
echo ""
echo "Summary:"
echo "  - GET bounds endpoint tested"
echo "  - POST viewport query tested"
echo "  - Small and large viewport ranges tested"
echo "  - Invalid request handling tested"
echo ""
echo "Next Steps:"
echo "  1. Verify spatial indexes with: make db-verify-indexes"
echo "  2. Check query performance with: make db-explain-viewport"
echo "  3. Test with real data by creating items with positions"
