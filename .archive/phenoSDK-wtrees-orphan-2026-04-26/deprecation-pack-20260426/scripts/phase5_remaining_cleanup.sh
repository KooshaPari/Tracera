#!/bin/bash
# Phase 5 Remaining: Quick cleanup of remaining phases
# Phases: 5c, 5d, 5e, 5g, 5l, 5m

set -e

BACKUP_DIR="backups/phase5-remaining-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 5 Remaining Cleanup ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup
mkdir -p "$BACKUP_DIR"

echo "Step 1: Finding files to delete..."

# Phase 5l: Custom queue implementations
QUEUE_FILES=(
    "src/pheno/async/queue_manager.py"
    "src/pheno/async/priority_queue.py"
)

# Phase 5m: Custom async utilities  
ASYNC_UTILS=(
    "src/pheno/async/async_helpers.py"
    "src/pheno/async/async_utils.py"
)

# Phase 5g: Duplicate utilities
DUPLICATE_UTILS=(
    "src/pheno/core/concated_utilities.py"
    "src/pheno/core/shared/utilities/helpers.py"
    "src/pheno/core/shared/utilities/common.py"
)

# Old/deprecated files
OLD_FILES=(
    "src/pheno/core/shared/auth_modern_old"
    "src/pheno/core/shared/fastapi_app_old"
    "src/pheno/core/shared/supavisor_deployment_old"
    "src/pheno/core/shared/multi_tenant_isolation_old"
)

# Combine all
FILES_TO_DELETE=("${QUEUE_FILES[@]}" "${ASYNC_UTILS[@]}" "${DUPLICATE_UTILS[@]}")
DIRS_TO_DELETE=("${OLD_FILES[@]}")

echo "Step 2: Backing up files..."
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Backing up file: $file"
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
    fi
done

for dir in "${DIRS_TO_DELETE[@]}"; do
    if [ -d "$dir" ]; then
        echo "  Backing up directory: $dir"
        mkdir -p "$BACKUP_DIR/$(dirname "$dir")"
        cp -r "$dir" "$BACKUP_DIR/$dir"
    fi
done

echo ""
echo "Step 3: Counting LOC..."
TOTAL_LOC=0
ITEMS_FOUND=0

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
        ITEMS_FOUND=$((ITEMS_FOUND + 1))
    fi
done

for dir in "${DIRS_TO_DELETE[@]}"; do
    if [ -d "$dir" ]; then
        LOC=$(find "$dir" -name "*.py" -type f | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        if [ -n "$LOC" ] && [ "$LOC" != "0" ]; then
            echo "  $dir: $LOC LOC"
            TOTAL_LOC=$((TOTAL_LOC + LOC))
            ITEMS_FOUND=$((ITEMS_FOUND + 1))
        fi
    fi
done

echo "  Total items: $ITEMS_FOUND"
echo "  Total LOC: $TOTAL_LOC"

echo ""
echo "Step 4: Deleting files and directories..."
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting file: $file"
        rm "$file"
    fi
done

for dir in "${DIRS_TO_DELETE[@]}"; do
    if [ -d "$dir" ]; then
        echo "  Deleting directory: $dir"
        rm -rf "$dir"
    fi
done

echo ""
echo "Step 5: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Phase 5 Remaining Cleanup Migration Guide

## What Changed

Deleted remaining custom implementations and old/deprecated code.

## Phases Completed

### Phase 5l: Queues
- Deleted custom queue implementations
- **Use**: `asyncio.Queue` (built-in)

### Phase 5m: Async Utils
- Deleted custom async utilities
- **Use**: `anyio` library or `asyncio` built-ins

### Phase 5g: Utilities
- Deleted duplicate utility files
- **Use**: Consolidated utils in single location

### Old/Deprecated Directories
- Deleted `*_old` directories
- Use modern implementations instead

## Migration Examples

### Queues (Phase 5l)

```python
# Before
from pheno.async.queue_manager import QueueManager
queue = QueueManager()

# After
import asyncio
queue = asyncio.Queue()
```

### Async Utils (Phase 5m)

```python
# Before
from pheno.async.async_helpers import run_async
result = await run_async(func)

# After
import asyncio
result = await asyncio.create_task(func())
```

### Utilities (Phase 5g)

```python
# Before
from pheno.core.concated_utilities import some_util

# After
from pheno.utils import some_util
```

## Benefits

1. **Standard Library**: Use Python built-ins
2. **Less Code**: Removed duplicate implementations
3. **Better Maintained**: Standard libraries are well-tested
4. **Simpler**: Fewer custom abstractions

## Rollback

```bash
cp -r backups/phase5-remaining-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 6: Summary"
echo "  Items deleted: $ITEMS_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 5 Remaining Complete!"

