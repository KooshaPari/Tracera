"""Health and metrics router for TraceRTM API.

This module provides endpoints for:
- Basic health checks (/health)
- Prometheus metrics (/metrics)
- Comprehensive API health (/api/v1/health)
- Readiness checks (/ready)

Extracted from main.py as part of Phase 4.1 decomposition.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_cache_service, get_db
from tracertm.api.handlers.health import (
    get_comprehensive_health,
    get_failed_components,
)
from tracertm.services.cache_service import CacheService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint.

    Returns:
        Simple health status response
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "TraceRTM API",
    }


@router.get("/metrics")
async def metrics() -> Response:
    """Prometheus scrape endpoint for monitoring (process metrics, etc.).

    Returns:
        Prometheus metrics in text format
    """
    from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

    output = generate_latest(REGISTRY)
    return Response(
        content=output,
        media_type=CONTENT_TYPE_LATEST,
    )


@router.get("/ready", response_model=None)
async def readiness_check(
    db: Annotated[AsyncSession, Depends(get_db)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> dict[str, Any] | JSONResponse:
    """Readiness check endpoint for orchestrators (k8s, etc.).

    Checks critical dependencies only (database and cache).

    Returns:
        Readiness status with critical components

    Raises:
        503 if not ready
    """
    from tracertm.api.handlers.health import check_database, check_redis

    components: dict[str, dict[str, Any]] = {}

    # Check critical components only
    db_components = await check_database(db)
    components.update(db_components)

    redis_component = await check_redis(cache)
    components.update(redis_component)

    # Determine readiness
    ready = all(c.get("status") == "healthy" for c in components.values())
    status = "ready" if ready else "not_ready"

    body = {
        "status": status,
        "ready": ready,
        "components": components,
    }

    if not ready:
        failed = get_failed_components(components)
        body["detail"] = "Not ready: " + "; ".join(failed)
        return JSONResponse(status_code=503, content=body)

    return body


@router.get("/api/v1/health", response_model=None)
async def api_health_check(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> dict[str, Any] | JSONResponse:
    """Comprehensive API health check endpoint with component status.

    Checks all dependencies:
    - Database (PostgreSQL)
    - Migrations status
    - Redis/cache
    - NATS
    - Temporal
    - Go backend integration

    Returns:
        Detailed health status for all components

    Raises:
        503 if any component is unhealthy
    """
    # Get NATS client from app state
    nats_client = getattr(request.app.state, "nats_client", None)

    # Get comprehensive health
    components, status = await get_comprehensive_health(db, cache, nats_client)

    body = {
        "status": status,
        "service": "tracertm-api",
        "components": components,
    }

    # Fail clearly: return 503 when any required component is unhealthy (CLAUDE.md).
    if status == "unhealthy":
        failed = get_failed_components(components)
        body["detail"] = "Unhealthy components: " + "; ".join(failed)
        return JSONResponse(status_code=503, content=body)

    return body
