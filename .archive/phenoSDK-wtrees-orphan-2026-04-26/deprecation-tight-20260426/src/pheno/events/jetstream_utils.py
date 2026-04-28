"""JetStream helpers for streams, consumers, and simple work-queue patterns.

All functions expect a JetStream context from nats-py (nc.jetstream()). Imports are
guarded; install nats-py for actual usage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


async def ensure_stream(js, name: str, subjects: Iterable[str], **stream_kwargs: Any):
    """
    Create stream if it doesn't exist; otherwise return True.
    """
    try:
        await js.stream_info(name)
        return True
    except Exception:
        pass
    await js.add_stream(name=name, subjects=list(subjects), **stream_kwargs)
    return True


async def ensure_consumer(
    js,
    stream: str,
    durable: str,
    *,
    deliver_policy: str | None = None,
    ack_policy: str | None = None,
    max_deliver: int | None = None,
    filter_subject: str | None = None,
    **consumer_kwargs: Any,
):
    """
    Create durable consumer with minimal options if it doesn't exist.
    """
    try:
        await js.consumer_info(stream, durable)
        return True
    except Exception:
        pass
    # Map simple string policies to enum values if available
    enums = {}
    try:
        from nats.js.api import AckPolicy, DeliverPolicy  # type: ignore

        enums["deliver"] = {
            None: DeliverPolicy.All,
            "all": DeliverPolicy.All,
            "new": DeliverPolicy.New,
            "last": DeliverPolicy.Last,
        }
        enums["ack"] = {
            None: AckPolicy.Explicit,
            "explicit": AckPolicy.Explicit,
            "none": AckPolicy.None_,
            "all": AckPolicy.All,
        }
    except Exception:
        enums = None

    dp = enums["deliver"].get(deliver_policy, deliver_policy) if enums else deliver_policy
    ap = enums["ack"].get(ack_policy, ack_policy) if enums else ack_policy

    await js.add_consumer(
        stream,
        durable,
        deliver_policy=dp,
        ack_policy=ap,
        max_deliver=max_deliver,
        filter_subject=filter_subject,
        **consumer_kwargs,
    )
    return True


async def ensure_workqueue(
    js,
    name: str,
    subject: str,
    *,
    _max_msgs: int | None = None,
    **stream_kwargs: Any,
):
    """
    Create a simple work-queue style stream (limits retention default).
    """
    kwargs = dict(stream_kwargs)
    # Prefer limits retention for simple work-queue patterns
    try:
        from nats.js.api import RetentionPolicy  # type: ignore

        kwargs.setdefault("retention", RetentionPolicy.Limits)
    except Exception:
        pass
    return await ensure_stream(js, name=name, subjects=[subject], **kwargs)
