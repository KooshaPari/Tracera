#!/bin/bash
# Phase 11.2 - Execute final cleanup

set -e

echo "🔧 Phase 11.2: Execute Final Cleanup"
echo "====================================="
echo ""

GREEN='\033[0;32m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
BACKUP_DIR="backups/cleanup-phase11-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup: $BACKUP_DIR"
echo ""

BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# ============================================================================
# 1. Move example files to examples/ directory
# ============================================================================
echo "📦 1. Moving example files to examples/..."
echo ""

EXAMPLE_FILES=(
    "src/pheno/testing/conftest_template.py"
    "src/pheno/dev/pytest_asyncio_integration.py"
    "src/pheno/mcp/qa/pytest_plugins.py"
    "src/pheno/testing/modes/pytest_plugin.py"
    "src/pheno/testing/adapters/pytest_runner.py"
)

MOVED_LOC=0

for file in "${EXAMPLE_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Check if imported
        filename=$(basename "$file" .py)
        import_count=$(grep -r "import $filename\|from.*$filename" src/pheno --include="*.py" 2>/dev/null | grep -v "$file" | wc -l || echo "0")
        
        if [ "$import_count" -eq "0" ]; then
            LOC=$(wc -l < "$file")
            MOVED_LOC=$((MOVED_LOC + LOC))
            
            # Backup
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            
            # Move to examples
            target_dir="examples/$(dirname ${file#src/pheno/})"
            mkdir -p "$target_dir"
            mv "$file" "$target_dir/"
            
            echo "  ✓ Moved: $file ($LOC LOC)"
        else
            echo "  ⚠ Skipped: $file ($import_count imports)"
        fi
    fi
done

print_status "Moved examples: $MOVED_LOC LOC"
echo ""

# ============================================================================
# 2. Remove files with only old-style classes (if unused)
# ============================================================================
echo "🗑️  2. Checking old-style code files..."
echo ""

OLD_STYLE=(
    "src/pheno/database/storage.py"
)

OLD_STYLE_DELETED=0

for file in "${OLD_STYLE[@]}"; do
    if [ -f "$file" ]; then
        import_count=$(grep -r "storage" src/pheno --include="*.py" 2>/dev/null | grep -v "$file" | wc -l || echo "0")
        
        if [ "$import_count" -lt "5" ]; then
            LOC=$(wc -l < "$file")
            OLD_STYLE_DELETED=$((OLD_STYLE_DELETED + LOC))
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            rm "$file"
            echo "  ✓ Deleted: $file ($LOC LOC)"
        else
            echo "  ⚠ Skipped: $file ($import_count imports)"
        fi
    fi
done

print_status "Old-style removed: $OLD_STYLE_DELETED LOC"
echo ""

# ============================================================================
# Summary
# ============================================================================

TOTAL_CLEANED=$((MOVED_LOC + OLD_STYLE_DELETED))

AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 11.2 Complete!"
echo "======================"
echo ""
echo "  Moved examples: $MOVED_LOC LOC"
echo "  Old-style removed: $OLD_STYLE_DELETED LOC"
echo "  Total: $TOTAL_CLEANED LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup: $BACKUP_DIR"

