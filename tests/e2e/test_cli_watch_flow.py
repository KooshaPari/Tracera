"""Watch command error/success branches without running a real loop."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from tracertm.cli.app import app

runner = CliRunner()


@pytest.mark.e2e
def test_watch_init_failure() -> None:
    with patch("tracertm.cli.commands.watch.LocalStorageManager", side_effect=RuntimeError("boom")):
        result = runner.invoke(app, ["watch", "--path", str(Path.cwd())], catch_exceptions=False)
    assert result.exit_code != 0
    assert "Failed to initialize file watcher" in result.stdout


@pytest.mark.e2e
def test_watch_start_failure() -> None:
    fake_storage = MagicMock()
    fake_watcher = MagicMock()
    fake_watcher.start.side_effect = RuntimeError("cannot start")

    with (
        patch("tracertm.cli.commands.watch.LocalStorageManager", return_value=fake_storage),
        patch("tracertm.cli.commands.watch.TraceFileWatcher", return_value=fake_watcher),
    ):
        result = runner.invoke(app, ["watch", "--path", str(Path.cwd())], catch_exceptions=False)

    assert result.exit_code != 0
    assert "Failed to start file watcher" in result.stdout
