#!/usr/bin/env python3
"""Check for duplicate imports in Python files.

Ensures clean import statements and prevents redundancy.
"""

import ast
import sys
from pathlib import Path


class DuplicateImportChecker(ast.NodeVisitor):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.imports: dict[str, list[tuple[str, int]]] = {}  # module -> [(line, alias), ...]
        self.duplicates: list[tuple[str, list[tuple[str, int]]]] = []

    def visit_Import(self, node):
        """
        Handle regular imports.
        """
        for alias in node.names:
            module = alias.name
            if module not in self.imports:
                self.imports[module] = []
            self.imports[module].append((node.lineno, alias.asname))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """
        Handle from imports.
        """
        if node.module:
            module = node.module
            if module not in self.imports:
                self.imports[module] = []

            for alias in node.names:
                full_import = f"{module}.{alias.name}"
                if full_import not in self.imports:
                    self.imports[full_import] = []
                self.imports[full_import].append((node.lineno, alias.asname))

        self.generic_visit(node)

    def find_duplicates(self):
        """
        Find duplicate imports.
        """
        for module, imports in self.imports.items():
            if len(imports) > 1:
                self.duplicates.append((module, imports))

    def validate(self) -> list[tuple[str, list[tuple[str, int]]]]:
        """
        Return list of duplicate imports.
        """
        self.find_duplicates()
        return self.duplicates


def check_file(file_path: Path) -> list[tuple[str, list[tuple[str, int]]]]:
    """
    Check a single Python file for duplicate imports.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except (SyntaxError, UnicodeDecodeError) as e:
        return [(f"Error parsing {file_path}: {e}", [])]

    checker = DuplicateImportChecker(file_path)
    checker.visit(tree)
    return checker.validate()


def main():
    if len(sys.argv) < 2:
        print("No files provided for duplicate import checking")
        return 0

    files = [Path(f) for f in sys.argv[1:]]
    all_duplicates = []

    for file_path in files:
        if not file_path.exists() or not file_path.suffix == ".py":
            continue

        duplicates = check_file(file_path)
        if duplicates:
            all_duplicates.append((file_path, duplicates))

    if not all_duplicates:
        print("✅ No duplicate imports found")
        return 0

    print("❌ Duplicate imports found:")
    for file_path, duplicates in all_duplicates:
        print(f"\n📄 {file_path}:")
        for module, imports in duplicates:
            if any("Error parsing" in str(module) for module in [module]):
                print(f"  ⚠️  {module}")
                continue

            print(f"  🔄 Duplicate import: '{module}' found at lines:")
            for line_num, alias in imports:
                alias_str = f" as {alias}" if alias else ""
                print(f"    - Line {line_num}: import {module}{alias_str}")

    total_duplicates = sum(
        len(dup)
        for _, dup in all_duplicates
        for module, dup_list in dup
        if not any("Error" in str(module) for module in [module])
    )

    if total_duplicates > 0:
        print(f"\n❌ Found {total_duplicates} duplicate import(s)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
