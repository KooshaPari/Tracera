#!/bin/bash
# Phase 5 - Category 7: Consolidate Config Management
# Remove redundant config files (pydantic-settings already handles this)

set -e

echo "🔧 Phase 5 - Category 7: Config Consolidation"
echo "=============================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase5-config-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count LOC before
BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# Delete redundant config files
echo "🗑️  Deleting redundant config files..."
echo ""

# These are duplicate/redundant config loaders
FILES_TO_DELETE=(
    "src/pheno/dev/pre_commit/config.py"
    "src/pheno/dev/ruff_integration/config.py"
    "src/pheno/dev/pydantic_v2/config.py"
    "src/pheno/dev/structlog/config.py"
    "src/pheno/dev/meilisearch_integration/config.py"
    "src/pheno/core/configuration_variants.py"
)

DELETED_LOC=0

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        DELETED_LOC=$((DELETED_LOC + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
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

echo "✨ Category 7 Complete!"
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
echo "Note: Use pydantic-settings instead:"
echo "  from pydantic_settings import BaseSettings"
echo "  class Settings(BaseSettings):"
echo "      api_key: str"
echo "      class Config:"
echo "          env_file = '.env'"

