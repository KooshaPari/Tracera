"""Prebuilt message queue adapters."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

from .base import AdapterOperationError, BasePrebuiltAdapter

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


class NATSAdapter(BasePrebuiltAdapter):
    """Adapter around the ``nats-py`` client."""

    name = "nats"
    category = "message_queue"

    def __init__(self, **config: Any):
        defaults = {"servers": ["nats://127.0.0.1:4222"]}
        defaults.update(config)
        super().__init__(**defaults)
        self._client: Any | None = None

    async def connect_async(self) -> None:
        nats = self._require("nats.aio.client", install_hint="nats-py")
        try:
            self._client = await nats.Client().connect(**self._config)
            self._connected = True
        except Exception as exc:  # pragma: no cover - depends on broker
            raise AdapterOperationError(f"nats connect failed: {exc}") from exc

    async def publish(self, subject: str, data: bytes) -> None:
        if self._client is None:
            await self.connect_async()
        try:
            await self._client.publish(subject, data)
        except Exception as exc:  # pragma: no cover
            raise AdapterOperationError(f"nats publish failed: {exc}") from exc

    async def subscribe(self, subject: str, callback: Callable[[bytes], Any]) -> None:
        if self._client is None:
            await self.connect_async()

        async def _handler(msg: Any) -> None:
            result = callback(msg.data)
            if inspect.isawaitable(result):  # pragma: no branch - small helper
                await result

        try:
            await self._client.subscribe(subject, cb=_handler)
        except Exception as exc:  # pragma: no cover
            raise AdapterOperationError(f"nats subscribe failed: {exc}") from exc

    async def close_async(self) -> None:
        if self._client is not None:
            await self._client.drain()
            await self._client.close()
            self._client = None
        self._connected = False


class RabbitMQAdapter(BasePrebuiltAdapter):
    """Adapter around the ``pika`` blocking connection."""

    name = "rabbitmq"
    category = "message_queue"

    def __init__(self, **config: Any):
        defaults = {"host": "127.0.0.1", "port": 5672, "virtual_host": "/"}
        defaults.update(config)
        super().__init__(**defaults)
        self._connection: Any | None = None
        self._channel: Any | None = None

    def connect(self) -> None:
        pika = self._require("pika")

        def _connect() -> tuple[Any, Any]:
            params = pika.ConnectionParameters(
                host=self._config.get("host"),
                port=self._config.get("port"),
                virtual_host=self._config.get("virtual_host"),
                credentials=self._build_credentials(pika),
            )
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            return connection, channel

        self._connection, self._channel = self._wrap_errors("connect", _connect)
        super().connect()

    def _build_credentials(self, pika_module: Any) -> Any:
        user = self._config.get("username")
        password = self._config.get("password")
        if user and password:
            return pika_module.PlainCredentials(user, password)
        return pika_module.ConnectionParameters.DEFAULT_CREDENTIALS

    def declare_queue(self, queue: str, **kwargs: Any) -> None:
        self.ensure_connected()
        self._wrap_errors("declare_queue", lambda: self._channel.queue_declare(queue=queue, **kwargs))

    def publish(self, queue: str, body: bytes, *, routing_key: str | None = None) -> None:
        self.ensure_connected()
        rk = routing_key or queue
        self._wrap_errors("publish", lambda: self._channel.basic_publish(exchange="", routing_key=rk, body=body))

    def consume(self, queue: str, handler: Callable[[bytes], None], *, auto_ack: bool = True) -> None:
        self.ensure_connected()

        def _callback(ch, method, properties, body):  # pragma: no cover - relies on broker
            handler(body)
            if not auto_ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        self._wrap_errors("consume", lambda: self._channel.basic_consume(queue=queue, on_message_callback=_callback, auto_ack=auto_ack))

    def start_consuming(self) -> None:
        self.ensure_connected()
        self._wrap_errors("start_consuming", self._channel.start_consuming)

    def close(self) -> None:
        if self._channel is not None:
            try:
                self._channel.close()
            except Exception:  # pragma: no cover
                pass
            self._channel = None
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        super().close()


class KafkaAdapter(BasePrebuiltAdapter):
    """Adapter built on top of ``kafka-python``."""

    name = "kafka"
    category = "message_queue"

    def __init__(self, *, bootstrap_servers: Iterable[str] | None = None, **config: Any):
        super().__init__(bootstrap_servers=list(bootstrap_servers or ["127.0.0.1:9092"]), **config)
        self._producer: Any | None = None
        self._consumer: Any | None = None

    def connect(self) -> None:
        kafka = self._require("kafka")

        def _connect() -> tuple[Any, Any]:
            producer = kafka.KafkaProducer(bootstrap_servers=self._config["bootstrap_servers"], **self._config.get("producer", {}))
            consumer_conf = {"bootstrap_servers": self._config["bootstrap_servers"], **self._config.get("consumer", {})}
            consumer = kafka.KafkaConsumer(**consumer_conf) if consumer_conf else None
            return producer, consumer

        self._producer, self._consumer = self._wrap_errors("connect", _connect)
        super().connect()

    def produce(self, topic: str, value: bytes, *, key: bytes | None = None) -> None:
        self.ensure_connected()
        if self._producer is None:
            raise AdapterOperationError("kafka producer not initialised")
        self._wrap_errors("produce", lambda: self._producer.send(topic, value=value, key=key))

    def flush(self) -> None:
        if self._producer is not None:
            self._wrap_errors("flush", self._producer.flush)

    def consume(self, topics: Iterable[str], handler: Callable[[Any], None]) -> None:
        self.ensure_connected()
        if self._consumer is None:
            raise AdapterOperationError("kafka consumer not initialised")
        self._consumer.subscribe(list(topics))
        for message in self._consumer:  # pragma: no cover - requires broker
            handler(message)

    def close(self) -> None:
        if self._producer is not None:
            try:
                self._producer.flush()
                self._producer.close()
            except Exception:  # pragma: no cover
                pass
            self._producer = None
        if self._consumer is not None:
            self._consumer.close()
            self._consumer = None
        super().close()


__all__ = [
    "KafkaAdapter",
    "NATSAdapter",
    "RabbitMQAdapter",
]
