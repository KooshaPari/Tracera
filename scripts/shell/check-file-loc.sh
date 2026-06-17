#!/bin/bash
# LOC guard: check that source files don't exceed the line-count limit
# Reads limit and exclude patterns from config/loc-guard.json if present, defaults to 500 lines
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

# Use Python to handle pattern matching with fnmatch
python3 << PYTHON_EOF
import json
import os
import fnmatch

CONFIG = "config/loc-guard.json"
LIMIT = 500
exclude_patterns = []

if os.path.isfile(CONFIG):
    try:
        with open(CONFIG) as f:
            config = json.load(f)
        LIMIT = config.get('max_lines', 500)
        exclude_patterns = config.get('exclude_patterns', [])
    except:
        pass

def should_exclude(filepath):
    """Check if file matches any exclude pattern"""
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(filepath, pattern):
            return True
    return False

violations = []
file_list = """${files[*]}""".split()

for filepath in file_list:
    if not os.path.isfile(filepath):
        continue
    if should_exclude(filepath):
        continue

    try:
        with open(filepath) as f:
            lines = len(f.readlines())
        if lines > LIMIT:
            violations.append((filepath, lines))
    except:
        pass

if violations:
    print(f"LOC limit violations (>{LIMIT} lines):")
    for filepath, lines in violations:
        print(f"  {filepath}: {lines} lines (limit {LIMIT})")
    exit(1)
else:
    print(f"LOC check passed — all {len(file_list)} file(s) within {LIMIT}-line limit")
    exit(0)
PYTHON_EOF
