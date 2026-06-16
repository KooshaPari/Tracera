#!/bin/bash
# LOC guard: check that source files don't exceed the line-count limit
# Reads limit from config/loc-guard.json if present, defaults to 500 lines
set -euo pipefail

LIMIT=500
CONFIG="config/loc-guard.json"

if [[ -f "$CONFIG" ]]; then
  LIMIT=$(python3 -c "import json,sys; d=json.load(open('$CONFIG')); print(d.get('max_lines', 500))" 2>/dev/null || echo 500)
fi

files=("$@")

# If no files passed, scan all tracked source files
if (( ${#files[@]} == 0 )); then
  mapfile -t files < <(git ls-files -- '*.py' '*.go' '*.ts' '*.tsx' '*.js' '*.jsx' '*.mjs' '*.cjs' 2>/dev/null || true)
fi

if (( ${#files[@]} == 0 )); then
  echo "No source files to check"
  exit 0
fi

violations=()
for f in "${files[@]}"; do
  [[ -f "$f" ]] || continue
  lines=$(wc -l < "$f")
  if (( lines > LIMIT )); then
    violations+=("$f: $lines lines (limit $LIMIT)")
  fi
done

if (( ${#violations[@]} > 0 )); then
  echo "LOC limit violations (>${LIMIT} lines):"
  for v in "${violations[@]}"; do echo "  $v"; done
  exit 1
fi

echo "LOC check passed — all ${#files[@]} file(s) within ${LIMIT}-line limit"
