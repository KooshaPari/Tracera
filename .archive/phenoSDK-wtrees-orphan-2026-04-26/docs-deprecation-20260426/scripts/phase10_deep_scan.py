#!/usr/bin/env python3
"""Phase 10 - Deep scan for remaining opportunities."""

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

def find_todo_fixme():
    """Find TODO/FIXME comments."""
    src_dir = Path("src/pheno")
    todos = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                        todos.append((filepath, i, line.strip()))
        except:
            pass
    
    return todos

def find_deprecated_code():
    """Find deprecated code."""
    src_dir = Path("src/pheno")
    deprecated = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if '@deprecated' in content or 'deprecated' in content.lower():
                    loc = count_lines(filepath)
                    deprecated.append((filepath, loc))
        except:
            pass
    
    return deprecated

def find_incomplete_implementations():
    """Find incomplete implementations."""
    src_dir = Path("src/pheno")
    incomplete = []
    
    patterns = [
        r'raise NotImplementedError',
        r'pass\s*$',
        r'\.\.\..*$',
        r'# TODO',
        r'# FIXME',
    ]
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                matches = 0
                for pattern in patterns:
                    matches += len(re.findall(pattern, content, re.MULTILINE))
                
                if matches > 5:  # Significant incomplete code
                    loc = count_lines(filepath)
                    incomplete.append((filepath, matches, loc))
        except:
            pass
    
    return incomplete

