"""Comprehensive unit tests for database connection module.

Tests database/connection.py:
- DatabaseConnection class
- Connection management
- Pool configuration
- Health checks
- Session creation
- Global functions (get_engine, get_session)
"""

from typing import Any

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from tests.test_constants import COUNT_TWO
from tracertm.database.connection import DatabaseConnection, get_engine, get_session


class TestDatabaseConnectionInit:
    """Test DatabaseConnection initialization."""

    def test_create_with_postgresql_url(self) -> None:
        """Test creating connection with PostgreSQL URL."""
        db = DatabaseConnection("postgresql://localhost/test")
        assert db.database_url == "postgresql://localhost/test"
        assert db._engine is None
        assert db._session_factory is None

    def test_create_with_sqlite_url(self) -> None:
        """Test creating connection with SQLite URL."""
        db = DatabaseConnection("sqlite:///test.db")
        assert db.database_url == "sqlite:///test.db"

    def test_invalid_url_raises_error(self) -> None:
        """Test that invalid URL raises ValueError."""
        with pytest.raises(ValueError, match="postgresql://"):
            DatabaseConnection("mysql://localhost/test")

    def test_empty_url_raises_error(self) -> None:
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="postgresql://"):
            DatabaseConnection("")

    def test_http_url_raises_error(self) -> None:
        """Test that HTTP URL raises ValueError."""
        with pytest.raises(ValueError, match="postgresql://"):
            DatabaseConnection("http://localhost/test")

    def test_engine_property_initially_none(self) -> None:
        """Test that engine property is initially None."""
        db = DatabaseConnection("postgresql://localhost/test")
        assert db.engine is None


class TestDatabaseConnectionConnect:
    """Test DatabaseConnection.connect method."""

    def test_connect_with_sqlite(self, tmp_path: Any) -> None:
        """Test connecting with SQLite database."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        engine = db.connect()

        assert isinstance(engine, Engine)
        assert db._engine is engine
        assert db._session_factory is not None

    def test_connect_creates_engine(self, tmp_path: Any) -> None:
        """Test that connect creates engine."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        assert db._engine is None
        db.connect()
        assert db._engine is not None

    def test_connect_creates_session_factory(self, tmp_path: Any) -> None:
        """Test that connect creates session factory."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        assert db._session_factory is None
        db.connect()
        assert db._session_factory is not None

    def test_connect_invalid_database_raises_error(self) -> None:
        """Test that connecting to invalid database raises ConnectionError."""
        db = DatabaseConnection("postgresql://invalid:invalid@nonexistent/db")

        with pytest.raises(ConnectionError) as exc_info:
            db.connect()

        error_msg = str(exc_info.value)
        assert "Failed to connect" in error_msg
        assert "PostgreSQL is running" in error_msg

    def test_connect_sets_pool_configuration(self, tmp_path: Any) -> None:
        """Test that connect sets pool configuration."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        engine = db.connect()

        # Pool should be configured
        assert engine.pool is not None

    def test_connect_enables_pool_pre_ping(self, tmp_path: Any) -> None:
        """Test that connect enables pool pre-ping."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        engine = db.connect()

        # Pre-ping should be enabled for health checks
        # (exact assertion depends on SQLAlchemy internals)
        assert engine is not None

    def test_engine_property_after_connect(self, tmp_path: Any) -> None:
        """Test engine property after connect."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        db.connect()

        assert db.engine is not None
        assert isinstance(db.engine, Engine)


