#!/usr/bin/env python3
"""
Automated refactoring script for large files.

This script helps split large files (≥500 LOC) into smaller modules (≤350 LOC).
"""

import re
import sys
from pathlib import Path


def count_lines(file_path: Path) -> int:
    """Count non-empty lines in a file."""
    try:
        with open(file_path) as f:
            return sum(1 for line in f if line.strip())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0


def find_large_files(root_dir: Path, min_lines: int = 500) -> list[tuple[Path, int]]:
    """Find all Python files with >= min_lines."""
    large_files = []

    for py_file in root_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        line_count = count_lines(py_file)
        if line_count >= min_lines:
            large_files.append((py_file, line_count))

    return sorted(large_files, key=lambda x: x[1], reverse=True)


def analyze_init_file(file_path: Path) -> dict:
    """Analyze an __init__.py file to understand its structure."""
    with open(file_path) as f:
        content = f.read()

    # Find section comments
    sections = re.findall(r"^# (.+)$", content, re.MULTILINE)

    # Count imports
    import_lines = len(re.findall(r"^(?:from|import) ", content, re.MULTILINE))

    # Count class/function definitions
    definitions = len(re.findall(r"^(?:class|def) ", content, re.MULTILINE))

    return {
        "sections": sections,
        "import_lines": import_lines,
        "definitions": definitions,
        "is_import_only": definitions == 0,
    }


def split_init_by_sections(file_path: Path) -> list[tuple[str, str]]:
    """Split an __init__.py file by section comments."""
    with open(file_path) as f:
        lines = f.readlines()

    sections = []
    current_section = None
    current_lines = []

    for line in lines:
        # Check if this is a section header
        if line.startswith("# ") and not line.startswith("# Backward"):
            if current_section:
                sections.append((current_section, "".join(current_lines)))
            current_section = line.strip("# \n")
            current_lines = []
        else:
            current_lines.append(line)

    # Add last section
    if current_section:
        sections.append((current_section, "".join(current_lines)))

    return sections


def create_import_module(section_name: str, content: str, output_dir: Path) -> Path:
    """Create a separate import module for a section."""
    # Create safe filename from section name
    filename = section_name.lower().replace(" ", "_").replace("-", "_")
    filename = re.sub(r"[^a-z0-9_]", "", filename)
    filename = f"_imports_{filename}.py"

    output_path = output_dir / filename

    # Extract imports and create __all__
    imports = []
    all_exports = []

    for line in content.split("\n"):
        if line.strip().startswith(("from", "import")):
            imports.append(line)
            # Extract exported names
            if "import (" in line:
                # Multi-line import
                pass
            elif " import " in line:
                parts = line.split(" import ")
                if len(parts) == 2:
                    names = parts[1].split(",")
                    for name in names:
                        name = name.strip().split(" as ")[0].strip()
                        if name and not name.startswith("("):
                            all_exports.append(name)

    # Create module content
    module_content = f'"""Imports for {section_name}."""\n\n'
    module_content += "\n".join(imports)

    if all_exports:
        module_content += "\n\n__all__ = [\n"
        for export in sorted(set(all_exports)):
            module_content += f'    "{export}",\n'
        module_content += "]\n"

    with open(output_path, "w") as f:
        f.write(module_content)

    return output_path


def refactor_init_file(file_path: Path, dry_run: bool = True) -> None:
    """Refactor a large __init__.py file."""
    print(f"\n{'=' * 60}")
    print(f"Refactoring: {file_path}")
    print(f"{'=' * 60}")

    # Analyze file
    analysis = analyze_init_file(file_path)
    print(f"Sections found: {len(analysis['sections'])}")
    print(f"Import lines: {analysis['import_lines']}")
    print(f"Definitions: {analysis['definitions']}")
    print(f"Import-only file: {analysis['is_import_only']}")

    if not analysis["is_import_only"]:
        print("⚠️  File contains definitions - manual refactoring recommended")
        return

    # Split by sections
    sections = split_init_by_sections(file_path)
    print(f"\nFound {len(sections)} sections:")
    for section_name, content in sections:
        line_count = len([l for l in content.split("\n") if l.strip()])
        print(f"  - {section_name}: {line_count} lines")

    if dry_run:
        print("\n[DRY RUN] Would create the following files:")
        for section_name, _ in sections:
            filename = section_name.lower().replace(" ", "_").replace("-", "_")
            filename = re.sub(r"[^a-z0-9_]", "", filename)
            print(f"  - _imports_{filename}.py")
        return

    # Create import modules
    output_dir = file_path.parent
    created_files = []

    for section_name, content in sections:
        if content.strip():
            output_path = create_import_module(section_name, content, output_dir)
            created_files.append(output_path)
            print(f"✓ Created: {output_path.name}")

    # Create new __init__.py
    new_init_content = '"""Pheno Core - Foundation modules for the Pheno SDK.\n\n'
    new_init_content += "This package contains core utilities, registries, and foundational components.\n"
    new_init_content += '"""\n\n'

    # Import from sub-modules
    for created_file in created_files:
        module_name = created_file.stem
        new_init_content += f"from .{module_name} import *\n"

    # Backup original
    backup_path = file_path.with_suffix(".py.bak")
    file_path.rename(backup_path)
    print(f"✓ Backed up original to: {backup_path.name}")

    # Write new __init__.py
    with open(file_path, "w") as f:
        f.write(new_init_content)
    print(
        f"✓ Created new {file_path.name} ({len(new_init_content.split(chr(10)))} lines)",
    )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Refactor large Python files")
    parser.add_argument(
        "--root", type=Path, default=Path("src/pheno"), help="Root directory to search",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=500,
        help="Minimum lines to consider a file large",
    )
    parser.add_argument(
        "--list", action="store_true", help="List large files without refactoring",
    )
    parser.add_argument("--file", type=Path, help="Refactor a specific file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Actually perform the refactoring",
    )

    args = parser.parse_args()

    if args.file:
        # Refactor specific file
        if not args.file.exists():
            print(f"Error: File not found: {args.file}")
            return 1

        refactor_init_file(args.file, dry_run=not args.execute)
        return 0

    # Find large files
    print(f"Searching for Python files with ≥{args.min_lines} lines in {args.root}...")
    large_files = find_large_files(args.root, args.min_lines)

    print(f"\nFound {len(large_files)} large files:\n")
    for file_path, line_count in large_files:
        rel_path = file_path.relative_to(args.root)
        print(f"{line_count:5d} LOC  {rel_path}")

    if args.list:
        return 0

    # Refactor __init__.py files
    init_files = [f for f, _ in large_files if f.name == "__init__.py"]

    if init_files:
        print(f"\n\nFound {len(init_files)} large __init__.py files")
        print("These can be automatically refactored.\n")

        for init_file in init_files:
            refactor_init_file(init_file, dry_run=not args.execute)

    return 0


if __name__ == "__main__":
    sys.exit(main())
