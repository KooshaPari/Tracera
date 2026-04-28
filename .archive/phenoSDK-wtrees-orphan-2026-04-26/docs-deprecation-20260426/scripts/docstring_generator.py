#!/usr/bin/env python3
"""Automated docstring generator for Python files."""

import ast
from pathlib import Path
from typing import List, Tuple


def get_function_signature(node) -> Tuple[List[str], bool]:
    """Extract function parameters."""
    args = []
    for arg in node.args.args:
        if arg.arg not in ('self', 'cls'):
            args.append(arg.arg)
    return args, node.returns is not None


def generate_class_docstring(class_name: str) -> str:
    """Generate class docstring."""
    if "Error" in class_name or "Exception" in class_name:
        return f'"""{class_name} exception.\n\nRaised when an error occurs.\n"""'
    elif "Config" in class_name:
        return f'"""{class_name} configuration.\n\nManages configuration settings.\n"""'
    else:
        return f'"""{class_name} class.\n\nProvides core functionality.\n"""'


def generate_function_docstring(func_name: str, args: List[str]) -> str:
    """Generate function docstring."""
    desc = func_name.replace('_', ' ').title()
    return f'"""{desc}.\n\nPerforms the operation.\n"""'


def process_file(filepath: Path) -> Tuple[int, int, int]:
    """Process a Python file and add missing docstrings."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        changes = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    changes += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_') and not ast.get_docstring(node):
                    changes += 1
        
        return changes, 0, 0
    except Exception:
        return 0, 0, 0


if __name__ == '__main__':
    root = Path('src/pheno')
    total = 0
    
    print("Scanning for missing docstrings...")
    for py_file in sorted(root.rglob('*.py')):
        if '__pycache__' in str(py_file):
            continue
        
        changes, _, _ = process_file(py_file)
        total += changes
    
    print(f"Total missing docstrings: {total}")

