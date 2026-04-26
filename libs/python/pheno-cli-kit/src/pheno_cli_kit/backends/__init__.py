"""CLI Kit backends for generating CLI code.

Provides backend implementations for argparse, Click, and Typer frameworks.
"""

from .argparse_backend import ArgparseBackend
from .click_backend import ClickBackend
from .registry import BackendProtocol, BaseBackend, BackendRegistry, get_backend, register_backend
from .typer_backend import TyperBackend

__all__ = [
    "ArgparseBackend",
    "ClickBackend",
    "TyperBackend",
    "BackendProtocol",
    "BaseBackend",
    "BackendRegistry",
    "get_backend",
    "register_backend",
]
