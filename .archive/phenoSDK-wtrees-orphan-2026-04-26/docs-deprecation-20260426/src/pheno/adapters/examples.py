"""
Reference adapters showcasing the framework primitives.

These adapters are intentionally lightweight so they can operate inside the
pheno-sdk development environment without external dependencies.
"""

from __future__ import annotations

import queue
import sqlite3
import subprocess
from typing import TYPE_CHECKING, Any

try:  # pragma: no cover - requests is optional
    import requests
except Exception:  # pragma: no cover - defensive import guard
    requests = None  # type: ignore[assignment]

from pheno.core.registry.adapters import AdapterType

from .base import (
    AdapterConfig,
    AdapterContext,
    AdapterError,
    BaseAdapter,
    StatelessAdapter,
)
from .registry import FrameworkAdapterRegistry, get_framework_registry

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence


class HttpAdapter(StatelessAdapter):
    """Outbound HTTP client with optional dry-run support."""

    CAPABILITIES: Sequence[str] = ("http", "rest", "json")
    TAGS: Sequence[str] = ("networking", "transport")

    def invoke(self, payload: Mapping[str, Any] | None, **kwargs: Any) -> dict[str, Any]:
        request_envelope = {**self.config.fixed_parameters, **(payload or {})}
        method = request_envelope.get("method", "GET")
        url = request_envelope.get("url")
        if not url:
            raise AdapterError("HTTP adapter requires 'url'.")

        headers = {
            **self.config.fixed_parameters.get("headers", {}),
            **request_envelope.get("headers", {}),
        }

        if self.context.metadata.get("dry_run", False) or requests is None:
            return {
                "dry_run": True,
                "request": {"method": method, "url": url, "headers": headers},
            }

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=request_envelope.get("body"),
            timeout=request_envelope.get("timeout", 10),
        )
        body = response.text
        try:
            parsed = response.json()
        except ValueError:
            parsed = None
        return {
            "status": response.status_code,
            "headers": dict(response.headers),
            "body": body,
            "json": parsed,
        }


class SqliteAdapter(BaseAdapter):
    """Simple SQLite adapter illustrating persistent resources."""

    CAPABILITIES: Sequence[str] = ("sql", "sqlite")
    TAGS: Sequence[str] = ("storage", "database")

    def start(self) -> None:
        database = self.config.fixed_parameters.get("database", ":memory:")
        self._connection = sqlite3.connect(database)
        self._connection.row_factory = sqlite3.Row

    def invoke(self, payload: Mapping[str, Any] | None, **kwargs: Any) -> list[dict[str, Any]]:
        if payload is None:
            raise AdapterError("Database adapter requires payload with 'query'.")
        query = payload.get("query")
        if not query:
            raise AdapterError("Database adapter payload missing 'query'.")
        parameters = payload.get("parameters") or ()
        cursor = self._connection.execute(query, parameters)
        if query.lstrip().upper().startswith("SELECT"):
            rows = [dict(row) for row in cursor.fetchall()]
        else:
            self._connection.commit()
            rows = [{"rowcount": cursor.rowcount}]
        return rows

    def stop(self) -> None:
        self._connection.close()


class InMemoryMessagingAdapter(BaseAdapter):
    """In-memory queue to demonstrate messaging semantics."""

    CAPABILITIES: Sequence[str] = ("publish", "consume", "memory")
    TAGS: Sequence[str] = ("messaging", "queue")

    def start(self) -> None:
        maxsize = int(self.config.fixed_parameters.get("maxsize", 0))
        self._queue: queue.Queue[Any] = queue.Queue(maxsize=maxsize)

    def invoke(self, payload: Mapping[str, Any] | None, **kwargs: Any) -> Any:
        if payload is None:
            raise AdapterError("Messaging adapter requires payload with 'action'.")
        action = payload.get("action")
        if action == "publish":
            message = payload.get("message")
            self._queue.put(message, timeout=payload.get("timeout"))
            return {"queued": True, "size": self._queue.qsize()}
        if action == "consume":
            try:
                message = self._queue.get(timeout=payload.get("timeout"))
                return {"message": message, "size": self._queue.qsize()}
            except queue.Empty:
                return {"message": None, "size": self._queue.qsize()}
        raise AdapterError("Unsupported messaging action. Use 'publish' or 'consume'.")

    def stop(self) -> None:
        while not self._queue.empty():
            self._queue.get_nowait()


