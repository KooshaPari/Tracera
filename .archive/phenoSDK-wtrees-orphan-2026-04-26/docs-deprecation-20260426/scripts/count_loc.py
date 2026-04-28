#!/usr/bin/env python3
"""
Count logical lines of Python code and enforce LOC guardrails.
"""

from __future__ import annotations

import argparse
import json
import sys
import tokenize
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

PHENO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_EXCLUDES = (
    ".git",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    "htmlcov",
    "examples",
    "tests",
    "docs",
    "__pycache__",
)

DEFAULT_INCLUDES = (
    "src",
    "lib",
    "config",
    "scripts",
    "cli",
)


@dataclass
class LocSummary:
    total_loc: int
    threshold: int
    exceeded: bool
    files_counted: int
    include_paths: Sequence[str]
    excluded_paths: Sequence[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def iter_python_files(
    root: Path,
    includes: Iterable[str],
    excludes: Iterable[str],
) -> Iterable[Path]:
    exclude_set = {root / Path(p) for p in excludes}
    exclude_prefixes = tuple(exclude_set)
    include_entries = tuple(includes) or DEFAULT_INCLUDES
    visited: set[Path] = set()

    for include in include_entries:
        target = (root / include).resolve()
        if not target.exists():
            continue
        if target.is_file() and target.suffix == ".py":
            candidates = (target,)
        elif target.is_dir():
            candidates = (path for path in target.rglob("*.py") if path.is_file())
        else:
            continue
        for path in candidates:
            if any(path.is_relative_to(prefix) for prefix in exclude_prefixes):
                continue
            if path in visited:
                continue
            visited.add(path)
            yield path


def count_file_loc(path: Path) -> int:
    """
    Count logical lines of code for a Python file.
    """
    try:
        with tokenize.open(path) as handle:
            tokens = tokenize.generate_tokens(handle.readline)
            logical_lines: set[int] = set()
            for token_type, _, start, _, _ in tokens:
                if token_type in {
                    tokenize.ENCODING,
                    tokenize.ENDMARKER,
                    tokenize.NL,
                    tokenize.NEWLINE,
                    tokenize.COMMENT,
                }:
                    continue
                logical_lines.add(start[0])
            return len(logical_lines)
    except (SyntaxError, tokenize.TokenError):  # pragma: no cover - guardrail
        # Fall back to a simple textual scan if tokenization fails.
        approx_loc = 0
        with path.open(encoding="utf-8", errors="ignore") as handle:
            for raw_line in handle:
                stripped = raw_line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                approx_loc += 1
        print(
            f"WARNING: Tokenization failed for {path}; " "falling back to heuristic line counting.",
            file=sys.stderr,
        )
        return approx_loc


def compute_loc(
    root: Path,
    includes: Iterable[str],
    excludes: Iterable[str],
) -> tuple[int, int]:
    total = 0
    counted_files = 0
    for file_path in iter_python_files(root, includes, excludes):
        total += count_file_loc(file_path)
        counted_files += 1
    return total, counted_files


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count Python logical LOC and enforce maximum runtime threshold.",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=8500,
        help="Maximum allowed logical lines of code (default: 8500).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=PHENO_ROOT,
        help=f"Project root to inspect (default: {PHENO_ROOT}).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional paths to exclude (relative to root). Can be passed multiple times.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Paths to include in LOC counting (relative to root). "
        "Defaults to src, lib, config, scripts, and cli.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit summary as JSON.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.root.resolve()
    excludes = list(DEFAULT_EXCLUDES) + args.exclude
    includes = args.include or list(DEFAULT_INCLUDES)

    total_loc, counted_files = compute_loc(root, includes, excludes)
    summary = LocSummary(
        total_loc=total_loc,
        threshold=args.threshold,
        exceeded=total_loc > args.threshold,
        files_counted=counted_files,
        include_paths=tuple(sorted(set(includes))),
        excluded_paths=tuple(sorted(set(excludes))),
    )

    if args.json:
        print(summary.to_json())
    else:
        print(
            f"Runtime LOC: {summary.total_loc} "
            f"(threshold: {summary.threshold}, files counted: {summary.files_counted})",
        )
    if summary.exceeded:
        print(
            f"ERROR: LOC threshold exceeded by {summary.total_loc - summary.threshold} lines.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
