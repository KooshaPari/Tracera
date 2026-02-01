#!/bin/bash
set -e

# Sync OpenAPI specification from backend
# Usage: ./sync-openapi.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$DOCS_DIR/../../../backend"

echo "📝 Syncing OpenAPI specification..."

# Check if Go is installed
if ! command -v go &> /dev/null; then
  echo "❌ Go is not installed. Cannot generate OpenAPI spec."
  exit 1
fi

# Check if swag is installed
if ! command -v swag &> /dev/null; then
  echo "Installing swag..."
  go install github.com/swaggo/swag/cmd/swag@latest
fi

# Generate OpenAPI spec from backend
if [ ! -d "$BACKEND_DIR" ]; then
  echo "❌ Backend directory not found at: $BACKEND_DIR"
  exit 1
fi

cd "$BACKEND_DIR"
echo "Generating OpenAPI spec from Go backend..."

swag init \
  --generalInfo main.go \
  --dir ./ \
  --output ./docs \
  --parseDependency \
  --parseInternal \
  --parseDepth 2 \
  --instanceName "tracertm"

# Validate the generated spec
if command -v swagger &> /dev/null; then
  echo "Validating OpenAPI spec..."
  swagger validate docs/swagger.json
fi

# Copy to docs public directory
mkdir -p "$DOCS_DIR/public/api"
cp docs/swagger.json "$DOCS_DIR/public/api/openapi.json"
cp docs/swagger.yaml "$DOCS_DIR/public/api/openapi.yaml"

echo "✓ OpenAPI spec synced successfully!"
echo "  - JSON: $DOCS_DIR/public/api/openapi.json"
echo "  - YAML: $DOCS_DIR/public/api/openapi.yaml"
