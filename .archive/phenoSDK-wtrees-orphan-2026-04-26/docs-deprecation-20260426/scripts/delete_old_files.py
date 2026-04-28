#!/usr/bin/env python3
"""
Script to safely delete old/deprecated files for Phase 6a.

This script identifies and removes old files while maintaining backups
and ensuring no active dependencies exist.
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
BACKUP_DIR = PROJECT_ROOT / "backups" / f"phase6a_deletion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
DRY_RUN = True  # Set to False for actual deletion

# Files and directories to delete
OLD_ITEMS = [
    # Core shared old integrations
    "src/pheno/core/shared/fastapi_app_old/",
    "src/pheno/core/shared/auth_modern_old/",
    "src/pheno/core/shared/redis_http_proxy_old/",
    "src/pheno/core/shared/nats_jetstream_old/",
    "src/pheno/core/shared/opentelemetry_tracing_old/",
    "src/pheno/core/shared/supavisor_deployment_old/",
    "src/pheno/core/shared/multi_tenant_isolation_old/",
    "src/pheno/core/shared/rich_console_old/",
    "src/pheno/core/shared/apscheduler_old/",
    
    # Dev integration old files
    "src/pheno/dev/pytest_integration/threshold_checker.py",
    "src/pheno/dev/pytest_cov_integration/threshold.py",
    
    # LLM optimization old files
    "src/pheno/llm/optimization/context_folding/",
    "src/pheno/patterns/crud/scaffold.py",
    "src/pheno/credentials/detect/legacy.py",
    
    # Testing duplicates
    "src/pheno/testing/base/test_runner_new.py",
    "src/pheno/testing/adapters/test_fixtures.py",
    "src/pheno/testing/modes/test_modes.py",
    "src/pheno/mcp/qa/core/test_registry.py",
    "src/pheno/ui/tui/process_monitor/test_process_monitor.py",
]

def check_dependencies(item_path: Path) -> list[str]:
    """Check if item has active dependencies."""
    item_path = PROJECT_ROOT / item_path
    if not item_path.exists():
        return []
    
    dependencies = []
    item_name = item_path.stem if item_path.is_file() else item_path.name
    
    # Search for imports of old modules
    for py_file in PROJECT_ROOT.rglob("*.py"):
        if py_file == item_path:
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if f"import.*{item_name}" in content or f"from.*{item_name}" in content:
                    dependencies.append(str(py_file.relative_to(PROJECT_ROOT)))
        except (OSError, UnicodeDecodeError):
            continue
    
    return dependencies

def calculate_loc(item_path: str) -> int:
    """Calculate lines of code for item."""
    full_path = PROJECT_ROOT / item_path
    if not full_path.exists():
        return 0
    
    if full_path.is_file():
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except (OSError, UnicodeDecodeError):
            return 0
    
    # Directory
    total_loc = 0
    for py_file in full_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                total_loc += len(f.readlines())
        except (OSError, UnicodeDecodeError):
            continue
    
    return total_loc

def create_backup(item_path: str):
    """Create backup of item before deletion."""
    full_path = PROJECT_ROOT / item_path
    if not full_path.exists():
        return
    
    backup_path = BACKUP_DIR / item_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    if full_path.is_file():
        shutil.copy2(full_path, backup_path)
    else:
        shutil.copytree(full_path, backup_path, dirs_exist_ok=True)

def delete_item(item_path: str) -> bool:
    """Delete item safely."""
    full_path = PROJECT_ROOT / item_path
    if not full_path.exists():
        print(f"  ⚠️  Item not found: {item_path}")
        return True
    
    try:
        if full_path.is_file():
            full_path.unlink()
        else:
            shutil.rmtree(full_path)
        return True
    except OSError as e:
        print(f"  ❌ Error deleting {item_path}: {e}")
        return False

def main():
    """Main deletion process."""
    print("🔍 Phase 6a: Old Files Cleanup")
    print("=" * 50)
    
    if DRY_RUN:
        print("🔒 DRY RUN MODE - No files will be deleted")
    else:
        print("🔓 LIVE MODE - Files will be deleted")
        print(f"💾 Backups will be stored in: {BACKUP_DIR}")
    
    print()
    
    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    total_loc = 0
    total_items = len(OLD_ITEMS)
    safe_to_delete = 0
    blocked_items = []
    
    # Analyze each item
    for i, item in enumerate(OLD_ITEMS, 1):
        print(f"[{i:2d}/{total_items}] Analyzing: {item}")
        
        # Calculate LOC
        loc = calculate_loc(item)
        total_loc += loc
        
        # Check dependencies
        dependencies = check_dependencies(item)
        
        if dependencies:
            print(f"  ❌ BLOCKED - Dependencies found:")
            for dep in dependencies[:3]:  # Show first 3
                print(f"    - {dep}")
            if len(dependencies) > 3:
                print(f"    - ... and {len(dependencies) - 3} more")
            blocked_items.append(item)
        else:
            print(f"  ✅ SAFE to delete ({loc} LOC)")
            safe_to_delete += 1
            
            # Create backup and delete
            if not DRY_RUN:
                try:
                    create_backup(item)
                    if delete_item(item):
                        print(f"  🗑️  Deleted successfully")
                    else:
                        print(f"  ⚠️  Deletion failed")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        
        print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"Total items analyzed: {total_items}")
    print(f"Safe to delete: {safe_to_delete}")
    print(f"Blocked by dependencies: {len(blocked_items)}")
    print(f"Total LOC reduction: {total_loc:,}")
    
    if blocked_items:
        print(f"\n📋 BLOCKED ITEMS:")
        for item in blocked_items:
            print(f"  - {item}")
    
    if DRY_RUN:
        print(f"\n🔒 DRY RUN COMPLETE")
        print(f"   Run with DRY_RUN=False to execute deletion")
        print(f"   Backup directory: {BACKUP_DIR}")
    else:
        print(f"\n🗑️  DELETION COMPLETE")
        print(f"   Backup created at: {BACKUP_DIR}")
        print(f"   LOC removed: {total_loc:,}")
    
    return 0 if safe_to_delete == len(blocked_items) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
