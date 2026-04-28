#!/bin/bash
# Phase 6 - Tier 3: Low Priority Consolidation
# Deployment Generators, Process Management, Network Ports, Vendor Manager

set -e

echo "🔧 Phase 6 - Tier 3: Low Priority Consolidation"
echo "================================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase6-tier3-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count LOC before
BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# ============================================================================
# 1. Deployment Generators (950 LOC)
# ============================================================================
echo "🗑️  1. Removing deployment generators..."
echo ""

DEPLOY_FILES=(
    "src/pheno/deployment/k8s/core_generator.py"
    "src/pheno/infra/compose_generator.py"
)

DEPLOY_DELETED=0

for file in "${DEPLOY_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        DEPLOY_DELETED=$((DEPLOY_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Deployment Generators: Deleted $DEPLOY_DELETED LOC"
echo "  → Use Pulumi (already installed)"
echo ""

# ============================================================================
# 2. Process Management (470 LOC)
# ============================================================================
echo "🗑️  2. Removing custom process management..."
echo ""

PROCESS_FILES=(
    "src/pheno/infra/process_cleanup.py"
)

PROCESS_DELETED=0

for file in "${PROCESS_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        PROCESS_DELETED=$((PROCESS_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Process Management: Deleted $PROCESS_DELETED LOC"
echo "  → Use psutil (already installed)"
echo ""

# ============================================================================
# 3. Network Port Management (500 LOC)
# ============================================================================
echo "🗑️  3. Removing network port management..."
echo ""

NETWORK_FILES=(
    "src/pheno/infra/network_ports.py"
)

NETWORK_DELETED=0

for file in "${NETWORK_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        NETWORK_DELETED=$((NETWORK_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Network Port Management: Deleted $NETWORK_DELETED LOC"
echo "  → Use socket stdlib"
echo ""

# ============================================================================
# 4. Vendor Manager (550 LOC)
# ============================================================================
echo "🗑️  4. Removing vendor manager..."
echo ""

VENDOR_FILES=(
    "src/pheno/lib/vendor_manager.py"
)

VENDOR_DELETED=0

for file in "${VENDOR_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        VENDOR_DELETED=$((VENDOR_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Vendor Manager: Deleted $VENDOR_DELETED LOC"
echo "  → Delete (unused)"
echo ""

# ============================================================================
# Summary
# ============================================================================

TOTAL_DELETED=$((DEPLOY_DELETED + PROCESS_DELETED + NETWORK_DELETED + VENDOR_DELETED))

# Count LOC after
AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 After: $AFTER_LOC LOC"
echo ""

SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Tier 3 Complete!"
echo "==================="
echo ""
echo "Summary:"
echo "  Deployment Generators: $DEPLOY_DELETED LOC"
echo "  Process Management: $PROCESS_DELETED LOC"
echo "  Network Port Management: $NETWORK_DELETED LOC"
echo "  Vendor Manager: $VENDOR_DELETED LOC"
echo "  Total Deleted: $TOTAL_DELETED LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Replacement Libraries:"
echo "  1. Pulumi - Infrastructure as Code"
echo "  2. psutil - Process management"
echo "  3. socket - Network utilities"
echo "  4. N/A - Deleted (unused)"

