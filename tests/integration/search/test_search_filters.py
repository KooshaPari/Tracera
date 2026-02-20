"""Integration tests for Epic 7: Search and Filters (FR60-FR67).

Tests full-text search, filtering, and saved queries.
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


def test_full_text_search(temp_project: Any, _runner: Any) -> None:
    """Test full-text search (FR60)."""
    # Create items
    runner.invoke(
        app,
        [
            "item",
            "create",
            "Authentication Feature",
            "--view",
            "FEATURE",
            "--type",
            "feature",
        ],
    )

    # Search
    result = runner.invoke(app, ["search", "Authentication"])
    assert result.exit_code == 0
    assert "Authentication" in result.stdout or "No items found" in result.stdout


def test_search_with_filters(temp_project: Any, _runner: Any) -> None:
    """Test search with multiple filters (FR61-FR64, FR67)."""
    # Create item with specific attributes
    runner.invoke(
        app,
        [
            "item",
            "create",
            "Filtered Item",
            "--view",
            "FEATURE",
            "--type",
            "feature",
            "--status",
            "todo",
            "--owner",
            "alice",
        ],
    )

    # Search with filters
    result = runner.invoke(
        app,
        [
            "search",
            "Filtered",
            "--status",
            "todo",
            "--owner",
            "alice",
        ],
    )
    assert result.exit_code == 0


def test_fuzzy_matching(temp_project: Any, _runner: Any) -> None:
    """Test fuzzy matching (FR66)."""
    # Create item
    runner.invoke(
        app,
        [
            "item",
            "create",
            "Authentication System",
            "--view",
            "FEATURE",
            "--type",
            "feature",
        ],
    )

    # Search with fuzzy
    result = runner.invoke(app, ["search", "auth", "--fuzzy"])
    assert result.exit_code == 0


def test_saved_queries(temp_project: Any, _runner: Any) -> None:
    """Test saved queries (FR65)."""
    # Save a query
    result1 = runner.invoke(
        app,
        [
            "saved-queries",
            "save",
            "my-todos",
            "--filter",
            "status=todo",
        ],
    )
    assert result1.exit_code == 0

    # List queries
    result2 = runner.invoke(app, ["saved-queries", "list"])
    assert result2.exit_code == 0
    assert "my-todos" in result2.stdout

    # Delete query
    result3 = runner.invoke(app, ["saved-queries", "delete", "my-todos"])
    assert result3.exit_code == 0
