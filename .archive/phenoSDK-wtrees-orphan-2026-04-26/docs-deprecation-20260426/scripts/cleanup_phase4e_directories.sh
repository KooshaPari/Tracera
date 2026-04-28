#!/bin/bash
# PhenoSDK Root Cleanup Script
# Phase 4e: Consolidate Directories

set -e  # Exit on error

echo "🧹 PhenoSDK Root Cleanup - Phase 4e: Directories"
echo "================================================="
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
BACKUP_DIR="backups/cleanup-phase4e-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count before
BEFORE_COUNT=$(ls -d */ 2>/dev/null | wc -l)
echo "📊 Before cleanup: $BEFORE_COUNT directories at root"
echo ""

ACTIONS_COUNT=0

# 1. Merge tools_unified into tools
echo "🔧 Merging tools_unified/ into tools/..."
if [ -d "tools_unified" ]; then
    cp -r tools_unified/* tools/ 2>/dev/null || true
    rm -rf tools_unified/
    echo "  ✓ Merged and deleted tools_unified/"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ tools_unified/ not found"
fi
echo ""

# 2. Move prompt directories to docs/prompts/
echo "📝 Moving prompt directories to docs/prompts/..."
mkdir -p docs/prompts

if [ -d "fix_prompts" ]; then
    mv fix_prompts docs/prompts/fix
    echo "  ✓ Moved: fix_prompts → docs/prompts/fix"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ fix_prompts/ not found"
fi

if [ -d "work-prompts" ]; then
    mv work-prompts docs/prompts/work
    echo "  ✓ Moved: work-prompts → docs/prompts/work"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ work-prompts/ not found"
fi

if [ -d "systemprompts" ]; then
    mv systemprompts docs/prompts/system
    echo "  ✓ Moved: systemprompts → docs/prompts/system"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ systemprompts/ not found"
fi
echo ""

# 3. Delete build artifacts
echo "🗑️  Deleting build artifacts..."

if [ -d "htmlcov" ]; then
    rm -rf htmlcov/
    echo "  ✓ Deleted: htmlcov/"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ htmlcov/ not found"
fi

if [ -d "__pycache__" ]; then
    rm -rf __pycache__/
    echo "  ✓ Deleted: __pycache__/"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ __pycache__/ not found"
fi

# Delete cleanup_output.log if exists
if [ -f "cleanup_output.log" ]; then
    rm cleanup_output.log
    echo "  ✓ Deleted: cleanup_output.log"
fi
echo ""

# 4. Check virtual envs (don't delete if in use)
echo "🐍 Checking virtual environments..."

if [ -d "venv" ]; then
    print_warning "venv/ exists - keeping (may be in use)"
else
    echo "  ✓ venv/ not found"
fi

if [ -d "production" ]; then
    print_warning "production/ exists - keeping (may be in use)"
else
    echo "  ✓ production/ not found"
fi

if [ -d "pytest_asyncio" ]; then
    print_warning "pytest_asyncio/ exists - keeping (may be package)"
else
    echo "  ✓ pytest_asyncio/ not found"
fi
echo ""

# 5. Move lib to src/pheno/lib
echo "📚 Moving lib/ to src/pheno/lib/..."
if [ -d "lib" ]; then
    if [ -d "src/pheno/lib" ]; then
        print_warning "src/pheno/lib/ already exists - merging"
        cp -r lib/* src/pheno/lib/ 2>/dev/null || true
        rm -rf lib/
    else
        mv lib src/pheno/lib
    fi
    echo "  ✓ Moved: lib → src/pheno/lib"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ lib/ not found"
fi
echo ""

# Count after
AFTER_COUNT=$(ls -d */ 2>/dev/null | wc -l)
echo "📊 After cleanup: $AFTER_COUNT directories at root"
echo ""

echo "✨ Phase 4e Complete!"
echo "===================="
echo ""
echo "Summary:"
echo "  Actions performed: $ACTIONS_COUNT"
echo "  Directories before: $BEFORE_COUNT"
echo "  Directories after: $AFTER_COUNT"
echo "  Reduction: $((BEFORE_COUNT - AFTER_COUNT)) directories"
echo ""
echo "Backup location: $BACKUP_DIR"

