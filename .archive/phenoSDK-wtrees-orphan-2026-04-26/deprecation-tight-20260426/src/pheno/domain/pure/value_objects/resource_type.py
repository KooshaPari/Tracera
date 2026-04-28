from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class ResourceKind(Enum):
    """Enumerates supported resource categories."""

    DATABASE = "database"
    QUEUE = "queue"
    STORAGE = "storage"
    COMPUTE = "compute"
    CACHE = "cache"
    GENERIC = "generic"


@dataclass(frozen=True)
class ResourceType:
    """
    Value object encapsulating the category of a resource.

    Allows mapping aliases to canonical kinds and enforces that only defined
    kinds are used across the domain.
    """

    kind: ResourceKind

    _ALIAS_MAPPING: ClassVar[dict[str, ResourceKind]] = {
        "db": ResourceKind.DATABASE,
        "sql": ResourceKind.DATABASE,
        "mq": ResourceKind.QUEUE,
        "worker": ResourceKind.COMPUTE,
        "function": ResourceKind.COMPUTE,
        "cache": ResourceKind.CACHE,
        "bucket": ResourceKind.STORAGE,
    }

    @classmethod
    def from_name(cls, name: str) -> ResourceType:
        normalized = name.strip().lower()
        try:
            return cls(ResourceKind(normalized))
        except ValueError:
            mapped = cls._ALIAS_MAPPING.get(normalized)
            if mapped is None:
                raise ValueError(f"Unsupported resource type '{name}'")
            return cls(mapped)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.kind.value
