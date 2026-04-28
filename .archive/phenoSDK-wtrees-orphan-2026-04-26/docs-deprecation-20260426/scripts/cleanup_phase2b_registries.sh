#!/bin/bash
# PhenoSDK Codebase Cleanup Script
# Phase 2b: Delete Registry Files (keep adapter_registry.py and domain-specific)

set -e  # Exit on error

echo "🧹 PhenoSDK Cleanup - Phase 2b: Delete Registry Files"
echo "====================================================="
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
BACKUP_DIR="backups/cleanup-phase2b-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno "$BACKUP_DIR/"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Create archive directory
ARCHIVE_DIR="archives/archive/cleanup_phase2b_$(date +%Y%m%d_%H%M%S)"
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

# Step 1: Delete registry files (EXCEPT adapter_registry.py and domain-specific)
echo "🗑️  Step 1: Deleting registry files..."
echo ""

# List of registry files to DELETE
REGISTRY_FILES=(
    "src/pheno/core/api_registry.py"
    "src/pheno/core/configuration_registry/registry.py"
    "src/pheno/core/database_registry.py"
    "src/pheno/core/exception_registry.py"
    "src/pheno/core/logging_registry.py"
    "src/pheno/core/manager_registry.py"
    "src/pheno/core/monitoring_registry.py"
    "src/pheno/core/port_registry.py"
    "src/pheno/core/security_registry.py"
    "src/pheno/core/storage_registry.py"
    "src/pheno/core/testing_registry.py"
    "src/pheno/core/unified_registry.py"
    "src/pheno/core/utility_registry.py"
    "src/pheno/core/validator_registry.py"
    "src/pheno/adapters/unified_registry.py"
)

# KEEP these (domain-specific or essential):
# - src/pheno/core/adapter_registry.py (essential)
# - src/pheno/logging/handlers/registry.py (domain-specific)
# - src/pheno/mcp/adapters/tool_registry.py (domain-specific)
# - src/pheno/mcp/qa/core/test_registry.py (domain-specific)
# - src/pheno/mcp/registry.py (domain-specific)
# - src/pheno/quality/registry.py (domain-specific)
# - src/pheno/infra/global_registry.py (infrastructure)
# - src/pheno/infra/port_registry.py (infrastructure)
# - src/pheno/infra/resources/registry.py (infrastructure)

DELETED_COUNT=0
DELETED_LINES=0

for file in "${REGISTRY_FILES[@]}"; do
    if [ -f "$file" ]; then
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
print_status "Deleted $DELETED_COUNT registry files ($DELETED_LINES lines)"
echo ""

# Step 2: Delete empty registry directories
echo "🗑️  Step 2: Deleting empty registry directories..."
echo ""

REGISTRY_DIRS=(
    "src/pheno/core/configuration_registry"
)

DELETED_DIRS=0

for dir in "${REGISTRY_DIRS[@]}"; do
    if [ -d "$dir" ]; then
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

# Count files after
AFTER_COUNT=$(find src/pheno -name "*.py" -type f | wc -l)
AFTER_LINES=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')

# Step 3: Generate cleanup report
echo "📊 Step 3: Generating cleanup report..."
REPORT_FILE="reports/cleanup-phase2b-registries-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p reports

{
    echo "PhenoSDK Cleanup Phase 2b - Registry Files Report"
    echo "================================================="
    echo "Date: $(date)"
    echo ""
    echo "Files Deleted:"
    echo "-------------"
    echo "Registry files: $DELETED_COUNT"
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
    echo "Files: -$((BEFORE_COUNT - AFTER_COUNT))"
    echo "Lines: -$((BEFORE_LINES - AFTER_LINES))"
    echo ""
    echo "Files Kept (domain-specific or essential):"
    echo "------------------------------------------"
    echo "- src/pheno/core/adapter_registry.py (essential)"
    echo "- src/pheno/logging/handlers/registry.py (domain-specific)"
    echo "- src/pheno/mcp/adapters/tool_registry.py (domain-specific)"
    echo "- src/pheno/mcp/qa/core/test_registry.py (domain-specific)"
    echo "- src/pheno/mcp/registry.py (domain-specific)"
    echo "- src/pheno/quality/registry.py (domain-specific)"
    echo "- src/pheno/infra/global_registry.py (infrastructure)"
    echo "- src/pheno/infra/port_registry.py (infrastructure)"
    echo "- src/pheno/infra/resources/registry.py (infrastructure)"
} > "$REPORT_FILE"

print_status "Report saved to $REPORT_FILE"
echo ""

# Summary
echo "✨ Cleanup Phase 2b (Registry Files) Complete!"
echo "=============================================="
echo ""
echo "Summary:"
echo "  Deleted: $DELETED_COUNT registry files ($DELETED_LINES lines)"
echo "  Deleted: $DELETED_DIRS empty directories"
echo "  Reduction: -$((BEFORE_COUNT - AFTER_COUNT)) files, -$((BEFORE_LINES - AFTER_LINES)) lines"
echo ""
echo "Backup location: $BACKUP_DIR"
echo "Archive location: $ARCHIVE_DIR"
echo "Report location: $REPORT_FILE"

