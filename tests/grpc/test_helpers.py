#!/usr/bin/env python3
"""gRPC Testing Utilities for Python.

Provides helper functions for testing gRPC services:
- Request/response logging
- Error handling utilities
- Mock server setup
- Common test fixtures
"""

import asyncio
import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any

import grpc
from grpc import aio

logger = logging.getLogger(__name__)


class GRPCTestLogger:
    """Logger for gRPC requests and responses."""

    def __init__(self, service_name: str, verbose: bool = True) -> None:
        self.service_name = service_name
        self.verbose = verbose
        self.requests: list[dict[str, Any]] = []
        self.responses: list[dict[str, Any]] = []

    def log_request(self, method: str, request: Any) -> None:
        """Log a gRPC request."""
        entry = {
            "timestamp": time.time(),
            "method": method,
            "request": str(request),
        }
        self.requests.append(entry)

        if self.verbose:
            logger.info(f"📤 {self.service_name}.{method}")
            logger.debug("   Request: %s", request)

    def log_response(self, method: str, response: Any, duration: float) -> None:
        """Log a gRPC response."""
        entry = {
            "timestamp": time.time(),
            "method": method,
            "response": str(response),
            "duration_ms": duration * 1000,
        }
        self.responses.append(entry)

        if self.verbose:
            logger.info(f"📥 {self.service_name}.{method} ({duration * 1000:.2f}ms)")
            logger.debug("   Response: %s", response)

    def log_error(self, method: str, error: Exception, duration: float) -> None:
        """Log a gRPC error."""
        entry = {
            "timestamp": time.time(),
            "method": method,
            "error": str(error),
            "error_type": type(error).__name__,
            "duration_ms": duration * 1000,
        }
        self.responses.append(entry)

        if self.verbose:
            logger.error(f"❌ {self.service_name}.{method} failed ({duration * 1000:.2f}ms)")
            logger.error("   Error: %s", error)

    def clear(self) -> None:
        """Clear logged requests and responses."""
        self.requests.clear()
        self.responses.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about logged requests."""
        total_requests = len(self.requests)
        successful = sum(1 for r in self.responses if "error" not in r)
        failed = sum(1 for r in self.responses if "error" in r)

        durations = [r["duration_ms"] for r in self.responses if "duration_ms" in r]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0

        return {
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_requests if total_requests > 0 else 0,
            "avg_duration_ms": avg_duration,
            "max_duration_ms": max_duration,
            "min_duration_ms": min_duration,
        }


class GRPCTestClient:
    """Base class for gRPC test clients with logging and error handling."""

    def __init__(
        self,
        channel: aio.Channel,
        service_name: str,
        logger: GRPCTestLogger | None = None,
    ) -> None:
        self.channel = channel
        self.service_name = service_name
        self.logger = logger or GRPCTestLogger(service_name)

    async def call_unary(
        self,
        method_name: str,
        stub_method: Callable,
        request: Any,
        timeout_sec: float | None = None,
    ) -> Any:
        """Call a unary RPC method with logging and error handling.

        Args:
            method_name: Name of the method being called
            stub_method: The stub method to call
            request: Request message
            timeout_sec: Optional timeout in seconds

        Returns:
            Response message

        Raises:
            grpc.RpcError: If the RPC fails
        """
        self.logger.log_request(method_name, request)
        start_time = time.time()

        try:
            response = await stub_method(request, timeout=timeout_sec)
            duration = time.time() - start_time
            self.logger.log_response(method_name, response, duration)
            return response
        except grpc.RpcError as e:
            duration = time.time() - start_time
            self.logger.log_error(method_name, e, duration)
            raise

    async def call_streaming_response(
        self,
        method_name: str,
        stub_method: Callable,
        request: Any,
        timeout_sec: float | None = None,
    ) -> list[Any]:
        """Call a server-streaming RPC method with logging.

        Args:
            method_name: Name of the method being called
            stub_method: The stub method to call
            request: Request message
            timeout_sec: Optional timeout in seconds

        Returns:
            List of response messages

        Raises:
            grpc.RpcError: If the RPC fails
        """
        self.logger.log_request(method_name, request)
        start_time = time.time()
        responses = []

        try:
            responses.extend([response async for response in stub_method(request, timeout=timeout_sec)])

            duration = time.time() - start_time
            self.logger.log_response(method_name, f"Received {len(responses)} messages", duration)
            return responses
        except grpc.RpcError as e:
            duration = time.time() - start_time
            self.logger.log_error(method_name, e, duration)
            raise


@asynccontextmanager
async def grpc_test_channel(
    host: str = "localhost",
    port: int = 50051,
    insecure: bool = True,
    options: list | None = None,
) -> None:
    """Create a test gRPC channel with proper cleanup.

    Args:
        host: Server host
        port: Server port
        insecure: If True, use insecure channel
        options: Optional channel options

    Yields:
        grpc.aio.Channel
    """
    target = f"{host}:{port}"

    if insecure:
        channel = aio.insecure_channel(target, options=options)
    else:
        # For secure channels, you'd add credentials here
        credentials = grpc.ssl_channel_credentials()
        channel = aio.secure_channel(target, credentials, options=options)

    try:
        yield channel
    finally:
        await channel.close()


async def wait_for_server(
    host: str = "localhost",
    port: int = 50051,
    timeout_sec: float = 10.0,
    interval: float = 0.5,
) -> bool:
    """Wait for gRPC server to be ready.

    Args:
        host: Server host
        port: Server port
        timeout_sec: Maximum time to wait (seconds)
        interval: Time between connection attempts (seconds)

    Returns:
        True if server is ready, False if timeout

    Example:
        if await wait_for_server("localhost", 50051, timeout_sec=5.0):
            print("Server is ready!")
        else:
            print("Server failed to start")
    """
    start_time = time.time()
    target = f"{host}:{port}"

    while time.time() - start_time < timeout_sec:
        try:
            async with aio.insecure_channel(target) as channel:
                # Try to check channel state
                await channel.channel_ready()
                logger.info("✅ gRPC server ready at %s", target)
                return True
        except Exception:
            await asyncio.sleep(interval)

    logger.error("❌ gRPC server at %s not ready after %ss", target, timeout_sec)
    return False


def assert_grpc_error(
    error: grpc.RpcError,
    expected_code: grpc.StatusCode,
    expected_message: str | None = None,
) -> None:
    """Assert that a gRPC error has the expected status code and message.

    Args:
        error: The gRPC error
        expected_code: Expected status code
        expected_message: Optional expected message substring

    Raises:
        AssertionError: If assertions fail

    Example:
        try:
            await client.some_method(invalid_request)
        except grpc.RpcError as e:
            assert_grpc_error(e, grpc.StatusCode.INVALID_ARGUMENT, "invalid item_id")
    """
    assert isinstance(error, grpc.RpcError), f"Expected grpc.RpcError, got {type(error)}"
    code = getattr(error, "code", lambda: None)()
    assert code == expected_code, f"Expected status code {expected_code}, got {code}"

    if expected_message:
        details = getattr(error, "details", lambda: None)()
        # Add null check for details() which may return None or str
        assert details and expected_message in details, (
            f"Expected message containing '{expected_message}', got '{details}'"
        )


class MockGRPCServicer:
    """Base class for mock gRPC servicers in tests."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def record_call(self, method: str, request: Any) -> None:
        """Record a method call for verification."""
        self.calls.append({
            "method": method,
            "request": request,
            "timestamp": time.time(),
        })

    def get_call_count(self, method: str | None = None) -> int:
        """Get the number of calls made (optionally filtered by method)."""
        if method:
            return sum(1 for call in self.calls if call["method"] == method)
        return len(self.calls)

    def get_last_request(self, method: str) -> Any | None:
        """Get the last request for a specific method."""
        for call in reversed(self.calls):
            if call["method"] == method:
                return call["request"]
        return None

    def clear_calls(self) -> None:
        """Clear recorded calls."""
        self.calls.clear()


