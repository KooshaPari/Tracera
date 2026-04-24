from typing import Any

"""Integration tests for database operations."""

import pytest
from services import DatabaseService
from services.database import DatabaseConfig


@pytest.mark.asyncio
class TestDatabaseIntegration:
    """Test database integration."""

    @pytest_asyncio.fixture
    async def db_service(self) -> None:
        """Create database service."""
        config = DatabaseConfig(
            postgres_url="postgresql://mcp_user:mcp_password@localhost/mcp_db",
            memgraph_url="bolt://localhost:7687",
            qdrant_url="http://localhost:6333",
            valkey_url="redis://localhost:6379",
        )
        service = DatabaseService(config)

        try:
            await service.connect()
            yield service
        finally:
            await service.disconnect()

    async def test_postgres_connection(self, db_service: Any) -> None:
        """Test PostgreSQL connection."""
        assert db_service.postgres is not None

    async def test_postgres_query(self, db_service: Any) -> None:
        """Test PostgreSQL query."""
        async with db_service.postgres.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            assert result == 1

    async def test_valkey_connection(self, db_service: Any) -> None:
        """Test Valkey connection."""
        assert db_service.valkey is not None

    async def test_valkey_operations(self, db_service: Any) -> None:
        """Test Valkey operations."""
        # Set value
        await db_service.valkey.set("test_key", "test_value")

        # Get value
        value = await db_service.valkey.get("test_key")
        assert value == b"test_value"

        # Delete value
        await db_service.valkey.delete("test_key")

    async def test_health_check(self, db_service: Any) -> None:
        """Test health check."""
        health = await db_service.health_check()
        assert "postgres" in health
        assert "valkey" in health
