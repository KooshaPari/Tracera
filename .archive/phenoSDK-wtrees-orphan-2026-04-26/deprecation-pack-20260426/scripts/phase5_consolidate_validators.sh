#!/bin/bash
# Phase 5 - Category 4: Consolidate Validators
# Remove redundant validation code (pydantic already handles this)

set -e

echo "🔧 Phase 5 - Category 4: Validators Consolidation"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase5-validators-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count LOC before
BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# Delete redundant validator files
echo "🗑️  Deleting redundant validator files..."
echo ""

# These are duplicate/redundant validators that pydantic already handles
FILES_TO_DELETE=(
    "src/pheno/dev/cli_migration.py"
    "src/pheno/patterns/refactoring/validator/layer_validator.py"
)

DELETED_LOC=0

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        DELETED_LOC=$((DELETED_LOC + LOC))
        cp "$file" "$BACKUP_DIR/"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Deleted $DELETED_LOC LOC"
echo ""

# Count LOC after
AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 After: $AFTER_LOC LOC"
echo ""

SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Category 4 Complete!"
echo "======================"
echo ""
echo "Summary:"
echo "  Deleted: $DELETED_LOC LOC"
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Note: Use pydantic validators instead:"
echo "  from pydantic import BaseModel, validator, field_validator"
echo "  class MyModel(BaseModel):"
echo "      email: EmailStr"
echo "      @field_validator('field')"
echo "      def validate_field(cls, v):"
echo "          return v"

