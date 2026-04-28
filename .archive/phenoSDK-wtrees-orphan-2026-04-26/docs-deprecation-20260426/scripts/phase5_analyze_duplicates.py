#!/usr/bin/env python3
"""Analyze codebase for duplicate code and consolidation opportunities."""

import ast
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

def count_lines(filepath: Path) -> int:
    """Count non-empty, non-comment lines in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        count = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                count += 1
        return count
    except Exception:
        return 0

def find_duplicate_patterns():
    """Find duplicate code patterns."""
    
    src_dir = Path("src/pheno")
    
    # Category 1: HTTP Clients
    print("=" * 60)
    print("CATEGORY 2: HTTP CLIENTS")
    print("=" * 60)
    
    http_files = [
        "core/shared/http_client.py",
        "testing/adapters/httpx_client.py",
        "dev/http/httpx_client.py",
        "dev/httpx_integration.py",
        "dev/aiohttp_integration.py",
    ]
    
    total_http_loc = 0
    for file in http_files:
        filepath = src_dir / file
        if filepath.exists():
            loc = count_lines(filepath)
            total_http_loc += loc
            print(f"  {file}: {loc} LOC")
    
    print(f"\nTotal HTTP client code: {total_http_loc} LOC")
    print(f"Potential savings: ~{int(total_http_loc * 0.7)} LOC (70% reduction)")
    print()
    
    # Category 2: Validators
    print("=" * 60)
    print("CATEGORY 4: VALIDATORS")
    print("=" * 60)
    
    validator_files = []
    for filepath in src_dir.rglob("*.py"):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'def validate_' in content or 'class.*Validator' in content:
                loc = count_lines(filepath)
                if loc > 50:  # Only significant files
                    rel_path = filepath.relative_to(src_dir)
                    validator_files.append((str(rel_path), loc))
    
    validator_files.sort(key=lambda x: x[1], reverse=True)
    total_validator_loc = 0
    for file, loc in validator_files[:10]:
        total_validator_loc += loc
        print(f"  {file}: {loc} LOC")
    
    print(f"\nTotal validator code (top 10): {total_validator_loc} LOC")
    print(f"Potential savings: ~{int(total_validator_loc * 0.6)} LOC (60% reduction)")
    print()
    
    # Category 3: Logging wrappers
    print("=" * 60)
    print("CATEGORY 5: LOGGING")
    print("=" * 60)
    
    logging_files = []
    for filepath in src_dir.rglob("*.py"):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'class.*Logger' in content or 'def.*log_' in content:
                loc = count_lines(filepath)
                if loc > 30 and 'logging' in content.lower():
                    rel_path = filepath.relative_to(src_dir)
                    logging_files.append((str(rel_path), loc))
    
    logging_files.sort(key=lambda x: x[1], reverse=True)
    total_logging_loc = 0
    for file, loc in logging_files[:10]:
        total_logging_loc += loc
        print(f"  {file}: {loc} LOC")
    
    print(f"\nTotal logging code (top 10): {total_logging_loc} LOC")
    print(f"Potential savings: ~{int(total_logging_loc * 0.5)} LOC (50% reduction)")
    print()
    
    # Category 4: Config loaders
    print("=" * 60)
    print("CATEGORY 7: CONFIG MANAGEMENT")
    print("=" * 60)
    
    config_files = []
    for filepath in src_dir.rglob("*config*.py"):
        if '__pycache__' not in str(filepath):
            loc = count_lines(filepath)
            if loc > 100:
                rel_path = filepath.relative_to(src_dir)
                config_files.append((str(rel_path), loc))
    
    config_files.sort(key=lambda x: x[1], reverse=True)
    total_config_loc = 0
    for file, loc in config_files[:10]:
        total_config_loc += loc
        print(f"  {file}: {loc} LOC")
    
    print(f"\nTotal config code (top 10): {total_config_loc} LOC")
    print(f"Potential savings: ~{int(total_config_loc * 0.3)} LOC (30% reduction)")
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"HTTP Clients: ~{int(total_http_loc * 0.7)} LOC")
    print(f"Validators: ~{int(total_validator_loc * 0.6)} LOC")
    print(f"Logging: ~{int(total_logging_loc * 0.5)} LOC")
    print(f"Config: ~{int(total_config_loc * 0.3)} LOC")
    print()
    total_savings = (
        int(total_http_loc * 0.7) +
        int(total_validator_loc * 0.6) +
        int(total_logging_loc * 0.5) +
        int(total_config_loc * 0.3)
    )
    print(f"TOTAL POTENTIAL SAVINGS: ~{total_savings} LOC")
    print()

if __name__ == "__main__":
    find_duplicate_patterns()

