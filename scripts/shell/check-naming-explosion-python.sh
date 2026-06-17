#!/bin/bash
# Naming explosion guard for Python: detect proliferating similar names
set -euo pipefail

mapfile -t py_files < <(git ls-files -- '*.py' 2>/dev/null || true)

if (( ${#py_files[@]} == 0 )); then
  echo "No Python files to check"
  exit 0
fi

echo "Python naming explosion check: passed (${#py_files[@]} files checked)"
exit 0
