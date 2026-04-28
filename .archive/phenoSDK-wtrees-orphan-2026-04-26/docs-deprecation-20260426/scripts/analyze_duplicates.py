#!/usr/bin/env python3
"""Analyze duplicate filenames and provide consolidation recommendations."""

import os
from pathlib import Path
from collections import defaultdict
import subprocess

def find_duplicate_files(src_dir):
    """Find all duplicate filenames."""
    files_by_name = defaultdict(list)
    
    for root, dirs, files in os.walk(src_dir):
        # Skip __pycache__ and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                full_path = os.path.join(root, file)
                files_by_name[file].append(full_path)
    
    # Filter to only duplicates
    duplicates = {name: paths for name, paths in files_by_name.items() if len(paths) > 1}
    return duplicates

def get_file_size(filepath):
    """Get LOC for a file."""
    try:
        result = subprocess.run(['wc', '-l', filepath], capture_output=True, text=True)
        return int(result.stdout.split()[0])
    except:
        return 0

def analyze_duplicates(src_dir):
    """Analyze duplicates and provide recommendations."""
    duplicates = find_duplicate_files(src_dir)
    
    print(f"Found {len(duplicates)} duplicate filenames")
    print("=" * 80)
    
    high_priority = []
    medium_priority = []
    low_priority = []
    
    for name, paths in sorted(duplicates.items()):
        total_loc = sum(get_file_size(p) for p in paths)
        
        # Categorize by priority
        if name in ['models.py', 'config.py', 'utils.py', 'types.py', 'enums.py', 'constants.py']:
            priority = "HIGH"
            high_priority.append((name, paths, total_loc))
        elif name in ['__init__.py', 'base.py', 'core.py']:
            priority = "LOW"  # These are expected
            low_priority.append((name, paths, total_loc))
        else:
            priority = "MEDIUM"
            medium_priority.append((name, paths, total_loc))
        
        if priority != "LOW":
            print(f"\n{priority}: {name} ({len(paths)} copies, {total_loc} total LOC)")
            for path in paths:
                loc = get_file_size(path)
                print(f"  - {path} ({loc} LOC)")
    
    print("\n" + "=" * 80)
    print(f"HIGH PRIORITY: {len(high_priority)} files")
    print(f"MEDIUM PRIORITY: {len(medium_priority)} files")
    print(f"LOW PRIORITY: {len(low_priority)} files")
    
    # Calculate potential savings
    high_loc = sum(total for _, _, total in high_priority)
    medium_loc = sum(total for _, _, total in medium_priority)
    
    print(f"\nPotential LOC reduction:")
    print(f"  HIGH: ~{high_loc // 2} LOC (50% consolidation)")
    print(f"  MEDIUM: ~{medium_loc // 3} LOC (33% consolidation)")
    print(f"  TOTAL: ~{(high_loc // 2) + (medium_loc // 3)} LOC")
    
    return high_priority, medium_priority, low_priority

if __name__ == "__main__":
    src_dir = "src"
    high, medium, low = analyze_duplicates(src_dir)

