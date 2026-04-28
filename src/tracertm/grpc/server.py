"""gRPC server bootstrap for Python backend services."""

from __future__ import annotations

import logging
import os

from grpc import aio

from tracertm.grpc.spec_analytics_service import SpecAnalyticsService
from tracertm.proto.tracertm.v1 import tracertm_pb2_grpc

logger = logging.getLogger(__name__)


def _grpc_enabled() -> bool:
    return os.getenv("PYTHON_GRPC_ENABLED", "true").lower() == "true"


def _grpc_bind_addr() -> str:
    host = os.getenv("PYTHON_GRPC_HOST", "127.0.0.1")
    port = os.getenv("PYTHON_GRPC_PORT", "9092")
    return f"{host}:{port}"


async def start_grpc_server() -> aio.Server | None:
    """Start the gRPC server if enabled; returns server or None."""
    if not _grpc_enabled():
        logger.info("gRPC server disabled via PYTHON_GRPC_ENABLED=false")
        return None

    server = aio.server(
        options=[
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 10000),
        ],
    )
    tracertm_pb2_grpc.add_SpecAnalyticsServiceServicer_to_server(SpecAnalyticsService(), server)

    bind_addr = _grpc_bind_addr()
    server.add_insecure_port(bind_addr)
    await server.start()
    logger.info("gRPC server listening on %s", bind_addr)
    return server


async def stop_grpc_server(server: aio.Server | None) -> None:
    """Stop the gRPC server if running."""
    if server is None:
        return
    await server.stop(grace=5)
    logger.info("gRPC server stopped")
