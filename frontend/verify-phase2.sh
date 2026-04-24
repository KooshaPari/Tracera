#!/bin/bash

# Frontend Monorepo Phase 2 Verification Script

set -e

echo "==================================================================="
echo "Frontend Monorepo Phase 2: Dependency Deduplication - Verification"
echo "==================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to frontend directory
cd "$(dirname "$0")"

echo "📊 Current Metrics"
echo "------------------------------------------------------------------"

# 1. Package count
echo "Total packages installed:"
PACKAGE_COUNT=$(find node_modules -maxdepth 2 -type d 2>/dev/null | wc -l | tr -d ' ')
echo "  ${PACKAGE_COUNT} directories in node_modules"

# 2. Size
SIZE=$(du -sh node_modules 2>/dev/null | cut -f1)
echo "  ${SIZE} total size"

# 3. Install time
echo ""
echo "⏱️  Install Performance"
echo "------------------------------------------------------------------"
rm -rf node_modules bun.lock 2>/dev/null || true
echo "Testing fresh install..."
START=$(date +%s)
bun install --silent > /dev/null 2>&1
END=$(date +%s)
DURATION=$((END - START))
echo "  ${DURATION}s install time"

# 4. Version verification
echo ""
echo "✅ Critical Version Verification"
echo "------------------------------------------------------------------"

# React
REACT_VERSION=$(bun pm ls react 2>/dev/null | grep "react@" | head -1 | sed 's/.*react@//' | sed 's/ .*//')
if [[ "$REACT_VERSION" == 19.2.* ]]; then
  echo -e "  ${GREEN}✓${NC} React: $REACT_VERSION"
else
  echo -e "  ${RED}✗${NC} React: $REACT_VERSION (expected 19.2.x)"
fi

# TypeScript
TS_VERSION=$(bun pm ls typescript 2>/dev/null | grep "typescript@" | head -1 | sed 's/.*typescript@//' | sed 's/ .*//')
if [[ "$TS_VERSION" == 7.0.0-dev.* ]]; then
  echo -e "  ${GREEN}✓${NC} TypeScript: $TS_VERSION"
else
  echo -e "  ${RED}✗${NC} TypeScript: $TS_VERSION (expected 7.0.0-dev)"
fi

# @types/node
NODE_TYPES_VERSION=$(bun pm ls @types/node 2>/dev/null | grep "@types/node@" | head -1 | sed 's/.*@types\/node@//' | sed 's/ .*//')
if [[ "$NODE_TYPES_VERSION" == 22.* ]]; then
  echo -e "  ${GREEN}✓${NC} @types/node: $NODE_TYPES_VERSION"
else
  echo -e "  ${RED}✗${NC} @types/node: $NODE_TYPES_VERSION (expected 22.x)"
fi

# Vite
VITE_VERSION=$(bun pm ls vite 2>/dev/null | grep "vite@" | head -1 | sed 's/.*vite@//' | sed 's/ .*//')
if [[ "$VITE_VERSION" == 8.0.0-beta.* ]]; then
  echo -e "  ${GREEN}✓${NC} Vite: $VITE_VERSION"
else
  echo -e "  ${YELLOW}⚠${NC} Vite: $VITE_VERSION (expected 8.0.0-beta)"
fi

echo ""
echo "📦 Largest Dependencies"
echo "------------------------------------------------------------------"
du -sh node_modules/* 2>/dev/null | sort -hr | head -10

echo ""
echo "🎯 Phase 2 Success Criteria"
echo "------------------------------------------------------------------"

# Check overrides exist
OVERRIDES_COUNT=$(cat package.json | jq '.overrides | length' 2>/dev/null || echo "0")
if [ "$OVERRIDES_COUNT" -gt 30 ]; then
  echo -e "  ${GREEN}✓${NC} Overrides configured: $OVERRIDES_COUNT"
else
  echo -e "  ${RED}✗${NC} Overrides configured: $OVERRIDES_COUNT (expected >30)"
fi

# Check install speed
if [ "$DURATION" -lt 20 ]; then
  echo -e "  ${GREEN}✓${NC} Install time: ${DURATION}s (<20s)"
else
  echo -e "  ${YELLOW}⚠${NC} Install time: ${DURATION}s (target: <20s)"
fi

# Check disable folder is ignored
if grep -q "^disable/" .gitignore 2>/dev/null; then
  echo -e "  ${GREEN}✓${NC} disable/ folder in .gitignore"
else
  echo -e "  ${RED}✗${NC} disable/ folder NOT in .gitignore"
fi

echo ""
echo "==================================================================="
echo "Phase 2 Verification Complete"
echo "==================================================================="
