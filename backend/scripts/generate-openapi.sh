#!/bin/bash

# generate-openapi.sh - Generate OpenAPI specification from Go code annotations
# Usage: ./scripts/generate-openapi.sh [options]
# Options:
#   --validate    Validate the generated spec
#   --deploy      Copy to docs-site after generation
#   --help        Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="${BACKEND_DIR}/docs"
DOCS_SITE_DIR="${BACKEND_DIR}/../docs/public"
OPENAPI_JSON="${DOCS_DIR}/tracertm_swagger.json"
OPENAPI_YAML="${DOCS_DIR}/tracertm_swagger.yaml"

# Parse command line arguments
VALIDATE=false
DEPLOY=false

for arg in "$@"; do
    case $arg in
        --validate)
            VALIDATE=true
            shift
            ;;
        --deploy)
            DEPLOY=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --validate    Validate the generated spec"
            echo "  --deploy      Copy to docs-site after generation"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown argument: $arg${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}=== OpenAPI Spec Generation ===${NC}"
echo ""

# Check if swag is installed
if ! command -v swag &> /dev/null; then
    echo -e "${RED}Error: swag is not installed${NC}"
    echo -e "${YELLOW}Install it with: go install github.com/swaggo/swag/cmd/swag@latest${NC}"
    exit 1
fi

echo -e "${GREEN}✓ swag found: $(swag --version)${NC}"

# Navigate to backend directory
cd "${BACKEND_DIR}"

# Clean old docs
if [ -d "${DOCS_DIR}" ]; then
    echo -e "${YELLOW}Cleaning old documentation...${NC}"
    rm -rf "${DOCS_DIR}"
fi

# Generate documentation
echo -e "${BLUE}Generating OpenAPI specification...${NC}"
swag init \
    --generalInfo main.go \
    --dir ./ \
    --output ./docs \
    --parseDependency \
    --parseInternal \
    --parseDepth 2 \
    --instanceName "tracertm" \
    --markdownFiles ./docs/markdown

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ OpenAPI spec generated successfully${NC}"
else
    echo -e "${RED}✗ Failed to generate OpenAPI spec${NC}"
    exit 1
fi

# Check if files were created
if [ ! -f "${OPENAPI_JSON}" ]; then
    echo -e "${RED}✗ swagger.json not found${NC}"
    exit 1
fi

if [ ! -f "${OPENAPI_YAML}" ]; then
    echo -e "${RED}✗ swagger.yaml not found${NC}"
    exit 1
fi

# Print file sizes
echo ""
echo -e "${GREEN}Generated files:${NC}"
echo "  - swagger.json ($(du -h "${OPENAPI_JSON}" | cut -f1))"
echo "  - swagger.yaml ($(du -h "${OPENAPI_YAML}" | cut -f1))"
echo "  - docs.go"

# Count endpoints
ENDPOINT_COUNT=$(grep -c '"paths"' "${OPENAPI_JSON}" || echo "0")
echo ""
echo -e "${GREEN}Specification stats:${NC}"
echo "  - Endpoints documented: ${ENDPOINT_COUNT}"

# Validate if requested
if [ "$VALIDATE" = true ]; then
    echo ""
    echo -e "${BLUE}Validating OpenAPI specification...${NC}"

    if command -v openapi-generator-cli &> /dev/null; then
        openapi-generator-cli validate -i "${OPENAPI_JSON}"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ OpenAPI spec is valid${NC}"
        else
            echo -e "${RED}✗ OpenAPI spec validation failed${NC}"
            exit 1
        fi
    elif command -v swagger-cli &> /dev/null; then
        swagger-cli validate "${OPENAPI_JSON}"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ OpenAPI spec is valid${NC}"
        else
            echo -e "${RED}✗ OpenAPI spec validation failed${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ No validation tool found (install openapi-generator-cli or swagger-cli)${NC}"
        echo -e "${YELLOW}  npm install -g @openapitools/openapi-generator-cli${NC}"
        echo -e "${YELLOW}  or${NC}"
        echo -e "${YELLOW}  npm install -g @apidevtools/swagger-cli${NC}"
    fi
fi

# Deploy if requested
if [ "$DEPLOY" = true ]; then
    echo ""
    echo -e "${BLUE}Deploying to docs-site...${NC}"

    if [ ! -d "${DOCS_SITE_DIR}" ]; then
        echo -e "${YELLOW}Creating docs-site/public directory...${NC}"
        mkdir -p "${DOCS_SITE_DIR}"
    fi

    cp "${OPENAPI_JSON}" "${DOCS_SITE_DIR}/openapi.json"
    cp "${OPENAPI_YAML}" "${DOCS_SITE_DIR}/openapi.yaml"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Deployed to docs-site/public/${NC}"
        echo "  - openapi.json"
        echo "  - openapi.yaml"
    else
        echo -e "${RED}✗ Failed to deploy to docs-site${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}=== Generation Complete ===${NC}"
echo ""
echo -e "View your API documentation at:"
echo -e "  ${BLUE}http://localhost:8080/swagger/index.html${NC} (when server is running)"
echo ""
echo -e "Or use a standalone viewer:"
echo -e "  ${BLUE}https://editor.swagger.io/${NC}"
echo ""
