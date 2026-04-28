#!/bin/bash
# PhenoSDK Codebase Cleanup Script
# Phase 2: Delete Factory Files (keep exception_factory/)

set -e  # Exit on error

echo "🧹 PhenoSDK Cleanup - Phase 2: Delete Factory Files"
echo "===================================================="
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
BACKUP_DIR="backups/cleanup-phase2-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno "$BACKUP_DIR/"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Create archive directory for deleted files
ARCHIVE_DIR="archives/archive/cleanup_phase2_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"
print_status "Archive directory created at $ARCHIVE_DIR"
echo ""

# Count files before
BEFORE_COUNT=$(find src/pheno -name "*.py" -type f | wc -l)
BEFORE_LINES=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')

echo "📊 Before cleanup:"
echo "  Python files: $BEFORE_COUNT"
echo "  Lines of code: $BEFORE_LINES"
echo ""

# Step 1: Delete factory files (EXCEPT exception_factory/)
echo "🗑️  Step 1: Deleting factory files..."
echo ""

# List of factory files to DELETE (keep exception_factory/)
FACTORY_FILES=(
    "src/pheno/core/adapter_factory.py"
    "src/pheno/core/api_factory.py"
    "src/pheno/core/configuration_factory.py"
    "src/pheno/core/database_factory.py"
    "src/pheno/core/factory_factory.py"
    "src/pheno/core/factory_registry.py"
    "src/pheno/core/logging_factory.py"
    "src/pheno/core/manager_factory.py"
    "src/pheno/core/monitoring_factory.py"
    "src/pheno/core/port_factory.py"
    "src/pheno/core/security_factory.py"
    "src/pheno/core/storage_factory.py"
    "src/pheno/core/testing_factory.py"
    "src/pheno/core/unified_factory.py"
    "src/pheno/core/utility_factory.py"
    "src/pheno/core/validator_factory.py"
    "src/pheno/core/database/factory/connection.py"
    "src/pheno/core/database/factory/factory.py"
    "src/pheno/core/database/factory/pool.py"
    "src/pheno/core/factories/adapter/builder.py"
    "src/pheno/core/factories/adapter/factory.py"
    "src/pheno/core/factories/adapter/registry.py"
    "src/pheno/core/factories/config/builder.py"
    "src/pheno/core/factories/config/factory.py"
    "src/pheno/core/factories/config/loader.py"
    "src/pheno/core/factories/core/factory.py"
    "src/pheno/core/managers/factory_manager.py"
    "src/pheno/core/security_factory/factory_core.py"
    "src/pheno/core/security_factory/factory_manager.py"
    "src/pheno/core/shared/configuration/factory.py"
    "src/pheno/core/shared/factories/unified/factory.py"
    "src/pheno/core/shared/utilities/factory.py"
)

# KEEP these:
# - src/pheno/core/exception_factory.py (re-export file)
# - src/pheno/core/exception_factory/ (directory with actual implementation)
# - src/pheno/infra/resources/network_factory.py (infrastructure)
# - src/pheno/infra/resources/storage_factory.py (infrastructure)
# - src/pheno/llm/routing/ensemble/factory.py (domain-specific)
# - src/pheno/vector/providers/factory.py (domain-specific)

DELETED_COUNT=0
DELETED_LINES=0

for file in "${FACTORY_FILES[@]}"; do
    if [ -f "$file" ]; then
        # Count lines before deleting
        LINES=$(wc -l < "$file")
        DELETED_LINES=$((DELETED_LINES + LINES))
        
        # Move to archive
        ARCHIVE_PATH="$ARCHIVE_DIR/$(basename $file)"
        cp "$file" "$ARCHIVE_PATH"
        
        # Delete the file
        rm "$file"
        
        echo "  ✓ Deleted: $file ($LINES lines)"
        DELETED_COUNT=$((DELETED_COUNT + 1))
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Deleted $DELETED_COUNT factory files ($DELETED_LINES lines)"
echo ""

# Step 2: Delete empty factory directories
echo "🗑️  Step 2: Deleting empty factory directories..."
echo ""

FACTORY_DIRS=(
    "src/pheno/core/database/factory"
    "src/pheno/core/factories/adapter"
    "src/pheno/core/factories/config"
    "src/pheno/core/factories/core"
    "src/pheno/core/security_factory"
)

DELETED_DIRS=0

for dir in "${FACTORY_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        # Check if directory is empty (only __init__.py or completely empty)
        FILE_COUNT=$(find "$dir" -type f -name "*.py" ! -name "__init__.py" | wc -l)
        
        if [ "$FILE_COUNT" -eq 0 ]; then
            rm -rf "$dir"
            echo "  ✓ Deleted empty directory: $dir"
            DELETED_DIRS=$((DELETED_DIRS + 1))
        else
            echo "  ⚠ Directory not empty: $dir ($FILE_COUNT files remaining)"
        fi
    else
        echo "  ⚠ Not found: $dir"
    fi
done

