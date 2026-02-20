"""TraceRTM MCP Server - FastMCP 3.0.0b1 based MCP server for AI-native CLI.

This package intentionally avoids importing heavy MCP exports at module import
time to prevent blocking API startup. Accessing exported symbols will load
them lazily on demand.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any


def _exports_module() -> object:
    return import_module("tracertm.mcp._exports")


def __getattr__(name: str) -> object:
    exports = _exports_module()
    return getattr(exports, name)


def __dir__() -> list[str]:
    exports = _exports_module()
    return sorted(set(globals().keys()) | set(getattr(exports, "__all__", [])))


__all__ = []
