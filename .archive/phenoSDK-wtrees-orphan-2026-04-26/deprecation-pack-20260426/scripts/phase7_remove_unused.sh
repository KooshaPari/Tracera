#!/bin/bash
# Phase 7 - Remove unused files (LOC-reductive, least-breaking)

set -e

echo "🔧 Phase 7: Remove Unused Files"
echo "================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase7-unused-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count LOC before
BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# ============================================================================
# 1. Remove potentially unused large files
# ============================================================================
echo "🗑️  Removing potentially unused files..."
echo ""

# Verify each file is actually unused before deleting
UNUSED_FILES=(
    "src/pheno/testing/mcp_qa/adapters/fast_http_client.py"
    "src/pheno/infra/cloudflare_tunnel.py"
    "src/pheno/core/shared/typer_cli.py"
    "src/pheno/infra/enhanced_resource_coordinator.py"
    "src/pheno/infra/resources/lambda.py"
)

DELETED_LOC=0

for file in "${UNUSED_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Check if file is imported anywhere
        filename=$(basename "$file" .py)
        
        # Search for imports (excluding the file itself)
        import_count=$(grep -r "import $filename\|from.*$filename" src/pheno --include="*.py" 2>/dev/null | grep -v "$file" | wc -l || echo "0")
        
        if [ "$import_count" -eq "0" ]; then
            LOC=$(wc -l < "$file")
            DELETED_LOC=$((DELETED_LOC + LOC))
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            rm "$file"
            echo "  ✓ Deleted: $file ($LOC LOC) - No imports found"
        else
            echo "  ⚠ Skipped: $file - Found $import_count imports"
        fi
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Deleted $DELETED_LOC LOC from unused files"
echo ""

# ============================================================================
# 2. Remove empty/minimal files
# ============================================================================
echo "🗑️  Removing empty/minimal files..."
echo ""

MINIMAL_FILES=(
    "src/pheno/core/port_registry/lifecycle.py"
    "src/pheno/domain/exceptions/deployment.py"
    "src/pheno/domain/exceptions/infrastructure.py"
)

MINIMAL_DELETED=0

for file in "${MINIMAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        if [ "$LOC" -lt "10" ]; then
            MINIMAL_DELETED=$((MINIMAL_DELETED + LOC))
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            rm "$file"
            echo "  ✓ Deleted: $file ($LOC LOC)"
        fi
    fi
done

echo ""
print_status "Deleted $MINIMAL_DELETED LOC from minimal files"
echo ""

# ============================================================================
# Summary
# ============================================================================

TOTAL_DELETED=$((DELETED_LOC + MINIMAL_DELETED))

# Count LOC after
AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 After: $AFTER_LOC LOC"
echo ""

SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 7.1 Complete!"
echo "====================="
echo ""
echo "Summary:"
echo "  Unused files: $DELETED_LOC LOC"
echo "  Minimal files: $MINIMAL_DELETED LOC"
echo "  Total Deleted: $TOTAL_DELETED LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""

