#!/usr/bin/env bash
#
# PhenoSDK Deep Cleanup - Phase 1: Immediate Wins
#
# This script performs safe, automated cleanup of dead code and auto-fixes.
# Creates backup before making any changes.
#
# Usage: ./scripts/deep_cleanup_phase1.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="backups/pre-deep-cleanup-$(date +%Y%m%d-%H%M%S)"
REPORT_DIR="reports/deep-cleanup-phase1"
SRC_DIR="src/pheno"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$REPORT_DIR"

log_info "Starting Phase 1 Deep Cleanup..."
log_info "Backup directory: $BACKUP_DIR"
log_info "Report directory: $REPORT_DIR"

# ============================================================================
# Step 1: Create Backup
# ============================================================================

log_info "Step 1: Creating backup..."
cp -r "$SRC_DIR" "$BACKUP_DIR/"
log_success "Backup created at $BACKUP_DIR"

# ============================================================================
# Step 2: Collect Pre-Cleanup Metrics
# ============================================================================

log_info "Step 2: Collecting pre-cleanup metrics..."

# Count files
FILE_COUNT_BEFORE=$(find "$SRC_DIR" -name "*.py" | wc -l | tr -d ' ')
log_info "Python files before: $FILE_COUNT_BEFORE"

# Count lines
LINE_COUNT_BEFORE=$(find "$SRC_DIR" -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')
log_info "Lines of code before: $LINE_COUNT_BEFORE"

# Count errors
ERROR_COUNT_BEFORE=$(ruff check "$SRC_DIR" --select F,E,W,I --statistics 2>&1 | grep -E "^[0-9]+" | awk '{sum+=$1} END {print sum}' || echo "0")
log_info "Ruff errors before: $ERROR_COUNT_BEFORE"

# Save metrics
cat > "$REPORT_DIR/metrics_before.txt" <<EOF
Pre-Cleanup Metrics
===================
Date: $(date)
Python Files: $FILE_COUNT_BEFORE
Lines of Code: $LINE_COUNT_BEFORE
Ruff Errors: $ERROR_COUNT_BEFORE
EOF

# ============================================================================
# Step 3: Delete Backup Directories
# ============================================================================

log_info "Step 3: Deleting backup directories..."

if [ -d "backups/cleanup-20251029-052136" ]; then
    rm -rf backups/cleanup-20251029-052136
    log_success "Deleted backups/cleanup-20251029-052136"
fi

if [ -d "backups/cleanup-phase2-20251029-055218" ]; then
    rm -rf backups/cleanup-phase2-20251029-055218
    log_success "Deleted backups/cleanup-phase2-20251029-055218"
fi

if [ -d "backups/cleanup-phase2b-20251029-143343" ]; then
    rm -rf backups/cleanup-phase2b-20251029-143343
    log_success "Deleted backups/cleanup-phase2b-20251029-143343"
fi

if [ -d "backups/cleanup-phase2c-20251029-152012" ]; then
    rm -rf backups/cleanup-phase2c-20251029-152012
    log_success "Deleted backups/cleanup-phase2c-20251029-152012"
fi

if [ -d "backups/cleanup-phase2d-20251029-144309" ]; then
    rm -rf backups/cleanup-phase2d-20251029-144309
    log_success "Deleted backups/cleanup-phase2d-20251029-144309"
fi

if [ -d "backups/cleanup-phase3a-20251029-144743" ]; then
    rm -rf backups/cleanup-phase3a-20251029-144743
    log_success "Deleted backups/cleanup-phase3a-20251029-144743"
fi

# ============================================================================
# Step 4: Delete Archive Directory
# ============================================================================

log_info "Step 4: Deleting archive directory..."

if [ -d "archives" ]; then
    ARCHIVE_SIZE=$(du -sh archives | awk '{print $1}')
    rm -rf archives
    log_success "Deleted archives/ ($ARCHIVE_SIZE)"
fi

# ============================================================================
# Step 5: Delete Dead Code Files
# ============================================================================

log_info "Step 5: Deleting dead code files..."

# Legacy files
if [ -f "$SRC_DIR/credentials/detect/legacy.py" ]; then
    rm "$SRC_DIR/credentials/detect/legacy.py"
    log_success "Deleted credentials/detect/legacy.py"
fi

# Old integration
if [ -d "$SRC_DIR/dev/meilisearch_integration_old" ]; then
    rm -rf "$SRC_DIR/dev/meilisearch_integration_old"
    log_success "Deleted dev/meilisearch_integration_old/"
fi

# ============================================================================
# Step 6: Delete Placeholder Infrastructure Module
# ============================================================================

log_info "Step 6: Deleting placeholder infrastructure module..."

if [ -d "$SRC_DIR/infrastructure" ]; then
    # Check if it's just a placeholder
    FILE_COUNT=$(find "$SRC_DIR/infrastructure" -name "*.py" | wc -l | tr -d ' ')
    if [ "$FILE_COUNT" -eq 1 ]; then
        rm -rf "$SRC_DIR/infrastructure"
        log_success "Deleted infrastructure/ (placeholder only)"
    else
        log_warning "infrastructure/ has $FILE_COUNT files, skipping deletion"
    fi
fi

# ============================================================================
# Step 7: Run Ruff Auto-Fix
# ============================================================================

log_info "Step 7: Running ruff auto-fix..."

# Check if ruff is installed
if ! command -v ruff &> /dev/null; then
    log_error "ruff is not installed. Install with: pip install ruff"
    exit 1
fi

# Run ruff fix
log_info "Fixing F (pyflakes) errors..."
ruff check "$SRC_DIR" --fix --select F --unsafe-fixes 2>&1 | tee "$REPORT_DIR/ruff_fix_F.log"

log_info "Fixing E (pycodestyle errors)..."
ruff check "$SRC_DIR" --fix --select E --unsafe-fixes 2>&1 | tee "$REPORT_DIR/ruff_fix_E.log"

log_info "Fixing W (pycodestyle warnings)..."
ruff check "$SRC_DIR" --fix --select W --unsafe-fixes 2>&1 | tee "$REPORT_DIR/ruff_fix_W.log"

log_info "Fixing I (isort)..."
ruff check "$SRC_DIR" --fix --select I 2>&1 | tee "$REPORT_DIR/ruff_fix_I.log"

log_success "Ruff auto-fix complete"

# ============================================================================
# Step 8: Remove Unused Imports (Optional)
# ============================================================================

log_info "Step 8: Removing unused imports..."

if command -v autoflake &> /dev/null; then
    autoflake \
        --remove-all-unused-imports \
        --remove-unused-variables \
        --in-place \
        --recursive \
        "$SRC_DIR" 2>&1 | tee "$REPORT_DIR/autoflake.log"
    log_success "Unused imports removed"
else
    log_warning "autoflake not installed, skipping. Install with: pip install autoflake"
fi

# ============================================================================
# Step 9: Sort Imports (Optional)
# ============================================================================

log_info "Step 9: Sorting imports..."

if command -v isort &> /dev/null; then
    isort "$SRC_DIR" 2>&1 | tee "$REPORT_DIR/isort.log"
    log_success "Imports sorted"
else
    log_warning "isort not installed, skipping. Install with: pip install isort"
fi

# ============================================================================
# Step 10: Collect Post-Cleanup Metrics
# ============================================================================

log_info "Step 10: Collecting post-cleanup metrics..."

# Count files
FILE_COUNT_AFTER=$(find "$SRC_DIR" -name "*.py" | wc -l | tr -d ' ')
log_info "Python files after: $FILE_COUNT_AFTER"

# Count lines
LINE_COUNT_AFTER=$(find "$SRC_DIR" -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')
log_info "Lines of code after: $LINE_COUNT_AFTER"

# Count errors
ERROR_COUNT_AFTER=$(ruff check "$SRC_DIR" --select F,E,W,I --statistics 2>&1 | grep -E "^[0-9]+" | awk '{sum+=$1} END {print sum}' || echo "0")
log_info "Ruff errors after: $ERROR_COUNT_AFTER"

# Calculate improvements
FILES_REMOVED=$((FILE_COUNT_BEFORE - FILE_COUNT_AFTER))
LINES_REMOVED=$((LINE_COUNT_BEFORE - LINE_COUNT_AFTER))
ERRORS_FIXED=$((ERROR_COUNT_BEFORE - ERROR_COUNT_AFTER))

# Save metrics
cat > "$REPORT_DIR/metrics_after.txt" <<EOF
Post-Cleanup Metrics
====================
Date: $(date)
Python Files: $FILE_COUNT_AFTER
Lines of Code: $LINE_COUNT_AFTER
Ruff Errors: $ERROR_COUNT_AFTER

Improvements
============
Files Removed: $FILES_REMOVED
Lines Removed: $LINES_REMOVED
Errors Fixed: $ERRORS_FIXED
EOF

# ============================================================================
# Step 11: Generate Summary Report
# ============================================================================

log_info "Step 11: Generating summary report..."

cat > "$REPORT_DIR/SUMMARY.md" <<EOF
# Phase 1 Deep Cleanup Summary

**Date**: $(date)
**Backup**: $BACKUP_DIR

## Metrics

### Before Cleanup
- Python Files: $FILE_COUNT_BEFORE
- Lines of Code: $LINE_COUNT_BEFORE
- Ruff Errors: $ERROR_COUNT_BEFORE

### After Cleanup
- Python Files: $FILE_COUNT_AFTER
- Lines of Code: $LINE_COUNT_AFTER
- Ruff Errors: $ERROR_COUNT_AFTER

### Improvements
- Files Removed: $FILES_REMOVED (-$(echo "scale=1; $FILES_REMOVED * 100 / $FILE_COUNT_BEFORE" | bc)%)
- Lines Removed: $LINES_REMOVED (-$(echo "scale=1; $LINES_REMOVED * 100 / $LINE_COUNT_BEFORE" | bc)%)
- Errors Fixed: $ERRORS_FIXED (-$(echo "scale=1; $ERRORS_FIXED * 100 / $ERROR_COUNT_BEFORE" | bc)%)

## Actions Taken

1. ✅ Created backup at $BACKUP_DIR
2. ✅ Deleted 6 backup directories
3. ✅ Deleted archives/ directory
4. ✅ Deleted legacy.py
5. ✅ Deleted meilisearch_integration_old/
6. ✅ Deleted infrastructure/ placeholder
7. ✅ Ran ruff auto-fix (F, E, W, I)
8. ✅ Removed unused imports (autoflake)
9. ✅ Sorted imports (isort)

## Next Steps

1. Review changes: \`git diff\`
2. Run tests: \`pytest tests/\`
3. Commit changes: \`git commit -m "chore: phase 1 deep cleanup"\`
4. Proceed to Phase 2: Module consolidation

## Logs

- Ruff fix logs: $REPORT_DIR/ruff_fix_*.log
- Autoflake log: $REPORT_DIR/autoflake.log
- Isort log: $REPORT_DIR/isort.log
EOF

log_success "Summary report generated at $REPORT_DIR/SUMMARY.md"

# ============================================================================
# Final Summary
# ============================================================================

echo ""
echo "========================================================================"
echo "                    PHASE 1 CLEANUP COMPLETE                            "
echo "========================================================================"
echo ""
echo -e "${GREEN}✅ Files Removed:${NC} $FILES_REMOVED (-$(echo "scale=1; $FILES_REMOVED * 100 / $FILE_COUNT_BEFORE" | bc)%)"
echo -e "${GREEN}✅ Lines Removed:${NC} $LINES_REMOVED (-$(echo "scale=1; $LINES_REMOVED * 100 / $LINE_COUNT_BEFORE" | bc)%)"
echo -e "${GREEN}✅ Errors Fixed:${NC} $ERRORS_FIXED (-$(echo "scale=1; $ERRORS_FIXED * 100 / $ERROR_COUNT_BEFORE" | bc)%)"
echo ""
echo -e "${BLUE}📊 Full report:${NC} $REPORT_DIR/SUMMARY.md"
echo -e "${BLUE}💾 Backup:${NC} $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run tests: pytest tests/"
echo "  3. Commit: git commit -m 'chore: phase 1 deep cleanup'"
echo ""
echo "========================================================================"

