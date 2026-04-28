#!/usr/bin/env bash

# Run markdown-link-check against repository markdown files with shared config.
# Exits non-zero if any broken links are detected.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONFIG_FILE="$ROOT_DIR/config/markdown-link-check.json"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx is required to run markdown-link-check. Please install Node.js." >&2
  exit 1
fi

readarray -d '' MD_FILES < <(git -C "$ROOT_DIR" ls-files '*.md' -z)

if [ "${#MD_FILES[@]}" -eq 0 ]; then
  echo "No Markdown files detected."
  exit 0
fi

EXIT_CODE=0

for file in "${MD_FILES[@]}"; do
  echo "Checking links in $file"
  if [ -f "$CONFIG_FILE" ]; then
    npx --yes markdown-link-check@3.11.2 --quiet --config "$CONFIG_FILE" "$file" || EXIT_CODE=$?
  else
    npx --yes markdown-link-check@3.11.2 --quiet "$file" || EXIT_CODE=$?
  fi
done

exit "$EXIT_CODE"
