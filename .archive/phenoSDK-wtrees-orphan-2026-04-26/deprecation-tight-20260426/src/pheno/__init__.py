"""
Phen package: staging ground for the refactored hexagonal layout.

Modules will migrate here from the legacy ``pheno`` namespace until the repo-wide
rename lands. During the transition, legacy packages re-export from this module.

Infrastructure bootstrap: ensure shared adapters are registered once at import
time so downstream packages can resolve dependencies without manual wiring.
"""

import importlib
import os
import sys

if os.getenv("PHENO_SKIP_BOOTSTRAP") != "1":
    try:  # pragma: no cover - bootstrap should be transparent to consumers
        from .infrastructure import register_default_adapters

        register_default_adapters()
    except Exception:
        # Container bootstrap should never block module import; consumers can call
        # register_default_adapters() manually if they need custom wiring.
        pass

_ALIASES: dict[str, str] = {
    "pydevkit": "pheno.dev",
    "mcp_qa": "pheno.mcp.qa",
    "event_kit": "pheno.events",
    "stream_kit": "pheno.events.streaming",
    "tui_kit": "pheno.ui.tui",
    "vector_kit": "pheno.vector",
    "storage_kit": "pheno.storage",
    "workflow_kit": "pheno.workflow",
    "adapter_kit": "pheno.adapters",
    "db_kit": "pheno.database",
    "observability_kit": "pheno.observability",
    "process_monitor_sdk": "pheno.process",
    "authkit_client": "pheno.auth",
    "credentials_kit": "pheno.credentials",
}


def _register_aliases() -> None:
    for alias, target in _ALIASES.items():
        if alias in sys.modules:
            continue
        try:
            module = importlib.import_module(target)
        except Exception:
            continue
        sys.modules[alias] = module
        globals()[alias.split(".")[0]] = module


_register_aliases()

__all__ = ["domain", "ports", *list(_ALIASES.keys())]
