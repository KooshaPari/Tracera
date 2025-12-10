"""
Unified test command for TraceRTM.

Aggregates tests across Python, Go, and TypeScript with domain/functional
grouping, dependency-aware staging, and traceability matrix reporting.

Inspired by atoms-mcp-prod/cli.py test command patterns.

Usage:
    rtm test                          # Run all tests (unit + integration + e2e, local, parallel)
    rtm test --scope unit             # Unit tests only (local, parallel)
    rtm test --scope integration      # Integration tests (dev, parallel)
    rtm test --scope e2e              # E2E tests (dev, parallel)
    rtm test --parallel               # Dependency-ordered stages
    rtm test --env local              # Override environment
    rtm test --coverage               # Generate coverage
    rtm test --matrix                 # Generate traceability matrix
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from tracertm.cli.commands.test.env_manager import TestEnvironment, TestEnvManager
from tracertm.cli.commands.test.orchestrator import TestOrchestrator

app = typer.Typer(
    name="test",
    help="Run tests across all languages with unified interface",
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
)

console = Console()


@app.command()
def test(
    scope: Optional[str] = typer.Option(
        None,
        "--scope",
        help="Test scope: unit, integration, or e2e (if omitted, runs all tests)",
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
    coverage: bool = typer.Option(False, "--cov", help="Generate coverage report"),
    marker: Optional[str] = typer.Option(
        None, "-m", "--marker", help="Run specific marker (e.g., 'unit', 'story')"
    ),
    keyword: Optional[str] = typer.Option(
        None, "-k", "--keyword", help="Run tests matching keyword"
    ),
    env: Optional[str] = typer.Option(
        None,
        "--env",
        help="Environment: local, dev, or prod (auto-detected if not specified)",
    ),
    parallel: bool = typer.Option(
        False, "--parallel", help="Run dependency-ordered stages with pytest-xdist"
    ),
    no_parallel: bool = typer.Option(
        False,
        "--no-parallel",
        help="Disable pytest-xdist parallelization (default: enabled)",
    ),
    max_workers: Optional[int] = typer.Option(
        None, "--max-workers", help="Override pytest-xdist worker count (default: auto)"
    ),
    last_failed: bool = typer.Option(
        False, "--lf", "--last-failed", help="Rerun only the tests that failed at the last run"
    ),
    failed_first: bool = typer.Option(
        False,
        "--ff",
        "--failed-first",
        help="Run all tests, but run the last failures first",
    ),
    cache_clear: bool = typer.Option(
        False, "--cache-clear", help="Clear pytest cache before running tests"
    ),
    domain: Optional[str] = typer.Option(
        None, "--domain", "-d", help="Filter by domain (e.g., 'services', 'api')"
    ),
    epic: Optional[str] = typer.Option(
        None, "--epic", "-e", help="Filter by epic (e.g., 'Epic 1: Core Requirements')"
    ),
    story: Optional[str] = typer.Option(
        None, "--story", "-s", help="Filter by user story"
    ),
    function: Optional[str] = typer.Option(
        None, "--function", "-f", help="Filter by function (e.g., 'crud', 'query')"
    ),
) -> None:
    """Run the test suite with automatic environment targeting.

    Tests run in parallel by default using pytest-xdist. Use --no-parallel to disable.

    The CLI automatically targets the correct environment:
    - no scope → all tests (unit + integration + e2e, local)
    - --scope unit → unit tests only (local, no deployment needed)
    - --scope integration → integration tests (dev by default, or local)
    - --scope e2e → e2e tests (dev by default, or prod)
    - --scope all → explicitly run all tests without marker filtering

    Examples:
        rtm test                          # Run all tests without deselection (local, parallel)
        rtm test --scope unit             # Unit tests only (local, parallel)
        rtm test --scope all --env local  # All tests locally (unit + integration + e2e, parallel)
        rtm test --scope integration      # Integration tests (dev, parallel)
        rtm test --scope e2e              # E2E tests (dev, parallel)
        rtm test --scope e2e --env prod   # E2E tests against production (parallel)
        rtm test --scope unit -v          # Verbose unit tests (parallel)
        rtm test --scope integration --env local  # Integration against local server (parallel)
        rtm test -v --cov                 # All tests with coverage and verbose (parallel)
        rtm test --no-parallel            # Disable parallelization
        rtm test --max-workers 4         # Use 4 workers instead of auto
        rtm test --parallel               # Use dependency-ordered stages (different from default)
        rtm test --lf                     # Rerun only failed tests from last run
        rtm test --ff                     # Run failed tests first, then rest
        rtm test --cache-clear            # Clear cache before running
        rtm test --domain services        # Filter by domain
        rtm test --epic "Epic 1"          # Filter by epic
    """
    # Determine environment
    if env:
        try:
            environment = TestEnvironment.from_string(env)
        except ValueError as e:
            console.print(f"[red]❌ {e}[/red]")
            sys.exit(1)
    else:
        # Auto-detect based on scope (if provided)
        # If no scope, default to local for all tests
        if scope:
            environment = TestEnvManager.get_environment_for_scope(scope)
        else:
            environment = TestEnvironment.LOCAL

    # Set up environment variables
    TestEnvManager.setup_environment(environment)

    # Print environment info
    TestEnvManager.print_environment_info(environment)

    # When targeting remote deployments (dev/prod), no local server lifecycle management
    if environment != TestEnvironment.LOCAL:
        console.print(
            "\n[green]✅ Targeting remote deployment - no local server will be started[/green]"
        )
        console.print("   Tests will run against the remote deployment URL\n")

    if parallel:
        if scope:
            console.print(
                "[yellow]⚠️ --parallel runs the full suite. Remove --scope to continue.[/yellow]"
            )
            sys.exit(1)
        if max_workers is not None and max_workers < 1:
            console.print("[yellow]⚠️ --max-workers must be >= 1[/yellow]")
            sys.exit(1)

        orchestrator = TestOrchestrator(
            verbose=verbose,
            marker=marker,
            keyword=keyword,
            parallel=True,
            max_workers=max_workers,
            coverage=coverage,
        )
        summary = orchestrator.run()
        sys.exit(0 if summary.success else 1)

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    # Enable pytest-xdist parallelization by default (unless --no-parallel is used)
    # Always add parallelization FIRST, before any markers/keywords
    if not no_parallel:
        # Always add the -n flag with auto workers
        # pytest-xdist will be used if available, otherwise pytest will skip this flag gracefully
        worker_count = str(max_workers) if max_workers else "auto"
        cmd.extend(["-n", worker_count])

    if verbose:
        cmd.append("-v")
    if coverage:
        cmd.extend(["--cov=src/tracertm", "--cov-report=html", "--cov-report=term"])

    # Add marker based on scope or marker option
    if marker:
        cmd.extend(["-m", marker])
    elif scope == "all":
        # Explicitly run all tests without marker filtering
        pass  # Don't add -m flag to run all tests without filtering
    elif scope and scope in ["unit", "integration", "e2e"]:
        # If scope explicitly provided, use it
        cmd.extend(["-m", scope])
    else:
        # Default: run unit tests only if no scope specified
        cmd.extend(["-m", "unit"])

    if keyword:
        cmd.extend(["-k", keyword])

    # Cache-related options
    if cache_clear:
        cmd.append("--cache-clear")
    if last_failed:
        cmd.append("--lf")
    elif failed_first:
        cmd.append("--ff")

    # Add test path
    cmd.append("tests/")

    # Show what we're running
    console.print(f"\n[bold]🧪 Running tests: {' '.join(cmd[3:])}[/bold]\n")

    # CRITICAL: Pass environment variables explicitly to subprocess
    # This ensures environment variables are available when tests run
    test_env = os.environ.copy()

    # Debug: Log what we're passing to subprocess
    if environment != TestEnvironment.LOCAL:
        console.print("[dim]🔍 DEBUG: Passing to pytest subprocess:[/dim]")
        console.print(f"[dim]   TRACERTM_API_URL={test_env.get('TRACERTM_API_URL')}[/dim]")
        console.print(
            f"[dim]   TRACERTM_INTEGRATION_BASE_URL={test_env.get('TRACERTM_INTEGRATION_BASE_URL')}[/dim]"
        )
        console.print(
            f"[dim]   TRACERTM_E2E_BASE_URL={test_env.get('TRACERTM_E2E_BASE_URL')}[/dim]"
        )

    result = subprocess.run(cmd, env=test_env)

    # Exit with test result code
    sys.exit(result.returncode)


@app.command("test:unit")
def test_unit(
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    no_parallel: bool = typer.Option(
        False,
        "--no-parallel",
        help="Disable pytest-xdist parallelization (default: enabled)",
    ),
    max_workers: Optional[int] = typer.Option(
        None, "--max-workers", help="Override pytest-xdist worker count (default: auto)"
    ),
) -> None:
    """Run unit tests only (fast, no external services).

    Tests run in parallel by default using pytest-xdist. Use --no-parallel to disable.

    Always uses local environment (no deployment needed).

    Examples:
        rtm test:unit -v                  # Verbose, parallel
        rtm test:unit --no-parallel       # Disable parallelization
        rtm test:unit --max-workers 4    # Use 4 workers
    """
    # Unit tests always use local
    environment = TestEnvironment.LOCAL
    TestEnvManager.setup_environment(environment)

    cmd = ["python", "-m", "pytest"]

    # Enable pytest-xdist parallelization by default (unless --no-parallel is used)
    if not no_parallel:
        try:
            import pytest_xdist  # noqa: F401
            worker_count = str(max_workers) if max_workers else "auto"
            cmd.extend(["-n", worker_count])
        except ImportError:
            # xdist not available, skip parallelization
            pass

    if verbose:
        cmd.append("-v")

    cmd.extend(
        [
            "-m",
            "unit",  # Only run tests marked with @pytest.mark.unit
            "--ignore=tests/integration",  # Skip integration tests directory
            "--ignore=tests/e2e",  # Skip e2e tests directory
            "tests/",
        ]
    )

    console.print("[bold]🧪 Running unit tests (local)...[/bold]")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@app.command("test:int")
def test_integration(
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    env: Optional[str] = typer.Option(
        None, "--env", help="Environment: local, dev, or prod"
    ),
    no_parallel: bool = typer.Option(
        False,
        "--no-parallel",
        help="Disable pytest-xdist parallelization (default: enabled)",
    ),
    max_workers: Optional[int] = typer.Option(
        None, "--max-workers", help="Override pytest-xdist worker count (default: auto)"
    ),
) -> None:
    """Run integration tests (requires services).

    Tests run in parallel by default using pytest-xdist. Use --no-parallel to disable.

    Automatically targets dev deployment by default.
    Override with --env local to use local server or --env prod for production.

    Examples:
        rtm test:int                  # Integration tests on dev (parallel)
        rtm test:int -v               # Verbose (parallel)
        rtm test:int --env local      # Against local server (parallel)
        rtm test:int --env prod       # Against production (parallel)
        rtm test:int --no-parallel   # Disable parallelization
        rtm test:int --max-workers 4  # Use 4 workers
    """
    # Determine environment
    if env:
        try:
            environment = TestEnvironment.from_string(env)
        except ValueError as e:
            console.print(f"[red]❌ {e}[/red]")
            sys.exit(1)
    else:
        # Default to dev for integration tests
        environment = TestEnvironment.DEV

    TestEnvManager.setup_environment(environment)
    TestEnvManager.print_environment_info(environment)

    cmd = ["python", "-m", "pytest"]

    # Enable pytest-xdist parallelization by default (unless --no-parallel is used)
    if not no_parallel:
        try:
            import pytest_xdist  # noqa: F401
            worker_count = str(max_workers) if max_workers else "auto"
            cmd.extend(["-n", worker_count])
        except ImportError:
            # xdist not available, skip parallelization
            pass

    if verbose:
        cmd.append("-v")

    cmd.extend(["-m", "integration", "tests/"])

    console.print()
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@app.command("test:e2e")
def test_e2e(
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    env: Optional[str] = typer.Option(
        None, "--env", help="Environment: local, dev, or prod"
    ),
    no_parallel: bool = typer.Option(
        False,
        "--no-parallel",
        help="Disable pytest-xdist parallelization (default: enabled)",
    ),
    max_workers: Optional[int] = typer.Option(
        None, "--max-workers", help="Override pytest-xdist worker count (default: auto)"
    ),
) -> None:
    """Run end-to-end tests (full system).

    Tests run in parallel by default using pytest-xdist. Use --no-parallel to disable.

    Automatically targets dev deployment by default.
    Override with --env local to use local server or --env prod for production.

    Examples:
        rtm test:e2e                  # E2E tests on dev (parallel)
        rtm test:e2e -v               # Verbose (parallel)
        rtm test:e2e --env local      # Against local server (parallel)
        rtm test:e2e --env prod       # Against production (parallel)
        rtm test:e2e --no-parallel    # Disable parallelization
        rtm test:e2e --max-workers 4  # Use 4 workers
    """
    # Determine environment
    if env:
        try:
            environment = TestEnvironment.from_string(env)
        except ValueError as e:
            console.print(f"[red]❌ {e}[/red]")
            sys.exit(1)
    else:
        # Default to dev for e2e tests
        environment = TestEnvironment.DEV

    TestEnvManager.setup_environment(environment)
    TestEnvManager.print_environment_info(environment)

    cmd = ["python", "-m", "pytest"]

    # Enable pytest-xdist parallelization by default (unless --no-parallel is used)
    if not no_parallel:
        try:
            import pytest_xdist  # noqa: F401
            worker_count = str(max_workers) if max_workers else "auto"
            cmd.extend(["-n", worker_count])
        except ImportError:
            # xdist not available, skip parallelization
            pass

    if verbose:
        cmd.append("-v")

    cmd.extend(["-m", "e2e", "tests/"])

    console.print()
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@app.command("test:cov")
def test_coverage() -> None:
    """Run unit tests with coverage report (HTML + terminal).

    Always uses local environment (coverage only for unit tests).

    Output:
        htmlcov/index.html - Interactive coverage report
    """
    # Coverage always uses local + unit tests
    environment = TestEnvironment.LOCAL
    TestEnvManager.setup_environment(environment)

    console.print("[bold]🧪 Running unit tests with coverage...[/bold]")
    result = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "-m",
            "unit",
            "--cov=src/tracertm",
            "--cov-report=html",
            "--cov-report=term-missing",
            "tests/",
        ]
    )
    console.print("\n[green]📊 Coverage report: htmlcov/index.html[/green]")
    sys.exit(result.returncode)


@app.command("test:matrix")
def test_matrix(
    epic: Optional[str] = typer.Option(None, "-e", "--epic", help="Filter by epic name"),
    output: str = typer.Option("html", "--output", "-o", help="Output format: html, json, xml"),
) -> None:
    """Generate traceability matrix linking requirements to tests.

    Examples:
        rtm test:matrix                    # Generate matrix for all requirements
        rtm test:matrix -e "Epic 1"       # Filter by epic
        rtm test:matrix --output json     # JSON output
    """
    import json
    from pathlib import Path

    console.print("[bold]📊 Generating traceability matrix...[/bold]")

    # Discover tests
    from tracertm.cli.commands.test.discovery import TestDiscovery
    discovery = TestDiscovery(Path.cwd())
    tests = discovery.discover()

    # Build traceability matrix
    matrix = {
        "generated": __import__("datetime").datetime.now().isoformat(),
        "epic_filter": epic,
        "total_tests": len(tests),
        "tests_by_language": {},
        "tests_by_scope": {},
        "coverage_summary": {
            "unit": 0,
            "integration": 0,
            "e2e": 0,
            "total": len(tests)
        }
    }

    # Group tests by language and scope
    for test in tests:
        # Count by language
        lang = test.language
        if lang not in matrix["tests_by_language"]:
            matrix["tests_by_language"][lang] = []
        matrix["tests_by_language"][lang].append({
            "path": test.path,
            "language": lang,
        })

        # Count by scope
        scope = "unit"  # Default scope
        if "integration" in test.path:
            scope = "integration"
            matrix["coverage_summary"]["integration"] += 1
        elif "e2e" in test.path or "end_to_end" in test.path:
            scope = "e2e"
            matrix["coverage_summary"]["e2e"] += 1
        else:
            matrix["coverage_summary"]["unit"] += 1

        if scope not in matrix["tests_by_scope"]:
            matrix["tests_by_scope"][scope] = []
        matrix["tests_by_scope"][scope].append(test.path)

    # Filter by epic if provided
    if epic:
        matrix["tests_by_language"] = {
            lang: [t for t in tests if epic.lower() in t.get("path", "").lower()]
            for lang, tests in matrix["tests_by_language"].items()
        }
        matrix["tests_by_scope"] = {
            scope: [t for t in tests if epic.lower() in t.lower()]
            for scope, tests in matrix["tests_by_scope"].items()
        }

    # Generate output
    if output == "json":
        output_file = Path("traceability_matrix.json")
        with open(output_file, "w") as f:
            json.dump(matrix, f, indent=2)
        console.print(f"[green]✓[/green] Generated {output_file}")
    elif output == "xml":
        output_file = Path("traceability_matrix.xml")
        xml_content = _generate_xml_matrix(matrix)
        with open(output_file, "w") as f:
            f.write(xml_content)
        console.print(f"[green]✓[/green] Generated {output_file}")
    else:  # HTML (default)
        output_file = Path("traceability_matrix.html")
        html_content = _generate_html_matrix(matrix)
        with open(output_file, "w") as f:
            f.write(html_content)
        console.print(f"[green]✓[/green] Generated {output_file}")

    # Print summary
    console.print(f"\n[bold]Matrix Summary[/bold]")
    console.print(f"  Total Tests: {matrix['total_tests']}")
    for lang, tests in matrix["tests_by_language"].items():
        console.print(f"  {lang.capitalize()}: {len(tests)}")
    console.print(f"\n[bold]Coverage by Scope[/bold]")
    for scope, count in matrix["coverage_summary"].items():
        console.print(f"  {scope.upper()}: {count}")

    sys.exit(0)


def _generate_html_matrix(matrix: dict) -> str:
    """Generate HTML traceability matrix."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Traceability Matrix</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        h2 { color: #333; border-bottom: 2px solid #ddd; padding-bottom: 10px; }
    </style>
