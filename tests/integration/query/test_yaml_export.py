"""Integration tests for Epic 3: YAML export format (FR30).

Tests the rtm export --format yaml command.
"""

from typing import Any

import pytest

pytestmark = pytest.mark.integration
import pathlib

import yaml
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

    # Initialize config with database URL
    db_path = tmp_path / "test.db"
    result_config = runner.invoke(
        app,
        ["config", "init", "--database-url", f"sqlite:///{db_path}"],
    )
    assert result_config.exit_code == 0

    # Run database migrations
    result_migrate = runner.invoke(app, ["db", "migrate"])
    assert result_migrate.exit_code == 0

    # Initialize project
    result = runner.invoke(
        app,
        ["project", "init", "test-project"],
    )
    assert result.exit_code == 0
    return "test-project"


def test_export_yaml_format(runner: Any, _temp_project: Any) -> None:
    """Test export to YAML format (FR30)."""
    # Create test items
    runner.invoke(
        app,
        [
            "item",
            "create",
            "Test Feature",
            "--view",
            "FEATURE",
            "--type",
            "feature",
            "--status",
            "todo",
        ],
    )

    # Export to YAML
    result = runner.invoke(app, ["export", "--format", "yaml"])
    assert result.exit_code == 0

    # Parse YAML output
    yaml_data = yaml.safe_load(result.stdout)
    assert "project" in yaml_data
    assert "items" in yaml_data
    assert "links" in yaml_data
    assert len(yaml_data["items"]) > 0
    assert yaml_data["items"][0]["title"] == "Test Feature"


def test_export_yaml_to_file(runner: Any, temp_project: Any, _tmp_path: Any) -> None:
    """Test export YAML to file."""
    # Create test item
    runner.invoke(
        app,
        [
            "item",
            "create",
            "YAML Export Test",
            "--view",
            "FEATURE",
            "--type",
            "feature",
        ],
    )

    # Export to file
    output_file = tmp_path / "export.yaml"
    result = runner.invoke(app, ["export", "--format", "yaml", "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()

    # Verify file content
    with pathlib.Path(output_file).open(encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)
        assert "items" in yaml_data
        assert len(yaml_data["items"]) > 0


def test_export_yaml_includes_all_data(runner: Any, _temp_project: Any) -> None:
    """Test YAML export includes all required fields."""
    # Create item with metadata
    runner.invoke(
        app,
        [
            "item",
            "create",
            "Complete Feature",
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
        ],
    )

    # Export to YAML
    result = runner.invoke(app, ["export", "--format", "yaml"])
    yaml_data = yaml.safe_load(result.stdout)

    item = yaml_data["items"][0]
    assert "id" in item
    assert "title" in item
    assert "view" in item
    assert "type" in item
    assert "status" in item
    assert "priority" in item
    assert "owner" in item
    assert "created_at" in item
    assert "updated_at" in item
