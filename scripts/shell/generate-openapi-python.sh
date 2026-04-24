#!/usr/bin/env bash
# Generate OpenAPI specification from Python FastAPI backend
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

echo -e "${YELLOW}==> Generating OpenAPI spec from Python FastAPI backend...${NC}"

# Check if Python virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}Error: Python virtual environment not found at $PROJECT_ROOT/.venv${NC}"
    echo "Run 'uv sync --extra full' first to create the virtual environment"
    exit 1
fi

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Verify required dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${RED}Error: fastapi not found in virtual environment${NC}"
    echo "Run 'uv sync --extra full' to install all dependencies"
    exit 1
fi

# Generate OpenAPI spec using FastAPI's built-in OpenAPI generation
cd "$PROJECT_ROOT"

python3 << 'EOF'
import json
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path.cwd() / "src"))

try:
    from tracertm.api.main import app

    # Get OpenAPI schema
    openapi_schema = app.openapi()

    # Write to file
    output_path = Path("openapi/python-api.json")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)

    print(f"✓ Generated: {output_path}")
    print(f"  Title: {openapi_schema.get('info', {}).get('title', 'N/A')}")
    print(f"  Version: {openapi_schema.get('info', {}).get('version', 'N/A')}")
    print(f"  Paths: {len(openapi_schema.get('paths', {}))}")

except Exception as e:
    print(f"Error generating OpenAPI spec: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

# Check if generation succeeded
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python OpenAPI spec generated successfully${NC}"
    echo "  Output: $OPENAPI_DIR/python-api.json"
else
    echo -e "${RED}✗ Failed to generate Python OpenAPI spec${NC}"
    exit 1
fi
