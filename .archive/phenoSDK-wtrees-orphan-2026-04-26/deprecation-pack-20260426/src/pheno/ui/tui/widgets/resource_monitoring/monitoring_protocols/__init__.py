"""Monitoring protocols for resource status widget.

This module contains protocols for custom resource monitoring implementations.
"""

from .database_provider import DatabaseProvider
from .resource_monitor import ResourceMonitor

__all__ = [
    "DatabaseProvider",
    "ResourceMonitor",
]
