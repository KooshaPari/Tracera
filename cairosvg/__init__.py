"""Compatibility shim for environments without native Cairo.

`interrogate` imports `cairosvg` unconditionally for badge generation.
On some machines, importing the real `cairosvg` package fails with an
`OSError` due to missing native Cairo libraries. `interrogate` only treats
`ImportError` as "optional dependency missing".

This shim attempts to load the real `cairosvg` package from site-packages.
If that import fails for any reason (notably missing Cairo), we re-raise as
`ImportError` so tools that treat Cairo/PDF/PNG rendering as optional can
continue to operate.
"""

from __future__ import annotations

import os
import sys
from types import ModuleType
from typing import Optional


def _find_real_cairosvg_init() -> Optional[tuple[str, str]]:
    """Find the installed cairosvg package `__init__.py` in site-packages.

    Returns:
        Tuple of `(package_dir, init_py_path)` if found, else `None`.
    """
    shim_pkg_dir = os.path.dirname(__file__)
    shim_repo_root = os.path.dirname(shim_pkg_dir)

    for entry in sys.path:
        # Ignore the repo root (and empty path meaning CWD) so we don't
        # resolve back to this shim.
        if entry in ("", shim_repo_root):
            continue
        candidate_dir = os.path.join(entry, "cairosvg")
        candidate_init = os.path.join(candidate_dir, "__init__.py")
        if os.path.isfile(candidate_init):
            return candidate_dir, candidate_init
    return None


_real = _find_real_cairosvg_init()
if _real is None:
    raise ImportError(
        "cairosvg is not installed (shim could not locate an installed package)."
    )

_real_pkg_dir, _real_init = _real

try:
    # Make this module behave like the real package for any consumers that
    # import cairosvg directly when it can be imported successfully.
    __file__ = _real_init  # type: ignore[assignment]
    __path__ = [_real_pkg_dir]  # type: ignore[assignment]

    with open(_real_init, "rb") as f:
        code = compile(f.read(), _real_init, "exec")
    exec(code, globals())
except Exception as exc:
    # Most commonly: OSError from missing native cairo during cairocffi import.
    raise ImportError(
        "Failed to import cairosvg (likely missing native Cairo libraries)."
    ) from exc

