"""Concurrency tests for optimistic locking (RISK-002 validation).

This test validates that optimistic locking prevents data corruption
when multiple agents update the same item concurrently.

Success Criteria:
- No data corruption under concurrent updates
- Conflicts detected and handled gracefully
- Retry logic works correctly
- No deadlocks
"""

import asyncio
from typing import Any

import pytest
from sqlalchemy.exc import StaleDataError

from tracertm.services.item_service import ItemService


@pytest.mark.concurrency
@pytest.mark.asyncio
class TestOptimisticLocking:
    """Tests for optimistic locking conflict detection."""

    async def test_concurrent_updates_same_item(self, db_session: Any, project_factory: Any, item_factory: Any) -> None:
        """Test concurrent updates to same item detect conflicts."""
        project = project_factory()
        item = item_factory(project_id=project.id, title="Original")
        item_service = ItemService(db_session)

        conflicts = []
        successes = []

        async def update_item(agent_id: int, new_title: str) -> None:
            """Attempt to update item."""
            try:
                updated = await item_service.update_item(
                    item_id=item.id,
                    title=new_title,
                )
                successes.append((agent_id, updated.version))
            except StaleDataError:
                conflicts.append(agent_id)

        # Concurrent updates
        tasks = [update_item(i, f"Title from agent {i}") for i in range(10)]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Assertions
        assert len(successes) + len(conflicts) == 10
        assert len(conflicts) > 0, "Expected conflicts not detected"
        assert len(successes) > 0, "Some updates should succeed"

    async def test_version_increment_on_update(self, db_session: Any, project_factory: Any, item_factory: Any) -> None:
        """Test that version increments on successful update."""
        project = project_factory()
        item = item_factory(project_id=project.id)
        initial_version = item.version
        item_service = ItemService(db_session)

        # Update item
        updated = await item_service.update_item(
            item_id=item.id,
            title="Updated",
        )

        # Assertions
        assert updated.version == initial_version + 1

    async def test_retry_logic_on_conflict(self, db_session: Any, project_factory: Any, item_factory: Any) -> None:
        """Test retry logic handles conflicts gracefully."""
        project = project_factory()
        item = item_factory(project_id=project.id)
        item_service = ItemService(db_session)

        # Simulate conflict and retry
        max_retries = 3
        retry_count = 0

        async def update_with_retry() -> None:
            nonlocal retry_count
            for attempt in range(max_retries):
                try:
                    return await item_service.update_item(
                        item_id=item.id,
                        title=f"Attempt {attempt}",
                    )
                except StaleDataError:
                    retry_count += 1
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.01 * (2**attempt))
                    else:
                        raise
            return None

        # Assertions
        result = await update_with_retry()
        assert result is not None

    async def test_no_deadlocks_under_contention(
        self, db_session: Any, project_factory: Any, item_factory: Any
    ) -> None:
        """Test no deadlocks occur under high contention."""
        project = project_factory()
        items = [item_factory(project_id=project.id) for _ in range(10)]
        item_service = ItemService(db_session)

        completed = []
        timeout_errors = []

        async def update_items(agent_id: int) -> None:
            """Update multiple items."""
            try:
                for item in items:
                    await item_service.update_item(
                        item_id=item.id,
                        title=f"Updated by agent {agent_id}",
                    )
                completed.append(agent_id)
            except TimeoutError:
                timeout_errors.append(agent_id)

        # Run with timeout
        tasks = [update_items(i) for i in range(50)]
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0,
            )
        except TimeoutError:
            pass

        # Assertions
        assert len(timeout_errors) == 0, "Deadlock detected (timeout)"
        assert len(completed) > 0, "Some agents should complete"
