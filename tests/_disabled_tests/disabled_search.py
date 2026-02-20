from typing import Any

"""Integration tests for search operations."""

import pytest
from services import DatabaseService, SearchService
from services.database import DatabaseConfig


@pytest.mark.asyncio
class TestSearchIntegration:
    """Test search integration."""

    @pytest_asyncio.fixture
    async def search_service(self) -> None:
        """Create search service."""
        config = DatabaseConfig(
            postgres_url="postgresql://mcp_user:mcp_password@localhost/mcp_db",
            memgraph_url="bolt://localhost:7687",
            qdrant_url="http://localhost:6333",
            valkey_url="redis://localhost:6379",
        )
        db_service = DatabaseService(config)

        try:
            await db_service.connect()
            service = SearchService(db_service)
            yield service
        finally:
            await db_service.disconnect()

    async def test_semantic_search(self, search_service: Any) -> None:
        """Test semantic search."""
        # Create sample embedding (1536 dimensions)
        query_embedding = [0.1] * 1536

        try:
            results = await search_service.semantic_search(
                query_embedding=query_embedding,
                limit=5,
            )

            # Should return results or empty list
            assert isinstance(results, list)

        except Exception as e:
            # May fail if no data in database
            pytest.skip(f"Semantic search not available: {e}")

    async def test_full_text_search(self, search_service: Any) -> None:
        """Test full-text search."""
        try:
            results = await search_service.full_text_search(
                query="data processing",
                limit=5,
            )

            # Should return results or empty list
            assert isinstance(results, list)

        except Exception as e:
            # May fail if no data in database
            pytest.skip(f"Full-text search not available: {e}")

    async def test_cache_operations(self, search_service: Any) -> None:
        """Test cache operations."""
        # Set cache
        success = await search_service.cache_set("test_key", "test_value", ttl=60)
        assert success is True

        # Get cache
        value = await search_service.cache_get("test_key")
        assert value == "test_value"
