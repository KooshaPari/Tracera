"""Canonical TUI facade shared across CLI, UI, and QA stacks.

This module re-exports the rich Textual widgets provided by ``pheno.ui.tui``
so legacy callers can migrate toward a single import location while we
collapse duplicate implementations in other packages.
"""

import sys
from importlib import import_module

_CANONICAL_PACKAGE = import_module("pheno.ui.tui")

# Mirror public API from the canonical package.
__all__ = getattr(_CANONICAL_PACKAGE, "__all__", [])

for _name in __all__:
    globals()[_name] = getattr(_CANONICAL_PACKAGE, _name)

# Register key subpackages so ``import pheno.tui.widgets`` resolves to the
# same implementation as ``pheno.ui.tui.widgets``.
_SUBMODULE_MAP = {
    "core": "pheno.ui.tui.core",
    "factories": "pheno.ui.tui.factories",
    "layouts": "pheno.ui.tui.layouts",
    "protocols": "pheno.ui.tui.protocols",
    "themes": "pheno.ui.tui.themes",
    "utils": "pheno.ui.tui.utils",
    "widgets": "pheno.ui.tui.widgets",
}

for _alias, _target in _SUBMODULE_MAP.items():
    sys.modules[f"{__name__}.{_alias}"] = import_module(_target)

# Clean up temporary names
del import_module
del sys
del _alias
del _target
del _SUBMODULE_MAP
del _CANONICAL_PACKAGE
