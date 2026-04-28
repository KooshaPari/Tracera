"""
Domain Entities - Objects with Identity

Entities are objects that have a distinct identity that runs through time
and different representations. They are defined by their identity, not their attributes.

Characteristics:
    - Have unique identity (ID)
    - Mutable (can change state)
    - Equality based on ID
    - Contain business logic
    - Emit domain events

Example:
    >>> from pheno.domain.entities import User
    >>> from pheno.domain.value_objects import Email
    >>>
    >>> email = Email("user@example.com")
    >>> user, event = User.create(email=email, name="John Doe")
    >>> user.deactivate()
"""

from pheno.domain.entities.configuration import Configuration
from pheno.domain.entities.deployment import Deployment
from pheno.domain.entities.service import Service
from pheno.domain.entities.user import User

__all__ = [
    "Configuration",
    "Deployment",
    "Service",
    "User",
]
