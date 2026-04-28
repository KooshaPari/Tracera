"""REST API adapters for Pheno SDK.

This package contains FastAPI-based REST API adapters that implement the hexagonal
architecture pattern.
"""

from .app import create_app
from .dependencies import get_container

__all__ = [
    "create_app",
    "get_container",
]