def find_test_files_without_tests():
    """Find test files with no actual tests."""
    src_dir = Path("src/pheno")
    empty_tests = []
    
    for filepath in src_dir.rglob("test_*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Count test functions
                test_count = len(re.findall(r'def test_', content))
                
                if test_count == 0:
                    loc = count_lines(filepath)
                    empty_tests.append((filepath, loc))
        except:
            pass
    
    return empty_tests

def find_duplicate_imports():
    """Find files with duplicate imports."""
    src_dir = Path("src/pheno")
    duplicates = []
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                imports = re.findall(r'^import\s+(\S+)', content, re.MULTILINE)
                from_imports = re.findall(r'^from\s+(\S+)\s+import', content, re.MULTILINE)
                
                all_imports = imports + from_imports
                
                # Check for duplicates
                seen = set()
                dups = []
                for imp in all_imports:
                    if imp in seen:
                        dups.append(imp)
                    seen.add(imp)
                
                if dups:
                    duplicates.append((filepath, dups))
        except:
            pass
    
    return duplicates

def find_migration_opportunities():
    """Find code that needs migration."""
    src_dir = Path("src/pheno")
    migrations = []
    
    # Old patterns to migrate
    old_patterns = {
        'typing.List': 'list',
        'typing.Dict': 'dict',
        'typing.Set': 'set',
        'typing.Tuple': 'tuple',
        'Optional[': '| None',
        'Union[': '|',
    }
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                found_patterns = []
                for old, new in old_patterns.items():
                    if old in content:
                        count = content.count(old)
                        found_patterns.append((old, new, count))
                
                if found_patterns:
                    migrations.append((filepath, found_patterns))
        except:
            pass
    
    return migrations

def find_integration_opportunities():
    """Find integration opportunities."""
    src_dir = Path("src/pheno")
    integrations = []
    
    # Look for standalone implementations that could integrate
    patterns = {
        'Custom HTTP client': r'class.*HTTPClient',
        'Custom logger': r'class.*Logger.*:',
        'Custom cache': r'class.*Cache.*:',
        'Custom queue': r'class.*Queue.*:',
        'Custom database': r'class.*Database.*:',
    }
    
    for filepath in src_dir.rglob("*.py"):
        if '__pycache__' in str(filepath):
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                found = []
                for name, pattern in patterns.items():
                    if re.search(pattern, content):
                        found.append(name)
                
                if found:
                    loc = count_lines(filepath)
                    integrations.append((filepath, found, loc))
        except:
            pass
    
    return integrations

def main():
    """Main analysis."""
    
    print("=" * 70)
    print("PHASE 10: DEEP SCAN FOR REMAINING OPPORTUNITIES")
    print("=" * 70)
    print()
    
    # 1. TODO/FIXME
    print("🔍 1. TODO/FIXME COMMENTS")
    print("-" * 70)
    todos = find_todo_fixme()
    
    if todos:
        print(f"Found {len(todos)} TODO/FIXME comments")
        print("\nTop 20:")
        for filepath, line_num, line in todos[:20]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}:{line_num} - {line[:60]}")
    
    # 2. Deprecated code
    print("\n" + "=" * 70)
    print("🔍 2. DEPRECATED CODE")
    print("-" * 70)
    deprecated = find_deprecated_code()
    
    if deprecated:
        total_deprecated_loc = sum(loc for _, loc in deprecated)
        print(f"Found {len(deprecated)} deprecated files ({total_deprecated_loc} LOC)")
        print("\nTop 10:")
        for filepath, loc in sorted(deprecated, key=lambda x: x[1], reverse=True)[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {loc} LOC")
        print(f"\nPotential savings: {total_deprecated_loc} LOC")
    
    # 3. Incomplete implementations
    print("\n" + "=" * 70)
    print("🔍 3. INCOMPLETE IMPLEMENTATIONS")
    print("-" * 70)
    incomplete = find_incomplete_implementations()
    
    if incomplete:
        total_incomplete_loc = sum(loc for _, _, loc in incomplete)
        print(f"Found {len(incomplete)} incomplete files ({total_incomplete_loc} LOC)")
        print("\nTop 10:")
        for filepath, matches, loc in sorted(incomplete, key=lambda x: x[1], reverse=True)[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {matches} incomplete items, {loc} LOC")
    
    # 4. Empty test files
    print("\n" + "=" * 70)
    print("🔍 4. EMPTY TEST FILES")
    print("-" * 70)
    empty_tests = find_test_files_without_tests()
    
    if empty_tests:
        total_empty_test_loc = sum(loc for _, loc in empty_tests)
        print(f"Found {len(empty_tests)} empty test files ({total_empty_test_loc} LOC)")
        for filepath, loc in empty_tests:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {loc} LOC")
        print(f"\nPotential savings: {total_empty_test_loc} LOC")
    
    # 5. Duplicate imports
    print("\n" + "=" * 70)
    print("🔍 5. DUPLICATE IMPORTS")
    print("-" * 70)
    duplicates = find_duplicate_imports()
    
    if duplicates:
        print(f"Found {len(duplicates)} files with duplicate imports")
        print("\nTop 10:")
        for filepath, dups in duplicates[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {', '.join(dups[:3])}")
    
    # 6. Migration opportunities
    print("\n" + "=" * 70)
    print("🔍 6. MIGRATION OPPORTUNITIES (Python 3.10+ syntax)")
    print("-" * 70)
    migrations = find_migration_opportunities()
    
    if migrations:
        total_migrations = sum(sum(count for _, _, count in patterns) for _, patterns in migrations)
        print(f"Found {len(migrations)} files with old syntax ({total_migrations} occurrences)")
        print("\nTop 10:")
        for filepath, patterns in migrations[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            total = sum(count for _, _, count in patterns)
            print(f"  {rel_path}: {total} old patterns")
    
    # 7. Integration opportunities
    print("\n" + "=" * 70)
    print("🔍 7. INTEGRATION OPPORTUNITIES")
    print("-" * 70)
    integrations = find_integration_opportunities()
    
    if integrations:
        total_integration_loc = sum(loc for _, _, loc in integrations)
        print(f"Found {len(integrations)} integration opportunities ({total_integration_loc} LOC)")
        print("\nTop 10:")
        for filepath, found, loc in sorted(integrations, key=lambda x: x[2], reverse=True)[:10]:
            rel_path = filepath.relative_to(Path("src/pheno"))
            print(f"  {rel_path}: {', '.join(found)} ({loc} LOC)")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - POTENTIAL IMPROVEMENTS")
    print("=" * 70)
    
    deprecated_loc = sum(loc for _, loc in deprecated) if deprecated else 0
    incomplete_loc = sum(loc for _, _, loc in incomplete) if incomplete else 0
    empty_test_loc = sum(loc for _, loc in empty_tests) if empty_tests else 0
    integration_loc = sum(loc for _, _, loc in integrations) if integrations else 0
    
    print(f"\n  1. TODO/FIXME items:          {len(todos):,}")
    print(f"  2. Deprecated code:           {deprecated_loc:,} LOC")
    print(f"  3. Incomplete implementations: {incomplete_loc:,} LOC")
    print(f"  4. Empty test files:          {empty_test_loc:,} LOC")
    print(f"  5. Duplicate imports:         {len(duplicates):,} files")
    print(f"  6. Migration opportunities:   {len(migrations):,} files")
    print(f"  7. Integration opportunities: {integration_loc:,} LOC")
    print()
    
    total_potential = deprecated_loc + empty_test_loc
    print(f"  TOTAL CLEANUP POTENTIAL: ~{total_potential:,} LOC")
    print()

if __name__ == "__main__":
    main()

