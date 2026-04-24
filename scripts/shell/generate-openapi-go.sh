#!/usr/bin/env bash
# Generate OpenAPI specification from Go Echo backend using swag
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

echo -e "${YELLOW}==> Generating OpenAPI spec from Go backend...${NC}"

# Check if swag is installed
if ! command -v swag &> /dev/null; then
    echo -e "${YELLOW}swag not found, installing...${NC}"
    go install github.com/swaggo/swag/cmd/swag@latest

    # Verify installation
    if ! command -v swag &> /dev/null; then
        echo -e "${RED}Error: Failed to install swag. Make sure \$GOPATH/bin is in your PATH${NC}"
        echo "Add this to your shell profile:"
        echo "  export PATH=\"\$PATH:\$HOME/go/bin\""
        exit 1
    fi
fi

# Change to backend directory
cd "$PROJECT_ROOT/backend"

# Generate docs using swag
echo "Running swag init..."
swag init \
    --generalInfo main.go \
    --dir . \
    --output docs \
    --parseDependency \
    --parseInternal \
    --parseDepth 3

# Check if swagger.json was generated
if [ ! -f "docs/swagger.json" ]; then
    echo -e "${RED}Error: docs/swagger.json was not generated${NC}"
    exit 1
fi

# Copy to openapi directory
cp docs/swagger.json "$OPENAPI_DIR/go-api.json"

# Pretty-print the spec
if command -v jq &> /dev/null; then
    jq '.' "$OPENAPI_DIR/go-api.json" > "$OPENAPI_DIR/go-api.json.tmp" && \
        mv "$OPENAPI_DIR/go-api.json.tmp" "$OPENAPI_DIR/go-api.json"
fi

echo -e "${GREEN}✓ Go OpenAPI spec generated successfully${NC}"
echo "  Output: $OPENAPI_DIR/go-api.json"

# Display spec info
if command -v jq &> /dev/null; then
    echo "  Title: $(jq -r '.info.title' "$OPENAPI_DIR/go-api.json")"
    echo "  Version: $(jq -r '.info.version' "$OPENAPI_DIR/go-api.json")"
    echo "  Paths: $(jq '.paths | keys | length' "$OPENAPI_DIR/go-api.json")"
fi
