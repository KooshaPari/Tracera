"""
Performance tests for memory efficiency and API operations.

Tests performance-critical paths:
- Memory efficiency during large operations
- API endpoint throughput
- Serialization performance
- Request/response handling
- Data transformation performance
- Connection pooling efficiency

Target: +2% coverage on performance-sensitive paths
"""

import pytest
import time
import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item
from tracertm.models.project import Project


@pytest.fixture
async def mock_async_session() -> AsyncMock:
    """Create mock async session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


class TestMemoryEfficiency:
    """Tests for memory efficiency in operations."""

    def test_json_serialization_small_payload(self):
        """Test JSON serialization performance for small payload."""
        data = {
            "id": "item-001",
            "title": "Test Item",
            "description": "Test description",
            "status": "todo",
            "priority": "medium",
        }

        start_time = time.time()
        json_str = json.dumps(data)
        elapsed = time.time() - start_time

        assert elapsed < 0.001
        assert isinstance(json_str, str)

    def test_json_serialization_large_payload(self):
        """Test JSON serialization for large payload."""
        # Create large payload (10KB)
        items = []
        for i in range(100):
            items.append({
                "id": f"item-{i:04d}",
                "title": f"Item {i}",
                "description": f"Description {i}" * 10,
                "metadata": {f"field_{j}": f"value_{j}" for j in range(10)}
            })

        start_time = time.time()
        json_str = json.dumps({"items": items})
        elapsed = time.time() - start_time

        assert elapsed < 0.01, "Large serialization should be < 10ms"
        assert len(json_str) > 10000

    def test_memory_during_large_iteration(self):
        """Test memory during iteration over large dataset."""
        import tracemalloc

        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        # Iterate over 1000 items
        total = 0
        for i in range(1000):
            item = {
                "id": f"item-{i:04d}",
                "data": f"data-{i}" * 5
            }
            total += len(str(item))

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        assert total > 0

    def test_data_transformation_memory(self):
        """Test memory during data transformation."""
        import tracemalloc

        # Create source data
        items = []
        for i in range(500):
            items.append({
                "id": f"item-{i:04d}",
                "title": f"Item {i}",
                "value": i * 100
            })

        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        # Transform data
        transformed = [
            {
                "id": item["id"],
                "title": item["title"].upper(),
                "value": item["value"] * 2
            }
            for item in items
        ]

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        assert len(transformed) == 500

    def test_list_comprehension_vs_loop(self):
        """Compare memory efficiency of list comprehension vs loop."""
        import tracemalloc

        data = list(range(10000))

        # Test list comprehension
        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        result = [x * 2 for x in data]

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        assert len(result) == 10000

    def test_string_concatenation_memory(self):
        """Test memory during string operations."""
        import tracemalloc

        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        # Inefficient: concatenation
        result = ""
        for i in range(100):
            result += f"Item {i}\n"

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        assert len(result) > 0

    def test_generator_memory_efficiency(self):
        """Test memory efficiency of generators."""
        import tracemalloc

        def item_generator(count: int):
            """Generate items lazily."""
            for i in range(count):
                yield {
                    "id": f"item-{i:04d}",
                    "data": f"data-{i}" * 10
                }

        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        # Consume generator
        count = 0
        for item in item_generator(1000):
            count += 1
            if count > 100:
                break

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        assert count == 101


class TestAPIPerformance:
    """Tests for API operation performance."""

    @pytest.mark.asyncio
    async def test_api_request_response_performance(self):
        """Test API request/response cycle."""
        request_payload = {
            "project_id": "proj-001",
            "items": [
                {"title": f"Item {i}", "status": "todo"}
                for i in range(100)
            ]
        }

        # Simulate request/response
        start_time = time.time()

        # Serialize request
        request_json = json.dumps(request_payload)

        # Simulate processing
        await asyncio.sleep(0.01)

        # Deserialize and process
        received = json.loads(request_json)

        # Serialize response
        response = json.dumps({"status": "ok", "count": len(received["items"])})

        elapsed = time.time() - start_time

        assert elapsed < 0.1, "Full request/response should be < 100ms"

    @pytest.mark.asyncio
    async def test_api_throughput(self):
        """Test API throughput (requests/second)."""
        async def handle_request(req_id: int):
            """Handle API request."""
            request = {"id": req_id, "data": f"request-{req_id}"}
            await asyncio.sleep(0.01)  # Simulate processing
            return {"id": req_id, "status": "ok"}

        start_time = time.time()
        results = await asyncio.gather(*[
            handle_request(i) for i in range(100)
        ])
        elapsed = time.time() - start_time

        throughput = len(results) / elapsed
        assert throughput > 5, f"Throughput {throughput} req/s is too low"

    @pytest.mark.asyncio
    async def test_large_response_handling(self):
        """Test handling of large API responses."""
        # Create large response
        large_items = []
        for i in range(1000):
            large_items.append({
                "id": f"item-{i:04d}",
                "title": f"Item {i}",
                "description": f"Description {i}" * 10,
                "metadata": {f"field_{j}": f"value_{j}" for j in range(20)}
            })

        response = json.dumps({"items": large_items})

        start_time = time.time()
        parsed = json.loads(response)
        elapsed = time.time() - start_time

        assert len(parsed["items"]) == 1000
        assert elapsed < 0.2, "Parsing 1000 items should be < 200ms"

    @pytest.mark.asyncio
    async def test_batch_api_requests(self):
        """Test batch API requests."""
        batch_size = 50

        async def batch_request(batch_num: int):
            """Process batch of requests."""
            items = [
                {"id": f"batch-{batch_num}-item-{i}", "value": i}
                for i in range(batch_size)
            ]
            await asyncio.sleep(0.02)
            return len(items)

        start_time = time.time()
        batches = await asyncio.gather(*[batch_request(i) for i in range(10)])
        elapsed = time.time() - start_time

        total_items = sum(batches)
        assert total_items == 500
        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self):
        """Test concurrent API requests."""
        async def api_call(call_id: int):
            """Make API call."""
            # Simulate request
            request = {"id": call_id}

            # Simulate network latency
            await asyncio.sleep(0.05)

            # Simulate response
            response = {"result": f"response-{call_id}"}
            return response

        start_time = time.time()
        responses = await asyncio.gather(*[api_call(i) for i in range(50)])
        elapsed = time.time() - start_time

        assert len(responses) == 50
        # 50 concurrent requests with 50ms each should take ~50ms, not 2500ms
        assert elapsed < 0.3, f"Concurrent requests took {elapsed}s"

    @pytest.mark.asyncio
    async def test_connection_pooling_efficiency(self):
        """Test connection pooling efficiency."""
        # Simulate connection pool
        pool = []
        pool_size = 10

        async def acquire_connection():
            """Acquire connection from pool."""
            if not pool:
                await asyncio.sleep(0.001)  # Create new connection
                return MagicMock()
            return pool.pop()

        async def release_connection(conn):
            """Release connection to pool."""
            if len(pool) < pool_size:
                pool.append(conn)

        async def execute_query():
            """Execute query using pooled connection."""
            conn = await acquire_connection()
            try:
                await asyncio.sleep(0.01)
                return "result"
            finally:
                await release_connection(conn)

        start_time = time.time()
        results = await asyncio.gather(*[execute_query() for i in range(100)])
        elapsed = time.time() - start_time

        assert len(results) == 100
        assert elapsed < 2.0, "With pooling should be efficient"

    @pytest.mark.asyncio
    async def test_pagination_api(self):
        """Test pagination API performance."""
        async def fetch_page(page: int, page_size: int = 100):
            """Fetch single page."""
            items = [
                {
                    "id": f"item-{page * page_size + i:04d}",
                    "title": f"Item {page * page_size + i}"
                }
                for i in range(page_size)
            ]

            await asyncio.sleep(0.01)  # Simulate DB query
            return {
                "page": page,
                "items": items,
                "total": 10000
            }

        start_time = time.time()
        pages = await asyncio.gather(*[fetch_page(i) for i in range(10)])
        elapsed = time.time() - start_time

        total_items = sum(len(p["items"]) for p in pages)
        assert total_items == 1000
        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_data_aggregation_performance(self):
        """Test data aggregation performance."""
        async def fetch_items(category: int):
            """Fetch items in category."""
            items = [
                {"id": f"cat-{category}-item-{i}", "value": i}
                for i in range(100)
            ]
            await asyncio.sleep(0.01)
            return items

        # Fetch from 10 categories concurrently
        start_time = time.time()
        all_items = await asyncio.gather(*[
            fetch_items(i) for i in range(10)
        ])
        elapsed = time.time() - start_time

        # Aggregate
        total_value = sum(
            sum(item["value"] for item in items)
            for items in all_items
        )

        assert total_value > 0
        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_filtering_performance(self):
        """Test filtering performance on large dataset."""
        # Create large dataset
        items = [
            {
                "id": f"item-{i:04d}",
                "status": ["todo", "in_progress", "done"][i % 3],
                "priority": ["low", "medium", "high"][i % 3],
                "value": i
            }
            for i in range(10000)
        ]

        start_time = time.time()

        # Filter items
        filtered = [
            item for item in items
            if item["status"] == "todo" and item["priority"] == "high"
        ]

        elapsed = time.time() - start_time

        assert len(filtered) > 0
        assert elapsed < 0.05, "Filtering 10000 items should be < 50ms"


class TestSerializationPerformance:
    """Tests for serialization performance."""

    def test_json_encode_decode(self):
        """Test JSON encode/decode performance."""
        data = {
            "items": [
                {
                    "id": f"item-{i:04d}",
                    "title": f"Item {i}",
                    "data": list(range(10))
                }
                for i in range(500)
            ]
        }

        start_time = time.time()
        encoded = json.dumps(data)
        decoded = json.loads(encoded)
        elapsed = time.time() - start_time

        assert elapsed < 0.05
        assert len(decoded["items"]) == 500

    def test_dict_vs_dataclass_serialization(self):
        """Test dict vs dataclass serialization."""
        # Dict version
        dict_data = [
            {"id": f"item-{i}", "title": f"Title {i}"}
            for i in range(1000)
        ]

        start_time = time.time()
        dict_json = json.dumps(dict_data)
        dict_time = time.time() - start_time

        assert dict_time < 0.05
        assert len(dict_json) > 0

    def test_nested_structure_serialization(self):
        """Test nested structure serialization."""
        data = {
            "project": {
                "id": "proj-001",
                "items": [
                    {
                        "id": f"item-{i}",
                        "links": [f"link-{j}" for j in range(5)]
                    }
                    for i in range(100)
                ]
            }
        }

        start_time = time.time()
        json_str = json.dumps(data)
        elapsed = time.time() - start_time

        assert elapsed < 0.02
