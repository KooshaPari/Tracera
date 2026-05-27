"""Pytest plugin: skip CLI-dependent test trees when tracertm.cli is not installed."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_CLI_DEPENDENT_TEST_DIRS = frozenset({"e2e", "integration", "phase_five"})
_TESTS_ROOT = Path(__file__).resolve().parent


def _tracertm_cli_available() -> bool:
    return importlib.util.find_spec("tracertm.cli") is not None


def pytest_ignore_collect(collection_path: Path, config) -> bool | None:  # noqa: ANN001
    if _tracertm_cli_available():
        return None
    try:
        rel = collection_path.resolve().relative_to(_TESTS_ROOT)
    except ValueError:
        return None
    return bool(rel.parts) and rel.parts[0] in _CLI_DEPENDENT_TEST_DIRS
