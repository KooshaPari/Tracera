#!/usr/bin/env python3
"""Phase 5 - Category 10: Final Consolidation
Find and remove duplicate/redundant code across the codebase.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def find_duplicate_files():
    """Find duplicate and redundant files."""
    
    src_dir = Path("src/pheno")
    
    # Files to delete (duplicates, old versions, unused)
    files_to_delete = []
    
    # Find *_old.py files
    for filepath in src_dir.rglob("*_old.py"):
        files_to_delete.append(filepath)
    
    # Find *_backup.py files
    for filepath in src_dir.rglob("*_backup.py"):
        files_to_delete.append(filepath)
    
    # Find *_deprecated.py files
    for filepath in src_dir.rglob("*_deprecated.py"):
        files_to_delete.append(filepath)
    
    # Find *_legacy.py files
    for filepath in src_dir.rglob("*_legacy.py"):
        files_to_delete.append(filepath)
    
    # Find duplicate integration files
    integration_files = [
        "src/pheno/dev/pytest_integration.py",
        "src/pheno/dev/mypy_integration.py",
        "src/pheno/dev/bandit_integration.py",
        "src/pheno/dev/black_integration.py",
        "src/pheno/dev/isort_integration.py",
    ]
    
    for file in integration_files:
        filepath = Path(file)
        if filepath.exists():
            files_to_delete.append(filepath)
    
    return files_to_delete

def main():
    """Execute final consolidation."""
    
    print("🔧 Phase 5 - Category 10: Final Consolidation")
    print("=" * 60)
    print()
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = Path(f"backups/cleanup-phase5-final-{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"📦 Backup created at {backup_dir}")
    print()
    
    # Count LOC before
    before_loc = 0
    for filepath in Path("src/pheno").rglob("*.py"):
        try:
            with open(filepath, 'r') as f:
                before_loc += len(f.readlines())
        except:
            pass
    
    print(f"📊 Before: {before_loc:,} LOC")
    print()
    
    # Find files to delete
    files_to_delete = find_duplicate_files()
    
    print(f"🗑️  Deleting {len(files_to_delete)} redundant files...")
    print()
    
    deleted_loc = 0
    deleted_count = 0
    
    for filepath in files_to_delete:
        if filepath.exists():
            # Count LOC
            try:
                with open(filepath, 'r') as f:
                    loc = len(f.readlines())
                deleted_loc += loc
                
                # Backup
                backup_path = backup_dir / filepath.relative_to("src/pheno")
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(filepath, backup_path)
                
                # Delete
                filepath.unlink()
                deleted_count += 1
                print(f"  ✓ Deleted: {filepath} ({loc} LOC)")
            except Exception as e:
                print(f"  ⚠ Error deleting {filepath}: {e}")
    
    print()
    print(f"✓ Deleted {deleted_loc:,} LOC from {deleted_count} files")
    print()
    
    # Count LOC after
    after_loc = 0
    for filepath in Path("src/pheno").rglob("*.py"):
        try:
            with open(filepath, 'r') as f:
                after_loc += len(f.readlines())
        except:
            pass
    
    print(f"📊 After: {after_loc:,} LOC")
    print()
    
    savings = before_loc - after_loc
    
    print("✨ Category 10 Complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  Deleted: {deleted_loc:,} LOC from {deleted_count} files")
    print(f"  Before: {before_loc:,} LOC")
    print(f"  After: {after_loc:,} LOC")
    print(f"  Savings: {savings:,} LOC")
    print()
    print(f"Backup location: {backup_dir}")
    print()

if __name__ == "__main__":
    main()

