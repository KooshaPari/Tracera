#!/usr/bin/env bash
# Generate TypeScript types from OpenAPI specifications
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Directories
OPENAPI_DIR="$PROJECT_ROOT/openapi"
FRONTEND_DIR="$PROJECT_ROOT/frontend/apps/web"
OUTPUT_DIR="$FRONTEND_DIR/src/api/generated"

echo -e "${YELLOW}==> Generating TypeScript types from OpenAPI specs...${NC}"

# Check if OpenAPI specs exist
if [ ! -f "$OPENAPI_DIR/python-api.json" ] && [ ! -f "$OPENAPI_DIR/go-api.json" ]; then
    echo -e "${RED}Error: No OpenAPI specs found in $OPENAPI_DIR${NC}"
    echo "Run generate-openapi-python.sh and/or generate-openapi-go.sh first"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Change to frontend directory
cd "$FRONTEND_DIR"

# Check if openapi-typescript is installed
if ! bun pm ls | grep -q "openapi-typescript"; then
    echo -e "${YELLOW}Installing openapi-typescript...${NC}"
    cd "$PROJECT_ROOT/frontend"
    bun add -D openapi-typescript
    cd "$FRONTEND_DIR"
fi

# Generate types from Python API
if [ -f "$OPENAPI_DIR/python-api.json" ]; then
    echo "Generating types from Python API..."
    bunx openapi-typescript "$OPENAPI_DIR/python-api.json" \
        --output "$OUTPUT_DIR/python-api.ts" \
        --export-type \
        --path-params-as-types

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Python API types generated${NC}"
        echo "  Output: $OUTPUT_DIR/python-api.ts"
    else
        echo -e "${RED}✗ Failed to generate Python API types${NC}"
    fi
fi

# Generate types from Go API
if [ -f "$OPENAPI_DIR/go-api.json" ]; then
    echo "Generating types from Go API..."
    bunx openapi-typescript "$OPENAPI_DIR/go-api.json" \
        --output "$OUTPUT_DIR/go-api.ts" \
        --export-type \
        --path-params-as-types

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Go API types generated${NC}"
        echo "  Output: $OUTPUT_DIR/go-api.ts"
    else
        echo -e "${RED}✗ Failed to generate Go API types${NC}"
    fi
fi

# Create index file to export all types
cat > "$OUTPUT_DIR/index.ts" << 'EOF'
/**
 * Auto-generated API types
 * Generated from OpenAPI specifications
 */

export * from './python-api';
export * from './go-api';
EOF

echo -e "${GREEN}✓ TypeScript type generation complete${NC}"
echo "  Import with: import { paths } from '@/api/generated'"
