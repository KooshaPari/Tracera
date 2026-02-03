"""
gRPC Client for TraceRTM Go Backend Services

This module provides a client for calling gRPC services implemented in the Go backend.
Primary use case: Python services calling Go's GraphService for high-performance graph operations.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

import grpc
from grpc import aio  # type: ignore[possibly-missing-import]

from tracertm.proto import tracertm_pb2, tracertm_pb2_grpc  # type: ignore[attr-defined]

logger = logging.getLogger(__name__)


class GoBackendClient:
    """
    Client for calling Go backend gRPC services.

    Provides methods for graph analysis operations implemented in Go:
    - Impact analysis
    - Cycle detection
    - Path calculation
    - Graph update streaming

    Example:
        >>> async with GoBackendClient() as client:
        ...     response = await client.analyze_impact(
        ...         item_id="item-123",
        ...         project_id="proj-456",
        ...         direction="upstream",
        ...         max_depth=3
        ...     )
        ...     print(f"Found {response.total_count} impacted items")
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        max_retries: int = 3,
        timeout: int = 30,
    ):
        """
        Initialize the gRPC client.

        Args:
            host: Go backend hostname (default: from GRPC_GO_BACKEND_HOST env or localhost)
            port: Go backend gRPC port (default: 9090)
            max_retries: Maximum number of retry attempts for transient failures
            timeout: Request timeout in seconds
        """
        # Parse host and port from environment or defaults
        default_host = os.getenv("GRPC_GO_BACKEND_HOST", "localhost:9090")
        if ":" in default_host:
            default_host_part, default_port_part = default_host.split(":")
            host = host or default_host_part
            port = port or int(default_port_part)
        else:
            host = host or default_host
            port = port or 9090

        self.host = host
        self.port = port
        self.address = f"{host}:{port}"
        self.max_retries = max_retries
        self.timeout = timeout

        self._channel: aio.Channel | None = None
        self._stub: tracertm_pb2_grpc.GraphServiceStub | None = None

        logger.info(f"Initialized GoBackendClient for {self.address}")

    async def connect(self):
        """Establish connection to the gRPC server."""
        if self._channel is not None:
            logger.warning("Already connected to gRPC server")
            return

        logger.info(f"Connecting to Go backend at {self.address}")

        # Create channel with connection pooling
        self._channel = aio.insecure_channel(
            self.address,
            options=[
                ("grpc.keepalive_time_ms", 30000),
                ("grpc.keepalive_timeout_ms", 10000),
                ("grpc.keepalive_permit_without_calls", True),
                ("grpc.http2.max_pings_without_data", 0),
                ("grpc.max_receive_message_length", 10 * 1024 * 1024),  # 10MB
                ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ],
        )

        self._stub = tracertm_pb2_grpc.GraphServiceStub(self._channel)

        # Test connection
        try:
            await self._test_connection()
            logger.info("Successfully connected to Go backend")
        except Exception as e:
            logger.error(f"Failed to connect to Go backend: {e}")
            await self.close()
            raise

    async def _test_connection(self):
        """Test the gRPC connection with a simple health check."""
        # For now, we'll skip the health check
        # In production, you'd call a health check endpoint

    async def close(self):
        """Close the gRPC connection."""
        if self._channel:
            logger.info("Closing gRPC connection")
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    @asynccontextmanager
    async def _retry_context(self, operation_name: str):
        """
        Context manager for retry logic with exponential backoff.

        Args:
            operation_name: Name of the operation for logging
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                yield
                return
            except grpc.RpcError as e:
                last_error = e
                code_fn = getattr(e, "code", lambda: None)
                details_fn = getattr(e, "details", lambda: b"")
                code = code_fn() if callable(code_fn) else None
                details = details_fn() if callable(details_fn) else b""

                # Check if error is retryable
                if code in (
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                ):
                    if attempt < self.max_retries - 1:
                        wait_time = 2**attempt  # Exponential backoff
                        logger.warning(
                            f"{operation_name} failed (attempt {attempt + 1}/{self.max_retries}): "
                            f"{code} - {details}. Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"{operation_name} failed after {self.max_retries} attempts")
                else:
                    # Non-retryable error
                    logger.error(f"{operation_name} failed with non-retryable error: {code} - {details}")
                    raise
            except Exception as e:
                last_error = e
                logger.error(f"{operation_name} failed with unexpected error: {e}")
                raise

        # If we get here, all retries failed
        if last_error:
            raise last_error

    async def analyze_impact(
        self,
        item_id: str,
        project_id: str,
        direction: str = "both",
        max_depth: int = 0,
        link_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze the impact of changes to an item.

        Args:
            item_id: ID of the item to analyze
            project_id: Project ID
            direction: Direction of impact analysis ("upstream", "downstream", or "both")
            max_depth: Maximum traversal depth (0 = unlimited)
            link_types: Optional list of link types to filter by

        Returns:
            Dictionary containing:
                - item_id: Source item ID
                - impacted_items: List of impacted items with metadata
                - total_count: Total number of impacted items
                - items_by_type: Count of impacted items by type
                - items_by_depth: Count of items at each depth level
                - critical_paths: List of item IDs on critical paths

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        if not self._stub:
            raise RuntimeError("Not connected to gRPC server. Call connect() first.")

        request = tracertm_pb2.ImpactRequest(
            item_id=item_id,
            project_id=project_id,
            direction=direction,
            max_depth=max_depth,
            link_types=link_types or [],
        )

        logger.debug(f"Analyzing impact for item {item_id} (direction={direction}, max_depth={max_depth})")

        async with self._retry_context("analyze_impact"):
            response = await self._stub.AnalyzeImpact(
                request,
                timeout=self.timeout,
            )

        # Convert protobuf response to dict
        result = {
            "item_id": response.item_id,
            "impacted_items": [
                {
                    "id": item.id,
                    "type": item.type,
                    "title": item.title,
                    "depth": item.depth,
                    "link_type": item.link_type,
                    "impact_score": item.impact_score,
                }
                for item in response.impacted_items
            ],
            "total_count": response.total_count,
            "items_by_type": dict(response.items_by_type),
            "items_by_depth": dict(response.items_by_depth),
            "critical_paths": list(response.critical_paths),
        }

        logger.info(f"Impact analysis complete: {result['total_count']} items impacted")
        return result

    async def find_cycles(
        self,
        project_id: str,
        link_types: list[str] | None = None,
        max_cycle_length: int = 0,
    ) -> dict[str, Any]:
        """
        Find circular dependencies in the project graph.

        Args:
            project_id: Project ID
            link_types: Optional list of link types to filter by
            max_cycle_length: Maximum cycle size to detect (0 = unlimited)

        Returns:
            Dictionary containing:
                - cycles: List of detected cycles
                - total_count: Total number of cycles
                - has_cycles: Boolean indicating if any cycles exist
        """
        if not self._stub:
            raise RuntimeError("Not connected to gRPC server. Call connect() first.")

        request = tracertm_pb2.CycleRequest(
            project_id=project_id,
            link_types=link_types or [],
            max_cycle_length=max_cycle_length,
        )

        logger.debug(f"Finding cycles in project {project_id}")

        async with self._retry_context("find_cycles"):
            response = await self._stub.FindCycles(
                request,
                timeout=self.timeout,
            )

        result = {
            "cycles": [
                {
                    "item_ids": list(cycle.item_ids),
                    "link_types": list(cycle.link_types),
                    "length": cycle.length,
                    "severity": cycle.severity,
                }
                for cycle in response.cycles
            ],
            "total_count": response.total_count,
            "has_cycles": response.has_cycles,
        }

        logger.info(f"Cycle detection complete: {result['total_count']} cycles found")
        return result

    async def calculate_path(
        self,
        project_id: str,
        source_item_id: str,
        target_item_id: str,
        link_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Calculate the shortest path between two items.

        Args:
            project_id: Project ID
            source_item_id: Starting item ID
            target_item_id: Target item ID
            link_types: Optional list of link types to filter by

        Returns:
            Dictionary containing:
                - item_ids: List of item IDs in the path
                - link_types: List of link types connecting the path
                - path_length: Number of items in the path
                - path_exists: Boolean indicating if a path exists
                - path_weight: Total weight/cost of the path
        """
        if not self._stub:
            raise RuntimeError("Not connected to gRPC server. Call connect() first.")

        request = tracertm_pb2.PathRequest(
            project_id=project_id,
            source_item_id=source_item_id,
            target_item_id=target_item_id,
            link_types=link_types or [],
        )

        logger.debug(f"Calculating path from {source_item_id} to {target_item_id}")

        async with self._retry_context("calculate_path"):
            response = await self._stub.CalculatePath(
                request,
                timeout=self.timeout,
            )

        result = {
            "item_ids": list(response.item_ids),
            "link_types": list(response.link_types),
            "path_length": response.path_length,
            "path_exists": response.path_exists,
            "path_weight": response.path_weight,
        }

        logger.info(f"Path calculation complete: path_exists={result['path_exists']}, length={result['path_length']}")
        return result


# Convenience function for one-off requests
async def analyze_impact_sync(
    item_id: str,
    project_id: str,
    direction: str = "both",
    max_depth: int = 0,
    link_types: list[str] | None = None,
) -> dict[str, Any]:
    """
    Convenience function for one-off impact analysis.

    Opens a connection, performs the analysis, and closes the connection.
    For multiple requests, use the GoBackendClient context manager instead.
    """
    async with GoBackendClient() as client:
        return await client.analyze_impact(
            item_id=item_id,
            project_id=project_id,
            direction=direction,
            max_depth=max_depth,
            link_types=link_types,
        )
