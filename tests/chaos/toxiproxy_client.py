"""Toxiproxy HTTP API client for chaos engineering.

Provides a Python client to interact with Toxiproxy's REST API for creating
proxies and injecting network-level failures (latency, bandwidth limits, etc.).
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ToxiproxyClient:
    """Client for Toxiproxy HTTP API.

    Toxiproxy is a TCP proxy that can simulate network conditions and failures:
    - Latency injection
    - Bandwidth limiting
    - Connection cuts
    - Slow connections
    - Timeouts
    """

    def __init__(self, base_url: str = "http://localhost:8474") -> None:
        """Initialize Toxiproxy client.

        Args:
            base_url: Toxiproxy HTTP API URL (default: http://localhost:8474)
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=10.0)

    async def version(self) -> str:
        """Get Toxiproxy version."""
        response = await self.client.get(f"{self.base_url}/version")
        response.raise_for_status()
        return response.text

    async def list_proxies(self) -> dict[str, Any]:
        """List all proxies."""
        response = await self.client.get(f"{self.base_url}/proxies")
        response.raise_for_status()
        return response.json()

    async def create_proxy(
        self,
        name: str,
        listen: str,
        upstream: str,
        enabled: bool = True,
    ) -> dict[str, Any]:
        """Create a new proxy.

        Args:
            name: Proxy name (unique identifier)
            listen: Listen address (e.g., "0.0.0.0:15432")
            upstream: Upstream address (e.g., "localhost:5432")
            enabled: Whether proxy is initially enabled

        Returns:
            Proxy configuration
        """
        payload = {
            "name": name,
            "listen": listen,
            "upstream": upstream,
            "enabled": enabled,
        }

        response = await self.client.post(
            f"{self.base_url}/proxies",
            json=payload,
        )
        response.raise_for_status()
        logger.info("Created proxy '%s': %s -> %s", name, listen, upstream)
        return response.json()

    async def get_proxy(self, name: str) -> dict[str, Any]:
        """Get proxy configuration by name."""
        response = await self.client.get(f"{self.base_url}/proxies/{name}")
        response.raise_for_status()
        return response.json()

    async def delete_proxy(self, name: str) -> None:
        """Delete a proxy."""
        response = await self.client.delete(f"{self.base_url}/proxies/{name}")
        response.raise_for_status()
        logger.info("Deleted proxy '%s'", name)

    async def enable_proxy(self, name: str) -> dict[str, Any]:
        """Enable a proxy."""
        payload = {"enabled": True}
        response = await self.client.post(
            f"{self.base_url}/proxies/{name}",
            json=payload,
        )
        response.raise_for_status()
        logger.info("Enabled proxy '%s'", name)
        return response.json()

    async def disable_proxy(self, name: str) -> dict[str, Any]:
        """Disable a proxy (cuts all connections)."""
        payload = {"enabled": False}
        response = await self.client.post(
            f"{self.base_url}/proxies/{name}",
            json=payload,
        )
        response.raise_for_status()
        logger.info("Disabled proxy '%s'", name)
        return response.json()

    # Toxic management

    async def add_toxic(
        self,
        proxy_name: str,
        toxic_name: str,
        toxic_type: str,
        attributes: dict[str, Any],
        toxicity: float = 1.0,
        stream: str = "downstream",
    ) -> dict[str, Any]:
        """Add a toxic to a proxy.

        Args:
            proxy_name: Target proxy name
            toxic_name: Unique toxic identifier
            toxic_type: Type of toxic (latency, bandwidth, slow_close, timeout, etc.)
            attributes: Toxic-specific attributes
            toxicity: Probability (0.0-1.0) of applying toxic
            stream: Apply to "upstream", "downstream", or "both"

        Returns:
            Toxic configuration
        """
        payload = {
            "name": toxic_name,
            "type": toxic_type,
            "attributes": attributes,
            "toxicity": toxicity,
            "stream": stream,
        }

        response = await self.client.post(
            f"{self.base_url}/proxies/{proxy_name}/toxics",
            json=payload,
        )
        response.raise_for_status()
        logger.info("Added toxic '%s' (%s) to proxy '%s'", toxic_name, toxic_type, proxy_name)
        return response.json()

    async def list_toxics(self, proxy_name: str) -> list[dict[str, Any]]:
        """List all toxics for a proxy."""
        response = await self.client.get(f"{self.base_url}/proxies/{proxy_name}/toxics")
        response.raise_for_status()
        return response.json()

    async def get_toxic(self, proxy_name: str, toxic_name: str) -> dict[str, Any]:
        """Get a specific toxic."""
        response = await self.client.get(f"{self.base_url}/proxies/{proxy_name}/toxics/{toxic_name}")
        response.raise_for_status()
        return response.json()

    async def update_toxic(
        self,
        proxy_name: str,
        toxic_name: str,
        attributes: dict[str, Any],
        toxicity: float | None = None,
    ) -> dict[str, Any]:
        """Update a toxic's attributes."""
        payload: dict[str, Any] = {"attributes": attributes}
        if toxicity is not None:
            payload["toxicity"] = toxicity

        response = await self.client.post(
            f"{self.base_url}/proxies/{proxy_name}/toxics/{toxic_name}",
            json=payload,
        )
        response.raise_for_status()
        logger.info("Updated toxic '%s' on proxy '%s'", toxic_name, proxy_name)
        return response.json()

    async def remove_toxic(self, proxy_name: str, toxic_name: str) -> None:
        """Remove a toxic from a proxy."""
        response = await self.client.delete(f"{self.base_url}/proxies/{proxy_name}/toxics/{toxic_name}")
        response.raise_for_status()
        logger.info("Removed toxic '%s' from proxy '%s'", toxic_name, proxy_name)

    # Convenience methods for common toxics

    async def add_latency(
        self,
        proxy_name: str,
        latency_ms: int,
        jitter_ms: int = 0,
        toxicity: float = 1.0,
        stream: str = "downstream",
    ) -> dict[str, Any]:
        """Add latency toxic.

        Args:
            proxy_name: Target proxy
            latency_ms: Latency in milliseconds
            jitter_ms: Jitter (randomness) in milliseconds
            toxicity: Probability of applying
            stream: downstream/upstream/both
        """
        return await self.add_toxic(
            proxy_name=proxy_name,
            toxic_name=f"latency_{proxy_name}",
            toxic_type="latency",
            attributes={"latency": latency_ms, "jitter": jitter_ms},
            toxicity=toxicity,
            stream=stream,
        )

    async def add_bandwidth_limit(
        self,
        proxy_name: str,
        rate_kbps: int,
        stream: str = "downstream",
    ) -> dict[str, Any]:
        """Add bandwidth limit toxic.

        Args:
            proxy_name: Target proxy
            rate_kbps: Bandwidth limit in KB/s
            stream: downstream/upstream/both
        """
        return await self.add_toxic(
            proxy_name=proxy_name,
            toxic_name=f"bandwidth_{proxy_name}",
            toxic_type="bandwidth",
            attributes={"rate": rate_kbps},
            toxicity=1.0,
            stream=stream,
        )

    async def add_timeout(
        self,
        proxy_name: str,
        timeout_ms: int,
        stream: str = "downstream",
    ) -> dict[str, Any]:
        """Add timeout toxic (connections hang for specified duration).

        Args:
            proxy_name: Target proxy
            timeout_ms: Timeout in milliseconds
            stream: downstream/upstream/both
        """
        return await self.add_toxic(
            proxy_name=proxy_name,
            toxic_name=f"timeout_{proxy_name}",
            toxic_type="timeout",
            attributes={"timeout": timeout_ms},
            toxicity=1.0,
            stream=stream,
        )

    async def add_slow_close(
        self,
        proxy_name: str,
        delay_ms: int,
        stream: str = "downstream",
    ) -> dict[str, Any]:
        """Add slow_close toxic (delays connection close).

        Args:
            proxy_name: Target proxy
            delay_ms: Delay in milliseconds before close
            stream: downstream/upstream/both
        """
        return await self.add_toxic(
            proxy_name=proxy_name,
            toxic_name=f"slow_close_{proxy_name}",
            toxic_type="slow_close",
            attributes={"delay": delay_ms},
            toxicity=1.0,
            stream=stream,
        )

    async def cleanup_all(self) -> None:
        """Remove all proxies and toxics (cleanup after tests)."""
        try:
            proxies = await self.list_proxies()
            for proxy_name in proxies:
                await self.delete_proxy(proxy_name)
            logger.info("Cleaned up all Toxiproxy proxies")
        except Exception as e:
            logger.warning("Error during Toxiproxy cleanup: %s", e)
        finally:
            await self.client.aclose()
