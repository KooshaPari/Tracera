"""State management classes for the reactive system.

This module contains classes for managing state changes and transactions.
"""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StateChange:
    """
    Represents a single state change.
    """

    path: str
    old_value: Any
    new_value: Any
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def invert(self) -> "StateChange":
        """
        Create an inverted change for undo operations.
        """
        return StateChange(
            path=self.path,
            old_value=self.new_value,
            new_value=self.old_value,
            timestamp=time.time(),
            metadata={**self.metadata, "inverted": True},
        )


@dataclass
class Transaction:
    """
    Represents a batch of state changes.
    """

    changes: list[StateChange] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    committed: bool = False

    def commit(self):
        """
        Mark transaction as committed.
        """
        self.committed = True
        self.end_time = time.time()

    def rollback(self) -> list[StateChange]:
        """
        Get inverted changes for rollback.
        """
        return [change.invert() for change in reversed(self.changes)]
