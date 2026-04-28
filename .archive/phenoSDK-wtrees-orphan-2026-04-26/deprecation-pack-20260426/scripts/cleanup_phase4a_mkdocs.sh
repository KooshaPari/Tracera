#!/bin/bash
# PhenoSDK Root Cleanup Script
# Phase 4a: Consolidate MkDocs Configs

set -e  # Exit on error

echo "🧹 PhenoSDK Root Cleanup - Phase 4a: MkDocs Configs"
echo "===================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase4a-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp mkdocs*.yml "$BACKUP_DIR/" 2>/dev/null || true
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count before
BEFORE_COUNT=$(ls -1 mkdocs*.yml 2>/dev/null | wc -l)
echo "📊 Before cleanup: $BEFORE_COUNT mkdocs config files"
echo ""

# Delete duplicate mkdocs configs
echo "🗑️  Deleting duplicate mkdocs configs..."
echo ""

MKDOCS_FILES=(
    "mkdocs-backup.yml"
    "mkdocs-canonical.yml"
    "mkdocs-clean.yml"
    "mkdocs-complete.yml"
    "mkdocs-comprehensive.yml"
    "mkdocs-final.yml"
    "mkdocs-minimal-test.yml"
    "mkdocs-minimal.yml"
    "mkdocs-simple.yml"
    "mkdocs.yml.backup"
)

DELETED_COUNT=0

for file in "${MKDOCS_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  ✓ Deleted: $file"
        DELETED_COUNT=$((DELETED_COUNT + 1))
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Deleted $DELETED_COUNT mkdocs config files"
echo ""

# Count after
AFTER_COUNT=$(ls -1 mkdocs*.yml 2>/dev/null | wc -l)
echo "📊 After cleanup: $AFTER_COUNT mkdocs config files"
echo ""

# Verify mkdocs.yml exists
if [ -f "mkdocs.yml" ]; then
    print_status "Main mkdocs.yml exists"
else
    print_warning "Main mkdocs.yml NOT FOUND!"
fi

echo ""
echo "✨ Phase 4a Complete!"
echo "===================="
echo ""
echo "Summary:"
echo "  Deleted: $DELETED_COUNT files"
echo "  Remaining: $AFTER_COUNT file (mkdocs.yml)"
echo ""
echo "Backup location: $BACKUP_DIR"

