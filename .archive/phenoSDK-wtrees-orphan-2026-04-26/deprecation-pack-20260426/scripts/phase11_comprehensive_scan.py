#!/usr/bin/env python3
"""Phase 11 - Comprehensive scan for all remaining opportunities."""

import ast
import os
from collections import defaultdict
from pathlib import Path
import re

def count_lines(filepath: Path) -> int:
    """Count non-empty, non-comment lines."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
    except:
        return 0

def find_unused_imports():
    """Find files with unused imports."""
    src_dir = Path("src/pheno")
    unused = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Get imports
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
            
            # Check if imports are used
            unused_in_file = []
            for imp in imports:
                # Simple heuristic: check if import name appears in code
                if content.count(imp) == 1:  # Only appears in import line
                    unused_in_file.append(imp)
            
            if unused_in_file:
                unused.append((filepath, unused_in_file))
        
        except:
            pass
    
    return unused

def find_example_files():
    """Find example/demo files that could be moved."""
    src_dir = Path("src/pheno")
    examples = []
    
    patterns = [
        r'example',
        r'demo',
        r'sample',
        r'test_.*\.py$',
    ]
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        filename = filepath.name.lower()
        
        for pattern in patterns:
            if re.search(pattern, filename):
                loc = count_lines(filepath)
                examples.append((filepath, loc))
                break
    
    return examples

def find_large_functions():
    """Find large functions that could be refactored."""
    src_dir = Path("src/pheno")
    large_funcs = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Count lines in function
                    if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                        func_lines = node.end_lineno - node.lineno
                        if func_lines > 100:  # Large function
                            large_funcs.append((filepath, node.name, func_lines))
        
        except:
            pass
    
    return large_funcs

def find_duplicate_code():
    """Find potential duplicate code blocks."""
    src_dir = Path("src/pheno")
    duplicates = []
    
    # Simple heuristic: find files with similar names
    files_by_name = defaultdict(list)
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        name = filepath.stem
        files_by_name[name].append(filepath)
    
    for name, files in files_by_name.items():
        if len(files) > 1:
            total_loc = sum(count_lines(f) for f in files)
            duplicates.append((name, files, total_loc))
    
    return duplicates

def find_missing_docstrings():
    """Find files/functions missing docstrings."""
    src_dir = Path("src/pheno")
    missing = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            missing_count = 0
            
            # Check module docstring
            if not ast.get_docstring(tree):
                missing_count += 1
            
            # Check function docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        missing_count += 1
            
            if missing_count > 5:  # Significant missing docstrings
                missing.append((filepath, missing_count))
        
        except:
            pass
    
    return missing

def find_old_style_code():
    """Find old-style Python code."""
    src_dir = Path("src/pheno")
    old_style = []
    
    patterns = {
        'Old string formatting': r'%[sd]',
        'Old exception syntax': r'except.*,',
        'Print statements': r'print\s+[^(]',
        'Old-style classes': r'class\s+\w+:',
    }
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found = []
            for name, pattern in patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    found.append((name, len(matches)))
            
            if found:
                old_style.append((filepath, found))
        
        except:
            pass
    
    return old_style

def find_integration_gaps():
    """Find integration gaps."""
    src_dir = Path("src/pheno")
    gaps = []
    
    # Check for SST components not in __init__
    sst_components_dir = src_dir / "adapters" / "sst" / "components"
    if sst_components_dir.exists():
        component_files = list(sst_components_dir.glob("*.py"))
        component_files = [f for f in component_files if f.stem not in ['__init__', 'base']]
        
        # Check if exported
        init_file = src_dir / "adapters" / "sst" / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r') as f:
                init_content = f.read()
            
            for comp_file in component_files:
                comp_name = comp_file.stem.title().replace('_', '')
                if comp_name not in init_content:
                    gaps.append(("SST component not exported", comp_file))
    
    return gaps

def main():
    """Main analysis."""
    
    print("=" * 70)
    print("PHASE 11: COMPREHENSIVE SCAN FOR REMAINING OPPORTUNITIES")
    print("=" * 70)
    print()
    
    # 1. Unused imports
    print("🔍 1. UNUSED IMPORTS")
    print("-" * 70)
    unused = find_unused_imports()
    
    if unused:
        print(f"Found {len(unused)} files with potentially unused imports")
        print("\nTop 10:")
        for filepath, imports in unused[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {', '.join(imports[:3])}")
    else:
        print("No unused imports found")
    
    # 2. Example files
    print("\n" + "=" * 70)
    print("🔍 2. EXAMPLE/DEMO FILES IN SRC")
    print("-" * 70)
    examples = find_example_files()
    
    if examples:
        total_example_loc = sum(loc for _, loc in examples)
        print(f"Found {len(examples)} example files ({total_example_loc} LOC)")
        print("\nFiles:")
        for filepath, loc in examples:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {loc} LOC")
        print(f"\nPotential to move: {total_example_loc} LOC")
    else:
        print("No example files found in src")
    
    # 3. Large functions
    print("\n" + "=" * 70)
    print("🔍 3. LARGE FUNCTIONS (>100 lines)")
    print("-" * 70)
    large_funcs = find_large_functions()
    
    if large_funcs:
        print(f"Found {len(large_funcs)} large functions")
        print("\nTop 10:")
        for filepath, func_name, lines in sorted(large_funcs, key=lambda x: x[2], reverse=True)[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}::{func_name}: {lines} lines")
    else:
        print("No large functions found")
    
    # 4. Duplicate code
    print("\n" + "=" * 70)
    print("🔍 4. POTENTIAL DUPLICATE CODE")
    print("-" * 70)
    duplicates = find_duplicate_code()
    
    if duplicates:
        total_dup_loc = sum(loc for _, _, loc in duplicates)
        print(f"Found {len(duplicates)} sets of files with same name ({total_dup_loc} LOC)")
        print("\nTop 10:")
        for name, files, loc in sorted(duplicates, key=lambda x: x[2], reverse=True)[:10]:
            print(f"  {name}: {len(files)} files, {loc} LOC")
            for f in files[:3]:
                rel_path = f.relative_to(Path("src/pheno"))
                print(f"    - {rel_path}")
    else:
        print("No duplicate filenames found")
    
    # 5. Missing docstrings
    print("\n" + "=" * 70)
    print("🔍 5. MISSING DOCSTRINGS")
    print("-" * 70)
    missing = find_missing_docstrings()
    
    if missing:
        print(f"Found {len(missing)} files with significant missing docstrings")
        print("\nTop 10:")
        for filepath, count in sorted(missing, key=lambda x: x[1], reverse=True)[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {count} missing docstrings")
    else:
        print("All files have good docstring coverage")
    
    # 6. Old-style code
    print("\n" + "=" * 70)
    print("🔍 6. OLD-STYLE CODE")
    print("-" * 70)
    old_style = find_old_style_code()
    
    if old_style:
        print(f"Found {len(old_style)} files with old-style code")
        print("\nTop 10:")
        for filepath, found in old_style[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            issues = ', '.join(f"{name} ({count})" for name, count in found)
            print(f"  {rel_path}: {issues}")
    else:
        print("No old-style code found")
    
    # 7. Integration gaps
    print("\n" + "=" * 70)
    print("🔍 7. INTEGRATION GAPS")
    print("-" * 70)
    gaps = find_integration_gaps()
    
    if gaps:
        print(f"Found {len(gaps)} integration gaps")
        for gap_type, item in gaps:
            print(f"  {gap_type}: {item}")
    else:
        print("No integration gaps found")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - REMAINING OPPORTUNITIES")
    print("=" * 70)
    
    example_loc = sum(loc for _, loc in examples) if examples else 0
    dup_loc = sum(loc for _, _, loc in duplicates) if duplicates else 0
    
    print(f"\n  1. Unused imports:        {len(unused):,} files")
    print(f"  2. Example files:         {example_loc:,} LOC")
    print(f"  3. Large functions:       {len(large_funcs):,} functions")
    print(f"  4. Duplicate code:        {dup_loc:,} LOC")
    print(f"  5. Missing docstrings:    {len(missing):,} files")
    print(f"  6. Old-style code:        {len(old_style):,} files")
    print(f"  7. Integration gaps:      {len(gaps):,} gaps")
    print()
    
    total_potential = example_loc
    print(f"  TOTAL CLEANUP POTENTIAL: ~{total_potential:,} LOC")
    print()

if __name__ == "__main__":
    main()

