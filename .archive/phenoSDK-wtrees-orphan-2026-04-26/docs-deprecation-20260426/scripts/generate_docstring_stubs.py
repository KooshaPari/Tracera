#!/usr/bin/env python3
"""Generate Google-style docstring stubs for missing docstrings.

This script analyzes Python files and generates stub docstrings following
Google style conventions. It preserves existing docstrings and only adds
stubs for missing ones.

Usage:
    python scripts/generate_docstring_stubs.py src/ --dry-run
    python scripts/generate_docstring_stubs.py src/pheno/domain/ --apply
    python scripts/generate_docstring_stubs.py src/pheno/application/ --apply --verbose
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import List, Tuple


class DocstringStubGenerator(ast.NodeTransformer):
    """Generate docstring stubs for AST nodes."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.changes: List[Tuple[int, str, str]] = []  # (lineno, item_type, item_name)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Add module docstring if missing."""
        if not ast.get_docstring(node):
            module_name = Path(self.file_path).stem
            stub = self._generate_module_stub(module_name)
            self._insert_docstring(node, stub)
            self.changes.append((1, "module", module_name))
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Add class docstring if missing."""
        if not ast.get_docstring(node):
            stub = self._generate_class_stub(node)
            self._insert_docstring(node, stub)
            self.changes.append((node.lineno, "class", node.name))
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Add function docstring if missing."""
        if not ast.get_docstring(node):
            # Skip private functions
            if node.name.startswith('_') and not node.name.startswith('__'):
                return node

            stub = self._generate_function_stub(node)
            self._insert_docstring(node, stub)
            item_type = "method" if self._is_method(node) else "function"
            self.changes.append((node.lineno, item_type, node.name))
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Add async function docstring if missing."""
        if not ast.get_docstring(node):
            if node.name.startswith('_') and not node.name.startswith('__'):
                return node

            stub = self._generate_function_stub(node, is_async=True)
            self._insert_docstring(node, stub)
            item_type = "async method" if self._is_method(node) else "async function"
            self.changes.append((node.lineno, item_type, node.name))
        self.generic_visit(node)
        return node

    def _insert_docstring(self, node, docstring: str) -> None:
        """Insert docstring as first node in body."""
        docstring_node = ast.Expr(value=ast.Constant(value=docstring))
        node.body.insert(0, docstring_node)

    def _is_method(self, node) -> bool:
        """Check if function is a method (has self/cls parameter)."""
        if not node.args.args:
            return False
        first_arg = node.args.args[0].arg
        return first_arg in ('self', 'cls')

    def _generate_module_stub(self, module_name: str) -> str:
        """Generate module docstring stub."""
        return f'"""TODO: Document {module_name} module.\n\nProvide module overview here.\n"""'

    def _generate_class_stub(self, node: ast.ClassDef) -> str:
        """Generate class docstring stub."""
        # Check for dataclass
        is_dataclass = any(
            isinstance(dec, ast.Name) and dec.id == 'dataclass'
            or isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == 'dataclass'
            for dec in node.decorator_list
        )

        # Extract attributes from __init__ if present
        attributes = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                # Get parameters (skip self)
                params = [arg.arg for arg in item.args.args if arg.arg != 'self']
                attributes = params
                break
            elif isinstance(item, ast.AnnAssign) and is_dataclass:
                # Dataclass field
                if isinstance(item.target, ast.Name):
                    attributes.append(item.target.id)

        stub = f'"""TODO: Document {node.name} class.\n\n'
        stub += 'Provide class overview here.\n'

        if attributes:
            stub += '\nAttributes:\n'
            for attr in attributes:
                stub += f'    {attr}: TODO: Document attribute.\n'

        stub += '"""'
        return stub

    def _generate_function_stub(self, node, is_async: bool = False) -> str:
        """Generate function/method docstring stub."""
        # Get parameters (skip self/cls)
        params = [
            arg.arg for arg in node.args.args
            if arg.arg not in ('self', 'cls')
        ]

        # Check for return annotation
        has_return = node.returns is not None

        # Check if it's __init__
        is_init = node.name == '__init__'

        # Generate stub
        prefix = "Async " if is_async else ""
        stub = f'"""TODO: Document {prefix}{node.name}.\n\n'
        stub += 'Provide description here.\n'

        if params:
            stub += '\nArgs:\n'
            for param in params:
                stub += f'    {param}: TODO: Document parameter.\n'

        if has_return and not is_init:
            stub += '\nReturns:\n'
            stub += '    TODO: Document return value.\n'

        stub += '"""'
        return stub


def process_file(file_path: Path, dry_run: bool = True, verbose: bool = False) -> int:
    """Process a single Python file.

    Args:
        file_path: Path to Python file.
        dry_run: If True, only report changes without modifying file.
        verbose: If True, print detailed information.

    Returns:
        Number of docstrings that would be added/were added.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        generator = DocstringStubGenerator(str(file_path))
        new_tree = generator.visit(tree)

        if not generator.changes:
            if verbose:
                print(f"✓ {file_path}: No changes needed")
            return 0

        if dry_run:
            print(f"\n📄 {file_path}:")
            print(f"   Would add {len(generator.changes)} docstrings:")
            for lineno, item_type, name in generator.changes:
                print(f"   - Line {lineno}: {item_type} '{name}'")
        else:
            # Apply changes
            new_content = ast.unparse(new_tree)

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"✅ {file_path}: Added {len(generator.changes)} docstrings")
            if verbose:
                for lineno, item_type, name in generator.changes:
                    print(f"   - Line {lineno}: {item_type} '{name}'")

        return len(generator.changes)

    except SyntaxError as e:
        if verbose:
            print(f"⚠️  {file_path}: Syntax error - {e}")
        return 0
    except Exception as e:
        if verbose:
            print(f"❌ {file_path}: Error - {e}")
        return 0


def main():
    """Run docstring stub generation."""
    parser = argparse.ArgumentParser(
        description="Generate Google-style docstring stubs for missing docstrings"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to Python file or directory"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default: dry-run)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: Path {args.path} does not exist", file=sys.stderr)
        return 1

    dry_run = not args.apply

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print("   Use --apply to write changes\n")
    else:
        print("✏️  APPLY MODE - Files will be modified\n")

    # Collect Python files
    if args.path.is_file():
        py_files = [args.path]
    else:
        py_files = list(args.path.rglob('*.py'))
        # Filter out __pycache__ and .venv
        py_files = [
            f for f in py_files
            if '__pycache__' not in str(f) and '.venv' not in str(f)
        ]

    print(f"Processing {len(py_files)} Python files...\n")

    total_changes = 0
    for py_file in sorted(py_files):
        changes = process_file(py_file, dry_run=dry_run, verbose=args.verbose)
        total_changes += changes

    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed:   {len(py_files)}")
    print(f"Docstrings {'would be added' if dry_run else 'added'}: {total_changes}")

    if dry_run:
        print(f"\nRun with --apply to make changes permanent")

    return 0


if __name__ == '__main__':
    sys.exit(main())
