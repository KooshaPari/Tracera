"""
Enumerations for infrastructure service/resource statuses.
"""

from __future__ import annotations

from enum import Enum


class ServiceStatus(Enum):
    """
    Status of a managed service.
    """

    PENDING = "pending"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"


class ResourceStatus(Enum):
    """
    Status of a provisioned resource.
    """

    PENDING = "pending"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"


__all__ = ["ResourceStatus", "ServiceStatus"]
