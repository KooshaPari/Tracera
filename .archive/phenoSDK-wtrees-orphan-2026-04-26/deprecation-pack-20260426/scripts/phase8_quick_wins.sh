#!/bin/bash
# Phase 8 - Quick LOC wins (safe, high-impact)

set -e

echo "🔧 Phase 8: Quick LOC Wins"
echo "=========================="
echo ""

GREEN='\033[0;32m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
BACKUP_DIR="backups/cleanup-phase8-quick-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup: $BACKUP_DIR"
echo ""

BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# ============================================================================
# 1. Remove thin wrapper files (2,242 LOC potential)
# ============================================================================
echo "🗑️  1. Removing thin wrapper files..."
echo ""

WRAPPERS=(
    "src/pheno/adapters/sst/wrapper.py"
    "src/pheno/databases/duckdb_client.py"
    "src/pheno/databases/qdrant_wrapper.py"
    "src/pheno/workflows/temporal_client.py"
    "src/pheno/databases/questdb_client.py"
    "src/pheno/core/shared/redis_http_proxy.py"
)

WRAPPER_DELETED=0

for file in "${WRAPPERS[@]}"; do
    if [ -f "$file" ]; then
        # Check if imported
        filename=$(basename "$file" .py)
        import_count=$(grep -r "import $filename\|from.*$filename" src/pheno --include="*.py" 2>/dev/null | grep -v "$file" | wc -l || echo "0")
        
        if [ "$import_count" -eq "0" ]; then
            LOC=$(wc -l < "$file")
            WRAPPER_DELETED=$((WRAPPER_DELETED + LOC))
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            rm "$file"
            echo "  ✓ Deleted: $file ($LOC LOC)"
        else
            echo "  ⚠ Skipped: $file ($import_count imports)"
        fi
    fi
done

print_status "Wrappers: $WRAPPER_DELETED LOC"
echo ""

# ============================================================================
# 2. Simplify large config files (725 LOC potential)
# ============================================================================
echo "🔧 2. Simplifying config files..."
echo ""

# Remove redundant config files
CONFIGS=(
    "src/pheno/core/shared/configuration/pydantic_settings_config.py"
)

CONFIG_DELETED=0

for file in "${CONFIGS[@]}"; do
    if [ -f "$file" ]; then
        import_count=$(grep -r "pydantic_settings_config" src/pheno --include="*.py" 2>/dev/null | grep -v "$file" | wc -l || echo "0")
        
        if [ "$import_count" -eq "0" ]; then
            LOC=$(wc -l < "$file")
            CONFIG_DELETED=$((CONFIG_DELETED + LOC))
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            rm "$file"
            echo "  ✓ Deleted: $file ($LOC LOC)"
        else
            echo "  ⚠ Skipped: $file ($import_count imports)"
        fi
    fi
done

print_status "Configs: $CONFIG_DELETED LOC"
echo ""

# ============================================================================
# 3. Remove duplicate manager files (771 LOC potential)
# ============================================================================
echo "🗑️  3. Removing duplicate manager files..."
echo ""

MANAGERS=(
    "src/pheno/lib/embeddings_manager.py"
    "src/pheno/lib/orchestration_manager.py"
)

MANAGER_DELETED=0

for file in "${MANAGERS[@]}"; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .py)
        import_count=$(grep -r "import $filename\|from.*$filename" src/pheno --include="*.py" 2>/dev/null | grep -v "$file" | wc -l || echo "0")
        
        if [ "$import_count" -eq "0" ]; then
            LOC=$(wc -l < "$file")
            MANAGER_DELETED=$((MANAGER_DELETED + LOC))
            mkdir -p "$BACKUP_DIR/$(dirname $file)"
            cp "$file" "$BACKUP_DIR/$file"
            rm "$file"
            echo "  ✓ Deleted: $file ($LOC LOC)"
        else
            echo "  ⚠ Skipped: $file ($import_count imports)"
        fi
    fi
done

print_status "Managers: $MANAGER_DELETED LOC"
echo ""

# ============================================================================
# Summary
# ============================================================================

TOTAL_DELETED=$((WRAPPER_DELETED + CONFIG_DELETED + MANAGER_DELETED))

AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Phase 8 Quick Wins Complete!"
echo "==============================="
echo ""
echo "  Wrappers: $WRAPPER_DELETED LOC"
echo "  Configs: $CONFIG_DELETED LOC"
echo "  Managers: $MANAGER_DELETED LOC"
echo "  Total: $TOTAL_DELETED LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup: $BACKUP_DIR"

