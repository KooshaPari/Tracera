#!/bin/bash
# Phase 5k: Delete Custom Connection Pools
# Target: -1,000 LOC

set -e

BACKUP_DIR="backups/phase5k-connection-pools-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 5k: Connection Pools Cleanup ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup
mkdir -p "$BACKUP_DIR"

echo "Step 1: Backing up custom connection pool files..."
FILES_TO_DELETE=(
    "src/pheno/lib/connection_pool.py"
    "src/pheno/llm/protocol/optimization/connection_pool.py"
    "src/pheno/optimization/session_pool.py"
)

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Backing up: $file"
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
    fi
done

echo ""
echo "Step 2: Counting LOC before deletion..."
TOTAL_LOC=0
FILES_FOUND=0
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
        FILES_FOUND=$((FILES_FOUND + 1))
    fi
done
echo "  Files found: $FILES_FOUND"
echo "  Total LOC to delete: $TOTAL_LOC"

echo ""
echo "Step 3: Deleting custom connection pool files..."
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 4: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Connection Pool Migration Guide

## What Changed

Deleted custom connection pool implementations in favor of built-in pooling from SQLAlchemy and asyncpg.

## Files Deleted

1. `src/pheno/lib/connection_pool.py` (~640 LOC)
2. `src/pheno/llm/protocol/optimization/connection_pool.py` (~200 LOC)
3. `src/pheno/optimization/session_pool.py` (~100 LOC)

## Migration Path

### Before (Custom Connection Pool)

```python
from pheno.lib.connection_pool import ConnectionPool

pool = ConnectionPool(
    host="localhost",
    port=5432,
    database="mydb",
    min_size=10,
    max_size=20
)
async with pool.acquire() as conn:
    result = await conn.execute("SELECT * FROM users")
```

### After (SQLAlchemy)

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/mydb",
    pool_size=10,
    max_overflow=10
)

async with engine.begin() as conn:
    result = await conn.execute("SELECT * FROM users")
```

### After (asyncpg)

```python
import asyncpg

pool = await asyncpg.create_pool(
    host="localhost",
    port=5432,
    database="mydb",
    user="user",
    password="pass",
    min_size=10,
    max_size=20
)

async with pool.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users")
```

## Benefits

1. **Battle-tested**: SQLAlchemy and asyncpg are used by millions
2. **Better Performance**: Highly optimized connection pooling
3. **Less Code**: -1,000 LOC to maintain
4. **More Features**: Connection recycling, health checks, etc.
5. **Better Docs**: Excellent documentation

## Next Steps

If any code breaks due to missing imports:
1. Check the migration examples above
2. Update imports to use SQLAlchemy or asyncpg
3. Update connection pool initialization code
4. Run tests to verify functionality

## Rollback

If needed, restore from backup:
```bash
cp -r backups/phase5k-connection-pools-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 5: Summary"
echo "  Files deleted: $FILES_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 5k Complete!"
echo ""
echo "Next: Run tests to verify nothing broke"
echo "  pytest tests/ -v"

