"""Feature: general

Feature: general

Smoke tests for the Typer-based deployment checker CLI."""

from typer.testing import CliRunner

from scripts.categories.deployment import check_deployment

runner = CliRunner()


def test_list_checks_runs_successfully():
    result = runner.invoke(check_deployment.app, ["--list-checks"])
    assert result.exit_code == 0
    assert "Available deployment readiness checks" in result.stdout
