#!/usr/bin/env python3
"""Cleanup Validation Script for Pheno-SDK.

Validates code cleanup, dead code, and unused import reports produced by CI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_DEAD_CODE_REPORT = Path("dead-code-report.txt")
DEFAULT_UNUSED_IMPORTS_REPORT = Path("unused-imports.txt")


def validate_cleanup() -> dict[str, Any]:
    """
    Inspect the workspace for common artefacts that should be cleaned.
    """

    cleanup_issues: list[dict[str, Any]] = []
    root = Path().resolve()

    patterns = {
        "temporary_files": ["*.pyc", "*.pyo", "*.log", "*.tmp"],
        "cache_directories": ["__pycache__"],
        "os_junk": [".DS_Store"],
    }
    severity = {
        "temporary_files": "high",
        "os_junk": "medium",
        "cache_directories": "low",
    }

    ignored_parts = {"node_modules", ".git", ".venv", "htmlcov"}
    ignored_filenames = {"tui.log"}

    for issue_type, globs in patterns.items():
        matches: list[str] = []
        for pattern in globs:
            for path in root.rglob(pattern):
                if any(part in ignored_parts for part in path.parts):
                    continue
                if pattern.endswith(".pyc") and "__pycache__" in path.parts:
                    continue
                if path.name in ignored_filenames:
                    continue
                matches.append(str(path))

        if matches:
            cleanup_issues.append(
                {
                    "type": issue_type,
                    "patterns": globs,
                    "count": len(matches),
                    "samples": matches[:5],
                    "severity": severity.get(issue_type, "medium"),
                },
            )

    blocking_issues = [
        issue for issue in cleanup_issues if issue.get("severity") in {"high", "medium"}
    ]
    status = "clean" if not blocking_issues else "needs_cleanup"
    return {
        "cleanup_issues": cleanup_issues,
        "total_issues": len(cleanup_issues),
        "blocking_issues": len(blocking_issues),
        "status": status,
    }


def parse_dead_code_report(report_path: Path) -> dict[str, Any]:
    """
    Parse the Vulture dead code report from CI.
    """

    if not report_path.exists():
        return {
            "status": "missing",
            "dead_code_found": False,
            "dead_code_count": 0,
            "entries": [],
        }

    entries: list[str] = []
    for raw_line in report_path.read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("Analyzing") or line.startswith("python"):
            continue
        if line.startswith("="):
            continue
        entries.append(line)

    return {
        "status": "no_dead_code" if not entries else "issues_found",
        "dead_code_found": bool(entries),
        "dead_code_count": len(entries),
        "entries": entries[:20],
    }


def parse_unused_imports_report(report_path: Path) -> dict[str, Any]:
    """
    Parse the unimport report from CI.
    """

    if not report_path.exists():
        return {
            "status": "missing",
            "unused_imports_found": False,
            "unused_imports_count": 0,
            "entries": [],
        }

    entries: list[str] = []
    text = report_path.read_text().strip()

    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        lower = cleaned.lower()
        if lower.startswith("processed"):
            continue
        if lower.startswith("nothing to do"):
            return {
                "status": "no_unused_imports",
                "unused_imports_found": False,
                "unused_imports_count": 0,
                "entries": [],
            }
        entries.append(cleaned)

    return {
        "status": "no_unused_imports" if not entries else "issues_found",
        "unused_imports_found": bool(entries),
        "unused_imports_count": len(entries),
        "entries": entries[:20],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate cleanup artefacts produced by CI.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument(
        "--dead-code-report",
        type=Path,
        default=DEFAULT_DEAD_CODE_REPORT,
        help="Path to the Vulture report file (default: dead-code-report.txt).",
    )
    parser.add_argument(
        "--unused-imports-report",
        type=Path,
        default=DEFAULT_UNUSED_IMPORTS_REPORT,
        help="Path to the unimport report file (default: unused-imports.txt).",
    )
    args = parser.parse_args()

    cleanup_result = validate_cleanup()
    dead_code_result = parse_dead_code_report(args.dead_code_report)
    unused_imports_result = parse_unused_imports_report(args.unused_imports_report)

    all_clean = (
        cleanup_result["status"] == "clean"
        and dead_code_result["status"] in {"no_dead_code", "missing"}
        and unused_imports_result["status"] in {"no_unused_imports", "missing"}
    )

    combined_result = {
        "cleanup_check": cleanup_result,
        "dead_code_check": dead_code_result,
        "unused_imports_check": unused_imports_result,
        "overall_status": "clean" if all_clean else "needs_attention",
    }

    if args.json:
        print(json.dumps(combined_result, indent=2))
    else:
        print("Cleanup Validation Results")
        print("==========================")
        print(
            f"\nWorkspace hygiene: {cleanup_result['status']} "
            f"(blocking issues: {cleanup_result['blocking_issues']})",
        )
        for issue in cleanup_result["cleanup_issues"]:
            print(
                f"  - {issue['type']} ({issue['severity']}): {issue['count']} occurrences "
                f"(sample: {', '.join(issue['samples'])})",
            )
        print(
            f"\nDead code status: {dead_code_result['status']} "
            f"({dead_code_result['dead_code_count']} findings)",
        )
        print(
            f"Unused imports status: {unused_imports_result['status']} "
            f"({unused_imports_result['unused_imports_count']} findings)",
        )
        print(f"\nOverall status: {combined_result['overall_status']}")

    return 0 if all_clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
