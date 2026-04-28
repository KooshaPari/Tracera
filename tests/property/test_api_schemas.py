"""Property-based tests for API schema invariants.

Validates that API response schemas preserve information, that list wrappers
maintain totals, and that enum-constrained fields reject out-of-band values.
"""

from datetime import UTC, datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from tracertm.schemas.item import ItemCreate, ItemResponse
from tracertm.schemas.problem import ImpactLevel
from tracertm.schemas.specification import (
    ADRCreate,
    ADRListResponse,
    ADRStatus,
    ContractType,
    FeatureCreate,
    FeatureListResponse,
    FeatureStatus,
    RequirementQualityRead,
)
from tracertm.schemas.test_case import (
    TestCaseCreate as TCCreate,
)
from tracertm.schemas.test_case import (
    TestCaseListResponse as TCListResponse,
)
from tracertm.schemas.test_case import (
    TestCasePriority as TCPriority,
)
from tracertm.schemas.test_case import (
    TestCaseType as TCType,
)

# ---------------------------------------------------------------------------
# Shared strategies
# ---------------------------------------------------------------------------

safe_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Z")),
    min_size=1,
    max_size=100,
)

uuid_st = st.uuids().map(str)

now = datetime.now(tz=UTC)
now_str = now.isoformat()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.property
class TestEnumCoverage:
    """All enum values are accepted; non-members are rejected."""

    @given(status=st.sampled_from(list(ADRStatus)))
    @settings(max_examples=20)
    def test_adr_status_all_variants_valid(self, status: ADRStatus) -> None:
        """Every ADRStatus enum member creates a valid ADRCreate."""
        adr = ADRCreate(
            project_id="abc",
            title="test",
            status=status,
            context="ctx",
            decision="dec",
            consequences="cons",
        )
        assert adr.status == status

    @given(status=st.text(min_size=1, max_size=30).filter(lambda s: s not in [e.value for e in ADRStatus]))
    @settings(max_examples=50)
    def test_adr_status_rejects_non_members(self, status: str) -> None:
        """Arbitrary strings not in ADRStatus are rejected."""
        with pytest.raises(ValidationError):
            ADRCreate(
                project_id="abc",
                title="test",
                status=status,
                context="ctx",
                decision="dec",
                consequences="cons",
            )

    @given(status=st.sampled_from(list(FeatureStatus)))
    @settings(max_examples=20)
    def test_feature_status_all_variants_valid(self, status: FeatureStatus) -> None:
        """Every FeatureStatus enum member is accepted."""
        feature = FeatureCreate(project_id="p1", name="f1", status=status)
        assert feature.status == status

    @given(tc_type=st.sampled_from(list(TCType)))
    @settings(max_examples=20)
    def test_test_case_type_all_variants_valid(self, tc_type: TCType) -> None:
        """Every TestCaseType variant is accepted."""
        tc = TCCreate(title="test", test_type=tc_type)
        assert tc.test_type == tc_type

    @given(priority=st.sampled_from(list(TCPriority)))
    @settings(max_examples=20)
    def test_test_case_priority_all_variants(self, priority: TCPriority) -> None:
        """Every TestCasePriority variant is accepted."""
        tc = TCCreate(title="test", priority=priority)
        assert tc.priority == priority

    @given(ct=st.sampled_from(list(ContractType)))
    @settings(max_examples=20)
    def test_contract_type_all_variants(self, ct: ContractType) -> None:
        """Every ContractType variant is valid."""
        assert ct.value in [e.value for e in ContractType]

    @given(il=st.sampled_from(list(ImpactLevel)))
    @settings(max_examples=10)
    def test_impact_level_all_variants(self, il: ImpactLevel) -> None:
        """Every ImpactLevel variant is valid."""
        assert il.value in [e.value for e in ImpactLevel]


