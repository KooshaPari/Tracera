#!/bin/bash
# PhenoSDK Codebase Cleanup Script
# Phase 2c: Consolidate Unified Files

set -e  # Exit on error

echo "🧹 PhenoSDK Cleanup - Phase 2c: Consolidate Unified Files"
echo "=========================================================="
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
BACKUP_DIR="backups/cleanup-phase2c-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno "$BACKUP_DIR/"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Create archive directory
ARCHIVE_DIR="archives/archive/cleanup_phase2c_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"
print_status "Archive directory created at $ARCHIVE_DIR"
echo ""

# Count files before
BEFORE_COUNT=$(find src/pheno -name "*.py" -type f | wc -l)
BEFORE_LINES=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')

echo "📊 Before cleanup:"
echo "  Python files: $BEFORE_COUNT"
echo "  Lines of code: $BEFORE_LINES"
echo "  Unified files: $(find src/pheno -name '*unified*.py' -type f | wc -l)"
echo ""

# Step 1: Delete redundant unified files
echo "🗑️  Step 1: Deleting redundant unified files..."
echo ""

# Strategy: Keep only essential unified files, delete the rest
# KEEP these (essential/actively used):
# - src/pheno/core/api/unified.py (API facade)
# - src/pheno/testing/unified/ (testing framework)
# - src/pheno/vector/unified_search/ (directory with implementation)
#
# DELETE all others (redundant/unused)

UNIFIED_FILES_TO_DELETE=(
    # Adapters (5 files) - redundant
    "src/pheno/adapters/unified_auth.py"
    "src/pheno/adapters/unified_llm.py"
    "src/pheno/adapters/unified_specialized.py"
    "src/pheno/adapters/unified_utilities.py"
    "src/pheno/adapters/unified.py"
    
    # Async (1 file) - redundant
    "src/pheno/async/unified_task_orchestrator.py"
    
    # CLI (7 files) - redundant
    "src/pheno/cli/unified_cli_system.py"
    "src/pheno/cli/unified_commands.py"
    "src/pheno/cli/unified_core.py"
    "src/pheno/cli/unified_platform.py"
    "src/pheno/cli/unified_templates.py"
    "src/pheno/cli/unified_tui.py"
    "src/pheno/cli/unified_utils.py"
    
    # Core (13 files) - keep only api/unified.py
    "src/pheno/core/managers/unified_systems_manager.py"
    "src/pheno/core/shared/analyzers/unified_analyzer.py"
    "src/pheno/core/shared/configuration/unified_configuration.py"
    "src/pheno/core/shared/utilities/unified_utilities.py"
    "src/pheno/core/shared/validators/unified_validator.py"
    "src/pheno/core/unified_adapter.py"
    "src/pheno/core/unified_cache.py"
    "src/pheno/core/unified_configuration.py"
    "src/pheno/core/unified_database.py"
    "src/pheno/core/unified_http_client.py"
    "src/pheno/core/unified_manager.py"
    "src/pheno/core/unified_monitoring.py"
    "src/pheno/core/unified_observability.py"
    "src/pheno/core/unified_port.py"
    "src/pheno/core/unified_security.py"
    "src/pheno/core/unified_storage.py"
    "src/pheno/core/unified_testing.py"
    "src/pheno/core/unified_utility.py"
    
    # Database (1 file) - redundant
    "src/pheno/database/unified_database.py"
    
    # Deployment (6 files) - redundant
    "src/pheno/deployment/unified_base.py"
    "src/pheno/deployment/unified_cloud_providers.py"
    "src/pheno/deployment/unified_config.py"
    "src/pheno/deployment/unified_platforms.py"
    "src/pheno/deployment/unified_specialized.py"
    "src/pheno/deployment/unified_utils.py"
    
    # Dev (7 files) - redundant
    "src/pheno/dev/unified_data_structures.py"
    "src/pheno/dev/unified_datetime.py"
    "src/pheno/dev/unified_performance.py"
    "src/pheno/dev/unified_strings.py"
    "src/pheno/dev/unified_tracing.py"
    "src/pheno/dev/unified_utilities.py"
    "src/pheno/dev/unified_validation.py"
    
    # Exceptions (1 file) - redundant
    "src/pheno/exceptions/unified_exceptions.py"
    
    # Security (5 files) - redundant
    "src/pheno/security/unified_auth.py"
    "src/pheno/security/unified_crypto.py"
    "src/pheno/security/unified_sandbox.py"
    "src/pheno/security/unified_scanners.py"
    "src/pheno/security/unified_tools.py"
    
    # UI/TUI (5 files) - redundant
    "src/pheno/ui/tui/unified_components.py"
    "src/pheno/ui/tui/unified_theming.py"
    "src/pheno/ui/tui/unified_tui.py"
    "src/pheno/ui/tui/unified_web.py"
    "src/pheno/ui/tui/unified_widgets.py"
    
    # Root (1 file) - redundant
    "src/pheno/unified_utilities.py"
    
    # Vector (6 files) - keep unified_search/ directory, delete standalone files
    "src/pheno/vector/unified_backends.py"
    "src/pheno/vector/unified_client.py"
    "src/pheno/vector/unified_embeddings.py"
    "src/pheno/vector/unified_pipelines.py"
    "src/pheno/vector/unified_search.py"
    "src/pheno/vector/unified_stores.py"
)

