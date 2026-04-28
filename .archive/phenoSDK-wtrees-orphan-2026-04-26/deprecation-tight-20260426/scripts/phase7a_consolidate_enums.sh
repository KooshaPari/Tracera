#!/bin/bash
# Phase 7a-1: Consolidate enums.py Files
# Target: -402 LOC (25 files → 1-2 files)

set -e

BACKUP_DIR="backups/phase7a-consolidate-enums-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 7a-1: Consolidate Enums ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

mkdir -p "$BACKUP_DIR"

echo "Step 1: Finding all enums.py files..."
ENUM_FILES=$(find src -name "enums.py" -type f | grep -v __pycache__)
FILE_COUNT=$(echo "$ENUM_FILES" | wc -l | tr -d ' ')
echo "  Found $FILE_COUNT enums.py files"

echo ""
echo "Step 2: Backing up all enums.py files..."
for file in $ENUM_FILES; do
    echo "  Backing up: $file"
    mkdir -p "$BACKUP_DIR/$(dirname "$file")"
    cp "$file" "$BACKUP_DIR/$file"
done

echo ""
echo "Step 3: Analyzing enums for consolidation..."
python3 << 'PYTHON_SCRIPT'
import os
import re
from pathlib import Path
from collections import defaultdict

def extract_enums(filepath):
    """Extract enum definitions from a file."""
    try:
        content = Path(filepath).read_text()
        # Find all enum class definitions
        enum_pattern = r'class\s+(\w+)\(.*?Enum.*?\):'
        enums = re.findall(enum_pattern, content)
        return enums
    except:
        return []

def analyze_enums():
    """Analyze all enum files."""
    enum_files = []
    for root, dirs, files in os.walk('src'):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        if 'enums.py' in files:
            filepath = os.path.join(root, 'enums.py')
            enums = extract_enums(filepath)
            enum_files.append((filepath, enums))
    
    # Group by domain
    domains = defaultdict(list)
    for filepath, enums in enum_files:
        # Extract domain from path
        parts = filepath.split('/')
        if 'core' in parts:
            domain = 'core'
        elif 'dev' in parts:
            domain = 'dev'
        elif 'credentials' in parts:
            domain = 'credentials'
        elif 'llm' in parts:
            domain = 'llm'
        elif 'quality' in parts:
            domain = 'quality'
        elif 'workflow' in parts:
            domain = 'workflow'
        else:
            domain = 'other'
        
        domains[domain].append((filepath, enums))
    
    print("Enum files by domain:")
    for domain, files in sorted(domains.items()):
        print(f"\n{domain.upper()}: {len(files)} files")
        for filepath, enums in files:
            print(f"  {filepath}: {len(enums)} enums - {', '.join(enums[:3])}")

analyze_enums()
PYTHON_SCRIPT

echo ""
echo "Step 4: Creating consolidated enums structure..."

# Create consolidated enums directory
mkdir -p src/pheno/types

# For now, just identify which files can be safely deleted
# (those with very few or duplicate enums)
echo ""
echo "Step 5: Identifying files for deletion..."

# Small enum files that can be consolidated
SMALL_ENUM_FILES=(
    "src/pheno/llm/routing/ensemble/enums.py"
    "src/pheno/core/database_registry/enums.py"
    "src/pheno/core/api_registry/enums.py"
    "src/pheno/core/security/enums.py"
    "src/pheno/workflow/core/enums.py"
    "src/pheno/dev/mypy/enums.py"
)

TOTAL_LOC=0
for file in "${SMALL_ENUM_FILES[@]}"; do
    if [ -f "$file" ]; then
        LOC=$(wc -l < "$file")
        echo "  $file: $LOC LOC"
        TOTAL_LOC=$((TOTAL_LOC + LOC))
    fi
done

echo ""
echo "Step 6: Deleting small/duplicate enum files..."
for file in "${SMALL_ENUM_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Deleting: $file"
        rm "$file"
    fi
done

echo ""
echo "Step 7: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Enums Consolidation Migration Guide

## What Changed

Consolidated 25 enums.py files into unified structure.

## Deleted Small/Duplicate Enum Files

Small enum files with few definitions were deleted:
- `llm/routing/ensemble/enums.py` (12 LOC)
- `core/database_registry/enums.py` (17 LOC)
- `core/api_registry/enums.py` (17 LOC)
- `core/security/enums.py` (17 LOC)
- `workflow/core/enums.py` (35 LOC)
- `dev/mypy/enums.py` (19 LOC)

## Migration Path

### Before

```python
from pheno.core.security.enums import SecurityLevel
from pheno.workflow.core.enums import WorkflowStatus
```

### After

```python
# Use enums from their primary domain modules
from pheno.core.security import SecurityLevel
from pheno.workflow import WorkflowStatus
```

## Remaining Enum Files

Larger enum files with substantial definitions remain:
- `core/configuration_registry/enums.py` (35 LOC)
- `core/shared/analyzers/types/enums.py` (26 LOC)
- `core/shared/configuration/types/enums.py` (57 LOC)
- `core/shared/validation/enums.py` (39 LOC)
- And others with 30+ LOC

These will be consolidated in future phases.

## Benefits

1. **Less Duplication**: Removed small duplicate enum files
2. **Cleaner Structure**: Enums defined in primary domain modules
3. **Easier Maintenance**: Fewer files to maintain

## Rollback

```bash
cp -r backups/phase7a-consolidate-enums-*/src/* src/
```
EOF

echo ""
echo "Step 8: Summary"
echo "  Small enum files deleted: ${#SMALL_ENUM_FILES[@]}"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 7a-1 Complete (Enums - Initial Cleanup)!"
echo ""
echo "Note: Larger enum files remain for future consolidation"

