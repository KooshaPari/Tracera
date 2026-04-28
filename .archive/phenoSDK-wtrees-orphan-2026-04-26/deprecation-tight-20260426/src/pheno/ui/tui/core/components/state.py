"""
State container for component data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ComponentStateStore:
    """
    Mutable container that tracks component-specific data and metadata.
    """

    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    version: int = 0

    def get(self, key: str, default: Any = None) -> Any:
        """
        Fetch a stored value, returning ``default`` when missing.
        """
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Persist a value and bump the version counter.
        """
        self.data[key] = value
        self.version += 1

    def update(self, data: dict[str, Any]) -> None:
        """
        Merge multiple values into the state.
        """
        self.data.update(data)
        self.version += 1

    def clear(self) -> None:
        """
        Reset stored values and increment the version.
        """
        self.data.clear()
        self.version += 1


__all__ = ["ComponentStateStore"]
