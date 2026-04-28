#!/bin/bash
# PhenoSDK Root Cleanup Script
# Phase 4c: Consolidate Documentation

set -e  # Exit on error

echo "🧹 PhenoSDK Root Cleanup - Phase 4c: Documentation"
echo "==================================================="
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
BACKUP_DIR="backups/cleanup-phase4c-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp *.md "$BACKUP_DIR/" 2>/dev/null || true
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count before
BEFORE_COUNT=$(ls -1 *.md 2>/dev/null | wc -l)
echo "📊 Before cleanup: $BEFORE_COUNT markdown files at root"
echo ""

# Move markdown files to docs/
echo "📝 Moving markdown files to docs/..."
echo ""

MARKDOWN_FILES=(
    "AGENTS.md"
    "CLAUDE.md"
    "CONSOLIDATION_COMPLETE.md"
    "CONSOLIDATION_COMPLETE_REPORT.md"
)

MOVED_COUNT=0

for file in "${MARKDOWN_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Check if file already exists in docs/
        if [ -f "docs/$file" ]; then
            echo "  ⚠ Already exists in docs/, deleting root copy: $file"
            rm "$file"
        else
            mv "$file" "docs/"
            echo "  ✓ Moved: $file → docs/"
        fi
        MOVED_COUNT=$((MOVED_COUNT + 1))
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Processed $MOVED_COUNT markdown files"
echo ""

# Verify README.md exists
if [ -f "README.md" ]; then
    print_status "Main README.md kept at root"
else
    print_warning "Main README.md NOT FOUND!"
fi

echo ""

# Count after
AFTER_COUNT=$(ls -1 *.md 2>/dev/null | wc -l)
echo "📊 After cleanup: $AFTER_COUNT markdown files at root"
echo ""

echo "✨ Phase 4c Complete!"
echo "===================="
echo ""
echo "Summary:"
echo "  Processed: $MOVED_COUNT files"
echo "  Remaining at root: $AFTER_COUNT file (README.md)"
echo ""
echo "Backup location: $BACKUP_DIR"

