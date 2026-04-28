#!/bin/bash
# Auto-fix remaining errors before SST integration

set -e

echo "🔧 Auto-fixing Remaining Errors"
echo "================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Count errors before
echo "📊 Counting errors before..."
BEFORE_ERRORS=$(ruff check src/pheno 2>&1 | grep "Found" | awk '{print $2}' || echo "0")
echo "  Before: $BEFORE_ERRORS errors"
echo ""

# 1. Auto-fix with ruff
echo "🔧 1. Running ruff auto-fix..."
ruff check src/pheno --fix --unsafe-fixes --quiet || true
print_status "Ruff auto-fix complete"
echo ""

# 2. Format with ruff
echo "🔧 2. Running ruff format..."
ruff format src/pheno --quiet || true
print_status "Ruff format complete"
echo ""

# 3. Remove unused imports
echo "🔧 3. Removing unused imports..."
if command -v autoflake &> /dev/null; then
    autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive src/pheno || true
    print_status "Unused imports removed"
else
    echo "  ⚠ autoflake not installed, skipping"
fi
echo ""

# 4. Sort imports
echo "🔧 4. Sorting imports..."
if command -v isort &> /dev/null; then
    isort src/pheno --quiet || true
    print_status "Imports sorted"
else
    echo "  ⚠ isort not installed, skipping"
fi
echo ""

# Count errors after
echo "📊 Counting errors after..."
AFTER_ERRORS=$(ruff check src/pheno 2>&1 | grep "Found" | awk '{print $2}' || echo "0")
echo "  After: $AFTER_ERRORS errors"
echo ""

# Calculate improvement
if [ "$BEFORE_ERRORS" != "0" ] && [ "$AFTER_ERRORS" != "0" ]; then
    FIXED=$((BEFORE_ERRORS - AFTER_ERRORS))
    PERCENT=$(awk "BEGIN {printf \"%.1f\", ($FIXED / $BEFORE_ERRORS) * 100}")
    echo "✨ Auto-fix Complete!"
    echo "===================="
    echo ""
    echo "  Before: $BEFORE_ERRORS errors"
    echo "  After: $AFTER_ERRORS errors"
    echo "  Fixed: $FIXED errors ($PERCENT%)"
    echo ""
else
    echo "✨ Auto-fix Complete!"
    echo "===================="
    echo ""
fi

echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run tests: pytest tests/"
echo "  3. Commit: git add -A && git commit -m 'chore: auto-fix remaining errors'"
echo "  4. Start SST integration!"
echo ""

