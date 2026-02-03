#!/bin/bash

# Python Naming Explosion Detection Script
# Prevents AI from creating versioned/prefixed module names.
# Catches all casing styles (snake, camel, Pascal, kebab, UPPER) and positions (prefix, suffix, middle).

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking Python files for naming explosion patterns..."

SEARCH_DIRS="src/tracertm tests"
# shellcheck disable=SC2086
run_find() { find $SEARCH_DIRS -type f -name '*.py' -not -path '*/ARCHIVE/*' -not -path '*/__pycache__/*' -not -path '*/migrations/*' -not -path '*_pb2.py' -not -path '*_pb2_grpc.py' "$@"; }

# Domain-specific exceptions (legitimate use of otherwise forbidden words)
# These patterns are excluded from forbidden word checks:
# - backup: backup/restore functionality (services, commands, tests)
# - benchmark: performance benchmarking (services, commands, tests)
# - final: test coverage files (test_final_*.py, *_final_coverage.py)
# - batch/part: test files split for size/performance (test_*_batch[0-9].py, test_*_part[0-9].py)
filter_domain_exceptions() {
  grep -v -E '(backup|benchmark)' | grep -v -E 'test_final_(gap_|edge_)?coverage\.py$'
}

filter_numbered_exceptions() {
  grep -v -E 'test_.*_(batch|part)[0-9]+\.py$'
}

# Forbidden words (all casings via grep -iE): prefix, suffix, middle
WORDS="new|improved|enhanced|updated|fixed|refactored|modified|revised|copy|backup|old|draft|final|latest|temp|tmp|wip|legacy|deprecated|duplicate|alternate|iteration|replacement|variant"

# --- Version / rev / iter (all casings) ---
# _v2, V2, v2, dashboardv2.py, version2.py, rev3.py, iter1.py
VERSIONED_FILES=$(run_find | grep -iE '(_v|V|v|version|ver|rev|iter)[-_]?[0-9]+\.py$' || true)
# Name then digits (no separator): dashboard2.py, component3.py
# At least 2 letters then digits (exclude a1.py)
# Exclude legitimate test batches/parts: test_*batch1.py, test_*part2.py
NAME_DIGITS_FILES=$(run_find | grep -E '[A-Za-z]{2,}[0-9]+\.py$' | filter_numbered_exceptions || true)

# --- Numbered suffix: *_2.py, *_3.py ---
# Exclude legitimate test batches/parts: test_*_batch1.py, test_*_part2.py
NUMBERED_FILES=$(run_find -not -path '*/fixtures/*' | grep -E '_[0-9]+\.py$' | filter_numbered_exceptions || true)

# --- Phase (all casings): phase1, Phase2, phase_3, PHASE_4, _phase5_, phase6_, phase-2 ---
PHASE_END_FILES=$(run_find | grep -iE 'phase[-_]?[0-9][0-9]*\.py$' || true)
PHASE_MID_FILES=$(run_find | grep -iE '_phase[0-9][0-9]*_|phase[0-9][0-9]*_|phase[-_]?[0-9][0-9]*_' || true)

# --- Forbidden words: prefix, suffix, middle (all casings); kebab: *-new.py, *-new-* ---
# Suffix: *_new.py, *_Final.py (case-insensitive). Use pattern var so grep gets one arg.
# Apply domain exceptions to filter out legitimate uses (backup, benchmark, final coverage tests)
SUFFIX_PAT="_(${WORDS})\\.py\$"
PREFIX_PAT="/(${WORDS})_[a-zA-Z0-9_]+\\.py\$"
# Word boundary: _word_ or _word. so "temp" doesn't match "temporal"
MIDDLE_PAT="_(${WORDS})(_|\\.)"
KEBAB_PAT="-(${WORDS})(\\.py\$|_)"
FORBIDDEN_SUFFIX=$(run_find | grep -i -E -e "$SUFFIX_PAT" | filter_domain_exceptions || true)
FORBIDDEN_PREFIX=$(run_find | grep -i -E -e "$PREFIX_PAT" | filter_domain_exceptions || true)
FORBIDDEN_MIDDLE=$(run_find | grep -i -E -e "$MIDDLE_PAT" | filter_domain_exceptions || true)
FORBIDDEN_KEBAB=$(run_find | grep -i -E -e "$KEBAB_PAT" | filter_domain_exceptions || true)

# Combine all violations
ALL_VIOLATIONS=""
for var in VERSIONED_FILES NAME_DIGITS_FILES NUMBERED_FILES PHASE_END_FILES PHASE_MID_FILES FORBIDDEN_SUFFIX FORBIDDEN_PREFIX FORBIDDEN_MIDDLE FORBIDDEN_KEBAB; do
  eval "val=\$$var"
  if [ -n "$val" ]; then
    ALL_VIOLATIONS="$ALL_VIOLATIONS$val
"
  fi
done

# Report results
if [ -n "$ALL_VIOLATIONS" ]; then
  echo -e "${RED}❌ NAMING EXPLOSION DETECTED${NC}"
  echo ""
  echo -e "${YELLOW}The following Python files use forbidden naming patterns:${NC}"
  echo ""
  echo -e "$ALL_VIOLATIONS" | sort | uniq
  echo ""
  echo -e "${YELLOW}Forbidden patterns (all casings: snake, camel, Pascal, kebab, UPPER):${NC}"
  echo "  • Versioned: *_v2.py, *V2.py, *v2.py, *version2.py, *rev3.py, *iter1.py, *dashboardv2.py"
  echo "  • Name+digits: *dashboard2.py, *component3.py"
  echo "  • Numbered suffix: *_2.py, *_3.py"
  echo "  • Phase: *phase1.py, *Phase2.py, *_phase_3.py, *phase4_*.py, *_phase5_*.py"
  echo "  • Forbidden words (prefix/suffix/middle): new, improved, enhanced, updated, fixed,"
  echo "    refactored, modified, revised, copy, backup, old, draft, final, latest, temp, tmp,"
  echo "    wip, legacy, deprecated, duplicate, alternate, iteration, replacement, variant"
  echo ""
  echo -e "${YELLOW}Required action:${NC}"
  echo "  1. Identify the canonical (currently used) module"
  echo "  2. Edit the canonical module in place"
  echo "  3. Delete ALL versioned/prefixed variants"
  echo "  4. Update imports to use canonical names only"
  echo ""
  echo "See: docs/reports/NAMING_EXPLOSION_GUARD_STATUS.md"
  echo ""
  exit 1
else
  echo -e "${GREEN}✅ No naming explosion detected${NC}"
  exit 0
fi
