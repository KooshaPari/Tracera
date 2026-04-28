#!/bin/bash
# Phase 6: Aggressive Cleanup - Remove Duplicate Directories
# Target: Remaining ~17,000 LOC

set -e

BACKUP_DIR="backups/phase6-aggressive-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 6: Aggressive Cleanup ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

mkdir -p "$BACKUP_DIR"

echo "Step 1: Identifying duplicate/redundant directories..."

# Duplicate directories (database vs databases, workflow vs workflows, etc.)
DUPLICATE_DIRS=(
    "src/pheno/databases"
    "src/pheno/workflows"
    "src/pheno/infrastructure"
)

# Redundant registry/support/variant files
REDUNDANT_FILES=(
    "src/pheno/core/adapter_registry.py"
    "src/pheno/core/adapter_support.py"
    "src/pheno/core/adapter_variants.py"
    "src/pheno/core/database_support.py"
    "src/pheno/core/database_variants.py"
    "src/pheno/core/monitoring_support.py"
    "src/pheno/core/monitoring_variants.py"
    "src/pheno/core/port_support.py"
    "src/pheno/core/port_variants.py"
    "src/pheno/core/security_support.py"
    "src/pheno/core/security_variants.py"
)

# Duplicate export files
EXPORT_FILES=(
    "src/pheno/core/_configuration_exports.py"
    "src/pheno/core/_database_exports.py"
    "src/pheno/core/_monitoring_exports.py"
    "src/pheno/core/_port_exports.py"
    "src/pheno/core/_security_exports.py"
    "src/pheno/core/_storage_exports.py"
    "src/pheno/core/_utility_exports.py"
)

# Redundant single-file modules
SINGLE_FILE_MODULES=(
    "src/pheno/credentials.py"
    "src/pheno/creds.py"
    "src/pheno/stream.py"
    "src/pheno/core/serialization.py"
    "src/pheno/core/exception_factory.py"
    "src/pheno/core/core_facade.py"
    "src/pheno/core/data_processor.py"
    "src/pheno/core/pathing.py"
    "src/pheno/core/attrs_utils.py"
)

# Large scaffold/generator files (code generation, not runtime)
SCAFFOLD_FILES=(
    "src/pheno/patterns/crud/scaffold.py"
    "src/pheno/deployment/systemd/generator.py"
    "src/pheno/deployment/k8s/hikaru_generator.py"
    "src/pheno/dev/sphinx/api_generator.py"
)

echo "Step 2: Backing up files and directories..."

for dir in "${DUPLICATE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  Backing up directory: $dir"
        mkdir -p "$BACKUP_DIR/$(dirname "$dir")"
        cp -r "$dir" "$BACKUP_DIR/$dir"
    fi
done

ALL_FILES=("${REDUNDANT_FILES[@]}" "${EXPORT_FILES[@]}" "${SINGLE_FILE_MODULES[@]}" "${SCAFFOLD_FILES[@]}")
for file in "${ALL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Backing up file: $file"
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
    fi
done

echo ""
echo "Step 3: Counting LOC..."
TOTAL_LOC=0
ITEMS_FOUND=0

for dir in "${DUPLICATE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        LOC=$(find "$dir" -name "*.py" -type f | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        if [ -n "$LOC" ] && [ "$LOC" != "0" ]; then
            echo "  $dir: $LOC LOC"
            TOTAL_LOC=$((TOTAL_LOC + LOC))
            ITEMS_FOUND=$((ITEMS_FOUND + 1))
        fi
    fi
done

for file in "${ALL_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
        ITEMS_FOUND=$((ITEMS_FOUND + 1))
    fi
done

echo "  Total items: $ITEMS_FOUND"
echo "  Total LOC: $TOTAL_LOC"

echo ""
echo "Step 4: Deleting files and directories..."

for dir in "${DUPLICATE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  Deleting directory: $dir"
        rm -rf "$dir"
    fi
done

for file in "${ALL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting file: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 5: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Phase 6 Aggressive Cleanup Migration Guide

## What Changed

Deleted duplicate directories and redundant support/variant/export files.

## Duplicate Directories Deleted

1. `src/pheno/databases/` - Use `src/pheno/database/` instead
2. `src/pheno/workflows/` - Use `src/pheno/workflow/` instead
3. `src/pheno/infrastructure/` - Use `src/pheno/infra/` instead

## Redundant Files Deleted

### Support/Variant Files (11 files)
- `core/adapter_support.py`, `core/adapter_variants.py`
- `core/database_support.py`, `core/database_variants.py`
- `core/monitoring_support.py`, `core/monitoring_variants.py`
- `core/port_support.py`, `core/port_variants.py`
- `core/security_support.py`, `core/security_variants.py`
- `core/adapter_registry.py`

### Export Files (7 files)
- `core/_configuration_exports.py`
- `core/_database_exports.py`
- `core/_monitoring_exports.py`
- `core/_port_exports.py`
- `core/_security_exports.py`
- `core/_storage_exports.py`
- `core/_utility_exports.py`

### Single-File Modules (9 files)
- `credentials.py`, `creds.py` - Use `credentials/` package
- `stream.py` - Use `events/streaming.py`
- `core/serialization.py` - Use pydantic/cattrs
- `core/exception_factory.py` - Use `exceptions/`
- `core/core_facade.py` - Direct imports
- `core/data_processor.py` - Use specific processors
- `core/pathing.py` - Use pathlib
- `core/attrs_utils.py` - Use attrs directly

### Scaffold/Generator Files (4 files)
- `patterns/crud/scaffold.py`
- `deployment/systemd/generator.py`
- `deployment/k8s/hikaru_generator.py`
- `dev/sphinx/api_generator.py`

## Migration Examples

### Duplicate Directories

```python
# Before
from pheno.databases import Database
from pheno.workflows import Workflow
from pheno.infrastructure import Infra

# After
from pheno.database import Database
from pheno.workflow import Workflow
from pheno.infra import Infra
```

### Support/Variant Files

```python
# Before
from pheno.core.adapter_support import get_adapter
from pheno.core.adapter_variants import AdapterVariant

# After
from pheno.core.adapters import get_adapter, AdapterVariant
```

### Export Files

```python
# Before
from pheno.core._database_exports import *

# After
from pheno.core.database import Session, Engine
```

### Single-File Modules

```python
# Before
from pheno.credentials import Credentials
from pheno.creds import Creds

# After
from pheno.credentials import Credentials
```

## Benefits

1. **Less Duplication**: Removed duplicate directories
2. **Cleaner Structure**: Single canonical location for each module
3. **Less Confusion**: No more database vs databases
4. **Simpler Imports**: Direct imports instead of re-exports

## Rollback

```bash
cp -r backups/phase6-aggressive-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 6: Summary"
echo "  Items deleted: $ITEMS_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 6 Aggressive Cleanup Complete!"

