#!/usr/bin/env python3
"""
Atlas health monitoring and reporting utilities.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_SEVERITY = "warning"
SEVERITY_LEVELS = {"error": 0, "warning": 1, "info": 2}


@dataclass
class AtlasHealthResult:
    """
    Container for Atlas health outputs.
    """

    project: str
    root: Path
    adapter: str
    summary: dict[str, Any]
    metrics: dict[str, Any]
    report: str
    status_line: str

    def as_dict(self) -> dict[str, Any]:
        """
        Return a JSON-serialisable payload.
        """
        return {
            "project": self.project,
            "root": str(self.root),
            "adapter": self.adapter,
            "summary": self.summary,
            "metrics": self.metrics,
            "report": self.report,
            "status": self.status_line,
        }


def _load_module(module_path: Path):
    """
    Dynamically load a Python module by path.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module at {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_path.stem] = module
    spec.loader.exec_module(module)
    return module


def _serialize_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    """
    Normalise metrics so they are JSON serialisable.
    """
    serialised: dict[str, Any] = {}
    for key, value in metrics.items():
        if hasattr(value, "items"):
            serialised[key] = {k: int(v) for k, v in value.items()}
        elif isinstance(value, list):
            if value and isinstance(value[0], (list, tuple)) and len(value[0]) == 2:
                serialised[key] = [
                    {"name": str(name), "value": int(count)} for name, count in value
                ]
            else:
                serialised[key] = value
        else:
            serialised[key] = value
    return serialised


def _generate_with_legacy_scanner(project_root: Path, severity: str) -> AtlasHealthResult:
    """
    Generate Atlas health using the legacy code scanner.
    """
    module_path = project_root / "scripts" / "legacy_code_scanner.py"
    module = _load_module(module_path)

    scanner = module.LegacyCodeScanner(project_root)
    scanner.config["severity_threshold"] = severity
    results = scanner.scan()

    min_level = SEVERITY_LEVELS[severity]
    filtered_findings = [
        finding for finding in results.findings if SEVERITY_LEVELS[finding.severity] <= min_level
    ]

    metrics = module.compute_health_metrics(project_root, filtered_findings, results, severity)
    report = module.render_atlas_report(project_root, results, metrics)

    severity_counts = metrics["severity_counts"]
    status_line = (
        f"{project_root.name} :: health {metrics['health_score']}/100 "
        f"({metrics['health_label']}) · "
        f"errors={severity_counts.get('error', 0)}, "
        f"warnings={severity_counts.get('warning', 0)}, "
        f"info={severity_counts.get('info', 0)}"
    )

    return AtlasHealthResult(
        project=project_root.name,
        root=project_root,
        adapter="legacy_code_scanner",
        summary=results.summary(),
        metrics=_serialize_metrics(metrics),
        report=report,
        status_line=status_line,
    )


