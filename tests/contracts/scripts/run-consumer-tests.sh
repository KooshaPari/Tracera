#!/bin/bash
#
# Run Consumer Contract Tests
# Generates pact files from frontend consumer tests
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../.." && pwd )"
CONTRACTS_DIR="$PROJECT_ROOT/tests/contracts"
FRONTEND_DIR="$PROJECT_ROOT/frontend/apps/web"

echo "=================================================="
echo "Running Consumer Contract Tests"
echo "=================================================="

# Clean previous pacts
echo "Cleaning previous pact files..."
rm -rf "$CONTRACTS_DIR/pacts"/*.json
mkdir -p "$CONTRACTS_DIR/pacts"

# Run consumer tests
echo ""
echo "Running consumer tests..."
cd "$FRONTEND_DIR"

# Run all consumer contract tests
bun run vitest run tests/contracts/consumer --reporter=verbose

# Check if pacts were generated
PACT_COUNT=$(find "$CONTRACTS_DIR/pacts" -name "*.json" 2>/dev/null | wc -l)
echo ""
echo "Generated $PACT_COUNT pact file(s)"

if [ "$PACT_COUNT" -eq 0 ]; then
    echo "⚠️  Warning: No pact files generated"
    exit 1
fi

# List generated pacts
echo ""
echo "Generated pact files:"
ls -lh "$CONTRACTS_DIR/pacts"/*.json 2>/dev/null || true

# Validate pact files
echo ""
echo "Validating pact files..."
for pact in "$CONTRACTS_DIR/pacts"/*.json; do
    if [ -f "$pact" ]; then
        echo "  ✓ $(basename "$pact")"
        # Check if valid JSON
        if ! jq empty "$pact" 2>/dev/null; then
            echo "    ✗ Invalid JSON"
            exit 1
        fi
    fi
done

echo ""
echo "=================================================="
echo "✅ Consumer contract tests completed successfully"
echo "=================================================="
