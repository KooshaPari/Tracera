"""Adapter implementations for the ``pheno`` namespace."""

from . import base, examples, prebuilt, registry
from .prebuilt import register_prebuilt_adapters

__all__ = [
    "auth",
    "base",
    "examples",
    "prebuilt",
    "register_prebuilt_adapters",
    "registry",
]
