from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import MagicMock

from click.testing import CliRunner

from pheno.infra.cli.project_cli import project_cli


class DummyProgress:
    def __init__(self):
        self.updates = []
        self.succeeded = []
        self.failed = []

    def update(self, message: str) -> None:
        self.updates.append(message)

    def succeed(self, message: str | None = None) -> None:
        self.succeeded.append(message)

    def fail(self, message: str | None = None) -> None:
        self.failed.append(message)


def _patch_project_context(monkeypatch):
    ctx_mock = MagicMock()
    ctx_mock.enable_maintenance = MagicMock()
    ctx_mock.disable_maintenance = MagicMock()
    ctx_mock.update_fallback_content = MagicMock()

    @contextmanager
    def _fake_context(*args, **kwargs):
        yield ctx_mock

    monkeypatch.setattr("pheno.infra.cli.project_cli.project_infra_context", _fake_context)
    return ctx_mock


def _patch_progress_helper(monkeypatch):
    calls: list[str] = []

    @contextmanager
    def _fake_progress(message: str, **_: object):
        calls.append(message)
        yield DummyProgress()

    monkeypatch.setattr("pheno.infra.cli.project_cli.progress_step", _fake_progress)
    return calls


def test_enable_maintenance_command_invokes_context(monkeypatch):
    progress_calls = _patch_progress_helper(monkeypatch)
    ctx_mock = _patch_project_context(monkeypatch)
    runner = CliRunner()

    result = runner.invoke(
        project_cli,
        [
            "demo-project",
            "enable-maintenance",
            "--message",
            "Scheduled work",
            "--duration",
            "45m",
            "--contact",
            "ops@example.com",
            "--page-type",
            "maintenance",
        ],
    )

    assert result.exit_code == 0
    ctx_mock.enable_maintenance.assert_called_once_with(
        message="Scheduled work",
        estimated_duration="45m",
        contact_info="ops@example.com",
        page_type="maintenance",
    )
    assert progress_calls == ["Enabling maintenance banner for 'demo-project'"]


def test_disable_maintenance_command_invokes_context(monkeypatch):
    progress_calls = _patch_progress_helper(monkeypatch)
    ctx_mock = _patch_project_context(monkeypatch)
    runner = CliRunner()

    result = runner.invoke(project_cli, ["demo-project", "disable-maintenance"])

    assert result.exit_code == 0
    ctx_mock.disable_maintenance.assert_called_once_with()
    assert progress_calls == ["Disabling maintenance banner for 'demo-project'"]


def test_update_fallback_content_command_invokes_context(monkeypatch):
    progress_calls = _patch_progress_helper(monkeypatch)
    ctx_mock = _patch_project_context(monkeypatch)
    runner = CliRunner()

    result = runner.invoke(
        project_cli,
        [
            "demo-project",
            "update-fallback-content",
            "--page-type",
            "loading",
            "--message",
            "Booting up",
            "--duration",
            "3m",
            "--contact",
            "ops@example.com",
        ],
    )

    assert result.exit_code == 0
    ctx_mock.update_fallback_content.assert_called_once_with(
        page_type="loading",
        message="Booting up",
        estimated_duration="3m",
        contact_info="ops@example.com",
    )
    assert progress_calls == ["Updating fallback content for page 'loading'"]


def test_progress_step_falls_back_without_rich(monkeypatch, capsys):
    from pheno.infra.cli import progress as progress_module

    monkeypatch.setattr(progress_module, "_RICH_AVAILABLE", False)
    monkeypatch.setattr(progress_module, "Progress", None)
    monkeypatch.setattr(progress_module, "SpinnerColumn", None)
    monkeypatch.setattr(progress_module, "TextColumn", None)
    monkeypatch.setattr(progress_module, "_CONSOLE", None)

    with progress_module.progress_step("Allocating ports") as reporter:
        reporter.update("Allocating ports for test")

    output = capsys.readouterr().out
    assert "Allocating ports..." in output
    assert "Allocating ports for test..." in output
    assert "Allocating ports done" in output
