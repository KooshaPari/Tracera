"""
User-related domain events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class UserCreated:
    """
    Event emitted when a user is created.
    """

    aggregate_id: str
    user_id: str
    email: str
    name: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "UserCreated"


@dataclass(frozen=True)
class UserUpdated:
    """
    Event emitted when a user is updated.
    """

    aggregate_id: str
    user_id: str
    field: str
    old_value: Any
    new_value: Any
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "UserUpdated"


@dataclass(frozen=True)
class UserDeactivated:
    """
    Event emitted when a user is deactivated.
    """

    aggregate_id: str
    user_id: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = "UserDeactivated"
