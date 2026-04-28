#!/bin/bash
# Phase 5 - Category 2: Consolidate HTTP Clients
# Replace custom HTTP wrappers with direct httpx usage

set -e

echo "🔧 Phase 5 - Category 2: HTTP Clients Consolidation"
echo "===================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase5-http-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno/dev/http "$BACKUP_DIR/" 2>/dev/null || true
cp -r src/pheno/dev/*http*.py "$BACKUP_DIR/" 2>/dev/null || true
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count LOC before
BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# Delete redundant HTTP client files
echo "🗑️  Deleting redundant HTTP client files..."
echo ""

FILES_TO_DELETE=(
    "src/pheno/dev/http/httpx_client.py"
    "src/pheno/dev/httpx_integration.py"
    "src/pheno/dev/aiohttp_integration.py"
)

DELETED_LOC=0

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        DELETED_LOC=$((DELETED_LOC + LOC))
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

# Delete empty http directory if exists
if [ -d "src/pheno/dev/http" ] && [ -z "$(ls -A src/pheno/dev/http)" ]; then
    rmdir "src/pheno/dev/http"
    echo "  ✓ Removed empty directory: src/pheno/dev/http"
fi

echo ""
print_status "Deleted $DELETED_LOC LOC"
echo ""

# Count LOC after
AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 After: $AFTER_LOC LOC"
echo ""

SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Category 2 Complete!"
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
echo "Note: Use httpx directly instead:"
echo "  import httpx"
echo "  async with httpx.AsyncClient() as client:"
echo "      response = await client.get('https://api.example.com')"

