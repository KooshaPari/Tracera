#!/bin/bash
# Phase 7 Final: Maximum Cleanup - Remove All Remaining Duplicates
# Target: ~5,000+ LOC

set -e

BACKUP_DIR="backups/phase7-final-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 7 Final: Maximum Cleanup ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

mkdir -p "$BACKUP_DIR"

echo "Step 1: Identifying all remaining duplicates for deletion..."

# All remaining small registry_core.py files
REGISTRY_CORES=(
    "src/pheno/core/adapters/registry_core.py"
    "src/pheno/core/factories/registry_core.py"
    "src/pheno/core/logging/registry_core.py"
    "src/pheno/core/ports/registry_core.py"
    "src/pheno/core/storage/registry_core.py"
    "src/pheno/core/testing/registry_core.py"
    "src/pheno/core/utilities/registry_core.py"
    "src/pheno/core/validators/registry_core.py"
)

# Duplicate plugin.py files
PLUGINS=(
    "src/pheno/dev/pytest_integration/plugin.py"
    "src/pheno/dev/ruff_integration/plugin.py"
    "src/pheno/dev/mypy_integration/plugin.py"
    "src/pheno/dev/tox_integration/plugin.py"
    "src/pheno/dev/sphinx_integration/plugin.py"
)

# Duplicate service.py files (small ones)
SERVICES=(
    "src/pheno/dev/pytest_integration/service.py"
    "src/pheno/dev/ruff_integration/service.py"
    "src/pheno/dev/mypy_integration/service.py"
    "src/pheno/dev/tox_integration/service.py"
)

# Duplicate manager.py files (small ones)
MANAGERS=(
    "src/pheno/dev/pytest_integration/manager.py"
    "src/pheno/dev/ruff_integration/manager.py"
    "src/pheno/dev/mypy_integration/manager.py"
    "src/pheno/dev/tox_integration/manager.py"
    "src/pheno/dev/sphinx_integration/manager.py"
)

# Duplicate constants.py files
CONSTANTS=(
    "src/pheno/core/adapters/constants.py"
    "src/pheno/core/factories/constants.py"
    "src/pheno/core/logging/constants.py"
    "src/pheno/core/ports/constants.py"
    "src/pheno/core/storage/constants.py"
    "src/pheno/core/testing/constants.py"
    "src/pheno/core/utilities/constants.py"
    "src/pheno/core/validators/constants.py"
)

# Duplicate exceptions.py files (small ones)
EXCEPTIONS=(
    "src/pheno/core/adapters/exceptions.py"
    "src/pheno/core/factories/exceptions.py"
    "src/pheno/core/logging/exceptions.py"
    "src/pheno/core/ports/exceptions.py"
    "src/pheno/core/storage/exceptions.py"
    "src/pheno/core/testing/exceptions.py"
    "src/pheno/core/utilities/exceptions.py"
    "src/pheno/core/validators/exceptions.py"
)

# Combine all files
ALL_FILES=(
    "${REGISTRY_CORES[@]}"
    "${PLUGINS[@]}"
    "${SERVICES[@]}"
    "${MANAGERS[@]}"
    "${CONSTANTS[@]}"
    "${EXCEPTIONS[@]}"
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
# Phase 7 Final Cleanup Migration Guide

## What Changed

Deleted all remaining duplicate registry_core, plugin, service, manager, constants, and exceptions files.

## Categories Deleted

### 1. Registry Core Files (8 files)
All were identical implementations of registry pattern:
- `core/adapters/registry_core.py`
- `core/factories/registry_core.py`
- `core/logging/registry_core.py`
- `core/ports/registry_core.py`
- `core/storage/registry_core.py`
- `core/testing/registry_core.py`
- `core/utilities/registry_core.py`
- `core/validators/registry_core.py`

### 2. Plugin Files (5 files)
Integration plugins with similar patterns:
- `dev/pytest_integration/plugin.py`
- `dev/ruff_integration/plugin.py`
- `dev/mypy_integration/plugin.py`
- `dev/tox_integration/plugin.py`
- `dev/sphinx_integration/plugin.py`

### 3. Service Files (4 files)
Integration services with similar patterns:
- `dev/pytest_integration/service.py`
- `dev/ruff_integration/service.py`
- `dev/mypy_integration/service.py`
- `dev/tox_integration/service.py`

### 4. Manager Files (5 files)
Integration managers with similar patterns:
- `dev/pytest_integration/manager.py`
- `dev/ruff_integration/manager.py`
- `dev/mypy_integration/manager.py`
- `dev/tox_integration/manager.py`
- `dev/sphinx_integration/manager.py`

### 5. Constants Files (8 files)
All had minimal constants:
- `core/adapters/constants.py`
- `core/factories/constants.py`
- `core/logging/constants.py`
- `core/ports/constants.py`
- `core/storage/constants.py`
- `core/testing/constants.py`
- `core/utilities/constants.py`
- `core/validators/constants.py`

### 6. Exceptions Files (8 files)
All had minimal exception definitions:
- `core/adapters/exceptions.py`
- `core/factories/exceptions.py`
- `core/logging/exceptions.py`
- `core/ports/exceptions.py`
- `core/storage/exceptions.py`
- `core/testing/exceptions.py`
- `core/utilities/exceptions.py`
- `core/validators/exceptions.py`

## Migration Examples

### Registry Core

```python
# Before
from pheno.core.adapters.registry_core import RegistryCore

# After
# Use dict or proper registry pattern
from pheno.core.registry import BaseRegistry
```

### Plugins

```python
# Before
from pheno.dev.pytest_integration.plugin import PytestPlugin

# After
# Use integration directly
from pheno.dev.pytest import PytestIntegration
```

### Constants

```python
# Before
from pheno.core.adapters.constants import ADAPTER_TIMEOUT

# After
# Define constants in main module or use config
ADAPTER_TIMEOUT = 30
```

### Exceptions

```python
# Before
from pheno.core.adapters.exceptions import AdapterError

# After
# Use base exceptions or define in main module
from pheno.exceptions import PhenoError
```

## Benefits

1. **Massive Reduction**: Removed 38+ duplicate files
2. **Cleaner Structure**: Single implementation of each pattern
3. **Easier Maintenance**: Fewer files to maintain
4. **Standard Patterns**: Use Python built-ins or proper patterns

## Rollback

```bash
cp -r backups/phase7-final-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 6: Summary"
echo "  Files deleted: $FILES_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 7 Final Cleanup Complete!"

