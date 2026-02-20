"""Chaos Test: Database Resilience.

Tests that the database layer handles connection drops, mid-transaction failures,
and session corruption gracefully -- rolling back cleanly and raising clear errors.

Uses unittest.mock to simulate failures without requiring live infrastructure.
"""

from typing import Any, Never
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from tests.test_constants import COUNT_THREE
from tracertm.core.concurrency import ConcurrencyError, update_with_retry
from tracertm.database.connection import DatabaseConnection


@pytest.mark.chaos
class TestDatabaseConnectionResilience:
    """Verify DatabaseConnection handles failures explicitly (no silent degradation)."""

    def test_connect_raises_connection_error_on_engine_failure(self) -> None:
        """If the underlying engine cannot connect, DatabaseConnection.connect() must raise ConnectionError."""
        db = DatabaseConnection("postgresql://user:pass@localhost:5432/testdb")

        with patch("tracertm.database.connection.create_engine") as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine
            # Simulate the test-connection query exploding
            mock_engine.connect.side_effect = OperationalError(
                "connection refused",
                params=None,
                orig=Exception("conn refused"),
            )

            with pytest.raises(ConnectionError, match="Failed to connect to database"):
                db.connect()

        # Session factory must NOT be set on failure (connect failed before creating it)
        assert db._session_factory is None

    def test_health_check_returns_error_on_query_failure(self) -> None:
        """health_check must report error status when the DB query fails mid-flight."""
        db = DatabaseConnection("sqlite:///fake.db")
        # Manually wire up enough state to bypass "not connected" guard
        mock_engine = MagicMock()
        mock_engine.dialect.name = "sqlite"
        db._engine = mock_engine

        # Simulate a broken connection during the health-check query
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = OperationalError(
            "disk I/O error",
            params=None,
            orig=Exception("disk I/O error"),
        )
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        result = db.health_check()

        assert result["status"] == "error"
        assert "disk I/O error" in result["error"]

    def test_get_session_raises_when_not_connected(self) -> None:
        """get_session must raise RuntimeError when connection was never established."""
        db = DatabaseConnection("sqlite:///fake.db")
        with pytest.raises(RuntimeError, match="Not connected"):
            db.get_session()

    def test_create_tables_raises_when_not_connected(self) -> None:
        """create_tables must raise RuntimeError when engine is None."""
        db = DatabaseConnection("sqlite:///fake.db")
        with pytest.raises(RuntimeError, match="Not connected"):
            db.create_tables()

    def test_close_disposes_engine_and_clears_state(self) -> None:
        """close() must dispose engine and nil out internal references."""
        db = DatabaseConnection("sqlite:///fake.db")
        mock_engine = MagicMock()
        db._engine = mock_engine
        db._session_factory = MagicMock()

        db.close()

        mock_engine.dispose.assert_called_once()
        assert db._engine is None
        assert db._session_factory is None

    def test_invalid_url_raises_value_error(self) -> None:
        """Constructing with an invalid URL scheme must raise ValueError."""
        with pytest.raises(ValueError, match="Database URL must start with"):
            DatabaseConnection("mysql://localhost/db")

    def test_empty_url_raises_value_error(self) -> None:
        """Constructing with empty string must raise ValueError."""
        with pytest.raises(ValueError, match="Database URL must start with"):
            DatabaseConnection("")


@pytest.mark.chaos
class TestTransactionRollbackOnFailure:
    """Verify that transactions roll back cleanly when the DB dies mid-operation."""

    @pytest.mark.asyncio
    async def test_session_rollback_on_execute_failure(self) -> None:
        """When execute() raises OperationalError, the session must be rollback-able."""
        mock_session = AsyncMock()

        # First execute succeeds (e.g., a SELECT), second one blows up mid-transaction
        call_count = 0

        async def execute_side_effect(stmt: Any, *args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return MagicMock(scalar_one_or_none=MagicMock(return_value=None))
            msg = "server closed the connection unexpectedly"
            raise OperationalError(
                msg,
                params=None,
                orig=Exception("connection lost"),
            )

        mock_session.execute = AsyncMock(side_effect=execute_side_effect)
        mock_session.rollback = AsyncMock()

        # Simulate a two-step operation where the second step fails
        try:
            await mock_session.execute(text("SELECT 1"))  # succeeds
            await mock_session.execute(text("INSERT INTO items ..."))  # fails
        except OperationalError:
            await mock_session.rollback()

        mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_flush_failure_triggers_rollback(self) -> None:
        """When flush() raises (e.g., FK violation during DB hiccup), rollback must execute."""
        mock_session = AsyncMock()
        mock_session.flush.side_effect = OperationalError(
            "could not serialize access",
            params=None,
            orig=Exception("serialization failure"),
        )
        mock_session.rollback = AsyncMock()

        with pytest.raises(OperationalError):
            await mock_session.flush()

        await mock_session.rollback()
        mock_session.rollback.assert_awaited_once()


@pytest.mark.chaos
class TestOptimisticLockingUnderFailure:
    """Verify that update_with_retry handles ConcurrencyError correctly."""

    @pytest.mark.asyncio
    async def test_retry_exhaustion_raises_concurrency_error(self) -> None:
        """When all retries fail with ConcurrencyError, it must propagate."""
        call_count = 0

        async def always_conflict() -> Never:
            nonlocal call_count
            call_count += 1
            msg = f"version mismatch attempt {call_count}"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError, match="Failed after 3 retries"):
            await update_with_retry(always_conflict, max_retries=3, base_delay=0.01)

        # Must have been called exactly max_retries times
        assert call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_retry_succeeds_after_transient_conflict(self) -> None:
        """update_with_retry must succeed when the conflict resolves before exhaustion."""
        call_count = 0

        async def transient_conflict() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_THREE:
                msg = "version mismatch"
                raise ConcurrencyError(msg)
            return "success"

        result = await update_with_retry(transient_conflict, max_retries=5, base_delay=0.01)

        assert result == "success"
        assert call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_non_concurrency_error_not_retried(self) -> None:
        """Non-ConcurrencyError exceptions must NOT be retried -- they propagate immediately."""
        call_count = 0

        async def unexpected_error() -> Never:
            nonlocal call_count
            call_count += 1
            msg = "something unrelated broke"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="something unrelated broke"):
            await update_with_retry(unexpected_error, max_retries=5, base_delay=0.01)

        # Must have been called exactly once (no retry for ValueError)
        assert call_count == 1
