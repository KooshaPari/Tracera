#!/usr/bin/env python3
"""Find functions missing return type hints."""

import ast
import subprocess
from pathlib import Path
from typing import List, Tuple


class FunctionVisitor(ast.NodeVisitor):
    """Visitor to find functions without return type hints."""

    def __init__(self):
        self.functions = []
        self.current_class = None

    def visit_ClassDef(self, node):
        """Track current class context."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        """Check if function has return type hint."""
        if node.returns is None:
            # Skip dunder methods and private methods for now
            if not node.name.startswith('_'):
                context = f"{self.current_class}." if self.current_class else ""
                self.functions.append((node.lineno, f"{context}{node.name}"))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Check async functions too."""
        self.visit_FunctionDef(node)


def analyze_file(file_path: Path) -> List[Tuple[int, str]]:
    """Analyze a file for missing return types."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content, filename=str(file_path))
        visitor = FunctionVisitor()
        visitor.visit(tree)
        return visitor.functions
    except Exception as e:
        return []


def main():
    """Find all functions without return types."""
    # Get all Python files in src/
    result = subprocess.run(
        ["find", "src/", "-name", "*.py", "-not", "-name", "*_pb2.py"],
        capture_output=True,
        text=True,
    )

    files = [f for f in result.stdout.strip().split('\n') if f and not f.endswith('.pyi')]

    total_missing = 0
    files_with_missing = 0
    results = []

    for file_path_str in files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            continue

        missing = analyze_file(file_path)
        if missing:
            files_with_missing += 1
            total_missing += len(missing)
            results.append((file_path, missing))

    # Print summary
    print(f"Files with missing return types: {files_with_missing}")
    print(f"Total functions missing return types: {total_missing}")
    print()

    # Show top 20 files with most missing
    results.sort(key=lambda x: len(x[1]), reverse=True)
    print("Top 20 files with most missing return types:")
    for file_path, missing in results[:20]:
        print(f"  {file_path}: {len(missing)} functions")


if __name__ == "__main__":
    main()
