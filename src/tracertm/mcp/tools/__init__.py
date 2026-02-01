"""
TraceRTM MCP Tools.

This package contains all MCP tool implementations organized by domain.
Tools are registered via decorators on the shared `mcp` instance.
"""

from __future__ import annotations

import importlib

# Import tool modules to register them with the mcp instance.
# Some environments (tests) don't have FastMCP dependencies available, so
# we tolerate import failures to keep unit tests focused on local logic.
# param is NOT loaded here: server.py loads split modules (params.project, params.system, etc.)
# which register each tool once. Loading param.py here would duplicate tool registration
# and trigger "Component already exists" (FastMCP LocalProvider on_duplicate=warn).
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

__all__ = []
for _name in _MODULES:
    try:
        importlib.import_module(f"{__name__}.{_name}")
        __all__.append(_name)
    except Exception:
        # Allow tests to import subsets without FastMCP dependencies.
        continue
