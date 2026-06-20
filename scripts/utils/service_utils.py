#!/usr/bin/env python3
"""Service utilities for development.

Provides helper functions for checking, starting, and stopping
services during development.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Any

import redis
from neo4j import GraphDatabase


def wait_for_service(check_func: Any, _service_name: str, max_wait: int = 30, interval: float = 1.0) -> bool:
    """Wait for a service to become available.

    Args:
        check_func: Function that returns True when service is ready
        service_name: Name of service for logging
        max_wait: Maximum seconds to wait
        interval: Seconds between checks

    Returns:
        True if service becomes available, False if timeout
    """
    elapsed = 0
    while elapsed < max_wait:
        try:
            if check_func():
                return True
        except Exception:
            pass

        time.sleep(interval)
        elapsed += interval

    return False


def clear_redis_cache(pattern: str | None = None) -> int:
    """Clear Redis cache.

    Args:
        pattern: Optional key pattern to match (e.g., "user:*")

    Returns:
        Number of keys deleted
    """
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url)

        if pattern:
            keys = r.keys(pattern)
            if keys:
                return r.delete(*keys)
            return 0
        r.flushdb()
        return -1  # Indicates full flush

    except Exception:
        return 0


def get_redis_stats() -> dict[str, Any]:
    """Get Redis statistics."""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url)
        info = r.info()

        return {
            "version": info.get("redis_version"),
            "used_memory": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_keys": r.dbsize(),
            "uptime_days": info.get("uptime_in_days"),
        }
    except Exception:
        return {}


def clear_neo4j_graph(confirm: bool = False) -> bool:
    """Clear all data from Neo4j graph.

    Args:
        confirm: Safety flag - must be True to execute

    Returns:
        True if successful
    """
    if not confirm:
        return False

    try:
        uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            # Delete all nodes and relationships
            session.run("MATCH (n) DETACH DELETE n")
        driver.close()
        return True

    except Exception:
        return False


def get_neo4j_stats() -> dict[str, Any]:
    """Get Neo4j statistics."""
    try:
        uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            # Count nodes
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = node_result.single()["count"]

            # Count relationships
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()["count"]

            # Get node labels
            labels_result = session.run("CALL db.labels()")
            labels = [record["label"] for record in labels_result]

        driver.close()

        return {
            "nodes": node_count,
            "relationships": rel_count,
            "labels": labels,
        }

    except Exception:
        return {}


def restart_service(service_name: str) -> bool:
    """Restart a service using process-compose.

    Args:
        service_name: Name of service to restart

    Returns:
        True if successful
    """
    try:
        # This assumes process-compose is running
        # In practice, you'd use process-compose API or CLI
        result = subprocess.run(["pkill", "-HUP", "-f", service_name], capture_output=True, text=True)
        return result.returncode == 0

    except Exception:
        return False


def get_service_logs(service_name: str, lines: int = 50, follow: bool = False) -> str | None:
    """Get logs for a service.

    Args:
        service_name: Name of service
        lines: Number of lines to retrieve
        follow: Whether to follow (tail -f)

    Returns:
        Log content or None
    """
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_file = log_dir / f"{service_name}.log"

    if not log_file.exists():
        return None

    try:
        if follow:
            subprocess.run(["tail", "-f", "-n", str(lines), str(log_file)])
            return None
        with Path(log_file).open(encoding="utf-8") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])

    except Exception:
        return None


def check_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is available (not in use)."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    try:
        sock.bind((host, port))
        sock.close()
        return True
    except OSError:
        return False


def find_available_port(start_port: int = 8000, end_port: int = 9000) -> int | None:
    """Find an available port in the given range."""
    for port in range(start_port, end_port):
        if check_port_available(port):
            return port
    return None


def get_process_info(process_name: str) -> list[dict[str, Any]]:
    """Get information about running processes matching name."""
    try:
        result = subprocess.run(["pgrep", "-fl", process_name], capture_output=True, text=True)

        if result.returncode != 0:
            return []

        processes = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split(None, 1)
                if len(parts) == 2:
                    processes.append({
                        "pid": int(parts[0]),
                        "command": parts[1],
                    })

        return processes

    except Exception:
        return []


def kill_process_on_port(port: int) -> bool:
    """Kill process using a specific port."""
    try:
        # Find process using the port
        result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)

        if result.returncode == 0 and result.stdout.strip():
            pid = result.stdout.strip()
            subprocess.run(["kill", "-9", pid])
            return True

        return False

    except Exception:
        return False