echo ""
print_status "Deleted $DELETED_DIRS empty directories"
echo ""

# Step 3: Update imports (find files that import deleted factories)
echo "🔍 Step 3: Finding files that import deleted factories..."
echo ""

# Search for imports of deleted factories
IMPORT_PATTERNS=(
    "from pheno.core.adapter_factory import"
    "from pheno.core.api_factory import"
    "from pheno.core.configuration_factory import"
    "from pheno.core.database_factory import"
    "from pheno.core.factory_factory import"
    "from pheno.core.logging_factory import"
    "from pheno.core.manager_factory import"
    "from pheno.core.monitoring_factory import"
    "from pheno.core.port_factory import"
    "from pheno.core.security_factory import"
    "from pheno.core.storage_factory import"
    "from pheno.core.testing_factory import"
    "from pheno.core.unified_factory import"
    "from pheno.core.utility_factory import"
    "from pheno.core.validator_factory import"
)

AFFECTED_FILES=()

for pattern in "${IMPORT_PATTERNS[@]}"; do
    FILES=$(grep -r "$pattern" src/pheno --include="*.py" 2>/dev/null | cut -d: -f1 | sort -u || true)
    if [ -n "$FILES" ]; then
        echo "  Found imports of: $pattern"
        echo "$FILES" | while read file; do
            echo "    - $file"
            AFFECTED_FILES+=("$file")
        done
    fi
done

UNIQUE_AFFECTED=$(printf '%s\n' "${AFFECTED_FILES[@]}" | sort -u | wc -l)

echo ""
print_warning "Found $UNIQUE_AFFECTED files with imports that need updating"
echo "  These will need manual review and updates"
echo ""

# Count files after
AFTER_COUNT=$(find src/pheno -name "*.py" -type f | wc -l)
AFTER_LINES=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')

# Step 4: Generate cleanup report
echo "📊 Step 4: Generating cleanup report..."
REPORT_FILE="reports/cleanup-phase2-factories-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p reports

{
    echo "PhenoSDK Cleanup Phase 2 - Factory Files Report"
    echo "==============================================="
    echo "Date: $(date)"
    echo ""
    echo "Files Deleted:"
    echo "-------------"
    echo "Factory files: $DELETED_COUNT"
    echo "Empty directories: $DELETED_DIRS"
    echo "Lines removed: $DELETED_LINES"
    echo ""
    echo "Before:"
    echo "-------"
    echo "Python files: $BEFORE_COUNT"
    echo "Lines of code: $BEFORE_LINES"
    echo ""
    echo "After:"
    echo "------"
    echo "Python files: $AFTER_COUNT"
    echo "Lines of code: $AFTER_LINES"
    echo ""
    echo "Change:"
    echo "-------"
    echo "Files: -$((BEFORE_COUNT - AFTER_COUNT)) ($((100 * (BEFORE_COUNT - AFTER_COUNT) / BEFORE_COUNT))%)"
    echo "Lines: -$((BEFORE_LINES - AFTER_LINES)) ($((100 * (BEFORE_LINES - AFTER_LINES) / BEFORE_LINES))%)"
    echo ""
    echo "Files Kept:"
    echo "-----------"
    echo "- src/pheno/core/exception_factory.py (re-export)"
    echo "- src/pheno/core/exception_factory/ (implementation)"
    echo "- src/pheno/infra/resources/network_factory.py (infrastructure)"
    echo "- src/pheno/infra/resources/storage_factory.py (infrastructure)"
    echo "- src/pheno/llm/routing/ensemble/factory.py (domain-specific)"
    echo "- src/pheno/vector/providers/factory.py (domain-specific)"
    echo ""
    echo "Affected Files (need import updates):"
    echo "-------------------------------------"
    printf '%s\n' "${AFFECTED_FILES[@]}" | sort -u
    echo ""
    echo "Remaining Issues:"
    echo "----------------"
    ruff check src/pheno --statistics 2>&1 || echo "Ruff not available"
} > "$REPORT_FILE"

print_status "Report saved to $REPORT_FILE"
echo ""

# Summary
echo "✨ Cleanup Phase 2 (Factory Files) Complete!"
echo "==========================================="
echo ""
echo "Summary:"
echo "  Deleted: $DELETED_COUNT factory files ($DELETED_LINES lines)"
echo "  Deleted: $DELETED_DIRS empty directories"
echo "  Reduction: -$((BEFORE_COUNT - AFTER_COUNT)) files, -$((BEFORE_LINES - AFTER_LINES)) lines"
echo "  Affected: $UNIQUE_AFFECTED files need import updates"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Update imports in affected files (see report)"
echo "  3. Run tests: pytest tests/"
echo "  4. Commit changes: git add -A && git commit -m 'chore: phase 2 - delete factory files'"
echo "  5. Proceed to Phase 2b: Delete registry files"
echo ""
echo "Backup location: $BACKUP_DIR"
echo "Archive location: $ARCHIVE_DIR"
echo "Report location: $REPORT_FILE"

