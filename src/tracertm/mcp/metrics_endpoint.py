"""Metrics endpoint for exposing Prometheus metrics via HTTP.

Provides a simple HTTP server that exposes metrics at /metrics endpoint.
Can be run standalone or integrated with the MCP server.
"""

from __future__ import annotations

import errno
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from tracertm.mcp.metrics import MetricsExporter, mcp_registry

logger = logging.getLogger(__name__)

# System error codes
EADDRINUSE = errno.EADDRINUSE  # Address already in use (48 on macOS, 98 on Linux)


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint."""

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/metrics":
            self.send_metrics()
        elif self.path == "/health":
            self.send_health()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def send_metrics(self) -> None:
        """Send Prometheus metrics."""
        try:
            metrics = MetricsExporter.export_metrics(mcp_registry)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(metrics)
        except Exception as e:
            logger.exception("Error exporting metrics")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())

    def send_health(self) -> None:
        """Send health check response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "healthy", "service": "tracertm-mcp"}')

    def log_message(self, format: str, *args: object) -> None:
        """Override to use our logger instead of stderr."""
        logger.debug("[METRICS_ENDPOINT] %s", format % args)


class MetricsServer:
    """HTTP server for exposing Prometheus metrics."""

    def __init__(self, host: str = "0.0.0.0", port: int = 9090) -> None:  # nosec B104 -- configurable bind address
        """Initialize metrics server.

        Args:
            host: Host to bind to (default 0.0.0.0 for container compatibility)
            port: Port to bind to
        """
        self.host = host
        self.port = port
        self.server: HTTPServer | None = None
        self.thread: Thread | None = None

    def start(self) -> None:
        """Start the metrics server in a background thread."""
        if self.server is not None:
            logger.warning("Metrics server already running")
            return

        try:
            self.server = HTTPServer((self.host, self.port), MetricsHandler)
            self.thread = Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info("Metrics server started at http://%s:%s/metrics", self.host, self.port)
        except OSError as e:
            if e.errno == EADDRINUSE and (
                os.getenv("PYTEST_CURRENT_TEST") or os.getenv("PYTEST_RUNNING") or os.getenv("PYTEST_WORKER")
            ):
                logger.warning("Metrics server port already in use during tests; continuing without metrics")
                return
            logger.exception("Failed to start metrics server")
            raise
        except Exception:
            logger.exception("Failed to start metrics server")
            raise

    def stop(self) -> None:
        """Stop the metrics server."""
        if self.server is None:
            logger.warning("Metrics server not running")
            return

        try:
            self.server.shutdown()
            self.server = None
            self.thread = None
            logger.info("Metrics server stopped")
        except Exception:
            logger.exception("Error stopping metrics server")
            raise

    def is_running(self) -> bool:
        """Check if server is running.

        Returns:
            True if running, False otherwise
        """
        return self.server is not None


# Global metrics server instance
_metrics_server: MetricsServer | None = None


def get_metrics_server(host: str = "0.0.0.0", port: int = 9090) -> MetricsServer:  # nosec B104
    """Get or create global metrics server instance.

    Args:
        host: Host to bind to
        port: Port to bind to

    Returns:
        MetricsServer instance
    """
    global _metrics_server
    if _metrics_server is None:
        _metrics_server = MetricsServer(host, port)
    return _metrics_server


def start_metrics_server(host: str = "0.0.0.0", port: int = 9090) -> MetricsServer:  # nosec B104
    """Start the global metrics server.

    Args:
        host: Host to bind to
        port: Port to bind to

    Returns:
        Started MetricsServer instance
    """
    server = get_metrics_server(host, port)
    if not server.is_running():
        server.start()
    return server


__all__ = [
    "MetricsHandler",
    "MetricsServer",
    "get_metrics_server",
    "start_metrics_server",
]
