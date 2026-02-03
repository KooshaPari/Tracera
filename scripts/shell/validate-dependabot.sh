#!/bin/bash

# Validate Dependabot Configuration
# This script checks the Dependabot configuration for common issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPENDABOT_CONFIG="$PROJECT_ROOT/.github/dependabot.yml"

echo "🔍 Validating Dependabot Configuration..."
echo

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if config file exists
if [ ! -f "$DEPENDABOT_CONFIG" ]; then
    echo -e "${RED}❌ Error: dependabot.yml not found at $DEPENDABOT_CONFIG${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Configuration file exists${NC}"

# Validate YAML syntax (requires yq or python)
if command -v yq &> /dev/null; then
    if yq eval '.' "$DEPENDABOT_CONFIG" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ YAML syntax is valid${NC}"
    else
        echo -e "${RED}❌ Invalid YAML syntax${NC}"
        exit 1
    fi
elif command -v python3 &> /dev/null; then
    if python3 -c "import yaml; yaml.safe_load(open('$DEPENDABOT_CONFIG'))" 2>/dev/null; then
        echo -e "${GREEN}✓ YAML syntax is valid${NC}"
    else
        echo -e "${RED}❌ Invalid YAML syntax${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Cannot validate YAML syntax (install yq or python3)${NC}"
fi

# Check directories exist
echo
echo "📁 Checking directories..."

DIRECTORIES=(
    "/frontend"
    "/frontend/apps/web"
    "/frontend/apps/desktop"
    "/"  # Root for Python
    "/cli"
    "/backend"
    "/backend/tests"
    "/backend/tests/integration/clients"
    "/backend/tests/integration/database"
)

for dir in "${DIRECTORIES[@]}"; do
    full_path="$PROJECT_ROOT$dir"
    if [ -d "$full_path" ]; then
        echo -e "${GREEN}✓ Directory exists: $dir${NC}"
    else
        echo -e "${YELLOW}⚠ Directory not found: $dir${NC}"
    fi
done

# Check for package files
echo
echo "📦 Checking package files..."

PACKAGE_FILES=(
    "frontend/package.json:npm"
    "frontend/apps/web/package.json:npm"
    "frontend/apps/desktop/package.json:npm"
    "pyproject.toml:pip"
    "cli/pyproject.toml:pip"
    "backend/go.mod:gomod"
    "backend/tests/go.mod:gomod"
    "backend/tests/integration/clients/go.mod:gomod"
    "backend/tests/integration/database/go.mod:gomod"
    "backend/Dockerfile:docker"
)

for item in "${PACKAGE_FILES[@]}"; do
    IFS=':' read -r file type <<< "$item"
    full_path="$PROJECT_ROOT/$file"
    if [ -f "$full_path" ]; then
        echo -e "${GREEN}✓ $type package file exists: $file${NC}"
    else
        echo -e "${YELLOW}⚠ $type package file not found: $file${NC}"
    fi
done

# Check GitHub Actions workflows
echo
echo "🔧 Checking GitHub Actions..."

if [ -d "$PROJECT_ROOT/.github/workflows" ]; then
    echo -e "${GREEN}✓ Workflows directory exists${NC}"

    workflow_count=$(find "$PROJECT_ROOT/.github/workflows" -name "*.yml" -o -name "*.yaml" | wc -l)
    echo -e "${GREEN}✓ Found $workflow_count workflow files${NC}"

    if [ -f "$PROJECT_ROOT/.github/workflows/dependabot-auto-merge.yml" ]; then
        echo -e "${GREEN}✓ Auto-merge workflow exists${NC}"
    else
        echo -e "${YELLOW}⚠ Auto-merge workflow not found${NC}"
    fi
else
    echo -e "${RED}❌ Workflows directory not found${NC}"
fi

# Check version constraint patterns
echo
echo "🔒 Checking version constraints..."

# Frontend package.json
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    if grep -q '"react":' "$PROJECT_ROOT/frontend/package.json"; then
        version=$(grep '"react":' "$PROJECT_ROOT/frontend/package.json" | head -1)
        echo "  Frontend React version: $version"
    fi
fi

# Python pyproject.toml
if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    if grep -q 'fastapi' "$PROJECT_ROOT/pyproject.toml"; then
        echo -e "${GREEN}✓ Python dependencies found in pyproject.toml${NC}"
    fi
fi

# Go go.mod
if [ -f "$PROJECT_ROOT/backend/go.mod" ]; then
    if grep -q 'github.com/gofiber/fiber' "$PROJECT_ROOT/backend/go.mod"; then
        echo -e "${GREEN}✓ Go dependencies found in go.mod${NC}"
    fi
fi

# Summary
echo
echo "📊 Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count ecosystems in config
if command -v grep &> /dev/null; then
    npm_count=$(grep -c "package-ecosystem: \"npm\"" "$DEPENDABOT_CONFIG" || echo "0")
    pip_count=$(grep -c "package-ecosystem: \"pip\"" "$DEPENDABOT_CONFIG" || echo "0")
    gomod_count=$(grep -c "package-ecosystem: \"gomod\"" "$DEPENDABOT_CONFIG" || echo "0")
    actions_count=$(grep -c "package-ecosystem: \"github-actions\"" "$DEPENDABOT_CONFIG" || echo "0")
    docker_count=$(grep -c "package-ecosystem: \"docker\"" "$DEPENDABOT_CONFIG" || echo "0")

    echo "  npm configurations: $npm_count"
    echo "  pip configurations: $pip_count"
    echo "  gomod configurations: $gomod_count"
    echo "  github-actions configurations: $actions_count"
    echo "  docker configurations: $docker_count"

    total=$((npm_count + pip_count + gomod_count + actions_count + docker_count))
    echo "  Total update configurations: $total"
fi

echo
echo -e "${GREEN}✅ Dependabot configuration validation complete!${NC}"
echo
echo "Next steps:"
echo "  1. Commit the configuration: git add .github/dependabot.yml"
echo "  2. Push to GitHub: git push"
echo "  3. Enable Dependabot in repository settings"
echo "  4. Monitor PRs: gh pr list --author 'dependabot[bot]'"
echo
