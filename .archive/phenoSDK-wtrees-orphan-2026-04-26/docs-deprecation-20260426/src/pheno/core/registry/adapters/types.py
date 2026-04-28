"""
Type aliases for adapter plugins.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .enums import AdapterType

PluginHook = Callable[["AdapterRegistry", Any], None]

__all__ = ["AdapterType", "PluginHook"]
