#!/usr/bin/env python3
"""Deployment readiness checker (Typer-based)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from lib.deployment_checker import CheckPriority, ReadinessChecker

app = typer.Typer(help="Run deployment readiness checks for ATOMS-PHENO")


def _resolve_priorities(values: list[str] | None) -> list[CheckPriority] | None:
    if not values:
        return None
    mapping = {
        "critical": CheckPriority.CRITICAL,
        "high": CheckPriority.HIGH,
        "medium": CheckPriority.MEDIUM,
        "low": CheckPriority.LOW,
    }
    resolved: list[CheckPriority] = []
    for value in values:
        key = value.lower()
        if key not in mapping:
            raise typer.BadParameter(
                "Priority must be one of: critical, high, medium, low",
            )
        resolved.append(mapping[key])
    return resolved


def _resolve_format(value: str) -> str:
    allowed = {"json", "markdown", "text"}
    key = value.lower()
    if key not in allowed:
        raise typer.BadParameter("Format must be json, markdown, or text")
    return key


@app.command("check")
def run_checks(
    output_format: str = typer.Option("text", "--format", help="Report format"),
    priority: list[str] | None = typer.Option(
        None,
        "--priority",
        help="Check priorities to run (repeatable)",
    ),
    check: str | None = typer.Option(None, "--check", help="Run a single check"),
    list_checks: bool = typer.Option(
        False, "--list-checks", help="List available checks",
    ),
    parallel: bool = typer.Option(
        True, "--parallel/--no-parallel", help="Run checks in parallel",
    ),
    sequential: bool = typer.Option(
        False, "--sequential", help="Force sequential execution",
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output-file",
        help="Write report to this file",
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    project_dir: Path | None = typer.Option(
        None,
        "--project-dir",
        help="Project directory (defaults to current working directory)",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    fail_on_warning: bool = typer.Option(
        False,
        "--fail-on-warning",
        help="Exit non-zero if warnings are present",
    ),
):
    """Run deployment readiness checks."""

    fmt = _resolve_format(output_format)
    priorities = _resolve_priorities(priority)
    root = project_dir or Path.cwd()
    checker = ReadinessChecker(str(root))

    if list_checks:
        available_checks = list(checker._check_registry.keys())
        typer.echo("Available deployment readiness checks:")
        for idx, name in enumerate(available_checks, 1):
            typer.echo(f"  {idx:2d}. {name}")
        raise typer.Exit(code=0)

    run_parallel = parallel and not sequential

    if check:
        result = checker.run_check(check)
        results = [result] if result else []
    else:
        results = checker.run_all_checks(priorities=priorities, parallel=run_parallel)

    if not isinstance(results, list):
        results = []

    report_payload = fmt if fmt != "text" else "json"
    report = checker.generate_report(results, format=report_payload)

    if output_file:
        output_file.write_text(report)
        typer.echo(f"Deployment readiness report written to {output_file}")
    elif fmt == "markdown":
        typer.echo(report)
    elif fmt == "json":
        typer.echo(json.dumps(json.loads(report), indent=2))
    else:
        typer.echo("🚀 ATOMS-PHENO Deployment Readiness Check")
        typer.echo("=" * 50)

        total_checks = len(results)
        passed = sum(1 for r in results if r.status.value.lower() == "passed")
        failed = sum(1 for r in results if r.status.value.lower() == "failed")
        warnings_count = sum(1 for r in results if r.status.value.lower() == "warning")

        typer.echo(f"Total Checks: {total_checks}")
        typer.echo(f"✅ Passed: {passed}")
        typer.echo(f"❌ Failed: {failed}")
        typer.echo(f"⚠️  Warnings: {warnings_count}")

        readiness_score = (passed / total_checks * 100) if total_checks else 0
        typer.echo(f"📊 Readiness Score: {readiness_score:.1f}%")

        critical_failures = sum(
            1
            for r in results
            if r.priority == CheckPriority.CRITICAL
            and r.status.value.lower() == "failed"
        )

        typer.echo(
            "\n🎉 DEPLOYMENT READY"
            if critical_failures == 0
            else f"\n🚫 DEPLOYMENT BLOCKED ({critical_failures} critical failures)",
        )

        typer.echo("\nDetailed Results:")
        typer.echo("-" * 30)

        for result in results:
            status_emoji = {
                "passed": "✅",
                "failed": "❌",
                "warning": "⚠️",
                "error": "🚨",
                "skipped": "⏭️",
            }.get(result.status.value.lower(), "❓")

            priority_badge = result.priority.value.upper()
            typer.echo(f"{status_emoji} {result.name} [{priority_badge}]")
            typer.echo(f"   {result.message}")

            if result.details:
                for key, value in result.details.items():
                    typer.echo(f"   {key}: {value}")

            if result.duration > 0:
                typer.echo(f"   Duration: {result.duration:.2f}s")
            typer.echo("")

    if fail_on_warning:
        has_issues = any(
            r.status.value.lower() in {"failed", "warning", "error"} for r in results
        )
    else:
        has_issues = any(
            r.priority == CheckPriority.CRITICAL and r.status.value.lower() == "failed"
            for r in results
        )

    raise typer.Exit(code=1 if has_issues else 0)


if __name__ == "__main__":  # pragma: no cover
    app()
