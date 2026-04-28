"""Webhook delivery via NATS + httpx with DLQ support.

Producer: enqueue_webhook(js, subject, url, method="POST", headers=None, body=None, signature=None)
Consumer: run_webhook_worker(js, source_subject, dlq_subject, concurrency=1, max_attempts=3)

Notes:
- Requires nats-py and httpx; uses pydevkit http retry helpers if available.
- DLQ (dead-letter) subject receives tasks that exceeded max attempts.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from typing import Any

import httpx


async def enqueue_webhook(
    js,
    subject: str,
    *,
    url: str,
    method: str = "POST",
    headers: dict[str, str] | None = None,
    body: Any | None = None,
    signature: str | None = None,
) -> None:
    payload = {
        "url": url,
        "method": method,
        "headers": headers or {},
        "body": body,
        "signature": signature,
        "attempt": 0,
    }
    await js.publish(subject, json.dumps(payload).encode("utf-8"))


async def _deliver_once(client, task: dict[str, Any]) -> int:
    method = task.get("method", "POST").upper()
    url = task["url"]
    headers = task.get("headers") or {}
    data = task.get("body")

    # Use pydevkit retry helper if present
    try:
        from pydevkit.http import async_request_with_retries

        resp = await async_request_with_retries(
            client, method, url, json=data, headers=headers, retries=2,
        )
    except Exception:
        resp = await client.request(method, url, json=data, headers=headers)
    return resp.status_code


async def run_webhook_worker(
    js, source_subject: str, dlq_subject: str, *, concurrency: int = 1, max_attempts: int = 5,
) -> None:
    """
    Consume webhook tasks from source_subject and deliver them via httpx; DLQ on
    exhaust.
    """

    async def _worker(sub):
        async with httpx.AsyncClient() as client:
            async for msg in sub.messages:
                try:
                    task = json.loads(msg.data.decode("utf-8"))
                    task["attempt"] = int(task.get("attempt", 0)) + 1
                    status = await _deliver_once(client, task)
                    if 200 <= status < 400:
                        await msg.ack()
                    # Retry until max_attempts; then DLQ
                    elif task["attempt"] >= max_attempts:
                        await js.publish(dlq_subject, json.dumps(task).encode("utf-8"))
                        await msg.ack()
                    else:
                        await msg.nak()
                except Exception:
                    # On unexpected failures, request redelivery
                    with contextlib.suppress(Exception):
                        await msg.nak()

    sub = await js.subscribe(source_subject, durable="webhook-worker")
    tasks = [asyncio.create_task(_worker(sub)) for _ in range(max(1, concurrency))]
    await asyncio.gather(*tasks)
