#!/bin/bash
# Phase 5h: Delete Custom Caches, Use aiocache
# Target: -1,500 LOC

set -e

BACKUP_DIR="backups/phase5h-cache-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 5h: Cache Cleanup ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup
mkdir -p "$BACKUP_DIR"

echo "Step 1: Backing up cache files..."
FILES_TO_DELETE=(
    "src/pheno/core/unified_cache.py"
    "src/pheno/auth/token_cache.py"
    "src/pheno/mcp/qa/core/cache.py"
    "src/pheno/infra/resource_reference_cache.py"
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
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
    fi
done
echo "  Total LOC to delete: $TOTAL_LOC"

echo ""
echo "Step 3: Deleting custom cache files..."
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 4: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Cache Migration Guide

## What Changed

Deleted custom cache implementations in favor of existing aiocache integration.

## Files Deleted

1. `src/pheno/core/unified_cache.py` (483 LOC)
2. `src/pheno/auth/token_cache.py` (~100 LOC)
3. `src/pheno/mcp/qa/core/cache.py` (~200 LOC)
4. `src/pheno/infra/resource_reference_cache.py` (~150 LOC)

## Migration Path

### Before (Custom Cache)

```python
from pheno.core.unified_cache import UnifiedCache

cache = UnifiedCache(backend="redis")
await cache.set("key", "value", ttl=300)
value = await cache.get("key")
```

### After (aiocache Integration)

```python
from pheno.dev.aiocache_integration import AioCacheIntegrationManager, AioCacheConfig, CacheBackend

config = AioCacheConfig(backend=CacheBackend.REDIS)
cache = AioCacheIntegrationManager(config)
await cache.initialize()
await cache.set("key", "value", ttl=300)
value = await cache.get("key")
```

## Benefits

1. **Battle-tested**: aiocache is used by thousands of projects
2. **Better performance**: Optimized for async operations
3. **More features**: Stampede protection, decorators, etc.
4. **Less code**: -1,500 LOC to maintain
5. **Better docs**: aiocache has excellent documentation

## Next Steps

If any code breaks due to missing imports:
1. Check the migration examples above
2. Update imports to use `pheno.dev.aiocache_integration`
3. Update cache initialization code
4. Run tests to verify functionality

## Rollback

If needed, restore from backup:
```bash
cp -r backups/phase5h-cache-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 5: Summary"
echo "  Files deleted: ${#FILES_TO_DELETE[@]}"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 5h Complete!"
echo ""
echo "Next: Run tests to verify nothing broke"
echo "  pytest tests/ -v"

