"""
Common domain value objects.
"""

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse
from uuid import UUID, uuid4

from pheno.domain.base import ValueObject
from pheno.domain.exceptions import ValidationError


@dataclass(frozen=True)
class Email(ValueObject):
    """
    Email address value object with validation.
    """

    value: str

    def __post_init__(self):
        """
        Validate email format.
        """
        if not self.value:
            raise ValidationError("Email cannot be empty")

        # Simple email validation
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, self.value):
            raise ValidationError(f"Invalid email format: {self.value}")

    def __str__(self) -> str:
        return self.value

    @property
    def domain(self) -> str:
        """
        Get email domain.
        """
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """
        Get email local part.
        """
        return self.value.split("@")[0]


@dataclass(frozen=True)
class Port(ValueObject):
    """
    Network port value object with validation.
    """

    value: int

    def __post_init__(self):
        """
        Validate port range.
        """
        if not isinstance(self.value, int):
            raise ValidationError(f"Port must be an integer, got {type(self.value)}")

        if not (1 <= self.value <= 65535):
            raise ValidationError(f"Port must be between 1 and 65535, got {self.value}")

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.value

    def is_privileged(self) -> bool:
        """
        Check if port is privileged (< 1024).
        """
        return self.value < 1024

    def is_ephemeral(self) -> bool:
        """
        Check if port is ephemeral (>= 49152).
        """
        return self.value >= 49152


@dataclass(frozen=True)
class URL(ValueObject):
    """
    URL value object with validation.
    """

    value: str

    def __post_init__(self):
        """
        Validate URL format.
        """
        if not self.value:
            raise ValidationError("URL cannot be empty")

        parsed = urlparse(self.value)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError(f"Invalid URL format: {self.value}")

    def __str__(self) -> str:
        return self.value

    @property
    def scheme(self) -> str:
        """
        Get URL scheme.
        """
        return urlparse(self.value).scheme

    @property
    def host(self) -> str:
        """
        Get URL host.
        """
        return urlparse(self.value).netloc

    @property
    def path(self) -> str:
        """
        Get URL path.
        """
        return urlparse(self.value).path

    def is_secure(self) -> bool:
        """
        Check if URL uses secure protocol.
        """
        return self.scheme in ("https", "wss")


@dataclass(frozen=True)
class ConfigKey(ValueObject):
    """
    Configuration key value object.
    """

    value: str

    def __post_init__(self):
        """
        Validate config key format.
        """
        if not self.value:
            raise ValidationError("Config key cannot be empty")

        # Allow alphanumeric, dots, underscores, hyphens
        pattern = r"^[a-zA-Z0-9._-]+$"
        if not re.match(pattern, self.value):
            raise ValidationError(
                f"Invalid config key format: {self.value}. "
                "Only alphanumeric, dots, underscores, and hyphens allowed.",
            )

    def __str__(self) -> str:
        return self.value

    @property
    def parts(self) -> list[str]:
        """
        Get config key parts (split by dot).
        """
        return self.value.split(".")

    @property
    def namespace(self) -> str | None:
        """
        Get config key namespace (first part).
        """
        parts = self.parts
        return parts[0] if len(parts) > 1 else None


@dataclass(frozen=True)
class ConfigValue(ValueObject):
    """
    Configuration value value object.
    """

    value: Any

    def __str__(self) -> str:
        return str(self.value)

    def as_string(self) -> str:
        """
        Get value as string.
        """
        return str(self.value)

    def as_int(self) -> int:
        """
        Get value as integer.
        """
        try:
            return int(self.value)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Cannot convert {self.value} to int") from e

    def as_bool(self) -> bool:
        """
        Get value as boolean.
        """
        if isinstance(self.value, bool):
            return self.value
        if isinstance(self.value, str):
            return self.value.lower() in ("true", "1", "yes", "on")
        return bool(self.value)


@dataclass(frozen=True)
class UserId(ValueObject):
    """
    User ID value object.
    """

    value: str

    def __post_init__(self):
        """
        Validate user ID format (UUID).
        """
        if not self.value:
            raise ValidationError("User ID cannot be empty")

        try:
            UUID(self.value)
        except ValueError as e:
            raise ValidationError(f"Invalid user ID format: {self.value}") from e

    def __str__(self) -> str:
        return self.value

    @classmethod
    def generate(cls) -> "UserId":
        """
        Generate a new user ID.
        """
        return cls(str(uuid4()))


@dataclass(frozen=True)
class ServiceId(ValueObject):
    """
    Service ID value object.
    """

    value: str

    def __post_init__(self):
        """
        Validate service ID format (UUID).
        """
        if not self.value:
            raise ValidationError("Service ID cannot be empty")

        try:
            UUID(self.value)
        except ValueError as e:
            raise ValidationError(f"Invalid service ID format: {self.value}") from e

    def __str__(self) -> str:
        return self.value

    @classmethod
    def generate(cls) -> "ServiceId":
        """
        Generate a new service ID.
        """
        return cls(str(uuid4()))


@dataclass(frozen=True)
class DeploymentId(ValueObject):
    """
    Deployment ID value object.
    """

    value: str

    def __post_init__(self):
        """
        Validate deployment ID format (UUID).
        """
        if not self.value:
            raise ValidationError("Deployment ID cannot be empty")

        try:
            UUID(self.value)
        except ValueError as e:
            raise ValidationError(f"Invalid deployment ID format: {self.value}") from e

    def __str__(self) -> str:
        return self.value

    @classmethod
    def generate(cls) -> "DeploymentId":
        """
        Generate a new deployment ID.
        """
        return cls(str(uuid4()))
