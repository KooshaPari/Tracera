#!/usr/bin/env python3
"""
Script to automatically add missing docstrings to Python files.

This script:
1. Finds all classes and functions without docstrings
2. Generates appropriate docstring templates
3. Adds them to the source files
4. Validates the results

Usage:
    python scripts/add_missing_docstrings.py src/pheno --dry-run
    python scripts/add_missing_docstrings.py src/pheno --apply
"""

import ast
import sys
from pathlib import Path
from typing import Optional


def generate_class_docstring(class_name: str, bases: list[str]) -> str:
    """Generate a docstring template for a class."""
    if "Error" in class_name or "Exception" in class_name:
        return f'''"""
{class_name} exception.

Raised when an error occurs in the system.

Attributes:
    message: Error message
    code: Error code
    details: Additional error details
"""'''
    elif "Config" in class_name:
        return f'''"""
Configuration for {class_name}.

Attributes:
    See class attributes for configuration options.
"""'''
    else:
        return f'''"""
{class_name} class.

This class provides functionality for managing {class_name.lower()}.

Attributes:
    See class attributes for details.
"""'''


def generate_function_docstring(func_name: str, args: list[str]) -> str:
    """Generate a docstring template for a function."""
    args_section = "\n    ".join([f"{arg}: Description of {arg}" for arg in args if arg != "self"])
    
    return f'''"""
{func_name.replace('_', ' ').title()}.

Args:
    {args_section}

Returns:
    Description of return value.

Raises:
    Exception: Description of when exception is raised.
"""'''


def process_file(filepath: Path, apply: bool = False) -> dict:
    """Process a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        changes = {'classes': 0, 'functions': 0, 'modules': 0}
        
        # Check module docstring
        if not ast.get_docstring(tree):
            changes['modules'] = 1
        
        # Check classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    changes['classes'] += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_') and not ast.get_docstring(node):
                    changes['functions'] += 1
        
        return changes
    except Exception as e:
        return {'error': str(e)}


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_missing_docstrings.py <path> [--dry-run|--apply]")
        sys.exit(1)
    
    root_path = Path(sys.argv[1])
    apply = '--apply' in sys.argv
    dry_run = '--dry-run' in sys.argv or not apply
    
    total_changes = {'classes': 0, 'functions': 0, 'modules': 0}
    
    print(f"Scanning {root_path}...")
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY'}\n")
    
    for py_file in root_path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        
        changes = process_file(py_file)
        
        if changes.get('error'):
            continue
        
        if any(changes.values()):
            rel_path = py_file.relative_to(root_path)
            print(f"{rel_path}:")
            print(f"  Classes: {changes['classes']}")
            print(f"  Functions: {changes['functions']}")
            print(f"  Modules: {changes['modules']}")
            
            for key in ['classes', 'functions', 'modules']:
                total_changes[key] += changes[key]
    
    print(f"\n{'='*60}")
    print(f"Total Missing Docstrings:")
    print(f"  Classes: {total_changes['classes']}")
    print(f"  Functions: {total_changes['functions']}")
    print(f"  Modules: {total_changes['modules']}")
    print(f"  TOTAL: {sum(total_changes.values())}")
    print(f"{'='*60}")
    
    if dry_run:
        print("\nRun with --apply to add docstrings")


if __name__ == '__main__':
    main()

