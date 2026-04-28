#!/bin/bash
# PhenoSDK Root Cleanup Script
# Phase 4d: Consolidate Baseline Files

set -e  # Exit on error

echo "🧹 PhenoSDK Root Cleanup - Phase 4d: Baseline Files"
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
BACKUP_DIR="backups/cleanup-phase4d-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp *baseline* *report*.json coverage.* 2>/dev/null "$BACKUP_DIR/" || true
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count before
BEFORE_COUNT=$(ls -1 *baseline* *report*.json coverage.* 2>/dev/null | wc -l)
echo "📊 Before cleanup: $BEFORE_COUNT baseline/report files at root"
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p reports/baselines
print_status "Directories created"
echo ""

# Move baseline files
echo "📊 Moving baseline files to reports/baselines/..."
echo ""

BASELINE_FILES=(
    "bandit_baseline.json"
    "coverage_baseline.txt"
    "mypy_baseline.txt"
    "ruff_baseline.json"
)

MOVED_BASELINES=0

for file in "${BASELINE_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "reports/baselines/"
        echo "  ✓ Moved: $file → reports/baselines/"
        MOVED_BASELINES=$((MOVED_BASELINES + 1))
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Moved $MOVED_BASELINES baseline files"
echo ""

# Move report files
echo "📋 Moving report files to reports/..."
echo ""

REPORT_FILES=(
    "bandit-report.json"
    "coverage.json"
    "coverage.xml"
)

MOVED_REPORTS=0

for file in "${REPORT_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "reports/"
        echo "  ✓ Moved: $file → reports/"
        MOVED_REPORTS=$((MOVED_REPORTS + 1))
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Moved $MOVED_REPORTS report files"
echo ""

# Count after
AFTER_COUNT=$(ls -1 *baseline* *report*.json coverage.* 2>/dev/null | wc -l)
echo "📊 After cleanup: $AFTER_COUNT baseline/report files at root"
echo ""

echo "✨ Phase 4d Complete!"
echo "===================="
echo ""
echo "Summary:"
echo "  Moved to reports/baselines/: $MOVED_BASELINES files"
echo "  Moved to reports/: $MOVED_REPORTS files"
echo "  Total removed from root: $((MOVED_BASELINES + MOVED_REPORTS)) files"
echo ""
echo "Backup location: $BACKUP_DIR"

