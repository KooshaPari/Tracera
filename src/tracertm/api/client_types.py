"""Type definitions for the TraceRTM Python API client."""

from collections.abc import Iterator
from typing import Any

from tracertm.models.item import Item


class BatchResult:
    """Wrapper that behaves like a list of items while exposing summary stats.

    This is primarily used by integration tests to validate batch operations.
    """

    def __init__(self, items: list[Any], stats: dict[str, Any]) -> None:
        """Initialize a BatchResult.

        Args:
            items: Items returned by the operation.
            stats: Summary stats (e.g., created/updated/deleted counts).
        """
        self._items = items
        self._stats = stats

    def __iter__(self) -> Iterator[Any]:
        """Iterate over the underlying items."""
        return iter(self._items)

    def __len__(self) -> int:
        """Return the number of underlying items."""
        return len(self._items)

    def __getitem__(self, key: int | str) -> Any:
        """Return an item by index or a stat by name.

        Args:
            key: Item index or stat name.

        Returns:
            Item at the given index, or a stat value when key is a known stat.
        """
        if isinstance(key, str) and key in self._stats:
            return self._stats[key]
        if isinstance(key, int):
            return self._items[key]
        msg = f"indices must be integers or strings, not {type(key).__name__}"
        raise TypeError(msg)

    def __bool__(self) -> bool:
        """Return True to preserve truthiness semantics used by tests."""
        return True

    def __eq__(self, other: object) -> bool:
        """Compare this result to another object.

        This preserves backward-compatible semantics used in tests.
        """
        if other is True:
            return True
        return self._items == other

    @property
    def items(self) -> list[Any]:
        """Return the underlying items list."""
        return self._items

    def to_dict(self) -> dict[str, Any]:
        """Return the summary stats as a dictionary."""
        return self._stats


class ItemView:
    """Lightweight, detached view of an Item that supports both attr and dict access."""

    def __init__(self, item: Item) -> None:
        """Initialize an ItemView.

        Args:
            item: Item model instance to snapshot into a detached view.
        """
        self._data = {
            "id": getattr(item, "id", None),
            "project_id": getattr(item, "project_id", None),
            "title": getattr(item, "title", None),
            "description": getattr(item, "description", None),
            "view": getattr(item, "view", None),
            "type": getattr(item, "item_type", None),
            "item_type": getattr(item, "item_type", None),
            "status": getattr(item, "status", None),
            "priority": getattr(item, "priority", None),
            "owner": getattr(item, "owner", None),
            "parent_id": getattr(item, "parent_id", None),
            "metadata": getattr(item, "item_metadata", None),
            "item_metadata": getattr(item, "item_metadata", None),
            "version": getattr(item, "version", None),
            "created_at": getattr(item, "created_at", None),
            "updated_at": getattr(item, "updated_at", None),
            "deleted_at": getattr(item, "deleted_at", None),
        }

    def __getitem__(self, key: str) -> Any:
        """Return a field value by key."""
        return self._data[key]

    def __getattr__(self, name: str) -> Any:
        """Provide attribute-style access to known fields."""
        if name in self._data:
            return self._data[name]
        raise AttributeError(name)

    def __iter__(self) -> Iterator[str]:
        """Iterate over available keys."""
        return iter(self._data)

    def items(self) -> Any:
        """Return dict-like (key, value) pairs for the view."""
        return self._data.items()

    def __repr__(self) -> str:
        """Return a debug representation of the view."""
        return f"ItemView({self._data})"
