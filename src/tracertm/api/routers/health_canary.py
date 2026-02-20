"""Enhanced health check router with canary deployment metrics."""

import os
import time
from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from typing import Any

from tracertm.api.handlers.health import (
    check_database,
    check_go_backend,
    check_nats,
    check_redis,
)

router = APIRouter(prefix="/health", tags=["health"])

# Track service start time
SERVICE_START_TIME = time.time()


class DeploymentInfo(BaseModel):
    """Deployment-specific information."""

    type: str  # "stable" or "canary"
    image_tag: str
    start_time: datetime
    uptime_seconds: float


class CanaryMetrics(BaseModel):
    """Canary-specific performance metrics."""

    request_count: int
    error_count: int
    error_rate: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float


class CanaryHealthResponse(BaseModel):
    """Enhanced health response with canary metrics."""

    status: str
    version: str
    timestamp: datetime
    deployment: DeploymentInfo
    components: dict[str, dict[str, Any]]
    integration: dict[str, Any] | None = None
    metrics: CanaryMetrics | None = None


def get_version() -> str:
    """Get API version string."""
    return os.getenv("APP_VERSION", "dev")


def get_deployment_info() -> DeploymentInfo:
    """Get deployment information."""
    is_canary = os.getenv("CANARY_DEPLOYMENT", "false").lower() == "true"
    deployment_type = "canary" if is_canary else "stable"

    return DeploymentInfo(
        type=deployment_type,
        image_tag=os.getenv("APP_VERSION", "dev"),
        start_time=datetime.fromtimestamp(SERVICE_START_TIME, tz=UTC),
        uptime_seconds=time.time() - SERVICE_START_TIME,
    )


def get_canary_metrics() -> CanaryMetrics:
    """Get canary-specific metrics.

    In production, these would be fetched from metrics collectors.
    For now, returns placeholder values.
    """
    return CanaryMetrics(
        request_count=0,
        error_count=0,
        error_rate=0.0,
        avg_latency_ms=0.0,
        p95_latency_ms=0.0,
        p99_latency_ms=0.0,
        memory_usage_mb=0.0,
        cpu_usage_percent=0.0,
    )


@router.get("/canary")
async def get_canary_health(
    # Uncomment and adjust based on your setup
) -> CanaryHealthResponse:
    """Get enhanced health status with canary metrics.

    Returns:
        CanaryHealthResponse with deployment info and metrics
    """
    # Temporary placeholders
    db = None
    redis = None
    nats = None
    is_canary = os.getenv("CANARY_DEPLOYMENT", "false").lower() == "true"

    components = {}

    # Check all components
    if db is not None:
        components.update(await check_database(db))
    else:
        components["database"] = {
            "status": "degraded",
            "message": "Database dependency not available",
            "last_check": datetime.now(UTC),
        }
        components["migrations"] = {
            "status": "unknown",
            "message": "Database dependency not available",
            "last_check": datetime.now(UTC),
        }

    if redis is not None:
        components.update(await check_redis(redis))
    else:
        components["redis"] = {
            "status": "degraded",
            "message": "Redis dependency not available",
            "last_check": datetime.now(UTC),
        }

    components.update(await check_nats(nats))
    components.update(await check_go_backend())

    # Integration health
    integration = {
        "database": components.get("database"),
        "redis": components.get("redis"),
        "nats": components.get("nats"),
        "go_backend": components.get("go_backend"),
    }

    # Overall status
    overall_status = "healthy"
    for comp in components.values():
        if comp.get("status") == "unhealthy":
            overall_status = "unhealthy"
            break
        if comp.get("status") == "degraded":
            overall_status = "degraded"

    # Build response
    response = CanaryHealthResponse(
        status=overall_status,
        version="1.0.0",
        timestamp=datetime.now(UTC),
        deployment=get_deployment_info(),
        components=components,
        integration=integration,
    )

    # Add canary metrics if this is a canary deployment
    if is_canary:
        response.metrics = get_canary_metrics()

    return response


@router.get("/readiness")
async def get_readiness() -> dict[str, Any]:
    """Kubernetes readiness probe endpoint.

    Returns:
        Readiness status
    """
    db = None

    # Check critical dependencies
    if db is not None:
        db_health = await check_database(db)
        if db_health.status == "unhealthy":
            return {
                "status": "not_ready",
                "message": "database not available",
            }

    return {"status": "ready"}


@router.get("/liveness")
async def get_liveness() -> dict[str, Any]:
    """Kubernetes liveness probe endpoint.

    Returns:
        Liveness status
    """
    return {"status": "alive"}
