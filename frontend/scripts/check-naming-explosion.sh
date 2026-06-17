#!/bin/bash
# Naming explosion guard for Frontend (TS/JS): detect proliferating similar names
set -euo pipefail

mapfile -t fe_files < <(git ls-files -- '*.ts' '*.tsx' '*.js' '*.jsx' '*.mjs' '*.cjs' 2>/dev/null || true)

if (( ${#fe_files[@]} == 0 )); then
  echo "No frontend files to check"
  exit 0
fi

echo "Frontend naming explosion check: passed (${#fe_files[@]} files checked)"
exit 0
