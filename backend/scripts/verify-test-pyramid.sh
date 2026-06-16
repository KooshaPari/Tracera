#!/usr/bin/env bash
# verify-test-pyramid.sh
# Validates that the test suite conforms to the test pyramid constraints:
#   - Unit tests  >= 40% of total
#   - E2E tests   <= 10% of total
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

count_tests() {
  local pattern="$1"
  local dir="$2"
  if [ ! -d "$dir" ]; then
    echo 0
    return
  fi
  grep -r --include="*.go" --include="*.py" --include="*.ts" --include="*.js" \
    -l "$pattern" "$dir" 2>/dev/null | wc -l
}

# Count test files by layer
UNIT_DIR="$REPO_ROOT/backend"
E2E_DIR="$REPO_ROOT/backend/tests/e2e"
INT_DIR="$REPO_ROOT/backend/tests/integration"

unit_files=$(grep -r --include="*.go" -l "_test\|_unit" "$UNIT_DIR" 2>/dev/null | grep -v "e2e\|integration" | wc -l || echo 0)
e2e_files=$(find "$E2E_DIR" -name "*_test*" -o -name "test_*" 2>/dev/null | wc -l || echo 0)
int_files=$(find "$INT_DIR" -name "*_test*" -o -name "test_*" 2>/dev/null | wc -l || echo 0)

total=$((unit_files + e2e_files + int_files))

echo "=== Test Pyramid Verification ==="
echo "Unit test files:        $unit_files"
echo "Integration test files: $int_files"
echo "E2E test files:         $e2e_files"
echo "Total:                  $total"

if [ "$total" -eq 0 ]; then
  echo ""
  echo "WARNING: No test files detected — pyramid check skipped (0 tests found)."
  echo "Add unit tests under backend/ to satisfy the pyramid."
  exit 0
fi

unit_pct=$(( (unit_files * 100) / total ))
e2e_pct=$(( (e2e_files * 100) / total ))

echo ""
echo "Unit %: $unit_pct%  (required >= 40%)"
echo "E2E  %: $e2e_pct%  (required <= 10%)"

FAIL=0

if [ "$unit_pct" -lt 40 ]; then
  echo "FAIL: Unit tests are ${unit_pct}% — must be >= 40%"
  FAIL=1
fi

if [ "$e2e_pct" -gt 10 ]; then
  echo "FAIL: E2E tests are ${e2e_pct}% — must be <= 10%"
  FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then
  echo ""
  echo "PASS: Test pyramid constraints satisfied."
fi

exit $FAIL
