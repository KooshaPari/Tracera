"""E2E-style sync flows using a fake sync engine (no network/db)."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from tracertm.cli.app import app
from tracertm.storage.sync_engine import SyncResult, SyncState, SyncStatus

runner = CliRunner()


class _FakeSyncEngine:
    def __init__(self) -> None:
        self.state = SyncState(status=SyncStatus.SUCCESS, pending_changes=2, conflicts_count=1)

    async def sync(self, _force: bool = False) -> None:
        return SyncResult(
            success=True,
            entities_synced=3,
            conflicts=[{"entity_type": "item", "entity_id": "item-1"}],
            errors=[],
            duration_seconds=0.4,
        )

    def get_status(self) -> None:
        return self.state


@pytest.mark.e2e
def test_sync_dry_run_shows_conflicts() -> None:
    fake_engine = _FakeSyncEngine()
    with patch("tracertm.cli.commands.sync._get_sync_engine", return_value=fake_engine):
        result = runner.invoke(app, ["sync", "sync", "--dry-run"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Conflicts" in result.stdout or "conflicts" in result.stdout
    assert "Entities synced" in result.stdout


@pytest.mark.e2e
def test_sync_status_online() -> None:
    fake_engine = _FakeSyncEngine()
    with (
        patch("tracertm.cli.commands.sync._get_sync_engine", return_value=fake_engine),
        patch("tracertm.cli.commands.sync._check_online_status", return_value=(True, "[green]Online[/green]")),
    ):
        result = runner.invoke(app, ["sync", "status"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Online" in result.stdout
    assert "Pending local changes" in result.stdout or "Pending changes" in result.stdout


@pytest.mark.e2e
def test_sync_force_success() -> None:
    fake_engine = _FakeSyncEngine()
    with patch("tracertm.cli.commands.sync._get_sync_engine", return_value=fake_engine):
        result = runner.invoke(app, ["sync", "sync", "--force"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "Sync completed successfully" in result.stdout


@pytest.mark.e2e
def test_sync_failure_path() -> None:
    class _FailEngine(_FakeSyncEngine):
        async def sync(self, _force: bool = False) -> None:
            return SyncResult(success=False, entities_synced=0, conflicts=[], errors=["boom"], duration_seconds=0.1)

    with patch("tracertm.cli.commands.sync._get_sync_engine", return_value=_FailEngine()):
        result = runner.invoke(app, ["sync", "sync"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "Sync failed" in result.stdout or "Errors" in result.stdout


@pytest.mark.e2e
def test_sync_status_offline_shows_message() -> None:
    fake_engine = _FakeSyncEngine()
    with (
        patch("tracertm.cli.commands.sync._get_sync_engine", return_value=fake_engine),
        patch(
            "tracertm.cli.commands.sync._check_online_status",
            return_value=(False, "[red]Offline[/red] (timeout...)"),
        ),
    ):
        result = runner.invoke(app, ["sync", "status"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Offline" in result.stdout
