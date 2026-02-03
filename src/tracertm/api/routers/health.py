"""Health check router for monitoring service and integration health."""

import os
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.infrastructure.nats_client import NATSClient

# Note: Import your actual dependencies here
# from tracertm.infrastructure.database import get_db
# from tracertm.infrastructure.redis_client import get_redis
# from tracertm.infrastructure.nats_client import get_nats
# from tracertm.core.config import Settings, get_settings

router = APIRouter(prefix="/health", tags=["health"])

# Latency thresholds (ms) for health status
LATENCY_DEGRADED_MS = 1000
LATENCY_DEGRADED_REDIS_NATS_MS = 500
LATENCY_DEGRADED_GO_MS = 2000
HTTP_SERVER_ERROR_START = 500


class ComponentHealth(BaseModel):
    """Health status of a single component."""

    status: str  # "healthy", "degraded", "unhealthy"
    message: str | None = None
    latency_ms: float | None = None
    last_check: datetime


class IntegrationHealth(BaseModel):
    """Cross-backend integration health status."""

    go_backend: ComponentHealth
    nats: ComponentHealth
    redis: ComponentHealth
    database: ComponentHealth


class HealthResponse(BaseModel):
    """Complete health check response."""

    status: str
    version: str
    timestamp: datetime
    components: dict[str, ComponentHealth]
    integration: IntegrationHealth | None = None


def get_version() -> str:
    """Get application version from environment."""
    return os.getenv("APP_VERSION", "dev")


async def check_database(db: AsyncSession) -> ComponentHealth:
    """Check database connectivity and health.

    Args:
        db: Database session

    Returns:
        ComponentHealth with database status
    """
    import time

    start = time.time()

    try:
        # Simple query to check database connectivity
        await db.execute(text("SELECT 1"))
        latency_ms = (time.time() - start) * 1000

        status = "healthy"
        message = None

        # Check for degraded performance
        if latency_ms > LATENCY_DEGRADED_MS:
            status = "degraded"
            message = "High latency detected"

        return ComponentHealth(
            status=status,
            message=message,
            latency_ms=latency_ms,
            last_check=datetime.now(UTC),
        )

    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        return ComponentHealth(
            status="unhealthy",
            message=f"Database check failed: {e!s}",
            latency_ms=latency_ms,
            last_check=datetime.now(UTC),
        )


async def check_redis(redis: Redis | None) -> ComponentHealth:
    """Check Redis connectivity and health.

    Args:
        redis: Redis client (optional)

    Returns:
        ComponentHealth with Redis status
    """
    import time

    start = time.time()

    if redis is None:
        return ComponentHealth(
            status="degraded",
            message="Redis not available (optional)",
            last_check=datetime.now(UTC),
        )

    try:
        # Ping Redis
        await redis.ping()  # type: ignore[misc]
        latency_ms = (time.time() - start) * 1000

        status = "healthy"
        message = None

        if latency_ms > LATENCY_DEGRADED_REDIS_NATS_MS:
            status = "degraded"
            message = "High latency detected"

        return ComponentHealth(
            status=status,
            message=message,
            latency_ms=latency_ms,
            last_check=datetime.now(UTC),
        )

    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        return ComponentHealth(
            status="degraded",
            message=f"Redis check failed: {e!s}",
            latency_ms=latency_ms,
            last_check=datetime.now(UTC),
        )


def check_nats(nats: NATSClient | None) -> ComponentHealth:
    """Check NATS connectivity and health.

    Args:
        nats: NATS client (optional)

    Returns:
        ComponentHealth with NATS status
    """
    import time

    start = time.time()

    if nats is None:
        return ComponentHealth(
            status="degraded",
            message="NATS not initialized (optional)",
            last_check=datetime.now(UTC),
        )

    try:
        # Check if connected (NATSClient.is_connected is a method)
        connected = nats.is_connected
        if not (connected() if callable(connected) else connected):
            return ComponentHealth(
                status="unhealthy",
                message="NATS not connected",
                last_check=datetime.now(UTC),
            )

        latency_ms = (time.time() - start) * 1000

        status = "healthy"
        message = None

        if latency_ms > LATENCY_DEGRADED_REDIS_NATS_MS:
            status = "degraded"
            message = "High latency detected"

        return ComponentHealth(
            status=status,
            message=message,
            latency_ms=latency_ms,
            last_check=datetime.now(UTC),
        )

    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        return ComponentHealth(
            status="degraded",
            message=f"NATS check failed: {e!s}",
            latency_ms=latency_ms,
            last_check=datetime.now(UTC),
        )


async def check_go_backend(base_url: str) -> ComponentHealth:
    """Check Go backend connectivity and health.

    Args:
        base_url: Base URL of Go backend

    Returns:
        ComponentHealth with Go backend status
    """
    import time

    start = time.time()

    if not base_url:
        return ComponentHealth(
            status="degraded",
            message="Go backend URL not configured",
            last_check=datetime.now(UTC),
        )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/health")
            latency_ms = (time.time() - start) * 1000

            if resp.status_code >= HTTP_SERVER_ERROR_START:
                return ComponentHealth(
                    status="unhealthy",
                    message=f"HTTP {resp.status_code}",
                    latency_ms=latency_ms,
                    last_check=datetime.now(UTC),
                )

            status = "healthy"
            message = None

            if latency_ms > LATENCY_DEGRADED_GO_MS:
                status = "degraded"
                message = "High latency detected"

            return ComponentHealth(
                status=status,
                message=message,
                latency_ms=latency_ms,
                last_check=datetime.now(UTC),
            )

    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        return ComponentHealth(
            status="unhealthy",
            message=f"Request failed: {e!s}",
            latency_ms=latency_ms,
            last_check=datetime.now(UTC),
        )


@router.get("", response_model=HealthResponse)
async def get_health(
    # Uncomment and adjust these dependencies based on your setup
    # db: AsyncSession = Depends(get_db),
    # redis: Redis = Depends(get_redis),
    # nats: NATSClient = Depends(get_nats),
    # settings: Settings = Depends(get_settings)
) -> HealthResponse:
    """Get comprehensive health status.

    Returns:
        HealthResponse with overall status and component details
    """
    # Temporary placeholders - replace with actual dependencies
    db = None
    redis = None
    nats = None
    nats_bridge_enabled = os.getenv("NATS_BRIDGE_ENABLED", "true").lower() == "true"
    go_backend_url = os.getenv("GO_BACKEND_URL", "")

    components = {}

    # Check database
    if db is not None:
        components["database"] = await check_database(db)
    else:
        components["database"] = ComponentHealth(
            status="degraded",
            message="Database dependency not available",
            last_check=datetime.now(UTC),
        )

    # Check Redis
    components["redis"] = await check_redis(redis)

    # Check NATS
    components["nats"] = check_nats(nats)

    # Integration health
    integration = None
    if nats_bridge_enabled:
        integration = IntegrationHealth(
            database=components["database"],
            redis=components["redis"],
            nats=components["nats"],
            go_backend=await check_go_backend(go_backend_url),
        )

    # Overall status
    status = "healthy"
    for comp in components.values():
        if comp.status == "unhealthy":
            status = "unhealthy"
            break
        if comp.status == "degraded":
            status = "degraded"

    return HealthResponse(
        status=status,
        version=get_version(),
        timestamp=datetime.now(UTC),
        components=components,
        integration=integration,
    )
