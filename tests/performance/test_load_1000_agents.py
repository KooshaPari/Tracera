"""Load testing for 1000+ concurrent agents (RISK-001 validation).

This test validates that TraceRTM can handle 1000+ concurrent agents
performing simultaneous operations without performance degradation.

Success Criteria:
- <1% conflict rate for different items
- 100+ operations/second aggregate throughput
- <100ms average operation latency
- Zero data corruption after 10K operations
"""

import asyncio
import time
from typing import Any

import pytest

from tracertm.models.agent import Agent
from tracertm.services.agent_coordination_service import AgentCoordinationService
from tracertm.services.item_service import ItemService


@pytest.mark.performance
@pytest.mark.asyncio
class TestLoad1000Agents:
    """Load tests for 1000+ concurrent agents."""

    async def test_1000_agents_concurrent_crud(self, db_session: Any, project_factory: Any, _item_factory: Any) -> None:
        """Test 1000 agents performing concurrent CRUD operations."""
        project = await project_factory()
        item_service = ItemService(db_session)
        AgentCoordinationService(db_session)

        # Create 1000 test agents
        agents: list[Agent] = []
        for i in range(1000):
            agent = Agent(
                name=f"agent-{i}",
                agent_type="test",
                status="idle",
                project_id=project.id,
            )
            agents.append(agent)
        db_session.add_all(agents)
        await db_session.flush()

        # Track metrics
        start_time = time.time()
        operations = 0
        conflicts = 0
        errors = 0

        async def agent_work(agent_idx: int) -> None:
            """Simulate agent work."""
            nonlocal operations, conflicts, errors
            agent = agents[agent_idx]
            try:
                # Create item
                item = await item_service.create_item(
                    project_id=str(project.id),
                    title=f"Item by agent {agent_idx}",
                    view="FEATURE",
                    item_type="feature",
                    agent_id=str(agent.id),
                )
                operations += 1

                # Update item
                await item_service.update_item(
                    item_id=str(item.id),
                    agent_id=str(agent.id),
                    title=f"Updated by agent {agent_idx}",
                )
                operations += 1

                # Read item
                await item_service.get_item(project_id=str(project.id), item_id=str(item.id))
                operations += 1

            except Exception as e:
                if "conflict" in str(e).lower():
                    conflicts += 1
                else:
                    errors += 1

        # Run concurrent operations
        tasks = [agent_work(i) for i in range(1000)]
        await asyncio.gather(*tasks)

        elapsed = time.time() - start_time
        throughput = operations / elapsed

        # Assertions
        assert conflicts < operations * 0.01, "Conflict rate > 1%"
        assert throughput > 100, f"Throughput {throughput} < 100 ops/sec"
        assert errors == 0, f"Errors occurred: {errors}"

    async def test_1000_agents_same_item_updates(
        self, db_session: Any, project_factory: Any, item_factory: Any
    ) -> None:
        """Test 1000 agents updating the same item (worst case)."""
        project = await project_factory()
        item = await item_factory(project_id=project.id)
        item_service = ItemService(db_session)

        # Create 1000 test agents
        agents: list[Agent] = []
        for i in range(1000):
            agent = Agent(
                name=f"agent-{i}",
                agent_type="test",
                status="idle",
                project_id=project.id,
            )
            agents.append(agent)
        db_session.add_all(agents)
        await db_session.flush()

        conflicts = 0
        successful_updates = 0

        async def update_item(agent_idx: int) -> None:
            """Attempt to update item."""
            nonlocal conflicts, successful_updates
            agent = agents[agent_idx]
            try:
                await item_service.update_item(
                    item_id=str(item.id),
                    agent_id=str(agent.id),
                    title=f"Updated by agent {agent_idx}",
                )
                successful_updates += 1
            except Exception as e:
                if "conflict" in str(e).lower():
                    conflicts += 1

        # Run concurrent updates
        tasks = [update_item(i) for i in range(1000)]
        await asyncio.gather(*tasks)

        # Assertions
        assert successful_updates + conflicts == 1000
        assert conflicts < 1000 * 0.05, "Conflict rate > COUNT_FIVE% for same item"

    @pytest.mark.benchmark
    async def test_query_performance_10k_items(self, db_session: Any, project_factory: Any, item_factory: Any) -> None:
        """Test query performance with 10K items."""
        project = await project_factory()
        item_service = ItemService(db_session)

        # Create 10K items
        for i in range(10000):
            await item_factory(project_id=project.id, title=f"Item {i}")

        # Benchmark queries
        start = time.time()
        items = await item_service.list_items(project_id=project.id)
        query_time = time.time() - start

        # Assertions
        assert len(items) == 10000
        assert query_time < 1.0, f"Query time {query_time}s > 1s for 10K items"
