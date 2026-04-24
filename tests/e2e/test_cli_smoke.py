from typing import Any

"""Smoke-level E2E checks for the CLI happy path."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from tracertm.cli.app import app

runner = CliRunner()


@pytest.mark.e2e
@pytest.mark.smoke
class TestCliSmoke:
    @patch("tracertm.cli.commands.config.ConfigManager")
    @patch("tracertm.cli.commands.project.DatabaseConnection")
    @patch("tracertm.database.connection.DatabaseConnection")
    def test_config_project_db_status(self, mock_db_class: Any, mock_project_db: Any, mock_config_class: Any) -> None:
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///smoke.db"
        mock_config.config_path = Path("/tmp/test_config.json")
        mock_config_class.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db.health_check.return_value = {"status": "connected", "version": "SQLite"}
        mock_db_class.return_value = mock_db
        mock_project_db.return_value = mock_db

        result1 = runner.invoke(app, ["config", "init", "--database-url", "sqlite:///smoke.db"], catch_exceptions=False)
        result2 = runner.invoke(
            app,
            ["project", "init", "Smoke Project", "--description", "Smoke"],
            catch_exceptions=False,
        )
        result3 = runner.invoke(app, ["db", "status"], catch_exceptions=False)

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert result3.exit_code == 0
