#!/bin/bash
# Phase 12.1: Low-Risk Migrations
# All automated or simple library swaps
# Estimated savings: -11,402 LOC

set -e

echo "🚀 Phase 12.1: Low-Risk Migrations"
echo "=================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Create backup
BACKUP_DIR="backups/cleanup-phase12-low-risk-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno "$BACKUP_DIR/pheno-before"
print_status "Backup created: $BACKUP_DIR"
echo ""

BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Starting LOC: $BEFORE_LOC"
echo ""

# ============================================================================
# 12.1.1: Remove Unused Imports (-2,500 LOC)
# ============================================================================
echo "🔧 12.1.1: Removing unused imports..."
echo ""

if command -v autoflake &> /dev/null; then
    print_info "Running autoflake..."
    
    autoflake \
        --remove-all-unused-imports \
        --remove-unused-variables \
        --remove-duplicate-keys \
        --in-place \
        --recursive \
        src/pheno/ 2>&1 | grep -v "^$" | head -20
    
    AFTER_AUTOFLAKE=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
    AUTOFLAKE_SAVINGS=$((BEFORE_LOC - AFTER_AUTOFLAKE))
    print_status "Removed unused imports: $AUTOFLAKE_SAVINGS LOC"
else
    print_warning "autoflake not installed, skipping"
    AUTOFLAKE_SAVINGS=0
    AFTER_AUTOFLAKE=$BEFORE_LOC
fi

echo ""

# ============================================================================
# 12.1.2: Modernize Old-Style Code (-3,000 LOC)
# ============================================================================
echo "🔧 12.1.2: Modernizing old-style code..."
echo ""

if command -v pyupgrade &> /dev/null; then
    print_info "Running pyupgrade for Python 3.10+..."
    
    find src/pheno -name "*.py" -type f -print0 | \
        xargs -0 -P 4 pyupgrade --py310-plus 2>&1 | \
        grep -v "^$" | head -20
    
    AFTER_PYUPGRADE=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
    PYUPGRADE_SAVINGS=$((AFTER_AUTOFLAKE - AFTER_PYUPGRADE))
    print_status "Modernized code: $PYUPGRADE_SAVINGS LOC"
else
    print_warning "pyupgrade not installed, installing..."
    pip install -q pyupgrade
    
    find src/pheno -name "*.py" -type f -print0 | \
        xargs -0 -P 4 pyupgrade --py310-plus 2>&1 | \
        grep -v "^$" | head -20
    
    AFTER_PYUPGRADE=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
    PYUPGRADE_SAVINGS=$((AFTER_AUTOFLAKE - AFTER_PYUPGRADE))
    print_status "Modernized code: $PYUPGRADE_SAVINGS LOC"
fi

echo ""

# ============================================================================
# 12.1.3: Move Example File (-102 LOC)
# ============================================================================
echo "🔧 12.1.3: Moving example file from src/ to examples/..."
echo ""

EXAMPLE_FILE="src/pheno/testing/adapters/pytest_runner.py"

if [ -f "$EXAMPLE_FILE" ]; then
    # Check if it's actually used
    IMPORT_COUNT=$(grep -r "pytest_runner" src/pheno --include="*.py" 2>/dev/null | grep -v "$EXAMPLE_FILE" | wc -l || echo "0")
    
    if [ "$IMPORT_COUNT" -eq "0" ]; then
        TARGET_DIR="examples/testing/adapters"
        mkdir -p "$TARGET_DIR"
        
        LOC=$(wc -l < "$EXAMPLE_FILE")
        mv "$EXAMPLE_FILE" "$TARGET_DIR/"
        
        print_status "Moved example file: $LOC LOC"
        EXAMPLE_SAVINGS=$LOC
    else
        print_warning "File is imported $IMPORT_COUNT times, keeping in src/"
        EXAMPLE_SAVINGS=0
    fi
else
    print_info "Example file already moved or doesn't exist"
    EXAMPLE_SAVINGS=0
fi

AFTER_EXAMPLE=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')

echo ""

# ============================================================================
# 12.1.4: Install Dependencies for Library Migrations
# ============================================================================
echo "🔧 12.1.4: Installing dependencies for library migrations..."
echo ""

