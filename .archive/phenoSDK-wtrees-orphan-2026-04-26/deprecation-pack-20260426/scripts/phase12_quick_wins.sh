#!/bin/bash
# Phase 12.1 - Quick Wins (Week 1)
# Estimated savings: -15,800 LOC

set -e

echo "🚀 Phase 12.1: Quick Wins"
echo "========================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Create backup
BACKUP_DIR="backups/cleanup-phase12-quick-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup: $BACKUP_DIR"
echo ""

BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# ============================================================================
# Priority 1.1: Remove Unused Imports (-2,500 LOC)
# ============================================================================
echo "🔧 1.1: Removing unused imports..."
echo ""

# Backup before autoflake
cp -r src/pheno "$BACKUP_DIR/pheno-before-autoflake"

# Run autoflake
if command -v autoflake &> /dev/null; then
    autoflake \
        --remove-all-unused-imports \
        --remove-unused-variables \
        --in-place \
        --recursive \
        src/pheno/
    
    AFTER_AUTOFLAKE=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
    AUTOFLAKE_SAVINGS=$((BEFORE_LOC - AFTER_AUTOFLAKE))
    print_status "Removed unused imports: $AUTOFLAKE_SAVINGS LOC"
else
    print_warning "autoflake not installed, skipping"
    AUTOFLAKE_SAVINGS=0
fi

echo ""

# ============================================================================
# Priority 3.2: Modernize Old-Style Code (-3,000 LOC)
# ============================================================================
echo "🔧 3.2: Modernizing old-style code..."
echo ""

# Backup before pyupgrade
cp -r src/pheno "$BACKUP_DIR/pheno-before-pyupgrade"

# Run pyupgrade
if command -v pyupgrade &> /dev/null; then
    find src/pheno -name "*.py" -type f -exec pyupgrade --py310-plus {} \;
    
    AFTER_PYUPGRADE=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
    PYUPGRADE_SAVINGS=$((AFTER_AUTOFLAKE - AFTER_PYUPGRADE))
    print_status "Modernized code: $PYUPGRADE_SAVINGS LOC"
else
    print_warning "pyupgrade not installed, skipping"
    PYUPGRADE_SAVINGS=0
    AFTER_PYUPGRADE=$AFTER_AUTOFLAKE
fi

echo ""

# ============================================================================
# Priority 1.2: Consolidate __init__ Files (-6,000 LOC)
# ============================================================================
echo "🔧 1.2: Consolidating __init__ files..."
echo ""

# Backup before init consolidation
cp -r src/pheno "$BACKUP_DIR/pheno-before-init-consolidation"

# Find and simplify __init__ files
INIT_SIMPLIFIED=0

find src/pheno -name "__init__.py" -type f | while read init_file; do
    # Get current LOC
    CURRENT_LOC=$(wc -l < "$init_file")
    
    # Skip if already minimal (< 5 lines)
    if [ "$CURRENT_LOC" -lt 5 ]; then
        continue
    fi
    
    # Check if it's just imports and __all__
    if grep -qE "^(from |import |__all__|#|$)" "$init_file"; then
        # Get module name from directory
        MODULE_DIR=$(dirname "$init_file")
        MODULE_NAME=$(basename "$MODULE_DIR")
        
        # Create minimal __init__.py
        echo "\"\"\"${MODULE_NAME^} module.\"\"\"" > "$init_file"
        
        NEW_LOC=$(wc -l < "$init_file")
        SAVED=$((CURRENT_LOC - NEW_LOC))
        INIT_SIMPLIFIED=$((INIT_SIMPLIFIED + SAVED))
    fi
done

AFTER_INIT=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
INIT_SAVINGS=$((AFTER_PYUPGRADE - AFTER_INIT))
print_status "Consolidated __init__ files: $INIT_SAVINGS LOC"
echo ""

# ============================================================================
# Summary
# ============================================================================

TOTAL_SAVINGS=$((AUTOFLAKE_SAVINGS + PYUPGRADE_SAVINGS + INIT_SAVINGS))

AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
ACTUAL_SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 12.1 Quick Wins Complete!"
echo "=================================="
echo ""
echo "  Unused imports:     $AUTOFLAKE_SAVINGS LOC"
echo "  Modernized code:    $PYUPGRADE_SAVINGS LOC"
echo "  Consolidated inits: $INIT_SAVINGS LOC"
echo "  ────────────────────────────"
echo "  Total:              $TOTAL_SAVINGS LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After:  $AFTER_LOC LOC"
echo "  Actual Savings: $ACTUAL_SAVINGS LOC"
echo ""
echo "Backup: $BACKUP_DIR"
echo ""

# ============================================================================
# Next Steps
# ============================================================================
echo "📋 Next Steps:"
echo ""
echo "1. Run tests to verify no breakage:"
echo "   pytest tests/ -v"
echo ""
echo "2. Check for any import errors:"
echo "   python -m pheno --help"
echo ""
echo "3. Review changes:"
echo "   git diff"
echo ""
echo "4. If all looks good, commit:"
echo "   git add -A"
echo "   git commit -m 'feat: Phase 12.1 Quick Wins (-$ACTUAL_SAVINGS LOC)'"
echo ""
echo "5. Continue with Phase 12.2 (Library Migrations)"
echo ""

