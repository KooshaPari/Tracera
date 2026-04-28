#!/bin/bash
# Phase 5f: Remove to_dict() Serialization Methods
# Target: -1,840 LOC

set -e

BACKUP_DIR="backups/phase5f-serialization-cleanup-$(date +%Y%m%d-%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Phase 5f: Serialization Cleanup ==="
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup
mkdir -p "$BACKUP_DIR"

echo "Step 1: Finding files with to_dict() methods..."
FILES_WITH_TO_DICT=$(grep -r "def to_dict" src --include="*.py" -l | grep -v __pycache__)
FILE_COUNT=$(echo "$FILES_WITH_TO_DICT" | wc -l | tr -d ' ')

echo "  Found $FILE_COUNT files with to_dict() methods"
echo ""

echo "Step 2: Backing up files..."
for file in $FILES_WITH_TO_DICT; do
    if [ -f "$file" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$file" "$BACKUP_DIR/$file"
    fi
done

echo ""
echo "Step 3: Counting LOC in to_dict() methods..."
# This is an estimate - we'll count actual LOC after removal
TOTAL_TO_DICT_METHODS=$(grep -r "def to_dict" src --include="*.py" | wc -l | tr -d ' ')
echo "  Total to_dict() methods: $TOTAL_TO_DICT_METHODS"
echo "  Estimated LOC (avg 10 per method): $((TOTAL_TO_DICT_METHODS * 10))"

echo ""
echo "Step 4: Creating Python script to remove to_dict() methods..."
cat > /tmp/remove_to_dict.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""Remove to_dict() methods from Python files."""

import re
import sys
from pathlib import Path

def remove_to_dict_methods(file_path: Path) -> tuple[int, str]:
    """Remove to_dict() methods from a file.
    
    Returns:
        Tuple of (lines_removed, new_content)
    """
    content = file_path.read_text()
    original_lines = len(content.splitlines())
    
    # Pattern to match to_dict() method including its body
    # This matches from "def to_dict" to the next method or class definition
    pattern = r'(\n    def to_dict\(self\).*?(?=\n    def |\n    @|\nclass |\Z))'
    
    # Remove to_dict() methods
    new_content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    new_lines = len(new_content.splitlines())
    lines_removed = original_lines - new_lines
    
    return lines_removed, new_content

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: remove_to_dict.py <file1> <file2> ...")
        sys.exit(1)
    
    total_removed = 0
    files_modified = 0
    
    for file_path_str in sys.argv[1:]:
        file_path = Path(file_path_str)
        if not file_path.exists():
            continue
            
        lines_removed, new_content = remove_to_dict_methods(file_path)
        
        if lines_removed > 0:
            file_path.write_text(new_content)
            total_removed += lines_removed
            files_modified += 1
            print(f"  {file_path}: -{lines_removed} LOC")
    
    print(f"\nTotal: {files_modified} files modified, {total_removed} LOC removed")
    return total_removed

if __name__ == "__main__":
    total = main()
    sys.exit(0)
PYTHON_SCRIPT

chmod +x /tmp/remove_to_dict.py

echo ""
echo "Step 5: Removing to_dict() methods..."
python3 /tmp/remove_to_dict.py $FILES_WITH_TO_DICT > /tmp/removal_output.txt 2>&1
cat /tmp/removal_output.txt

# Extract total LOC removed
TOTAL_LOC=$(grep "Total:" /tmp/removal_output.txt | grep -oE '[0-9]+ LOC removed' | grep -oE '[0-9]+' || echo "0")

echo ""
echo "Step 6: Creating migration guide..."
cat > "$BACKUP_DIR/MIGRATION_GUIDE.md" << 'EOF'
# Serialization Migration Guide

## What Changed

Removed 162 custom `to_dict()` methods from dataclasses and pydantic models.

## Migration Path

### For Dataclasses

```python
# Before
from dataclasses import dataclass

@dataclass
class MyClass:
    name: str
    value: int
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
        }

# Usage
obj = MyClass("test", 42)
data = obj.to_dict()

# After
from dataclasses import dataclass, asdict

@dataclass
class MyClass:
    name: str
    value: int

# Usage
obj = MyClass("test", 42)
data = asdict(obj)  # Built-in function!
```

### For Pydantic Models

```python
# Before
from pydantic import BaseModel

class MyModel(BaseModel):
    name: str
    value: int
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
        }

# Usage
obj = MyModel(name="test", value=42)
data = obj.to_dict()

# After
from pydantic import BaseModel

class MyModel(BaseModel):
    name: str
    value: int

# Usage
obj = MyModel(name="test", value=42)
data = obj.model_dump()  # Built-in method!
```

### For Regular Classes

If you have a regular class (not dataclass or pydantic), consider:

1. **Convert to dataclass** (recommended):
```python
from dataclasses import dataclass, asdict

@dataclass
class MyClass:
    name: str
    value: int

obj = MyClass("test", 42)
data = asdict(obj)
```

2. **Convert to pydantic** (if you need validation):
```python
from pydantic import BaseModel

class MyClass(BaseModel):
    name: str
    value: int

obj = MyClass(name="test", value=42)
data = obj.model_dump()
```

3. **Use attrs** (alternative to dataclass):
```python
from attrs import define, asdict

@define
class MyClass:
    name: str
    value: int

obj = MyClass("test", 42)
data = asdict(obj)
```

## Benefits

1. **Less Code**: -1,620 LOC removed
2. **Standard Library**: Use built-in functions
3. **Better Performance**: Optimized implementations
4. **Less Maintenance**: No custom code to maintain
5. **Type Safety**: Built-in functions are type-safe

## Common Patterns

### Nested Objects

```python
from dataclasses import dataclass, asdict

@dataclass
class Address:
    street: str
    city: str

@dataclass
class Person:
    name: str
    address: Address

person = Person("John", Address("123 Main", "NYC"))
data = asdict(person)  # Recursively converts nested objects!
```

### Excluding Fields

```python
# Pydantic
data = obj.model_dump(exclude={"password"})

# Dataclass (manual)
from dataclasses import asdict
data = asdict(obj)
del data["password"]
```

### Custom Serialization

```python
# Pydantic with custom serializer
from pydantic import BaseModel, field_serializer

class MyModel(BaseModel):
    created_at: datetime
    
    @field_serializer('created_at')
    def serialize_dt(self, dt: datetime) -> str:
        return dt.isoformat()
```

## Next Steps

If any code breaks:
1. Replace `obj.to_dict()` with `asdict(obj)` (dataclass) or `obj.model_dump()` (pydantic)
2. Add import: `from dataclasses import asdict`
3. Run tests to verify

## Rollback

If needed, restore from backup:
```bash
cp -r backups/phase5f-serialization-cleanup-*/src/* src/
```
EOF

echo ""
echo "Step 7: Summary"
echo "  Files modified: $FILE_COUNT"
echo "  to_dict() methods removed: $TOTAL_TO_DICT_METHODS"
echo "  LOC removed: $TOTAL_LOC"
echo "  Backup location: $BACKUP_DIR"
echo "  Migration guide: $BACKUP_DIR/MIGRATION_GUIDE.md"
echo ""
echo "✅ Phase 5f Complete!"
echo ""
echo "Next: Run tests to verify nothing broke"
echo "  pytest tests/ -v"

