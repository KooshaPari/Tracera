"""Auto-load hook to add local pheno-sdk kits to sys.path.

Python automatically imports `sitecustomize` on startup if it is importable on
sys.path. This file ensures the sibling/embedded `pheno-sdk/` tree is added so
packages like `observability`, `observability_kit`, `mcp_qa`, etc. are available
without pip-installing.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _add_pheno_sdk_paths() -> None  # noqa: PLR0912:
    project_root = Path(__file__).parent

    candidate_roots: list[Path] = []
    # Allow explicit override
    env_root = os.environ.get("PHENO_SDK_ROOT")
    if env_root:
        candidate_roots.append(Path(env_root).expanduser())

    # Common layouts: sibling at repo root, or nested inside current project
    sibling_root = project_root / "pheno-sdk"
    if sibling_root.exists():
        candidate_roots.append(sibling_root)

    seen: set[str] = set()
    candidates: list[Path] = []

    # Lazy import to avoid cost if nothing to do
    import importlib.util as _importlib_util

    for root in candidate_roots:
        resolved = str(root.resolve())
        if resolved in seen or not root.exists():
            continue
        seen.add(resolved)

        # Add each kit project (prefer src/ layout when present)
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            has_build_file = (child / "pyproject.toml").exists() or (
                child / "setup.py"
            ).exists()
            if not has_build_file:
                continue

            project_name = child.name
            canonical_pkg = project_name.replace("-", "_")
            # If already installed/importable, do not shadow
            if _importlib_util.find_spec(canonical_pkg) is not None:
                continue

            src_dir = child / "src"
            candidates.append(src_dir if src_dir.exists() else child)

        # Special-case: KInfra python libraries path (opt-in only)
        # Avoid adding by default since vendored KInfra may be incomplete in dev clones.
        # Set PHENO_SDK_ENABLE_KINFRA=1 to include.
        kinfra_path = root / "KInfra" / "libraries" / "python"
        if os.environ.get("PHENO_SDK_ENABLE_KINFRA") == "1" and kinfra_path.exists():
            candidates.append(kinfra_path)

    # Explicitly include a few high-value kits even if build metadata is unusual
    extra_kits = [
        "observability-kit",
        "mcp-QA",
        "process-monitor-sdk",
        "tui-kit",
        "stream-kit",
        "event-kit",
    ]
    for root in candidate_roots:
        for name in extra_kits:
            p = root / name
            if p.exists():
                src_dir = p / "src"
                candidates.append(src_dir if src_dir.exists() else p)
        # Add namespace src/ if present
        src_ns = root / "src"
        if src_ns.exists():
            candidates.append(src_ns)

    added: list[str] = []
    for path in candidates:
        path_str = str(path)
        if path_str not in sys.path:
            # Append so site-packages (if any) take precedence
            sys.path.append(path_str)
            added.append(path_str)

    if added:
        pythonpath = os.environ.get("PYTHONPATH", "")
        prefix = ":".join(added)
        os.environ["PYTHONPATH"] = f"{prefix}:{pythonpath}" if pythonpath else prefix


_add_pheno_sdk_paths()

# Prevent pytest from auto-loading third-party plugins that depend on the legacy mcp_qa namespace

os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

try:
    import sys

    import pheno.mcp.qa as _pheno_mcp_qa
    from pheno.mcp.qa import pytest_plugins as _pheno_pytest_plugins
    from pheno.mcp.qa.pytest_plugins import auth as _pheno_pytest_auth

    sys.modules.setdefault("mcp_qa", _pheno_mcp_qa)
    sys.modules.setdefault("mcp_qa.pytest_plugins", _pheno_pytest_plugins)
    sys.modules.setdefault("mcp_qa.pytest_plugins.auth_plugin", _pheno_pytest_auth)
except Exception:  # pragma: no cover
    pass
