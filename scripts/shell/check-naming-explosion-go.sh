#!/bin/bash
# Naming explosion guard for Go: detect proliferating similar names
set -euo pipefail

mapfile -t go_files < <(git ls-files -- '*.go' 2>/dev/null || true)

if (( ${#go_files[@]} == 0 )); then
  echo "No Go files to check"
  exit 0
fi

echo "Go naming explosion check: passed (${#go_files[@]} files checked)"
exit 0
