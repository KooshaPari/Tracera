"""Httpx client factories and lightweight retry helpers.

This module standardizes HTTP usage across the monorepo on httpx.
- Provide sane defaults for timeouts and connection behavior
- Optional request/response hooks for tracing/metrics (e.g., OpenTelemetry)
- Lightweight retry helpers without extra dependencies

Note: httpx is a required dependency for HTTP usage in PyDevKit.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping


def create_client(
    base_url: str | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float | None = None,
    connect_timeout: float = 5.0,
    read_timeout: float = 10.0,
    write_timeout: float = 10.0,
    pool_timeout: float = 5.0,
    event_hooks: Mapping[str, Iterable[Callable[..., Any]]] | None = None,
):
    """Create a configured httpx.Client with sane defaults.

    Args:
        base_url: Optional base URL
        headers: Default headers
        timeout: Overall timeout (seconds) if set, overrides individual components
        connect_timeout, read_timeout, write_timeout, pool_timeout: components
        event_hooks: Mapping with optional "request"/"response" hooks
    """
    t = (
        timeout
        if timeout is not None
        else httpx.Timeout(
            connect=connect_timeout, read=read_timeout, write=write_timeout, pool=pool_timeout,
        )
    )
    return httpx.Client(
        base_url=base_url or "",
        headers=dict(headers or {}),
        timeout=t,
        event_hooks=event_hooks or {},
    )


def create_async_client(
    base_url: str | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float | None = None,
    connect_timeout: float = 5.0,
    read_timeout: float = 10.0,
    write_timeout: float = 10.0,
    pool_timeout: float = 5.0,
    event_hooks: Mapping[str, Iterable[Callable[..., Any]]] | None = None,
):
    """
    Create a configured httpx.AsyncClient with sane defaults.
    """
    t = (
        timeout
        if timeout is not None
        else httpx.Timeout(
            connect=connect_timeout, read=read_timeout, write=write_timeout, pool=pool_timeout,
        )
    )
    return httpx.AsyncClient(
        base_url=base_url or "",
        headers=dict(headers or {}),
        timeout=t,
        event_hooks=event_hooks or {},
    )


def request_with_retries(
    client,
    method: str,
    url: str,
    *,
    retries: int = 2,
    backoff_seconds: float = 0.5,
    retry_statuses: tuple[int, ...] = (408, 429, 500, 502, 503, 504),
    **kwargs: Any,
):
    """Sync request with simple exponential backoff retries for idempotent calls.

    Note: Prefer to keep retries small and idempotent-only (GET/HEAD).
    """
    attempt = 0
    while True:
        try:
            resp = client.request(method, url, **kwargs)
            if resp.status_code in retry_statuses and attempt < retries:
                raise httpx.HTTPStatusError("retryable status", request=resp.request, response=resp)
            return resp
        except (httpx.TimeoutException, httpx.HTTPStatusError):
            if attempt >= retries:
                raise
            attempt += 1
            # basic backoff
            import time

            time.sleep(backoff_seconds * (2 ** (attempt - 1)))


async def async_request_with_retries(
    client,
    method: str,
    url: str,
    *,
    retries: int = 2,
    backoff_seconds: float = 0.5,
    retry_statuses: tuple[int, ...] = (408, 429, 500, 502, 503, 504),
    **kwargs: Any,
):
    """
    Async request with simple exponential backoff retries for idempotent calls.
    """
    attempt = 0
    while True:
        try:
            resp = await client.request(method, url, **kwargs)
            if resp.status_code in retry_statuses and attempt < retries:
                raise httpx.HTTPStatusError("retryable status", request=resp.request, response=resp)
            return resp
        except (httpx.TimeoutException, httpx.HTTPStatusError):
            if attempt >= retries:
                raise
            attempt += 1
            import asyncio

            await asyncio.sleep(backoff_seconds * (2 ** (attempt - 1)))
