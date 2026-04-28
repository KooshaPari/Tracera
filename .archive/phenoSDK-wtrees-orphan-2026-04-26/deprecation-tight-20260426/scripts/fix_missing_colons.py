#!/usr/bin/env python3
"""Fix missing colons in function definitions with noqa comments."""

import re
import sys
from pathlib import Path

# Files and line numbers that need fixing
FIXES = [
    ("src/pheno/adapters/providers/usage_collectors/infrastructure/loaders/droid_loader.py", 194),
    ("src/pheno/core/shared/cache/config.py", 66),
    ("src/pheno/core/shared/deployment/config.py", 96),
    ("src/pheno/core/shared/messaging/config.py", 101),
    ("src/pheno/core/shared/redis_http_proxy_old/proxy.py", 138),
    ("src/pheno/core/shared/utilities/migration_helper.py", 207),
    ("src/pheno/credentials/hierarchy/models/builder.py", 247),
    ("src/pheno/credentials/hierarchy/models/hierarchy.py", 154),
    ("src/pheno/credentials/hierarchy/models/scope_node.py", 142),
    ("src/pheno/dev/aiocache_integration/config.py", 119),
    ("src/pheno/dev/black/config.py", 63),
    ("src/pheno/dev/cli_migration.py", 60),
    ("src/pheno/dev/granian_integration/config.py", 120),
    ("src/pheno/dev/instructor_integration/config.py", 89),
    ("src/pheno/dev/meilisearch_integration/config.py", 139),
    ("src/pheno/dev/mypy_integration/checker.py", 171),
    ("src/pheno/dev/pre_commit/config.py", 387),
    ("src/pheno/dev/ruff_integration/config.py", 87),
    ("src/pheno/dev/structlog/config.py", 212),
    ("src/pheno/infra/project_config.py", 766),
    ("src/pheno/infra/resources/container.py", 151),
    ("src/pheno/infra/resources/database.py", 913),
    ("src/pheno/patterns/refactoring/validator/layer_validator.py", 299),
    ("src/pheno/storage/repository.py", 181),
    ("src/pheno/testing/mcp_qa/adapters/fast_http_client.py", 286),
    ("src/pheno/testing/modes/fixtures.py", 237),
]

def fix_file(filepath: str, line_num: int) -> bool:
    """Fix missing colon in a specific line of a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"  ⚠ File not found: {filepath}")
        return False
    
    lines = path.read_text().splitlines(keepends=True)
    
    if line_num > len(lines):
        print(f"  ⚠ Line {line_num} out of range in {filepath}")
        return False
    
    # Get the line (0-indexed)
    idx = line_num - 1
    line = lines[idx]
    
    # Pattern: function definition with type hint and noqa comment, missing colon
    # Example: "def foo() -> bool  # noqa: PLR0911"
    # Should be: "def foo() -> bool:  # noqa: PLR0911"
    
    # Check if line has a noqa comment and is missing a colon
    if "# noqa" in line and not re.search(r":\s*#\s*noqa", line):
        # Add colon before the noqa comment
        fixed_line = re.sub(r"(\s+)#\s*noqa", r":  # noqa", line)
        
        if fixed_line != line:
            lines[idx] = fixed_line
            path.write_text("".join(lines))
            print(f"  ✓ Fixed: {filepath}:{line_num}")
            return True
        else:
            print(f"  ⚠ No change needed: {filepath}:{line_num}")
            return False
    else:
        print(f"  ⚠ Pattern not matched: {filepath}:{line_num}")
        return False

def main():
    """Fix all missing colons."""
    print("🔧 Fixing missing colons in function definitions...")
    print("")
    
    fixed_count = 0
    failed_count = 0
    
    for filepath, line_num in FIXES:
        if fix_file(filepath, line_num):
            fixed_count += 1
        else:
            failed_count += 1
    
    print("")
    print(f"✨ Fixed {fixed_count} files")
    if failed_count > 0:
        print(f"⚠ Failed to fix {failed_count} files")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