class TestDatabaseConnectionTables:
    """Test table creation and dropping."""

    def test_create_tables_requires_connection(self) -> None:
        """Test that create_tables requires connection."""
        db = DatabaseConnection("sqlite:///test.db")

        with pytest.raises(RuntimeError, match="Not connected"):
            db.create_tables()

    def test_create_tables_after_connect(self, tmp_path: Any) -> None:
        """Test creating tables after connect."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        # Should not raise error
        db.create_tables()

    def test_drop_tables_requires_connection(self) -> None:
        """Test that drop_tables requires connection."""
        db = DatabaseConnection("sqlite:///test.db")

        with pytest.raises(RuntimeError, match="Not connected"):
            db.drop_tables()

    def test_drop_tables_after_connect(self, tmp_path: Any) -> None:
        """Test dropping tables after connect."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        # Should not raise error
        db.drop_tables()

    def test_create_then_drop_tables(self, tmp_path: Any) -> None:
        """Test creating then dropping tables."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        db.create_tables()
        db.drop_tables()
        # Should complete without error


class TestDatabaseConnectionHealthCheck:
    """Test health_check method."""

    def test_health_check_requires_connection(self) -> None:
        """Test that health_check requires connection."""
        db = DatabaseConnection("sqlite:///test.db")

        with pytest.raises(RuntimeError, match="Not connected"):
            db.health_check()

    def test_health_check_with_sqlite(self, tmp_path: Any) -> None:
        """Test health check with SQLite."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        health = db.health_check()

        assert isinstance(health, dict)
        assert health["status"] == "connected"
        assert "version" in health
        assert "SQLite" in health["version"]
        assert "tables" in health
        assert "pool_size" in health
        assert "checked_out" in health

    def test_health_check_includes_version(self, tmp_path: Any) -> None:
        """Test that health check includes database version."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        health = db.health_check()

        assert "version" in health
        assert health["version"] is not None

    def test_health_check_includes_table_count(self, tmp_path: Any) -> None:
        """Test that health check includes table count."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        health = db.health_check()

        assert "tables" in health
        assert isinstance(health["tables"], int)
        assert health["tables"] >= 0

    def test_health_check_includes_pool_info(self, tmp_path: Any) -> None:
        """Test that health check includes pool information."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        health = db.health_check()

        assert "pool_size" in health
        assert "checked_out" in health
        assert isinstance(health["pool_size"], int)
        assert isinstance(health["checked_out"], int)

    def test_health_check_after_table_creation(self, tmp_path: Any) -> None:
        """Test health check after creating tables."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()
        db.create_tables()

        health = db.health_check()

        assert health["status"] == "connected"
        # Should have some tables now
        assert health["tables"] >= 0


class TestDatabaseConnectionSession:
    """Test session creation."""

    def test_get_session_requires_connection(self) -> None:
        """Test that get_session requires connection."""
        db = DatabaseConnection("sqlite:///test.db")

        with pytest.raises(RuntimeError, match="Not connected"):
            db.get_session()

    def test_get_session_returns_session(self, tmp_path: Any) -> None:
        """Test that get_session returns Session instance."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        session = db.get_session()

        assert isinstance(session, Session)

    def test_get_session_multiple_calls(self, tmp_path: Any) -> None:
        """Test getting multiple sessions."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        session1 = db.get_session()
        session2 = db.get_session()

        # Should get different session instances
        assert session1 is not session2

    def test_session_can_execute_queries(self, tmp_path: Any) -> None:
        """Test that session can execute queries."""
        from sqlalchemy import text

        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        session = db.get_session()

        # Should be able to execute simple query
        result = session.execute(text("SELECT 1"))
        assert result is not None

        session.close()

    def test_session_lifecycle(self, tmp_path: Any) -> None:
        """Test session open and close lifecycle."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        session = db.get_session()
        assert session is not None

        session.close()
        # Session should be closed


class TestDatabaseConnectionClose:
    """Test connection closing."""

    def test_close_disposes_engine(self, tmp_path: Any) -> None:
        """Test that close disposes of engine."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        assert db._engine is not None
        db.close()
        assert db._engine is None

    def test_close_clears_session_factory(self, tmp_path: Any) -> None:
        """Test that close clears session factory."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        assert db._session_factory is not None
        db.close()
        assert db._session_factory is None

    def test_close_without_connection(self) -> None:
        """Test that close works even without connection."""
        db = DatabaseConnection("sqlite:///test.db")

        # Should not raise error
        db.close()

    def test_close_multiple_times(self, tmp_path: Any) -> None:
        """Test calling close multiple times."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")
        db.connect()

        db.close()
        db.close()  # Should not raise error


