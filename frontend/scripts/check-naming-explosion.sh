#!/bin/bash

# Frontend Naming Explosion Detection Script
# Prevents AI from creating versioned/prefixed component names.
# Catches all casing styles (camel, Pascal, snake, kebab) and positions (prefix, suffix, middle).

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking for naming explosion patterns..."

# shellcheck disable=SC2086
run_find() { find apps packages -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \) -not -path '*/node_modules/*' "$@"; }
EXT_RE='\.(ts|tsx|js|jsx)\$'

# Domain-specific exceptions (legitimate use of otherwise forbidden words)
# These patterns are excluded from forbidden word checks:
# - benchmark: performance benchmarking (scripts, tests)
filter_domain_exceptions() {
  grep -v -E 'benchmark'
}

# Forbidden words (all casings); use -e for pattern on macOS grep
WORDS="new|improved|enhanced|updated|fixed|refactored|modified|revised|copy|backup|old|draft|final|latest|temp|tmp|wip|legacy|deprecated|duplicate|alternate|iteration|replacement|variant"

# --- Version / rev / iter (all casings) ---
VERSIONED_FILES=$(run_find | grep -iE "(_v|V|v|version|ver|rev|iter)[-_]?[0-9]+${EXT_RE}" || true)
# At least 2 letters then digits (exclude a1.ts)
NAME_DIGITS_FILES=$(run_find | grep -E "[A-Za-z]{2,}[0-9]+${EXT_RE}" || true)
NUMBERED_FILES=$(run_find | grep -E "_[0-9]+${EXT_RE}" || true)

# --- Phase (all casings) ---
PHASE_END_FILES=$(run_find | grep -iE "phase[-_]?[0-9][0-9]*${EXT_RE}" || true)
PHASE_MID_FILES=$(run_find | grep -iE "_phase[0-9][0-9]*_|phase[0-9][0-9]*_|phase[-_]?[0-9][0-9]*_" || true)

# --- Forbidden words: prefix, suffix, middle, kebab ---
# Apply domain exceptions to filter out legitimate uses (benchmark scripts/tests)
SUFFIX_PAT="_(${WORDS})\\.(ts|tsx|js|jsx)\$"
PREFIX_PAT="/(${WORDS})_[a-zA-Z0-9_]+\\.(ts|tsx|js|jsx)\$"
# Word boundary: _word_ or _word. so "temp" doesn't match "temporal"
MIDDLE_PAT="_(${WORDS})(_|\\.)"
KEBAB_PAT="-(${WORDS})(\\.(ts|tsx|js|jsx)\$|_)"
FORBIDDEN_SUFFIX=$(run_find | grep -i -E -e "$SUFFIX_PAT" | filter_domain_exceptions || true)
FORBIDDEN_PREFIX=$(run_find | grep -i -E -e "$PREFIX_PAT" | filter_domain_exceptions || true)
FORBIDDEN_MIDDLE=$(run_find | grep -i -E -e "$MIDDLE_PAT" | filter_domain_exceptions || true)
FORBIDDEN_KEBAB=$(run_find | grep -i -E -e "$KEBAB_PAT" | filter_domain_exceptions || true)
# Pascal/camel prefix/suffix: New*.tsx, *New.tsx, *V2.tsx
# Exclude domain paths: temporal (Temporal.io), template (TEMPLATE.stories) — avoid false positives on "temp"
PASCAL_PREFIX_PAT="/(New|Improved|Enhanced|Updated|Fixed|Refactored|Modified|Revised|Copy|Backup|Old|Draft|Final|Latest|Temp|Tmp|Wip|Legacy|Deprecated|Duplicate|Alternate)[A-Z].*\\.(ts|tsx|js|jsx)\$"
PASCAL_SUFFIX_PAT="(New|Improved|Enhanced|Updated|Fixed|Refactored|Modified|Revised|Final|Latest)\\.(ts|tsx|js|jsx)\$"
PASCAL_PREFIX=$(run_find | grep -v -iE 'temporal|/template|TEMPLATE' | grep -i -E -e "$PASCAL_PREFIX_PAT" || true)
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
  echo -e "${YELLOW}The following files use forbidden naming patterns:${NC}"
  echo ""
  echo -e "$ALL_VIOLATIONS" | sort | uniq
  echo ""
  echo -e "${YELLOW}Forbidden patterns (all casings):${NC}"
  echo "  • Versioned: *_v2.tsx, *V2.tsx, *v2.tsx, *version2.tsx, *dashboardv2.tsx"
  echo "  • Name+digits: *Dashboard2.tsx, *component3.tsx"
  echo "  • Phase: *phase1.tsx, *Phase2.tsx, *_phase3_*.tsx"
  echo "  • Forbidden words (prefix/suffix/middle/kebab): New*, *New, *_new, *-new.tsx, etc."
  echo ""
  echo "See: docs/reports/AI_NAMING_EXPLOSION_PREVENTION.md"
  echo ""
  exit 1
else
  echo -e "${GREEN}✅ No naming explosion detected${NC}"
  exit 0
fi
