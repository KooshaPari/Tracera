"""Automatic instrumentation for FastAPI, database, and external APIs.

Provides automatic tracing for:
- FastAPI HTTP requests/responses
- SQLAlchemy database queries
- HTTP client requests
- Redis operations
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI
    from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


def instrument_app(app: "FastAPI") -> None:
    """Instrument FastAPI application with OpenTelemetry.

    Automatically traces:
    - HTTP requests and responses
    - Request/response headers (sanitized)
    - Status codes
    - Request duration

    Args:
        app: FastAPI application instance
    """
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("✅ FastAPI instrumentation enabled")
    except ImportError as e:
        logger.warning("FastAPI instrumentation not available: %s", e)
    except Exception:
        logger.exception("Failed to instrument FastAPI")


def instrument_database(engine: "AsyncEngine") -> None:
    """Instrument SQLAlchemy async engine with OpenTelemetry.

    Automatically traces:
    - SQL queries
    - Query parameters (sanitized)
    - Query duration
    - Connection pool statistics

    Args:
        engine: SQLAlchemy async engine instance
    """
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        # Instrument the engine
        SQLAlchemyInstrumentor().instrument(
            engine=engine.sync_engine,
            enable_commenter=True,  # Add SQL comments with trace context
            commenter_options={
                "db_driver": True,
                "db_framework": True,
            },
        )
        logger.info("✅ SQLAlchemy instrumentation enabled")
    except ImportError as e:
        logger.warning("SQLAlchemy instrumentation not available: %s", e)
    except Exception:
        logger.exception("Failed to instrument SQLAlchemy")


def instrument_http_client() -> None:
    """Instrument httpx/requests HTTP clients with OpenTelemetry.

    Automatically traces:
    - HTTP client requests
    - Request/response headers
    - Status codes
    - Request duration
    """
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        HTTPXClientInstrumentor().instrument()
        logger.info("✅ HTTPX client instrumentation enabled")
    except ImportError:
        logger.debug("HTTPX instrumentation not available")

    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        RequestsInstrumentor().instrument()
        logger.info("✅ Requests client instrumentation enabled")
    except ImportError:
        logger.debug("Requests instrumentation not available")


def instrument_redis() -> None:
    """Instrument Redis client with OpenTelemetry.

    Automatically traces:
    - Redis commands
    - Command arguments (sanitized)
    - Command duration
    """
    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        RedisInstrumentor().instrument()
        logger.info("✅ Redis instrumentation enabled")
    except ImportError as e:
        logger.debug("Redis instrumentation not available: %s", e)
    except Exception:
        logger.exception("Failed to instrument Redis")


def instrument_all() -> None:
    """Enable all available automatic instrumentation.

    This is a convenience function that instruments:
    - HTTP clients
    - Redis
    """
    instrument_http_client()
    instrument_redis()


__all__ = [
    "instrument_all",
    "instrument_app",
    "instrument_database",
    "instrument_http_client",
    "instrument_redis",
]
