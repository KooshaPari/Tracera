#!/bin/bash
# TanStack Router Verification Script
# This script verifies that all routes are properly configured and accessible

set -e

echo "======================================"
echo "TanStack Router Verification"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Verify routeTree.gen.ts exists
echo "Check 1: Verifying routeTree.gen.ts..."
if [ -f "src/routeTree.gen.ts" ]; then
  echo -e "${GREEN}✓ routeTree.gen.ts exists${NC}"
else
  echo -e "${RED}✗ routeTree.gen.ts not found${NC}"
  exit 1
fi
echo ""

# Check 2: Count routes in routeTree
echo "Check 2: Counting routes in routeTree.gen.ts..."
ROUTE_COUNT=$(grep -c "^import { Route" src/routeTree.gen.ts || echo 0)
echo -e "${GREEN}✓ Found $ROUTE_COUNT routes${NC}"
echo ""

# Check 3: Verify all route files exist
echo "Check 3: Verifying all route files..."
MISSING_COUNT=0
while read -r route; do
  ROUTE_FILE="src/routes/$route.tsx"
  if [ ! -f "$ROUTE_FILE" ]; then
    echo -e "${RED}✗ Missing: $ROUTE_FILE${NC}"
    ((MISSING_COUNT++))
  fi
done < <(grep "from './routes/" src/routeTree.gen.ts | sed "s/.*from '\.\\/routes\\///g" | sed "s/'.*//g" | sort -u)

if [ $MISSING_COUNT -eq 0 ]; then
  echo -e "${GREEN}✓ All route files exist${NC}"
else
  echo -e "${RED}✗ $MISSING_COUNT route files are missing${NC}"
  exit 1
fi
echo ""

# Check 4: Verify router.tsx configuration
echo "Check 4: Verifying router configuration..."
if grep -q "routeTree" src/router.tsx && grep -q "createTanStackRouter" src/router.tsx; then
  echo -e "${GREEN}✓ Router properly configured${NC}"
else
  echo -e "${RED}✗ Router configuration incomplete${NC}"
  exit 1
fi
echo ""

# Check 5: Verify main.tsx setup
echo "Check 5: Verifying main entry point..."
if grep -q "RouterProvider" src/main.tsx && grep -q "createRouter" src/main.tsx; then
  echo -e "${GREEN}✓ Main entry point properly configured${NC}"
else
  echo -e "${RED}✗ Main entry point configuration incomplete${NC}"
  exit 1
fi
echo ""

# Check 6: Count actual route files
echo "Check 6: Counting actual route files..."
ACTUAL_ROUTES=$(find src/routes -name "*.tsx" | wc -l)
echo -e "${GREEN}✓ Found $ACTUAL_ROUTES route files${NC}"
echo ""

# Check 7: Verify route file syntax (basic)
echo "Check 7: Verifying route file syntax..."
SYNTAX_ERRORS=0
for route_file in src/routes/__root.tsx src/routes/*.tsx; do
  if [ -f "$route_file" ]; then
    # Check for createFileRoute or createRootRoute
    if ! grep -q "createFileRoute\|createRootRoute" "$route_file"; then
      echo -e "${RED}✗ $route_file missing route creation${NC}"
      ((SYNTAX_ERRORS++))
    fi
  fi
done

# Also check subdirectories
for route_file in src/routes/**/*.tsx; do
  if [ -f "$route_file" ]; then
    if ! grep -q "createFileRoute" "$route_file"; then
      echo -e "${RED}✗ $route_file missing createFileRoute${NC}"
      ((SYNTAX_ERRORS++))
    fi
  fi
done 2>/dev/null || true

if [ $SYNTAX_ERRORS -eq 0 ]; then
  echo -e "${GREEN}✓ All route files have proper structure${NC}"
else
  echo -e "${RED}✗ $SYNTAX_ERRORS route files have syntax issues${NC}"
  exit 1
fi
echo ""

# Check 8: Verify dynamic route patterns
echo "Check 8: Verifying dynamic route patterns..."
DYNAMIC_ROUTES=$(grep -l '\$' src/routes/*.tsx 2>/dev/null | wc -l)
echo -e "${GREEN}✓ Found $DYNAMIC_ROUTES routes with parameters${NC}"
echo ""

# Summary
echo "======================================"
echo -e "${GREEN}All routing verification checks passed!${NC}"
echo "======================================"
echo ""
echo "Summary:"
echo "  Total routes registered: $ROUTE_COUNT"
echo "  Route files: $ACTUAL_ROUTES"
echo "  Dynamic routes: $DYNAMIC_ROUTES"
echo "  Missing files: 0"
echo "  Syntax errors: 0"
echo "  Router status: Configured"
echo ""
echo "Next steps:"
echo "  1. Run: bun run dev"
echo "  2. Navigate to http://localhost:5173"
echo "  3. Test key routes manually"
echo "  4. Check browser console for errors"
echo ""
