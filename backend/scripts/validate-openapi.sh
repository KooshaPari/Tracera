#!/bin/bash

# validate-openapi.sh - Validate OpenAPI specification
# Usage: ./scripts/validate-openapi.sh [spec-file]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC_FILE="${1:-${BACKEND_DIR}/docs/swagger.json}"

echo -e "${BLUE}=== OpenAPI Spec Validation ===${NC}"
echo ""

# Check if spec file exists
if [ ! -f "${SPEC_FILE}" ]; then
    echo -e "${RED}Error: Spec file not found: ${SPEC_FILE}${NC}"
    echo -e "${YELLOW}Run 'make gen-docs' first to generate the spec${NC}"
    exit 1
fi

echo -e "${GREEN}Validating: ${SPEC_FILE}${NC}"
echo ""

# Validation results
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0

# 1. JSON Syntax Validation
echo -e "${BLUE}[1/5] Checking JSON syntax...${NC}"
if jq empty "${SPEC_FILE}" 2>/dev/null; then
    echo -e "${GREEN}✓ Valid JSON syntax${NC}"
else
    echo -e "${RED}✗ Invalid JSON syntax${NC}"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi
echo ""

# 2. Check required OpenAPI fields
echo -e "${BLUE}[2/5] Checking required OpenAPI fields...${NC}"

# Check openapi version
if jq -e '.openapi' "${SPEC_FILE}" > /dev/null 2>&1; then
    VERSION=$(jq -r '.openapi' "${SPEC_FILE}")
    echo -e "${GREEN}✓ OpenAPI version: ${VERSION}${NC}"
else
    echo -e "${RED}✗ Missing 'openapi' field${NC}"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

# Check info
if jq -e '.info.title' "${SPEC_FILE}" > /dev/null 2>&1; then
    TITLE=$(jq -r '.info.title' "${SPEC_FILE}")
    echo -e "${GREEN}✓ Title: ${TITLE}${NC}"
else
    echo -e "${RED}✗ Missing 'info.title' field${NC}"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

if jq -e '.info.version' "${SPEC_FILE}" > /dev/null 2>&1; then
    API_VERSION=$(jq -r '.info.version' "${SPEC_FILE}")
    echo -e "${GREEN}✓ Version: ${API_VERSION}${NC}"
else
    echo -e "${RED}✗ Missing 'info.version' field${NC}"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

# Check paths
if jq -e '.paths' "${SPEC_FILE}" > /dev/null 2>&1; then
    PATH_COUNT=$(jq '.paths | length' "${SPEC_FILE}")
    echo -e "${GREEN}✓ Paths defined: ${PATH_COUNT}${NC}"

    if [ "${PATH_COUNT}" -eq 0 ]; then
        echo -e "${YELLOW}⚠ Warning: No paths defined${NC}"
        VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
    fi
else
    echo -e "${RED}✗ Missing 'paths' field${NC}"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

echo ""

# 3. Validate with external tools
echo -e "${BLUE}[3/5] Validating with external tools...${NC}"

TOOL_FOUND=false

# Try openapi-generator-cli
if command -v openapi-generator-cli &> /dev/null; then
    echo -e "${BLUE}Using openapi-generator-cli...${NC}"
    if openapi-generator-cli validate -i "${SPEC_FILE}" 2>&1 | grep -q "Spec is valid"; then
        echo -e "${GREEN}✓ openapi-generator-cli validation passed${NC}"
    else
        echo -e "${RED}✗ openapi-generator-cli validation failed${NC}"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
    TOOL_FOUND=true
fi

# Try swagger-cli
if command -v swagger-cli &> /dev/null; then
    echo -e "${BLUE}Using swagger-cli...${NC}"
    if swagger-cli validate "${SPEC_FILE}" 2>&1; then
        echo -e "${GREEN}✓ swagger-cli validation passed${NC}"
    else
        echo -e "${RED}✗ swagger-cli validation failed${NC}"
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    fi
    TOOL_FOUND=true
fi

# Try spectral (if installed)
if command -v spectral &> /dev/null; then
    echo -e "${BLUE}Using spectral linter...${NC}"
    if spectral lint "${SPEC_FILE}" --format stylish; then
        echo -e "${GREEN}✓ spectral linting passed${NC}"
    else
        echo -e "${YELLOW}⚠ spectral linting found issues${NC}"
        VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
    fi
    TOOL_FOUND=true
fi

