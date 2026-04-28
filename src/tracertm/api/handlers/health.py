"""Health check handlers for TraceRTM API.

This module provides health check logic for the API and its dependencies.
Extracted from main.py as part of Phase 4.1 decomposition.
"""

import os
import time
from typing import Any, cast

import httpx
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.cache_service import CacheService, RedisUnavailableError
from tracertm.services.temporal_service import TemporalService

# HTTP status codes
HTTP_SERVER_ERROR_START = 500


def _unhealthy_component(name: str, exc: Exception) -> dict[str, dict[str, object]]:
    """Build a consistent unhealthy response for component checks."""
    return {name: {"status": "unhealthy", "error": str(exc)}}


async def check_database(db: AsyncSession) -> dict[str, object]:
    """Check database health and migrations status.

    Args:
        db: Database session

    Returns:
        Dictionary with database and migrations component status
    """
    components: dict[str, object] = {}

    db_start = time.time()
    try:
        await db.execute(text("SELECT 1"))
        latency = (time.time() - db_start) * 1000
        components["database"] = {"status": "healthy", "latency_ms": latency}

        # Preflight: require key Python tables (Alembic migrations applied)
        result = await db.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'test_cases')",
            ),
        )
        tables_ok = result.scalar() is True
        if not tables_ok:
            components["migrations"] = {
                "status": "unhealthy",
                "error": (
                    "Python tables missing; run: ./scripts/run_python_migrations.sh or uv run alembic upgrade head"
                ),
            }
        else:
            components["migrations"] = {"status": "healthy"}
    except (SQLAlchemyError, RuntimeError, OSError, ValueError) as exc:
        components["database"] = _unhealthy_component("database", exc)["database"]
        components["migrations"] = {"status": "unknown"}

    return components


async def check_redis(cache: CacheService) -> dict[str, object]:
    """Check Redis/cache health.

    Args:
        cache: Cache service instance

    Returns:
        Dictionary with redis component status
    """
    try:
        healthy = await cache.health_check()
    except (RedisUnavailableError, RuntimeError, OSError, ValueError) as exc:
        return cast("dict[str, object]", _unhealthy_component("redis", exc))
    else:
        return {"redis": {"status": "healthy" if healthy else "unhealthy"}}


async def check_nats(nats_client: object | None) -> dict[str, object]:
    """Check NATS health.

    Args:
        nats_client: NATS client instance or None

    Returns:
        Dictionary with nats component status
    """
    try:
        if nats_client is None:
            return {"nats": {"status": "unhealthy", "error": "not initialized"}}

        # Cast to Any to call health_check method (duck typing)
        nats_health = await cast("Any", nats_client).health_check()
        return {
            "nats": {
                "status": "healthy" if nats_health.get("connected") else "unhealthy",
                "details": nats_health,
            },
        }
    except (AttributeError, RuntimeError, OSError, ValueError, TypeError) as exc:
        return cast("dict[str, object]", _unhealthy_component("nats", exc))


async def check_temporal() -> dict[str, object]:
    """Check Temporal health.

    Returns:
        Dictionary with temporal component status
    """
    try:
        temporal_health = await TemporalService().health_check()
        return {
            "temporal": {
                "status": "healthy" if temporal_health.get("status") == "ready" else "unhealthy",
                "details": temporal_health,
            },
        }
    except (RuntimeError, OSError, ValueError, TypeError) as exc:
        return cast("dict[str, object]", _unhealthy_component("temporal", exc))


async def check_go_backend() -> dict[str, object]:
    """Check Go backend health.

    Returns:
        Dictionary with go_backend component status
    """
    go_backend_url = os.getenv("GO_BACKEND_URL", "http://localhost:8080")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{go_backend_url}/health")
            return {
                "go_backend": {
                    "status": "healthy" if resp.status_code < HTTP_SERVER_ERROR_START else "unhealthy",
                    "http_status": resp.status_code,
                },
            }
    except (httpx.HTTPError, OSError, ValueError) as exc:
        return cast("dict[str, object]", _unhealthy_component("go_backend", exc))


async def get_comprehensive_health(
    db: AsyncSession,
    cache: CacheService,
    nats_client: object | None = None,
) -> tuple[dict[str, object], str]:
    """Get comprehensive health status for all components.

    Args:
        db: Database session
        cache: Cache service instance
        nats_client: NATS client instance (optional)

    Returns:
        Tuple of (components dict, overall status string)
    """
    components: dict[str, object] = {}
    status = "ok"

    # Check all components
    db_components = await check_database(db)
    components.update(db_components)

    redis_component = await check_redis(cache)
    components.update(redis_component)

    nats_component = await check_nats(nats_client)
    components.update(nats_component)

    temporal_component = await check_temporal()
    components.update(temporal_component)

    go_backend_component = await check_go_backend()
    components.update(go_backend_component)

    # Determine overall status
    for component_data in components.values():
        if isinstance(component_data, dict) and component_data.get("status") == "unhealthy":
            status = "unhealthy"
            break

    return components, status


def get_failed_components(components: dict[str, object]) -> list[str]:
    """Get list of failed component names.

    Args:
        components: Dictionary of component health data

    Returns:
        List of component names that are unhealthy
    """
    return [name for name, c in components.items() if isinstance(c, dict) and c.get("status") == "unhealthy"]
