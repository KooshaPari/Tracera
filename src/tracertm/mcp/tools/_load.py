"""Load MCP tool submodules for registration. Not part of public API."""

from __future__ import annotations

import importlib

# param is NOT loaded here: server.py loads split modules (params.project, etc.)
# which register each tool once. Loading param.py here would duplicate registration.
_MODULES = [
    "base",
    "core_tools",
    "bmm_workflows",
    "specifications",
    "auth_config_db",
    "design_ingest_migration",
    "optional_features",
    "feature_demos",
    "streaming",
]

__all__: list[str] = []
for _name in _MODULES:
    try:
        importlib.import_module(f"tracertm.mcp.tools.{_name}")
        __all__.append(_name)
    except Exception:
        continue
