#!/bin/bash

# Chromatic Setup Script
# Initializes Chromatic visual regression testing for TraceRTM

set -e

echo "======================================"
echo "Chromatic Visual Testing Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v bun &> /dev/null; then
	echo -e "${RED}Error: Bun is not installed${NC}"
	echo "Please install Bun: https://bun.sh"
	exit 1
fi

if ! command -v node &> /dev/null; then
	echo -e "${RED}Error: Node.js is not installed${NC}"
	echo "Please install Node.js 20+: https://nodejs.org"
	exit 1
fi

echo -e "${GREEN}✓ Prerequisites met${NC}"
echo ""

# Check if in correct directory
if [ ! -f "package.json" ]; then
	echo -e "${RED}Error: Not in a project directory${NC}"
	echo "Please run this script from frontend/apps/web/"
	exit 1
fi

echo -e "${BLUE}Installing dependencies...${NC}"
bun install
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Build Storybook
echo -e "${BLUE}Building Storybook...${NC}"
bun run storybook:build
echo -e "${GREEN}✓ Storybook built${NC}"
echo ""

# Check for Chromatic token
echo -e "${BLUE}Checking Chromatic configuration...${NC}"

CHROMATIC_TOKEN=${CHROMATIC_PROJECT_TOKEN:-}
CHROMATIC_CONFIG="chromatic.config.json"

if [ -z "$CHROMATIC_TOKEN" ]; then
	echo -e "${YELLOW}No CHROMATIC_PROJECT_TOKEN environment variable found${NC}"
	echo ""
	echo "To set up Chromatic visual testing:"
	echo ""
	echo -e "${BLUE}Step 1: Create Chromatic Account${NC}"
	echo "  1. Go to https://www.chromatic.com"
	echo "  2. Sign in with GitHub"
	echo "  3. Click 'Create Project'"
	echo "  4. Copy your project token (looks like: chroma_xxxxxxxxxxxxx)"
	echo ""
	echo -e "${BLUE}Step 2: Set Environment Variable${NC}"
	echo "  export CHROMATIC_PROJECT_TOKEN=chroma_xxxxxxxxxxxxx"
	echo ""
	echo -e "${BLUE}Step 3: Update chromatic.config.json${NC}"
	echo "  vim chromatic.config.json"
	echo "  # Set projectToken to your token"
	echo ""
	echo -e "${BLUE}Step 4: Run this script again${NC}"
	echo ""
	exit 0
fi

echo -e "${GREEN}✓ CHROMATIC_PROJECT_TOKEN is set${NC}"
echo ""

# Test Chromatic connection
echo -e "${BLUE}Testing Chromatic connection...${NC}"

if bun run chromatic --dry > /dev/null 2>&1; then
	echo -e "${GREEN}✓ Chromatic connection successful${NC}"
else
	echo -e "${RED}✗ Chromatic connection failed${NC}"
	echo "Please check your project token and internet connection"
	exit 1
fi

echo ""
echo -e "${BLUE}Running initial visual tests...${NC}"
bun run chromatic:ci || echo -e "${YELLOW}Note: Some snapshots may need approval${NC}"
echo ""

echo "======================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "======================================"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. View your Storybook locally:"
echo "   bun run storybook"
echo ""
echo "2. Make changes to components and stories"
echo ""
echo "3. Run visual tests:"
echo "   bun run chromatic"
echo ""
echo "4. Review changes at:"
echo "   https://www.chromatic.com/builds"
echo ""
echo "5. For GitHub Actions integration:"
echo "   - Add CHROMATIC_PROJECT_TOKEN as a GitHub secret"
echo "   - Workflow file: .github/workflows/chromatic.yml"
echo ""
echo -e "${YELLOW}Documentation:${NC}"
echo "  Quick Start:     ../../docs/VISUAL_TESTING_QUICK_START.md"
echo "  Full Guide:      ../../docs/VISUAL_TESTING_GUIDE.md"
echo "  Storybook Docs:  .storybook/README.md"
echo ""