</head>
<body>
    <h1>Traceability Matrix</h1>
    <p>Generated: {generated}</p>
"""
    html += f"<h2>Summary</h2><ul><li>Total Tests: {matrix['total_tests']}</li>"
    for scope, count in matrix["coverage_summary"].items():
        html += f"<li>{scope.upper()}: {count}</li>"
    html += "</ul>"

    html += "<h2>Tests by Language</h2><table><tr><th>Language</th><th>Count</th></tr>"
    for lang, tests in matrix["tests_by_language"].items():
        html += f"<tr><td>{lang}</td><td>{len(tests)}</td></tr>"
    html += "</table>"

    html += "<h2>Tests by Scope</h2><table><tr><th>Scope</th><th>Count</th></tr>"
    for scope, tests in matrix["tests_by_scope"].items():
        html += f"<tr><td>{scope}</td><td>{len(tests)}</td></tr>"
    html += "</table>"

    html += "</body></html>"
    return html.format(generated=matrix["generated"])


def _generate_xml_matrix(matrix: dict) -> str:
    """Generate XML traceability matrix."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<traceability_matrix>
    <metadata>
        <generated>{matrix['generated']}</generated>
        <total_tests>{matrix['total_tests']}</total_tests>
    </metadata>
    <summary>
        <unit>{matrix['coverage_summary']['unit']}</unit>
        <integration>{matrix['coverage_summary']['integration']}</integration>
        <e2e>{matrix['coverage_summary']['e2e']}</e2e>
    </summary>
    <tests_by_language>
