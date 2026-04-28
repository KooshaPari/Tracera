#!/usr/bin/env python3
"""Phase 8 - Deep analysis for more LOC reduction opportunities."""

import ast
import os
from collections import defaultdict
from pathlib import Path

def count_lines(filepath: Path) -> int:
    """Count non-empty, non-comment lines."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
    except:
        return 0

def find_duplicate_code():
    """Find duplicate code patterns."""
    
    src_dir = Path("src/pheno")
    
    # Find files with similar names (likely duplicates)
    file_groups = defaultdict(list)
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        # Group by base name
        base_name = filepath.stem.lower()
        file_groups[base_name].append(filepath)
    
    # Find duplicates
    duplicates = []
    for base_name, files in file_groups.items():
        if len(files) > 1:
            total_loc = sum(count_lines(f) for f in files)
            if total_loc > 100:  # Only significant duplicates
                duplicates.append((base_name, files, total_loc))
    
    return duplicates

def find_large_test_files():
    """Find large test files that could be simplified."""
    
    src_dir = Path("src/pheno")
    large_tests = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        if 'test' in filepath.name.lower() or 'fixture' in filepath.name.lower():
            loc = count_lines(filepath)
            if loc > 300:
                large_tests.append((filepath, loc))
    
    return large_tests

def find_wrapper_files():
    """Find thin wrapper files that could be removed."""
    
    src_dir = Path("src/pheno")
    wrappers = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        # Look for files with "wrapper", "adapter", "proxy" in name
        if any(word in filepath.name.lower() for word in ['wrapper', 'adapter', 'proxy', 'client']):
            loc = count_lines(filepath)
            if 100 < loc < 500:  # Thin wrappers
                wrappers.append((filepath, loc))
    
    return wrappers

def find_config_files():
    """Find config files that could be consolidated."""
    
    src_dir = Path("src/pheno")
    configs = []
    
    for filepath in src_dir.rglob("*config*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        loc = count_lines(filepath)
        if loc > 200:
            configs.append((filepath, loc))
    
    return configs

def find_manager_files():
    """Find manager files that could be simplified."""
    
    src_dir = Path("src/pheno")
    managers = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        if 'manager' in filepath.name.lower() or 'coordinator' in filepath.name.lower():
            loc = count_lines(filepath)
            if loc > 300:
                managers.append((filepath, loc))
    
    return managers

def main():
    """Main analysis."""
    
    print("=" * 70)
    print("PHASE 8: DEEP LOC REDUCTION ANALYSIS")
    print("=" * 70)
    print()
    
    # 1. Duplicate code
    print("🔍 1. DUPLICATE CODE PATTERNS")
    print("-" * 70)
    duplicates = find_duplicate_code()
    
    if duplicates:
        total_dup_loc = 0
        for base_name, files, total_loc in sorted(duplicates, key=lambda x: x[2], reverse=True)[:15]:
            print(f"\n  {base_name} ({len(files)} files, {total_loc} LOC total):")
            for f in files:
                loc = count_lines(f)
                rel_path = f.relative_to(Path("src/pheno"))
                print(f"    - {rel_path}: {loc} LOC")
            
            # Estimate savings (keep 1, remove others)
            savings = sum(count_lines(f) for f in files[1:])
            total_dup_loc += savings
            print(f"    Potential savings: ~{savings} LOC")
        
        print(f"\n  Total duplicate code savings: ~{total_dup_loc} LOC")
    
    # 2. Large test files
    print("\n" + "=" * 70)
    print("🔍 2. LARGE TEST/FIXTURE FILES")
    print("-" * 70)
    large_tests = find_large_test_files()
    
    if large_tests:
        total_test_loc = 0
        for filepath, loc in sorted(large_tests, key=lambda x: x[1], reverse=True)[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {loc} LOC")
            total_test_loc += loc
        
        # Estimate 30% reduction
        savings = int(total_test_loc * 0.3)
        print(f"\n  Total test LOC: {total_test_loc}")
        print(f"  Potential savings (30% reduction): ~{savings} LOC")
    
    # 3. Wrapper files
    print("\n" + "=" * 70)
    print("🔍 3. THIN WRAPPER FILES")
    print("-" * 70)
    wrappers = find_wrapper_files()
    
    if wrappers:
        total_wrapper_loc = 0
        for filepath, loc in sorted(wrappers, key=lambda x: x[1], reverse=True)[:15]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {loc} LOC")
            total_wrapper_loc += loc
        
        # Estimate 70% can be removed
        savings = int(total_wrapper_loc * 0.7)
        print(f"\n  Total wrapper LOC: {total_wrapper_loc}")
        print(f"  Potential savings (70% removal): ~{savings} LOC")
    
    # 4. Config files
    print("\n" + "=" * 70)
    print("🔍 4. LARGE CONFIG FILES")
    print("-" * 70)
    configs = find_config_files()
    
    if configs:
        total_config_loc = 0
        for filepath, loc in sorted(configs, key=lambda x: x[1], reverse=True)[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {loc} LOC")
            total_config_loc += loc
        
        # Estimate 40% reduction
        savings = int(total_config_loc * 0.4)
        print(f"\n  Total config LOC: {total_config_loc}")
        print(f"  Potential savings (40% reduction): ~{savings} LOC")
    
    # 5. Manager files
    print("\n" + "=" * 70)
    print("🔍 5. LARGE MANAGER/COORDINATOR FILES")
    print("-" * 70)
    managers = find_manager_files()
    
    if managers:
        total_manager_loc = 0
        for filepath, loc in sorted(managers, key=lambda x: x[1], reverse=True)[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {loc} LOC")
            total_manager_loc += loc
        
        # Estimate 30% reduction
        savings = int(total_manager_loc * 0.3)
        print(f"\n  Total manager LOC: {total_manager_loc}")
        print(f"  Potential savings (30% reduction): ~{savings} LOC")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - POTENTIAL LOC SAVINGS")
    print("=" * 70)
    
    dup_savings = sum(sum(count_lines(f) for f in files[1:]) for _, files, _ in duplicates)
    test_savings = int(sum(loc for _, loc in large_tests) * 0.3) if large_tests else 0
    wrapper_savings = int(sum(loc for _, loc in wrappers) * 0.7) if wrappers else 0
    config_savings = int(sum(loc for _, loc in configs) * 0.4) if configs else 0
    manager_savings = int(sum(loc for _, loc in managers) * 0.3) if managers else 0
    
    print(f"\n  1. Duplicate code:        ~{dup_savings:,} LOC")
    print(f"  2. Large test files:      ~{test_savings:,} LOC")
    print(f"  3. Thin wrappers:         ~{wrapper_savings:,} LOC")
    print(f"  4. Config files:          ~{config_savings:,} LOC")
    print(f"  5. Manager files:         ~{manager_savings:,} LOC")
    print()
    
    total_potential = dup_savings + test_savings + wrapper_savings + config_savings + manager_savings
    print(f"  TOTAL POTENTIAL: ~{total_potential:,} LOC")
    print()
    
    current_loc = 208715
    target_loc = current_loc - total_potential
    print(f"  Current LOC: {current_loc:,}")
    print(f"  Target LOC:  {target_loc:,}")
    print(f"  Reduction:   {(total_potential/current_loc)*100:.1f}%")
    print()

if __name__ == "__main__":
    main()