class LocalInferenceAdapter(StatelessAdapter):
    """Wraps a callable model for local inference."""

    CAPABILITIES: Sequence[str] = ("ml", "predict")
    TAGS: Sequence[str] = ("ml", "inference")

    def __init__(self, config: AdapterConfig, context: AdapterContext | None = None):
        super().__init__(config, context)
        model = self.config.fixed_parameters.get("model")
        if model is None:
            raise AdapterError("LocalInferenceAdapter requires fixed_parameters['model'].")
        if not callable(model):
            raise AdapterError("Provided model must be callable.")
        self._model: Callable[..., Any] = model

    def invoke(self, payload: Mapping[str, Any] | None, **kwargs: Any) -> Any:
        inputs = payload.get("inputs") if payload else None
        if inputs is None:
            raise AdapterError("Inference adapter payload requires 'inputs'.")
        result = self._model(inputs)
        return {"inputs": inputs, "outputs": result}


class SshTunnelingAdapter(StatelessAdapter):
    """Suggests SSH tunnelling commands; optionally executes them."""

    CAPABILITIES: Sequence[str] = ("ssh", "tunnel")
    TAGS: Sequence[str] = ("networking", "security")

    def invoke(self, payload: Mapping[str, Any] | None, **kwargs: Any) -> dict[str, Any]:
        request = {**self.config.fixed_parameters, **(payload or {})}
        local = request.get("local")
        remote = request.get("remote")
        host = request.get("host")
        user = request.get("user")
        if not all((local, remote, host)):
            raise AdapterError("Tunneling adapter requires 'local', 'remote', and 'host'.")
        cmd = [
            "ssh",
            "-N",
            "-L",
            f"{local}:{remote}",
            f"{user + '@' if user else ''}{host}",
        ]
        dry_run = request.get("dry_run", True)
        if dry_run:
            return {"command": cmd, "dry_run": True}

        process = subprocess.Popen(cmd)  # pragma: no cover - external command
        return {"command": cmd, "dry_run": False, "pid": process.pid}


def register_examples(registry: FrameworkAdapterRegistry | None = None) -> None:
    framework_registry = registry or get_framework_registry()
    framework_registry.register(
        adapter_type=AdapterType.EVENT,
        adapter_class=HttpAdapter,
        name="http_client",
        abstraction_level=0.32,
        description="Protocol-aware HTTP client for outbound REST calls.",
        tags=("http", "rest"),
        fixed_parameters={"timeout": 5},
    )
    framework_registry.register(
        adapter_type=AdapterType.DATABASE,
        adapter_class=SqliteAdapter,
        name="sqlite_local",
        abstraction_level=0.28,
        description="Low-abstraction SQLite adapter with explicit SQL control.",
        fixed_parameters={"database": ":memory:"},
    )
    framework_registry.register(
        adapter_type=AdapterType.EVENT,
        adapter_class=InMemoryMessagingAdapter,
        name="in_memory_queue",
        abstraction_level=0.62,
        description="Domain-aware messaging adapter exposing publish/consume verbs.",
        fixed_parameters={"maxsize": 0},
    )
    framework_registry.register(
        adapter_type=AdapterType.LLM,
        adapter_class=LocalInferenceAdapter,
        name="local_inference",
        abstraction_level=0.74,
        description="Wraps a callable model for deterministic local inference.",
        fixed_parameters={"model": lambda x: x},  # placeholder identity
    )
    framework_registry.register(
        adapter_type=AdapterType.DEPLOY,
        adapter_class=SshTunnelingAdapter,
        name="ssh_tunneling",
        abstraction_level=0.88,
        description="Plug-and-play tunnelling helper emitting SSH commands.",
        fixed_parameters={"dry_run": True},
        tags=("ssh", "ops"),
    )


register_examples()

__all__ = [
    "HttpAdapter",
    "InMemoryMessagingAdapter",
    "LocalInferenceAdapter",
    "SqliteAdapter",
    "SshTunnelingAdapter",
    "register_examples",
]