@pytest.mark.property
class TestRequirementQualityScores:
    """RequirementQualityRead score fields are bounded [0, 1]."""

    @given(
        ambiguity=st.floats(min_value=0.0, max_value=1.0),
        completeness=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100)
    def test_valid_scores_accepted(self, ambiguity: float, completeness: float) -> None:
        """Scores in [0, 1] are accepted."""
        rq = RequirementQualityRead(
            id="rq1",
            item_id="it1",
            smells=[],
            ambiguity_score=ambiguity,
            completeness_score=completeness,
            suggestions=[],
            last_analyzed_at=now,
            version=1,
            created_at=now,
            updated_at=now,
        )
        assert 0.0 <= rq.ambiguity_score <= 1.0
        assert 0.0 <= rq.completeness_score <= 1.0

    @given(score=st.floats(min_value=1.01, max_value=1000.0))
    @settings(max_examples=50)
    def test_ambiguity_score_over_1_rejected(self, score: float) -> None:
        """Ambiguity score > 1.0 is rejected."""
        with pytest.raises(ValidationError):
            RequirementQualityRead(
                id="rq1",
                item_id="it1",
                smells=[],
                ambiguity_score=score,
                completeness_score=0.5,
                suggestions=[],
                last_analyzed_at=now,
                version=1,
                created_at=now,
                updated_at=now,
            )

    @given(score=st.floats(max_value=-0.01, min_value=-1000.0))
    @settings(max_examples=50)
    def test_completeness_score_below_0_rejected(self, score: float) -> None:
        """Completeness score < 0.0 is rejected."""
        with pytest.raises(ValidationError):
            RequirementQualityRead(
                id="rq1",
                item_id="it1",
                smells=[],
                ambiguity_score=0.5,
                completeness_score=score,
                suggestions=[],
                last_analyzed_at=now,
                version=1,
                created_at=now,
                updated_at=now,
            )


@pytest.mark.property
class TestListResponseInvariants:
    """List response wrappers maintain structural invariants."""

    @given(total=st.integers(min_value=0, max_value=10000))
    @settings(max_examples=100)
    def test_adr_list_response_total_non_negative(self, total: int) -> None:
        """ADRListResponse always accepts non-negative totals."""
        resp = ADRListResponse(total=total, adrs=[])
        assert resp.total >= 0

    @given(total=st.integers(min_value=0, max_value=10000))
    @settings(max_examples=100)
    def test_feature_list_response_total_non_negative(self, total: int) -> None:
        """FeatureListResponse always accepts non-negative totals."""
        resp = FeatureListResponse(total=total, features=[])
        assert resp.total >= 0

    @given(total=st.integers(min_value=0, max_value=10000))
    @settings(max_examples=100)
    def test_test_case_list_response_total_non_negative(self, total: int) -> None:
        """TestCaseListResponse always accepts non-negative totals."""
        resp = TCListResponse(total=total, test_cases=[])
        assert resp.total >= 0


@pytest.mark.property
class TestItemResponseFromCreate:
    """ItemResponse can represent any data that ItemCreate produces."""

    @given(
        title=st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=("L", "N"))),
        view=st.sampled_from(["FEATURE", "CODE", "TEST"]),
        status=st.sampled_from(["todo", "done"]),
    )
    @settings(max_examples=100)
    def test_item_response_covers_item_create_fields(self, title: str, view: str, status: str) -> None:
        """Any valid ItemCreate data can be represented in ItemResponse."""
        create = ItemCreate(title=title, view=view, item_type=view.lower(), status=status)
        # Build a minimal response matching what the create payload would produce
        response = ItemResponse(
            id="00000000-0000-0000-0000-000000000001",
            project_id="00000000-0000-0000-0000-000000000002",
            title=create.title,
            description=create.description,
            view=create.view,
            item_type=create.item_type,
            status=create.status,
            parent_id=create.parent_id,
            metadata=create.metadata,
            version=1,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
        assert response.title == create.title
        assert response.view == create.view
        assert response.status == create.status
        assert response.metadata == create.metadata
