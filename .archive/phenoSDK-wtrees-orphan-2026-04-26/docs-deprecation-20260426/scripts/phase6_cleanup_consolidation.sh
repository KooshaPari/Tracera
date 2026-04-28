#!/bin/bash
# Phase 6: Cleanup & Consolidation
# Target: -20,000 LOC

set -e

BACKUP_DIR="backups/phase6-cleanup-consolidation-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 6: Cleanup & Consolidation ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup
mkdir -p "$BACKUP_DIR"

echo "Step 1: Identifying files and directories to delete..."

# Old/deprecated directories
OLD_DIRS=(
    "src/pheno/dev/meilisearch_integration_old"
    "src/pheno/llm/optimization/context_folding"
)

# Example/demo files (not needed in production)
EXAMPLE_FILES=(
    "src/pheno/ui/tui/process_monitor/example.py"
    "src/pheno/infra/fallback_site/example_usage.py"
    "src/pheno/infra/resources/examples.py"
    "src/pheno/core/environment/demo_url_switching.py"
    "src/pheno/core/environment/examples.py"
    "src/pheno/credentials/examples.py"
)

# Legacy files
LEGACY_FILES=(
    "src/pheno/credentials/detect/legacy.py"
)

# Large files that can be simplified (we'll analyze these separately)
# For now, just delete truly unused ones

echo "Step 2: Backing up files and directories..."

for dir in "${OLD_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  Backing up directory: $dir"
        mkdir -p "$BACKUP_DIR/$(dirname "$dir")"
        cp -r "$dir" "$BACKUP_DIR/$dir"
    fi
done

for file in "${EXAMPLE_FILES[@]}" "${LEGACY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Backing up file: $file"
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
    fi
done

echo ""
echo "Step 3: Counting LOC before deletion..."
TOTAL_LOC=0
ITEMS_FOUND=0

for dir in "${OLD_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        LOC=$(find "$dir" -name "*.py" -type f | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        if [ -n "$LOC" ] && [ "$LOC" != "0" ]; then
            echo "  $dir: $LOC LOC"
            TOTAL_LOC=$((TOTAL_LOC + LOC))
            ITEMS_FOUND=$((ITEMS_FOUND + 1))
        fi
    fi
done

for file in "${EXAMPLE_FILES[@]}" "${LEGACY_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
        ITEMS_FOUND=$((ITEMS_FOUND + 1))
    fi
done

echo "  Total items: $ITEMS_FOUND"
echo "  Total LOC: $TOTAL_LOC"

echo ""
echo "Step 4: Deleting files and directories..."

for dir in "${OLD_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  Deleting directory: $dir"
        rm -rf "$dir"
    fi
done

for file in "${EXAMPLE_FILES[@]}" "${LEGACY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting file: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 5: Finding and analyzing large files for potential simplification..."

# Create a report of large files (>500 LOC) for manual review
echo "  Generating large files report..."
find src -name "*.py" -type f -exec wc -l {} + 2>/dev/null | \
    awk '$1 > 500 {print $1, $2}' | \
    sort -rn > "$BACKUP_DIR/large_files_report.txt"

LARGE_FILES_COUNT=$(wc -l < "$BACKUP_DIR/large_files_report.txt")
echo "  Found $LARGE_FILES_COUNT files >500 LOC"
echo "  Report saved to: $BACKUP_DIR/large_files_report.txt"

echo ""
echo "Step 6: Finding duplicate code patterns..."

# Find files with similar names (potential duplicates)
echo "  Searching for potential duplicates..."
find src -name "*.py" -type f | \
    xargs -I {} basename {} | \
    sort | uniq -d > "$BACKUP_DIR/duplicate_filenames.txt"

DUPLICATE_NAMES=$(wc -l < "$BACKUP_DIR/duplicate_filenames.txt")
echo "  Found $DUPLICATE_NAMES duplicate filenames"
echo "  Report saved to: $BACKUP_DIR/duplicate_filenames.txt"

echo ""
echo "Step 7: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Phase 6 Cleanup & Consolidation Migration Guide

## What Changed

Deleted old/deprecated code, example files, and legacy implementations.

## Directories Deleted

1. `src/pheno/dev/meilisearch_integration_old/` (768 LOC)
   - Old meilisearch integration
   - Use modern meilisearch integration instead

2. `src/pheno/llm/optimization/context_folding/` (677 LOC)
   - Old context folding implementation
   - Use modern LLM optimization instead

## Files Deleted

### Example/Demo Files (6 files)
1. `src/pheno/ui/tui/process_monitor/example.py`
2. `src/pheno/infra/fallback_site/example_usage.py`
3. `src/pheno/infra/resources/examples.py`
4. `src/pheno/core/environment/demo_url_switching.py`
5. `src/pheno/core/environment/examples.py`
6. `src/pheno/credentials/examples.py`

### Legacy Files (1 file)
7. `src/pheno/credentials/detect/legacy.py`

## Migration Path

### Meilisearch Integration

```python
# Before (old)
from pheno.dev.meilisearch_integration_old import MeilisearchManager

# After (modern)
from pheno.dev.meilisearch import MeilisearchManager
```

### Context Folding

```python
# Before (old)
from pheno.llm.optimization.context_folding import ContextFolder

# After (modern)
from pheno.llm.optimization import ContextOptimizer
```

### Examples

Example files were for demonstration only. Remove any imports from:
- `*.example.py`
- `*example_usage.py`
- `*examples.py`
- `*demo*.py`

## Reports Generated

### Large Files Report
- `large_files_report.txt` - Files >500 LOC
- Review these for potential simplification

### Duplicate Filenames Report
- `duplicate_filenames.txt` - Files with same name in different dirs
- Review these for potential consolidation

## Benefits

1. **Less Code**: Removed old/deprecated implementations
2. **Cleaner Codebase**: No example/demo files in production
3. **Less Confusion**: Only modern implementations remain
4. **Better Maintenance**: Fewer files to maintain

## Next Steps

1. Review large files report for simplification opportunities
2. Review duplicate filenames for consolidation
3. Run tests to verify nothing broke

## Rollback

```bash
cp -r backups/phase6-cleanup-consolidation-*/src/* src/
```
EOF

echo ""
echo "Step 8: Summary"
echo "  Items deleted: $ITEMS_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Large files found: $LARGE_FILES_COUNT"
echo "  Duplicate filenames: $DUPLICATE_NAMES"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 6 Initial Cleanup Complete!"
echo ""
echo "Next steps:"
echo "  1. Review large_files_report.txt for simplification"
echo "  2. Review duplicate_filenames.txt for consolidation"
echo "  3. Run tests: pytest tests/ -v"

