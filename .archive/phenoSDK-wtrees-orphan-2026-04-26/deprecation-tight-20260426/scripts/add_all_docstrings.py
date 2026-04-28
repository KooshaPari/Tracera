#!/usr/bin/env python3
"""Add missing docstrings to all Python files."""

import ast
import re
from pathlib import Path


def add_docstrings(filepath: Path) -> int:
    """Add missing docstrings to a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        tree = ast.parse(''.join(lines))
        added = 0
        
        # Collect all nodes that need docstrings
        nodes_to_add = []
        
        # Check module
        if not ast.get_docstring(tree):
            module_name = filepath.stem
            doc = f'"""{module_name.replace("_", " ").title()} module."""\n\n'
            nodes_to_add.append((0, doc, 'module'))
            added += 1
        
        # Check classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    class_name = node.name
                    if 'Error' in class_name or 'Exception' in class_name:
                        doc = f'    """{class_name} exception."""\n'
                    elif 'Config' in class_name:
                        doc = f'    """{class_name} configuration."""\n'
                    else:
                        doc = f'    """{class_name} class."""\n'
                    nodes_to_add.append((node.lineno, doc, 'class'))
                    added += 1
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_') and not ast.get_docstring(node):
                    func_name = node.name.replace('_', ' ').title()
                    indent = '    ' * (node.col_offset // 4 + 1)
                    doc = f'{indent}"""{func_name}."""\n'
                    nodes_to_add.append((node.lineno, doc, 'function'))
                    added += 1
        
        # Apply changes (in reverse order)
        if nodes_to_add:
            nodes_to_add.sort(reverse=True, key=lambda x: x[0])
            for line_num, doc, node_type in nodes_to_add:
                if node_type == 'module':
                    lines.insert(0, doc)
                else:
                    # Insert after the def line
                    if line_num <= len(lines):
                        lines.insert(line_num, doc)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        
        return added
    
    except Exception as e:
        return 0


def main():
    """Main entry point."""
    root = Path('src/pheno')
    total_added = 0
    files_modified = 0
    
    print('Adding missing docstrings...')
    print('=' * 60)
    
    for py_file in sorted(root.rglob('*.py')):
        if '__pycache__' in str(py_file):
            continue
        
        added = add_docstrings(py_file)
        if added > 0:
            total_added += added
            files_modified += 1
            rel_path = py_file.relative_to(root)
            print(f'{rel_path}: +{added}')
    
    print('=' * 60)
    print(f'Files modified: {files_modified}')
    print(f'Docstrings added: {total_added}')


if __name__ == '__main__':
    main()

