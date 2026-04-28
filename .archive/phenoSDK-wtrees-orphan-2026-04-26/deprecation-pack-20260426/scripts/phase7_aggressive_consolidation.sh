#!/bin/bash
# Phase 7: Aggressive Consolidation of Duplicate Files
# Target: ~7,000 LOC (config, models, types, utils, small duplicates)

set -e

BACKUP_DIR="backups/phase7-aggressive-consolidation-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 7: Aggressive Consolidation ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

mkdir -p "$BACKUP_DIR"

echo "Step 1: Identifying small/duplicate files for deletion..."

# Small config files (< 50 LOC or duplicates)
SMALL_CONFIGS=(
    "src/pheno/dev/pytest_integration/config.py"
    "src/pheno/dev/ruff_integration/config.py"
    "src/pheno/dev/mypy_integration/config.py"
    "src/pheno/dev/tox_integration/config.py"
    "src/pheno/dev/sphinx_integration/config.py"
    "src/pheno/core/security_factory/config.py"
    "src/pheno/core/api_registry/config.py"
    "src/pheno/core/database_registry/config.py"
    "src/pheno/quality/export_import/config.py"
)

# Small models files (< 50 LOC or duplicates)
SMALL_MODELS=(
    "src/pheno/dev/pytest_integration/models.py"
    "src/pheno/dev/ruff_integration/models.py"
    "src/pheno/dev/mypy_integration/models.py"
    "src/pheno/dev/tox_integration/models.py"
    "src/pheno/core/security_factory/models.py"
    "src/pheno/core/api_registry/models.py"
    "src/pheno/core/database_registry/models.py"
)

# Small types files (< 50 LOC or duplicates)
SMALL_TYPES=(
    "src/pheno/dev/pytest_integration/types.py"
    "src/pheno/dev/ruff_integration/types.py"
    "src/pheno/dev/mypy_integration/types.py"
    "src/pheno/core/security_factory/types.py"
    "src/pheno/core/api_registry/types.py"
)

# Duplicate registry files
DUPLICATE_REGISTRIES=(
    "src/pheno/core/adapter_registry.py"
    "src/pheno/core/configuration_registry.py"
    "src/pheno/core/factory_registry.py"
    "src/pheno/core/logging_registry.py"
    "src/pheno/core/port_registry.py"
    "src/pheno/core/storage_registry.py"
    "src/pheno/core/testing_registry.py"
    "src/pheno/core/utility_registry.py"
    "src/pheno/core/validator_registry.py"
)

# Duplicate instance manager files
DUPLICATE_INSTANCE_MANAGERS=(
    "src/pheno/core/adapters/instance_manager.py"
    "src/pheno/core/factories/instance_manager.py"
    "src/pheno/core/logging/instance_manager.py"
    "src/pheno/core/ports/instance_manager.py"
    "src/pheno/core/storage/instance_manager.py"
    "src/pheno/core/testing/instance_manager.py"
    "src/pheno/core/utilities/instance_manager.py"
    "src/pheno/core/validators/instance_manager.py"
)

# Combine all files
ALL_FILES=(
    "${SMALL_CONFIGS[@]}"
    "${SMALL_MODELS[@]}"
    "${SMALL_TYPES[@]}"
    "${DUPLICATE_REGISTRIES[@]}"
    "${DUPLICATE_INSTANCE_MANAGERS[@]}"
)

echo "Step 2: Backing up files..."
for file in "${ALL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Backing up: $file"
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
    fi
done

echo ""
echo "Step 3: Counting LOC..."
TOTAL_LOC=0
FILES_FOUND=0

for file in "${ALL_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
        FILES_FOUND=$((FILES_FOUND + 1))
    fi
done

echo ""
echo "  Total files: $FILES_FOUND"
echo "  Total LOC: $TOTAL_LOC"

echo ""
echo "Step 4: Deleting files..."
for file in "${ALL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 5: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Phase 7 Aggressive Consolidation Migration Guide

## What Changed

Deleted small/duplicate config, models, types, registry, and instance_manager files.

## Categories Deleted

### 1. Small Config Files (9 files)
Integration configs with minimal settings:
- `dev/pytest_integration/config.py`
- `dev/ruff_integration/config.py`
- `dev/mypy_integration/config.py`
- `dev/tox_integration/config.py`
- `dev/sphinx_integration/config.py`
- `core/security_factory/config.py`
- `core/api_registry/config.py`
- `core/database_registry/config.py`
- `quality/export_import/config.py`

### 2. Small Models Files (7 files)
Integration models with minimal definitions:
- `dev/pytest_integration/models.py`
- `dev/ruff_integration/models.py`
- `dev/mypy_integration/models.py`
- `dev/tox_integration/models.py`
- `core/security_factory/models.py`
- `core/api_registry/models.py`
- `core/database_registry/models.py`

### 3. Small Types Files (5 files)
Integration types with minimal definitions:
- `dev/pytest_integration/types.py`
- `dev/ruff_integration/types.py`
- `dev/mypy_integration/types.py`
- `core/security_factory/types.py`
- `core/api_registry/types.py`

### 4. Duplicate Registry Files (9 files)
All were thin wrappers around dict:
- `core/adapter_registry.py`
- `core/configuration_registry.py`
- `core/factory_registry.py`
- `core/logging_registry.py`
- `core/port_registry.py`
- `core/storage_registry.py`
- `core/testing_registry.py`
- `core/utility_registry.py`
- `core/validator_registry.py`

### 5. Duplicate Instance Managers (8 files)
All were identical implementations:
- `core/adapters/instance_manager.py`
- `core/factories/instance_manager.py`
- `core/logging/instance_manager.py`
- `core/ports/instance_manager.py`
- `core/storage/instance_manager.py`
- `core/testing/instance_manager.py`
- `core/utilities/instance_manager.py`
- `core/validators/instance_manager.py`

## Migration Examples

### Config Files

```python
# Before
from pheno.dev.pytest_integration.config import PytestConfig

# After
# Use pydantic-settings directly or main config
from pheno.config import DevConfig
```

### Models Files

```python
# Before
from pheno.dev.pytest_integration.models import TestResult

# After
# Use pydantic models directly
from pydantic import BaseModel

class TestResult(BaseModel):
    pass
```

### Registry Files

```python
# Before
from pheno.core.adapter_registry import AdapterRegistry
registry = AdapterRegistry()

# After
# Use dict directly or proper registry pattern
from pheno.core.registries.adapter import registry_core
```

### Instance Managers

```python
# Before
from pheno.core.adapters.instance_manager import InstanceManager

# After
# Use dict or proper singleton pattern
instances = {}
```

## Benefits

1. **Less Duplication**: Removed duplicate implementations
2. **Cleaner Structure**: Fewer files to maintain
3. **Standard Patterns**: Use built-in dict or proper patterns
4. **Easier Navigation**: Less clutter

## Rollback

```bash
cp -r backups/phase7-aggressive-consolidation-*/src/* src/
```
EOF

echo ""
echo "Step 6: Summary"
echo "  Files deleted: $FILES_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 7 Aggressive Consolidation Complete!"

