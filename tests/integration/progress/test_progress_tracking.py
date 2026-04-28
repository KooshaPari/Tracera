"""Integration tests for Epic 7: Progress Tracking (FR68-FR73).

Tests progress calculation, blocked items, stalled items, velocity, and reports.
"""

from typing import Any

import pytest

pytestmark = pytest.mark.integration
from typer.testing import CliRunner

from tracertm.cli.app import app


@pytest.fixture
def runner() -> None:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project(runner: Any, tmp_path: Any, monkeypatch: Any) -> str:
    """Create a temporary project for testing."""
    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True)
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


def test_progress_calculation(temp_project: Any, _runner: Any) -> None:
    """Test progress calculation (FR68)."""
    # Create parent and child items
    result1 = runner.invoke(
        app,
        [
            "item",
            "create",
            "Parent Feature",
            "--view",
            "FEATURE",
            "--type",
            "feature",
        ],
    )
    assert result1.exit_code == 0

    # Show progress
    result2 = runner.invoke(app, ["progress", "show"])
    assert result2.exit_code == 0


def test_progress_view(temp_project: Any, _runner: Any) -> None:
    """Test PROGRESS view (FR69)."""
    # Show progress for view
    result = runner.invoke(app, ["progress", "show", "--view", "FEATURE"])
    assert result.exit_code == 0


def test_blocked_items(temp_project: Any, _runner: Any) -> None:
    """Test blocked items detection (FR70)."""
    # Create items and blocking links
    # Then check blocked items
    result = runner.invoke(app, ["progress", "blocked"])
    assert result.exit_code == 0


def test_stalled_items(temp_project: Any, _runner: Any) -> None:
    """Test stalled items detection (FR71)."""
    # Show stalled items
    result = runner.invoke(app, ["progress", "stalled"])
    assert result.exit_code == 0


def test_velocity_tracking(temp_project: Any, _runner: Any) -> None:
    """Test velocity tracking (FR73)."""
    # Show velocity
    result = runner.invoke(app, ["progress", "velocity"])
    assert result.exit_code == 0
    assert "velocity" in result.stdout.lower() or "items" in result.stdout.lower()


def test_progress_report(temp_project: Any, _runner: Any) -> None:
    """Test progress report generation (FR72)."""
    # Generate report
    result = runner.invoke(app, ["progress", "report", "--days", "7"])
    assert result.exit_code == 0

    # Generate JSON report
    result2 = runner.invoke(app, ["progress", "report", "--days", "30", "--json"])
    assert result2.exit_code == 0
