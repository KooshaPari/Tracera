#!/usr/bin/env python3
"""Fix internal imports in the migrated TUI module.

Convert relative imports to absolute imports using the new pheno.ui.tui path.
"""

import argparse
import re
from pathlib import Path


def fix_tui_imports(file_path: Path, dry_run: bool = True) -> bool:
    """
    Fix imports in a single file.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Fix relative imports to use absolute pheno.ui.tui paths
        patterns = [
            # from .submodule import ...
            (r"from\s+\.([a-zA-Z_][a-zA-Z0-9_]*)\s+import", r"from pheno.ui.tui.\1 import"),
            # from ..submodule import ...
            (r"from\s+\.\.([a-zA-Z_][a-zA-Z0-9_]*)\s+import", r"from pheno.ui.\1 import"),
            # from .submodule.subsubmodule import ...
            (
                r"from\s+\.([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)\s+import",
                r"from pheno.ui.tui.\1 import",
            ),
            # import .submodule
            (r"import\s+\.([a-zA-Z_][a-zA-Z0-9_]*)", r"import pheno.ui.tui.\1"),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            if not dry_run:
                file_path.write_text(content, encoding="utf-8")
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Fix TUI internal imports")
    parser.add_argument("path", type=str, help="Path to TUI directory")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()

    tui_path = Path(args.path)
    if not tui_path.exists():
        print(f"Path {tui_path} does not exist")
        return

    changed_files = []
    for py_file in tui_path.rglob("*.py"):
        if fix_tui_imports(py_file, dry_run=not args.apply):
            changed_files.append(py_file)

    if args.apply:
        print(f"✅ Fixed imports in {len(changed_files)} files")
    else:
        print(f"🔎 Would fix imports in {len(changed_files)} files (use --apply to write)")

    if changed_files:
        print("Files that would be/were changed:")
        for f in changed_files[:10]:  # Show first 10
            print(f"  {f}")
        if len(changed_files) > 10:
            print(f"  ... and {len(changed_files) - 10} more")


if __name__ == "__main__":
    main()
