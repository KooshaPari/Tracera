from typing import Any

"""E2E-style search/drill flows with storage fakes to hit edge branches."""

import contextlib
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from tracertm.cli.app import app

runner = CliRunner()


def _storage_with_no_results() -> None:
    class _DummySession:
        def query(self, *_args: Any, **_kwargs: Any) -> None:
            return self

        def filter(self, *_args: Any, **_kwargs: Any) -> None:
            return self

        def limit(self, _n: Any) -> None:
            return self

        def all(self) -> None:
            return []

    class _Storage:
        def get_session(self) -> None:
            @contextlib.contextmanager
            def _ctx() -> None:
                yield _DummySession()

            return _ctx()

    return _Storage()


def _storage_with_items() -> None:
    class _DummySession:
        def query(self, *_args: Any, **_kwargs: Any) -> None:
            return self

        def filter(self, *_args: Any, **_kwargs: Any) -> None:
            return self

        def limit(self, _n: Any) -> None:
            return self

        def all(self) -> None:
            return [
                SimpleNamespace(
                    id="item-1",
                    title="Login flow",
                    description="",
                    view="FEATURE",
                    item_type="feature",
                    status="todo",
                ),
            ]

    class _Storage:
        def get_session(self) -> None:
            @contextlib.contextmanager
            def _ctx() -> None:
                yield _DummySession()

            return _ctx()

    return _Storage()


@pytest.mark.e2e
def test_search_no_results_shows_message() -> None:
    with (
        patch("tracertm.cli.commands.search.ConfigManager") as cfg,
        patch("tracertm.cli.commands.search._get_storage_manager", return_value=_storage_with_no_results()),
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.return_value = "proj-1"
        cfg.return_value = cfg_inst

        result = runner.invoke(app, ["search", "missing"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "No items found" in result.stdout


@pytest.mark.e2e
def test_search_fuzzy_invalid_date_handling() -> None:
    with (
        patch("tracertm.cli.commands.search.ConfigManager") as cfg,
        patch("tracertm.cli.commands.search._get_storage_manager", return_value=_storage_with_items()),
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.return_value = "proj-1"
        cfg.return_value = cfg_inst

        result = runner.invoke(
            app,
            ["search", "login", "--fuzzy", "--created-after", "not-a-date"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert "Search Results" in result.stdout


@pytest.mark.e2e
def test_search_with_date_filters_parses_iso() -> None:
    with (
        patch("tracertm.cli.commands.search.ConfigManager") as cfg,
        patch("tracertm.cli.commands.search._get_storage_manager", return_value=_storage_with_items()),
    ):
        cfg_inst = MagicMock()
        cfg_inst.get.return_value = "proj-1"
        cfg.return_value = cfg_inst

        result = runner.invoke(
            app,
            ["search", "login", "--created-after", "2025-01-02T00:00:00Z", "--updated-before", "2025-02-01"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    assert "Search Results" in result.stdout
