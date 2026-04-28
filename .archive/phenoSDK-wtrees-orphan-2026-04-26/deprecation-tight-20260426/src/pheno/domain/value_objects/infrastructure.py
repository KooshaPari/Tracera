"""
Infrastructure-related value objects.
"""

import re
from dataclasses import dataclass
from enum import StrEnum

from pheno.domain.base import ValueObject
from pheno.domain.exceptions import ValidationError


class ServiceStatusEnum(StrEnum):
    """
    Service status enumeration.
    """

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ServiceStatus(ValueObject):
    """
    Service status value object.
    """

    value: ServiceStatusEnum

    def __post_init__(self):
        """
        Validate service status.
        """
        if not isinstance(self.value, ServiceStatusEnum):
            raise ValidationError(
                f"Invalid service status: {self.value}. "
                f"Must be one of {[s.value for s in ServiceStatusEnum]}",
            )

    def __str__(self) -> str:
        return self.value.value

    def is_healthy(self) -> bool:
        """
        Check if service is healthy.
        """
        return self.value == ServiceStatusEnum.RUNNING

    def is_transitioning(self) -> bool:
        """
        Check if service is in transition state.
        """
        return self.value in (
            ServiceStatusEnum.STARTING,
            ServiceStatusEnum.STOPPING,
        )

    def can_transition_to(self, new_status: "ServiceStatus") -> bool:
        """
        Check if transition to new status is valid.
        """
        valid_transitions = {
            ServiceStatusEnum.STOPPED: [
                ServiceStatusEnum.STARTING,
            ],
            ServiceStatusEnum.STARTING: [
                ServiceStatusEnum.RUNNING,
                ServiceStatusEnum.FAILED,
            ],
            ServiceStatusEnum.RUNNING: [
                ServiceStatusEnum.STOPPING,
                ServiceStatusEnum.FAILED,
            ],
            ServiceStatusEnum.STOPPING: [
                ServiceStatusEnum.STOPPED,
                ServiceStatusEnum.FAILED,
            ],
            ServiceStatusEnum.FAILED: [
                ServiceStatusEnum.STARTING,
                ServiceStatusEnum.STOPPED,
            ],
        }

        allowed = valid_transitions.get(self.value, [])
        return new_status.value in allowed


@dataclass(frozen=True)
class ServicePort(ValueObject):
    """
    Service port value object with protocol.
    """

    port: int
    protocol: str = "tcp"

    def __post_init__(self):
        """
        Validate service port.
        """
        if not isinstance(self.port, int):
            raise ValidationError(f"Port must be an integer, got {type(self.port)}")

        if not (1 <= self.port <= 65535):
            raise ValidationError(f"Port must be between 1 and 65535, got {self.port}")

        if self.protocol not in ("tcp", "udp", "http", "https", "grpc"):
            raise ValidationError(
                f"Invalid protocol: {self.protocol}. " "Must be one of: tcp, udp, http, https, grpc",
            )

    def __str__(self) -> str:
        return f"{self.port}/{self.protocol}"

    def is_http(self) -> bool:
        """
        Check if port uses HTTP protocol.
        """
        return self.protocol in ("http", "https")

    def is_secure(self) -> bool:
        """
        Check if port uses secure protocol.
        """
        return self.protocol in ("https", "grpc")


@dataclass(frozen=True)
class ServiceName(ValueObject):
    """
    Service name value object with validation.
    """

    value: str

    def __post_init__(self):
        """
        Validate service name format.
        """
        if not self.value:
            raise ValidationError("Service name cannot be empty")

        # Service name: lowercase alphanumeric, hyphens, underscores
        # Must start with letter, 1-63 characters
        pattern = r"^[a-z][a-z0-9_-]{0,62}$"
        if not re.match(pattern, self.value):
            raise ValidationError(
                f"Invalid service name: {self.value}. "
                "Must start with lowercase letter, contain only lowercase "
                "alphanumeric, hyphens, underscores, and be 1-63 characters.",
            )

    def __str__(self) -> str:
        return self.value

    def to_dns_label(self) -> str:
        """
        Convert to valid DNS label (replace underscores with hyphens).
        """
        return self.value.replace("_", "-")

    def to_env_var_prefix(self) -> str:
        """
        Convert to environment variable prefix (uppercase, underscores).
        """
        return self.value.upper().replace("-", "_")
