"""Httpx event hooks to propagate correlation IDs on outbound requests.

Integrates with pydevkit.tracing.correlation_id to attach `x-correlation-id`. Returns
empty mapping if httpx is unavailable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..tracing.correlation_id import get_or_create_correlation_id

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


def _has_httpx() -> bool:
    try:
        import httpx  # noqa: F401

        return True
    except Exception:
        return False


def build_httpx_correlation_hooks(
    header_name: str = "x-correlation-id",
) -> Mapping[str, Iterable[Any]]:
    """
    Return httpx event_hooks for sync Client that inject correlation header.
    """
    if not _has_httpx():
        return {}

    def on_request(request):
        cid = get_or_create_correlation_id()
        request.headers.setdefault(header_name, cid)

    return {"request": [on_request]}


def build_async_httpx_correlation_hooks(
    header_name: str = "x-correlation-id",
) -> Mapping[str, Iterable[Any]]:
    """
    Return httpx event_hooks for AsyncClient that inject correlation header.
    """
    if not _has_httpx():
        return {}

    async def on_request(request):
        cid = get_or_create_correlation_id()
        request.headers.setdefault(header_name, cid)

    return {"request": [on_request]}
