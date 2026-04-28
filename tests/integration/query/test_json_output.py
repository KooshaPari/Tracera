"""Integration tests for Epic 3: JSON output flag (FR32).

Tests --json flag on various commands.
"""

import json
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
    # Set up temporary config directory
    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    # Initialize project
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


def test_item_list_json_output(runner: Any, _temp_project: Any) -> None:
    """Test item list with JSON output (FR32)."""
    # Create test item
    create_result = runner.invoke(
        app,
        [
            "item",
            "create",
            "JSON Test Item",
            "--view",
            "FEATURE",
            "--type",
            "feature",
        ],
    )
    assert create_result.exit_code == 0, create_result.stdout

    # List with JSON output
    result = runner.invoke(app, ["item", "list", "--json"])
    assert result.exit_code == 0

    # Parse JSON
    output = result.stdout.strip()
    json_start = output.find("{")
    if json_start >= 0:
        json_str = output[json_start:]
        data = json.loads(json_str)
        assert "items" in data
        assert "count" in data
        assert len(data["items"]) > 0
        assert data["items"][0]["title"] == "JSON Test Item"


def test_query_json_output(runner: Any, _temp_project: Any) -> None:
    """Test query with JSON output (FR32)."""
    # Create test item
    runner.invoke(
        app,
        [
            "item",
            "create",
            "Query JSON Test",
            "--view",
            "FEATURE",
            "--type",
            "feature",
            "--status",
            "todo",
        ],
    )

    # Query with JSON
    result = runner.invoke(app, ["query", "--filter", "status=todo", "--json"])
    assert result.exit_code == 0

    # Parse JSON
    output = result.stdout.strip()
    json_start = output.find("{")
    if json_start >= 0:
        json_str = output[json_start:]
        data = json.loads(json_str)
        assert "items" in data
        assert "count" in data
        assert data["count"] > 0


def test_json_output_structure(runner: Any, _temp_project: Any) -> None:
    """Test JSON output has correct structure."""
    # Create item with all fields
    runner.invoke(
        app,
        [
            "item",
            "create",
            "Complete Item",
            "--view",
            "FEATURE",
            "--type",
            "feature",
            "--status",
            "in_progress",
            "--priority",
            "high",
            "--owner",
            "testuser",
            "--description",
            "Test description",
        ],
    )

    # Get JSON output
    result = runner.invoke(app, ["item", "list", "--json"])
    output = result.stdout.strip()
    json_start = output.find("{")
    if json_start >= 0:
        json_str = output[json_start:]
        data = json.loads(json_str)

        item = data["items"][0]
        # Verify all expected fields
        assert "id" in item
        assert "title" in item
        assert "description" in item
        assert "view" in item
        assert "type" in item
        assert "status" in item
        assert "priority" in item
        assert "owner" in item
        assert "version" in item
        assert "created_at" in item
        assert "updated_at" in item
