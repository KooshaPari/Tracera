"""Tracera — Python SDK for the Tracera REST API.

This package provides both synchronous and asynchronous clients that wrap the
Tracera HTTP API. The synchronous client (:class:`Tracera`) uses only the
standard library, while the asynchronous client (:class:`AsyncTracera`) is
backed by ``httpx``.

Quick start (sync)::

    from tracera import Tracera

    client = Tracera(base_url="http://127.0.0.1:8080", token="...")
    node = client.get_node(123)
    client.ingest_github(payload)

Quick start (async)::

    from tracera import AsyncTracera

    async with AsyncTracera(base_url="http://127.0.0.1:8080") as client:
        node = await client.get_node(123)
        await client.ingest_jira(payload)
"""

from __future__ import annotations

from .client import (
    AsyncTracera,
    Tracera,
    TraceraAPIError,
    TraceraConfig,
    TraceraError,
)

__all__ = [
    "AsyncTracera",
    "Tracera",
    "TraceraAPIError",
    "TraceraConfig",
    "TraceraError",
]

__version__ = "0.1.0"