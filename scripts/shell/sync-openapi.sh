#!/bin/bash

# sync-openapi.sh - Generate backend OpenAPI spec and sync to frontend
# This ensures type safety across the entire stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
FRONTEND_SPEC_DIR="${PROJECT_ROOT}/frontend/apps/web/public/specs"

echo -e "${BLUE}=== OpenAPI Spec Generation & Sync ===${NC}"
echo ""

# Step 1: Generate backend OpenAPI spec
echo -e "${BLUE}Step 1: Generating backend OpenAPI spec...${NC}"
cd "${BACKEND_DIR}"

if [ ! -f "scripts/shell/generate-openapi.sh" ]; then
    echo -e "${RED}✗ Backend generation script not found${NC}"
    exit 1
fi

bash scripts/shell/generate-openapi.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Backend OpenAPI generation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend spec generated${NC}"
echo ""

# Step 2: Convert Swagger 2.0 to OpenAPI 3.0
echo -e "${BLUE}Step 2: Converting to OpenAPI 3.0...${NC}"
SWAGGER_SPEC="${BACKEND_DIR}/docs/tracertm_swagger.json"
BACKEND_SPEC="${BACKEND_DIR}/docs/openapi.json"

if [ ! -f "${SWAGGER_SPEC}" ]; then
    echo -e "${RED}✗ Generated spec not found at ${SWAGGER_SPEC}${NC}"
    exit 1
fi

# Check if swagger2openapi is installed
if ! command -v swagger2openapi &> /dev/null; then
    echo -e "${YELLOW}Installing swagger2openapi...${NC}"
    bun add -g swagger2openapi
fi

# Convert to OpenAPI 3.0
cd "${BACKEND_DIR}"
swagger2openapi docs/tracertm_swagger.json -o docs/openapi.json 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to convert to OpenAPI 3.0${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Converted to OpenAPI 3.0${NC}"
echo ""

# Step 3: Create frontend specs directory if it doesn't exist
if [ ! -d "${FRONTEND_SPEC_DIR}" ]; then
    echo -e "${YELLOW}Creating frontend specs directory...${NC}"
    mkdir -p "${FRONTEND_SPEC_DIR}"
fi

# Step 3: Sync to frontend
echo -e "${BLUE}Step 3: Syncing to frontend...${NC}"
FRONTEND_SPEC="${FRONTEND_SPEC_DIR}/openapi.json"

# Backup existing frontend spec if it exists
if [ -f "${FRONTEND_SPEC}" ]; then
    BACKUP="${FRONTEND_SPEC}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "${FRONTEND_SPEC}" "${BACKUP}"
    echo -e "${YELLOW}  Backed up existing spec to: ${BACKUP}${NC}"
fi

# Copy backend spec to frontend
cp "${BACKEND_SPEC}" "${FRONTEND_SPEC}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Spec synced to frontend${NC}"
else
    echo -e "${RED}✗ Failed to sync spec to frontend${NC}"
    exit 1
fi

echo ""

# Step 5: Show file sizes and stats
echo -e "${GREEN}File sizes:${NC}"
echo "  Backend:  $(du -h "${BACKEND_SPEC}" | cut -f1) (${BACKEND_SPEC})"
echo "  Frontend: $(du -h "${FRONTEND_SPEC}" | cut -f1) (${FRONTEND_SPEC})"
echo ""

# Step 5: Generate frontend TypeScript types
echo -e "${BLUE}Step 4: Generating frontend TypeScript types...${NC}"
cd "${PROJECT_ROOT}/frontend/apps/web"

if command -v bun &> /dev/null; then
    bun run generate:types
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend types generated${NC}"
    else
        echo -e "${RED}✗ Frontend type generation failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ bun not found, skipping frontend type generation${NC}"
    echo -e "${YELLOW}  Run 'bun run generate:types' in frontend/apps/web manually${NC}"
fi

echo ""
echo -e "${GREEN}=== Sync Complete ===${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Review changes: ${BLUE}git diff frontend/apps/web/src/api/schema.ts${NC}"
echo -e "  2. Test the types: ${BLUE}cd frontend/apps/web && bun run typecheck${NC}"
echo -e "  3. Commit if everything looks good"
echo ""
