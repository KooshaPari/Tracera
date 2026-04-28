"""
Dataclasses representing service and resource configuration/state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime
    from pathlib import Path

    from .statuses import ResourceStatus, ServiceStatus


@dataclass
class ServiceConfig:
    """
    Configuration for a managed service.
    """

    name: str
    command: str | list[str]
    working_directory: Path | None = None
    environment: dict[str, str] = field(default_factory=dict)
    port: int | None = None
    health_check_url: str | None = None
    health_check_interval: float = 30.0
    restart_policy: str = "on-failure"
    depends_on: list[str] = field(default_factory=list)
    resources: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceConfig:
    """
    Configuration for an infrastructure resource.
    """

    name: str
    resource_type: str
    provider: str = "docker"
    shared: bool = True
    required: bool = True
    configuration: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceInfo:
    """
    Runtime information about a managed service.
    """

    name: str
    status: ServiceStatus
    pid: int | None = None
    port: int | None = None
    health_status: str = "unknown"
    start_time: datetime | None = None
    restart_count: int = 0
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceInfo:
    """
    Runtime information about a provisioned resource.
    """

    name: str
    resource_type: str
    status: ResourceStatus
    provider: str
    endpoint: str | None = None
    port: int | None = None
    credentials: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "ResourceConfig",
    "ResourceInfo",
    "ServiceConfig",
    "ServiceInfo",
]
