#!/bin/bash

# Go Naming Explosion Detection Script
# Prevents AI from creating versioned/prefixed package/file names.
# Catches all casing styles (Pascal, camel, snake, kebab) and positions (prefix, suffix, middle).

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking Go files for naming explosion patterns..."

if [ ! -d "backend" ]; then
  echo -e "${GREEN}✅ No backend directory found - skipping check${NC}"
  exit 0
fi

SEARCH_DIRS="backend"
# shellcheck disable=SC2086
# Exclude domain paths: temporal (Temporal.io), template — avoid false positives on "temp"
run_find() { find $SEARCH_DIRS -type f -name '*.go' -not -path '*/vendor/*' -not -path '*_test.go' -not -path '*/pb/*.pb.go' "$@" | grep -v -iE 'temporal|template' || true; }

# Domain-specific exceptions (legitimate use of otherwise forbidden words)
# These patterns are excluded from forbidden word checks:
# - backup: backup/restore functionality (services, handlers, repositories)
# - benchmark: performance benchmarking (test files, utilities)
filter_domain_exceptions() {
  grep -v -E 'backup|benchmark'
}

# Forbidden words (all casings via grep -iE); use -e for pattern on macOS
WORDS="new|improved|enhanced|updated|fixed|refactored|modified|revised|copy|backup|old|draft|final|latest|temp|tmp|wip|legacy|deprecated|duplicate|alternate|iteration|replacement|variant"

# --- Version / rev / iter (all casings) ---
VERSIONED_FILES=$(run_find | grep -iE '(_v|V|v|version|ver|rev|iter)[-_]?[0-9]+\.go$' || true)
# At least 2 letters then digits (exclude s3.go, a1.go)
NAME_DIGITS_FILES=$(run_find | grep -E '[A-Za-z]{2,}[0-9]+\.go$' || true)
NUMBERED_FILES=$(run_find | grep -E '_[0-9]+\.go$' || true)

# --- Phase (all casings) ---
PHASE_END_FILES=$(run_find | grep -iE 'phase[-_]?[0-9][0-9]*\.go$' || true)
PHASE_MID_FILES=$(run_find | grep -iE '_phase[0-9][0-9]*_|phase[0-9][0-9]*_|Phase[0-9]|phase[-_]?[0-9][0-9]*_' || true)

# --- Forbidden words: prefix (New*, Improved*), suffix (*New, *_final), middle (*_backup_*) ---
# Apply domain exceptions to filter out legitimate uses (backup, benchmark)
SUFFIX_PAT="_(${WORDS})\\.go\$"
PREFIX_PAT="/(${WORDS})_[a-zA-Z0-9_]+\\.go\$"
# Word boundary: _word_ or _word. so "temp" doesn't match "temporal"
MIDDLE_PAT="_(${WORDS})(_|\\.)"
KEBAB_PAT="-(${WORDS})(\\.go\$|_)"
FORBIDDEN_SUFFIX=$(run_find | grep -i -E -e "$SUFFIX_PAT" | filter_domain_exceptions || true)
FORBIDDEN_PREFIX=$(run_find | grep -i -E -e "$PREFIX_PAT" | filter_domain_exceptions || true)
FORBIDDEN_MIDDLE=$(run_find | grep -i -E -e "$MIDDLE_PAT" | filter_domain_exceptions || true)
FORBIDDEN_KEBAB=$(run_find | grep -i -E -e "$KEBAB_PAT" | filter_domain_exceptions || true)
# Pascal prefix/suffix: New*.go, *New.go, *Final.go (use -e for macOS grep)
PASCAL_PREFIX_PAT="/(New|Improved|Enhanced|Updated|Fixed|Refactored|Modified|Revised|Copy|Backup|Old|Draft|Final|Latest|Temp|Tmp|Wip|Legacy|Deprecated|Duplicate|Alternate)[A-Z][a-zA-Z0-9]*\\.go\$"
PASCAL_SUFFIX_PAT="(New|Improved|Enhanced|Updated|Fixed|Refactored|Modified|Revised|Final|Latest|Revised)\\.go\$"
PASCAL_PREFIX=$(run_find | grep -i -E -e "$PASCAL_PREFIX_PAT" || true)
PASCAL_SUFFIX=$(run_find | grep -i -E -e "$PASCAL_SUFFIX_PAT" || true)

# Combine all violations
ALL_VIOLATIONS=""
for var in VERSIONED_FILES NAME_DIGITS_FILES NUMBERED_FILES PHASE_END_FILES PHASE_MID_FILES \
  FORBIDDEN_SUFFIX FORBIDDEN_PREFIX FORBIDDEN_MIDDLE FORBIDDEN_KEBAB PASCAL_PREFIX PASCAL_SUFFIX; do
  eval "val=\$$var"
  if [ -n "$val" ]; then
    ALL_VIOLATIONS="$ALL_VIOLATIONS$val
"
  fi
done

if [ -n "$ALL_VIOLATIONS" ]; then
  echo -e "${RED}❌ NAMING EXPLOSION DETECTED${NC}"
  echo ""
  echo -e "${YELLOW}The following Go files use forbidden naming patterns:${NC}"
  echo ""
  echo -e "$ALL_VIOLATIONS" | sort | uniq
  echo ""
  echo -e "${YELLOW}Forbidden patterns (all casings):${NC}"
  echo "  • Versioned: *_v2.go, *V2.go, *v2.go, *version2.go, *HandlerV2.go"
  echo "  • Name+digits: *Handler2.go, *Service3.go"
  echo "  • Phase: *phase1.go, *Phase2.go, *_phase3_*.go"
  echo "  • Forbidden words (prefix/suffix/middle): New*, *New, *_new, *_backup_*, etc."
  echo ""
  echo "See: docs/reports/NAMING_EXPLOSION_GUARD_STATUS.md"
  echo ""
  exit 1
else
  echo -e "${GREEN}✅ No naming explosion detected${NC}"
  exit 0
fi
