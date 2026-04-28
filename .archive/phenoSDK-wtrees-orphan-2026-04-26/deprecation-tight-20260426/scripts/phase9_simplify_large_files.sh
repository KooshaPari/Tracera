#!/bin/bash
# Phase 9.2 - Simplify large files

set -e

echo "🔧 Phase 9.2: Simplify Large Files"
echo "==================================="
echo ""

GREEN='\033[0;32m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
BACKUP_DIR="backups/cleanup-phase9-large-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup: $BACKUP_DIR"
echo ""

BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# ============================================================================
# Strategy: Remove files that are likely unused or can be simplified
# ============================================================================

echo "🗑️  Removing/simplifying large files..."
echo ""

# Files to check and potentially remove
LARGE_FILES=(
    "src/pheno/lib/deployment_checker.py"
    "src/pheno/infra/proxy_gateway.py"
    "src/pheno/infra/cloudflare_tunnel.py"
    "src/pheno/infra/fallback_site/fallback_server.py"
    "src/pheno/quality/export_import.py"
    "src/pheno/adapters/providers/usage_collectors/infrastructure/loaders/cursor_loader.py"
    "src/pheno/adapters/providers/usage_collectors/infrastructure/loaders/codex_loader.py"
    "src/pheno/core/database/factories.py"
    "src/pheno/core/shared/utilities/migration_helper.py"
)

DELETED_LOC=0

for file in "${LARGE_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Check if imported
        filename=$(basename "$file" .py)
        import_count=$(grep -r "import $filename\|from.*$filename" src/pheno --include="*.py" 2>/dev/null | grep -v "$file" | wc -l || echo "0")
        
        if [ "$import_count" -eq "0" ]; then
            LOC=$(wc -l < "$file")
            DELETED_LOC=$((DELETED_LOC + LOC))
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            rm "$file"
            echo "  ✓ Deleted: $file ($LOC LOC) - No imports"
        else
            echo "  ⚠ Skipped: $file ($import_count imports)"
        fi
    fi
done

echo ""
print_status "Deleted: $DELETED_LOC LOC"
echo ""

# ============================================================================
# Summary
# ============================================================================

AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 9.2 Complete!"
echo "====================="
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup: $BACKUP_DIR"

