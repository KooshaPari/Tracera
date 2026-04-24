#!/usr/bin/env bash
# CI gate: fail if inline suppression count increases beyond baseline.
# Counts: # noqa, # type: ignore, //nolint, eslint-disable, @ts-ignore, @ts-expect-error, # pragma: no cover
set -euo pipefail

BASELINE_FILE=".ci-baselines/suppression-count.txt"

if [ ! -f "$BASELINE_FILE" ]; then
  echo "WARNING: No suppression baseline found at $BASELINE_FILE. Skipping check."
  exit 0
fi

BASELINE=$(cat "$BASELINE_FILE" | tr -d '[:space:]')

PY_NOQA=$(grep -rn '# noqa' --include='*.py' src/ tests/ 2>/dev/null | wc -l | tr -d ' ')
PY_TYPE_IGNORE=$(grep -rn '# type: ignore' --include='*.py' src/ tests/ 2>/dev/null | wc -l | tr -d ' ')
PY_PRAGMA=$(grep -rn '# pragma: no cover' --include='*.py' src/ tests/ 2>/dev/null | wc -l | tr -d ' ')
GO_NOLINT=$(grep -rn '//nolint' --include='*.go' backend/ 2>/dev/null | wc -l | tr -d ' ')
TS_DISABLE=$(grep -rn 'eslint-disable\|@ts-ignore\|@ts-expect-error' --include='*.ts' --include='*.tsx' frontend/apps/ 2>/dev/null | grep -v 'node_modules/' | grep -v '\.next/' | wc -l | tr -d ' ')

CURRENT=$((PY_NOQA + PY_TYPE_IGNORE + PY_PRAGMA + GO_NOLINT + TS_DISABLE))

echo "Suppression counts:"
echo "  Python noqa:        $PY_NOQA"
echo "  Python type:ignore: $PY_TYPE_IGNORE"
echo "  Python pragma:      $PY_PRAGMA"
echo "  Go nolint:          $GO_NOLINT"
echo "  TS disables:        $TS_DISABLE"
echo "  ────────────────────"
echo "  Total:              $CURRENT (baseline: $BASELINE)"

if [ "$CURRENT" -gt "$BASELINE" ]; then
  echo ""
  echo "FAILED: Suppression count increased ($BASELINE -> $CURRENT)."
  echo "Fix the code instead of adding suppressions."
  exit 1
fi

if [ "$CURRENT" -lt "$BASELINE" ]; then
  echo ""
  echo "Great: Suppression count decreased! Update baseline:"
  echo "  echo $CURRENT > $BASELINE_FILE"
fi

echo ""
echo "PASSED: Suppression count within baseline."
