#!/usr/bin/env python3
"""Repository hygiene validator."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", ".venv", "venv", ".mypy_cache", ".pytest_cache", ".ruff_cache", "node_modules", "build", "dist", "architecture-results"}
LARGE_FILE_THRESHOLD = 1_000_000
LARGE_FILE_ALLOW = {"docs/atlas_reports/", "docs/atlas_data/"}


@dataclass
class CleanupIssue:
    category: str
    message: str
    samples: list[str]


def _should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def find_pycache(root: Path) -> list[CleanupIssue]:
    offenders = [str(path.relative_to(root)) for path in root.rglob("__pycache__") if not _should_skip(path)]
    if offenders:
        return [CleanupIssue("cache_directories", "__pycache__ directories present", offenders[:20])]
    return []


def find_pyc(root: Path) -> list[CleanupIssue]:
    offenders = [str(path.relative_to(root)) for path in root.rglob("*.pyc") if not _should_skip(path)]
    if offenders:
        return [CleanupIssue("compiled_python", "*.pyc files present", offenders[:20])]
    return []


def find_misc(root: Path) -> list[CleanupIssue]:
    issues: list[CleanupIssue] = []
    patterns = {"*.log": "Log files committed", "*.tmp": "Temporary files committed"}
    for pattern, message in patterns.items():
        offenders = [str(path.relative_to(root)) for path in root.rglob(pattern) if not _should_skip(path)]
        if offenders:
            issues.append(CleanupIssue("temporary_files", message, offenders[:20]))
    ds_store = [str(path.relative_to(root)) for path in root.rglob(".DS_Store") if not _should_skip(path)]
    if ds_store:
        issues.append(CleanupIssue("os_artifacts", ".DS_Store files present", ds_store[:20]))
    return issues


def find_large_files(root: Path, threshold: int) -> list[CleanupIssue]:
    offenders: list[str] = []
    for path in root.rglob("*"):
        if path.is_dir() or _should_skip(path):
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size <= threshold:
            continue
        rel = str(path.relative_to(root))
        if any(rel.startswith(prefix) for prefix in LARGE_FILE_ALLOW):
            continue
        offenders.append(f"{rel} ({size / 1024:.1f} KiB)")
    if offenders:
        return [CleanupIssue("large_files", f"Files exceed {threshold // 1024} KiB limit", offenders[:20])]
    return []


def build_report(root: Path, threshold: int) -> dict[str, object]:
    issues = []
    issues.extend(find_pycache(root))
    issues.extend(find_pyc(root))
    issues.extend(find_misc(root))
    issues.extend(find_large_files(root, threshold))
    return {
        "status": "clean" if not issues else "needs_cleanup",
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate repository for stray build artefacts.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--threshold", type=int, default=LARGE_FILE_THRESHOLD, help="Large file threshold in bytes.")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(REPO_ROOT, args.threshold)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Cleanup Validation Results")
        print("=" * 32)
        print(f"Status: {report['status']}")
        print(f"Issue count: {report['issue_count']}")
        for issue in report["issues"]:
            print(f"- [{issue['category']}] {issue['message']}")
            for sample in issue["samples"]:
                print(f"    • {sample}")
    return 0 if report["status"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main())
