"""Lightweight integration smoke tests for the CLI query command.

These ensure the command is discoverable and help text renders without requiring
real database connections (coverage for wiring only).
"""

from typing import Any

import pytest
from typer.testing import CliRunner

from tracertm.cli.app import app

pytestmark = pytest.mark.integration


@pytest.fixture
def runner() -> None:
    return CliRunner()


def test_query_help(runner: Any) -> None:
    result = runner.invoke(app, ["query", "--help"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "query" in result.stdout.lower()


def test_query_help_filters_section(runner: Any) -> None:
    result = runner.invoke(app, ["query", "--help"], catch_exceptions=False)
    assert "--filter" in result.stdout


def test_query_help_json_flag(runner: Any) -> None:
    result = runner.invoke(app, ["query", "--help"], catch_exceptions=False)
    assert "--json" in result.stdout
