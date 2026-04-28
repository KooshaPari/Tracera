"""
Domain modeling base classes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class Entity:
    """
    Base entity with identity.
    """

    id: str | None = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


@dataclass(frozen=True)
class ValueObject:
    """
    Base value object (immutable).
    """

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


@dataclass
class AggregateRoot(Entity):
    """
    Aggregate root with domain events.
    """

    _events: list[Any] = field(default_factory=list, init=False, repr=False)

    def add_event(self, event: Any):
        """
        Add domain event.
        """
        self._events.append(event)

    @property
    def domain_events(self) -> list[Any]:
        """
        Return collected domain events.
        """
        return list(self._events)

    def clear_events(self):
        """
        Clear domain events.
        """
        events = self._events.copy()
        self._events.clear()
        return events


@dataclass(frozen=True)
class DomainEvent:
    """
    Base domain event.
    """

    aggregate_id: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = field(default="")

    def __post_init__(self):
        if not self.event_type:
            object.__setattr__(self, "event_type", self.__class__.__name__)
