"""Comprehensive unit tests for RequirementQualityRepository to achieve 85%+ coverage.

Tests for:
- create() - requirement quality spec creation
- get_by_id() - retrieval by ID
- get_by_item_id() - retrieval by item ID
- list_by_project() - listing with ordering and pagination
- list_by_quality_score() - listing by quality score range
- list_high_volatility() - listing high volatility specs
- list_high_impact() - listing high impact specs
- list_unverified() - listing unverified specs
- list_by_wsjf_priority() - listing by WSJF priority
- update() - updating spec fields
- delete() - deleting spec
- delete_by_item_id() - deleting by item ID
- get_stats() - getting aggregate statistics
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories.requirement_quality_repository import RequirementQualityRepository


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# HELPER FIXTURES
# ============================================================================


async def create_test_item(db_session: AsyncSession, project_id: str, title: str = "Test Item") -> None:
    """Helper to create a test item."""
    item_repo = ItemRepository(db_session)
    return await item_repo.create(
        project_id=project_id,
        title=title,
        view="FEATURE",
        item_type="feature",
    )


# ============================================================================
# CREATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_basic(db_session: AsyncSession) -> None:
    """Test creating requirement quality spec with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    spec = await repo.create(
        item_id=item.id,
        project_id=project.id,
    )

    assert spec.id is not None
    assert spec.item_id == item.id
    assert spec.project_id == project.id
    assert spec.overall_quality_score == 0.5
    assert spec.quality_scores == {}
    assert spec.quality_issues == []
    assert spec.is_verified is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_quality_scores(db_session: AsyncSession) -> None:
    """Test creating spec with quality scores."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    quality_scores = {
        "unambiguity": 0.8,
        "completeness": 0.7,
        "verifiability": 0.9,
    }
    spec = await repo.create(
        item_id=item.id,
        project_id=project.id,
        quality_scores=quality_scores,
        overall_quality_score=0.8,
    )

    assert spec.quality_scores == quality_scores
    assert spec.overall_quality_score == 0.8


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_impact_metrics(db_session: AsyncSession) -> None:
    """Test creating spec with impact metrics."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    spec = await repo.create(
        item_id=item.id,
        project_id=project.id,
        change_propagation_index=0.75,
        downstream_impact_count=5,
        upstream_dependency_count=3,
        impact_assessment={"risk": "high", "reason": "core component"},
    )

    assert spec.change_propagation_index == 0.75
    assert spec.downstream_impact_count == COUNT_FIVE
    assert spec.upstream_dependency_count == COUNT_THREE
    assert spec.impact_assessment["risk"] == "high"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_wsjf(db_session: AsyncSession) -> None:
    """Test creating spec with WSJF score."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    wsjf_components = {
        "business_value": 8.0,
        "time_criticality": 5.0,
        "risk_reduction": 3.0,
        "job_size": 5.0,
    }
    spec = await repo.create(
        item_id=item.id,
        project_id=project.id,
        wsjf_score=3.2,
        wsjf_components=wsjf_components,
    )

    assert spec.wsjf_score == float(COUNT_THREE + 0.2)
    assert spec.wsjf_components == wsjf_components


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_verified(db_session: AsyncSession) -> None:
    """Test creating verified spec."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    spec = await repo.create(
        item_id=item.id,
        project_id=project.id,
        is_verified=True,
    )

    assert spec.is_verified is True


# ============================================================================
# GET_BY_ID OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_existing(db_session: AsyncSession) -> None:
    """Test get_by_id returns spec when it exists."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    created = await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_nonexistent(db_session: AsyncSession) -> None:
    """Test get_by_id returns None when spec doesn't exist."""
    repo = RequirementQualityRepository(db_session)
    found = await repo.get_by_id("nonexistent-id")
    assert found is None


# ============================================================================
# GET_BY_ITEM_ID OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_item_id_existing(db_session: AsyncSession) -> None:
    """Test get_by_item_id returns spec when it exists."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    found = await repo.get_by_item_id(item.id)
    assert found is not None
    assert found.item_id == item.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_item_id_nonexistent(db_session: AsyncSession) -> None:
    """Test get_by_item_id returns None when spec doesn't exist."""
    repo = RequirementQualityRepository(db_session)
    found = await repo.get_by_item_id("nonexistent-id")
    assert found is None


