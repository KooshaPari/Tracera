#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for f in \
  "$repo_root/contracts/template.manifest.json" \
  "$repo_root/contracts/reconcile.rules.yaml" \
  "$repo_root/templates/domain/webapp.compose.yaml" \
  "$repo_root/Taskfile.yml"; do
  test -f "$f" || { echo "[FAIL] missing $f"; exit 1; }
done
echo "[OK] scaffold smoke passed"