print_info "Checking/installing: anyio, msgspec, aiolimiter..."

pip install -q anyio>=4.0.0 msgspec>=0.18.0 aiolimiter>=1.1.0

print_status "Dependencies installed"
echo ""

# ============================================================================
# Summary
# ============================================================================

AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
TOTAL_SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 12.1 Low-Risk Migrations Complete!"
echo "==========================================="
echo ""
echo "  Removed unused imports:  $AUTOFLAKE_SAVINGS LOC"
echo "  Modernized code:         $PYUPGRADE_SAVINGS LOC"
echo "  Moved example file:      $EXAMPLE_SAVINGS LOC"
echo "  ────────────────────────────────────"
echo "  Total Savings:           $TOTAL_SAVINGS LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After:  $AFTER_LOC LOC"
echo "  Reduction: $(echo "scale=1; $TOTAL_SAVINGS * 100 / $BEFORE_LOC" | bc)%"
echo ""
echo "Backup: $BACKUP_DIR"
echo ""

# ============================================================================
# Verification
# ============================================================================
echo "🔍 Running verification checks..."
echo ""

# Check for syntax errors
print_info "Checking for syntax errors..."
SYNTAX_ERRORS=0
for file in $(find src/pheno -name "*.py" -type f); do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        echo "  ✗ Syntax error in: $file"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    print_status "No syntax errors found"
else
    print_warning "Found $SYNTAX_ERRORS syntax errors"
fi

echo ""

# Check imports
print_info "Checking if pheno module can be imported..."
if python3 -c "import sys; sys.path.insert(0, 'src'); import pheno" 2>/dev/null; then
    print_status "Module imports successfully"
else
    print_warning "Module import failed (may need dependencies)"
fi

echo ""

# ============================================================================
# Next Steps
# ============================================================================
echo "📋 Next Steps:"
echo ""
echo "1. Review changes:"
echo "   git diff --stat"
echo ""
echo "2. Run tests:"
echo "   pytest tests/ -v --tb=short"
echo ""
echo "3. Check for any issues:"
echo "   ruff check src/pheno/"
echo ""
echo "4. If all looks good, commit:"
echo "   git add -A"
echo "   git commit -m 'feat: Phase 12.1 Low-Risk Migrations (-$TOTAL_SAVINGS LOC)'"
echo ""
echo "5. Continue with library migrations (Phase 12.2)"
echo ""

# ============================================================================
# Create migration report
# ============================================================================
cat > "$BACKUP_DIR/MIGRATION_REPORT.md" << EOF
# Phase 12.1 Low-Risk Migrations Report

**Date:** $(date +%Y-%m-%d)
**Status:** ✅ COMPLETE

## Summary

- **Before:** $BEFORE_LOC LOC
- **After:** $AFTER_LOC LOC
- **Savings:** $TOTAL_SAVINGS LOC ($(echo "scale=1; $TOTAL_SAVINGS * 100 / $BEFORE_LOC" | bc)%)

## Migrations Executed

### 12.1.1: Remove Unused Imports
- **Tool:** autoflake
- **Savings:** $AUTOFLAKE_SAVINGS LOC
- **Risk:** Very Low (automated)

### 12.1.2: Modernize Old-Style Code
- **Tool:** pyupgrade --py310-plus
- **Savings:** $PYUPGRADE_SAVINGS LOC
- **Risk:** Very Low (automated)

### 12.1.3: Move Example File
- **Action:** Move pytest_runner.py to examples/
- **Savings:** $EXAMPLE_SAVINGS LOC
- **Risk:** Very Low (simple move)

## Verification

- Syntax Errors: $SYNTAX_ERRORS
- Module Import: $(python3 -c "import sys; sys.path.insert(0, 'src'); import pheno" 2>/dev/null && echo "✓ Success" || echo "✗ Failed")

## Backup Location

$BACKUP_DIR

## Next Steps

1. Run tests to verify no breakage
2. Continue with Phase 12.2 (Library Migrations)
EOF

print_status "Migration report created: $BACKUP_DIR/MIGRATION_REPORT.md"
echo ""

