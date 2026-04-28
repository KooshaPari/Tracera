#!/bin/bash
# Phase 6 - Tier 2: Medium Priority Consolidation
# TUI Dashboard, Container Orchestration, Service Registry

set -e

echo "🔧 Phase 6 - Tier 2: Medium Priority Consolidation"
echo "==================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase6-tier2-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count LOC before
BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# ============================================================================
# 1. TUI Dashboard (700 LOC)
# ============================================================================
echo "🗑️  1. Removing custom TUI dashboard..."
echo ""

TUI_FILES=(
    "src/pheno/infra/tui_dashboard.py"
)

TUI_DELETED=0

for file in "${TUI_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        TUI_DELETED=$((TUI_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "TUI Dashboard: Deleted $TUI_DELETED LOC"
echo "  → Use Textual framework"
echo ""

# ============================================================================
# 2. Container Orchestration (600 LOC)
# ============================================================================
echo "🗑️  2. Removing container orchestration wrapper..."
echo ""

CONTAINER_FILES=(
    "src/pheno/infra/resources/container.py"
)

CONTAINER_DELETED=0

for file in "${CONTAINER_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        CONTAINER_DELETED=$((CONTAINER_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Container Orchestration: Deleted $CONTAINER_DELETED LOC"
echo "  → Use docker-py directly"
echo ""

# ============================================================================
# 3. Service Registry (1,100 LOC)
# ============================================================================
echo "🗑️  3. Removing custom service registry..."
echo ""

REGISTRY_FILES=(
    "src/pheno/infra/global_registry.py"
    "src/pheno/infra/resources/registry.py"
)

REGISTRY_DELETED=0

for file in "${REGISTRY_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        REGISTRY_DELETED=$((REGISTRY_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Service Registry: Deleted $REGISTRY_DELETED LOC"
echo "  → Use consul-py or etcd3"
echo ""

# ============================================================================
# Summary
# ============================================================================

TOTAL_DELETED=$((TUI_DELETED + CONTAINER_DELETED + REGISTRY_DELETED))

# Count LOC after
AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 After: $AFTER_LOC LOC"
echo ""

SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Tier 2 Complete!"
echo "==================="
echo ""
echo "Summary:"
echo "  TUI Dashboard: $TUI_DELETED LOC"
echo "  Container Orchestration: $CONTAINER_DELETED LOC"
echo "  Service Registry: $REGISTRY_DELETED LOC"
echo "  Total Deleted: $TOTAL_DELETED LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Replacement Libraries:"
echo "  1. Textual - Modern TUI framework"
echo "  2. docker-py - Docker SDK"
echo "  3. consul-py - Service discovery"

