"""Dependencies for TraceRTM API."""

import logging
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Optional, Any

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from tracertm.config.manager import ConfigManager
from tracertm.services import workos_auth_service
from tracertm.services.cache_service import CacheService
from tracertm.core.context import current_user_id

logger = logging.getLogger(__name__)

# Cache service singleton
_cache_service: CacheService | None = None


def get_cache_service() -> CacheService:
    """Get singleton CacheService for dependency injection."""
    global _cache_service
    if _cache_service is None:
        config_manager = ConfigManager()
        redis_url = config_manager.get("redis_url", "redis://localhost:6379")
        _cache_service = CacheService(redis_url)
    return _cache_service

# Cache engine to avoid recreation
_async_engine = None

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    global _async_engine
    
    config_manager = ConfigManager()
    database_url = config_manager.get("database_url")

    if not database_url:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Convert sqlite:// to sqlite+aiosqlite:// for async
    if database_url.startswith("sqlite:///"):
        async_database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    elif database_url.startswith("sqlite://"):
        async_database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    elif database_url.startswith("postgresql://"):
        # Remove query parameters that asyncpg doesn't support (like sslmode)
        base_url = database_url.split("?")[0]
        async_database_url = base_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        async_database_url = database_url

    try:
        # Simple caching strategy
        if not _async_engine:
            _async_engine = create_async_engine(
                async_database_url,
                echo=False,
            )
            
        async_session = async_sessionmaker(_async_engine, expire_on_commit=False)
        
        async with async_session() as session:
            # Set RLS context if user is authenticated
            user_id = current_user_id.get()
            if user_id and "postgres" in async_database_url:
                await session.execute(
                    text("SELECT set_config('app.current_user_id', :user_id, false)"),
                    {"user_id": user_id}
                )
            
            yield session
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def verify_token(token: str) -> dict:
    """Verify WorkOS AuthKit access tokens."""
    try:
        return workos_auth_service.verify_access_token(token)
    except Exception as exc:
        raise ValueError(str(exc)) from exc


def verify_api_key(api_key: str) -> dict:
    """Placeholder for API key verification."""
    # In a real app, this would check against a database
    # For now, we'll return a valid dummy result if it matches a test key
    if api_key == "sk_test_placeholder":
        return {"valid": True, "role": "admin"}
    return {"valid": False}


def auth_guard(request: Request) -> dict:
    """Authenticate incoming requests when auth is enabled."""
    config_manager = ConfigManager()
    auth_value = config_manager.get("auth_enabled", False)
    auth_enabled = auth_value is True or (isinstance(auth_value, str) and auth_value.lower() == "true")

    # API Key path (always validated if provided)
    api_key = request.headers.get("X-API-Key")
    if api_key and not request.headers.get("Authorization"):
        api_result = verify_api_key(api_key)
        if not api_result or not api_result.get("valid", False):
            raise HTTPException(status_code=401, detail="Invalid API key")
        return {"role": "api_key", **api_result}

    if not auth_enabled and "authorization" not in {k.lower(): v for k, v in request.headers.items()}:
        return {"role": "public"}

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

    return claims or {}