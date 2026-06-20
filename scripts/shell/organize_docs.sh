#!/bin/bash
# organize_docs.sh - Organize markdown files into proper docs/ subdirectories
# Follows the documentation structure defined in CLAUDE.md

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ALLOWED_ROOT_FILES=(
  "README.md"
  "CHANGELOG.md"
  "AGENTS.md"
  "CLAUDE.md"
  "claude.md"
  "00_START_HERE.md"
)

# Create docs subdirectories if they don't exist
mkdir -p "$REPO_ROOT/docs/guides/quick-start"
mkdir -p "$REPO_ROOT/docs/reference"
mkdir -p "$REPO_ROOT/docs/guides"
mkdir -p "$REPO_ROOT/docs/reports"
mkdir -p "$REPO_ROOT/docs/research"
mkdir -p "$REPO_ROOT/docs/checklists"

# Function to check if file is in allowed list
is_allowed_root_file() {
  local filename="$1"
  for allowed in "${ALLOWED_ROOT_FILES[@]}"; do
    if [[ "$filename" == "$allowed" ]]; then
      return 0
    fi
  done
  return 1
}

# Function to determine target directory based on filename
get_target_dir() {
  local filename="$1"

  # Quick Starts
  if [[ "$filename" =~ QUICK_START|QUICKSTART ]]; then
    echo "docs/guides/quick-start"
    return
  fi

  # Quick References
  if [[ "$filename" =~ QUICK_REFERENCE|QUICK_REF ]]; then
    echo "docs/reference"
    return
  fi

  # Implementation Guides
  if [[ "$filename" =~ IMPLEMENTATION_GUIDE|GUIDE ]] && [[ ! "$filename" =~ RESEARCH ]]; then
    echo "docs/guides"
    return
  fi

  # Completion Reports and Summaries
  if [[ "$filename" =~ COMPLETE|COMPLETION|SUMMARY|REPORT|^PHASE_|TEST ]] && [[ ! "$filename" =~ RESEARCH|GUIDE ]]; then
    echo "docs/reports"
    return
  fi

  # Research Files
  if [[ "$filename" =~ RESEARCH|INDEX ]] && [[ ! "$filename" =~ GUIDE ]]; then
    echo "docs/research"
    return
  fi

  # Checklists
  if [[ "$filename" =~ CHECKLIST ]]; then
    echo "docs/checklists"
    return
  fi

  # Default to reports for anything else with .md extension
  echo "docs/reports"
}

# Count statistics
moved=0
skipped=0
errors=0

echo "Starting documentation organization..."
echo "======================================="
echo "Processing markdown files in root directory..."
echo ""

# Process all .md files in root
for file in "$REPO_ROOT"/*.md; do
  if [ ! -f "$file" ]; then
    continue
  fi

  filename=$(basename "$file")

  # Skip allowed root files
  if is_allowed_root_file "$filename"; then
    echo "✓ Keeping $filename (allowed in root)"
    skipped=$((skipped + 1))
    continue
  fi

  # Skip CLAUDE.md specifically (case-insensitive)
  if [[ "$filename" == "CLAUDE.md" ]] || [[ "$filename" == "claude.md" ]]; then
    echo "✓ Keeping $filename (project instructions)"
    skipped=$((skipped + 1))
    continue
  fi

  # Determine target directory
  target_dir=$(get_target_dir "$filename")
  target_file="$REPO_ROOT/$target_dir/$filename"

  # Skip if already in correct location
  if [[ "$(dirname "$file")" == "$REPO_ROOT/$target_dir" ]]; then
    echo "✓ Already organized: $filename -> $target_dir"
    skipped=$((skipped + 1))
    continue
  fi

  # Move file
  if mv "$file" "$target_file"; then
    echo "→ Moved: $filename -> $target_dir/"
    moved=$((moved + 1))
  else
    echo "✗ Error moving: $filename"
    errors=$((errors + 1))
  fi
done

echo ""
echo "======================================="
echo "Organization Summary"
echo "======================================="
echo "Files moved:  $moved"
echo "Files skipped: $skipped"
echo "Errors:       $errors"
echo ""
echo "Documentation structure:"
echo "  docs/guides/quick-start/    - Quick start guides"
echo "  docs/reference/             - Quick references and API docs"
echo "  docs/guides/                - Implementation guides"
echo "  docs/reports/               - Completion reports and summaries"
echo "  docs/research/              - Research and analysis documents"
echo "  docs/checklists/            - Implementation checklists"
echo ""

if [ $errors -eq 0 ]; then
  echo "✓ Organization complete!"
  exit 0
else
  echo "✗ Organization completed with $errors error(s)"
  exit 1
fi
