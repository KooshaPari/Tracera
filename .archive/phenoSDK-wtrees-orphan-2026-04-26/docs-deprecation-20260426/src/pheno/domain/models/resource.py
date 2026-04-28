"""Resource information data model.

Canonical ResourceInfo class used across all pheno-sdk components.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResourceInfo:
    """
    Information about a monitored resource.
    """

    name: str
    """
    Resource name.
    """

    project: str
    """
    Associated project name.
    """

    endpoint: str
    """
    Resource endpoint.
    """

    state: str = "unknown"
    """
    Resource state (available, unavailable, degraded)
    """

    required: bool = True
    """
    Whether this resource is required.
    """

    metadata: dict[str, Any] = field(default_factory=dict)
    """
    Additional resource metadata.
    """
