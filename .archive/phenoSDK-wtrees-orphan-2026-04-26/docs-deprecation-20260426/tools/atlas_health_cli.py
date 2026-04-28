#!/usr/bin/env python3
"""
Atlas Health Monitor

User-facing wrapper around pheno-sdk's atlas health engine. Provides friendly
commands for generating reports, quick status checks, and monitoring loops
across the workspace projects.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = REPO_ROOT / "pheno-sdk" / "scripts" / "atlas_health.py"


def _load_engine():
    """Dynamically load the shared atlas health implementation."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("atlas_health_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load atlas health engine from {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["atlas_health_engine"] = module
    spec.loader.exec_module(module)
    return module


ENGINE = _load_engine()
AtlasHealthResult = ENGINE.AtlasHealthResult
SEVERITY_LEVELS = ENGINE.SEVERITY_LEVELS
DEFAULT_SEVERITY = ENGINE.DEFAULT_SEVERITY


PROJECT_ALIASES = {
    "pheno": "pheno-sdk",
    "pheno-sdk": "pheno-sdk",
    "zen": "zen-mcp-server",
    "zen-mcp-server": "zen-mcp-server",
    "atoms": "atoms_mcp-old",
    "atoms_mcp-old": "atoms_mcp-old",
}


def _resolve_project(project: str | None) -> Path:
    """Resolve a project argument to an absolute project root."""
    if project is None:
        return Path.cwd()

    key = project.strip().lower()
    if key in PROJECT_ALIASES:
        candidate = REPO_ROOT / PROJECT_ALIASES[key]
    else:
        candidate = Path(project)
        if not candidate.is_absolute():
            candidate = REPO_ROOT / candidate

    if not candidate.exists():
        raise SystemExit(f"[atlas-health] Project path not found: {candidate}")

    return candidate.resolve()


def _write_report(output_path: Path, payload: dict[str, Any]) -> None:
    """Persist report payload to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def generate_report(project_root: Path, severity: str, refresh: bool) -> AtlasHealthResult:
    """Convenience wrapper around the shared engine."""
    return ENGINE.generate_health_report(project_root, severity=severity, refresh=refresh)


def print_report(result: AtlasHealthResult) -> None:
    """Print the full atlas report to stdout."""
    print(result.report)


def print_status(result: AtlasHealthResult) -> None:
    """Print the concise atlas status line."""
    print(result.status_line)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Atlas health monitoring utility")
    parser.add_argument(
        "--project",
        type=str,
        help="Project to analyse (name alias or path). Defaults to current working directory.",
    )
    parser.add_argument(
        "--severity",
        choices=list(SEVERITY_LEVELS.keys()),
        default=DEFAULT_SEVERITY,
        help="Minimum severity to include when using the legacy scanner adapter.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh underlying Atlas data sources before generating output.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print the detailed atlas health report.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print a concise atlas status line.",
    )
    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Persist a JSON payload to docs/atlas_reports (or custom --output path).",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Run monitoring mode (status line followed by detailed report).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Custom path for writing the report payload when using --full-report.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Polling interval (seconds) when using --monitor. Defaults to 300s.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project_root = _resolve_project(args.project)

    if not any([args.report, args.status, args.full_report, args.monitor]):
        args.report = True

    try:
        result = generate_report(project_root, args.severity, args.refresh)
    except Exception as exc:  # pragma: no cover - error path
        sys.stderr.write(f"[atlas-health] Failed for {project_root}: {exc}\n")
        return 2

    if args.status:
        print_status(result)

    if args.report or args.monitor or (not args.status and not args.full_report):
        print_report(result)

    if args.full_report:
        output_path = args.output
        if output_path is None:
            output_path = project_root / "docs" / "atlas_reports" / "atlas_health.json"
        elif not output_path.is_absolute():
            output_path = (project_root / output_path).resolve()

        _write_report(output_path, result.as_dict())
        print(f"📄 Atlas report written to {output_path}")

    if args.monitor:
        try:
            while True:
                time.sleep(args.interval)
                refreshed = generate_report(project_root, args.severity, args.refresh)
                print_status(refreshed)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
