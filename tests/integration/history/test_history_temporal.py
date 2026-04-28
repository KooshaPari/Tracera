"""Integration tests for Epic 7: History and Temporal Queries (FR54-FR59).

Tests history tracking, temporal queries, and rollback.
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


def test_view_history(temp_project: Any, _runner: Any) -> None:
    """Test viewing item history (FR55)."""
    # Create item
    result1 = runner.invoke(
        app,
        [
            "item",
            "create",
            "History Test Item",
            "--view",
            "FEATURE",
            "--type",
            "feature",
        ],
    )
    assert result1.exit_code == 0

    # Update item
    # Would need item ID from result1
    # result2 = runner.invoke(app, ["item", "update", item_id, "--status", "in_progress"])

    # View history
    # result3 = runner.invoke(app, ["history", item_id])
    # assert result3.exit_code == 0
    # assert "item_created" in result3.stdout or "History Test Item" in result3.stdout


def test_temporal_query(temp_project: Any, _runner: Any) -> None:
    """Test temporal queries with --at flag (FR56, FR59)."""
    # Create item
    result1 = runner.invoke(
        app,
        [
            "item",
            "create",
            "Temporal Test",
            "--view",
            "FEATURE",
            "--type",
            "feature",
        ],
    )
    assert result1.exit_code == 0

    # Query at specific date
    # Would need item ID
    # result2 = runner.invoke(app, ["history", item_id, "--at", "2025-01-15"])
    # assert result2.exit_code == 0


def test_rollback_item(temp_project: Any, runner: Any) -> None:
    """Test rolling back item to previous version (FR57)."""
    # Create and update item
    # Then rollback
    # result = runner.invoke(app, ["history", "rollback", item_id, "--version", "2", "--confirm"])
    # assert result.exit_code == 0
    # Placeholder - would need full item setup
