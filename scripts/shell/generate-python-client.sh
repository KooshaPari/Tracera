#!/usr/bin/env bash
# Generate Python client from OpenAPI specifications
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
OUTPUT_DIR="$PROJECT_ROOT/src/tracertm/generated"

echo -e "${YELLOW}==> Generating Python clients from OpenAPI specs...${NC}"

# Check if OpenAPI specs exist
if [ ! -f "$OPENAPI_DIR/python-api.json" ] && [ ! -f "$OPENAPI_DIR/go-api.json" ]; then
    echo -e "${RED}Error: No OpenAPI specs found in $OPENAPI_DIR${NC}"
    echo "Run generate-openapi-python.sh and/or generate-openapi-go.sh first"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}Error: Python virtual environment not found${NC}"
    echo "Run 'uv sync' first"
    exit 1
fi

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Check if openapi-python-client is installed
if ! python -c "import openapi_python_client" 2>/dev/null; then
    echo -e "${YELLOW}Installing openapi-python-client...${NC}"
    uv pip install openapi-python-client
fi

# Generate client from Python API
if [ -f "$OPENAPI_DIR/python-api.json" ]; then
    echo "Generating Python client from Python API..."

    # Remove old client if it exists
    rm -rf "$OUTPUT_DIR/python_api_client"

    # Generate client
    openapi-python-client generate \
        --path "$OPENAPI_DIR/python-api.json" \
        --output-path "$OUTPUT_DIR/python_api_client" \
        --overwrite

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Python API client generated${NC}"
        echo "  Output: $OUTPUT_DIR/python_api_client"
    else
        echo -e "${RED}✗ Failed to generate Python API client${NC}"
    fi
fi

# Generate client from Go API
if [ -f "$OPENAPI_DIR/go-api.json" ]; then
    echo "Generating Python client from Go API..."

    # Remove old client if it exists
    rm -rf "$OUTPUT_DIR/go_api_client"

    # Generate client
    openapi-python-client generate \
        --path "$OPENAPI_DIR/go-api.json" \
        --output-path "$OUTPUT_DIR/go_api_client" \
        --overwrite

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Go API client generated${NC}"
        echo "  Output: $OUTPUT_DIR/go_api_client"
    else
        echo -e "${RED}✗ Failed to generate Go API client${NC}"
    fi
fi

# Create __init__.py to make it a package
cat > "$OUTPUT_DIR/__init__.py" << 'EOF'
"""
Auto-generated API clients
Generated from OpenAPI specifications
"""

try:
    from .python_api_client import Client as PythonAPIClient
except ImportError:
    PythonAPIClient = None

try:
    from .go_api_client import Client as GoAPIClient
except ImportError:
    GoAPIClient = None

__all__ = ["PythonAPIClient", "GoAPIClient"]
EOF

echo -e "${GREEN}✓ Python client generation complete${NC}"
echo "  Import with: from tracertm.generated import PythonAPIClient, GoAPIClient"
