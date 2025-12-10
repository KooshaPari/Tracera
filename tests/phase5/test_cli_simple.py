"""
Simple CLI test to verify mocking approach works.
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from tracertm.cli.commands.item import app as item_app

@pytest.fixture
def cli_runner():
    return CliRunner()

def test_simple_cli_item(cli_runner):
    """Simple test to verify CLI mocking works."""
    with patch("tracertm.cli.commands.item.DatabaseConnection") as mock_db:
        # Mock the session
        mock_session = mock_db.return_value.get_session.return_value
        
        # Mock other functions
        with patch("tracertm.cli.commands.item._get_project_storage_path") as mock_path:
            with patch("tracertm.cli.commands.item._load_project_yaml") as mock_yaml:
                with patch("tracertm.cli.commands.item._get_storage_manager") as mock_storage:
                    # Set up basic mocks
                    mock_path.return_value = "/tmp/test"
                    mock_yaml.return_value = {"name": "test-project"}
                    
                    # Test a simple command
                    result = cli_runner.invoke(item_app, ["--help"])
                    assert result.exit_code == 0
                    assert "create" in result.stdout
                    assert "list" in result.stdout
