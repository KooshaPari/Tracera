#!/bin/bash
# Phase 10.2 - Execute cleanup opportunities

set -e

echo "🔧 Phase 10.2: Execute Cleanup Opportunities"
echo "============================================="
echo ""

GREEN='\033[0;32m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
BACKUP_DIR="backups/cleanup-phase10-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup: $BACKUP_DIR"
echo ""

BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# ============================================================================
# 1. Remove deprecated files (1,327 LOC)
# ============================================================================
echo "🗑️  1. Removing deprecated files..."
echo ""

DEPRECATED=(
    "src/pheno/core/config/core.py"
    "src/pheno/infra/port_allocator.py"
    "src/pheno/infra/port_registry.py"
    "src/pheno/resilience/health.py"
    "src/pheno/core/config/integration.py"
    "src/pheno/observability/monitoring/health.py"
    "src/pheno/infra/kinfra/orchestrator.py"
    "src/pheno/infra/tunnel_governance.py"
    "src/pheno/mcp/tools/__init__.py"
    "src/pheno/infra/orchestrator.py"
)

DEPRECATED_DELETED=0

for file in "${DEPRECATED[@]}"; do
    if [ -f "$file" ]; then
        # Check if imported
        filename=$(basename "$file" .py)
        import_count=$(grep -r "import $filename\|from.*$filename" src/pheno --include="*.py" 2>/dev/null | grep -v "$file" | wc -l || echo "0")
        
        if [ "$import_count" -eq "0" ]; then
            LOC=$(wc -l < "$file")
            DEPRECATED_DELETED=$((DEPRECATED_DELETED + LOC))
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            rm "$file"
            echo "  ✓ Deleted: $file ($LOC LOC)"
        else
            echo "  ⚠ Skipped: $file ($import_count imports)"
        fi
    fi
done

print_status "Deprecated: $DEPRECATED_DELETED LOC"
echo ""

# ============================================================================
# 2. Remove empty test files (213 LOC)
# ============================================================================
echo "🗑️  2. Removing empty test files..."
echo ""

EMPTY_TESTS=(
    "src/pheno/testing/base/runner/test_executor.py"
)

EMPTY_TEST_DELETED=0

for file in "${EMPTY_TESTS[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        EMPTY_TEST_DELETED=$((EMPTY_TEST_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    fi
done

print_status "Empty tests: $EMPTY_TEST_DELETED LOC"
echo ""

# ============================================================================
# 3. Remove incomplete implementations (select files)
# ============================================================================
echo "🗑️  3. Removing incomplete implementations..."
echo ""

INCOMPLETE=(
    "src/pheno/patterns/refactoring/extractors/layer_extractor.py"
    "src/pheno/patterns/refactoring/extractors/concern_extractor.py"
)

INCOMPLETE_DELETED=0

for file in "${INCOMPLETE[@]}"; do
    if [ -f "$file" ]; then
        import_count=$(grep -r "layer_extractor\|concern_extractor" src/pheno --include="*.py" 2>/dev/null | grep -v "$file" | wc -l || echo "0")
        
        if [ "$import_count" -eq "0" ]; then
            LOC=$(wc -l < "$file")
            INCOMPLETE_DELETED=$((INCOMPLETE_DELETED + LOC))
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            rm "$file"
            echo "  ✓ Deleted: $file ($LOC LOC)"
        else
            echo "  ⚠ Skipped: $file ($import_count imports)"
        fi
    fi
done

print_status "Incomplete: $INCOMPLETE_DELETED LOC"
echo ""

# ============================================================================
# Summary
# ============================================================================

TOTAL_DELETED=$((DEPRECATED_DELETED + EMPTY_TEST_DELETED + INCOMPLETE_DELETED))

AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 10.2 Complete!"
echo "======================"
echo ""
echo "  Deprecated: $DEPRECATED_DELETED LOC"
echo "  Empty tests: $EMPTY_TEST_DELETED LOC"
echo "  Incomplete: $INCOMPLETE_DELETED LOC"
echo "  Total: $TOTAL_DELETED LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup: $BACKUP_DIR"

