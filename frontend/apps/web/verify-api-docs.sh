#!/bin/bash

# API Documentation Verification Script
# Tests that all API documentation components are properly set up

set -e

echo "========================================="
echo "API Documentation Verification"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Missing: $1"
        ((FAILED++))
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1/"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Missing: $1/"
        ((FAILED++))
    fi
}

# Function to check package installed
check_package() {
    if grep -q "\"$1\"" package.json; then
        echo -e "${GREEN}✓${NC} Package installed: $1"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Package missing: $1"
        ((FAILED++))
    fi
}

# Check directories
echo "Checking directories..."
check_dir "public/specs"
check_dir "src/components/api-docs"
check_dir "src/routes/api-docs"
check_dir "src/routes/api"
echo ""

# Check OpenAPI spec
echo "Checking OpenAPI specification..."
check_file "public/specs/openapi.json"

if [ -f "public/specs/openapi.json" ]; then
    # Validate JSON
    if node -e "JSON.parse(require('fs').readFileSync('public/specs/openapi.json', 'utf8'))" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} OpenAPI spec is valid JSON"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} OpenAPI spec is invalid JSON"
        ((FAILED++))
    fi

    # Check OpenAPI version
    if grep -q '"openapi": "3.1.0"' public/specs/openapi.json; then
        echo -e "${GREEN}✓${NC} OpenAPI version is 3.1.0"
        ((PASSED++))
    else
        echo -e "${YELLOW}!${NC} OpenAPI version might not be 3.1.0"
    fi
fi
echo ""

# Check components
echo "Checking components..."
check_file "src/components/api-docs/swagger-ui-wrapper.tsx"
check_file "src/components/api-docs/redoc-wrapper.tsx"
echo ""

# Check utilities
echo "Checking utilities..."
check_file "src/lib/openapi-utils.ts"
echo ""

# Check routes
echo "Checking routes..."
check_file "src/routes/api-docs.index.tsx"
check_file "src/routes/api-docs.swagger.tsx"
check_file "src/routes/api-docs.redoc.tsx"
check_file "src/routes/api/spec.ts"
check_file "src/routes/api/swagger-config.ts"
check_file "src/routes/api/auth-test.ts"
echo ""

# Check documentation
echo "Checking documentation..."
check_file "API_DOCS_SETUP.md"
check_file "API_DOCS_QUICK_REFERENCE.md"
check_file "API_DOCS_SUMMARY.md"
check_file ".env.api-docs.example"
echo ""

# Check packages
echo "Checking npm packages..."
check_package "swagger-ui-react"
check_package "redoc"
echo ""

# Check for common issues
echo "Checking for common issues..."

# Check if spec has paths
if [ -f "public/specs/openapi.json" ]; then
    if grep -q '"paths"' public/specs/openapi.json; then
        echo -e "${GREEN}✓${NC} OpenAPI spec contains paths"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} OpenAPI spec missing paths"
        ((FAILED++))
    fi

    # Check if spec has info
    if grep -q '"info"' public/specs/openapi.json; then
        echo -e "${GREEN}✓${NC} OpenAPI spec contains info"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} OpenAPI spec missing info"
        ((FAILED++))
    fi
fi
echo ""

# Summary
echo "========================================="
echo "Verification Summary"
echo "========================================="
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start dev server: bun run dev"
    echo "2. Visit: http://localhost:3000/api-docs"
    echo "3. Try Swagger UI: http://localhost:3000/api-docs/swagger"
    echo "4. Try ReDoc: http://localhost:3000/api-docs/redoc"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo ""
    echo "Please review the errors above and:"
    echo "1. Ensure all files are created"
    echo "2. Run: bun add swagger-ui-react redoc"
    echo "3. Check that all files are in the correct locations"
    echo ""
    exit 1
fi
