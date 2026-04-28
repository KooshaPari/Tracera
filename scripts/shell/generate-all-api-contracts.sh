#!/usr/bin/env bash
# Generate all API contracts (OpenAPI specs, TypeScript types, Python clients)
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TraceRTM API Contract Generation                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Track failures
FAILED=()

# Step 1: Generate OpenAPI specifications
echo -e "${YELLOW}[1/4] Generating OpenAPI specifications...${NC}"
echo ""

# Python API
echo -e "${YELLOW}→ Python FastAPI backend...${NC}"
if "$SCRIPT_DIR/generate-openapi-python.sh"; then
    echo -e "${GREEN}  ✓ Python API spec generated${NC}"
else
    echo -e "${RED}  ✗ Python API spec failed${NC}"
    FAILED+=("Python API spec")
fi
echo ""

# Go API
echo -e "${YELLOW}→ Go Echo backend...${NC}"
if "$SCRIPT_DIR/generate-openapi-go.sh"; then
    echo -e "${GREEN}  ✓ Go API spec generated${NC}"
else
    echo -e "${RED}  ✗ Go API spec failed${NC}"
    FAILED+=("Go API spec")
fi
echo ""

# Gateway merged spec (single contract for external clients)
echo -e "${YELLOW}→ Gateway merged spec...${NC}"
if node "$SCRIPT_DIR/merge-gateway-openapi.js"; then
    echo -e "${GREEN}  ✓ Gateway API spec generated (openapi/gateway-api.json)${NC}"
else
    echo -e "${YELLOW}  ⚠ Gateway merge skipped (run generate:openapi first)${NC}"
fi
echo ""

# Step 2: Generate TypeScript types
echo -e "${YELLOW}[2/4] Generating TypeScript types...${NC}"
if "$SCRIPT_DIR/generate-typescript-types.sh"; then
    echo -e "${GREEN}  ✓ TypeScript types generated${NC}"
else
    echo -e "${RED}  ✗ TypeScript types failed${NC}"
    FAILED+=("TypeScript types")
fi
echo ""

# Step 3: Generate Python clients
echo -e "${YELLOW}[3/4] Generating Python API clients...${NC}"
if "$SCRIPT_DIR/generate-python-client.sh"; then
    echo -e "${GREEN}  ✓ Python clients generated${NC}"
else
    echo -e "${RED}  ✗ Python clients failed${NC}"
    FAILED+=("Python clients")
fi
echo ""

# Step 4: Summary
echo -e "${YELLOW}[4/4] Generation Summary${NC}"
echo ""

if [ ${#FAILED[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All API contracts generated successfully!${NC}"
    echo ""
    echo -e "${BLUE}Generated files:${NC}"
    echo "  OpenAPI specs:"
    echo "    - openapi/python-api.json"
    echo "    - openapi/go-api.json"
    echo "    - openapi/gateway-api.json (gateway-only contract)"
    echo "  TypeScript types:"
    echo "    - frontend/apps/web/src/api/generated/python-api.ts"
    echo "    - frontend/apps/web/src/api/generated/go-api.ts"
    echo "  Python clients:"
    echo "    - src/tracertm/generated/python_api_client/"
    echo "    - src/tracertm/generated/go_api_client/"
    echo ""
    echo -e "${GREEN}Ready to use in your application!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some generations failed:${NC}"
    for item in "${FAILED[@]}"; do
        echo -e "${RED}  - $item${NC}"
    done
    echo ""
    echo "Check the logs above for details"
    exit 1
fi
