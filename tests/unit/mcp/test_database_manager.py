"""Tests for DatabaseManager (Phase 3)."""

import asyncio

import pytest
from sqlalchemy import text

from tracertm.mcp.database_manager import DatabaseManager, QueryMetrics


@pytest.fixture
def database_url():
    """Test database URL (SQLite)."""
    return "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_manager(database_url):
    """Create DatabaseManager instance."""
    manager = DatabaseManager(database_url)
    await manager.initialize()
    yield manager
    await manager.close()


class TestDatabaseManager:
    """Test DatabaseManager functionality."""

    @pytest.mark.asyncio
    async def test_initialization(self, database_url):
        """Test DatabaseManager initialization."""
        manager = DatabaseManager(database_url)
        assert manager.database_url == database_url
        assert manager._engine is None

        await manager.initialize()
        assert manager._engine is not None
        assert manager._session_factory is not None
        assert manager._initialized is True

        await manager.close()

    @pytest.mark.asyncio
    async def test_singleton_pattern(self, database_url):
        """Test singleton instance."""
        manager1 = await DatabaseManager.get_instance(database_url)
        manager2 = await DatabaseManager.get_instance()

        assert manager1 is manager2

        await manager1.close()

    @pytest.mark.asyncio
    async def test_session_context(self, db_manager):
        """Test async session context manager."""
        async with db_manager.session() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1

    @pytest.mark.asyncio
    async def test_pool_status(self, db_manager):
        """Test connection pool status."""
        status = await db_manager.get_pool_status()

        assert "size" in status
        assert "checked_out" in status
        assert "overflow" in status
        assert "checked_in" in status

    @pytest.mark.asyncio
    async def test_health_check(self, db_manager):
        """Test database health check."""
        health = await db_manager.health_check()

        assert health["status"] == "healthy"
        assert "version" in health
        assert "SQLite" in health["version"]
        assert "pool" in health
        assert "queries" in health

    @pytest.mark.asyncio
    async def test_multiple_sessions(self, db_manager):
        """Test multiple concurrent sessions."""
        async def query_db(value: int):
            async with db_manager.session() as session:
                result = await session.execute(text(f"SELECT {value}"))
                return result.scalar()

        # Run 10 concurrent queries
        tasks = [query_db(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        assert results == list(range(10))


class TestQueryMetrics:
    """Test QueryMetrics functionality."""

    def test_record_query(self):
        """Test recording query execution."""
        metrics = QueryMetrics()

        metrics.record_query("SELECT * FROM items", 50.0)
        metrics.record_query("SELECT * FROM projects", 150.0)

        stats = metrics.get_stats()
        assert stats["total_queries"] == 2
        assert stats["total_duration_ms"] == 200.0
        assert stats["avg_duration_ms"] == 100.0
        assert stats["slow_queries_count"] == 1  # Only 150ms is slow (>100ms)

    def test_slow_query_threshold(self):
        """Test slow query detection."""
        metrics = QueryMetrics()
        metrics.slow_threshold_ms = 100.0

        # Fast query
        metrics.record_query("SELECT 1", 50.0)
        assert len(metrics.slow_queries) == 0

        # Slow query
        metrics.record_query("SELECT * FROM large_table", 150.0)
        assert len(metrics.slow_queries) == 1
        assert metrics.slow_queries[0]["duration_ms"] == 150.0

    def test_reset(self):
        """Test metrics reset."""
        metrics = QueryMetrics()

        metrics.record_query("SELECT 1", 50.0)
        metrics.record_query("SELECT 2", 150.0)

        assert metrics.query_count == 2
        assert len(metrics.slow_queries) == 1

        metrics.reset()

        assert metrics.query_count == 0
        assert len(metrics.slow_queries) == 0
        assert metrics.total_duration == 0.0


@pytest.mark.asyncio
async def test_url_conversion():
    """Test database URL conversion."""
    # PostgreSQL sync -> async
    manager = DatabaseManager("postgresql://user:pass@localhost/db")
    assert manager.database_url == "postgresql+asyncpg://user:pass@localhost/db"

    # SQLite sync -> async
    manager = DatabaseManager("sqlite:///test.db")
    assert manager.database_url == "sqlite+aiosqlite:///test.db"
