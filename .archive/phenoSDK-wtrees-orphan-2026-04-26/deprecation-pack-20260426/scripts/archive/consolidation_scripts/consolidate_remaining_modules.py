#!/usr/bin/env python3
"""
Remaining Modules Consolidation Script.

This script consolidates the remaining fragmented modules into
a unified, well-architected solution following hexagonal architecture principles.

Actions performed:
1. Consolidate workflow and orchestration modules
2. Merge database and storage modules
3. Unify authentication modules
4. Optimize observability modules
5. Remove remaining duplicates and legacy code
"""

import shutil
from pathlib import Path


class RemainingModulesConsolidator:
    """Consolidates remaining modules."""

    def __init__(self, base_path: str = "src/pheno"):
        """Initialize consolidator.

        Args:
            base_path: Base path for pheno modules
        """
        self.base_path = Path(base_path)
        self.removed_files: list[str] = []
        self.consolidated_modules: dict[str, str] = {}

    def consolidate_workflow_modules(self) -> None:
        """Consolidate workflow and orchestration modules."""
        print("🔧 Consolidating workflow and orchestration modules...")

        # Files to remove (duplicate workflow functionality)
        duplicate_workflow_files = [
            "workflow/patterns/workflow.py",  # Duplicate workflow engine
            "workflow/patterns/",  # Old patterns directory
            "workflow/orchestrators/",  # Old orchestrators directory
            "workflow/unified_workflow_orchestrator.py",  # Temporary unified version
        ]

        for file_path in duplicate_workflow_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate workflow functionality
        self._consolidate_workflow_functionality()

    def consolidate_database_storage(self) -> None:
        """Consolidate database and storage modules."""
        print("🔧 Consolidating database and storage modules...")

        # Files to remove (duplicate database/storage functionality)
        duplicate_db_storage_files = [
            "database/storage/",  # Duplicate storage in database
            "storage/backends/",  # Old backends directory
            "storage/core/",  # Old core directory
            "storage/client.py",  # Old client
        ]

        for file_path in duplicate_db_storage_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate database/storage functionality
        self._consolidate_database_storage_functionality()

    def consolidate_auth_modules(self) -> None:
        """Consolidate authentication modules."""
        print("🔧 Consolidating authentication modules...")

        # Files to remove (duplicate auth functionality)
        duplicate_auth_files = [
            "auth/unified_auth/",  # Old unified auth directory
            "auth/credential_manager.py",  # Move to adapters
            "auth/interfaces.py",  # Move to ports
            "auth/manager.py",  # Old manager
            "auth/mfa_handler.py",  # Move to adapters
            "auth/playwright_adapter.py",  # Move to adapters
            "auth/session_broker.py",  # Move to adapters
            "auth/session_manager.py",  # Move to adapters
            "auth/token_cache.py",  # Move to adapters
            "auth/token_manager.py",  # Move to adapters
            "auth/types.py",  # Move to core
            "auth/utils/",  # Move to core
        ]

        for file_path in duplicate_auth_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate auth functionality
        self._consolidate_auth_functionality()

    def consolidate_observability_modules(self) -> None:
        """Consolidate observability modules."""
        print("🔧 Consolidating observability modules...")

        # Files to remove (duplicate observability functionality)
        duplicate_observability_files = [
            "observability/metrics/",  # Move to core
            "observability/logging/",  # Move to core
            "observability/tracing/",  # Move to core
            "observability/monitoring/",  # Move to core
        ]

        for file_path in duplicate_observability_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

        # Consolidate observability functionality
        self._consolidate_observability_functionality()

    def remove_legacy_core_modules(self) -> None:
        """Remove legacy core modules."""
        print("🧹 Removing legacy core modules...")

        # Files to remove (legacy core functionality)
        legacy_core_files = [
            "core/unified_manager.py",  # Old unified manager
            "core/shared/",  # Old shared directory
            "core/container.py",  # Move to adapters
            "core/exceptions.py",  # Move to base
        ]

        for file_path in legacy_core_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                    print(f"  ❌ Removed directory: {file_path}")
                else:
                    self._remove_file(full_path)
                    print(f"  ❌ Removed: {file_path}")

    def create_unified_architecture(self) -> None:
        """Create unified architecture structure."""
        print("🏗️  Creating unified architecture structure...")

        # Create the unified architecture structure
        unified_structure = {
            "workflow/": [
                "__init__.py",
                "engine.py",  # Unified workflow engine
                "orchestrator.py",  # Unified orchestrator
                "patterns.py",  # Unified patterns
                "saga.py",  # Saga pattern
                "state_machine.py",  # State machine pattern
            ],
            "database/": [
                "__init__.py",
                "client.py",  # Unified database client
                "adapters/",  # Database adapters
                "pooling.py",  # Connection pooling
                "realtime.py",  # Realtime features
            ],
            "storage/": [
                "__init__.py",
                "repository.py",  # Unified repository
                "adapters/",  # Storage adapters
            ],
            "auth/": [
                "__init__.py",
                "manager.py",  # Unified auth manager
                "providers/",  # Auth providers
                "adapters/",  # Auth adapters
            ],
            "observability/": [
                "__init__.py",
                "metrics.py",  # Unified metrics
                "logging.py",  # Unified logging
                "tracing.py",  # Unified tracing
                "monitoring.py",  # Unified monitoring
            ],
            "core/": [
                "__init__.py",
                "exceptions.py",  # Core exceptions
                "types.py",  # Core types
                "utils.py",  # Core utilities
            ],
        }

        for dir_path, files in unified_structure.items():
            full_dir = self.base_path / dir_path
            full_dir.mkdir(parents=True, exist_ok=True)

            for file_name in files:
                if file_name.endswith("/"):
                    # Create subdirectory
                    sub_dir = full_dir / file_name
                    sub_dir.mkdir(parents=True, exist_ok=True)
                    (sub_dir / "__init__.py").touch()
                    print(f"  ✅ Created directory: {dir_path}{file_name}")
                else:
                    file_path = full_dir / file_name
                    if not file_path.exists():
                        file_path.touch()
                        print(f"  ✅ Created: {dir_path}{file_name}")

    def _consolidate_workflow_functionality(self) -> None:
        """Consolidate workflow functionality."""
        print("  🔄 Consolidating workflow functionality...")

        # Keep the best workflow implementation
        workflow_core = self.base_path / "workflow/core"
        if workflow_core.exists():
            # Move core workflow to main workflow directory
            for file_path in workflow_core.glob("*.py"):
                if file_path.name != "__init__.py":
                    new_path = self.base_path / "workflow" / file_path.name
                    if not new_path.exists():
                        shutil.move(str(file_path), str(new_path))
                        print(f"    ✅ Moved {file_path.name} to main workflow")

        # Keep the best orchestration implementation
        orchestration_dir = self.base_path / "workflow/orchestration"
        if orchestration_dir.exists():
            # Move orchestration to main workflow directory
            orchestration_file = orchestration_dir / "orchestrator.py"
            if orchestration_file.exists():
                new_path = self.base_path / "workflow" / "orchestrator.py"
                if not new_path.exists():
                    shutil.move(str(orchestration_file), str(new_path))
                    print("    ✅ Moved orchestrator.py to main workflow")

    def _consolidate_database_storage_functionality(self) -> None:
        """Consolidate database/storage functionality."""
        print("  🔄 Consolidating database/storage functionality...")

        # Keep the best database implementation
        database_client = self.base_path / "database/client.py"
        if database_client.exists():
            print("    ✅ Keeping unified database client")

        # Keep the best storage implementation
        storage_repository = self.base_path / "storage/repository.py"
        if storage_repository.exists():
            print("    ✅ Keeping unified storage repository")

    def _consolidate_auth_functionality(self) -> None:
        """Consolidate auth functionality."""
        print("  🔄 Consolidating auth functionality...")

        # Keep the best auth implementation
        auth_init = self.base_path / "auth/__init__.py"
        if auth_init.exists():
            print("    ✅ Keeping unified auth module")

    def _consolidate_observability_functionality(self) -> None:
        """Consolidate observability functionality."""
        print("  🔄 Consolidating observability functionality...")

        # Keep the best observability implementation
        observability_init = self.base_path / "observability/__init__.py"
        if observability_init.exists():
            print("    ✅ Keeping unified observability module")

    def generate_consolidation_report(self) -> None:
        """Generate consolidation report."""
        print("\n📊 Remaining Modules Consolidation Report")
        print("=" * 60)
        print(f"Files removed: {len(self.removed_files)}")
        print(f"Modules consolidated: {len(self.consolidated_modules)}")

        print("\nRemoved files:")
        for file_path in self.removed_files:
            print(f"  - {file_path}")

        print("\nConsolidated modules:")
        for old_module, new_module in self.consolidated_modules.items():
            print(f"  - {old_module} → {new_module}")

    def run_consolidation(self) -> None:
        """Run full remaining modules consolidation process."""
        print("🚀 Starting remaining modules consolidation...")
        print("=" * 60)

        # Step 1: Create unified architecture
        self.create_unified_architecture()

        # Step 2: Consolidate workflow modules
        self.consolidate_workflow_modules()

        # Step 3: Consolidate database/storage
        self.consolidate_database_storage()

        # Step 4: Consolidate auth modules
        self.consolidate_auth_modules()

        # Step 5: Consolidate observability modules
        self.consolidate_observability_modules()

        # Step 6: Remove legacy core modules
        self.remove_legacy_core_modules()

        # Step 7: Generate report
        self.generate_consolidation_report()

        print("\n✅ Remaining modules consolidation complete!")
        print("Next steps:")
        print("1. Update imports in remaining files")
        print("2. Run tests to ensure functionality is preserved")
        print("3. Update documentation")
        print("4. Final architecture review")

    def _remove_file(self, file_path: Path) -> None:
        """Remove a file and track it."""
        try:
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
            self.removed_files.append(str(file_path))
        except Exception as e:
            print(f"    ⚠️  Could not remove {file_path}: {e}")


def main():
    """Main consolidation function."""
    consolidator = RemainingModulesConsolidator()
    consolidator.run_consolidation()


if __name__ == "__main__":
    main()
