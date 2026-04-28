#!/usr/bin/env python3
"""Shared entrypoint helpers for the Pheno CLI wrappers."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_sys_path(project_root: Path) -> None:
    """Prepend project directories to sys.path if they are missing."""
    for candidate in (project_root, project_root / "src"):
        candidate_str = str(candidate)
        if candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)


def run_cli(project_root: Path | None = None, *, label: str = "Pheno CLI") -> int:
    """Execute the shared CLI using the provided project root."""
    root = Path(project_root or Path(__file__).parent).resolve()
    _ensure_sys_path(root)

    try:
        from pheno.cli.simple import create_simple_cli

        return create_simple_cli(root)
    except ImportError as exc:
        print(f"Error: {label} framework not available: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(run_cli())
