#!/usr/bin/env python3
"""Fix missing imports by analyzing ruff errors and adding necessary imports."""

import re
import subprocess
from collections import defaultdict
from pathlib import Path

# Common typing imports
TYPING_IMPORTS = {
    "Optional", "Type", "Dict", "List", "Set", "Tuple", "Union", 
    "Any", "Callable", "Iterable", "Iterator", "Sequence", "Mapping",
    "TypeVar", "Generic", "Protocol", "Literal", "Final", "ClassVar",
    "Awaitable", "Coroutine", "AsyncIterator", "AsyncIterable"
}

# Common collections.abc imports
COLLECTIONS_ABC_IMPORTS = {
    "Mapping", "MutableMapping", "Sequence", "MutableSequence",
    "Set", "MutableSet", "Iterable", "Iterator", "Callable"
}

def get_undefined_names():
    """Get all undefined names from ruff."""
    import json

    result = subprocess.run(
        ["ruff", "check", "src/pheno", "--select", "F821", "--output-format", "json"],
        capture_output=True,
        text=True
    )

    # Parse JSON output to get file -> undefined names mapping
    file_undefined = defaultdict(set)

    try:
        errors = json.loads(result.stdout)
        for error in errors:
            filepath = error['filename']
            # Convert absolute path to relative
            if '/src/pheno/' in filepath:
                filepath = 'src/pheno/' + filepath.split('/src/pheno/')[1]

            # Extract undefined name from message
            message = error['message']
            match = re.search(r'Undefined name `([^`]+)`', message)
            if match:
                undefined_name = match.group(1)
                file_undefined[filepath].add(undefined_name)
    except json.JSONDecodeError:
        print("  ⚠ Failed to parse ruff output")

    return file_undefined

def add_imports_to_file(filepath: str, undefined_names: set):
    """Add missing imports to a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"  ⚠ File not found: {filepath}")
        return False
    
    content = path.read_text()
    lines = content.split('\n')
    
    # Determine which imports to add
    typing_to_add = undefined_names & TYPING_IMPORTS
    
    if not typing_to_add:
        return False
    
    # Find where to insert imports
    import_line = -1
    typing_import_line = -1
    last_import_line = -1
    
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            last_import_line = i
            if line.startswith('from typing import'):
                typing_import_line = i
            elif line.startswith('import typing'):
                import_line = i
    
    # Add typing imports
    if typing_to_add:
        if typing_import_line >= 0:
            # Extend existing typing import
            existing_line = lines[typing_import_line]
            
            # Parse existing imports
            match = re.search(r'from typing import (.+)', existing_line)
            if match:
                existing_imports = {imp.strip() for imp in match.group(1).split(',')}
                all_imports = existing_imports | typing_to_add
                
                # Create new import line
                sorted_imports = sorted(all_imports)
                if len(sorted_imports) <= 5:
                    new_line = f"from typing import {', '.join(sorted_imports)}"
                else:
                    # Multi-line import
                    new_line = "from typing import (\n"
                    new_line += ",\n".join(f"    {imp}" for imp in sorted_imports)
                    new_line += "\n)"
                
                lines[typing_import_line] = new_line
        else:
            # Add new typing import
            sorted_imports = sorted(typing_to_add)
            if len(sorted_imports) <= 5:
                new_line = f"from typing import {', '.join(sorted_imports)}"
            else:
                # Multi-line import
                new_line = "from typing import (\n"
                new_line += ",\n".join(f"    {imp}" for imp in sorted_imports)
                new_line += "\n)"
            
            # Insert after last import or at the beginning
            insert_pos = last_import_line + 1 if last_import_line >= 0 else 0
            lines.insert(insert_pos, new_line)
    
    # Write back
    path.write_text('\n'.join(lines))
    return True

def main():
    """Fix missing imports."""
    print("🔧 Fixing missing imports...")
    print("")
    
    file_undefined = get_undefined_names()
    
    if not file_undefined:
        print("✓ No undefined names found!")
        return 0
    
    print(f"Found {len(file_undefined)} files with undefined names")
    print("")
    
    fixed_count = 0
    
    for filepath, undefined_names in sorted(file_undefined.items()):
        if add_imports_to_file(filepath, undefined_names):
            print(f"  ✓ Fixed: {filepath} (added {len(undefined_names & TYPING_IMPORTS)} imports)")
            fixed_count += 1
        else:
            print(f"  ⚠ Skipped: {filepath} (no typing imports needed)")
    
    print("")
    print(f"✨ Fixed {fixed_count} files")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

