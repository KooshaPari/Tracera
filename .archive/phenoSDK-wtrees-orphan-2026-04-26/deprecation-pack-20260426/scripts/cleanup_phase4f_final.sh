#!/bin/bash
# PhenoSDK Root Cleanup Script
# Phase 4f: Final Organization

set -e  # Exit on error

echo "🧹 PhenoSDK Root Cleanup - Phase 4f: Final Organization"
echo "========================================================"
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
BACKUP_DIR="backups/cleanup-phase4f-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count before
BEFORE_COUNT=$(ls -d */ 2>/dev/null | wc -l)
echo "📊 Before cleanup: $BEFORE_COUNT directories at root"
echo ""

ACTIONS_COUNT=0

# 1. Move analysis to reports
echo "📊 Moving analysis/ to reports/..."
if [ -d "analysis" ]; then
    mv analysis reports/
    echo "  ✓ Moved: analysis → reports/"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ analysis/ not found"
fi
echo ""

# 2. Move benchmarks to tests
echo "⚡ Moving benchmarks/ to tests/..."
if [ -d "benchmarks" ]; then
    if [ -d "tests/benchmarks" ]; then
        print_warning "tests/benchmarks/ already exists - merging"
        cp -r benchmarks/* tests/benchmarks/ 2>/dev/null || true
        rm -rf benchmarks/
    else
        mv benchmarks tests/
    fi
    echo "  ✓ Moved: benchmarks → tests/"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ benchmarks/ not found"
fi
echo ""

# 3. Move openspec to docs
echo "📋 Moving openspec/ to docs/..."
if [ -d "openspec" ]; then
    mv openspec docs/specs
    echo "  ✓ Moved: openspec → docs/specs"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ openspec/ not found"
fi
echo ""

# 4. Move quality to tools
echo "🔍 Moving quality/ to tools/..."
if [ -d "quality" ]; then
    if [ -d "tools/quality" ]; then
        print_warning "tools/quality/ already exists - merging"
        cp -r quality/* tools/quality/ 2>/dev/null || true
        rm -rf quality/
    else
        mv quality tools/
    fi
    echo "  ✓ Moved: quality → tools/"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ quality/ not found"
fi
echo ""

# 5. Move settings to config
echo "⚙️  Moving settings/ to config/..."
if [ -d "settings" ]; then
    mv settings config/
    echo "  ✓ Moved: settings → config/"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ settings/ not found"
fi
echo ""

# 6. Move pheno_sdk_benchmarks to tests
echo "📈 Moving pheno_sdk_benchmarks/ to tests/..."
if [ -d "pheno_sdk_benchmarks" ]; then
    if [ -d "tests/benchmarks" ]; then
        cp -r pheno_sdk_benchmarks/* tests/benchmarks/ 2>/dev/null || true
        rm -rf pheno_sdk_benchmarks/
    else
        mv pheno_sdk_benchmarks tests/benchmarks
    fi
    echo "  ✓ Moved: pheno_sdk_benchmarks → tests/benchmarks"
    ACTIONS_COUNT=$((ACTIONS_COUNT + 1))
else
    echo "  ⚠ pheno_sdk_benchmarks/ not found"
fi
echo ""

# Count after
AFTER_COUNT=$(ls -d */ 2>/dev/null | wc -l)
echo "📊 After cleanup: $AFTER_COUNT directories at root"
echo ""

# List remaining directories
echo "📁 Remaining directories at root:"
ls -d */ | head -30
echo ""

echo "✨ Phase 4f Complete!"
echo "===================="
echo ""
echo "Summary:"
echo "  Actions performed: $ACTIONS_COUNT"
echo "  Directories before: $BEFORE_COUNT"
echo "  Directories after: $AFTER_COUNT"
echo "  Reduction: $((BEFORE_COUNT - AFTER_COUNT)) directories"
echo ""
echo "Backup location: $BACKUP_DIR"

