#!/usr/bin/env python3
"""Phase 7 - Analyze dead code and unused files."""

import ast
import os
from collections import defaultdict
from pathlib import Path

def find_imports(filepath: Path) -> set[str]:
    """Find all imports in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return imports
    except Exception:
        return set()

def find_unused_files():
    """Find potentially unused files."""
    
    src_dir = Path("src/pheno")
    
    # Build import graph
    all_files = list(src_dir.rglob("*.py"))
    import_graph = defaultdict(set)
    
    print("🔍 Analyzing import graph...")
    for filepath in all_files:
        if '__pycache__' in str(filepath):
            continue
        
        imports = find_imports(filepath)
        for imp in imports:
            import_graph[filepath].add(imp)
    
    # Find files that are never imported
    print("\n📊 Finding unused files...")
    
    all_modules = set()
    for filepath in all_files:
        if '__pycache__' in str(filepath):
            continue
        rel_path = filepath.relative_to(src_dir)
        module = str(rel_path).replace('/', '.').replace('.py', '')
        all_modules.add(module)
    
    # Files that look unused (heuristic)
    potentially_unused = []
    
    for filepath in all_files:
        if '__pycache__' in str(filepath):
            continue
        
        # Skip __init__.py
        if filepath.name == '__init__.py':
            continue
        
        # Skip main entry points
        if filepath.name in ['__main__.py', 'cli.py', 'main.py']:
            continue
        
        # Check if file has "test" in name
        if 'test' in filepath.name.lower():
            continue
        
        # Check file size
        try:
            with open(filepath, 'r') as f:
                lines = len(f.readlines())
            
            # Large files that might be unused
            if lines > 500:
                # Check if it's imported anywhere
                module_name = filepath.stem
                imported = False
                
                for other_file in all_files:
                    if other_file == filepath:
                        continue
                    
                    try:
                        with open(other_file, 'r') as f:
                            content = f.read()
                            if f'import {module_name}' in content or f'from .{module_name}' in content:
                                imported = True
                                break
                    except:
                        pass
                
                if not imported:
                    potentially_unused.append((filepath, lines))
        
        except Exception:
            pass
    
    return potentially_unused

def find_empty_or_minimal_files():
    """Find empty or minimal files."""
    
    src_dir = Path("src/pheno")
    minimal_files = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r') as f:
                lines = [l.strip() for l in f.readlines() if l.strip() and not l.strip().startswith('#')]
            
            # Empty or just imports
            if len(lines) < 5:
                minimal_files.append((filepath, len(lines)))
        
        except Exception:
            pass
    
    return minimal_files

def main():
    """Main analysis."""
    
    print("=" * 60)
    print("PHASE 7: DEAD CODE ANALYSIS")
    print("=" * 60)
    print()
    
    # Find unused files
    unused = find_unused_files()
    
    if unused:
        print(f"\n🗑️  Potentially Unused Files ({len(unused)} files):")
        print()
        
        total_loc = 0
        for filepath, lines in sorted(unused, key=lambda x: x[1], reverse=True)[:20]:
            total_loc += lines
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {lines} LOC")
        
        print()
        print(f"Total potentially unused: {total_loc} LOC")
    
    # Find minimal files
    print("\n" + "=" * 60)
    minimal = find_empty_or_minimal_files()
    
    if minimal:
        print(f"\n📄 Minimal/Empty Files ({len(minimal)} files):")
        print()
        
        for filepath, lines in sorted(minimal, key=lambda x: x[1])[:30]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {lines} lines")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"Potentially unused files: {len(unused)}")
    print(f"Minimal/empty files: {len(minimal)}")
    print()
    
    if unused:
        total_unused_loc = sum(lines for _, lines in unused)
        print(f"Potential LOC savings: ~{total_unused_loc} LOC")
    
    print()

if __name__ == "__main__":
    main()

