"""Phase 6: E2E Integration Testing - Test Fixtures.

This module provides comprehensive test fixtures for all infrastructure components:
- PostgreSQL (SQLAlchemy + asyncpg)
- Neo4j (async driver)
- Redis (async client)
- MinIO (S3 client)
- NATS JetStream (async client)
- Temporal (test server)

All fixtures handle lifecycle management and cleanup between tests.
"""

import asyncio
import os

# Import application components
import sys
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, datetime, timezone
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from minio import Minio
from nats.aio.client import Client as NATSClient
from nats.js import JetStreamContext
from neo4j import AsyncDriver, AsyncGraphDatabase
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from temporalio import activity, workflow
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

sys.path.insert(0, "/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src")

import contextlib

from tracertm.agent.agent_service import AgentService
from tracertm.agent.events import AgentEventPublisher
from tracertm.agent.graph_session_store import GraphSessionStore
from tracertm.workflows.activities import (
    create_session_checkpoint,
)

# ============================================================================
# Test Configuration
# ============================================================================

TEST_CONFIG = {
    # PostgreSQL
    "postgres_url": os.getenv(
        "TEST_POSTGRES_URL",
        "postgresql+asyncpg://postgres:password@localhost:5432/tracertm_test",
    ),
    # Neo4j
    "neo4j_uri": os.getenv("TEST_NEO4J_URI", "bolt://localhost:7687"),
    "neo4j_user": os.getenv("TEST_NEO4J_USER", "neo4j"),
    "neo4j_password": os.getenv("TEST_NEO4J_PASSWORD", "neo4j_password"),
    # Redis
    "redis_url": os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1"),
    # MinIO
    "minio_endpoint": os.getenv("TEST_MINIO_ENDPOINT", "localhost:9000"),
    "minio_access_key": os.getenv("TEST_MINIO_ACCESS_KEY", "minioadmin"),
    "minio_secret_key": os.getenv("TEST_MINIO_SECRET_KEY", "minioadmin"),
    "minio_bucket": os.getenv("TEST_MINIO_BUCKET", "tracertm-test"),
    # NATS
    "nats_url": os.getenv("TEST_NATS_URL", "nats://localhost:4222"),
    "nats_stream": "TRACERTM_TEST",
}


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config: Any) -> None:
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers",
        "e2e: end-to-end integration tests requiring all infrastructure",
    )
    config.addinivalue_line(
        "markers",
        "slow: tests that take >5 seconds",
    )
    config.addinivalue_line(
        "markers",
        "oauth: tests requiring OAuth mock",
    )


