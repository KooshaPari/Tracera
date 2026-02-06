"""Parallel test orchestrator with dependency-aware staging.

This module powers the ``rtm test --parallel`` command. It executes the
complete test suite in dependency-ordered stages and stops execution as soon
as a dependency breaks. Each stage can optionally use ``pytest-xdist`` for
parallelism.

Inspired by atoms-mcp-prod/test_orchestrator.py
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Any

from tracertm.cli.commands.test.dependencies import TestDependencies

# Find project root
_current = Path(__file__).resolve()
while _current != _current.parent:
    if (_current / "pyproject.toml").exists() or (_current / "tests").exists():
        PROJECT_ROOT = _current
        break
    _current = _current.parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent


@dataclass
class TestStage:
    """Definition of a dependency-aware test stage."""

    __test__ = False

    name: str
    display_name: str
    description: str
    paths: List[str] = field(default_factory=list)
    ignore: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)

    def pytest_args(self) -> List[str]:
        """Generate pytest arguments for this stage."""
        args: List[str] = []
        for ignore_path in self.ignore:
            args.extend(["--ignore", ignore_path])
        args.extend(self.paths)
        return args


@dataclass
class StageRunResult:
    """Outcome of running a single stage."""

    stage: TestStage
    status: str
    exit_code: int
    duration: float
    reason: Optional[str] = None


@dataclass
class TestRunSummary:
    """Aggregate result of the orchestrated run."""

    success: bool
    stage_results: List[StageRunResult]


class TestOrchestrator:
    """Runs pytest suites in dependency-aware stages with optional parallelism."""

    __test__ = False

    def __init__(
        self,
        *,
        verbose: bool = False,
        marker: Optional[str] = None,
        keyword: Optional[str] = None,
        parallel: bool = False,
        max_workers: Optional[int] = None,
        coverage: bool = False,
    ) -> None:
        self.verbose = verbose
        self.marker = marker
        self.keyword = keyword
        self.parallel = parallel
        self.max_workers = max_workers
        self.coverage = coverage
        self._coverage_initialized = False

        if self.parallel:
            self._verify_parallel_support()

    def run(self) -> TestRunSummary:
        """Execute all stages sequentially until one fails."""
        stages = self.build_stage_plan()
        stage_results: List[StageRunResult] = []
        failed_stages: set[str] = set()

        if self.coverage:
            self._reset_coverage_data()

        for stage in stages:
            blocking = failed_stages.intersection(stage.depends_on)
            if blocking:
                blockers = ", ".join(sorted(blocking))
                stage_results.append(
                    StageRunResult(
                        stage=stage,
                        status="skipped",
                        exit_code=0,
                        duration=0.0,
                        reason=f"Skipped because {blockers} failed",
                    )
                )
                continue

            result = self._run_stage(stage)
            stage_results.append(result)
            if result.status == "failed":
                failed_stages.add(stage.name)
            if self.coverage and result.status != "skipped":
                self._coverage_initialized = True

        success = not failed_stages
        if self.coverage and self._coverage_initialized:
            self._finalize_coverage_reports()

        self._print_summary(stage_results)
        return TestRunSummary(success=success, stage_results=stage_results)

    def build_stage_plan(self) -> List[TestStage]:
        """Build ordered stage definitions covering the full suite."""
        foundation_files = _files_from_dependencies(TestDependencies.FOUNDATION)
        stage_configs: list[dict[str, object]] = [
            {
                "name": "foundation",
                "display": "Foundation",
                "description": "Core storage, database, models",
                "dependency_map": TestDependencies.FOUNDATION,
                "extra_paths": ["tests/unit/core/**", "tests/unit/storage/**"],
                "ignore": [],
                "depends_on": [],
            },
            {
                "name": "repositories",
                "display": "Repositories",
                "description": "Database repositories and queries",
                "dependency_map": TestDependencies.REPOSITORIES,
                "extra_paths": ["tests/unit/repositories/**"],
                "ignore": [],
                "depends_on": ["foundation"],
            },
            {
                "name": "services",
                "display": "Services",
                "description": "Business logic services",
                "dependency_map": TestDependencies.SERVICES,
                "extra_paths": ["tests/unit/services/**", "tests/component/services/**"],
                "ignore": [],
                "depends_on": ["repositories"],
            },
            {
                "name": "api",
                "display": "API",
                "description": "HTTP handlers and endpoints",
                "dependency_map": TestDependencies.API,
                "extra_paths": ["tests/unit/api/**", "tests/component/api/**"],
                "ignore": [],
                "depends_on": ["services"],
            },
            {
                "name": "cli",
                "display": "CLI",
                "description": "CLI commands and user interface",
                "dependency_map": TestDependencies.CLI,
                "extra_paths": ["tests/unit/cli/**"],
                "ignore": [],
                "depends_on": ["api"],
            },
            {
                "name": "integration",
                "display": "Integration",
                "description": "Cross-service integration tests",
                "dependency_map": TestDependencies.INTEGRATION,
                "extra_paths": ["tests/integration/**"],
                "ignore": [],
                "depends_on": ["cli"],
            },
            {
                "name": "e2e",
                "display": "End-to-End",
                "description": "Full workflow coverage",
                "dependency_map": TestDependencies.E2E,
                "extra_paths": ["tests/e2e/**"],
                "ignore": foundation_files,
                "depends_on": ["integration"],
            },
        ]

        stages: List[TestStage] = []
        for config in stage_configs:
            dep_map = config.get("dependency_map")
            if not isinstance(dep_map, dict):
                dep_map = None
            extra_paths_obj = config.get("extra_paths", [])
            extra_paths = extra_paths_obj if isinstance(extra_paths_obj, list) else []
            paths = _collect_existing_paths(dep_map, extra_paths)

            ignore_list_obj = config.get("ignore", [])
            ignore_list = ignore_list_obj if isinstance(ignore_list_obj, list) else []
            ignore_paths = _filter_existing_paths(ignore_list)

            if not paths:
                continue

            name = config.get("name", "")
            display = config.get("display", "")
            desc = config.get("description", "")
            deps = config.get("depends_on", [])
            if isinstance(name, str) and isinstance(display, str) and isinstance(desc, str) and isinstance(deps, list):
                stage = TestStage(
                    name=name,
                    display_name=display,
                    description=desc,
                    paths=paths,
                    ignore=ignore_paths,
                    depends_on=deps,
                )
                stages.append(stage)

        valid_names = {stage.name for stage in stages}
        for stage in stages:
            stage.depends_on = [dep for dep in stage.depends_on if dep in valid_names]

        return stages

    def _verify_parallel_support(self) -> None:
        """Ensure pytest-xdist is available before running in parallel."""
        if importlib.util.find_spec("xdist") is None:
            raise RuntimeError(
                "pytest-xdist is required for --parallel runs. Install it first."
            )

    def _run_stage(self, stage: TestStage) -> StageRunResult:
        """Execute a stage via pytest and capture its outcome."""
        if not stage.paths:
            return StageRunResult(
                stage=stage, status="skipped", exit_code=0, duration=0.0
            )

        print(f"\n🔹 Stage: {stage.display_name} - {stage.description}")
        cov_append = self._coverage_initialized
        cmd = self._build_pytest_command(stage, cov_append)
        print(f"   ↳ Command: {' '.join(cmd)}")

        start = time.perf_counter()
        completed = subprocess.run(cmd, cwd=PROJECT_ROOT)
        duration = time.perf_counter() - start
        status = "passed" if completed.returncode == 0 else "failed"

        return StageRunResult(
            stage=stage,
            status=status,
            exit_code=completed.returncode,
            duration=duration,
        )

    def _build_pytest_command(self, stage: TestStage, cov_append: bool) -> List[str]:
        """Create the pytest command for a given stage."""
        cmd: List[str] = ["python", "-m", "pytest"]

        if self.parallel:
            worker_count = str(self.max_workers) if self.max_workers else "auto"
            cmd.extend(["-n", worker_count])

        if self.verbose:
            cmd.append("-v")

        if self.marker:
            cmd.extend(["-m", self.marker])

        if self.keyword:
            cmd.extend(["-k", self.keyword])

        if self.coverage:
            cmd.extend(["--cov=src/tracertm", "--cov-report="])
            if cov_append:
                cmd.append("--cov-append")

        cmd.extend(stage.pytest_args())
        return cmd

    @staticmethod
    def _print_summary(stage_results: Iterable[StageRunResult]) -> None:
        """Render a compact textual summary of all stages."""
        print("\n📋 Parallel Test Stage Summary")
        print("═" * 60)
        for result in stage_results:
            status = result.status.upper()
            duration = f"{result.duration:.1f}s" if result.duration else "-"
            if result.reason:
                print(
                    f"{result.stage.display_name:25} {status:8} {duration:>8}  {result.reason}"
                )
            else:
                print(f"{result.stage.display_name:25} {status:8} {duration:>8}")
        print("═" * 60)

    def _reset_coverage_data(self) -> None:
        """Reset coverage data before running tests."""
        self._run_coverage_command(["erase"])

    def _finalize_coverage_reports(self) -> None:
        """Generate final coverage reports."""
        commands = [
            ["combine"],
            ["html"],
            ["xml"],
            ["json", "-o", "coverage.json"],
            ["report", "--skip-covered"],
        ]
        for args in commands:
            self._run_coverage_command(args)

    def _run_coverage_command(self, args: List[str]) -> None:
        """Run a coverage command."""
        cmd = ["python", "-m", "coverage"] + args
        subprocess.run(cmd, cwd=PROJECT_ROOT)


def _files_from_dependencies(dep_map: dict[str, dict[str, object]] | None) -> list[str]:
    """Extract file paths from dependency map."""
    if not dep_map:
        return []
    files: set[str] = set()
    for info in dep_map.values():
        if isinstance(info, dict):
            file_val = info.get("file")
            if isinstance(file_val, str):
                files.add(file_val)
    return sorted(files)


def _collect_existing_paths(
    dep_map: dict[str, dict[str, object]] | None, extra_paths: Iterable[str]
) -> list[str]:
    """Collect existing test paths from dependencies and extra paths."""
    paths = _files_from_dependencies(dep_map)
    paths.extend(extra_paths)
    filtered = _filter_existing_paths(paths)
    return _remove_child_paths_when_parent_is_present(filtered)


def _filter_existing_paths(paths: Iterable[str]) -> list[str]:
    """Filter paths to only include existing files/directories."""
    filtered: list[str] = []
    seen: set[str] = set()
    for rel_path in paths:
        if not rel_path or rel_path in seen:
            continue
        absolute = PROJECT_ROOT / rel_path
        if absolute.exists():
            filtered.append(rel_path)
            seen.add(rel_path)
    return filtered


def _remove_child_paths_when_parent_is_present(paths: list[str]) -> list[str]:
    """Drop file paths when their parent directory is already scheduled."""
    normalized: list[str] = []
    directories: list[str] = []

    for rel_path in paths:
        absolute = PROJECT_ROOT / rel_path
        is_child_of_dir = any(rel_path.startswith(f"{parent}/") for parent in directories)
        if is_child_of_dir:
            continue

        normalized.append(rel_path)
        if absolute.is_dir():
            directories.append(rel_path.rstrip("/"))

    return normalized


__all__ = [
    "TestOrchestrator",
    "TestStage",
    "StageRunResult",
    "TestRunSummary",
]