# ============================================================================
# LIST_BY_PROJECT OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_basic(db_session: AsyncSession) -> None:
    """Test listing specs by project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    for i in range(3):
        item = await create_test_item(db_session, project.id, f"Item {i}")
        await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    specs = await repo.list_by_project(project.id)
    assert len(specs) == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_pagination(db_session: AsyncSession) -> None:
    """Test listing specs with pagination."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    for i in range(10):
        item = await create_test_item(db_session, project.id, f"Item {i}")
        await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    specs = await repo.list_by_project(project.id, limit=5, offset=0)
    assert len(specs) == COUNT_FIVE

    specs = await repo.list_by_project(project.id, limit=5, offset=5)
    assert len(specs) == COUNT_FIVE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_ascending_order(db_session: AsyncSession) -> None:
    """Test listing specs with ascending order."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    for i in range(3):
        item = await create_test_item(db_session, project.id, f"Item {i}")
        await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    specs = await repo.list_by_project(project.id, descending=False)
    assert len(specs) == COUNT_THREE


# ============================================================================
# LIST_BY_QUALITY_SCORE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_quality_score(db_session: AsyncSession) -> None:
    """Test listing specs by quality score range."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    scores = [0.3, 0.5, 0.7, 0.9]
    for i, score in enumerate(scores):
        item = await create_test_item(db_session, project.id, f"Item {i}")
        await repo.create(
            item_id=item.id,
            project_id=project.id,
            overall_quality_score=score,
        )
    await db_session.commit()

    # Filter for scores between 0.4 and 0.8
    specs = await repo.list_by_quality_score(project.id, min_score=0.4, max_score=0.8)
    assert len(specs) == COUNT_TWO
    assert all(0.4 <= s.overall_quality_score <= 0.8 for s in specs)


# ============================================================================
# LIST_HIGH_VOLATILITY OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_high_volatility(db_session: AsyncSession) -> None:
    """Test listing high volatility specs."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    volatilities = [0.2, 0.4, 0.6, 0.8]
    for i, vol in enumerate(volatilities):
        item = await create_test_item(db_session, project.id, f"Item {i}")
        await repo.create(
            item_id=item.id,
            project_id=project.id,
            volatility_index=vol,
        )
    await db_session.commit()

    # List specs with volatility >= 0.5
    specs = await repo.list_high_volatility(project.id, threshold=0.5)
    assert len(specs) == COUNT_TWO
    assert all(s.volatility_index >= 0.5 for s in specs)


# ============================================================================
# LIST_HIGH_IMPACT OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_high_impact(db_session: AsyncSession) -> None:
    """Test listing high impact specs."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    cpis = [0.1, 0.3, 0.5, 0.7]
    for i, cpi in enumerate(cpis):
        item = await create_test_item(db_session, project.id, f"Item {i}")
        await repo.create(
            item_id=item.id,
            project_id=project.id,
            change_propagation_index=cpi,
        )
    await db_session.commit()

    # List specs with CPI >= 0.3
    specs = await repo.list_high_impact(project.id, threshold=0.3)
    assert len(specs) == COUNT_THREE
    assert all(s.change_propagation_index >= 0.3 for s in specs)


