"""Widget provider protocols for dependency injection.

This module defines protocols that widgets can use to interact with external providers
(like OAuth cache managers) without depending on concrete implementations.
"""

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

__all__ = [
    "ClientAdapter",
    "MetricsProvider",
    "OAuthCacheProvider",
    "ResourceProvider",
    "TunnelProvider",
]


class OAuthCacheProvider(Protocol):
    """Protocol for OAuth cache providers.

    This protocol defines the interface that OAuth cache implementations must
    provide to work with OAuthStatusWidget. By using this protocol, widgets
    can work with any cache implementation that provides the required methods.

    Example implementations:
        >>> from pathlib import Path
        >>>
        >>> class SimpleOAuthCache:
        ...     def __init__(self, cache_dir: Path):
        ...         self.cache_dir = cache_dir
        ...
        ...     def _get_cache_path(self) -> Path:
        ...         return self.cache_dir / "oauth_token.json"
        >>>
        >>> # Use with widget
        >>> cache = SimpleOAuthCache(Path.home() / ".cache")
        >>> widget = OAuthStatusWidget(cache_provider=cache)

    Required Methods:
        _get_cache_path() -> Path: Returns the path to the OAuth token cache file
    """

    def _get_cache_path(self) -> Path:
        """Get the path to the OAuth token cache file.

        Returns:
            Path object pointing to the token cache file location
        """
        ...


@runtime_checkable
class ClientAdapter(Protocol):
    """Protocol for MCP client adapters.

    Implement this protocol to integrate with ServerStatusWidget for
    comprehensive server health monitoring.

    Example:
        class MyClientAdapter:
            @property
            def endpoint(self) -> str:
                return "http://localhost:8000"

            async def list_tools(self) -> List[Dict[str, Any]]:
                # Perform health check by listing tools
                response = await self.client.list_tools()
                return response.tools
    """

    @property
    def endpoint(self) -> str:
        """Return the server endpoint URL.

        Returns:
            Server endpoint URL string
        """
        ...

    async def list_tools(self) -> list[dict[str, Any]]:
        """Perform a health check by listing available tools.

        This method is used by ServerStatusWidget to verify server connectivity
        and measure latency. It should return quickly and raise an exception
        if the connection fails.

        Returns:
            List of tool dictionaries with tool metadata

        Raises:
            Exception: If connection fails or server is unreachable
        """
        ...


@runtime_checkable
class TunnelProvider(Protocol):
    """Protocol for tunnel service providers.

    Implement this protocol to integrate with TunnelStatusWidget for
    custom tunnel monitoring solutions.

    Example:
        class NgrokProvider:
            async def get_status(self) -> Dict[str, Any]:
                response = requests.get("http://localhost:4040/api/tunnels")
                data = response.json()
                return {
                    "active": bool(data.get("tunnels")),
                    "url": data["tunnels"][0]["public_url"],
                    "type": "ngrok"
                }
    """

    async def get_status(self) -> dict[str, Any]:
        """Get current tunnel status.

        Returns:
            Dictionary with tunnel status:
            {
                "active": bool,
                "url": str,
                "type": str,
                "connections": int,
                "metrics": Dict[str, Any]
            }
        """
        ...

    async def get_metrics(self) -> dict[str, Any]:
        """Get tunnel performance metrics.

        Returns:
            Dictionary with metrics:
            {
                "latency_ms": float,
                "bandwidth_up": float,
                "bandwidth_down": float,
                "total_bytes_up": int,
                "total_bytes_down": int
            }
        """
        ...


@runtime_checkable
class ResourceProvider(Protocol):
    """Protocol for resource monitoring providers.

    Implement this protocol to integrate with ResourceStatusWidget for
    custom resource monitoring (database, cache, API limits, etc.).

    Example:
        class DatabaseProvider:
            async def check_health(self) -> Dict[str, Any]:
                conn = await asyncpg.connect(self.dsn)
                start = time.perf_counter()
                await conn.fetchval("SELECT 1")
                latency = (time.perf_counter() - start) * 1000
                await conn.close()

                return {
                    "connected": True,
                    "latency_ms": latency,
                    "type": "postgresql"
                }
    """

    async def check_health(self) -> dict[str, Any]:
        """Check resource health and connectivity.

        Returns:
            Dictionary with health status:
            {
                "connected": bool,
                "latency_ms": float,
                "type": str,
                "error": str (optional)
            }
        """
        ...

    async def get_metrics(self) -> dict[str, Any]:
        """Get resource performance metrics.

        Returns:
            Dictionary with resource-specific metrics
        """
        ...


@runtime_checkable
class MetricsProvider(Protocol):
    """Protocol for metrics collection and reporting.

    Implement this protocol to integrate with various widgets that
    support external metrics systems (Prometheus, StatsD, etc.).

    Example:
        class PrometheusMetricsProvider:
            async def record_metric(self, name: str, value: float, tags: Dict[str, str]):
                self.gauge.labels(**tags).set(value)

            async def get_metrics(self) -> Dict[str, float]:
                return {
                    "requests_total": self.counter.collect(),
                    "latency_seconds": self.histogram.collect()
                }
    """

    async def record_metric(
        self, name: str, value: float, tags: dict[str, str] | None = None,
    ) -> None:
        """Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional metric tags/labels
        """
        ...

    async def get_metrics(self) -> dict[str, float]:
        """Get all collected metrics.

        Returns:
            Dictionary mapping metric names to current values
        """
        ...

    async def increment_counter(
        self, name: str, value: float = 1.0, tags: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Counter name
            value: Increment amount (default 1.0)
            tags: Optional counter tags/labels
        """
        ...
