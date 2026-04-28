#!/usr/bin/env python3
"""
Workflow Migration Script
Helps migrate from old workflows to consolidated workflow.
"""

import argparse
import shutil
from pathlib import Path

import yaml


class WorkflowMigrator:
    """Migrate from old workflows to consolidated workflow."""

    def __init__(self, workflows_dir: str):
        self.workflows_dir = Path(workflows_dir)
        self.archive_dir = self.workflows_dir / "archive"

        # Workflows to disable (add if: false)
        self.workflows_to_disable = [
            "tests_light.yml",
            "config_kit_tests.yml",
            "test.yml",
            "pheno_cli_env_test.yml",
            "security-testing.yml",
            "mcp_oauth_tests.yml",
            "full-quality.yml",
            "lint.yml",
            "code-quality-gates.yml",
            "quality.yml",
            "code-quality.yml",
            "pr-quality.yml",
            "quality-full.yml",
            "security.yml",
            "ci-matrix.yml",
            "ci.yml",
            "build.yml",
            "architecture-fitness.yml",
        ]

        # Workflows to keep as-is
        self.workflows_to_keep = [
            "release.yml",
            "version.yml",
            "deploy.yml",
        ]

    def disable_workflows(self) -> None:
        """Disable workflows by adding 'if: false' to their triggers."""
        print("🔧 Disabling old workflows...")

        for workflow_name in self.workflows_to_disable:
            workflow_path = self.workflows_dir / workflow_name

            if not workflow_path.exists():
                print(f"  ⚠️  {workflow_name} not found, skipping")
                continue

            try:
                # Read workflow
                with open(workflow_path) as f:
                    workflow_data = yaml.safe_load(f)

                # Add if: false to disable
                if "on" in workflow_data:
                    workflow_data["on"] = {
                        "workflow_dispatch": None,
                        "if": "false",
                    }
                else:
                    workflow_data["on"] = {"if": "false"}

                # Write back
                with open(workflow_path, "w") as f:
                    yaml.dump(
                        workflow_data,
                        f,
                        default_flow_style=False,
                        sort_keys=False,
                    )

                print(f"  ✅ Disabled {workflow_name}")

            except Exception as e:
                print(f"  ❌ Failed to disable {workflow_name}: {e}")

    def enable_workflows(self) -> None:
        """Re-enable workflows by removing 'if: false'."""
        print("🔧 Re-enabling workflows...")

        for workflow_name in self.workflows_to_disable:
            workflow_path = self.workflows_dir / workflow_name

            if not workflow_path.exists():
                continue

            try:
                # Read workflow
                with open(workflow_path) as f:
                    workflow_data = yaml.safe_load(f)

                # Remove if: false
                if "on" in workflow_data and workflow_data["on"].get("if") == "false":
                    # Restore original triggers from archive
                    archive_path = self.archive_dir / workflow_name
                    if archive_path.exists():
                        with open(archive_path) as f:
                            original_data = yaml.safe_load(f)
                            workflow_data["on"] = original_data["on"]

                # Write back
                with open(workflow_path, "w") as f:
                    yaml.dump(
                        workflow_data,
                        f,
                        default_flow_style=False,
                        sort_keys=False,
                    )

                print(f"  ✅ Re-enabled {workflow_name}")

            except Exception as e:
                print(f"  ❌ Failed to re-enable {workflow_name}: {e}")

    def remove_disabled_workflows(self) -> None:
        """Remove disabled workflows (permanent)."""
        print("🗑️  Removing disabled workflows...")

        for workflow_name in self.workflows_to_disable:
            workflow_path = self.workflows_dir / workflow_name

            if workflow_path.exists():
                # Move to archive instead of deleting
                archive_path = self.archive_dir / f"removed_{workflow_name}"
                shutil.move(str(workflow_path), str(archive_path))
                print(f"  ✅ Moved {workflow_name} to archive")
            else:
                print(f"  ⚠️  {workflow_name} not found, skipping")

    def restore_from_archive(self) -> None:
        """Restore workflows from archive."""
        print("📁 Restoring workflows from archive...")

        for workflow_file in self.archive_dir.glob("*.yml"):
            if not workflow_file.name.startswith("removed_"):
                target_path = self.workflows_dir / workflow_file.name
                shutil.copy2(workflow_file, target_path)
                print(f"  ✅ Restored {workflow_file.name}")

    def create_migration_plan(self) -> str:
        """Create a step-by-step migration plan."""
        return """
# Workflow Migration Plan

## Phase 1: Preparation
1. ✅ Create consolidated-ci.yml workflow
2. ✅ Archive existing workflows
3. ✅ Create migration scripts

## Phase 2: Testing
1. Test consolidated-ci.yml workflow on a feature branch
2. Verify all functionality works as expected
3. Check that quality gates are properly enforced

## Phase 3: Gradual Migration
1. Disable old workflows (add if: false)
2. Monitor consolidated workflow for 1-2 days
3. Fix any issues that arise
4. Gradually remove disabled workflows

## Phase 4: Cleanup
1. Remove disabled workflows permanently
2. Update documentation
3. Train team on new workflow

## Commands

### Disable old workflows:
```bash
python3 scripts/migrate_workflows.py --disable
```

### Re-enable workflows (if needed):
```bash
python3 scripts/migrate_workflows.py --enable
```

### Remove disabled workflows:
```bash
python3 scripts/migrate_workflows.py --remove
```

### Restore from archive:
```bash
python3 scripts/migrate_workflows.py --restore
```

## Rollback Plan
If issues arise, you can quickly restore all workflows:
```bash
python3 scripts/migrate_workflows.py --restore
```
"""


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Migrate GitHub Actions workflows")
    parser.add_argument("workflows_dir", help="Path to workflows directory")
    parser.add_argument("--disable", action="store_true", help="Disable old workflows")
    parser.add_argument("--enable", action="store_true", help="Re-enable workflows")
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove disabled workflows",
    )
    parser.add_argument("--restore", action="store_true", help="Restore from archive")
    parser.add_argument("--plan", action="store_true", help="Show migration plan")

    args = parser.parse_args()

    migrator = WorkflowMigrator(args.workflows_dir)

    if args.plan:
        print(migrator.create_migration_plan())
    elif args.disable:
        migrator.disable_workflows()
    elif args.enable:
        migrator.enable_workflows()
    elif args.remove:
        migrator.remove_disabled_workflows()
    elif args.restore:
        migrator.restore_from_archive()
    else:
        print(
            "Please specify an action: --disable, --enable, --remove, --restore, or --plan",
        )


if __name__ == "__main__":
    main()
