#!/usr/bin/env python3
"""
Simple Final Cleanup Script.

This script performs a simple final cleanup of the consolidated codebase.
"""

import os
from pathlib import Path


def main():
    """Main cleanup function."""
    print("🚀 Starting simple final cleanup...")

    base_path = Path("src/pheno")
    removed_files = []

    # Remove empty directories
    print("🧹 Removing empty directories...")
    for root, dirs, files in os.walk(base_path, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    removed_files.append(str(dir_path))
                    print(f"  ❌ Removed empty directory: {dir_path}")
            except OSError:
                pass

    # Remove empty init files
    print("🧹 Removing empty __init__.py files...")
    init_files = list(base_path.rglob("__init__.py"))
    for init_file in init_files:
        try:
            content = init_file.read_text().strip()
            if not content or content in ["", '"""', "'''"]:
                parent_dir = init_file.parent
                other_files = [
                    f for f in parent_dir.iterdir() if f.name != "__init__.py"
                ]
                if not other_files:
                    init_file.unlink()
                    removed_files.append(str(init_file))
                    print(f"  ❌ Removed empty __init__.py: {init_file}")
        except Exception:
            pass

    # Remove temp files
    print("🧹 Removing temporary files...")
    temp_files = list(base_path.rglob("*.tmp"))
    for temp_file in temp_files:
        temp_file.unlink()
        removed_files.append(str(temp_file))
        print(f"  ❌ Removed temp file: {temp_file}")

    # Generate report
    print("\n📊 Simple Final Cleanup Report")
    print("=" * 40)
    print(f"Files removed: {len(removed_files)}")

    print("\nRemoved files:")
    for file_path in removed_files:
        print(f"  - {file_path}")

    print("\n✅ Simple final cleanup complete!")


if __name__ == "__main__":
    main()
