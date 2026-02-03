#!/bin/bash

# Go Naming Explosion Detection Script
# Prevents AI from creating versioned/prefixed package/file names
# Part of AI coding quality gates

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking Go files for naming explosion patterns..."

# Search in Go backend (exclude vendor, generated)
# Check if Go backend exists - TraceRTM uses backend/ with Go files at root
if [ ! -d "backend" ]; then
  echo -e "${GREEN}✅ No backend directory found - skipping check${NC}"
  exit 0
fi

SEARCH_DIRS="backend"

# Check for versioned file names (V2, _v2, etc.)
VERSIONED_FILES=$(find $SEARCH_DIRS -type f -name "*.go" \
  -not -path "*/vendor/*" \
  -not -path "*_test.go" \
  -not -path "*/pb/*.pb.go" | \
  grep -E '(_v|_V|V)[0-9]+\.go$' || true)

# Check for prefixed naming (Go uses PascalCase for exported)
# Match New*, Improved*, Enhanced*, etc. at file level
PREFIXED_FILES=$(find $SEARCH_DIRS -type f -name "*.go" \
  -not -path "*/vendor/*" \
  -not -path "*_test.go" \
  -not -path "*/pb/*.pb.go" | \
  grep -E '(New|Improved|Enhanced|Updated|Fixed|Refactored|Modified|Revised)[A-Z][a-zA-Z0-9]*\.go$' || true)

# Check for suffixed naming (*New, *Improved, etc.)
SUFFIXED_FILES=$(find $SEARCH_DIRS -type f -name "*.go" \
  -not -path "*/vendor/*" \
  -not -path "*_test.go" \
  -not -path "*/pb/*.pb.go" | \
  grep -E '(New|Improved|Enhanced|Updated|Fixed|Refactored)\.go$' || true)

# Check for numbered suffixes (_2, _3, etc.)
NUMBERED_FILES=$(find $SEARCH_DIRS -type f -name "*.go" \
  -not -path "*/vendor/*" \
  -not -path "*_test.go" \
  -not -path "*/pb/*.pb.go" | \
  grep -E '_[0-9]+\.go$' || true)

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

# Report results
if [ -n "$ALL_VIOLATIONS" ]; then
  echo -e "${RED}❌ NAMING EXPLOSION DETECTED${NC}"
  echo ""
  echo -e "${YELLOW}The following Go files use forbidden naming patterns:${NC}"
  echo ""
  echo -e "$ALL_VIOLATIONS" | sort | uniq
  echo ""
  echo -e "${YELLOW}Forbidden patterns (Go PascalCase):${NC}"
  echo "  • Versioned: DashboardV2.go, ServiceV2.go, api_v2.go"
  echo "  • Prefixed: NewDashboard.go, ImprovedService.go, EnhancedAPI.go"
  echo "  • Suffixed: DashboardNew.go, ServiceImproved.go"
  echo "  • Numbered: Dashboard_2.go, Service_3.go"
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
  echo -e "${YELLOW}Exception:${NC}"
  echo "  • /v2/, /v3/ in import paths for true API versioning is acceptable"
  echo "  • This script checks FILE names, not import path versions"
  echo ""
  echo "See: docs/reports/NAMING_EXPLOSION_GUARD_STATUS.md"
  echo ""
  exit 1
else
  echo -e "${GREEN}✅ No naming explosion detected${NC}"
  exit 0
fi