if [ "$TOOL_FOUND" = false ]; then
    echo -e "${YELLOW}⚠ No external validation tools found${NC}"
    echo -e "${YELLOW}Install one of:${NC}"
    echo -e "  - npm install -g @openapitools/openapi-generator-cli"
    echo -e "  - npm install -g @apidevtools/swagger-cli"
    echo -e "  - npm install -g @stoplight/spectral-cli"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
fi

echo ""

# 4. Check for common issues
echo -e "${BLUE}[4/5] Checking for common issues...${NC}"

# Check for endpoints without operationId
MISSING_OPERATION_IDS=$(jq '[.paths[][].operationId] | map(select(. == null)) | length' "${SPEC_FILE}")
if [ "${MISSING_OPERATION_IDS}" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warning: ${MISSING_OPERATION_IDS} endpoints missing operationId${NC}"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
else
    echo -e "${GREEN}✓ All endpoints have operationId${NC}"
fi

# Check for endpoints without tags
MISSING_TAGS=$(jq '[.paths[][].tags] | map(select(. == null or length == 0)) | length' "${SPEC_FILE}")
if [ "${MISSING_TAGS}" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warning: ${MISSING_TAGS} endpoints missing tags${NC}"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
else
    echo -e "${GREEN}✓ All endpoints have tags${NC}"
fi

# Check for endpoints without descriptions
MISSING_DESCRIPTIONS=$(jq '[.paths[][].description] | map(select(. == null or . == "")) | length' "${SPEC_FILE}")
if [ "${MISSING_DESCRIPTIONS}" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warning: ${MISSING_DESCRIPTIONS} endpoints missing descriptions${NC}"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
else
    echo -e "${GREEN}✓ All endpoints have descriptions${NC}"
fi

# Check for responses without descriptions
RESPONSES_WITHOUT_DESC=$(jq '[.paths[][].responses | to_entries[] | select(.value.description == null or .value.description == "")] | length' "${SPEC_FILE}")
if [ "${RESPONSES_WITHOUT_DESC}" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warning: ${RESPONSES_WITHOUT_DESC} responses missing descriptions${NC}"
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
else
    echo -e "${GREEN}✓ All responses have descriptions${NC}"
fi

echo ""

# 5. Generate statistics
echo -e "${BLUE}[5/5] Generating statistics...${NC}"

# Count different HTTP methods
GET_COUNT=$(jq '[.paths[].get] | map(select(. != null)) | length' "${SPEC_FILE}")
POST_COUNT=$(jq '[.paths[].post] | map(select(. != null)) | length' "${SPEC_FILE}")
PUT_COUNT=$(jq '[.paths[].put] | map(select(. != null)) | length' "${SPEC_FILE}")
PATCH_COUNT=$(jq '[.paths[].patch] | map(select(. != null)) | length' "${SPEC_FILE}")
DELETE_COUNT=$(jq '[.paths[].delete] | map(select(. != null)) | length' "${SPEC_FILE}")

echo "Endpoints by method:"
echo "  - GET:    ${GET_COUNT}"
echo "  - POST:   ${POST_COUNT}"
echo "  - PUT:    ${PUT_COUNT}"
echo "  - PATCH:  ${PATCH_COUNT}"
echo "  - DELETE: ${DELETE_COUNT}"

# Count tags
TAG_COUNT=$(jq '[.tags[]?.name] | length' "${SPEC_FILE}")
echo ""
echo "Tags defined: ${TAG_COUNT}"

# Count schemas
SCHEMA_COUNT=$(jq '[.components.schemas | keys[]] | length' "${SPEC_FILE}" 2>/dev/null || echo "0")
echo "Schemas defined: ${SCHEMA_COUNT}"

# Security schemes
SECURITY_COUNT=$(jq '[.components.securitySchemes | keys[]] | length' "${SPEC_FILE}" 2>/dev/null || echo "0")
echo "Security schemes: ${SECURITY_COUNT}"

echo ""
echo -e "${BLUE}=== Validation Summary ===${NC}"
echo ""

if [ ${VALIDATION_ERRORS} -eq 0 ] && [ ${VALIDATION_WARNINGS} -eq 0 ]; then
    echo -e "${GREEN}✓ All validations passed!${NC}"
    exit 0
elif [ ${VALIDATION_ERRORS} -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation passed with ${VALIDATION_WARNINGS} warning(s)${NC}"
    exit 0
else
    echo -e "${RED}✗ Validation failed with ${VALIDATION_ERRORS} error(s) and ${VALIDATION_WARNINGS} warning(s)${NC}"
    exit 1
fi
