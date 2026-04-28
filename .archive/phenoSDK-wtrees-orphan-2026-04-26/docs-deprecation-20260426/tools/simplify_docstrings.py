#!/usr/bin/env python3
"""Docstring Simplification Tool.

Simplifies verbose docstrings by:
1. Keeping only the summary line
2. Preserving Example sections if they contain actual code
3. Removing redundant Args/Returns that duplicate type hints
4. Removing excessive whitespace

Usage:
    python tools/simplify_docstrings.py src/pheno/
"""

import ast
import re
import sys
from pathlib import Path


class DocstringSimplifier(ast.NodeTransformer):
    """
    Simplifies docstrings in Python AST.
    """

    def __init__(self):
        self.changes = 0

    def simplify_docstring(self, docstring: str) -> str | None:
        """
        Simplify a docstring to just the summary line.
        """
        if not docstring:
            return None

        lines = docstring.strip().split("\n")
        if not lines:
            return None

        # Get the summary line (first non-empty line)
        summary = lines[0].strip()

        # Check if there's an Example section with actual code
        has_example = False
        example_lines = []
        in_example = False

        for line in lines:
            if "Example:" in line or "Examples:" in line:
                in_example = True
                continue
            if in_example:
                # Check if line contains code (has >>> or actual code patterns)
                if ">>>" in line or re.search(r"^\s+[a-zA-Z_]", line):
                    has_example = True
                    example_lines.append(line)
                elif line.strip() and not line.strip().startswith("```"):
                    example_lines.append(line)
                elif line.strip().startswith("Args:") or line.strip().startswith("Returns:"):
                    break

        # If summary is very short and there's no example, keep it simple
        if len(summary) < 100 and not has_example:
            return summary

        # If there's a valuable example, keep summary + example
        if has_example and example_lines:
            result = f"{summary}\n\nExample:\n" + "\n".join(example_lines)
            return result

        return summary

    def visit_FunctionDef(self, node):
        """
        Visit function definitions and simplify docstrings.
        """
        if ast.get_docstring(node):
            original = ast.get_docstring(node)
            simplified = self.simplify_docstring(original)

            if simplified and simplified != original:
                # Replace the docstring
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                ):
                    node.body[0].value.value = simplified
                    self.changes += 1

        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        """
        Visit class definitions and simplify docstrings.
        """
        if ast.get_docstring(node):
            original = ast.get_docstring(node)
            simplified = self.simplify_docstring(original)

            if simplified and simplified != original:
                # Replace the docstring
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                ):
                    node.body[0].value.value = simplified
                    self.changes += 1

        self.generic_visit(node)
        return node

    def visit_Module(self, node):
        """
        Visit module and simplify module docstring.
        """
        if ast.get_docstring(node):
            original = ast.get_docstring(node)
            # Keep module docstrings a bit longer as they're important
            lines = original.strip().split("\n")
            summary_lines = []
            for line in lines:
                if (
                    line.strip()
                    and not line.strip().startswith("Args:")
                    and not line.strip().startswith("Returns:")
                ):
                    summary_lines.append(line)
                    if len(summary_lines) >= 3:  # Keep first 3 lines for modules
                        break
                else:
                    break

            simplified = "\n".join(summary_lines).strip()

            if simplified and simplified != original:
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                ):
                    node.body[0].value.value = simplified
                    self.changes += 1

        self.generic_visit(node)
        return node


def simplify_file(file_path: Path, dry_run: bool = False) -> int:
    """
    Simplify docstrings in a Python file.
    """
    try:
        content = file_path.read_text()
        tree = ast.parse(content)

        simplifier = DocstringSimplifier()
        new_tree = simplifier.visit(tree)

        if simplifier.changes > 0:
            if not dry_run:
                # Write back the simplified code
                new_content = ast.unparse(new_tree)
                file_path.write_text(new_content)
            print(f"✓ {file_path}: {simplifier.changes} docstrings simplified")

        return simplifier.changes
    except Exception as e:
        print(f"✗ {file_path}: Error - {e}")
        return 0


def simplify_directory(directory: Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Simplify docstrings in all Python files in a directory.
    """
    total_files = 0
    total_changes = 0

    for py_file in directory.rglob("*.py"):
        # Skip test files and __pycache__
        if "__pycache__" in str(py_file) or "test_" in py_file.name:
            continue

        changes = simplify_file(py_file, dry_run)
        if changes > 0:
            total_files += 1
            total_changes += changes

    return total_files, total_changes


def main():
    """
    Main entry point.
    """
    if len(sys.argv) < 2:
        print("Usage: python tools/simplify_docstrings.py <directory> [--dry-run]")
        sys.exit(1)

    directory = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv

    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        sys.exit(1)

    print(f"Simplifying docstrings in {directory}...")
    if dry_run:
        print("(DRY RUN - no files will be modified)")

    files, changes = simplify_directory(directory, dry_run)

    print(
        f"\n{'Would simplify' if dry_run else 'Simplified'} {changes} docstrings in {files} files",
    )


if __name__ == "__main__":
    main()
