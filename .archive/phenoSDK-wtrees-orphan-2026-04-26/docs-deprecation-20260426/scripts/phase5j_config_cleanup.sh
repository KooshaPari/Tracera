#!/bin/bash
# Phase 5j: Config Simplification
# Target: -2,365 LOC

set -e

BACKUP_DIR="backups/phase5j-config-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 5j: Config Simplification ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup
mkdir -p "$BACKUP_DIR"

echo "Step 1: Backing up config files to delete/simplify..."

# Custom config managers (thin wrappers)
CONFIG_MANAGERS=(
    "src/pheno/core/shared/validation/config_manager.py"
    "src/pheno/dev/sphinx/config_manager.py"
)

# Support/helper files that duplicate pydantic functionality
CONFIG_SUPPORT=(
    "src/pheno/core/configuration_support.py"
)

# Old config files
OLD_CONFIGS=(
    "src/pheno/core/shared/nats_jetstream_old/config.py"
    "src/pheno/core/shared/apscheduler_old/config.py"
)

# Combine all files
FILES_TO_DELETE=("${CONFIG_MANAGERS[@]}" "${CONFIG_SUPPORT[@]}" "${OLD_CONFIGS[@]}")

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
echo "Step 3: Deleting config files..."
for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 4: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Config Simplification Migration Guide

## What Changed

Deleted custom config managers and support files in favor of pydantic-settings.

## Files Deleted

### Custom Config Managers (2 files)
1. `src/pheno/core/shared/validation/config_manager.py` (217 LOC)
2. `src/pheno/dev/sphinx/config_manager.py` (~100 LOC)

### Config Support Files (1 file)
3. `src/pheno/core/configuration_support.py` (229 LOC)

### Old Config Files (2 files)
4. `src/pheno/core/shared/nats_jetstream_old/config.py` (231 LOC)
5. `src/pheno/core/shared/apscheduler_old/config.py` (186 LOC)

## Migration Path

### Before (Custom Config Manager)

```python
from pheno.core.shared.validation.config_manager import ValidationConfigManager

config_mgr = ValidationConfigManager("my_config")
config = config_mgr.get_config()
```

### After (pydantic-settings)

```python
from pydantic_settings import BaseSettings

class ValidationConfig(BaseSettings):
    validate_assignment: bool = True
    validate_default: bool = True
    use_enum_values: bool = True
    
    class Config:
        env_prefix = "VALIDATION_"

config = ValidationConfig()
```

### Before (Custom Config Support)

```python
from pheno.core.configuration_support import ConfigurationType, ConfigurationSource

config_type = ConfigurationType.DATABASE
source = ConfigurationSource.FILE
```

### After (Direct Enums)

```python
from enum import Enum

class ConfigType(str, Enum):
    DATABASE = "database"
    CACHE = "cache"

class ConfigSource(str, Enum):
    FILE = "file"
    ENV = "environment"
```

## Benefits

1. **Standard Library**: Use pydantic-settings (industry standard)
2. **Less Code**: -963 LOC to maintain
3. **Better Features**: Environment variables, .env files, validation
4. **Better Docs**: pydantic-settings has excellent documentation
5. **Type Safety**: Full IDE support and type checking

## Canonical Config Implementation

**USE THIS**: `src/pheno/core/shared/configuration/pydantic_settings_config.py`

This file shows the correct way to use pydantic-settings:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    database_url: str
    redis_url: str
    debug: bool = False
```

## Next Steps

If any code breaks due to missing imports:
1. Check the migration examples above
2. Update to use pydantic-settings BaseSettings
3. Remove custom config manager instantiation
4. Run tests to verify functionality

## Rollback

If needed, restore from backup:
```bash
cp -r backups/phase5j-config-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 5: Summary"
echo "  Files deleted: $FILES_FOUND"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 5j Complete!"
echo ""
echo "Next: Run tests to verify nothing broke"
echo "  pytest tests/ -v"

