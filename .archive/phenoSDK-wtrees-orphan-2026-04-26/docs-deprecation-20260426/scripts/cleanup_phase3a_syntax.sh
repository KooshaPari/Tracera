#!/bin/bash
# PhenoSDK Codebase Cleanup Script
# Phase 3a: Fix Syntax Errors

set -e  # Exit on error

echo "🧹 PhenoSDK Cleanup - Phase 3a: Fix Syntax Errors"
echo "=================================================="
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

# Check if we're in the right directory
if [ ! -d "src/pheno" ]; then
    echo "Error: Must run from pheno-sdk root directory"
    exit 1
fi

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase3a-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno "$BACKUP_DIR/"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Get list of files with syntax errors
echo "🔍 Finding files with syntax errors..."
SYNTAX_ERROR_FILES=$(ruff format src/pheno 2>&1 | grep "error: Failed to parse" | cut -d: -f2 | sort -u)

if [ -z "$SYNTAX_ERROR_FILES" ]; then
    print_status "No syntax errors found!"
    exit 0
fi

echo "Found syntax errors in the following files:"
echo "$SYNTAX_ERROR_FILES" | while read file; do
    echo "  - $file"
done
echo ""

# Count errors before
BEFORE_ERRORS=$(ruff check src/pheno --statistics 2>&1 | grep "^[0-9]" | head -1 | awk '{print $1}')

echo "📊 Before cleanup:"
echo "  Total errors: $BEFORE_ERRORS"
echo ""

# Step 1: Fix "Unexpected indentation" errors
echo "🔧 Step 1: Fixing 'Unexpected indentation' errors..."
echo ""

INDENT_FILES=$(ruff format src/pheno 2>&1 | grep "Unexpected indentation" | cut -d: -f2 | sort -u)

if [ -n "$INDENT_FILES" ]; then
    echo "$INDENT_FILES" | while read file; do
        if [ -f "$file" ]; then
            # Check if file starts with whitespace
            if head -1 "$file" | grep -q "^[[:space:]]"; then
                echo "  Fixing: $file (removing leading whitespace)"
                # Remove leading whitespace from first line
                sed -i '' '1s/^[[:space:]]*//' "$file"
            fi
        fi
    done
    print_status "Fixed 'Unexpected indentation' errors"
else
    echo "  No 'Unexpected indentation' errors found"
fi
echo ""

# Step 2: List files that need manual fixing
echo "📝 Step 2: Files that need manual review..."
echo ""

MANUAL_FIX_FILES=$(ruff format src/pheno 2>&1 | grep "error: Failed to parse" | grep -v "Unexpected indentation" | cut -d: -f2 | sort -u)

if [ -n "$MANUAL_FIX_FILES" ]; then
    echo "The following files have syntax errors that need manual fixing:"
    echo "$MANUAL_FIX_FILES" | while read file; do
        ERROR_MSG=$(ruff format src/pheno 2>&1 | grep "$file" | head -1)
        echo "  - $ERROR_MSG"
    done
    echo ""
    print_warning "These files need manual review and fixing"
else
    print_status "All syntax errors fixed automatically!"
fi
echo ""

# Count errors after
AFTER_ERRORS=$(ruff check src/pheno --statistics 2>&1 | grep "^[0-9]" | head -1 | awk '{print $1}')

# Generate report
echo "📊 Step 3: Generating cleanup report..."
REPORT_FILE="reports/cleanup-phase3a-syntax-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p reports

{
    echo "PhenoSDK Cleanup Phase 3a - Syntax Errors Report"
    echo "================================================"
    echo "Date: $(date)"
    echo ""
    echo "Errors Before: $BEFORE_ERRORS"
    echo "Errors After: $AFTER_ERRORS"
    echo "Errors Fixed: $((BEFORE_ERRORS - AFTER_ERRORS))"
    echo ""
    echo "Files with Syntax Errors:"
    echo "------------------------"
    echo "$SYNTAX_ERROR_FILES"
    echo ""
    echo "Files Needing Manual Fix:"
    echo "------------------------"
    echo "$MANUAL_FIX_FILES"
} > "$REPORT_FILE"

print_status "Report saved to $REPORT_FILE"
echo ""

# Summary
echo "✨ Cleanup Phase 3a (Syntax Errors) Complete!"
echo "============================================="
echo ""
echo "Summary:"
echo "  Errors before: $BEFORE_ERRORS"
echo "  Errors after: $AFTER_ERRORS"
echo "  Errors fixed: $((BEFORE_ERRORS - AFTER_ERRORS))"
echo ""
echo "Backup location: $BACKUP_DIR"
echo "Report location: $REPORT_FILE"