# ============================================================================
# LIST_UNVERIFIED OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_unverified(db_session: AsyncSession) -> None:
    """Test listing unverified specs."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    for i in range(4):
        item = await create_test_item(db_session, project.id, f"Item {i}")
        await repo.create(
            item_id=item.id,
            project_id=project.id,
            is_verified=(i % 2 == 0),  # Even items are verified
        )
    await db_session.commit()

    specs = await repo.list_unverified(project.id)
    assert len(specs) == COUNT_TWO
    assert all(not s.is_verified for s in specs)


# ============================================================================
# LIST_BY_WSJF_PRIORITY OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_wsjf_priority(db_session: AsyncSession) -> None:
    """Test listing specs by WSJF priority."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    wsjf_scores = [3.0, 5.0, 2.0, None, 4.0]  # One without WSJF
    for i, score in enumerate(wsjf_scores):
        item = await create_test_item(db_session, project.id, f"Item {i}")
        await repo.create(
            item_id=item.id,
            project_id=project.id,
            wsjf_score=score,
        )
    await db_session.commit()

    specs = await repo.list_by_wsjf_priority(project.id)
    # Should only return specs with WSJF scores
    assert len(specs) == COUNT_FOUR
    # Should be ordered by WSJF score descending
    scores = [s.wsjf_score for s in specs]
    assert scores == sorted(scores, reverse=True)


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_quality_scores(db_session: AsyncSession) -> None:
    """Test updating quality scores."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    spec = await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    new_scores = {"unambiguity": 0.9, "completeness": 0.85}
    updated = await repo.update(
        spec.id,
        quality_scores=new_scores,
        overall_quality_score=0.875,
    )

    assert updated.quality_scores == new_scores
    assert updated.overall_quality_score == 0.875
    assert updated.version == COUNT_TWO  # Version should increment


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_verification(db_session: AsyncSession) -> None:
    """Test updating verification status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    spec = await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    now = datetime.now(UTC)
    updated = await repo.update(
        spec.id,
        is_verified=True,
        verified_by="test-user",
        verified_at=now,
        verification_evidence=[{"type": "test", "result": "passed"}],
    )

    assert updated.is_verified is True
    assert updated.verified_by == "test-user"
    assert updated.verification_evidence == [{"type": "test", "result": "passed"}]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_nonexistent_raises_error(db_session: AsyncSession) -> None:
    """Test updating nonexistent spec raises ValueError."""
    repo = RequirementQualityRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.update("nonexistent-id", overall_quality_score=0.9)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_all_fields(db_session: AsyncSession) -> None:
    """Test updating all available fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    spec = await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    now = datetime.now(UTC)
    updated = await repo.update(
        spec.id,
        quality_scores={"test": 0.9},
        overall_quality_score=0.9,
        quality_issues=[{"issue": "test"}],
        change_propagation_index=0.8,
        downstream_impact_count=10,
        upstream_dependency_count=5,
        impact_assessment={"risk": "high"},
        change_count=3,
        volatility_index=0.6,
        change_history=[{"change": "test"}],
        last_changed_at=now,
        wsjf_score=4.5,
        wsjf_components={"value": 5.0},
        is_verified=True,
        verified_by="user",
        verified_at=now,
        verification_evidence=[{"evidence": "test"}],
        last_analyzed_at=now,
    )

    assert updated.quality_scores == {"test": 0.9}
    assert updated.change_propagation_index == 0.8
    assert updated.volatility_index == 0.6
    assert updated.wsjf_score == float(COUNT_FOUR + 0.5)


# ============================================================================
# DELETE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_success(db_session: AsyncSession) -> None:
    """Test deleting spec."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    spec = await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    result = await repo.delete(spec.id)
    assert result is True
    await db_session.commit()

    found = await repo.get_by_id(spec.id)
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_nonexistent(db_session: AsyncSession) -> None:
    """Test deleting nonexistent spec returns False."""
    repo = RequirementQualityRepository(db_session)
    result = await repo.delete("nonexistent-id")
    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_by_item_id_success(db_session: AsyncSession) -> None:
    """Test deleting spec by item ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    item = await create_test_item(db_session, project.id)
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    await repo.create(item_id=item.id, project_id=project.id)
    await db_session.commit()

    result = await repo.delete_by_item_id(item.id)
    assert result is True
    await db_session.commit()

    found = await repo.get_by_item_id(item.id)
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_by_item_id_nonexistent(db_session: AsyncSession) -> None:
    """Test deleting by nonexistent item ID returns False."""
    repo = RequirementQualityRepository(db_session)
    result = await repo.delete_by_item_id("nonexistent-id")
    assert result is False


# ============================================================================
# GET_STATS OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_stats(db_session: AsyncSession) -> None:
    """Test getting aggregate statistics."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    # Create specs with various scores
    for i in range(4):
        item = await create_test_item(db_session, project.id, f"Item {i}")
        await repo.create(
            item_id=item.id,
            project_id=project.id,
            overall_quality_score=0.5 + (i * 0.1),
            volatility_index=0.1 * i,
            change_propagation_index=0.2 * i,
            is_verified=(i >= COUNT_TWO),  # Last 2 are verified
        )
    await db_session.commit()

    stats = await repo.get_stats(project.id)

    assert stats["total_specs"] == COUNT_FOUR
    assert "average_quality_score" in stats
    assert "average_volatility" in stats
    assert "average_impact_index" in stats
    assert stats["verified_count"] == COUNT_TWO
    assert stats["verification_rate"] == 0.5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_stats_empty_project(db_session: AsyncSession) -> None:
    """Test getting stats for empty project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RequirementQualityRepository(db_session)
    stats = await repo.get_stats(project.id)

    assert stats["total_specs"] == 0
    assert stats["verification_rate"] == 0
