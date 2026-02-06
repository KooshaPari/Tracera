#!/usr/bin/env bash
# Ensure generated contracts are up-to-date (fails if regeneration changes files).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "$PROJECT_ROOT"

bash "$PROJECT_ROOT/scripts/shell/generate-contracts.sh"

paths=(
  "openapi"
  "backend/docs"
  "frontend/apps/web/src/api/generated"
  "src/tracertm/generated"
)

changed=$(git status --porcelain -- "${paths[@]}" | wc -l | tr -d ' ')
if [ "$changed" != "0" ]; then
  echo "[contracts] Generated files are out of date. Run: bash scripts/shell/generate-contracts.sh" >&2
  git status --porcelain -- "${paths[@]}" >&2
  exit 1
fi

echo "[contracts] Generated contracts are up-to-date."
