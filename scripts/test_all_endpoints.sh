#!/bin/bash
# Test all TraceRTM API endpoints

set -e

BASE_URL="http://localhost:8080"
PASSED=0
FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -n "Testing $description... "
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [[ $http_code =~ ^[2] ]]; then
        echo -e "${GREEN}✅ $http_code${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ $http_code${NC}"
        ((FAILED++))
    fi
}

echo "🚀 TraceRTM API Endpoint Testing"
echo "=================================="
echo ""

# Health Check
echo "📋 Health & System Endpoints"
test_endpoint "GET" "/health" "" "Health check"

# Projects
echo ""
echo "📋 Project Endpoints"
test_endpoint "GET" "/api/projects" "" "List projects"
test_endpoint "POST" "/api/projects" '{"name":"Test Project"}' "Create project"

# Items
echo ""
echo "📋 Item Endpoints"
test_endpoint "GET" "/api/items" "" "List items"

# Links
echo ""
echo "📋 Link Endpoints"
test_endpoint "GET" "/api/links" "" "List links"

# Agents
echo ""
echo "📋 Agent Endpoints"
test_endpoint "GET" "/api/agents" "" "List agents"

# Search
echo ""
echo "📋 Search Endpoints"
test_endpoint "GET" "/api/search/full-text?q=test" "" "Full-text search"
test_endpoint "GET" "/api/search/vector?q=test" "" "Vector search"

# Graph
echo ""
echo "📋 Graph Endpoints"
test_endpoint "GET" "/api/graph/ancestors" "" "Get ancestors"
test_endpoint "GET" "/api/graph/descendants" "" "Get descendants"

echo ""
echo "=================================="
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo "=================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi

