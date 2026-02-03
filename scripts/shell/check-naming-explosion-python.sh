#!/bin/bash

# Python Naming Explosion Detection Script
# Prevents AI from creating versioned/prefixed module names
# Part of AI coding quality gates

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking Python files for naming explosion patterns..."

# Search in source and tests (exclude vendored, migrations, generated)
SEARCH_DIRS="src/tracertm tests"

# Check for versioned naming (_v2, _version2, etc.)
VERSIONED_FILES=$(find $SEARCH_DIRS -type f -name "*.py" \
  -not -path "*/ARCHIVE/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/migrations/*" \
  -not -path "*_pb2.py" \
  -not -path "*_pb2_grpc.py" | \
  grep -E '(_v|_V|V)[0-9]+\.py$' || true)

# Check for prefixed naming (new_*, improved_*, enhanced_*, etc.)
# Python uses snake_case, so check lowercase prefixes
PREFIXED_FILES=$(find $SEARCH_DIRS -type f -name "*.py" \
  -not -path "*/ARCHIVE/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/migrations/*" \
  -not -path "*_pb2.py" \
  -not -path "*_pb2_grpc.py" | \
  grep -E '^.*(new_|improved_|enhanced_|updated_|fixed_|refactored_|modified_|revised_)[a-z_]+\.py$' || true)

# Check for suffixed naming (*_new, *_improved, etc.)
SUFFIXED_FILES=$(find $SEARCH_DIRS -type f -name "*.py" \
  -not -path "*/ARCHIVE/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/migrations/*" \
  -not -path "*_pb2.py" \
  -not -path "*_pb2_grpc.py" | \
  grep -E '_(new|improved|enhanced|updated|fixed|refactored|modified|revised)\.py$' || true)

# Check for numbered suffixes (*_2, *_3, etc.) - exclude test fixtures
NUMBERED_FILES=$(find $SEARCH_DIRS -type f -name "*.py" \
  -not -path "*/ARCHIVE/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/migrations/*" \
  -not -path "*_pb2.py" \
  -not -path "*_pb2_grpc.py" \
  -not -path "*/fixtures/*" | \
  grep -E '_[0-9]+\.py$' || true)

# Check for phase suffixes (*_phase2, *_phase3, *phase2_*, etc.)
PHASE_FILES=$(find $SEARCH_DIRS -type f -name "*.py" \
  -not -path "*/ARCHIVE/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/migrations/*" \
  -not -path "*_pb2.py" \
  -not -path "*_pb2_grpc.py" | \
  grep -E '(_phase[0-9]|_phase[0-9][0-9]|phase[0-9]_|phase[0-9][0-9]_)\.py$' || true)

# Check for other common AI versioning (*_final, *_latest, etc.)
OTHER_VERSION_FILES=$(find $SEARCH_DIRS -type f -name "*.py" \
  -not -path "*/ARCHIVE/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/migrations/*" \
  -not -path "*_pb2.py" \
  -not -path "*_pb2_grpc.py" | \
  grep -E '_(final|latest|revised)\.py$' || true)

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
  echo -e "${YELLOW}The following Python files use forbidden naming patterns:${NC}"
  echo ""
  echo -e "$ALL_VIOLATIONS" | sort | uniq
  echo ""
  echo -e "${YELLOW}Forbidden patterns (Python snake_case):${NC}"
  echo "  • Versioned: service_v2.py, api_V2.py"
  echo "  • Prefixed: new_dashboard.py, improved_service.py, enhanced_api.py"
  echo "  • Suffixed: dashboard_new.py, service_improved.py"
  echo "  • Numbered: dashboard_2.py, service_3.py"
  echo "  • Phase suffixes: benchmark_phase2.py, service_phase3.py"
  echo "  • Other versions: service_final.py, module_latest.py"
  echo ""
  echo -e "${YELLOW}Required action:${NC}"
  echo "  1. Identify the canonical (currently used) module"
  echo "  2. Edit the canonical module in place"
  echo "  3. Delete ALL versioned/prefixed variants"
  echo "  4. Update imports to use canonical names only"
  echo ""
  echo -e "${YELLOW}Why this matters:${NC}"
  echo "  • This is an AI-coded project"
  echo "  • Naming explosion creates orphaned modules"
  echo "  • Each 'version' confuses future AI sessions"
  echo "  • Backward compatibility is NOT a goal here"
  echo "  • We aggressively evolve - edit in place always"
  echo ""
  echo "See: docs/reports/NAMING_EXPLOSION_GUARD_STATUS.md"
  echo ""
  exit 1
else
  echo -e "${GREEN}✅ No naming explosion detected${NC}"
  exit 0
fi
