"""Structural Design Patterns.

This module implements structural patterns for composing objects and classes into larger
structures while keeping them flexible and efficient.
"""

from .decorators import (
    CachingDecorator,
    LoggingDecorator,
    MetricsDecorator,
    RepositoryDecorator,
    RetryDecorator,
)
from .facade import RepositoryFacade, UseCaseFacade
from .proxy import CachingRepositoryProxy, LazyRepositoryProxy

__all__ = [
    # Decorators
    "CachingDecorator",
    "CachingRepositoryProxy",
    # Proxies
    "LazyRepositoryProxy",
    "LoggingDecorator",
    "MetricsDecorator",
    "RepositoryDecorator",
    # Facades
    "RepositoryFacade",
    "RetryDecorator",
    "UseCaseFacade",
]
