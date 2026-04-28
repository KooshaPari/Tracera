#!/usr/bin/env python3
"""
Architecture fitness harness for CI.

The script wraps existing guardrails (LOC budgets and dependency hygiene)
so GitHub Actions can fail fast with actionable diagnostics.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for older interpreters
    import tomli as tomllib  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from count_loc import (  # type: ignore[attr-defined]
        DEFAULT_EXCLUDES,
        DEFAULT_INCLUDES,
        compute_loc,
    )
except Exception as exc:  # pragma: no cover - misconfiguration
    raise RuntimeError("scripts/count_loc.py is required for architecture fitness checks") from exc


@dataclass(slots=True)
class CheckResult:
    """
    Aggregated outcome for an individual fitness check.
    """

    name: str
    passed: bool
    summary: str
    details: list[str] = field(default_factory=list)
    metrics: dict[str, int] | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "passed": self.passed,
            "summary": self.summary,
        }
        if self.metrics:
            payload["metrics"] = self.metrics
        if self.details:
            payload["details"] = self.details
        return payload


def run_total_loc_check(max_total_loc: int) -> CheckResult:
    """
    Reuse scripts/count_loc.py to enforce a global LOC ceiling.
    """

    total_loc, files_counted = compute_loc(
        ROOT,
        includes=DEFAULT_INCLUDES,
        excludes=DEFAULT_EXCLUDES,
    )
    passed = total_loc <= max_total_loc
    summary = (
        f"Runtime LOC {total_loc:,} (limit {max_total_loc:,}) across {files_counted} files."
    )
    if not passed:
        summary += " Threshold exceeded."
    metrics = {
        "total_loc": total_loc,
        "files": files_counted,
        "limit": max_total_loc,
    }
    return CheckResult(
        name="total_loc",
        passed=passed,
        summary=summary,
        metrics=metrics,
    )


def _iter_code_files(paths: Iterable[Path]) -> Iterable[Path]:
    for base in paths:
        if not base.exists():
            continue
        yield from (
            path
            for path in base.rglob("*.py")
            if path.is_file()
            if "tests" not in path.parts
            if "examples" not in path.parts
            if "/__pycache__/" not in str(path)
        )


def run_file_loc_check(max_file_loc: int, soft_file_loc: int, scope: Iterable[str]) -> CheckResult:
    """
    Enforce per-file LOC budgets with optional soft warnings.
    """

    base_paths = [ROOT / candidate for candidate in scope]
    offenders: list[tuple[str, int]] = []
    soft_hits: list[tuple[str, int]] = []

    for file_path in _iter_code_files(base_paths):
        try:
            loc = sum(1 for _ in file_path.open("r", encoding="utf-8", errors="ignore"))
        except OSError:
            continue

        rel = str(file_path.relative_to(ROOT))
        if loc > max_file_loc:
            offenders.append((rel, loc))
        elif loc > soft_file_loc:
            soft_hits.append((rel, loc))

    offenders.sort(key=lambda item: item[1], reverse=True)
    soft_hits.sort(key=lambda item: item[1], reverse=True)

    summary = f"{len(offenders)} files exceed {max_file_loc} LOC hard limit."
    details: list[str] = []

    if offenders:
        top_preview = "; ".join(f"{path} ({loc})" for path, loc in offenders[:5])
        details.append(f"Hard limit violations: {top_preview}")
    if soft_hits:
        preview = "; ".join(f"{path} ({loc})" for path, loc in soft_hits[:5])
        details.append(f"Soft limit warnings (> {soft_file_loc} LOC): {preview}")

    metrics = {
        "hard_violations": len(offenders),
        "soft_warnings": len(soft_hits),
        "hard_limit": max_file_loc,
        "soft_limit": soft_file_loc,
    }

    return CheckResult(
        name="file_loc",
        passed=not offenders,
        summary=summary,
        details=details,
        metrics=metrics,
    )


REQ_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)")


def _normalise_requirement(raw: str) -> tuple[str, str]:
    clause = raw.split(";", 1)[0].strip()
    clause = clause.split("#", 1)[0].strip()
    match = REQ_NAME_RE.match(clause)
    if not match:
        return raw.lower(), clause
    name = match.group(1).lower()
    spec = clause[match.end() :].strip()
    return name, spec


def run_dependency_check(
    pyproject_path: Path,
    banned: set[str],
) -> CheckResult:
    """
    Ensure dependency declarations stay consolidated and pinned.
    """

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    project_name = str(project.get("name", "")).lower()
    dependencies: list[str] = list(project.get("dependencies", []))

    optional = project.get("optional-dependencies", {})
    for extra_deps in optional.values():
        dependencies.extend(extra_deps)

    duplicates: dict[str, list[str]] = {}
    unpinned: list[str] = []
    banned_hits: list[str] = []

    seen: dict[str, str] = {}

    for raw in dependencies:
        name, spec = _normalise_requirement(raw)
        if not name:
            continue

        if name in seen:
            duplicates.setdefault(name, [seen[name]]).append(raw)
        else:
            seen[name] = raw

        if name in banned:
            banned_hits.append(raw)

        if name == project_name:
            continue

        if not spec or not any(char in spec for char in "<>=~!"):
            unpinned.append(raw)

    details: list[str] = []
    if duplicates:
        formatted = ", ".join(f"{pkg}: {entries}" for pkg, entries in duplicates.items())
        details.append(f"Duplicate dependency entries detected: {formatted}")
    if banned_hits:
        details.append(f"Banned dependencies present: {', '.join(banned_hits)}")
    if unpinned:
        preview = ", ".join(unpinned[:5])
        details.append(f"Unpinned dependencies: {preview}")

    passed = not (duplicates or banned_hits or unpinned)
    summary = (
        "Dependency declarations consolidated."
        if passed
        else "Dependency guardrails failed; see details."
    )
    metrics = {
        "total_dependencies": len(dependencies),
        "duplicates": len(duplicates),
        "banned": len(banned_hits),
        "unpinned": len(unpinned),
    }
    return CheckResult(
        name="dependency_hygiene",
        passed=passed,
        summary=summary,
        details=details,
        metrics=metrics,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run architecture fitness checks (LOC thresholds, dependency hygiene).",
    )
    parser.add_argument(
        "--max-total-loc",
        type=int,
        default=230_000,
        help="Hard ceiling for aggregate logical LOC across runtime code (default: 230000).",
    )
    parser.add_argument(
        "--max-file-loc",
        type=int,
        default=3_000,
        help="Hard ceiling for a single Python file (default: 3000).",
    )
    parser.add_argument(
        "--soft-file-loc",
        type=int,
        default=2_000,
        help="Soft warning threshold for a single Python file (default: 2000).",
    )
    parser.add_argument(
        "--scope",
        action="append",
        default=["src"],
        help="Relative directories to scan for LOC budgets (default: src).",
    )
    parser.add_argument(
        "--banned-dependency",
        action="append",
        default=["boto3", "django", "flask"],
        help="Dependency names that should never appear in pyproject (can pass multiple).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON for downstream consumers.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    banned = {dep.lower() for dep in args.banned_dependency}
    pyproject_path = ROOT / "pyproject.toml"
    if not pyproject_path.exists():
        raise SystemExit("pyproject.toml not found; run from repository root.")

    results = [
        run_total_loc_check(args.max_total_loc),
        run_file_loc_check(args.max_file_loc, args.soft_file_loc, scope=args.scope),
        run_dependency_check(pyproject_path, banned=banned),
    ]

    if args.json:
        print(json.dumps([result.to_dict() for result in results], indent=2))
    else:
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {result.name}: {result.summary}")
            for line in result.details:
                print(f"  - {line}")

    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
