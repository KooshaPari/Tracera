"""
Architecture fitness: import boundaries for hex layers.

- Domain/ports must not import adapters, frameworks (fastapi/starlette/uvicorn), or kit modules.
Enable by setting PHENO_ARCH_TESTS=1.
"""

from __future__ import annotations

import ast
import os
from collections.abc import Iterable
from pathlib import Path

import pytest

ENABLED = os.getenv("PHENO_ARCH_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not ENABLED, reason="Set PHENO_ARCH_TESTS=1 to enable architecture tests",
)


def _iter_py_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.py"):
        if "/__pycache__/" in str(p):
            continue
        yield p


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mods.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split(".")[0])
    return mods


def test_domain_and_ports_do_not_import_adapters_or_frameworks() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    # Enforce boundaries ONLY for domain and ports during initial rollout
    check_dirs = [
        repo_root / "src" / "pheno" / "domain",
        repo_root / "src" / "pheno" / "ports",
    ]

    # Known framework roots to forbid in domain/ports
    forbidden_frameworks = {"fastapi", "starlette", "uvicorn"}

    # Forbid kit imports by discovering top-level "*-kit" directories
    kit_dirs = [d for d in repo_root.iterdir() if d.is_dir() and d.name.endswith("-kit")]
    kit_roots = {k.name.replace("-", "_") for k in kit_dirs}
    # Also forbid legacy pheno-* imports directly (use pheno.* instead)
    legacy_pheno_dirs = [
        d for d in repo_root.iterdir() if d.is_dir() and d.name.startswith("pheno-")
    ]
    legacy_roots = {d.name.replace("-", "_") for d in legacy_pheno_dirs}

    forbidden = forbidden_frameworks | kit_roots | legacy_roots

    offenders: list[tuple[str, set[str]]] = []
    for d in check_dirs:
        if not d.exists():
            continue
        for py in _iter_py_files(d):
            imported = _imports_from(py)
            bad = imported & forbidden
            if bad:
                offenders.append((str(py.relative_to(repo_root)), bad))

    assert not offenders, f"Forbidden imports in domain/ports: {offenders}"
