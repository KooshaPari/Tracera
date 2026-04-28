#!/usr/bin/env python3
"""Phase 9 - Consolidate duplicate __init__.py files."""

import os
from pathlib import Path
import shutil
from datetime import datetime

def count_lines(filepath: Path) -> int:
    """Count non-empty, non-comment lines."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
    except:
        return 0

def is_simple_init(filepath: Path) -> bool:
    """Check if __init__.py is simple (just imports/exports)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple if it's just imports and __all__
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
        
        # Check if all lines are imports or __all__
        for line in lines:
            if not (line.startswith('from ') or 
                   line.startswith('import ') or 
                   line.startswith('__all__') or
                   line == '' or
                   line.startswith('"') or
                   line.startswith("'")):
                return False
        
        return True
    except:
        return False

def can_simplify_init(filepath: Path) -> tuple[bool, int]:
    """Check if __init__.py can be simplified."""
    loc = count_lines(filepath)
    
    # Skip if already minimal
    if loc < 5:
        return False, 0
    
    # Check if it's just re-exports
    if is_simple_init(filepath):
        # Can be simplified to empty or minimal
        potential_savings = max(0, loc - 2)  # Keep 2 lines for docstring
        return True, potential_savings
    
    return False, 0

def main():
    """Main consolidation."""
    
    print("=" * 70)
    print("PHASE 9: CONSOLIDATE __init__.py FILES")
    print("=" * 70)
    print()
    
    src_dir = Path("src/pheno")
    
    # Find all __init__.py files
    init_files = list(src_dir.rglob("__init__.py"))
    
    print(f"Found {len(init_files)} __init__.py files")
    print()
    
    # Analyze which can be simplified
    can_simplify = []
    total_potential = 0
    
    for filepath in init_files:
        can_simp, savings = can_simplify_init(filepath)
        if can_simp and savings > 0:
            can_simplify.append((filepath, savings))
            total_potential += savings
    
    print(f"Can simplify {len(can_simplify)} files")
    print(f"Potential savings: {total_potential} LOC")
    print()
    
    # Show top candidates
    print("Top 20 candidates for simplification:")
    print()
    
    for filepath, savings in sorted(can_simplify, key=lambda x: x[1], reverse=True)[:20]:
        rel_path = filepath.relative_to(src_dir)
        loc = count_lines(filepath)
        print(f"  {rel_path}: {loc} LOC → {loc - savings} LOC (save {savings})")
    
    print()
    
    # Ask for confirmation
    response = input(f"\nSimplify {len(can_simplify)} __init__.py files? (y/n): ")
    
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = Path(f"backups/cleanup-phase9-inits-{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📦 Backup: {backup_dir}")
    print()
    
    # Simplify files
    simplified_count = 0
    total_saved = 0
    
    for filepath, savings in can_simplify:
        try:
            # Backup
            rel_path = filepath.relative_to(src_dir)
            backup_path = backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filepath, backup_path)
            
            # Simplify to minimal __init__.py
            with open(filepath, 'w', encoding='utf-8') as f:
                # Get module name from directory
                module_name = filepath.parent.name
                f.write(f'"""{module_name.replace("_", " ").title()} module."""\n')
            
            simplified_count += 1
            total_saved += savings
            
            if simplified_count % 10 == 0:
                print(f"  Simplified {simplified_count}/{len(can_simplify)} files...")
        
        except Exception as e:
            print(f"  ⚠ Error simplifying {filepath}: {e}")
    
    print()
    print("✨ Phase 9.1 Complete!")
    print("=" * 70)
    print()
    print(f"  Simplified: {simplified_count} files")
    print(f"  Saved: {total_saved} LOC")
    print(f"  Backup: {backup_dir}")
    print()

if __name__ == "__main__":
    main()

