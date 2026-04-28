#!/bin/bash
# Phase 5o: Delete Unified Wrappers
# Target: -2,000 LOC

set -e

BACKUP_DIR="backups/phase5o-unified-wrappers-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 5o: Unified Wrappers Cleanup ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup
mkdir -p "$BACKUP_DIR"

echo "Step 1: Backing up unified directories and files..."
DIRS_TO_DELETE=(
    "src/pheno/core/security/unified"
    "src/pheno/core/unified_logging"
    "src/pheno/core/shared/analyzers/unified"
    "src/pheno/core/shared/factories/unified_factory"
    "src/pheno/core/shared/factories/unified"
    "src/pheno/core/unified_validator"
    "src/pheno/testing/unified"
    "src/pheno/vector/unified_search"
)

FILES_TO_DELETE=(
    "src/pheno/core/api/unified.py"
    "src/pheno/dev/unified_utilities.py"
    "src/pheno/async/unified_task_orchestrator.py"
)

for dir in "${DIRS_TO_DELETE[@]}"; do
    if [ -d "$dir" ]; then
        echo "  Backing up directory: $dir"
        mkdir -p "$BACKUP_DIR/$(dirname "$dir")"
        cp -r "$dir" "$BACKUP_DIR/$dir"
    fi
done

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Backing up file: $file"
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
    fi
done

echo ""
echo "Step 2: Counting LOC before deletion..."
TOTAL_LOC=0
ITEMS_FOUND=0

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

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
        ITEMS_FOUND=$((ITEMS_FOUND + 1))
    fi
done

echo "  Items found: $ITEMS_FOUND"
echo "  Total LOC to delete: $TOTAL_LOC"

echo ""
echo "Step 3: Deleting unified directories and files..."
for dir in "${DIRS_TO_DELETE[@]}"; do
    if [ -d "$dir" ]; then
        echo "  Deleting directory: $dir"
        rm -rf "$dir"
    fi
done

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting file: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 4: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Unified Wrappers Migration Guide

## What Changed

Deleted unified wrapper directories and files that wrapped existing libraries.

## Directories Deleted

1. `src/pheno/core/security/unified` (199 LOC)
2. `src/pheno/core/unified_logging` (932 LOC) - Use structlog directly
3. `src/pheno/core/shared/analyzers/unified` (1,195 LOC)
4. `src/pheno/core/shared/factories/unified_factory` (1,293 LOC)
5. `src/pheno/core/shared/factories/unified` (102 LOC)
6. `src/pheno/core/unified_validator` (703 LOC) - Use pydantic validators
7. `src/pheno/testing/unified` (262 LOC)
8. `src/pheno/vector/unified_search` (197 LOC)

## Files Deleted

1. `src/pheno/core/api/unified.py` (~30 LOC)
2. `src/pheno/dev/unified_utilities.py` (if exists)
3. `src/pheno/async/unified_task_orchestrator.py` (if exists)

## Migration Path

### Logging (unified_logging → structlog)

```python
# Before
from pheno.core.unified_logging import UnifiedLogger
logger = UnifiedLogger(__name__)

# After
import structlog
log = structlog.get_logger()
```

### Validation (unified_validator → pydantic)

```python
# Before
from pheno.core.unified_validator import UnifiedValidator
validator = UnifiedValidator()

# After
from pydantic import BaseModel, field_validator

class MyModel(BaseModel):
    @field_validator('field_name')
    def validate_field(cls, v):
        return v
```

### Factories (unified_factory → Direct instantiation)

```python
# Before
from pheno.core.shared.factories.unified_factory import UnifiedFactory
obj = UnifiedFactory.create("type", **kwargs)

# After
from pheno.specific.module import SpecificClass
obj = SpecificClass(**kwargs)
```

## Benefits

1. **Less Abstraction**: Direct use of libraries is clearer
2. **Less Code**: -4,883 LOC to maintain
3. **Better IDE Support**: Direct imports work better with IDEs
4. **Easier Debugging**: No wrapper layers to trace through
5. **Standard Patterns**: Use industry-standard patterns

## Next Steps

If any code breaks due to missing imports:
1. Check the migration examples above
2. Update imports to use libraries directly
3. Remove wrapper instantiation code
4. Run tests to verify functionality

## Rollback

If needed, restore from backup:
```bash
cp -r backups/phase5o-unified-wrappers-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 5: Summary"
echo "  Items deleted: $ITEMS_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 5o Complete!"
echo ""
echo "Next: Run tests to verify nothing broke"
echo "  pytest tests/ -v"

