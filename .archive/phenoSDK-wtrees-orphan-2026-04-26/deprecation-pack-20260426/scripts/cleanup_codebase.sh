#!/bin/bash
# PhenoSDK Codebase Cleanup Script
# Phase 1: Quick Wins - Delete dead code and fix auto-fixable issues

set -e  # Exit on error

echo "🧹 PhenoSDK Codebase Cleanup - Phase 1: Quick Wins"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "src/pheno" ]; then
    print_error "Error: Must run from pheno-sdk root directory"
    exit 1
fi

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno "$BACKUP_DIR/"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Step 1: Delete old/deprecated files
echo "🗑️  Step 1: Deleting old/deprecated files..."
OLD_FILES=$(find src/pheno -name "*_old.py" -o -name "*_backup.py" -o -name "*_deprecated.py")
if [ -n "$OLD_FILES" ]; then
    echo "$OLD_FILES" | while read file; do
        echo "  Deleting: $file"
        rm "$file"
    done
    print_status "Deleted $(echo "$OLD_FILES" | wc -l) old files"
else
    print_warning "No old files found"
fi
echo ""

# Step 2: Delete __pycache__ directories
echo "🗑️  Step 2: Deleting __pycache__ directories..."
PYCACHE_COUNT=$(find src/pheno -type d -name "__pycache__" | wc -l)
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    find src/pheno -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    print_status "Deleted $PYCACHE_COUNT __pycache__ directories"
else
    print_warning "No __pycache__ directories found"
fi
echo ""

# Step 3: Delete .pyc files
echo "🗑️  Step 3: Deleting .pyc files..."
PYC_COUNT=$(find src/pheno -name "*.pyc" | wc -l)
if [ "$PYC_COUNT" -gt 0 ]; then
    find src/pheno -name "*.pyc" -delete
    print_status "Deleted $PYC_COUNT .pyc files"
else
    print_warning "No .pyc files found"
fi
echo ""

# Step 4: Run ruff auto-fix
echo "🔧 Step 4: Running ruff auto-fix..."
if command -v ruff &> /dev/null; then
    ruff check src/pheno --fix --unsafe-fixes || true
    print_status "Ruff auto-fix complete"
else
    print_warning "Ruff not installed, skipping auto-fix"
fi
echo ""

# Step 5: Run ruff format
echo "🎨 Step 5: Running ruff format..."
if command -v ruff &> /dev/null; then
    ruff format src/pheno || true
    print_status "Ruff format complete"
else
    print_warning "Ruff not installed, skipping format"
fi
echo ""

# Step 6: Remove unused imports (if autoflake is installed)
echo "🔧 Step 6: Removing unused imports..."
if command -v autoflake &> /dev/null; then
    autoflake --remove-all-unused-imports --in-place --recursive src/pheno || true
    print_status "Unused imports removed"
else
    print_warning "Autoflake not installed, skipping unused import removal"
    echo "  Install with: pip install autoflake"
fi
echo ""

# Step 7: Sort imports (if isort is installed)
echo "📋 Step 7: Sorting imports..."
if command -v isort &> /dev/null; then
    isort src/pheno || true
    print_status "Imports sorted"
else
    print_warning "Isort not installed, skipping import sorting"
    echo "  Install with: pip install isort"
fi
echo ""

# Step 8: Generate cleanup report
echo "📊 Step 8: Generating cleanup report..."
REPORT_FILE="reports/cleanup-report-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p reports

{
    echo "PhenoSDK Cleanup Report"
    echo "======================="
    echo "Date: $(date)"
    echo ""
    echo "Files Deleted:"
    echo "-------------"
    echo "Old files: $(echo "$OLD_FILES" | wc -l)"
    echo "__pycache__ dirs: $PYCACHE_COUNT"
    echo ".pyc files: $PYC_COUNT"
    echo ""
    echo "Current State:"
    echo "-------------"
    echo "Python files: $(find src/pheno -name "*.py" | wc -l)"
    echo "Lines of code: $(cloc src/pheno --json 2>/dev/null | jq '.Python.code' || echo 'N/A')"
    echo ""
    echo "Remaining Issues:"
    echo "----------------"
    ruff check src/pheno --statistics 2>&1 || echo "Ruff not available"
} > "$REPORT_FILE"

print_status "Report saved to $REPORT_FILE"
echo ""

# Summary
echo "✨ Cleanup Phase 1 Complete!"
echo "============================"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run tests: pytest tests/"
echo "  3. Commit changes: git add -A && git commit -m 'chore: cleanup phase 1 - remove dead code'"
echo "  4. Proceed to Phase 2: scripts/cleanup_phase2.sh"
echo ""
echo "Backup location: $BACKUP_DIR"
echo "Report location: $REPORT_FILE"

