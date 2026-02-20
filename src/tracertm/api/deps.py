"""Dependencies for TraceRTM API."""

import logging
from collections.abc import AsyncGenerator

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.config.manager import ConfigManager
from tracertm.core.context import current_user_id
from tracertm.infrastructure.event_bus import EventBus
from tracertm.infrastructure.nats_client import NATSClient
from tracertm.services.cache_service import CacheService, RedisUnavailableError
from tracertm.services.token_bridge import TokenBridge, get_token_bridge
from typing import Any

logger = logging.getLogger(__name__)

# Cache service singleton
_cache_service: CacheService | None = None

# Token bridge singleton
_token_bridge: TokenBridge | None = None

# EventBus singleton
_event_bus: EventBus | None = None


def get_cache_service() -> CacheService:
    """Get singleton CacheService for dependency injection.

    Redis is required; fail clearly if unavailable (CLAUDE.md).
    """
    global _cache_service
    if _cache_service is None:
        config_manager = ConfigManager()
        redis_url = config_manager.get("redis_url", "redis://localhost:6379")
        try:
            _cache_service = CacheService(redis_url)
        except (RedisUnavailableError, RuntimeError) as e:
            # Required dependency: fail clearly with named item so operators see what failed (CLAUDE.md).
            raise HTTPException(
                status_code=503,
                detail=f"Redis unavailable: {e}",
            ) from e
    return _cache_service


def get_token_bridge_instance() -> TokenBridge:
    """Get singleton TokenBridge for dependency injection."""
    global _token_bridge
    if _token_bridge is None:
        _token_bridge = get_token_bridge()
    return _token_bridge


async def get_event_bus() -> EventBus:
    """Get EventBus singleton for dependency injection.

    Returns:
        EventBus: Connected EventBus instance for cross-backend communication
    """
    global _event_bus
    if _event_bus is None:
        config_manager = ConfigManager()
        nats_url = config_manager.get("nats_url", "nats://localhost:4222")
        nats_creds_path = config_manager.get("nats_creds_path")

        # Create and connect NATS client
        nats_client = NATSClient(url=nats_url, creds_path=nats_creds_path)
        try:
            await nats_client.connect()
            _event_bus = EventBus(nats_client)
            logger.info("EventBus initialized successfully")
        except Exception as e:
            msg = f"Failed to initialize EventBus: {e}"
            raise RuntimeError(msg) from e

    return _event_bus


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with shared connection pool.

    This now uses the MCP database adapter to share the connection pool
    between FastAPI routes and MCP tools, reducing resource usage by 50%.

    Yields:
        AsyncSession: Database session with RLS context set

    Raises:
        HTTPException: If database is not configured or connection fails
    """
    try:
        # Import here to avoid circular dependency
        from tracertm.mcp.database_adapter import get_mcp_session

        async with get_mcp_session() as session:
            yield session
    except ValueError as exc:
        # Database not configured
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        # Connection or other error
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def verify_token(token: str) -> dict[str, Any]:
    """Verify WorkOS AuthKit access tokens or internal service tokens.

    Uses TokenBridge to validate both RS256 (WorkOS) and HS256 (service) tokens.
    """
    try:
        bridge = get_token_bridge_instance()
        return bridge.validate_token(token)
    except Exception as exc:
        logger.warning("Token validation failed: %s", exc)
        raise ValueError(str(exc)) from exc


def auth_guard(request: Request) -> dict[str, Any]:
    """Authenticate incoming requests when auth is enabled."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer ") or "  " in auth_header:
        raise HTTPException(status_code=401, detail="Authorization required")

    token = auth_header.split(None, 1)[1].strip()
    if not token or " " in token:
        raise HTTPException(status_code=401, detail="Authorization required")

    try:
        claims = verify_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    # Set user context for database RLS
    user_id = claims.get("sub") if claims else None
    if user_id:
        current_user_id.set(user_id)

    # Set account context if present
    account_id = claims.get("org_id") or claims.get("account_id") if claims else None
    if account_id:
        from tracertm.core.context import current_account_id

        current_account_id.set(account_id)

    return claims or {}
