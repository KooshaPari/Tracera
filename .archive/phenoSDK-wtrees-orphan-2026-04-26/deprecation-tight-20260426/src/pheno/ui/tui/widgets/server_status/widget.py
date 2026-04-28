"""
Textual widget for monitoring MCP server status.
"""

from __future__ import annotations

import time
from collections import deque
from typing import TYPE_CHECKING, Any

from textual.reactive import reactive
from textual.widgets import Static

from .view import StatusViewModel, build_status_panel

if TYPE_CHECKING:
    from .client import ClientAdapter

__all__ = ["ServerStatusWidget"]


class ServerStatusWidget(Static):
    """
    Display MCP server status with comprehensive monitoring.
    """

    DEFAULT_CSS = """
    ServerStatusWidget {
        border: solid $accent;
        padding: 1;
        height: auto;
        background: $surface;
    }

    ServerStatusWidget.connected {
        border: solid $success;
    }

    ServerStatusWidget.disconnected {
        border: solid $error;
    }
    """

    endpoint = reactive("")
    connected = reactive(False)
    last_ping = reactive(0.0)
    latency_ms = reactive(0.0)
    last_request = reactive("")
    server_version = reactive("Unknown")
    error_message = reactive("")
    requests_per_sec = reactive(0.0)
    error_rate = reactive(0.0)

    def __init__(
        self,
        client_adapter: ClientAdapter | None = None,
        endpoint: str = "",
        check_interval: float = 5.0,
        stream_capture: Any | None = None,
        max_history: int = 20,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.client_adapter = client_adapter
        self._endpoint = endpoint
        self.check_interval = check_interval
        self.stream_capture = stream_capture
        self.max_history = max_history

        self._latency_history: deque[float] = deque(maxlen=max_history)
        self._health_history: deque[dict[str, Any]] = deque(maxlen=max_history)

        self._request_count = 0
        self._error_count = 0
        self._start_time = time.time()

        if client_adapter and hasattr(client_adapter, "endpoint"):
            self.endpoint = client_adapter.endpoint
        else:
            self.endpoint = endpoint

        self.set_timer(0.1, self._initial_update)

        if check_interval > 0:
            self.set_interval(check_interval, self.refresh_status)

    async def _initial_update(self) -> None:
        await self._update_status()

    async def _update_status(self) -> None:
        try:
            if not self.client_adapter:
                self.connected = False
                self.error_message = "No client configured"
                self.latency_ms = 0.0
                self.set_class(False, "connected")
                self.set_class(True, "disconnected")
                return

            start = time.perf_counter()
            try:
                tools = await self.client_adapter.list_tools()
                duration = (time.perf_counter() - start) * 1000

                self.connected = True
                self.latency_ms = duration
                self.last_ping = time.time()
                self.error_message = ""
                self._request_count += 1

                self._latency_history.append(duration)
                self._health_history.append(
                    {
                        "timestamp": time.time(),
                        "success": True,
                        "latency_ms": duration,
                        "tool_count": len(tools) if tools else 0,
                    },
                )

                if hasattr(self.client_adapter, "client"):
                    client = self.client_adapter.client
                    if hasattr(client, "_session") and hasattr(client._session, "server_version"):
                        self.server_version = client._session.server_version

                if self.stream_capture:
                    self.stream_capture.write(
                        f"[{time.strftime('%H:%M:%S')}] Server health check OK "
                        f"(latency: {duration:.1f}ms, tools: {len(tools) if tools else 0})\n",
                    )

            except Exception as exc:
                self.connected = False
                self.error_message = str(exc)[:50]
                self.latency_ms = 0.0
                self._error_count += 1
                self._health_history.append(
                    {
                        "timestamp": time.time(),
                        "success": False,
                        "error": str(exc)[:100],
                    },
                )
                if self.stream_capture:
                    self.stream_capture.write(
                        f"[{time.strftime('%H:%M:%S')}] Server health check failed: {exc}\n",
                    )

            self._update_metrics()
            self.set_class(self.connected, "connected")
            self.set_class(not self.connected, "disconnected")

        except Exception as exc:
            self.connected = False
            self.error_message = f"Status update failed: {str(exc)[:30]}"
            self.set_class(False, "connected")
            self.set_class(True, "disconnected")

    def _update_metrics(self) -> None:
        elapsed = time.time() - self._start_time
        if elapsed > 0:
            self.requests_per_sec = self._request_count / elapsed
            total_requests = self._request_count + self._error_count
            if total_requests > 0:
                self.error_rate = (self._error_count / total_requests) * 100

    def render(self):
        model = StatusViewModel(
            connected=self.connected,
            endpoint=self.endpoint,
            last_ping=self.last_ping,
            latency_ms=self.latency_ms,
            server_version=self.server_version,
            requests_per_sec=self.requests_per_sec,
            error_rate=self.error_rate,
            latency_history=list(self._latency_history),
            health_history=list(self._health_history),
            error_message=self.error_message,
        )
        return build_status_panel(model)

    async def refresh_status(self) -> None:
        await self._update_status()
        self.refresh()

    def get_health_history(self) -> list[dict[str, Any]]:
        return list(self._health_history)

    def get_latency_history(self) -> list[float]:
        return list(self._latency_history)

    def reset_metrics(self) -> None:
        self._request_count = 0
        self._error_count = 0
        self._start_time = time.time()
        self._update_metrics()
        self.refresh()

    def clear_history(self) -> None:
        self._health_history.clear()
        self._latency_history.clear()
        self.refresh()

    def set_client_adapter(self, adapter: ClientAdapter | None) -> None:
        self.client_adapter = adapter
        if adapter and hasattr(adapter, "endpoint"):
            self.endpoint = adapter.endpoint
        self.set_timer(0.1, self._initial_update)

    def get_status_summary(self) -> dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "connected": self.connected,
            "last_ping": self.last_ping,
            "latency_ms": self.latency_ms,
            "server_version": self.server_version,
            "error_message": self.error_message,
            "requests_per_sec": self.requests_per_sec,
            "error_rate": self.error_rate,
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "uptime_seconds": time.time() - self._start_time,
            "health_checks": len(self._health_history),
            "recent_latency_avg": (
                sum(self._latency_history) / len(self._latency_history)
                if self._latency_history
                else 0.0
            ),
            "has_client_adapter": self.client_adapter is not None,
        }
