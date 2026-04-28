"""NATS-backed event bus (optional).

Opt-in event bus using NATS (core) or JetStream for publish/subscribe. Keeps the default
in-memory EventBus intact.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

Handler = Callable[[dict[str, Any]], Awaitable[None] | None]


@dataclass
class NatsEventBus:
    nc: Any  # NATS client
    js: Any | None = None  # JetStream context (optional)
    subject_prefix: str = "events."

    async def publish(
        self, event_type: str, payload: dict, *, idempotency_key: str | None = None,
    ) -> None:
        subject = f"{self.subject_prefix}{event_type}"
        data = json.dumps(payload).encode("utf-8")
        headers = None
        if idempotency_key:
            try:
                from nats.aio.msg import Msg  # noqa: F401

                headers = {"Idempotency-Key": idempotency_key}
            except Exception:
                headers = None
        if self.js is not None:
            await self.js.publish(subject, data, headers=headers)
        else:
            await self.nc.publish(subject, data, headers=headers)

    async def subscribe(
        self,
        event_type: str,
        handler: Handler,
        *,
        durable: str | None = None,
        queue: str | None = None,
    ) -> Any:
        subject = f"{self.subject_prefix}{event_type}"
        if self.js is not None and durable:
            # JetStream push consumer subscription (at-least-once)
            sub = await self.js.subscribe(subject, durable=durable, queue=queue)

            async def _consume():
                async for msg in sub.messages:
                    try:
                        payload = json.loads(msg.data.decode("utf-8"))
                        res = handler(payload)
                        if asyncio.iscoroutine(res):
                            await res
                        await msg.ack()
                    except Exception:
                        # Do not ack on handler error; rely on redelivery policy
                        pass

            return asyncio.create_task(_consume())
        # Core NATS subscribe (best-effort)
        async def _cb(msg):
            try:
                payload = json.loads(msg.data.decode("utf-8"))
                res = handler(payload)
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

        return await self.nc.subscribe(subject, cb=_cb, queue=queue)
