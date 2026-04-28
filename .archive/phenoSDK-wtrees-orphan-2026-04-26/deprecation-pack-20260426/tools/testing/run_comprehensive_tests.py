#!/usr/bin/env python3
"""Comprehensive Typer-powered test runner for all suites."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import typer

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from pheno.cli.typer_utils import CLIContext, build_context, console
from pheno.logging import configure_structured_logging

app = typer.Typer(help="Run comprehensive pheno-sdk test batteries.")


class ComprehensiveTestRunner:
    """Comprehensive test runner for all test suites."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        self.test_suites = {
            "unit": {
                "path": "tests/unit",
                "markers": ["unit", "fast"],
                "coverage_target": 95.0,
                "timeout": 60,
                "parallel": True,
            },
            "integration": {
                "path": "tests/integration",
                "markers": ["integration"],
                "coverage_target": 85.0,
                "timeout": 300,
                "parallel": False,
            },
            "e2e": {
                "path": "tests/e2e",
                "markers": ["e2e"],
                "coverage_target": 80.0,
                "timeout": 600,
                "parallel": False,
            },
            "security": {
                "path": "tests/security",
                "markers": ["security"],
                "coverage_target": 90.0,
                "timeout": 180,
                "parallel": True,
            },
            "performance": {
                "path": "tests/performance",
                "markers": ["performance"],
                "coverage_target": 70.0,
                "timeout": 1200,
                "parallel": False,
            },
            "contract": {
                "path": "tests/contract",
                "markers": ["contract"],
                "coverage_target": 85.0,
                "timeout": 120,
                "parallel": True,
            },
        }

    def run_all_tests(
        self,
        *,
        parallel: bool = True,
        coverage: bool = True,
        exclude_slow: bool = False,
    ) -> dict[str, Any]:
        console.print("🧪 Running Comprehensive Test Suite...")

        results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "total_suites": len(self.test_suites),
            "suites": {},
            "summary": {},
        }
        suites: dict[str, Any] = results["suites"]  # type: ignore

        total_tests = 0
        total_passed = 0
        total_failed = 0

        for suite_name, config in self.test_suites.items():
            console.print(f"\n📋 Running {suite_name} tests...")

            if exclude_slow and config.get("markers") and "slow" in config["markers"]:
                console.print(f"⏭️  Skipping {suite_name} (slow tests excluded)")
                continue

            suite_result = self._run_test_suite(suite_name, config, parallel, coverage)
            suites[suite_name] = suite_result

            total_tests += suite_result.get("total_tests", 0)
            total_passed += suite_result.get("passed", 0)
            total_failed += suite_result.get("failed", 0)

        results["summary"] = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": (total_passed / total_tests * 100)
            if total_tests > 0
            else 0,
            "overall_success": total_failed == 0,
        }

        self._save_results(results)
        return results

    def run_specific_suite(
        self,
        suite_name: str,
        *,
        parallel: bool = True,
        coverage: bool = True,
    ) -> dict[str, Any]:
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}")

        config = self.test_suites[suite_name]
        return self._run_test_suite(suite_name, config, parallel, coverage)

    def run_fast_tests_only(self) -> dict[str, Any]:
        console.print("⚡ Running Fast Tests Only...")

        fast_suites = {
            name: config
            for name, config in self.test_suites.items()
            if "fast" in config.get("markers", [])
        }

        results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "mode": "fast_only",
            "suites": {},
        }

        for suite_name, config in fast_suites.items():
            console.print(f"📋 Running {suite_name} tests...")
            suite_result = self._run_test_suite(suite_name, config, True, True)
            results["suites"][suite_name] = suite_result

        return results

    def _run_test_suite(
        self,
        suite_name: str,
        config: dict[str, Any],
        parallel: bool,
        coverage: bool,
    ) -> dict[str, Any]:
        suite_path = self.project_root / config["path"]

        if not suite_path.exists():
            return {
                "exists": False,
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "success": True,
                "message": "Test directory does not exist",
            }

        cmd = ["python", "-m", "pytest", str(suite_path), "-v", "--tb=short"]

        if parallel and config.get("parallel", True):
            cmd.extend(["-n", "auto"])

        if coverage:
            cmd.extend(
                [
                    "--cov=src",
                    "--cov-report=html:htmlcov",
                    "--cov-report=xml:coverage.xml",
                    "--cov-report=json:coverage.json",
                    f"--cov-fail-under={config.get('coverage_target', 80)}",
                ],
            )

        markers = config.get("markers", [])
        if markers:
            marker_str = " or ".join(markers)
            cmd.extend(["-m", marker_str])

        cmd.extend(
            [
                f"--html=reports/{suite_name}-report.html",
                "--self-contained-html",
                f"--junitxml=reports/{suite_name}-junit.xml",
            ],
        )

        timeout = config.get("timeout", 300)
        cmd.extend(["--timeout", str(timeout)])

        try:
            console.print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=timeout + 60,
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Timed out",
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
            }

        suite_result = {
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }

        suite_result.update(self._extract_test_stats(result.stdout))
        return suite_result

    def _extract_test_stats(self, output: str) -> dict[str, Any]:
        total_tests = 0
        passed = 0
        failed = 0

        for line in output.splitlines():
            if "passed" in line and "failed" in line and "seconds" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        passed = int(parts[i - 1])
                    elif part == "failed":
                        failed = int(parts[i - 1])
                    elif part == "deselected":
                        total_tests += int(parts[i - 1])
                total_tests += passed + failed

        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
        }

    def _save_results(self, results: dict[str, Any]) -> None:
        report_file = self.reports_dir / "comprehensive-test-report.json"
        report_file.write_text(json.dumps(results, indent=2))
        console.print(f"\n📝 Report saved to {report_file}")


def _print_summary(result: dict[str, Any]) -> None:
    summary = result.get("summary") or {}
    if not summary:
        return
    console.print("\n[bold]Summary[/bold]")
    for key, value in summary.items():
        console.print(f"  • {key}: {value}")


@app.command("run")
def run_command(
    suite: str | None = typer.Option(
        None, "--suite", "-s", help="Run only the specified suite",
    ),
    fast_only: bool = typer.Option(
        False, "--fast-only", help="Run only fast-tagged suites",
    ),
    parallel: bool = typer.Option(
        True, "--parallel/--sequential", help="Enable pytest-xdist",
    ),
    coverage: bool = typer.Option(
        True, "--coverage/--no-coverage", help="Collect coverage",
    ),
    exclude_slow: bool = typer.Option(
        False, "--exclude-slow", help="Skip suites tagged slow",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON summary"),
    project_root: Path = typer.Option(
        Path.cwd(),
        "--project-root",
        help="Project root directory",
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
    ),
    env: str = typer.Option("local", "--env", help="Environment label"),
    target: str = typer.Option("local", "--target", help="Deployment target"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview actions without executing",
    ),
) -> None:
    """Run comprehensive tests across suites."""

    ctx: CLIContext = build_context(
        project_root=project_root,
        env=env,
        target=target,
        verbose=verbose,
        dry_run=dry_run,
    )
    configure_structured_logging(style="json", level="DEBUG" if verbose else "INFO")

    runner = ComprehensiveTestRunner(str(ctx.project_root))

    if suite:
        result = runner.run_specific_suite(suite, parallel=parallel, coverage=coverage)
    elif fast_only:
        result = runner.run_fast_tests_only()
    else:
        result = runner.run_all_tests(
            parallel=parallel, coverage=coverage, exclude_slow=exclude_slow,
        )

    if json_output:
        typer.echo(json.dumps(result, indent=2))
    else:
        _print_summary(result)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
