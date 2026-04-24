"""Pytest fixtures and configuration for chaos engineering tests."""

import asyncio
import logging
import os
import time
from collections.abc import AsyncGenerator, Callable, Generator
from typing import Any

import httpx
import pytest
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from tests.chaos.toxiproxy_client import ToxiproxyClient

logger = logging.getLogger(__name__)

# Toxiproxy configuration
TOXIPROXY_HOST = os.getenv("TOXIPROXY_HOST", "localhost")
TOXIPROXY_PORT = int(os.getenv("TOXIPROXY_PORT", "8474"))

# Service endpoints (proxied through Toxiproxy in chaos tests)
POSTGRES_PROXY_PORT = 15432
REDIS_PROXY_PORT = 16379
NATS_PROXY_PORT = 14222
GO_BACKEND_PROXY_PORT = 18080
PYTHON_BACKEND_PROXY_PORT = 18000

# Actual service endpoints
POSTGRES_UPSTREAM = "localhost:5432"
REDIS_UPSTREAM = "localhost:6379"
NATS_UPSTREAM = "localhost:4222"
GO_BACKEND_UPSTREAM = "localhost:8080"
PYTHON_BACKEND_UPSTREAM = "localhost:8000"

# Recovery time target (seconds)
RECOVERY_TIME_TARGET = 30


@pytest.fixture(scope="session")
def toxiproxy_url() -> str:
    """Toxiproxy HTTP API URL."""
    return f"http://{TOXIPROXY_HOST}:{TOXIPROXY_PORT}"


@pytest.fixture(scope="session")
async def toxiproxy_client(toxiproxy_url: str) -> AsyncGenerator[ToxiproxyClient, None]:
    """Provides a Toxiproxy client for managing proxies and toxics.

    Validates that Toxiproxy is running and accessible before tests.
    """
    client = ToxiproxyClient(toxiproxy_url)

    # Verify Toxiproxy is running
    try:
        await client.version()
        logger.info("Connected to Toxiproxy at %s", toxiproxy_url)
    except Exception as e:
        pytest.skip(f"Toxiproxy not available at {toxiproxy_url}: {e}")

    yield client

    # Cleanup: remove all toxics after tests
    await client.cleanup_all()


@pytest.fixture
async def postgres_proxy(toxiproxy_client: ToxiproxyClient) -> AsyncGenerator[str, None]:
    """Creates a Toxiproxy proxy for PostgreSQL.

    Returns the connection string to use (through proxy).
    """
    proxy_name = "postgres_chaos"
    listen = f"0.0.0.0:{POSTGRES_PROXY_PORT}"

    await toxiproxy_client.create_proxy(
        name=proxy_name,
        listen=listen,
        upstream=POSTGRES_UPSTREAM,
    )

    # Connection string through proxy
    db_password = os.getenv("DB_PASSWORD", "tracertm_password")
    connection_string = f"postgresql+asyncpg://tracertm:{db_password}@localhost:{POSTGRES_PROXY_PORT}/tracertm"

    yield connection_string

    await toxiproxy_client.delete_proxy(proxy_name)


@pytest.fixture
async def redis_proxy(toxiproxy_client: ToxiproxyClient) -> AsyncGenerator[str, None]:
    """Creates a Toxiproxy proxy for Redis.

    Returns the Redis URL to use (through proxy).
    """
    proxy_name = "redis_chaos"
    listen = f"0.0.0.0:{REDIS_PROXY_PORT}"

    await toxiproxy_client.create_proxy(
        name=proxy_name,
        listen=listen,
        upstream=REDIS_UPSTREAM,
    )

    redis_url = f"redis://localhost:{REDIS_PROXY_PORT}"

    yield redis_url

    await toxiproxy_client.delete_proxy(proxy_name)


@pytest.fixture
async def nats_proxy(toxiproxy_client: ToxiproxyClient) -> AsyncGenerator[str, None]:
    """Creates a Toxiproxy proxy for NATS.

    Returns the NATS URL to use (through proxy).
    """
    proxy_name = "nats_chaos"
    listen = f"0.0.0.0:{NATS_PROXY_PORT}"

    await toxiproxy_client.create_proxy(
        name=proxy_name,
        listen=listen,
        upstream=NATS_UPSTREAM,
    )

    nats_url = f"nats://localhost:{NATS_PROXY_PORT}"

    yield nats_url

    await toxiproxy_client.delete_proxy(proxy_name)


@pytest.fixture
async def go_backend_proxy(toxiproxy_client: ToxiproxyClient) -> AsyncGenerator[str, None]:
    """Creates a Toxiproxy proxy for Go backend.

    Returns the backend URL to use (through proxy).
    """
    proxy_name = "go_backend_chaos"
    listen = f"0.0.0.0:{GO_BACKEND_PROXY_PORT}"

    await toxiproxy_client.create_proxy(
        name=proxy_name,
        listen=listen,
        upstream=GO_BACKEND_UPSTREAM,
    )

    backend_url = f"http://localhost:{GO_BACKEND_PROXY_PORT}"

    yield backend_url

    await toxiproxy_client.delete_proxy(proxy_name)


@pytest.fixture
async def python_backend_proxy(toxiproxy_client: ToxiproxyClient) -> AsyncGenerator[str, None]:
    """Creates a Toxiproxy proxy for Python backend.

    Returns the backend URL to use (through proxy).
    """
    proxy_name = "python_backend_chaos"
    listen = f"0.0.0.0:{PYTHON_BACKEND_PROXY_PORT}"

    await toxiproxy_client.create_proxy(
        name=proxy_name,
        listen=listen,
        upstream=PYTHON_BACKEND_UPSTREAM,
    )

    backend_url = f"http://localhost:{PYTHON_BACKEND_PROXY_PORT}"

    yield backend_url

    await toxiproxy_client.delete_proxy(proxy_name)


@pytest.fixture
async def db_session(postgres_proxy: str) -> AsyncGenerator[AsyncSession, None]:
    """Provides a database session through the Toxiproxy proxy."""
    engine = create_async_engine(postgres_proxy, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def redis_client(redis_proxy: str) -> AsyncGenerator[redis.Redis, None]:
    """Provides a Redis client through the Toxiproxy proxy."""
    client = redis.from_url(redis_proxy, decode_responses=True)
    yield client
    await client.aclose()


def measure_recovery_time(func: Callable[..., Any]) -> None:
    """Decorator to measure service recovery time after chaos injection.

    Fails the test if recovery takes longer than RECOVERY_TIME_TARGET.
    """

    async def wrapper(*args: Any, **kwargs: Any) -> None:
        start_time = time.time()
        result = await func(*args, **kwargs)
        recovery_time = time.time() - start_time

        logger.info(f"Recovery time: {recovery_time:.2f}s (target: {RECOVERY_TIME_TARGET}s)")

        assert recovery_time <= RECOVERY_TIME_TARGET, (
            f"Service recovery took {recovery_time:.2f}s, exceeding target of {RECOVERY_TIME_TARGET}s"
        )

        return result

    return wrapper


@pytest.fixture
def assert_recovery_within_target() -> None:
    """Helper fixture to assert recovery time is within target.

    Usage:
        start = time.time()
        # ... chaos scenario ...
        assert_recovery_within_target(start)
    """

    def _assert(start_time: float, custom_target: float | None = None) -> None:
        recovery_time = time.time() - start_time
        target = custom_target or RECOVERY_TIME_TARGET

        logger.info(f"Recovery time: {recovery_time:.2f}s (target: {target}s)")

        assert recovery_time <= target, f"Service recovery took {recovery_time:.2f}s, exceeding target of {target}s"

    return _assert
