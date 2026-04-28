"""NATS connection factory (async) with JetStream helper.

This module requires nats-py.

Usage:
    factory = NATSConnectionFactory(servers=["nats://127.0.0.1:4222"], name="svc")
    async with factory as nc:
        js = factory.jetstream(nc)
        await js.publish("events.demo", b"hello")
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import nats  # type: ignore

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass
class NATSConnectionFactory:
    servers: Iterable[str] | None = None
    name: str | None = None
    connect_kwargs: dict[str, Any] | None = None

    async def connect(self):
        servers = list(self.servers or ["nats://127.0.0.1:4222"])
        kwargs = dict(self.connect_kwargs or {})
        if self.name:
            kwargs.setdefault("name", self.name)
        return await nats.connect(servers=servers, **kwargs)

    def jetstream(self, nc):
        """
        Return a JetStream context from a connected NATS client.
        """
        try:
            return nc.jetstream()
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Failed to create JetStream context from NATS client") from e

    async def close(self, nc):
        with contextlib.suppress(Exception):
            await nc.close()

    async def __aenter__(self):
        self._nc = await self.connect()
        return self._nc

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self._nc.drain()
        except Exception:
            with contextlib.suppress(Exception):
                await self._nc.close()
        self._nc = None
