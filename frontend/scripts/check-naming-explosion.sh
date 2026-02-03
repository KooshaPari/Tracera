#!/bin/bash

# Naming Explosion Detection Script
# Prevents AI from creating versioned/prefixed component names
# Part of AI coding quality gates

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking for naming explosion patterns..."

# Check for versioned file names (_v2, V2, _version2, etc.)
VERSIONED_FILES=$(find apps packages -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" | grep -E '(_v|_V|V)[0-9]+\.(ts|tsx|js|jsx)$' || true)

# Check for prefixed naming (New*, Improved*, Enhanced*, etc.)
PREFIXED_FILES=$(find apps packages -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" | grep -E '(New|Improved|Enhanced|Updated|Fixed|Refactored|Modified|Revised)[A-Z].*\.(ts|tsx|js|jsx)$' || true)

# Check for suffixed naming (*_new, *_improved, etc.)
SUFFIXED_FILES=$(find apps packages -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" | grep -E '_(new|improved|enhanced|updated|fixed|refactored|modified|revised)\.(ts|tsx|js|jsx)$' || true)

# Check for numbered suffixes (*_2, *_3, etc.)
NUMBERED_FILES=$(find apps packages -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" | grep -E '_[0-9]+\.(ts|tsx|js|jsx)$' || true)

# Check for phase suffixes (*_phase2, *_phase3, *phase2_*, etc.)
PHASE_FILES=$(find apps packages -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" | grep -E '(_phase[0-9]|_phase[0-9][0-9]|phase[0-9]_|phase[0-9][0-9]_)\.(ts|tsx|js|jsx)$' || true)

# Check for other common AI versioning (*_final, *_latest, *_updated, etc.)
OTHER_VERSION_FILES=$(find apps packages -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" | grep -E '_(final|latest|revised)\.(ts|tsx|js|jsx)$' || true)

# Combine all violations
ALL_VIOLATIONS=""
if [ -n "$VERSIONED_FILES" ]; then
  ALL_VIOLATIONS="$ALL_VIOLATIONS$VERSIONED_FILES\n"
fi
if [ -n "$PREFIXED_FILES" ]; then
  ALL_VIOLATIONS="$ALL_VIOLATIONS$PREFIXED_FILES\n"
fi
if [ -n "$SUFFIXED_FILES" ]; then
  ALL_VIOLATIONS="$ALL_VIOLATIONS$SUFFIXED_FILES\n"
fi
if [ -n "$NUMBERED_FILES" ]; then
  ALL_VIOLATIONS="$ALL_VIOLATIONS$NUMBERED_FILES\n"
fi
if [ -n "$PHASE_FILES" ]; then
  ALL_VIOLATIONS="$ALL_VIOLATIONS$PHASE_FILES\n"
fi
if [ -n "$OTHER_VERSION_FILES" ]; then
  ALL_VIOLATIONS="$ALL_VIOLATIONS$OTHER_VERSION_FILES\n"
fi

# Report results
if [ -n "$ALL_VIOLATIONS" ]; then
  echo -e "${RED}❌ NAMING EXPLOSION DETECTED${NC}"
  echo ""
  echo -e "${YELLOW}The following files use forbidden naming patterns:${NC}"
  echo ""
  echo -e "$ALL_VIOLATIONS" | sort | uniq
  echo ""
  echo -e "${YELLOW}Forbidden patterns:${NC}"
  echo "  • Versioned: *_v2.tsx, *V2.tsx, *_version2.tsx"
  echo "  • Prefixed: NewDashboard.tsx, ImprovedComponent.tsx, EnhancedButton.tsx"
  echo "  • Suffixed: Dashboard_new.tsx, Component_improved.tsx"
  echo "  • Numbered: Dashboard_2.tsx, Component_3.tsx"
  echo "  • Phase suffixes: benchmark_phase2.tsx, component_phase3.tsx"
  echo "  • Other versions: service_final.tsx, component_latest.tsx"
  echo ""
  echo -e "${YELLOW}Required action:${NC}"
  echo "  1. Identify the canonical (currently used) file"
  echo "  2. Edit the canonical file in place"
  echo "  3. Delete ALL versioned/prefixed variants"
  echo "  4. Update imports to use canonical names only"
  echo ""
  echo -e "${YELLOW}Why this matters:${NC}"
  echo "  • This is an AI-coded project"
  echo "  • Naming explosion creates orphaned files"
  echo "  • Each 'version' confuses future AI sessions"
  echo "  • Backward compatibility is NOT a goal here"
  echo "  • We aggressively evolve - edit in place always"
  echo ""
  echo "See: docs/reports/AI_NAMING_EXPLOSION_PREVENTION.md"
  echo ""
  exit 1
else
  echo -e "${GREEN}✅ No naming explosion detected${NC}"
  exit 0
fi