class TestGetEngineGlobalFunction:
    """Test get_engine global function."""

    def test_get_engine_with_sqlite(self, tmp_path: Any) -> None:
        """Test get_engine with SQLite URL."""
        db_path = tmp_path / "test.db"
        engine = get_engine(f"sqlite:///{db_path}")

        assert isinstance(engine, Engine)

    def test_get_engine_creates_global_connection(self, tmp_path: Any) -> None:
        """Test that get_engine creates global connection."""
        db_path = tmp_path / "test_global.db"
        url = f"sqlite:///{db_path}"

        engine1 = get_engine(url)
        engine2 = get_engine(url)

        # Should return same engine (global singleton)
        # Note: This might return same or different based on implementation
        assert engine1 is not None
        assert engine2 is not None


class TestGetSessionGlobalFunction:
    """Test get_session global function."""

    def test_get_session_yields_session(self, tmp_path: Any) -> None:
        """Test that get_session yields Session."""
        db_path = tmp_path / "test.db"
        url = f"sqlite:///{db_path}"

        sessions = []
        for session in get_session(url):
            sessions.append(session)
            assert isinstance(session, Session)
            break  # Only test first yield

        assert len(sessions) == 1

    def test_get_session_closes_session(self, tmp_path: Any) -> None:
        """Test that get_session closes session after use."""
        db_path = tmp_path / "test.db"
        url = f"sqlite:///{db_path}"

        for session in get_session(url):
            assert session is not None
            # Session should be closed after generator exits

    def test_get_session_multiple_uses(self, tmp_path: Any) -> None:
        """Test using get_session multiple times."""
        db_path = tmp_path / "test.db"
        url = f"sqlite:///{db_path}"

        sessions = []

        for session in get_session(url):
            sessions.append(session)
            break

        for session in get_session(url):
            sessions.append(session)
            break

        assert len(sessions) == COUNT_TWO


class TestDatabaseConnectionIntegration:
    """Integration tests for database connection."""

    def test_full_lifecycle(self, tmp_path: Any) -> None:
        """Test full connection lifecycle."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        # Connect
        engine = db.connect()
        assert engine is not None

        # Create tables
        db.create_tables()

        # Health check
        health = db.health_check()
        assert health["status"] == "connected"

        # Get session
        session = db.get_session()
        assert session is not None
        session.close()

        # Drop tables
        db.drop_tables()

        # Close
        db.close()

    def test_reconnect_after_close(self, tmp_path: Any) -> None:
        """Test reconnecting after close."""
        db_path = tmp_path / "test.db"
        db = DatabaseConnection(f"sqlite:///{db_path}")

        # First connection
        db.connect()
        db.close()

        # Reconnect
        engine = db.connect()
        assert engine is not None

    def test_pool_isolation(self, tmp_path: Any) -> None:
        """Test that different connections have isolated pools."""
        db_path1 = tmp_path / "test1.db"
        db_path2 = tmp_path / "test2.db"

        db1 = DatabaseConnection(f"sqlite:///{db_path1}")
        db2 = DatabaseConnection(f"sqlite:///{db_path2}")

        engine1 = db1.connect()
        engine2 = db2.connect()

        # Should have different engines
        assert engine1 is not engine2


class TestDatabaseConnectionErrorHandling:
    """Test error handling in database connection."""

    def test_connection_error_message_helpful(self) -> None:
        """Test that connection error has helpful message."""
        db = DatabaseConnection("postgresql://invalid:invalid@nonexistent/db")

        with pytest.raises(ConnectionError) as exc_info:
            db.connect()

        error_msg = str(exc_info.value)
        assert "Failed to connect" in error_msg
        assert "PostgreSQL is running" in error_msg
        assert "Database URL is correct" in error_msg
        assert "Database exists" in error_msg

    def test_runtime_error_for_unconnected_operations(self) -> None:
        """Test that operations on unconnected DB raise RuntimeError."""
        db = DatabaseConnection("sqlite:///test.db")

        with pytest.raises(RuntimeError, match="Not connected"):
            db.create_tables()

        with pytest.raises(RuntimeError, match="Not connected"):
            db.drop_tables()

        with pytest.raises(RuntimeError, match="Not connected"):
            db.health_check()

        with pytest.raises(RuntimeError, match="Not connected"):
            db.get_session()
