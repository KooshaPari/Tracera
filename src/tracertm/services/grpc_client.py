"""gRPC Client for TraceRTM Go Backend Services.

This module provides a client for calling gRPC services implemented in the Go backend.
Primary use case: Python services calling Go's GraphService for high-performance graph operations.
"""

import asyncio
import logging
import os
import types
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Self

import grpc
from grpc import aio

from tracertm.proto import tracertm_pb2, tracertm_pb2_grpc

logger = logging.getLogger(__name__)


class GoBackendClient:
    """Client for calling Go backend gRPC services.

    Provides methods for graph analysis operations implemented in Go:
    - Impact analysis
    - Cycle detection
    - Path calculation
    - Graph update streaming

    Example:
        >>> async with GoBackendClient() as client:
        ...     response = await client.analyze_impact(
        ...         item_id="item-123", project_id="proj-456", direction="upstream", max_depth=3
        ...     )
        ...     print(f"Found {response.total_count} impacted items")
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        max_retries: int = 3,
        timeout: int = 30,
    ) -> None:
        """Initialize the gRPC client.

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

        logger.info("Initialized GoBackendClient for %s", self.address)

    async def connect(self) -> None:
        """Establish connection to the gRPC server."""
        if self._channel is not None:
            logger.warning("Already connected to gRPC server")
            return

        logger.info("Connecting to Go backend at %s", self.address)

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
        except Exception:
            logger.exception("Failed to connect to Go backend")
            await self.close()
            raise

    async def _test_connection(self) -> None:
        """Test the gRPC connection with a simple health check."""
        # For now, we'll skip the health check
        # In production, you'd call a health check endpoint

    async def close(self) -> None:
        """Close the gRPC connection."""
        if self._channel:
            logger.info("Closing gRPC connection")
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: types.TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    @asynccontextmanager
    async def _retry_context(self, operation_name: str) -> AsyncGenerator[None, None]:
        """Context manager for retry logic with exponential backoff.

        Args:
            operation_name: Name of the operation for logging
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                yield
            except grpc.RpcError as e:
                last_error = e
                code_fn = getattr(e, "code", lambda: None)
                details_fn = getattr(e, "details", lambda: "")
                code = code_fn() if callable(code_fn) else None
                details = details_fn() if callable(details_fn) else ""

                # Check if error is retryable
                if code in {
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                }:
                    if attempt < self.max_retries - 1:
                        wait_time = 2**attempt  # Exponential backoff
                        logger.warning(
                            "%s failed (attempt %s/%s): %s - %s. Retrying in %ss...",
                            operation_name,
                            attempt + 1,
                            self.max_retries,
                            code,
                            details,
                            wait_time,
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.exception("%s failed after %s attempts", operation_name, self.max_retries)
                else:
                    # Non-retryable error
                    logger.exception("%s failed with non-retryable error: %s - %s", operation_name, code, details)
                    raise
            except Exception as e:
                last_error = e
                logger.exception("%s failed with unexpected error", operation_name)
                raise
            else:
                return

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
        """Analyze the impact of changes to an item.

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
            msg = "Not connected to gRPC server. Call connect() first."
            raise RuntimeError(msg)

        request = tracertm_pb2.AnalyzeImpactRequest(
            item_id=item_id,
            project_id=project_id,
            direction=direction,
            max_depth=max_depth,
            link_types=link_types or [],
        )

        logger.debug("Analyzing impact for item %s (direction=%s, max_depth=%s)", item_id, direction, max_depth)

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

        logger.info("Impact analysis complete: %s items impacted", result["total_count"])
        return result

    async def find_cycles(
        self,
        project_id: str,
        link_types: list[str] | None = None,
        max_cycle_length: int = 0,
    ) -> dict[str, Any]:
        """Find circular dependencies in the project graph.

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
            msg = "Not connected to gRPC server. Call connect() first."
            raise RuntimeError(msg)

        request = tracertm_pb2.FindCyclesRequest(
            project_id=project_id,
            link_types=link_types or [],
            max_cycle_length=max_cycle_length,
        )

        logger.debug("Finding cycles in project %s", project_id)

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

        logger.info("Cycle detection complete: %s cycles found", result["total_count"])
        return result

    async def calculate_path(
        self,
        project_id: str,
        source_item_id: str,
        target_item_id: str,
        link_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Calculate the shortest path between two items.

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
            msg = "Not connected to gRPC server. Call connect() first."
            raise RuntimeError(msg)

        request = tracertm_pb2.CalculatePathRequest(
            project_id=project_id,
            source_item_id=source_item_id,
            target_item_id=target_item_id,
            link_types=link_types or [],
        )

        logger.debug("Calculating path from %s to %s", source_item_id, target_item_id)

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

        logger.info(
            "Path calculation complete: path_exists=%s, length=%s", result["path_exists"], result["path_length"]
        )
        return result


# Convenience function for one-off requests
async def analyze_impact_sync(
    item_id: str,
    project_id: str,
    direction: str = "both",
    max_depth: int = 0,
    link_types: list[str] | None = None,
) -> dict[str, Any]:
    """Convenience function for one-off impact analysis.

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
