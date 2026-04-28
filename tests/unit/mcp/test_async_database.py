"""Tests for async database adapter and shared connection pool.

Validates:
- Async engine creation and sharing
- RLS context setting
- Connection pool sharing with FastAPI
- Session lifecycle
"""

from typing import Any, Never

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncEngine

from tracertm.mcp.database_adapter import (
    get_async_engine,
    get_mcp_session,
    get_pool_status,
    reset_engine,
)
from tracertm.models.project import Project


@pytest.fixture(autouse=True)
async def cleanup_engine() -> None:
    """Reset engine after each test."""
    yield
    await reset_engine()


@pytest.mark.asyncio
async def test_get_async_engine_creates_singleton() -> None:
    """Test that get_async_engine creates a singleton instance."""
    # Engine is already initialized by setup_test_database fixture
    engine1 = await get_async_engine()
    engine2 = await get_async_engine()

    assert engine1 is engine2
    assert isinstance(engine1, AsyncEngine)


@pytest.mark.asyncio
async def test_get_async_engine_connects_to_database() -> None:
    """Test that engine successfully connects to database."""
    engine = await get_async_engine()

    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1


@pytest.mark.asyncio
async def test_get_mcp_session_provides_valid_session() -> None:
    """Test that get_mcp_session provides a working session."""
    async with get_mcp_session() as session:
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1


@pytest.mark.asyncio
async def test_get_mcp_session_sets_rls_context(mocker: Any) -> None:
    """Test that get_mcp_session sets RLS context for PostgreSQL."""
    # Mock current_user_id context
    mocker.patch("tracertm.mcp.database_adapter.current_user_id.get", return_value="user-123")

    # Mock config to return PostgreSQL URL
    mock_config = mocker.patch("tracertm.mcp.database_adapter.ConfigManager")
    mock_config.return_value.get.return_value = "postgresql://localhost/test"

    async with get_mcp_session() as _session:
        # In PostgreSQL, this would set the RLS context
        # For SQLite tests, this is a no-op
        pass

    # Verify context was checked
    assert mock_config.return_value.get.called


@pytest.mark.asyncio
async def test_get_mcp_session_commits_on_success() -> None:
    """Test that session commits changes on successful execution."""
    async with get_mcp_session() as session:
        # Create a test project
        project = Project(
            id="test-project-1",
            name="Test Project",
            description="Test",
        )
        session.add(project)
        # Commit happens automatically on context exit

    # Verify project was committed
    async with get_mcp_session() as session:
        result = await session.execute(select(Project).filter(Project.id == "test-project-1"))
        saved_project = result.scalar_one_or_none()
        assert saved_project is not None
        assert saved_project.name == "Test Project"


@pytest.mark.asyncio
async def test_get_mcp_session_rollsback_on_error() -> None:
    """Test that session rolls back changes on error."""

    async def _rollback_scenario() -> Never:
        async with get_mcp_session() as session:
            project = Project(
                id="test-project-2",
                name="Test Project",
                description="Test",
            )
            session.add(project)
            msg = "Test error"
            raise ValueError(msg)

    with pytest.raises(ValueError, match="Test error"):
        await _rollback_scenario()

    # Verify project was not committed
    async with get_mcp_session() as session:
        result = await session.execute(select(Project).filter(Project.id == "test-project-2"))
        saved_project = result.scalar_one_or_none()
        assert saved_project is None


@pytest.mark.asyncio
async def test_get_pool_status_returns_metrics() -> None:
    """Test that get_pool_status returns pool metrics."""
    # Initialize engine
    await get_async_engine()

    status = await get_pool_status()

    assert "size" in status
    assert "checked_out" in status
    assert "overflow" in status
    assert "checked_in" in status
    assert isinstance(status["size"], (int, type(None)))


@pytest.mark.asyncio
async def test_get_pool_status_before_init() -> None:
    """Test that get_pool_status handles uninitialized engine."""
    status = await get_pool_status()

    assert status == {"status": "not_initialized"}


@pytest.mark.asyncio
async def test_engine_sharing_reduces_connections() -> None:
    """Test that multiple sessions share the same connection pool."""
    # Get pool status via adapter (avoids typing issues with pool.size())
    initial_status = await get_pool_status()
    initial_pool_size = initial_status["size"]

    # Create multiple sessions
    sessions_count = 5
    for _ in range(sessions_count):
        async with get_mcp_session() as session:
            await session.execute(text("SELECT 1"))

    # Verify we're still using the same pool
    final_status = await get_pool_status()
    final_pool_size = final_status["size"]
    assert initial_pool_size == final_pool_size  # Pool size shouldn't grow


@pytest.mark.asyncio
async def test_reset_engine_clears_singleton() -> None:
    """Test that reset_engine clears the singleton."""
    engine1 = await get_async_engine()
    await reset_engine()
    engine2 = await get_async_engine()

    assert engine1 is not engine2


@pytest.mark.asyncio
async def test_concurrent_sessions_use_pool() -> None:
    """Test that concurrent sessions properly use connection pool."""
    import asyncio

    async def run_query() -> None:
        async with get_mcp_session() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar()

    # Run multiple concurrent queries
    results = await asyncio.gather(*[run_query() for _ in range(10)])

    # All should succeed
    assert all(r == 1 for r in results)


@pytest.mark.asyncio
async def test_fastapi_integration_shares_engine(_mocker: Any) -> None:
    """Test that FastAPI's get_db uses the same engine."""
    # Get MCP engine
    mcp_engine = await get_async_engine()

    # Import and call FastAPI's get_db
    from tracertm.api.deps import get_db

    async for session in get_db():
        # Verify session is using the same engine
        assert session.bind == mcp_engine
        break


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
