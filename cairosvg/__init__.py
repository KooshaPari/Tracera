"""Compatibility shim for environments without native Cairo.

`interrogate` imports `cairosvg` unconditionally for badge generation.
On some machines, importing the real `cairosvg` package fails with an
`OSError` due to missing native Cairo libraries. `interrogate` only treats
`ImportError` as "optional dependency missing".

This shim exists to support tools like `interrogate`, which import `cairosvg`
unconditionally for badge generation.

If importing the real `cairosvg` fails due to missing native Cairo libraries
(commonly an `OSError` from `cairocffi`), we re-raise as `ImportError` so the
dependency is treated as optional and docstring coverage can still run.
"""

from __future__ import annotations

import contextlib
import os
import pathlib
import sys
from typing import Optional

with contextlib.suppress(Exception):
    # Best-effort: If a real cairosvg is importable but fails at runtime due to
    # missing native libs, we want that failure to be handled as ImportError.
    # Importing here ensures our shim module is the one used by downstream tools
    # when running from this repository.
    __import__("cairosvg")


def _find_real_cairosvg_init() -> tuple[str, str] | None:
    """Find the installed cairosvg package `__init__.py` in site-packages.

    Returns:
        Tuple of `(package_dir, init_py_path)` if found, else `None`.
    """
    shim_pkg_dir = pathlib.Path(__file__).parent
    shim_repo_root = pathlib.Path(shim_pkg_dir).parent

    for entry in sys.path:
        # Ignore the repo root (and empty path meaning CWD) so we don't
        # resolve back to this shim.
        if entry in {"", shim_repo_root}:
            continue
        candidate_dir = os.path.join(entry, "cairosvg")
        candidate_init = os.path.join(candidate_dir, "__init__.py")
        if pathlib.Path(candidate_init).is_file():
            return candidate_dir, candidate_init
    return None


_real = _find_real_cairosvg_init()
if _real is None:
    msg = "cairosvg is not installed (shim could not locate an installed package)."
    raise ImportError(
        msg,
    )

_real_pkg_dir, _real_init = _real

try:
    # Make this module behave like the real package for any consumers that
    # import cairosvg directly when it can be imported successfully.
    __file__ = _real_init  # type: ignore[assignment]
    __path__ = [_real_pkg_dir]  # type: ignore[assignment]

    with pathlib.Path(_real_init).open("rb") as f:
        code = compile(f.read(), _real_init, "exec")
    exec(code, globals())
except Exception as exc:
    # Most commonly: OSError from missing native cairo during cairocffi import.
    msg = "Failed to import cairosvg (likely missing native Cairo libraries)."
    raise ImportError(
        msg,
    ) from exc
