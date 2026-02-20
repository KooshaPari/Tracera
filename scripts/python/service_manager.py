#!/usr/bin/env python3
"""Service health check and auto-start manager for TraceRTM.

This script ensures all required infrastructure services are running before
starting the TraceRTM application services. It detects down services and
automatically starts them via Homebrew services.
"""

import socket
import subprocess
import sys
import time
from dataclasses import dataclass


@dataclass
class Service:
    """Configuration for a managed service."""

    name: str
    port: int
    brew_name: str
    required: bool = True


# Services managed by this script (check + start via brew when down)
# required=True: script exits non-zero if start fails; required=False: try to start but don't fail run
# PostgreSQL: try @17 then @14 then default (fallback applied in ensure_services_running)
# MinIO: required for S3-compatible storage (install: brew install minio or tap minio/minio)
SERVICES = [
    Service("PostgreSQL", 5432, "postgresql@17", required=True),
    Service("Redis", 6379, "redis", required=True),
    Service("Neo4j", 7687, "neo4j", required=True),
    Service("NATS", 4222, "nats-server", required=True),
    Service("Temporal", 7233, "temporal", required=True),
    Service("MinIO (S3)", 9000, "minio", required=True),
]


def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open and accepting connections.

    Args:
        host: Hostname or IP address to check
        port: Port number to check
        timeout: Connection timeout in seconds

    Returns:
        True if port is open, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_service(brew_name: str, fallbacks: list[str] | None = None) -> bool:
    """Start a service using Homebrew services.

    Args:
        brew_name: Name of the Homebrew formula/service
        fallbacks: Optional list of alternative formulae to try if brew_name fails

    Returns:
        True if service started successfully, False otherwise
    """
    to_try = [brew_name] + (fallbacks or [])
    for name in to_try:
        try:
            subprocess.run(
                ["brew", "services", "start", name],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            if e.stderr:
                pass
    return False


def ensure_services_running(retries: int = 5, delay: int = 3) -> bool:
    """Ensure all required services are running, starting them if needed.

    Args:
        retries: Number of retry attempts for service startup
        delay: Delay in seconds between retries

    Returns:
        True if all required services are running, False otherwise
    """
    all_healthy = True

    for service in SERVICES:
        # Check if service is already running
        if check_port("localhost", service.port):
            continue

        # Service is down - attempt to start it (required and optional)

        fallbacks = ["postgresql@14", "postgresql"] if service.name == "PostgreSQL" else None
        if not start_service(service.brew_name, fallbacks=fallbacks):
            if service.required:
                all_healthy = False
            continue

        # Wait for service to come up with retry logic
        service_started = False
        for _attempt in range(1, retries + 1):
            time.sleep(delay)
            if check_port("localhost", service.port):
                service_started = True
                break

        if not service_started and service.required:
            all_healthy = False

    if all_healthy:
        pass

    return all_healthy


def main() -> int:
    """Main entry point.

    Returns:
        0 if all services are healthy, 1 otherwise
    """
    return 0 if ensure_services_running() else 1


if __name__ == "__main__":
    sys.exit(main())
