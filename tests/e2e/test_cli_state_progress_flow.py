"""E2E-like flows for state/progress commands with lightweight fakes."""

import contextlib
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from tracertm.cli.app import app

runner = CliRunner()


class _DummySession:
    def __init__(self):
        self._last_model = None
        self._filter_view = None
        self._items = [
            MagicMock(id="item-1", title="Login", status="todo", view="FEATURE", version=1),
            MagicMock(id="item-2", title="API", status="doing", view="FEATURE", version=2),
        ]
        self._links = [MagicMock(project_id="proj-1")]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    # SQLAlchemy-like chain
    def query(self, model):
        self._last_model = getattr(model, "__name__", str(model))
        return self

    def filter(self, *args, **kwargs):
        # capture view filter if passed
        for arg in args:
            if hasattr(arg, "right") and hasattr(arg, "left") and hasattr(arg.left, "name"):
                self._filter_view = arg.right.value if hasattr(arg.right, "value") else None
        return self

    def first(self):
        if self._last_model == "Project":
            return MagicMock(id="proj-1", name="Project One", description="desc", created_at=None, updated_at=None)
        return None

    def all(self):
        if "Item" in str(self._last_model):
            return self._items
        if "Link" in str(self._last_model):
            return self._links
        # for distinct status/view queries return tuples
        if self._last_model is None:
            return []
        return []

    def count(self):
        if "Link" in str(self._last_model):
            return len(self._links)
        return len(self._items)


def _storage_session_ctx():
    @contextlib.contextmanager
    def _ctx():
        yield _DummySession()

    return _ctx()


@pytest.mark.e2e
def test_state_show_with_view():
    with (
        patch("tracertm.cli.commands.state.ConfigManager") as cfg,
        patch("tracertm.cli.commands.state.DatabaseConnection") as db,
        patch("tracertm.cli.commands.state.Session", return_value=_DummySession()),
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.side_effect = lambda key: "proj-1" if key == "current_project_id" else "sqlite:///tmp.db"
        cfg.return_value = cfg_inst
        db.return_value = MagicMock(engine=MagicMock())

        result = runner.invoke(app, ["state", "--view", "FEATURE"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Project State" in result.stdout
    assert "Total Items" in result.stdout


@pytest.mark.e2e
def test_progress_show_overall():
    with (
        patch("tracertm.cli.commands.progress.ConfigManager") as cfg,
        patch("tracertm.cli.commands.progress._get_storage_manager") as sm,
        patch("tracertm.cli.commands.progress.ProgressService") as ps,
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.side_effect = lambda key: "proj-1" if key == "current_project_id" else None
        cfg.return_value = cfg_inst

        storage = MagicMock()
        storage.get_session.return_value = _storage_session_ctx()
        sm.return_value = storage

        ps_inst = MagicMock()
        ps_inst.calculate_completion.side_effect = [50.0, 100.0]
        ps.return_value = ps_inst

        result = runner.invoke(app, ["progress", "show"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Project Progress" in result.stdout
    assert "Total Items" in result.stdout
    assert "Average Completion" in result.stdout


@pytest.mark.e2e
def test_state_missing_project_exits():
    with patch("tracertm.cli.commands.state.ConfigManager") as cfg:
        cfg_inst = MagicMock()
        cfg_inst.get.return_value = None  # no current project id
        cfg.return_value = cfg_inst

        result = runner.invoke(app, ["state"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "project" in result.stdout.lower()


@pytest.mark.e2e
def test_progress_item_not_found():
    with (
        patch("tracertm.cli.commands.progress.ConfigManager") as cfg,
        patch("tracertm.cli.commands.progress._get_storage_manager") as sm,
        patch("tracertm.cli.commands.progress.ProgressService") as ps,
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.side_effect = lambda key: "proj-1" if key == "current_project_id" else None
        cfg.return_value = cfg_inst

        storage = MagicMock()
        storage.get_session.return_value = _storage_session_ctx()
        sm.return_value = storage

        ps.return_value = MagicMock()

        result = runner.invoke(app, ["progress", "show", "--item", "missing"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "Item not found" in result.stdout


@pytest.mark.e2e
def test_progress_view_branch():
    with (
        patch("tracertm.cli.commands.progress.ConfigManager") as cfg,
        patch("tracertm.cli.commands.progress._get_storage_manager") as sm,
        patch("tracertm.cli.commands.progress.ProgressService") as ps,
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.side_effect = lambda key: "proj-1" if key == "current_project_id" else None
        cfg.return_value = cfg_inst

        storage = MagicMock()
        storage.get_session.return_value = _storage_session_ctx()
        sm.return_value = storage

        ps_inst = MagicMock()
        ps_inst.calculate_completion.side_effect = [40.0, 80.0]
        ps.return_value = ps_inst

        result = runner.invoke(app, ["progress", "show", "--view", "FEATURE"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Items:" in result.stdout
    assert "Average Completion" in result.stdout