# ============================================================================
# PostgreSQL Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def postgres_engine() -> None:
    """Create async SQLAlchemy engine for tests."""
    engine = create_async_engine(
        TEST_CONFIG["postgres_url"],
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def postgres_sessionmaker(postgres_engine: Any) -> None:
    """Create session factory."""
    sessionmaker = async_sessionmaker(
        postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield sessionmaker


@pytest_asyncio.fixture
async def db_session(postgres_sessionmaker: Any) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session with automatic rollback."""
    async with postgres_sessionmaker() as session, session.begin():
        yield session
        # Rollback happens automatically on context exit


# ============================================================================
# Neo4j Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def neo4j_driver() -> AsyncGenerator[AsyncDriver, None]:
    """Create Neo4j async driver for tests."""
    driver = AsyncGraphDatabase.driver(
        TEST_CONFIG["neo4j_uri"],
        auth=(TEST_CONFIG["neo4j_user"], TEST_CONFIG["neo4j_password"]),
    )

    # Verify connection
    await driver.verify_connectivity()

    yield driver

    await driver.close()


@pytest_asyncio.fixture
async def neo4j_session(neo4j_driver: Any) -> None:
    """Provide a Neo4j session with automatic cleanup."""
    async with neo4j_driver.session() as session:
        yield session

        # Clean up test data
        await session.run(
            """
            MATCH (n)
            WHERE n:TestSession OR n:TestNode
            DETACH DELETE n
            """,
        )


# ============================================================================
# Redis Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def redis_client() -> AsyncGenerator[Redis, None]:
    """Create Redis async client for tests."""
    client = Redis.from_url(
        TEST_CONFIG["redis_url"],
        decode_responses=True,
    )

    # Verify connection
    await client.ping()

    yield client

    await client.aclose()


@pytest_asyncio.fixture
async def redis_clean(redis_client: Any) -> None:
    """Provide clean Redis instance for each test."""
    # Clean before test
    await redis_client.flushdb()

    yield redis_client

    # Clean after test
    await redis_client.flushdb()


# ============================================================================
# MinIO Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def minio_client() -> Generator[Minio, None, None]:
    """Create MinIO client for tests."""
    client = Minio(
        TEST_CONFIG["minio_endpoint"],
        access_key=TEST_CONFIG["minio_access_key"],
        secret_key=TEST_CONFIG["minio_secret_key"],
        secure=False,  # Use HTTP for tests
    )

    # Create test bucket if not exists
    if not client.bucket_exists(TEST_CONFIG["minio_bucket"]):
        client.make_bucket(TEST_CONFIG["minio_bucket"])

    yield client

    # Cleanup: Remove all test objects
    objects = client.list_objects(
        TEST_CONFIG["minio_bucket"],
        recursive=True,
    )
    for obj in objects:
        client.remove_object(TEST_CONFIG["minio_bucket"], obj.object_name)


@pytest.fixture
def minio_clean(minio_client: Any) -> None:
    """Provide clean MinIO bucket for each test."""
    # Clean before test
    objects = minio_client.list_objects(
        TEST_CONFIG["minio_bucket"],
        recursive=True,
    )
    for obj in objects:
        minio_client.remove_object(TEST_CONFIG["minio_bucket"], obj.object_name)

    return minio_client


# ============================================================================
# NATS Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def nats_client() -> AsyncGenerator[NATSClient, None]:
    """Create NATS async client for tests."""
    nc = NATSClient()
    await nc.connect(TEST_CONFIG["nats_url"])

    # Create JetStream context
    js = nc.jetstream()

    # Create test stream
    try:
        await js.add_stream(
            name=TEST_CONFIG["nats_stream"],
            subjects=["tracertm.test.>"],
        )
    except Exception:
        pass  # Stream might already exist

    yield nc

    # Cleanup: Delete stream and close
    with contextlib.suppress(Exception):
        await js.delete_stream(TEST_CONFIG["nats_stream"])

    await nc.close()


@pytest_asyncio.fixture
async def nats_jetstream(nats_client: Any) -> JetStreamContext:
    """Provide JetStream context for tests."""
    js = nats_client.jetstream()
    yield js


@pytest_asyncio.fixture
async def nats_clean(nats_jetstream: Any) -> None:
    """Provide clean NATS stream for each test."""
    # Purge stream before test
    with contextlib.suppress(Exception):
        await nats_jetstream.purge_stream(TEST_CONFIG["nats_stream"])

    yield nats_jetstream


# ============================================================================
# Temporal Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def temporal_env() -> AsyncGenerator[WorkflowEnvironment, None]:
    """Create Temporal test environment."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        yield env


@pytest_asyncio.fixture
async def temporal_worker(temporal_env: Any) -> None:
    """Provide Temporal test environment for workflow execution.

    Note: For integration tests, we use the Python test environment.
    The Go snapshot workflow/activities need to be tested via the Go test suite.
    """
    # The temporal_env fixture provides the test environment
    # Workflows can be started via temporal_env.client
    yield temporal_env


# ============================================================================
# Integration Fixtures (Combined Services)
# ============================================================================


@pytest_asyncio.fixture
async def event_publisher(nats_client: Any) -> AgentEventPublisher:
    """Provide configured event publisher."""
    publisher = AgentEventPublisher(nats_client)
    yield publisher


@pytest_asyncio.fixture
async def graph_session_store(
    db_session: Any,
    neo4j_driver: Any,
    redis_client: Any,
    event_publisher: Any,
) -> GraphSessionStore:
    """Provide fully configured GraphSessionStore."""
    return GraphSessionStore(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
        redis_client=redis_client,
        event_publisher=event_publisher,
    )


@pytest_asyncio.fixture
async def agent_service(
    graph_session_store: Any,
    event_publisher: Any,
) -> AgentService:
    """Provide fully configured AgentService."""
    return AgentService(
        session_store=graph_session_store,
        event_publisher=event_publisher,
    )


# ============================================================================
# Test Data Factories
# ============================================================================


@pytest.fixture
def test_session_factory() -> None:
    """Factory for creating test session data."""

    def _create_session(
        project_id: str | None = None,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> dict:
        return {
            "session_id": str(uuid4()),
            "project_id": project_id or str(uuid4()),
            "user_id": user_id or str(uuid4()),
            "sandbox_root": f"/tmp/test-{uuid4()}",
            "created_at": datetime.now(UTC),
            **kwargs,
        }

    return _create_session


@pytest.fixture
def test_checkpoint_factory() -> None:
    """Factory for creating test checkpoint data."""

    def _create_checkpoint(
        session_id: str,
        turn_number: int = 1,
        **kwargs: Any,
    ) -> dict:
        return {
            "checkpoint_id": str(uuid4()),
            "session_id": session_id,
            "turn_number": turn_number,
            "state_snapshot": {
                "messages": [],
                "context": {},
            },
            "created_at": datetime.now(UTC),
            **kwargs,
        }

    return _create_checkpoint


# ============================================================================
# Cleanup Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
async def cleanup_test_data(
    _db_session: Any,
    _neo4j_session: Any,
    _redis_clean: Any,
    _minio_clean: Any,
    _nats_clean: Any,
) -> None:
    """Automatically clean up all test data after each test."""
    return

    # All cleanup happens in individual fixtures
    # This is just a marker that cleanup is handled
