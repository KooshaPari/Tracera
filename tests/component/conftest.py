"""Component-level fixtures (between unit and e2e).

Provides async and sync database sessions backed by in-memory SQLite for
repository and service contract tests.
"""

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

# Import ALL models to ensure they're registered with Base.metadata
# This is critical - SQLAlchemy only creates tables for imported models
from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.base import Base
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project

pytestmark = pytest.mark.integration


@pytest.fixture
def sync_session() -> None:
    """Sync SQLAlchemy Session on in-memory SQLite."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        yield session
    engine.dispose()


@pytest_asyncio.fixture
async def async_session() -> None:
    """Async SQLAlchemy AsyncSession on in-memory SQLite."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session
    await engine.dispose()
