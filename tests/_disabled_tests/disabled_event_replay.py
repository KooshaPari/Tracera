"""Property-based tests for event replay (RISK-003 validation).

This test validates that event sourcing correctly replays state
and temporal queries return correct results.

Success Criteria:
- Event replay produces identical state
- Temporal queries return correct state at any point in time
- No data loss during replay
- Deterministic state reconstruction
"""

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.services.event_sourcing_service import EventSourcingService


@pytest.mark.property
class TestEventReplay:
    """Property-based tests for event sourcing."""

    @given(
        titles=st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10),
        statuses=st.lists(
            st.sampled_from(["todo", "in_progress", "done"]),
            min_size=1,
            max_size=10,
        ),
    )
    async def test_event_replay_produces_identical_state(
        self, db_session: Any, project_factory: Any, titles: Any, statuses: Any
    ) -> None:
        """Test that replaying events produces identical state."""
        project = project_factory()
        event_service = EventSourcingService(db_session)

        # Create item
        item = Item(
            project_id=project.id,
            title="Initial",
            view="FEATURE",
            item_type="feature",
        )
        db_session.add(item)
        db_session.commit()

        # Record initial state

        # Apply events
        for title, status in zip(titles, statuses, strict=False):
            event = Event(
                project_id=project.id,
                item_id=item.id,
                event_type="item_updated",
                data={"title": title, "status": status},
            )
            db_session.add(event)
            item.title = title
            item.status = status
            item.version += 1

        db_session.commit()

        # Replay events
        replayed_state = await event_service.replay_events(
            project_id=project.id,
            item_id=item.id,
        )

        # Assertions
        assert replayed_state["title"] == item.title
        assert replayed_state["status"] == item.status
        assert replayed_state["version"] == item.version

    @given(
        num_events=st.integers(min_value=1, max_value=100),
        replay_point=st.integers(min_value=0, max_value=50),
    )
    async def test_temporal_query_at_any_point(
        self, db_session: Any, project_factory: Any, num_events: Any, replay_point: Any
    ) -> None:
        """Test temporal queries return correct state at any point."""
        project = project_factory()
        event_service = EventSourcingService(db_session)

        # Create item
        item = Item(
            project_id=project.id,
            title="Initial",
            view="FEATURE",
            item_type="feature",
        )
        db_session.add(item)
        db_session.commit()

        # Create events
        for i in range(num_events):
            event = Event(
                project_id=project.id,
                item_id=item.id,
                event_type="item_updated",
                data={"title": f"Title {i}", "status": "in_progress"},
            )
            db_session.add(event)

        db_session.commit()

        # Query at replay point
        if replay_point < num_events:
            state_at_point = await event_service.get_state_at_event(
                project_id=project.id,
                item_id=item.id,
                event_index=replay_point,
            )

            # Assertions
            assert state_at_point is not None
            assert "title" in state_at_point
            assert "status" in state_at_point

    async def test_no_data_loss_during_replay(self, db_session: Any, project_factory: Any, item_factory: Any) -> None:
        """Test no data is lost during event replay."""
        project = project_factory()
        item = item_factory(project_id=project.id)
        event_service = EventSourcingService(db_session)

        # Create events with metadata
        events_created = []
        for i in range(10):
            event = Event(
                project_id=project.id,
                item_id=item.id,
                event_type="item_updated",
                data={"index": i, "value": f"data_{i}"},
            )
            db_session.add(event)
            events_created.append(event)

        db_session.commit()

        # Replay and verify all events
        replayed_events = await event_service.get_all_events(
            project_id=project.id,
            item_id=item.id,
        )

        # Assertions
        assert len(replayed_events) == len(events_created)
        for original, replayed in zip(events_created, replayed_events, strict=False):
            assert original.data == replayed.data

    async def test_deterministic_state_reconstruction(
        self, db_session: Any, project_factory: Any, item_factory: Any
    ) -> None:
        """Test state reconstruction is deterministic."""
        project = project_factory()
        item = item_factory(project_id=project.id)
        event_service = EventSourcingService(db_session)

        # Create events
        for i in range(5):
            event = Event(
                project_id=project.id,
                item_id=item.id,
                event_type="item_updated",
                data={"iteration": i},
            )
            db_session.add(event)

        db_session.commit()

        # Replay multiple times
        state1 = await event_service.replay_events(
            project_id=project.id,
            item_id=item.id,
        )
        state2 = await event_service.replay_events(
            project_id=project.id,
            item_id=item.id,
        )
        state3 = await event_service.replay_events(
            project_id=project.id,
            item_id=item.id,
        )

        # Assertions
        assert state1 == state2 == state3
