"""Integration tests for Epic 4: Cycle detection (FR22).

Tests cycle prevention for depends_on relationships.
"""

from typing import Any

import pytest

pytestmark = pytest.mark.integration
from sqlalchemy.orm import Session
from typer.testing import CliRunner

from tracertm.cli.app import app
from tracertm.database.connection import DatabaseConnection
from tracertm.services.cycle_detection_service import CycleDetectionService


@pytest.fixture
def runner() -> None:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project(runner: Any, tmp_path: Any, monkeypatch: Any) -> str:
    """Create a temporary project for testing."""
    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    db_path = tmp_path / "test.db"
    result = runner.invoke(
        app,
        [
            "project",
            "init",
            "test-project",
            "--database-url",
            f"sqlite:///{db_path}",
        ],
    )
    assert result.exit_code == 0
    return "test-project"


def test_cycle_prevention_on_link_creation(runner: Any, _temp_project: Any) -> None:
    """Test that cycle prevention prevents creating circular dependencies (FR22)."""
    # Create items
    result1 = runner.invoke(
        app,
        [
            "item",
            "create",
            "Item A",
            "--view",
            "FEATURE",
            "--type",
            "feature",
        ],
    )
    assert result1.exit_code == 0
    item_a_id = result1.stdout.split("ID:")[1].strip().split()[0] if "ID:" in result1.stdout else None

    result2 = runner.invoke(
        app,
        [
            "item",
            "create",
            "Item B",
            "--view",
            "FEATURE",
            "--type",
            "feature",
        ],
    )
    assert result2.exit_code == 0
    item_b_id = result2.stdout.split("ID:")[1].strip().split()[0] if "ID:" in result2.stdout else None

    # Create A -> B link
    result3 = runner.invoke(
        app,
        [
            "link",
            "create",
            item_a_id,
            item_b_id,
            "--type",
            "depends_on",
        ],
    )
    assert result3.exit_code == 0

    # Try to create B -> A link (should fail - cycle)
    result4 = runner.invoke(
        app,
        [
            "link",
            "create",
            item_b_id,
            item_a_id,
            "--type",
            "depends_on",
        ],
    )
    assert result4.exit_code == 1
    assert "Circular dependency" in result4.stdout or "cycle" in result4.stdout.lower()


def test_cycle_detection_command(runner: Any, _temp_project: Any) -> None:
    """Test cycle detection command (FR22)."""
    # Create items and links that form a cycle
    # This test verifies the detect-cycles command works

    result = runner.invoke(app, ["link", "detect-cycles"])
    assert result.exit_code == 0
    # Should show no cycles initially
    assert "No cycles detected" in result.stdout or "cycle" in result.stdout.lower()


def test_cycle_detection_service(runner: Any, temp_project: Any, tmp_path: Any, _monkeypatch: Any) -> None:
    """Test cycle detection service directly."""
    from tracertm.config.manager import ConfigManager

    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    config_manager = ConfigManager()
    db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{db_path}"
    config_manager.set("database_url", database_url)

    db = DatabaseConnection(database_url)
    db.connect()

    with Session(db.engine) as session:
        project_id = config_manager.get("current_project_id")
        if not project_id:
            # Create a test project
            from tracertm.models.project import Project

            project = Project(name="test", description="test")
            session.add(project)
            session.commit()
            project_id = str(project.id)

        service = CycleDetectionService(session)
        result = service.detect_cycles(project_id, "depends_on")

        has_cycles = result.has_cycles if hasattr(result, "has_cycles") else result["has_cycles"]
        cycle_count = result.cycle_count if hasattr(result, "cycle_count") else result["cycle_count"]
        cycles = result.cycles if hasattr(result, "cycles") else result["cycles"]

        assert has_cycles is False
        assert cycle_count == 0
        assert isinstance(cycles, list)
