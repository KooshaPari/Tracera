#!/usr/bin/env bash
# Pre-push validation script - replaces billable CI checks
# Run via: pre-commit run --all-files --hook-stage pre-push
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "=== Pre-push validation ==="

# 1. Scaffold smoke test - verify required files exist
echo "[1/5] Running scaffold smoke test..."
for f in \
  "contracts/template.manifest.json" \
  "contracts/reconcile.rules.yaml" \
  "Taskfile.yml" \
  "SECURITY.md"; do
  if [ ! -f "$f" ]; then
    echo "[FAIL] missing required file: $f"
    exit 1
  fi
done
echo "    [OK] Scaffold files present"

# 2. Policy gate - validate required template contract files
echo "[2/5] Running policy gate checks..."
test -f contracts/template.manifest.json
test -f contracts/reconcile.rules.yaml
test -f Taskfile.yml
test -f SECURITY.md
echo "    [OK] Policy gate passed"

# 3. Secret pattern check (from policy-gate workflow)
# Excludes documentation files which may contain example patterns
echo "[3/5] Checking for secret-like patterns..."
if rg -n "(api[_-]?key|secret|password|token)\s*=\s*['\"]([^'\"]+)['\"]" -S . \
  --glob '!**/.git/**' \
  --glob '!*.md' \
  --glob '!docs/**' \
  --glob '!**/*.md' \
  2>/dev/null; then
  echo "[FAIL] Secret-like patterns found (excluding documentation)"
  exit 1
fi
echo "    [OK] No secret patterns detected"

# 4. Security guard (ggshield secret scan)
echo "[4/5] Running security guard (ggshield)..."
if command -v ggshield >/dev/null 2>&1; then
  ggshield secret scan pre-commit || {
    echo "[FAIL] ggshield scan failed"
    exit 1
  }
elif command -v uvx >/dev/null 2>&1; then
  uvx ggshield secret scan pre-commit || {
    echo "[FAIL] ggshield scan failed"
    exit 1
  }
elif command -v uv >/dev/null 2>&1; then
  uv tool run ggshield secret scan pre-commit || {
    echo "[FAIL] ggshield scan failed"
    exit 1
  }
else
  echo "    [SKIP] ggshield not installed (run: pipx install ggshield or uv tool install ggshield)"
fi

# 5. Codespell fast pass
echo "[5/5] Running codespell (if available)..."
if command -v codespell >/dev/null 2>&1; then
  # Get changed files for this push
  changed_files=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
  if [ -z "${changed_files}" ]; then
    changed_files=$(git diff --name-only --diff-filter=ACM HEAD~1..HEAD 2>/dev/null || true)
  fi

  if [ -n "${changed_files}" ]; then
    echo "${changed_files}" | \
      grep -E '\.(md|txt|py|ts|tsx|js|go|rs|kt|java|yaml|yml)$' | \
      xargs -r codespell -q 2 -L "hte,teh" || true
  fi
else
  echo "    [SKIP] codespell not installed"
fi

echo ""
echo "=== Pre-push validation complete ==="
