from contextvars import ContextVar
from typing import cast

# Context variable to store the current user ID (sub) from the auth token
# usage: current_user_id.set("user_123")
current_user_id: ContextVar[str | None] = cast(
    ContextVar[str | None], ContextVar("current_user_id", default=None)
)
current_account_id: ContextVar[str | None] = cast(
    ContextVar[str | None], ContextVar("current_account_id", default=None)
)