def _generate_with_gap_filler(
    project_root: Path,
    severity: str,
    refresh: bool,
) -> AtlasHealthResult:
    """
    Generate Atlas health via the Atlas gap filler script.
    """
    script_path = project_root / "scripts" / "atlas_gap_filler.py"
    output_dir = project_root / "docs" / "atlas_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "atlas_gaps_filled.json"
    if refresh or not report_path.exists():
        cmd = [sys.executable, str(script_path), "--all"]
        proc = subprocess.run(cmd, cwd=project_root, check=False, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(
                f"[atlas-health] Warning: atlas_gap_filler exited with code {proc.returncode}\n",
            )
            if proc.stderr:
                sys.stderr.write(proc.stderr.strip() + "\n")

    if not report_path.exists():
        raise FileNotFoundError(
            f"Atlas gap filler did not create report at {report_path}. "
            "Review the script output for errors.",
        )

    with open(report_path, encoding="utf-8") as handle:
        data = json.load(handle)

    coverage_pct = data.get("coverage", {}).get("total_coverage", 0.0) or 0.0
    churn_items = data.get("git_history", {}).get("top_churn_files", [])
    workflow_stats = data.get("ci_metrics", {}).get("workflow_stats", {})
    flaky_workflows = [
        name for name, stats in workflow_stats.items() if stats.get("success_rate", 100) < 90
    ]
    performance_hotspots = data.get("performance", {}).get("hotspots", [])

    health_score = 100.0
    if coverage_pct:
        health_score -= max(0.0, 90.0 - coverage_pct) * 0.5
    else:
        health_score -= 15.0

    health_score -= min(len(flaky_workflows) * 3.0, 25.0)
    health_score -= min(len(performance_hotspots) * 2.0, 20.0)
    health_score = max(0.0, min(100.0, health_score))

    metrics = {
        "coverage_percent": coverage_pct,
        "top_churn_files": churn_items[:10],
        "flaky_workflows": flaky_workflows,
        "performance_hotspots": performance_hotspots,
        "health_score": health_score,
        "health_label": (
            "excellent"
            if health_score >= 85
            else "good" if health_score >= 70 else "fair" if health_score >= 50 else "critical"
        ),
        "severity_counts": {
            "error": sum(1 for item in churn_items if item.get("changes", 0) >= 100),
            "warning": sum(1 for item in churn_items if 60 <= item.get("changes", 0) < 100),
            "info": max(len(churn_items) - 5, 0),
        },
    }

    status_line = (
        f"{project_root.name} :: health {metrics['health_score']}/100 "
        f"({metrics['health_label']}) · "
        f"flaky={len(flaky_workflows)}, "
        f"coverage={coverage_pct:.1f}%"
    )

    return AtlasHealthResult(
        project=project_root.name,
        root=project_root,
        adapter="atlas_gap_filler",
        summary={
            "flaky_workflows": flaky_workflows,
            "performance_hotspots": performance_hotspots,
            "coverage_percent": coverage_pct,
        },
        metrics=_serialize_metrics(metrics),
        report=json.dumps(data, indent=2),
        status_line=status_line,
    )


def _generate_with_heuristics(project_root: Path, severity: str) -> AtlasHealthResult:
    """
    Perform basic heuristic scan when no tooling available.
    """
    docs_dir = project_root / "docs"
    tests_dir = project_root / "tests"
    src_dir = project_root / "src"

    total_docs = sum(1 for _ in docs_dir.rglob("*.md")) if docs_dir.exists() else 0
    total_tests = sum(1 for _ in tests_dir.rglob("test_*.py")) if tests_dir.exists() else 0
    total_modules = sum(1 for _ in src_dir.rglob("*.py")) if src_dir.exists() else 1

    documentation_score = min(100.0, (total_docs / max(total_modules, 1)) * 100)
    testing_score = min(100.0, (total_tests / max(total_modules, 1)) * 120)
    overall_health = (documentation_score * 0.4) + (testing_score * 0.6)

    metrics = {
        "health_score": round(overall_health, 2),
        "health_label": (
            "excellent"
            if overall_health >= 85
            else "warning" if overall_health >= 60 else "critical"
        ),
        "documentation_score": round(documentation_score, 2),
        "testing_score": round(testing_score, 2),
        "severity_counts": {
            "error": 0 if overall_health >= 70 else 3,
            "warning": 2 if 40 <= overall_health < 70 else 0,
            "info": 5,
        },
    }

    status_line = (
        f"{project_root.name} :: heuristic health {metrics['health_score']}/100 "
        f"({metrics['health_label']}) · "
        f"docs={total_docs}, tests={total_tests}"
    )

    summary = {
        "total_docs": total_docs,
        "total_tests": total_tests,
        "total_modules": total_modules,
        "documentation_gap": max(total_modules - total_docs, 0),
        "testing_gap": max(total_modules - total_tests, 0),
    }

    report = json.dumps(
        {
            "summary": summary,
            "metrics": metrics,
            "recommendations": [
                (
                    "Add more unit tests"
                    if total_tests < total_modules
                    else "Tests coverage looks healthy"
                ),
                (
                    "Document public modules"
                    if total_docs < total_modules
                    else "Documentation coverage sufficient"
                ),
            ],
        },
        indent=2,
    )

    return AtlasHealthResult(
        project=project_root.name,
        root=project_root,
        adapter="heuristic_scan",
        summary=summary,
        metrics=_serialize_metrics(metrics),
        report=report,
        status_line=status_line,
    )


def _detect_tooling(project_root: Path) -> tuple[str, Path]:
    """
    Detect available Atlas tooling within a project.
    """
    if (project_root / "scripts" / "legacy_code_scanner.py").exists():
        return "legacy_scanner", project_root
    if (project_root / "scripts" / "atlas_gap_filler.py").exists():
        return "gap_filler", project_root
    return "heuristic", project_root


def generate_health_report(
    project_root: Path,
    *,
    severity: str = DEFAULT_SEVERITY,
    refresh: bool = False,
) -> AtlasHealthResult:
    """
    Generate Atlas health report for a project.
    """
    adapter, root = _detect_tooling(project_root)

    if adapter == "legacy_scanner":
        return _generate_with_legacy_scanner(root, severity)
    if adapter == "gap_filler":
        return _generate_with_gap_filler(root, severity, refresh)
    return _generate_with_heuristics(root, severity)


def _discover_projects(workspace_root: Path) -> list[Path]:
    """
    Discover candidate projects for Atlas health analysis.
    """
    candidates: list[Path] = []
    for candidate in workspace_root.iterdir():
        if not candidate.is_dir():
            continue
        if candidate.name.startswith("."):
            continue
        if (candidate / "pyproject.toml").exists() or (candidate / "scripts").exists():
            candidates.append(candidate)
    return candidates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Atlas health monitoring utility")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root to scan (default: current directory)",
    )
    parser.add_argument(
        "--project",
        type=Path,
        help="Specific project directory to scan; defaults to all projects in workspace",
    )
    parser.add_argument(
        "--severity",
        choices=SEVERITY_LEVELS.keys(),
        default=DEFAULT_SEVERITY,
        help="Severity threshold for findings",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force refresh any cached reports (Atlas gap filler)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON payload instead of formatted status lines",
    )
    parser.add_argument(
        "--fail-under",
        type=float,
        help="Exit with non-zero status if health score drops below threshold",
    )

    args = parser.parse_args(argv)

    workspace = args.workspace.resolve()
    if args.project:
        projects = [args.project.resolve()]
    else:
        projects = _discover_projects(workspace)

    if not projects:
        sys.stderr.write(f"[atlas-health] No projects found under {workspace}\n")
        return 1

    results: list[AtlasHealthResult] = []
    for project_root in projects:
        try:
            result = generate_health_report(
                project_root,
                severity=args.severity,
                refresh=args.refresh,
            )
            results.append(result)
        except Exception as exc:  # pragma: no cover - error path
            sys.stderr.write(f"[atlas-health] Failed for {project_root}: {exc}\n")

    if args.json:
        payload = [result.as_dict() for result in results]
        print(json.dumps(payload, indent=2))
    else:
        for result in results:
            print(result.status_line)

    if args.fail_under is not None:
        min_score = min(result.metrics.get("health_score", 100) for result in results)
        if min_score < args.fail_under:
            return 2

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