"""
    for lang, tests in matrix["tests_by_language"].items():
        xml += f'        <language name="{lang}" count="{len(tests)}" />\n'
    xml += """    </tests_by_language>
</traceability_matrix>
"""
    return xml


@app.command("test:story")
def test_story(
    epic: Optional[str] = typer.Option(None, "-e", "--epic", help="Filter by epic name"),
) -> None:
    """Run tests by user story mapping.

    Examples:
        rtm test:story                    # All story tests
        rtm test:story -e "Epic 1"       # Epic 1 story tests
    """
    cmd = ["python", "-m", "pytest", "-m", "story"]

    if epic:
        cmd.extend(["-k", epic])

    cmd.append("tests/")

    console.print(f"[bold]🧪 Running story tests: {epic or 'all epics'}[/bold]")
    subprocess.run(cmd)


@app.command("test:comprehensive")
def test_comprehensive(
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
) -> None:
    """Run comprehensive integration and e2e tests (100% coverage).

    Tests both mock and live services with full coverage.

    Examples:
        rtm test:comprehensive                    # Comprehensive tests
        rtm test:comprehensive -v                # Verbose output
    """
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add comprehensive test files
    cmd.extend(
        [
            "tests/integration/",
            "tests/e2e/",
        ]
    )

    console.print("[bold]🧪 Running comprehensive tests...[/bold]")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


# Language-specific commands (from original implementation)
from tracertm.cli.commands.test.discover import (
    discover_all_tests,
    GoTestDiscoverer,
    PythonTestDiscoverer,
    TypeScriptTestDiscoverer,
)


@app.command()
def python(
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Filter by domain"),
    coverage: bool = typer.Option(False, "--coverage", "-c", help="Generate coverage"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run Python tests using pytest."""
    cmd = ["pytest"]

    if coverage:
        cmd.extend(["--cov=src/tracertm", "--cov-report=html", "--cov-report=term"])

    if domain:
        # Map domain to test paths
        from tracertm.cli.commands.test.discover import DOMAIN_MAPPING

        if domain in DOMAIN_MAPPING:
            for pattern in DOMAIN_MAPPING[domain]["python"]:
                cmd.append(pattern.replace("**", "").replace("*", ""))

    if verbose:
        cmd.append("-vv")

    console.print(f"[bold]Running: {' '.join(cmd)}[/bold]\n")
    subprocess.run(cmd)


