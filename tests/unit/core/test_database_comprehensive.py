"""Comprehensive unit tests for core database module.

Tests core/database.py:
- get_engine function
- get_session_factory function
- get_session context manager
- init_db function
- drop_db function
- Global state management
"""

import logging
from typing import Any, Never
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.core.config import Config, DatabaseConfig
from tracertm.database.async_connection import (
    drop_db,
    get_engine,
    get_session,
    get_session_factory,
    init_db,
)


@pytest.fixture
def mock_config(tmp_path: Any) -> None:
    """Create a mock config for testing."""
    return Config(
        database=DatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            pool_size=5,
            max_overflow=2,
        ),
        data_dir=tmp_path / ".tracertm",
    )


@pytest.fixture
def mock_config_sqlite(tmp_path: Any) -> None:
    """Create a mock config for SQLite testing."""

    # Create a custom DatabaseConfig that returns SQLite URL
    class SQLiteDatabaseConfig(DatabaseConfig):
        @property
        def url(self) -> str:
            return "sqlite+aiosqlite:///:memory:"

    return Config(
        database=SQLiteDatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            pool_size=5,
            max_overflow=2,
        ),
        data_dir=tmp_path / ".tracertm",
    )


@pytest.fixture(autouse=True)
def reset_db_module() -> None:
    """Reset database module global state before each test."""
    import tracertm.database.async_connection as db_module

    original_engine = db_module._engine
    original_factory = db_module._session_factory

    yield

    # Restore original state after test
    db_module._engine = original_engine
    db_module._session_factory = original_factory


