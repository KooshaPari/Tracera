"""Per-route rate limiting helpers."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request


def enforce_rate_limit(request: Request, claims: dict[str, Any]) -> None:
    """Enforce per-user rate limits for sensitive analysis routes.

    Policy wiring is deferred to settings; this stub keeps imports valid and
    allows routers to mount without failing at import time.
    """
    _ = (request, claims)
