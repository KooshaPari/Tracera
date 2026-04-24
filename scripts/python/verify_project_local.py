#!/usr/bin/env python
"""Verification script for project-local storage implementation.

Runs a series of checks to ensure all functionality works correctly.
"""

import sys
import tempfile
from pathlib import Path

import yaml

from tracertm.storage.local_storage import LocalStorageManager


def check(condition: bool, _message: str) -> bool:
    """Check a condition and print result."""
    return bool(condition)


def main() -> int:
    """Run verification checks."""
    checks_passed = 0
    checks_total = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        storage = LocalStorageManager(base_dir=base_dir / ".tracertm")

        # ========================================
        # 1. Database initialization
        # ========================================
        checks_total += 1
        if check(storage.db_path.exists(), "Global SQLite database created"):
            checks_passed += 1

        # Check project_registry table exists
        session = storage.get_session()
        try:
            result = session.execute(
                storage.engine.dialect.statement_compiler(storage.engine.dialect, None).preparer.quote(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='project_registry'",
                ),
            )
            checks_total += 1
            if check(result.fetchone() is not None, "project_registry table exists"):
                checks_passed += 1
        except Exception:
            checks_total += 1
            check(False, "project_registry table exists")
        finally:
            session.close()

        # ========================================
        # 2. Project initialization
        # ========================================
        project_path = base_dir / "test-project"
        project_path.mkdir()

        try:
            trace_dir, project_id = storage.init_project(project_path, project_name="Test Project")

            checks_total += 1
            if check(trace_dir.exists(), ".trace/ directory created"):
                checks_passed += 1

            checks_total += 1
            if check((trace_dir / "project.yaml").exists(), "project.yaml created"):
                checks_passed += 1

            # Check subdirectories
            for subdir in ["epics", "stories", "tests", "tasks", "docs", "changes"]:
                checks_total += 1
                if check((trace_dir / subdir).is_dir(), f"{subdir}/ directory created"):
                    checks_passed += 1

            checks_total += 1
            if check((trace_dir / ".meta").is_dir(), ".meta/ directory created"):
                checks_passed += 1

            checks_total += 1
            if check(
                (trace_dir / ".meta" / "links.yaml").exists(),
                "links.yaml created",
            ):
                checks_passed += 1

        except Exception:
            checks_total += 7
            return 1

        # ========================================
        # 3. project.yaml format
        # ========================================
        project_yaml_path = trace_dir / "project.yaml"
        project_config = yaml.safe_load(project_yaml_path.read_text())

        checks_total += 1
        if check(project_config.get("id") == project_id, "Project ID correct"):
            checks_passed += 1

        checks_total += 1
        if check(project_config.get("name") == "Test Project", "Project name correct"):
            checks_passed += 1

        checks_total += 1
        if check("counters" in project_config, "Counters present"):
            checks_passed += 1

        checks_total += 1
        if check(project_config.get("counters", {}).get("epic") == 0, "Epic counter is 0"):
            checks_passed += 1

        # ========================================
        # 4. Counter operations
        # ========================================
        counters = storage.get_project_counters(project_path)
        checks_total += 1
        if check(
            counters == {"epic": 0, "story": 0, "test": 0, "task": 0},
            "Initial counters correct",
        ):
            checks_passed += 1

        counter, external_id = storage.increment_project_counter(project_path, "epic")
        checks_total += 1
        if check(counter == 1, "Counter incremented to 1"):
            checks_passed += 1

        checks_total += 1
        if check(external_id == "EPIC-001", "External ID generated correctly"):
            checks_passed += 1

        # Verify in file
        project_config = yaml.safe_load(project_yaml_path.read_text())
        checks_total += 1
        if check(
            project_config["counters"]["epic"] == 1,
            "Counter persisted to file",
        ):
            checks_passed += 1

        # ========================================
        # 5. Project detection
        # ========================================
        checks_total += 1
        if check(storage.is_trace_project(project_path), "is_trace_project() works"):
            checks_passed += 1

        checks_total += 1
        if check(
            storage.get_project_trace_dir(project_path) == trace_dir,
            "get_project_trace_dir() works",
        ):
            checks_passed += 1

        # ========================================
        # 6. Project storage
        # ========================================
        project_storage = storage.get_project_storage_for_path(project_path)

        checks_total += 1
        if check(project_storage is not None, "get_project_storage_for_path() works"):
            checks_passed += 1

        if project_storage is None:
            pass
        else:
            checks_total += 1
            if check(
                project_storage.is_project_local,
                "ProjectStorage in project-local mode",
            ):
                checks_passed += 1

            checks_total += 1
            if check(
                project_storage.project_dir == trace_dir,
                "ProjectStorage uses .trace/ directory",
            ):
                checks_passed += 1

            # ========================================
            # 7. Item creation and indexing
            # ========================================

            # Create project in DB
            project = project_storage.create_or_update_project(name="Test Project", description="Test")

            item_storage = project_storage.get_item_storage(project)

            # Create epic
            _epic = item_storage.create_item(
                title="Test Epic",
                item_type="epic",
                external_id="EPIC-002",
                description="Test description",
                status="todo",
                priority="high",
            )

            epic_md = trace_dir / "epics" / "EPIC-002.md"
            checks_total += 1
            if check(epic_md.exists(), "Epic markdown file created"):
                checks_passed += 1

            # Verify markdown content
            epic_content = epic_md.read_text()
            checks_total += 1
            if check("# Test Epic" in epic_content, "Epic markdown has title"):
                checks_passed += 1

            checks_total += 1
            if check("EPIC-002" in epic_content, "Epic markdown has external ID"):
                checks_passed += 1

            # Index project
            try:
                counts = storage.index_project(project_path)
                checks_total += 1
                if check(counts["epics"] >= 1, "Project indexing works"):
                    checks_passed += 1
            except Exception:
                checks_total += 1

            # ========================================
            # 8. Search functionality
            # ========================================
            try:
                search_results = storage.search_items("Test", project_id=str(project.id))
                checks_total += 1
                if check(len(search_results) > 0, "Full-text search works"):
                    checks_passed += 1
            except Exception:
                checks_total += 1

        # ========================================
        # 9. Backward compatibility
        # ========================================
        legacy_storage = storage.get_project_storage("legacy-test")
        checks_total += 1
        if check(
            not legacy_storage.is_project_local,
            "Legacy mode still works",
        ):
            checks_passed += 1

        checks_total += 1
        if check(
            str(storage.projects_dir) in str(legacy_storage.project_dir),
            "Legacy mode uses ~/.tracertm/projects/",
        ):
            checks_passed += 1

    # ========================================
    # Summary
    # ========================================

    if checks_passed == checks_total:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
