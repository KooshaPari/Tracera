#!/bin/bash
# Phase 6 - Tier 1: High Priority Consolidation
# DB Connection Pooling, OAuth Flows, Task Management

set -e

echo "🔧 Phase 6 - Tier 1: High Priority Consolidation"
echo "================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase6-tier1-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count LOC before
BEFORE_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 Before: $BEFORE_LOC LOC"
echo ""

# ============================================================================
# 1. DB Connection Pooling (1,200 LOC)
# ============================================================================
echo "🗑️  1. Removing custom DB connection pooling..."
echo ""

DB_FILES=(
    "src/pheno/lib/connection_pool.py"
    "src/pheno/lib/db_connection.py"
)

DB_DELETED=0

for file in "${DB_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        DB_DELETED=$((DB_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "DB Connection Pooling: Deleted $DB_DELETED LOC"
echo "  → Use asyncpg.create_pool() directly"
echo ""

# ============================================================================
# 2. OAuth Flows (450 LOC)
# ============================================================================
echo "🗑️  2. Removing custom OAuth flows..."
echo ""

OAUTH_FILES=(
    "src/pheno/credentials/oauth/flows.py"
)

OAUTH_DELETED=0

for file in "${OAUTH_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        OAUTH_DELETED=$((OAUTH_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "OAuth Flows: Deleted $OAUTH_DELETED LOC"
echo "  → Use authlib instead"
echo ""

# ============================================================================
# 3. Task Management (470 LOC)
# ============================================================================
echo "🗑️  3. Removing custom task management..."
echo ""

TASK_FILES=(
    "src/pheno/llm/task_management.py"
)

TASK_DELETED=0

for file in "${TASK_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        TASK_DELETED=$((TASK_DELETED + LOC))
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file"
        rm "$file"
        echo "  ✓ Deleted: $file ($LOC LOC)"
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Task Management: Deleted $TASK_DELETED LOC"
echo "  → Use ARQ (async task queue)"
echo ""

# ============================================================================
# Summary
# ============================================================================

TOTAL_DELETED=$((DB_DELETED + OAUTH_DELETED + TASK_DELETED))

# Count LOC after
AFTER_LOC=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
echo "📊 After: $AFTER_LOC LOC"
echo ""

SAVINGS=$((BEFORE_LOC - AFTER_LOC))

echo "✨ Tier 1 Complete!"
echo "==================="
echo ""
echo "Summary:"
echo "  DB Connection Pooling: $DB_DELETED LOC"
echo "  OAuth Flows: $OAUTH_DELETED LOC"
echo "  Task Management: $TASK_DELETED LOC"
echo "  Total Deleted: $TOTAL_DELETED LOC"
echo ""
echo "  Before: $BEFORE_LOC LOC"
echo "  After: $AFTER_LOC LOC"
echo "  Savings: $SAVINGS LOC"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Replacement Libraries:"
echo "  1. asyncpg.create_pool() - DB pooling"
echo "  2. authlib - OAuth 2.0 flows"
echo "  3. arq - Async task queue"

