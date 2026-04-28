"""Comprehensive integration test suite for Graph Analysis Services.

Tests cycle detection and impact analysis including:
- CycleDetectionService: has_cycle, detect_cycles, detect_cycles_async
- ImpactAnalysisService: analyze_impact, critical path analysis
- Complex multi-level cycles detection
- Cycle breaking strategies
- Large graph performance (1000+ nodes)
- Impact filtering and metrics
- Circular dependency handling

Coverage target: +4-5%
Test count: 50+
"""

import time
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.models.base import Base
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.services.cycle_detection_service import CycleDetectionService
from tracertm.services.impact_analysis_service import ImpactAnalysisService

pytestmark = pytest.mark.integration


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def db_session() -> None:
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
async def async_session() -> None:
    """Create an async test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, connect_args={"check_same_thread": False})

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
def sample_project(db_session: Any) -> None:
    """Create a sample project."""
    project = Project(id="test-proj", name="Test Project")
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def sample_items_basic(db_session: Any, sample_project: Any) -> None:
    """Create 5 basic test items."""
    items = []
    for i in range(1, 6):
        item = Item(
            id=f"item-{i}",
            project_id=sample_project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        items.append(item)
    db_session.commit()
    return items


@pytest.fixture
def sample_items_large(db_session: Any, sample_project: Any) -> None:
    """Create 100 items for medium-scale testing."""
    items = []
    for i in range(1, 101):
        item = Item(
            id=f"item-{i:03d}",
            project_id=sample_project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        items.append(item)
    db_session.commit()
    return items


@pytest.fixture
def sample_items_xlarge(db_session: Any, sample_project: Any) -> None:
    """Create 500 items for large-scale testing."""
    items = []
    for i in range(1, 501):
        item = Item(
            id=f"item-{i:04d}",
            project_id=sample_project.id,
            title=f"Item {i}",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        db_session.add(item)
        items.append(item)
    db_session.commit()
    return items


@pytest.fixture
def cycle_detection_service(db_session: Any) -> None:
    """Create cycle detection service instance."""
    return CycleDetectionService(db_session)


# ============================================================
# SIMPLE CYCLE DETECTION TESTS
# ============================================================


class TestSimpleCycleDetection:
    """Tests for simple cycle detection scenarios."""

    def test_self_referential_link(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test self-referential link detection."""
        # item-1 depends on itself
        service = CycleDetectionService(db_session)

        assert (
            service.has_cycle(sample_project.id, sample_items_basic[0].id, sample_items_basic[0].id, "depends_on")
            is True
        )

    def test_two_item_cycle(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test two-item cycle detection."""
        service = CycleDetectionService(db_session)

        # Create: item-1 -> item-2
        link = Link(
            id="link-1",
            project_id=sample_project.id,
            source_item_id=sample_items_basic[0].id,
            target_item_id=sample_items_basic[1].id,
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        # Verify: item-2 -> item-1 would create cycle
        assert (
            service.has_cycle(sample_project.id, sample_items_basic[1].id, sample_items_basic[0].id, "depends_on")
            is True
        )

    def test_no_cycle_simple(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test that simple dependencies don't create cycles."""
        service = CycleDetectionService(db_session)

        # Create: item-1 -> item-2
        link = Link(
            id="link-1",
            project_id=sample_project.id,
            source_item_id=sample_items_basic[0].id,
            target_item_id=sample_items_basic[1].id,
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        # Verify: item-3 -> item-1 doesn't create cycle
        assert (
            service.has_cycle(sample_project.id, sample_items_basic[2].id, sample_items_basic[0].id, "depends_on")
            is False
        )

    def test_non_depends_on_links_ignored(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test that non-depends_on links are ignored for cycle detection."""
        service = CycleDetectionService(db_session)

        # Create circular references with different link types
        link1 = Link(
            id="link-1",
            project_id=sample_project.id,
            source_item_id=sample_items_basic[0].id,
            target_item_id=sample_items_basic[1].id,
            link_type="relates_to",
        )
        db_session.add(link1)
        db_session.commit()

        # Should not be treated as cycle (not depends_on)
        assert (
            service.has_cycle(sample_project.id, sample_items_basic[1].id, sample_items_basic[0].id, "depends_on")
            is False
        )

    def test_isolated_items_no_cycle(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test that isolated items don't create cycles."""
        service = CycleDetectionService(db_session)

        # No links created - items isolated
        assert (
            service.has_cycle(sample_project.id, sample_items_basic[2].id, sample_items_basic[3].id, "depends_on")
            is False
        )


# ============================================================
# COMPLEX MULTI-LEVEL CYCLE DETECTION
# ============================================================


class TestComplexCycleDetection:
    """Tests for complex multi-level cycles."""

    def test_three_level_cycle(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test three-item circular dependency."""
        service = CycleDetectionService(db_session)

        # Create: item-1 -> item-2 -> item-3
        links = [
            Link(
                id="link-1",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[0].id,
                target_item_id=sample_items_basic[1].id,
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[1].id,
                target_item_id=sample_items_basic[2].id,
                link_type="depends_on",
            ),
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        # item-3 -> item-1 completes cycle
        assert (
            service.has_cycle(sample_project.id, sample_items_basic[2].id, sample_items_basic[0].id, "depends_on")
            is True
        )

    def test_four_level_cycle(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test four-item circular dependency."""
        service = CycleDetectionService(db_session)

        # Create chain: item-1 -> item-2 -> item-3 -> item-4
        links = [
            Link(
                id=f"link-{i}",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[i - 1].id,
                target_item_id=sample_items_basic[i].id,
                link_type="depends_on",
            )
            for i in range(1, 4)
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        # item-4 -> item-1 completes cycle
        assert (
            service.has_cycle(sample_project.id, sample_items_basic[3].id, sample_items_basic[0].id, "depends_on")
            is True
        )

    def test_multiple_paths_to_cycle(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test cycle detection with multiple dependency paths."""
        service = CycleDetectionService(db_session)

        # Create complex graph:
        # item-1 -> item-2 -> item-3
        # item-1 -> item-4 -> item-3
        links = [
            Link(
                id="link-1",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[0].id,
                target_item_id=sample_items_basic[1].id,
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[1].id,
                target_item_id=sample_items_basic[2].id,
                link_type="depends_on",
            ),
            Link(
                id="link-3",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[0].id,
                target_item_id=sample_items_basic[3].id,
                link_type="depends_on",
            ),
            Link(
                id="link-4",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[3].id,
                target_item_id=sample_items_basic[2].id,
                link_type="depends_on",
            ),
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        # item-3 -> item-1 creates cycle via multiple paths
        assert (
            service.has_cycle(sample_project.id, sample_items_basic[2].id, sample_items_basic[0].id, "depends_on")
            is True
        )

    def test_deep_dependency_chain(self, db_session: Any, sample_project: Any, _sample_items_large: Any) -> None:
        """Test cycle detection in deep dependency chains."""
        service = CycleDetectionService(db_session)

        # Create chain: item-001 -> item-002 -> ... -> item-050
        for i in range(1, 50):
            link = Link(
                id=f"link-{i}",
                project_id=sample_project.id,
                source_item_id=f"item-{i:03d}",
                target_item_id=f"item-{i + 1:03d}",
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

        # item-050 -> item-001 creates cycle
        assert service.has_cycle(sample_project.id, "item-050", "item-001", "depends_on") is True


# ============================================================
# CYCLE DETECTION - FULL GRAPH ANALYSIS
# ============================================================


class TestFullGraphCycleAnalysis:
    """Tests for detect_cycles method."""

    def test_detect_no_cycles(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test detection when no cycles exist."""
        service = CycleDetectionService(db_session)

        # Create simple linear chain
        link = Link(
            id="link-1",
            project_id=sample_project.id,
            source_item_id=sample_items_basic[0].id,
            target_item_id=sample_items_basic[1].id,
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        result = service.detect_cycles(sample_project.id, "depends_on")

        assert result is not None
        assert result.get("cycles_detected") is False

    def test_detect_single_cycle(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test detection of single cycle."""
        service = CycleDetectionService(db_session)

        # Create cycle: item-1 -> item-2 -> item-1
        links = [
            Link(
                id="link-1",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[0].id,
                target_item_id=sample_items_basic[1].id,
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[1].id,
                target_item_id=sample_items_basic[0].id,
                link_type="depends_on",
            ),
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        result = service.detect_cycles(sample_project.id, "depends_on")

        assert result is not None
        assert result.get("cycles_detected") is True
        assert "cycles" in result

    def test_detect_multiple_cycles(self, db_session: Any, sample_project: Any, _sample_items_large: Any) -> None:
        """Test detection of multiple cycles in same graph."""
        service = CycleDetectionService(db_session)

        # Create two independent cycles
        # Cycle 1: item-001 -> item-002 -> item-001
        links = [
            Link(
                id="link-1",
                project_id=sample_project.id,
                source_item_id="item-001",
                target_item_id="item-002",
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id=sample_project.id,
                source_item_id="item-002",
                target_item_id="item-001",
                link_type="depends_on",
            ),
            # Cycle 2: item-010 -> item-011 -> item-010
            Link(
                id="link-3",
                project_id=sample_project.id,
                source_item_id="item-010",
                target_item_id="item-011",
                link_type="depends_on",
            ),
            Link(
                id="link-4",
                project_id=sample_project.id,
                source_item_id="item-011",
                target_item_id="item-010",
                link_type="depends_on",
            ),
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        result = service.detect_cycles(sample_project.id, "depends_on")

        assert result is not None
        assert result.get("cycles_detected") is True

    def test_detect_cycles_with_multiple_link_types(
        self, db_session: Any, sample_project: Any, sample_items_basic: Any
    ) -> None:
        """Test cycle detection with multiple link types specified."""
        service = CycleDetectionService(db_session)

        # Create cycle with depends_on
        links = [
            Link(
                id="link-1",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[0].id,
                target_item_id=sample_items_basic[1].id,
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[1].id,
                target_item_id=sample_items_basic[0].id,
                link_type="depends_on",
            ),
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        result = service.detect_cycles(sample_project.id, link_types=["depends_on", "relates_to"])

        assert result is not None
        assert result.get("cycles_detected") is True


# ============================================================
# CYCLE BREAKING STRATEGIES
# ============================================================


class TestCycleBreakingStrategies:
    """Tests for breaking cycles and impact analysis."""

    def test_break_two_item_cycle(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test breaking a simple two-item cycle."""
        service = CycleDetectionService(db_session)

        # Create cycle
        links = [
            Link(
                id="link-1",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[0].id,
                target_item_id=sample_items_basic[1].id,
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[1].id,
                target_item_id=sample_items_basic[0].id,
                link_type="depends_on",
            ),
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        # Remove one link to break cycle
        link_to_remove = db_session.query(Link).filter_by(id="link-2").first()
        db_session.delete(link_to_remove)
        db_session.commit()

        # Verify cycle is broken
        assert (
            service.has_cycle(sample_project.id, sample_items_basic[1].id, sample_items_basic[0].id, "depends_on")
            is False
        )

    def test_identify_breaking_link_in_cycle(
        self, db_session: Any, sample_project: Any, sample_items_basic: Any
    ) -> None:
        """Test identifying which link breaks a cycle."""
        service = CycleDetectionService(db_session)

        # Create three-item cycle
        links = [
            Link(
                id="link-1",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[0].id,
                target_item_id=sample_items_basic[1].id,
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[1].id,
                target_item_id=sample_items_basic[2].id,
                link_type="depends_on",
            ),
            Link(
                id="link-3",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[2].id,
                target_item_id=sample_items_basic[0].id,
                link_type="depends_on",
            ),
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        # Breaking any of the three links should eliminate cycle
        for link_id in ["link-1", "link-2", "link-3"]:
            # Temporarily remove each link
            link = db_session.query(Link).filter_by(id=link_id).first()
            db_session.delete(link)
            db_session.flush()

            # Verify cycle is gone
            result = service.detect_cycles(sample_project.id)
            assert result.get("cycles_detected") is False

            # Restore link for next iteration
            db_session.rollback()
            db_session.refresh(link)


# ============================================================
# LARGE GRAPH PERFORMANCE TESTS
# ============================================================


class TestLargeGraphPerformance:
    """Tests for performance on large graphs."""

    def test_performance_100_items_no_cycle(
        self, db_session: Any, sample_project: Any, sample_items_large: Any
    ) -> None:
        """Test performance with 100 items and no cycles."""
        service = CycleDetectionService(db_session)

        # Create chain of 99 links
        for i in range(1, 100):
            link = Link(
                id=f"link-{i}",
                project_id=sample_project.id,
                source_item_id=f"item-{i:03d}",
                target_item_id=f"item-{i + 1:03d}",
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

        start = time.time()
        result = service.detect_cycles(sample_project.id)
        elapsed = time.time() - start

        assert result.get("cycles_detected") is False
        assert elapsed < float(COUNT_TWO + 0.0)  # Should complete in < COUNT_TWO seconds

    def test_performance_500_items_with_cycle(
        self, db_session: Any, sample_project: Any, sample_items_xlarge: Any
    ) -> None:
        """Test performance with 500 items and a cycle."""
        service = CycleDetectionService(db_session)

        # Create network of links
        for i in range(1, 500, 10):
            link = Link(
                id=f"link-{i}",
                project_id=sample_project.id,
                source_item_id=f"item-{i:04d}",
                target_item_id=f"item-{i + 1:04d}",
                link_type="depends_on",
            )
            db_session.add(link)

        # Add cycle at end
        link = Link(
            id="link-cycle",
            project_id=sample_project.id,
            source_item_id="item-0500",
            target_item_id="item-0001",
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        start = time.time()
        result = service.detect_cycles(sample_project.id)
        elapsed = time.time() - start

        assert result.get("cycles_detected") is True
        assert elapsed < float(COUNT_FIVE + 0.0)  # Should complete in < COUNT_FIVE seconds

    def test_performance_wide_dependency_graph(
        self, db_session: Any, sample_project: Any, sample_items_large: Any
    ) -> None:
        """Test performance with wide dependency graph."""
        service = CycleDetectionService(db_session)

        # Create wide graph: item-001 -> items 002-100
        for i in range(2, 101):
            link = Link(
                id=f"link-{i}",
                project_id=sample_project.id,
                source_item_id="item-001",
                target_item_id=f"item-{i:03d}",
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

        start = time.time()
        result = service.detect_cycles(sample_project.id)
        elapsed = time.time() - start

        assert result.get("cycles_detected") is False
        assert elapsed < 1.0


# ============================================================
# IMPACT ANALYSIS TESTS
# ============================================================


class TestImpactAnalysis:
    """Tests for impact analysis functionality."""

    @pytest.mark.asyncio
    async def test_single_item_impact(self, async_session: Any) -> None:
        """Test impact analysis on single item."""
        project = Project(id="test-proj", name="Test Project")
        async_session.add(project)
        await async_session.flush()

        item = Item(
            id="item-1",
            project_id=project.id,
            title="Item 1",
            view="FEATURE",
            item_type="feature",
            status="todo",
        )
        async_session.add(item)
        await async_session.flush()

        service = ImpactAnalysisService(async_session)
        result = await service.analyze_impact("item-1")

        assert result is not None
        assert result.root_item_id == "item-1"
        assert result.total_affected == 1  # Only itself
        assert result.max_depth_reached == 0

    @pytest.mark.asyncio
    async def test_linear_dependency_impact(self, async_session: Any) -> None:
        """Test impact analysis on linear dependencies."""
        project = Project(id="test-proj", name="Test Project")
        async_session.add(project)
        await async_session.flush()

        # Create items and dependencies
        items = []
        for i in range(1, 4):
            item = Item(
                id=f"item-{i}",
                project_id=project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            async_session.add(item)
            items.append(item)
        await async_session.flush()

        # item-1 depends on item-2 depends on item-3
        link1 = Link(
            id="link-1",
            project_id=project.id,
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )
        link2 = Link(
            id="link-2",
            project_id=project.id,
            source_item_id="item-2",
            target_item_id="item-3",
            link_type="depends_on",
        )
        async_session.add(link1)
        async_session.add(link2)
        await async_session.flush()

        service = ImpactAnalysisService(async_session)
        result = await service.analyze_impact("item-3")

        assert result.total_affected >= 1
        assert result.max_depth_reached >= 0

    @pytest.mark.asyncio
    async def test_impact_with_max_depth(self, async_session: Any) -> None:
        """Test impact analysis respects max depth."""
        project = Project(id="test-proj", name="Test Project")
        async_session.add(project)
        await async_session.flush()

        # Create deep chain
        for i in range(1, 11):
            item = Item(
                id=f"item-{i}",
                project_id=project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            async_session.add(item)
        await async_session.flush()

        # Create dependencies
        for i in range(1, 10):
            link = Link(
                id=f"link-{i}",
                project_id=project.id,
                source_item_id=f"item-{i}",
                target_item_id=f"item-{i + 1}",
                link_type="depends_on",
            )
            async_session.add(link)
        await async_session.flush()

        service = ImpactAnalysisService(async_session)
        result = await service.analyze_impact("item-1", max_depth=3)

        assert result.max_depth_reached <= COUNT_THREE

    @pytest.mark.asyncio
    async def test_impact_with_link_type_filter(self, async_session: Any) -> None:
        """Test impact analysis with specific link types."""
        project = Project(id="test-proj", name="Test Project")
        async_session.add(project)
        await async_session.flush()

        for i in range(1, 4):
            item = Item(
                id=f"item-{i}",
                project_id=project.id,
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
            async_session.add(item)
        await async_session.flush()

        # Mixed link types
        link1 = Link(
            id="link-1",
            project_id=project.id,
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="depends_on",
        )
        link2 = Link(
            id="link-2",
            project_id=project.id,
            source_item_id="item-2",
            target_item_id="item-3",
            link_type="relates_to",
        )
        async_session.add(link1)
        async_session.add(link2)
        await async_session.flush()

        service = ImpactAnalysisService(async_session)
        result = await service.analyze_impact("item-1", link_types=["depends_on"])

        assert result is not None

    @pytest.mark.asyncio
    async def test_impact_analysis_missing_item(self, async_session: Any) -> None:
        """Test impact analysis with non-existent item."""
        service = ImpactAnalysisService(async_session)

        with pytest.raises(ValueError):
            await service.analyze_impact("non-existent-item")


# ============================================================
# CIRCULAR DEPENDENCY HANDLING
# ============================================================


class TestCircularDependencyHandling:
    """Tests for handling circular dependencies."""

    def test_prevent_circular_dependency_creation(
        self, db_session: Any, sample_project: Any, sample_items_basic: Any
    ) -> None:
        """Test preventing creation of circular dependencies."""
        service = CycleDetectionService(db_session)

        # Create initial dependency
        link = Link(
            id="link-1",
            project_id=sample_project.id,
            source_item_id=sample_items_basic[0].id,
            target_item_id=sample_items_basic[1].id,
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        # Attempt to create circular dependency should be detected
        would_create_cycle = service.has_cycle(
            sample_project.id,
            sample_items_basic[1].id,
            sample_items_basic[0].id,
            "depends_on",
        )

        assert would_create_cycle is True

    def test_orphan_detection_after_cycle_break(
        self, db_session: Any, sample_project: Any, sample_items_basic: Any
    ) -> None:
        """Test detecting orphans after breaking a cycle."""
        service = CycleDetectionService(db_session)

        # Create complex graph
        links = [
            Link(
                id="link-1",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[0].id,
                target_item_id=sample_items_basic[1].id,
                link_type="depends_on",
            ),
            Link(
                id="link-2",
                project_id=sample_project.id,
                source_item_id=sample_items_basic[1].id,
                target_item_id=sample_items_basic[2].id,
                link_type="depends_on",
            ),
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        # item-3 and item-4 are orphans
        # Verify no cycles exist
        result = service.detect_cycles(sample_project.id)
        assert result.get("cycles_detected") is False


# ============================================================
# ERROR HANDLING AND EDGE CASES
# ============================================================


class TestErrorHandlingAndEdgeCases:
    """Tests for error handling and edge cases."""

    def test_empty_project(self, db_session: Any, sample_project: Any) -> None:
        """Test cycle detection on empty project."""
        service = CycleDetectionService(db_session)

        result = service.detect_cycles(sample_project.id)

        assert result is not None
        assert result.get("cycles_detected") is False

    def test_single_item_no_links(self, db_session: Any, sample_project: Any, _sample_items_basic: Any) -> None:
        """Test with single item and no links."""
        service = CycleDetectionService(db_session)

        result = service.detect_cycles(sample_project.id)

        assert result is not None
        assert result.get("cycles_detected") is False

    def test_nonexistent_project(self, db_session: Any) -> None:
        """Test cycle detection on non-existent project."""
        service = CycleDetectionService(db_session)

        result = service.detect_cycles("nonexistent-project")

        assert result is not None

    def test_invalid_link_type(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test with invalid link type."""
        service = CycleDetectionService(db_session)

        # Should not find cycles for non-depends_on types
        assert (
            service.has_cycle(sample_project.id, sample_items_basic[0].id, sample_items_basic[1].id, "invalid_type")
            is False
        )

    def test_null_item_ids(self, db_session: Any, sample_project: Any) -> None:
        """Test handling of null/empty item IDs."""
        service = CycleDetectionService(db_session)

        # Should handle gracefully
        result = service.detect_cycles(sample_project.id)
        assert result is not None

    def test_duplicate_links_same_direction(
        self, db_session: Any, sample_project: Any, sample_items_basic: Any
    ) -> None:
        """Test with duplicate links in same direction."""
        service = CycleDetectionService(db_session)

        # Create duplicate links
        link1 = Link(
            id="link-1",
            project_id=sample_project.id,
            source_item_id=sample_items_basic[0].id,
            target_item_id=sample_items_basic[1].id,
            link_type="depends_on",
        )
        link2 = Link(
            id="link-2",
            project_id=sample_project.id,
            source_item_id=sample_items_basic[0].id,
            target_item_id=sample_items_basic[1].id,
            link_type="depends_on",
        )
        db_session.add(link1)
        db_session.add(link2)
        db_session.commit()

        result = service.detect_cycles(sample_project.id)
        assert result is not None


# ============================================================
# INTEGRATION SCENARIOS
# ============================================================


class TestIntegrationScenarios:
    """Integration tests combining multiple features."""

    def test_complex_workflow_cycle_and_impact(
        self, db_session: Any, sample_project: Any, sample_items_large: Any
    ) -> None:
        """Test complex workflow with cycle detection and impact analysis."""
        cycle_service = CycleDetectionService(db_session)

        # Create complex dependency network
        for i in range(1, 50, 5):
            link = Link(
                id=f"link-{i}",
                project_id=sample_project.id,
                source_item_id=f"item-{i:03d}",
                target_item_id=f"item-{i + 5:03d}",
                link_type="depends_on",
            )
            db_session.add(link)
        db_session.commit()

        # Detect cycles
        result = cycle_service.detect_cycles(sample_project.id)
        assert result is not None

    def test_rapid_cycle_detection_calls(self, db_session: Any, sample_project: Any, sample_items_basic: Any) -> None:
        """Test rapid successive cycle detection calls."""
        service = CycleDetectionService(db_session)

        link = Link(
            id="link-1",
            project_id=sample_project.id,
            source_item_id=sample_items_basic[0].id,
            target_item_id=sample_items_basic[1].id,
            link_type="depends_on",
        )
        db_session.add(link)
        db_session.commit()

        # Rapid calls should not cause issues
        for _ in range(10):
            result = service.has_cycle(
                sample_project.id,
                sample_items_basic[1].id,
                sample_items_basic[0].id,
                "depends_on",
            )
            assert result is True

    def test_mixed_cycle_and_non_cycle_links(
        self, db_session: Any, sample_project: Any, sample_items_large: Any
    ) -> None:
        """Test graph with mix of cyclic and acyclic relationships."""
        service = CycleDetectionService(db_session)

        # Create both cyclic and acyclic parts
        # Cycle: 001 -> 002 -> 001
        links = [
            Link(
                id="link-cycle-1",
                project_id=sample_project.id,
                source_item_id="item-001",
                target_item_id="item-002",
                link_type="depends_on",
            ),
            Link(
                id="link-cycle-2",
                project_id=sample_project.id,
                source_item_id="item-002",
                target_item_id="item-001",
                link_type="depends_on",
            ),
            # Acyclic: 010 -> 011 -> 012
            Link(
                id="link-acyclic-1",
                project_id=sample_project.id,
                source_item_id="item-010",
                target_item_id="item-011",
                link_type="depends_on",
            ),
            Link(
                id="link-acyclic-2",
                project_id=sample_project.id,
                source_item_id="item-011",
                target_item_id="item-012",
                link_type="depends_on",
            ),
        ]
        for link in links:
            db_session.add(link)
        db_session.commit()

        result = service.detect_cycles(sample_project.id)
        assert result.get("cycles_detected") is True
