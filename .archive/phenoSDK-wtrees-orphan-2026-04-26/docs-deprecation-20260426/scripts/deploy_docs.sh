#!/usr/bin/env bash
# Automated documentation deployment script
# Extracts cross-links, generates docs, and deploys to Fumadocs

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Documentation Deployment Pipeline${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Extract cross-links
echo -e "${YELLOW}[1/6] Extracting cross-links...${NC}"
python scripts/extract_cross_links.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Cross-link extraction failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Cross-links extracted${NC}"
echo ""

# Step 2: Validate cross-links
echo -e "${YELLOW}[2/6] Validating cross-links...${NC}"
python scripts/validate_links.py

# Check validation results
if grep -q "❌" docs/CROSS_LINK_VALIDATION.md; then
    echo -e "${RED}❌ Cross-link validation found errors${NC}"
    echo -e "${YELLOW}Review: docs/CROSS_LINK_VALIDATION.md${NC}"

    # Ask user if they want to continue
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ Cross-links validated${NC}"
fi
echo ""

# Step 3: Generate documentation
echo -e "${YELLOW}[3/6] Generating documentation...${NC}"

echo "  - Spec coverage matrix..."
python scripts/generate_spec_coverage.py > /dev/null 2>&1

echo "  - Dependency graphs..."
python scripts/generate_dependency_graph.py > /dev/null 2>&1

echo "  - API reference..."
python scripts/generate_api_reference.py > /dev/null 2>&1

echo "  - Test coverage report..."
python scripts/generate_test_coverage_report.py > /dev/null 2>&1

echo -e "${GREEN}✅ Documentation generated${NC}"
echo ""

# Step 4: Update Fumadocs
echo -e "${YELLOW}[4/6] Updating Fumadocs...${NC}"

# Ensure directories exist
mkdir -p apps/docs/content/docs/api
mkdir -p apps/docs/content/docs/specs
mkdir -p apps/docs/content/docs/testing
mkdir -p apps/docs/content/docs/architecture

# Copy API reference
echo "  - Copying API reference..."
cp docs/API_REFERENCE.md apps/docs/content/docs/api/auto-reference.mdx

# Add frontmatter if missing
if ! grep -q "^---" apps/docs/content/docs/api/auto-reference.mdx; then
    cat > temp.mdx << 'EOF'
---
title: API Reference
description: Auto-generated API reference from module metadata
state: STABLE
tags: [api, reference, auto-generated]
---

EOF
    cat apps/docs/content/docs/api/auto-reference.mdx >> temp.mdx
    mv temp.mdx apps/docs/content/docs/api/auto-reference.mdx
fi

# Copy spec coverage
echo "  - Copying spec coverage..."
cp docs/SPEC_COVERAGE_MATRIX.md apps/docs/content/docs/specs/coverage.mdx

# Copy test coverage
echo "  - Copying test coverage..."
cp docs/TEST_COVERAGE_REPORT.md apps/docs/content/docs/testing/coverage.mdx

# Copy dependency graphs
echo "  - Copying dependency graphs..."
cp docs/DEPENDENCY_GRAPHS.md apps/docs/content/docs/architecture/dependencies.mdx

echo -e "${GREEN}✅ Fumadocs updated${NC}"
echo ""

# Step 5: Build Fumadocs (optional, skip if --no-build flag)
if [[ " $@ " =~ " --no-build " ]]; then
    echo -e "${YELLOW}[5/6] Skipping Fumadocs build (--no-build flag)${NC}"
else
    echo -e "${YELLOW}[5/6] Building Fumadocs...${NC}"
    cd apps/docs

    if command -v npm &> /dev/null; then
        npm run build
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Fumadocs build failed${NC}"
            cd "$PROJECT_ROOT"
            exit 1
        fi
        echo -e "${GREEN}✅ Fumadocs built successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  npm not found, skipping build${NC}"
    fi

    cd "$PROJECT_ROOT"
fi
echo ""

# Step 6: Commit changes (optional, skip if --no-commit flag)
if [[ " $@ " =~ " --no-commit " ]]; then
    echo -e "${YELLOW}[6/6] Skipping git commit (--no-commit flag)${NC}"
else
    echo -e "${YELLOW}[6/6] Committing changes...${NC}"

    # Check if there are changes
    if git diff --quiet docs/ apps/docs/content/; then
        echo -e "${BLUE}ℹ️  No documentation changes to commit${NC}"
    else
        # Show changed files
        echo -e "${BLUE}Changed files:${NC}"
        git diff --name-only docs/ apps/docs/content/ | sed 's/^/  - /'

        # Ask for confirmation
        read -p "Commit these changes? (Y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            git add docs/cross_links.json \
                    docs/SPEC_COVERAGE_MATRIX.md \
                    docs/spec_coverage.json \
                    docs/DEPENDENCY_GRAPHS.md \
                    docs/API_REFERENCE.md \
                    docs/TEST_COVERAGE_REPORT.md \
                    docs/CROSS_LINK_VALIDATION.md \
                    apps/docs/content/docs/

            git commit -m "docs: Auto-update generated documentation

- Updated cross-link database
- Updated spec coverage matrix
- Updated API reference
- Updated test coverage report
- Updated dependency graphs

Generated by: deploy_docs.sh
Date: $(date '+%Y-%m-%d %H:%M:%S')"

            echo -e "${GREEN}✅ Changes committed${NC}"
        else
            echo -e "${YELLOW}⚠️  Skipping commit${NC}"
        fi
    fi
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Cross-links extracted${NC}"
echo -e "${GREEN}✅ Validation complete${NC}"
echo -e "${GREEN}✅ Documentation generated${NC}"
echo -e "${GREEN}✅ Fumadocs updated${NC}"
if [[ ! " $@ " =~ " --no-build " ]]; then
    echo -e "${GREEN}✅ Build complete${NC}"
fi
if [[ ! " $@ " =~ " --no-commit " ]]; then
    echo -e "${GREEN}✅ Changes committed${NC}"
fi
echo ""

echo -e "${BLUE}Generated files:${NC}"
echo -e "  - docs/cross_links.json"
echo -e "  - docs/SPEC_COVERAGE_MATRIX.md"
echo -e "  - docs/DEPENDENCY_GRAPHS.md"
echo -e "  - docs/API_REFERENCE.md"
echo -e "  - docs/TEST_COVERAGE_REPORT.md"
echo -e "  - apps/docs/content/docs/api/auto-reference.mdx"
echo -e "  - apps/docs/content/docs/specs/coverage.mdx"
echo -e "  - apps/docs/content/docs/testing/coverage.mdx"
echo -e "  - apps/docs/content/docs/architecture/dependencies.mdx"
echo ""

echo -e "${GREEN}🎉 Documentation deployment complete!${NC}"
