"""
Plugin collection for optional integrations.
"""

from importlib import import_module
from typing import Any


def load_plugin(path: str) -> Any:
    """
    Dynamically import a plugin module by dotted path.
    """
    return import_module(path)


__all__ = ["load_plugin"]
