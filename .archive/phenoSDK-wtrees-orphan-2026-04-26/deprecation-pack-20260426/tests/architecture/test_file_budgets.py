"""
Architecture fitness: file-size budgets.

Soft budget: 350 LOC (warn). Hard budget: 500 LOC (fail).
Enable by setting PHENO_ARCH_TESTS=1.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

import pytest

ENABLED = os.getenv("PHENO_ARCH_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not ENABLED, reason="Set PHENO_ARCH_TESTS=1 to enable architecture tests",
)

SOFT = 350
HARD = 500


def _iter_py_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.py"):
        if "/__pycache__/" in str(p):
            continue
        if any(seg in {"tests", "examples", "benchmarks"} for seg in p.parts):
            continue
        yield p


def test_file_size_budgets() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    # Phase 1: enforce budgets for domain and ports only; expand scope later
    dirs = [
        repo_root / "src" / "pheno" / "domain",
        repo_root / "src" / "pheno" / "ports",
    ]
    offenders = []
    warnings = []
    for d in dirs:
        if not d.exists():
            continue
        for py in _iter_py_files(d):
            loc = sum(1 for _ in py.open("r", encoding="utf-8"))
            if loc > HARD:
                offenders.append((str(py.relative_to(repo_root)), loc))
            elif loc > SOFT:
                warnings.append((str(py.relative_to(repo_root)), loc))

    # Print warnings to test output for visibility; do not fail on soft limit
    if warnings:
        print("SOFT budget warnings:")
        for path, loc in warnings:
            print(f"  {path}: {loc} LOC > {SOFT}")

    assert not offenders, f"Files exceeding HARD budget ({HARD} LOC): {offenders}"
