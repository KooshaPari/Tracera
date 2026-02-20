"""Request-scoped context variables.

These contextvars hold identifiers (e.g. user/account id) extracted from auth
middleware so downstream services can access them without threading request
objects through every call.
"""

from contextvars import ContextVar
from typing import cast

# Context variable to store the current user ID (sub) from the auth token
current_user_id: ContextVar[str | None] = cast("ContextVar[str | None]", ContextVar("current_user_id", default=None))
current_account_id: ContextVar[str | None] = cast(
    "ContextVar[str | None]",
    ContextVar("current_account_id", default=None),
)
