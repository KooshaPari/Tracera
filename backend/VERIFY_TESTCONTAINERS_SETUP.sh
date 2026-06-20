#!/bin/bash

# Verification script for testcontainers Neo4j setup
# This script verifies that all components are correctly set up

set -e

echo "========================================="
echo "Testcontainers Setup Verification"
echo "========================================="
echo ""

# Check if files exist
echo "Checking files..."
echo ""

FILES=(
    "internal/testutil/neo4j_container.go"
    "internal/testutil/neo4j_helpers.go"
    "internal/testutil/README.md"
    "internal/testutil/INTEGRATION_TESTING_SETUP.md"
    "internal/graph/neo4j_integration_test.go"
    "TESTCONTAINERS_SETUP_COMPLETE.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo "✓ $file ($lines lines)"
    else
        echo "✗ $file (MISSING)"
        exit 1
    fi
done

echo ""
echo "Checking Go build tags..."
echo ""

# Check for build tags
if grep -q "//go:build integration" internal/testutil/neo4j_container.go; then
    echo "✓ neo4j_container.go has integration build tag"
else
    echo "✗ neo4j_container.go missing integration build tag"
    exit 1
fi

if grep -q "//go:build integration" internal/testutil/neo4j_helpers.go; then
    echo "✓ neo4j_helpers.go has integration build tag"
else
    echo "✗ neo4j_helpers.go missing integration build tag"
    exit 1
fi

if grep -q "//go:build integration" internal/graph/neo4j_integration_test.go; then
    echo "✓ neo4j_integration_test.go has integration build tag"
else
    echo "✗ neo4j_integration_test.go missing integration build tag"
    exit 1
fi

echo ""
echo "Checking Go build with integration tag..."
echo ""

# Build with integration tag
if go build -tags integration ./internal/testutil 2>&1 | grep -q "build constraints"; then
    echo "✗ Build with integration tag failed unexpectedly"
    exit 1
fi
echo "✓ Builds successfully with -tags integration"

# Build without integration tag should exclude files
if ! go build ./internal/testutil 2>&1 | grep -q "build constraints exclude"; then
    echo "✗ Build without integration tag should exclude files"
    exit 1
fi
echo "✓ Build without tag correctly excludes integration files"

echo ""
echo "Checking key functions and types..."
echo ""

# Check for key types and functions
if grep -q "type Neo4jContainer struct" internal/testutil/neo4j_container.go; then
    echo "✓ Neo4jContainer type exists"
else
    echo "✗ Neo4jContainer type missing"
    exit 1
fi

if grep -q "func.*StartNeo4jContainer" internal/testutil/neo4j_container.go; then
    echo "✓ StartNeo4jContainer function exists"
else
    echo "✗ StartNeo4jContainer function missing"
    exit 1
fi

if grep -q "type Neo4jTestClient struct" internal/testutil/neo4j_helpers.go; then
    echo "✓ Neo4jTestClient type exists"
else
    echo "✗ Neo4jTestClient type missing"
    exit 1
fi

if grep -q "func.*NewNeo4jTestClient" internal/testutil/neo4j_helpers.go; then
    echo "✓ NewNeo4jTestClient function exists"
else
    echo "✗ NewNeo4jTestClient function missing"
    exit 1
fi

# Check for test functions
if grep -q "func TestNeo4jClient_Connection" internal/graph/neo4j_integration_test.go; then
    echo "✓ TestNeo4jClient_Connection test exists"
else
    echo "✗ TestNeo4jClient_Connection test missing"
    exit 1
fi

if grep -q "func TestNeo4jClient_PathFinding" internal/graph/neo4j_integration_test.go; then
    echo "✓ TestNeo4jClient_PathFinding test exists"
else
    echo "✗ TestNeo4jClient_PathFinding test missing"
    exit 1
fi

echo ""
echo "Counting test functions..."
echo ""

test_count=$(grep -c "^func Test" internal/graph/neo4j_integration_test.go || true)
echo "✓ Found $test_count integration test functions"

if [ "$test_count" -lt 10 ]; then
    echo "✗ Expected at least 10 test functions, found $test_count"
    exit 1
fi

echo ""
echo "========================================="
echo "All Verifications Passed!"
echo "========================================="
echo ""
echo "To run integration tests:"
echo "  go test -tags integration -v ./internal/graph"
echo ""
echo "To run specific test:"
echo "  go test -tags integration -run TestName ./internal/graph"
echo ""
