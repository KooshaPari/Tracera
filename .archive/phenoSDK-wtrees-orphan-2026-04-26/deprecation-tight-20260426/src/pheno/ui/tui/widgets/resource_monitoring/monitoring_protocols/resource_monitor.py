"""Protocol for custom resource monitoring implementations.

This module defines the ResourceMonitor protocol for custom resource monitoring logic.
"""

from typing import Protocol


class ResourceMonitor(Protocol):
    """Protocol for custom resource monitoring implementations.

    Implement this protocol to provide custom resource monitoring logic.
    The widget will call these methods to gather metrics.

    Example:
        class CloudResourceMonitor:
            async def get_cpu_usage(self) -> float:
                # Query cloud provider API
                return await cloud_api.get_cpu_percent()

            async def get_memory_usage(self) -> Dict[str, float]:
                stats = await cloud_api.get_memory_stats()
                return {
                    "used_mb": stats.used / 1024 / 1024,
                    "percent": stats.percent
                }

            async def get_disk_usage(self) -> float:
                return await cloud_api.get_disk_percent()

            async def get_network_bandwidth(self) -> Dict[str, float]:
                stats = await cloud_api.get_network_stats()
                return {
                    "upload_kbps": stats.tx_kbps,
                    "download_kbps": stats.rx_kbps
                }
    """

    async def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage (0-100).
        """
        ...

    async def get_memory_usage(self) -> dict[str, float]:
        """Get memory usage statistics.

        Returns:
            Dict with keys:
                - used_mb: Used memory in megabytes
                - percent: Usage percentage (0-100)
        """
        ...

    async def get_disk_usage(self) -> float:
        """
        Get disk usage percentage (0-100).
        """
        ...

    async def get_network_bandwidth(self) -> dict[str, float]:
        """Get network bandwidth statistics.

        Returns:
            Dict with keys:
                - upload_kbps: Upload speed in KB/s
                - download_kbps: Download speed in KB/s
        """
        ...
