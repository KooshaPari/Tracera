#!/usr/bin/env python3
"""Phase 1 Week 4: Standardize naming and improve maintainability."""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Working directory
REPO_ROOT = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk")
SRC_DIR = REPO_ROOT / "src"

# Refactoring mappings
FUNCTION_RENAMES = {
    # FETCH/RETRIEVE → GET
    "retrieve_secret": "get_secret",
    "fetch_token": "get_token",

    # NEW/INIT → CREATE
    "init_alembic": "create_alembic",
    "new_id": "create_id",
    "init_otel": "create_otel",

    # REMOVE/DESTROY → DELETE
    "remove_credential": "delete_credential",
    "remove_automation_rule": "delete_automation_rule",
    "remove_policy": "delete_policy",
    "remove_node": "delete_node",
    "remove_plugin": "delete_plugin",
    "remove_child": "delete_child",
    "remove_pattern": "delete_pattern",
    "remove_metadata": "delete_metadata",
    "remove_logger": "delete_logger",
    "remove_tag": "delete_tag",
    "remove_attribute": "delete_attribute",
    "remove_check": "delete_check",
    "destroy_database": "delete_database",
    "remove_dto_validator": "delete_dto_validator",
    "remove_business_rule_validator": "delete_business_rule_validator",
    "remove_rule": "delete_rule",
    "remove_plugin_by_name": "delete_plugin_by_name",

    # CHECK/VERIFY → VALIDATE
    "check_hardcoded_secrets": "validate_hardcoded_secrets",
    "check_migration_needed": "validate_migration_needed",
    "check_due": "validate_due",
    "check_file": "validate_file",
    "check_directory": "validate_directory",
    "check_logger_health": "validate_logger_health",
    "check_compliance": "validate_compliance",
    "check_health": "validate_health",
    "check_port_health": "validate_port_health",
    "check_cloudflare_setup": "validate_cloudflare_setup",
    "verify_master_password": "validate_master_password",
    "check_component": "validate_component",
    "check_one": "validate_one",
    "check_all": "validate_all",
    "check_access": "validate_access",
    "check_status": "validate_status",
    "check_deployment_health": "validate_deployment_health",
    "check_gpl_compatibility": "validate_gpl_compatibility",
    "check_schema": "validate_schema",
    "check_alerts": "validate_alerts",
    "check_sla_compliance": "validate_sla_compliance",
    "check_compatibility": "validate_compatibility",
    "check_priority": "validate_priority",
    "verify_code": "validate_code",
    "check_code_quality": "validate_code_quality",
    "check_tests_status": "validate_tests_status",
    "check_security_vulnerabilities": "validate_security_vulnerabilities",
    "check_dependencies": "validate_dependencies",
    "check_configuration": "validate_configuration",
    "check_build_artifacts": "validate_build_artifacts",
}

ABBREVIATION_RENAMES = {
    # Standard abbreviations to expand
    r'\bcfg\b': 'config',
    r'\bctx\b': 'context',
    r'\bmgr\b': 'manager',
    r'\bsrv\b': 'service',
    # env is context-dependent, skip for safety
}


def find_files_with_pattern(pattern: str) -> List[Path]:
    """Find all files containing a pattern using ripgrep."""
    try:
        result = subprocess.run(
            ["rg", "-l", pattern, str(SRC_DIR)],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return [Path(line.strip()) for line in result.stdout.split('\n') if line.strip()]
        return []
    except Exception as e:
        print(f"Error searching for pattern {pattern}: {e}")
        return []


def rename_function_in_file(file_path: Path, old_name: str, new_name: str) -> int:
    """Rename a function in a file, handling definitions and calls."""
    try:
        content = file_path.read_text()
        original_content = content

        # Match function definitions: def old_name(
        content = re.sub(
            rf'\bdef {re.escape(old_name)}\b',
            f'def {new_name}',
            content
        )

        # Match method calls: .old_name( or self.old_name(
        content = re.sub(
            rf'\.{re.escape(old_name)}\b',
            f'.{new_name}',
            content
        )

        # Match standalone function calls: old_name(
        content = re.sub(
            rf'\b{re.escape(old_name)}\(',
            f'{new_name}(',
            content
        )

        if content != original_content:
            file_path.write_text(content)
            return 1
        return 0
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def replace_abbreviations_in_file(file_path: Path) -> int:
    """Replace abbreviations in a file."""
    try:
        content = file_path.read_text()
        original_content = content
        changes = 0

        for pattern, replacement in ABBREVIATION_RENAMES.items():
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes += 1
                content = new_content

        if content != original_content:
            file_path.write_text(content)
            return changes
        return 0
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def main():
    """Execute Phase 1 Week 4 refactoring."""
    print("=" * 80)
    print("PHASE 1 WEEK 4: STANDARDIZE NAMING")
    print("=" * 80)

    # Track statistics
    functions_renamed = 0
    files_modified = set()
    abbreviations_replaced = 0

    # Step 1: Rename functions
    print("\n1. Standardizing function names...")
    for old_name, new_name in FUNCTION_RENAMES.items():
        print(f"   {old_name} → {new_name}")

        # Find files containing the old name
        pattern = rf'\b{old_name}\b'
        files = find_files_with_pattern(pattern)

        for file_path in files:
            if file_path.suffix == '.py':  # Only process Python files
                changes = rename_function_in_file(file_path, old_name, new_name)
                if changes > 0:
                    functions_renamed += 1
                    files_modified.add(file_path)
                    print(f"      ✓ {file_path.relative_to(REPO_ROOT)}")

    # Step 2: Replace abbreviations
    print("\n2. Clarifying abbreviations...")
    py_files = list(SRC_DIR.rglob("*.py"))
    for file_path in py_files:
        changes = replace_abbreviations_in_file(file_path)
        if changes > 0:
            abbreviations_replaced += changes
            files_modified.add(file_path)
            print(f"   ✓ {file_path.relative_to(REPO_ROOT)} ({changes} replacements)")

    # Print summary
    print("\n" + "=" * 80)
    print("REFACTORING SUMMARY")
    print("=" * 80)
    print(f"Functions renamed: {functions_renamed}")
    print(f"Abbreviations replaced: {abbreviations_replaced}")
    print(f"Files modified: {len(files_modified)}")
    print("\nNext steps:")
    print("1. Add strategic WHY comments to complex business logic")
    print("2. Update documentation")
    print("3. Run test suite")

    return 0


if __name__ == "__main__":
    exit(main())
