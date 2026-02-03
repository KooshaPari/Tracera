#!/bin/bash
#
# Run Provider Contract Tests
# Verifies backend satisfies consumer contracts
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../.." && pwd )"
CONTRACTS_DIR="$PROJECT_ROOT/tests/contracts"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "=================================================="
echo "Running Provider Contract Tests"
echo "=================================================="

# Check if pact files exist
PACT_COUNT=$(find "$CONTRACTS_DIR/pacts" -name "*.json" 2>/dev/null | wc -l)
if [ "$PACT_COUNT" -eq 0 ]; then
    echo "⚠️  No pact files found. Run consumer tests first."
    echo "Run: ./run-consumer-tests.sh"
    exit 1
fi

echo "Found $PACT_COUNT pact file(s) to verify"
echo ""

# Setup test environment
export TEST_DB_HOST="${TEST_DB_HOST:-localhost}"
export TEST_DB_PORT="${TEST_DB_PORT:-5432}"
export TEST_DB_USER="${TEST_DB_USER:-postgres}"
export TEST_DB_PASSWORD="${TEST_DB_PASSWORD:-postgres}"
export TEST_DB_NAME="${TEST_DB_NAME:-tracertm_test}"

echo "Test Database Configuration:"
echo "  Host: $TEST_DB_HOST"
echo "  Port: $TEST_DB_PORT"
echo "  Database: $TEST_DB_NAME"
echo ""

# Run provider tests
cd "$BACKEND_DIR"
echo "Running provider verification tests..."
go test -v ./tests/contracts/provider -timeout 30m

echo ""
echo "=================================================="
echo "✅ Provider contract tests completed successfully"
echo "=================================================="
