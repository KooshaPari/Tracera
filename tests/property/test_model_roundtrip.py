"""Property-based tests for Pydantic model serialize/deserialize roundtrips.

Tests that models survive JSON roundtrips and that serialization is deterministic.
"""

from datetime import UTC, datetime
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tracertm.schemas.item import ItemCreate, ItemUpdate
from tracertm.schemas.link import LinkCreate
from tracertm.schemas.specification import (
    ADRCreate,
    ADRStatus,
    FeatureCreate,
    FeatureStatus,
    StateTransition,
)
from tracertm.schemas.test_case import (
    TestStep as TStep,
)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

safe_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
    min_size=1,
    max_size=100,
)

short_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N")),
    min_size=1,
    max_size=50,
)

json_safe_values = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False, allow_infinity=False) | safe_text,
    lambda children: st.lists(children, max_size=3) | st.dictionaries(short_text, children, max_size=3),
    max_leaves=10,
)

metadata_st = st.dictionaries(short_text, json_safe_values, max_size=5)

uuid_st = st.uuids().map(str)

item_status_st = st.sampled_from(["todo", "in_progress", "done", "blocked"])
view_st = st.sampled_from(["FEATURE", "CODE", "TEST", "API", "DESIGN", "REQUIREMENT"])

now = datetime.now(tz=UTC)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.property
class TestItemRoundtrip:
    """ItemCreate model roundtrip tests."""

    @given(
        title=st.text(min_size=1, max_size=500, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
        description=st.one_of(st.none(), safe_text),
        view=view_st,
        status=item_status_st,
        metadata=metadata_st,
    )
    @settings(max_examples=100)
    def test_item_create_roundtrip(
        self,
        title: str,
        description: str | None,
        view: str,
        status: str,
        metadata: dict[str, Any],
    ) -> None:
        """ItemCreate survives JSON serialization roundtrip."""
        original = ItemCreate(
            title=title,
            description=description,
            view=view,
            item_type=view.lower(),
            status=status,
            metadata=metadata,
        )
        json_data = original.model_dump_json()
        restored = ItemCreate.model_validate_json(json_data)
        assert original == restored

    @given(
        title=st.one_of(
            st.none(),
            st.text(min_size=1, max_size=500, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
        ),
        status=st.one_of(st.none(), item_status_st),
        metadata=st.one_of(st.none(), metadata_st),
    )
    @settings(max_examples=100)
    def test_item_update_roundtrip(
        self,
        title: str | None,
        status: str | None,
        metadata: dict[str, Any] | None,
    ) -> None:
        """ItemUpdate roundtrip preserves all optional fields."""
        original = ItemUpdate(title=title, status=status, metadata=metadata)
        json_data = original.model_dump_json()
        restored = ItemUpdate.model_validate_json(json_data)
        assert original == restored

    @given(
        title=st.text(min_size=1, max_size=500, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
        metadata=metadata_st,
    )
    @settings(max_examples=100)
    def test_item_create_model_dump_idempotent(self, title: str, metadata: dict[str, Any]) -> None:
        """model_dump called twice yields identical dicts."""
        item = ItemCreate(
            title=title,
            view="FEATURE",
            item_type="feature",
            metadata=metadata,
        )
        assert item.model_dump() == item.model_dump()


@pytest.mark.property
class TestLinkRoundtrip:
    """LinkCreate model roundtrip tests."""

    @given(
        source_item_id=uuid_st,
        target_item_id=uuid_st,
        link_type=st.sampled_from(["implements", "tests", "depends_on", "related_to"]),
        metadata=metadata_st,
    )
    @settings(max_examples=100)
    def test_link_create_roundtrip(
        self,
        source_item_id: str,
        target_item_id: str,
        link_type: str,
        metadata: dict[str, Any],
    ) -> None:
        """LinkCreate survives JSON roundtrip."""
        original = LinkCreate(
            source_item_id=source_item_id,
            target_item_id=target_item_id,
            link_type=link_type,
            metadata=metadata,
        )
        json_data = original.model_dump_json()
        restored = LinkCreate.model_validate_json(json_data)
        assert original == restored


@pytest.mark.property
class TestSpecificationRoundtrip:
    """Specification schema roundtrip tests."""

    @given(
        project_id=uuid_st,
        title=st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
        status=st.sampled_from(list(ADRStatus)),
        context=safe_text,
        decision=safe_text,
        consequences=safe_text,
        tags=st.lists(short_text, max_size=5),
    )
    @settings(max_examples=100)
    def test_adr_create_roundtrip(
        self,
        project_id: str,
        title: str,
        status: ADRStatus,
        context: str,
        decision: str,
        consequences: str,
        tags: list[str],
    ) -> None:
        """ADRCreate roundtrip via JSON."""
        original = ADRCreate(
            project_id=project_id,
            title=title,
            status=status,
            context=context,
            decision=decision,
            consequences=consequences,
            tags=tags,
        )
        json_data = original.model_dump_json()
        restored = ADRCreate.model_validate_json(json_data)
        assert original == restored

    @given(
        project_id=uuid_st,
        name=st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))),
        status=st.sampled_from(list(FeatureStatus)),
        tags=st.lists(short_text, max_size=5),
    )
    @settings(max_examples=100)
    def test_feature_create_roundtrip(
        self,
        project_id: str,
        name: str,
        status: FeatureStatus,
        tags: list[str],
    ) -> None:
        """FeatureCreate roundtrip via JSON."""
        original = FeatureCreate(
            project_id=project_id,
            name=name,
            status=status,
            tags=tags,
        )
        json_data = original.model_dump_json()
        restored = FeatureCreate.model_validate_json(json_data)
        assert original == restored


@pytest.mark.property
class TestNestedModelRoundtrip:
    """Roundtrip tests for models with nested sub-models."""

    @given(
        step_number=st.integers(min_value=1, max_value=1000),
        action=safe_text,
        expected_result=st.one_of(st.none(), safe_text),
    )
    @settings(max_examples=100)
    def test_test_step_roundtrip(self, step_number: int, action: str, expected_result: str | None) -> None:
        """TestStep with nested data roundtrips cleanly."""
        original = TStep(step_number=step_number, action=action, expected_result=expected_result)
        json_data = original.model_dump_json()
        restored = TStep.model_validate_json(json_data)
        assert original == restored

    @given(
        id_val=short_text,
        from_state=short_text,
        to_state=short_text,
        trigger=st.one_of(st.none(), short_text),
    )
    @settings(max_examples=100)
    def test_state_transition_roundtrip(self, id_val: str, from_state: str, to_state: str, trigger: str | None) -> None:
        """StateTransition roundtrip."""
        original = StateTransition(id=id_val, from_state=from_state, to_state=to_state, trigger=trigger)
        json_data = original.model_dump_json()
        restored = StateTransition.model_validate_json(json_data)
        assert original == restored