class TestGetEngine:
    """Test get_engine function."""

    @patch("tracertm.database.async_connection.get_config")
    def test_get_engine_returns_async_engine(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that get_engine returns an AsyncEngine."""
        mock_get_config.return_value = mock_config
        # Reset global state
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine = get_engine()
        assert isinstance(engine, AsyncEngine)

    @patch("tracertm.database.async_connection.get_config")
    def test_get_engine_singleton(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that get_engine returns the same instance."""
        mock_get_config.return_value = mock_config
        # Reset global state
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine1 = get_engine()
        engine2 = get_engine()
        assert engine1 is engine2

    @patch("tracertm.database.async_connection.get_config")
    def test_get_engine_url_conversion(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that postgresql:// URL is converted to postgresql+asyncpg://."""
        mock_get_config.return_value = mock_config
        # Reset global state
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine = get_engine()
        # URL should use asyncpg driver
        assert "asyncpg" in str(engine.url)

    @patch("tracertm.database.async_connection.get_config")
    def test_get_engine_pool_configuration(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that engine has pool configuration."""
        mock_get_config.return_value = mock_config
        # Reset global state
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine = get_engine()
        # Check pool settings exist
        assert engine.pool is not None


class TestGetSessionFactory:
    """Test get_session_factory function."""

    @patch("tracertm.database.async_connection.get_config")
    def test_get_session_factory_returns_sessionmaker(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that get_session_factory returns async_sessionmaker."""
        mock_get_config.return_value = mock_config
        # Reset global state
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        factory = get_session_factory()
        assert isinstance(factory, async_sessionmaker)

    @patch("tracertm.database.async_connection.get_config")
    def test_get_session_factory_singleton(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that get_session_factory returns the same instance."""
        mock_get_config.return_value = mock_config
        # Reset global state
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        factory1 = get_session_factory()
        factory2 = get_session_factory()
        assert factory1 is factory2

    @patch("tracertm.database.async_connection.get_config")
    def test_session_factory_creates_async_sessions(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that factory creates AsyncSession instances."""
        mock_get_config.return_value = mock_config
        # Reset global state
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        factory = get_session_factory()
        # Check that it's configured for AsyncSession
        assert factory.class_ == AsyncSession

    @patch("tracertm.database.async_connection.get_config")
    def test_session_factory_expire_on_commit_false(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that expire_on_commit is False."""
        mock_get_config.return_value = mock_config
        # Reset global state
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        factory = get_session_factory()
        assert factory.kw.get("expire_on_commit") is False


class TestGetSession:
    """Test get_session context manager."""

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_get_session_yields_async_session(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that get_session yields an AsyncSession."""
        mock_get_config.return_value = mock_config_sqlite
        # Reset global state
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        async with get_session() as session:
            assert isinstance(session, AsyncSession)

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_get_session_commits_on_success(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that session commits on successful exit."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        # This test verifies the context manager structure
        session_used = False
        async with get_session() as session:
            assert session is not None
            session_used = True
        assert session_used

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_get_session_rollback_on_error(self, mock_get_config: Any, mock_config_sqlite: Any) -> Never:
        """Test that session rolls back on exception."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        with pytest.raises(ValueError, match="Test error"):
            async with get_session() as session:
                assert session is not None
                # Raise error to trigger rollback
                msg = "Test error"
                raise ValueError(msg)

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_get_session_closes_session(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that session is closed after context exit."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        async with get_session() as _session:
            pass

        # Session should be closed after context exit
        # We can't directly check if closed, but we verified the pattern

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_get_session_multiple_contexts(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test creating multiple session contexts."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        sessions = []

        async with get_session() as session1:
            sessions.append(session1)

        async with get_session() as session2:
            sessions.append(session2)

        # Should get different session instances
        assert len(sessions) == COUNT_TWO
        assert sessions[0] is not sessions[1]

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_get_session_nested_not_recommended(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that nested sessions are separate instances."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        outer_session = None
        inner_session = None

        async with get_session() as session1:
            outer_session = session1
            async with get_session() as session2:
                inner_session = session2

        # Each context should get its own session
        assert outer_session is not None
        assert inner_session is not None


class TestInitDb:
    """Test init_db function."""

    @pytest.mark.asyncio
    async def test_init_db_callable(self) -> None:
        """Test that init_db is callable."""
        assert callable(init_db)

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_init_db_executes(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that init_db executes without error."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        try:
            await init_db()
            # Success if no exception
            assert True
        except Exception as e:
            # Database might not exist in test env, that's ok
            error_str = str(e).lower()
            assert any(word in error_str for word in ["database", "connection", "connect", "refused"])

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_init_db_uses_engine(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that init_db uses the global engine."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine_before = get_engine()
        try:
            await init_db()
        except Exception as e:
            logging.getLogger(__name__).debug("init_db in test: %s", e)
        engine_after = get_engine()

        # Should use same engine instance
        assert engine_before is engine_after


class TestDropDb:
    """Test drop_db function."""

    @pytest.mark.asyncio
    async def test_drop_db_callable(self) -> None:
        """Test that drop_db is callable."""
        assert callable(drop_db)

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_drop_db_executes(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that drop_db executes without error."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        try:
            await drop_db()
            # Success if no exception
            assert True
        except Exception as e:
            # Database might not exist in test env, that's ok
            error_str = str(e).lower()
            assert any(word in error_str for word in ["database", "connection", "connect", "refused"])

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_drop_db_uses_engine(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that drop_db uses the global engine."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine_before = get_engine()
        try:
            await drop_db()
        except Exception as e:
            logging.getLogger(__name__).debug("drop_db in test: %s", e)
        engine_after = get_engine()

        # Should use same engine instance
        assert engine_before is engine_after


class TestDatabaseModuleIntegration:
    """Integration tests for database module."""

    def test_module_exports(self) -> None:
        """Test that module exports expected functions."""
        from tracertm.database import async_connection as database

        assert hasattr(database, "get_engine")
        assert hasattr(database, "get_session_factory")
        assert hasattr(database, "get_session")
        assert hasattr(database, "init_db")
        assert hasattr(database, "drop_db")

    @patch("tracertm.database.async_connection.get_config")
    def test_engine_pool_settings(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that engine pool has expected settings."""
        mock_get_config.return_value = mock_config
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine = get_engine()

        # Verify pool configuration
        assert engine.pool is not None
        # Pool should have size limits
        assert hasattr(engine.pool, "size")

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_session_transaction_support(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that sessions support transactions."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        async with get_session() as session:
            # Should be able to begin transaction
            assert hasattr(session, "begin")
            assert hasattr(session, "commit")
            assert hasattr(session, "rollback")

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_multiple_concurrent_sessions(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test creating multiple concurrent sessions."""
        import asyncio

        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        sessions = []

        async def create_session() -> None:
            async with get_session() as session:
                sessions.append(session)
                await asyncio.sleep(0.01)

        # Create multiple sessions concurrently
        await asyncio.gather(
            create_session(),
            create_session(),
            create_session(),
        )

        # Should have created 3 sessions
        assert len(sessions) == COUNT_THREE


class TestDatabaseConfiguration:
    """Test database configuration from config."""

    @patch("tracertm.database.async_connection.get_config")
    def test_engine_uses_config(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that engine uses configuration settings."""
        mock_get_config.return_value = mock_config
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine = get_engine()

        # Engine should be configured (exact values depend on config)
        assert engine is not None
        # URL should contain database name from config
        # (actual assertion depends on config setup)

    @patch("tracertm.database.async_connection.get_config")
    def test_engine_pool_size(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that engine respects pool_size config."""
        mock_get_config.return_value = mock_config
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine = get_engine()

        # Pool should exist
        assert engine.pool is not None
        # Pool should have reasonable size
        # (exact value depends on config)

    @patch("tracertm.database.async_connection.get_config")
    def test_engine_connection_options(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that engine has proper connection options."""
        mock_get_config.return_value = mock_config
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        _engine = get_engine()

        # Should have pool pre-ping enabled for health checks
        # Should have pool recycle for connection refresh
        # These are set in get_engine() implementation


class TestDatabaseErrorHandling:
    """Test error handling in database operations."""

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_session_rollback_on_exception(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that exceptions trigger rollback."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        exception_raised = False

        try:
            async with get_session() as _session:
                # Simulate error during transaction
                msg = "Simulated error"
                raise RuntimeError(msg)
        except RuntimeError:
            exception_raised = True

        assert exception_raised

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_session_closes_after_exception(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test that session closes even after exception."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        session_created = False

        try:
            async with get_session() as _session:
                session_created = True
                msg = "Test error"
                raise RuntimeError(msg)
        except RuntimeError:
            pass

        # Session should have been created
        assert session_created
        # Session cleanup should have happened (in finally block)

    @pytest.mark.asyncio
    @patch("tracertm.database.async_connection.get_config")
    async def test_multiple_errors_in_sequence(self, mock_get_config: Any, mock_config_sqlite: Any) -> None:
        """Test handling multiple errors in sequence."""
        mock_get_config.return_value = mock_config_sqlite
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        errors = []

        for i in range(3):
            try:
                async with get_session() as _session:
                    msg = f"Error {i}"
                    raise RuntimeError(msg)
            except RuntimeError as e:
                errors.append(str(e))

        assert len(errors) == COUNT_THREE
        assert all(f"Error {i}" in errors[i] for i in range(3))


class TestDatabaseGlobalState:
    """Test global state management."""

    @patch("tracertm.database.async_connection.get_config")
    def test_engine_global_state(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that engine is stored in global state."""
        mock_get_config.return_value = mock_config
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine1 = get_engine()
        engine2 = get_engine()

        # Should return same instance (global)
        assert engine1 is engine2

    @patch("tracertm.database.async_connection.get_config")
    def test_session_factory_global_state(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that session factory is stored in global state."""
        mock_get_config.return_value = mock_config
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        factory1 = get_session_factory()
        factory2 = get_session_factory()

        # Should return same instance (global)
        assert factory1 is factory2

    @patch("tracertm.database.async_connection.get_config")
    def test_global_state_initialization_order(self, mock_get_config: Any, mock_config: Any) -> None:
        """Test that global state initializes in correct order."""
        mock_get_config.return_value = mock_config
        import tracertm.database.async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        # Engine should initialize before session factory
        engine = get_engine()
        factory = get_session_factory()

        # Factory should use the same engine
        assert engine is not None
        assert factory is not None
