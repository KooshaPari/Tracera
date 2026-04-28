from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..value_objects.resource_type import ResourceType


@dataclass
class Resource:
    """
    Entity representing an infrastructural component required by a service.
    """

    resource_id: str
    service_id: str
    resource_type: ResourceType
    name: str
    description: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    def describe(self, key: str, value: str) -> None:
        """
        Attach arbitrary metadata that remains within the domain boundary.
        """
        self.metadata[key] = value

    def remove_detail(self, key: str) -> str | None:
        return self.metadata.pop(key, None)

    def __hash__(self) -> int:  # pragma: no cover - entity identity
        return hash(self.resource_id)
