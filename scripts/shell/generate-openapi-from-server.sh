#!/usr/bin/env bash
# Generate OpenAPI specification from running Python FastAPI server
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Output directory
OPENAPI_DIR="$PROJECT_ROOT/openapi"
mkdir -p "$OPENAPI_DIR"

# Configuration
PYTHON_API_URL="${PYTHON_API_URL:-http://localhost:8000}"
GO_API_URL="${GO_API_URL:-http://localhost:8080}"

echo -e "${YELLOW}==> Generating OpenAPI specs from running servers...${NC}"
echo ""

# Function to check if server is running
check_server() {
    local url=$1
    if curl -f -s "$url/health" > /dev/null 2>&1 || curl -f -s "$url/api/v1/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Generate Python API spec
echo -e "${YELLOW}→ Fetching Python API spec from $PYTHON_API_URL...${NC}"
if check_server "$PYTHON_API_URL"; then
    if curl -f -s "$PYTHON_API_URL/openapi.json" -o "$OPENAPI_DIR/python-api.json"; then
        echo -e "${GREEN}  ✓ Python API spec fetched${NC}"

        # Pretty-print if jq is available
        if command -v jq &> /dev/null; then
            jq '.' "$OPENAPI_DIR/python-api.json" > "$OPENAPI_DIR/python-api.json.tmp" && \
                mv "$OPENAPI_DIR/python-api.json.tmp" "$OPENAPI_DIR/python-api.json"

            echo "    Title: $(jq -r '.info.title' "$OPENAPI_DIR/python-api.json")"
            echo "    Version: $(jq -r '.info.version' "$OPENAPI_DIR/python-api.json")"
            echo "    Paths: $(jq '.paths | keys | length' "$OPENAPI_DIR/python-api.json")"
        fi
    else
        echo -e "${RED}  ✗ Failed to fetch Python API spec${NC}"
        echo "    Make sure the Python backend is running at $PYTHON_API_URL"
    fi
else
    echo -e "${YELLOW}  ⊘ Python API server not running at $PYTHON_API_URL${NC}"
    echo "    Start with: overmind start -f Procfile python-backend"
fi
echo ""

# Generate Go API spec
echo -e "${YELLOW}→ Fetching Go API spec from $GO_API_URL...${NC}"
if check_server "$GO_API_URL"; then
    # Try multiple common swagger endpoints
    if curl -f -s "$GO_API_URL/swagger/doc.json" -o "$OPENAPI_DIR/go-api.json" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Go API spec fetched (from /swagger/doc.json)${NC}"
    elif curl -f -s "$GO_API_URL/api/v1/swagger.json" -o "$OPENAPI_DIR/go-api.json" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Go API spec fetched (from /api/v1/swagger.json)${NC}"
    elif curl -f -s "$GO_API_URL/openapi.json" -o "$OPENAPI_DIR/go-api.json" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Go API spec fetched (from /openapi.json)${NC}"
    else
        echo -e "${YELLOW}  ⊘ Go API spec not available${NC}"
        echo "    Ensure swag docs are generated and served"
        echo "    Run: cd backend && swag init"
    fi

    # Pretty-print if successful and jq is available
    if [ -f "$OPENAPI_DIR/go-api.json" ] && command -v jq &> /dev/null; then
        jq '.' "$OPENAPI_DIR/go-api.json" > "$OPENAPI_DIR/go-api.json.tmp" && \
            mv "$OPENAPI_DIR/go-api.json.tmp" "$OPENAPI_DIR/go-api.json"

        echo "    Title: $(jq -r '.info.title' "$OPENAPI_DIR/go-api.json")"
        echo "    Version: $(jq -r '.info.version' "$OPENAPI_DIR/go-api.json")"
        echo "    Paths: $(jq '.paths | keys | length' "$OPENAPI_DIR/go-api.json")"
    fi
else
    echo -e "${YELLOW}  ⊘ Go API server not running at $GO_API_URL${NC}"
    echo "    Start with: overmind start -f Procfile go-backend"
fi
echo ""

# Summary
echo -e "${YELLOW}Summary:${NC}"
if [ -f "$OPENAPI_DIR/python-api.json" ]; then
    echo -e "  ${GREEN}✓${NC} Python API spec: $OPENAPI_DIR/python-api.json"
else
    echo -e "  ${RED}✗${NC} Python API spec not generated"
fi

if [ -f "$OPENAPI_DIR/go-api.json" ]; then
    echo -e "  ${GREEN}✓${NC} Go API spec: $OPENAPI_DIR/go-api.json"
else
    echo -e "  ${RED}✗${NC} Go API spec not generated"
fi
echo ""

if [ -f "$OPENAPI_DIR/python-api.json" ] || [ -f "$OPENAPI_DIR/go-api.json" ]; then
    echo -e "${GREEN}Next steps:${NC}"
    echo "  - Generate TypeScript types: bun run generate:types"
    echo "  - Generate Python clients: bun run generate:client"
    exit 0
else
    echo -e "${RED}No specs generated. Start the API servers first.${NC}"
    exit 1
fi
