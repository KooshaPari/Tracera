from typing import Any

"""Backup/restore flow exercising error and success branches with fakes."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from tracertm.cli.app import app

runner = CliRunner()


@pytest.mark.e2e
def test_backup_restore_success(tmp_path: Any) -> None:
    backup_path = tmp_path / "backup.json"
    with (
        patch("tracertm.cli.commands.backup.ConfigManager") as cfg,
        patch("tracertm.cli.commands.backup.DatabaseConnection") as db,
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.side_effect = lambda key: "proj-1" if key == "current_project_id" else "sqlite:///tmp.db"
        cfg.return_value = cfg_inst

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        db.return_value = mock_db

        res_backup = runner.invoke(
            app,
            ["backup", "backup", "--output", str(backup_path), "--no-compress", "--project-id", "proj-1"],
            catch_exceptions=False,
        )
        res_restore = runner.invoke(app, ["backup", "restore", str(backup_path), "--force"], catch_exceptions=False)

    assert res_backup.exit_code == 0
    assert res_restore.exit_code == 0


@pytest.mark.e2e
def test_backup_missing_project_fails(tmp_path: Any) -> None:
    with (
        patch("tracertm.cli.commands.backup.ConfigManager") as cfg,
        patch("tracertm.cli.commands.backup.DatabaseConnection") as db,
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.return_value = None  # no current_project_id
        cfg.return_value = cfg_inst
        db.return_value = MagicMock()

        res_backup = runner.invoke(
            app,
            ["backup", "backup", "--output", str(tmp_path / "out.json"), "--no-compress"],
            catch_exceptions=False,
        )

    assert res_backup.exit_code != 0
    assert "database" in res_backup.stdout.lower()


@pytest.mark.e2e
def test_backup_restore_corrupt_file(tmp_path: Any) -> None:
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{not-json")

    with (
        patch("tracertm.cli.commands.backup.ConfigManager") as cfg,
        patch("tracertm.cli.commands.backup.DatabaseConnection") as db,
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.side_effect = lambda key: "proj-1" if key == "current_project_id" else "sqlite:///tmp.db"
        cfg.return_value = cfg_inst
        db.return_value = MagicMock()

        res_restore = runner.invoke(app, ["backup", "restore", str(corrupt), "--force"], catch_exceptions=False)

    assert res_restore.exit_code != 0
    assert "Restore failed" in res_restore.stdout or "Failed to load" in res_restore.stdout