@app.command()
def go(
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Filter by domain"),
    coverage: bool = typer.Option(False, "--coverage", "-c", help="Generate coverage"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run Go tests using go test."""
    backend_dir = Path.cwd() / "backend"

    if not backend_dir.exists():
        console.print("[red]Backend directory not found[/red]")
        raise typer.Exit(1)

    cmd = ["go", "test", "./..."]

    if coverage:
        cmd.extend(["-coverprofile=coverage.out", "-covermode=atomic"])

    if verbose:
        cmd.append("-v")

    console.print(f"[bold]Running: {' '.join(cmd)}[/bold]\n")
    subprocess.run(cmd, cwd=str(backend_dir))


@app.command()
def e2e(
    browser: Optional[str] = typer.Option(None, "--browser", help="Browser (chromium/firefox/webkit)"),
    headed: bool = typer.Option(False, "--headed", help="Run in headed mode"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Run TypeScript E2E tests using Playwright."""
    cmd = ["npx", "playwright", "test"]

    if browser:
        cmd.extend(["--project", browser])

    if headed:
        cmd.append("--headed")

    if verbose:
        cmd.append("--reporter=list")

    console.print(f"[bold]Running: {' '.join(cmd)}[/bold]\n")
    subprocess.run(cmd)


@app.command()
def list(
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Filter by language"),
    domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Filter by domain"),
) -> None:
    """List all available tests."""
    from tracertm.cli.commands.test.discover import discover_all_tests, _list_tests

    all_tests = discover_all_tests()

    filtered_tests = all_tests
    if language:
        filtered_tests = [t for t in filtered_tests if t.language == language]
    if domain:
        filtered_tests = [t for t in filtered_tests if domain in t.domain]

    _list_tests(filtered_tests)


if __name__ == "__main__":
    app()
