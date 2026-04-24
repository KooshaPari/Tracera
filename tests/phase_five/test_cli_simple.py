from typing import Any

"""Simple CLI test to verify mocking approach works."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from tracertm.cli.commands.item import app as item_app


@pytest.fixture
def cli_runner() -> None:
    return CliRunner()


def test_simple_cli_item(cli_runner: Any) -> None:
    """Simple test to verify CLI mocking works."""
    with patch("tracertm.cli.commands.item.DatabaseConnection"):
        # Mock the session

        # Mock other functions
        with patch("tracertm.cli.commands.item._get_project_storage_path") as mock_path:
            with patch("tracertm.cli.commands.item._load_project_yaml") as mock_yaml:
                with patch("tracertm.cli.commands.item._get_storage_manager"):
                    # Set up basic mocks
                    mock_path.return_value = "/tmp/test"
                    mock_yaml.return_value = {"name": "test-project"}

                    # Test a simple command
                    result = cli_runner.invoke(item_app, ["--help"])
                    assert result.exit_code == 0
                    assert "create" in result.stdout
                    assert "list" in result.stdout