# Example usage in tests:
"""
import pytest
from tests.grpc.test_helpers import (
    GRPCTestClient,
    GRPCTestLogger,
    grpc_test_channel,
    wait_for_server,
    assert_grpc_error,
)

@pytest.mark.asyncio
async def test_graph_service():
    # Wait for server to be ready
    assert await wait_for_server(timeout=5.0)

    # Create test channel and client
    async with grpc_test_channel() as channel:
        logger = GRPCTestLogger("GraphService", verbose=True)
        stub = GraphServiceStub(channel)
        client = GRPCTestClient(channel, "GraphService", logger)

        # Make a request
        request = ImpactRequest(
            item_id="test-123",
            project_id="proj-456",
            direction="both",
            max_depth=2,
        )

        response = await client.call_unary(
            "AnalyzeImpact",
            stub.AnalyzeImpact,
            request,
            timeout=5.0,
        )

        # Verify response
        assert response.total_count > 0

        # Check stats
        stats = logger.get_stats()
        assert stats["total_requests"] == 1
        assert stats["successful"] == 1

@pytest.mark.asyncio
async def test_error_handling():
    async with grpc_test_channel() as channel:
        stub = GraphServiceStub(channel)
        client = GRPCTestClient(channel, "GraphService")

        # Test invalid request
        try:
            request = ImpactRequest(item_id="")  # Invalid empty ID
            await client.call_unary("AnalyzeImpact", stub.AnalyzeImpact, request)
            pytest.fail("Should have raised error")
        except grpc.RpcError as e:
            assert_grpc_error(e, grpc.StatusCode.INVALID_ARGUMENT, "item_id")
"""