DELETED_COUNT=0
DELETED_LINES=0

for file in "${UNIFIED_FILES_TO_DELETE[@]}"; do
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
print_status "Deleted $DELETED_COUNT unified files ($DELETED_LINES lines)"
echo ""

# Count files after
AFTER_COUNT=$(find src/pheno -name "*.py" -type f | wc -l)
AFTER_LINES=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
AFTER_UNIFIED=$(find src/pheno -name '*unified*.py' -type f | wc -l)

# Generate report
echo "📊 Step 2: Generating cleanup report..."
REPORT_FILE="reports/cleanup-phase2c-unified-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p reports

{
    echo "PhenoSDK Cleanup Phase 2c - Unified Files Report"
    echo "================================================"
    echo "Date: $(date)"
    echo ""
    echo "Files Deleted:"
    echo "-------------"
    echo "Unified files: $DELETED_COUNT"
    echo "Lines removed: $DELETED_LINES"
    echo ""
    echo "Before:"
    echo "-------"
    echo "Python files: $BEFORE_COUNT"
    echo "Lines of code: $BEFORE_LINES"
    echo "Unified files: 64"
    echo ""
    echo "After:"
    echo "------"
    echo "Python files: $AFTER_COUNT"
    echo "Lines of code: $AFTER_LINES"
    echo "Unified files: $AFTER_UNIFIED"
    echo ""
    echo "Change:"
    echo "-------"
    echo "Files: -$((BEFORE_COUNT - AFTER_COUNT))"
    echo "Lines: -$((BEFORE_LINES - AFTER_LINES))"
    echo "Unified files: -$((64 - AFTER_UNIFIED))"
    echo ""
    echo "Files Kept (essential):"
    echo "----------------------"
    echo "- src/pheno/core/api/unified.py (API facade)"
    echo "- src/pheno/testing/unified/ (testing framework directory)"
    echo "- src/pheno/vector/unified_search/ (search implementation directory)"
} > "$REPORT_FILE"

print_status "Report saved to $REPORT_FILE"
echo ""

# Summary
echo "✨ Cleanup Phase 2c (Unified Files) Complete!"
echo "============================================="
echo ""
echo "Summary:"
echo "  Deleted: $DELETED_COUNT unified files ($DELETED_LINES lines)"
echo "  Reduction: -$((BEFORE_COUNT - AFTER_COUNT)) files, -$((BEFORE_LINES - AFTER_LINES)) lines"
echo "  Unified files: 64 → $AFTER_UNIFIED"
echo ""
echo "Backup location: $BACKUP_DIR"
echo "Archive location: $ARCHIVE_DIR"
echo "Report location: $REPORT_FILE"

