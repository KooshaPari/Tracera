"""Integration tests for item_spec_service with database.

Functional Requirements Coverage:
    - FR-QUAL-001: Requirement Quality Assessment
    - FR-QUAL-003: Dependency Analysis (via ImpactAnalyzer)
    - FR-DISC-002: Specification Parsing (partial)

Epics:
    - EPIC-002: Spec-Driven Traceability

Tests verify requirement quality analysis, impact analysis, and requirement
specification service integration with database persistence.
"""

from typing import Any

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.services.item_spec_service import (
    ImpactAnalyzer,
    RequirementQualityAnalyzer,
    RequirementSpecService,
)


@pytest.mark.asyncio
class TestRequirementSpecServiceIntegration:
    """Integration tests for RequirementSpecService."""

    @pytest.fixture
    async def setup(self, session: Any) -> None:
        """Set up test data."""
        # Create test project and items
        from tracertm.models.project import Project

        project = Project(
            id="test-proj",
            name="Test Project",
            description="Test project for specs",
        )
        session.add(project)
        await session.flush()

        # Create test items
        item1 = Item(
            id="item-1",
            project_id="test-proj",
            title="User authentication",
            description="The system shall authenticate users with username and password within 2 seconds",
            view="requirements",
            item_type="requirement",
            status="active",
            priority="high",
        )

        item2 = Item(
            id="item-2",
            project_id="test-proj",
            title="Password encryption",
            description="The system shall encrypt all passwords using bcrypt",
            view="requirements",
            item_type="requirement",
            status="active",
            priority="high",
        )

        item3 = Item(
            id="item-3",
            project_id="test-proj",
            title="Audit logging",
            description="TBD: Implement audit trail",
            view="requirements",
            item_type="requirement",
            status="todo",
            priority="medium",
        )

        session.add_all([item1, item2, item3])
        await session.flush()

        # Create links
        from tracertm.models.graph import Graph

        graph = Graph(
            id="graph-1",
            project_id="test-proj",
            graph_type="default",
        )
        session.add(graph)
        await session.flush()

        link = Link(
            id="link-1",
            project_id="test-proj",
            graph_id="graph-1",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="requires",
        )
        session.add(link)
        await session.flush()

        return {
            "project": project,
            "items": {"item1": item1, "item2": item2, "item3": item3},
            "graph": graph,
        }

    @pytest.mark.asyncio
    async def test_create_spec_with_quality_analysis(self, session: Any, _setup: Any) -> None:
        """Test creating spec with quality analysis."""
        service = RequirementSpecService(session)

        spec = await service.create_spec(item_id="item-1")

        assert spec.item_id == "item-1"
        assert spec.overall_quality_score > 0.7
        assert spec.quality_scores["unambiguity"] > 0.7
        assert "unambiguity" in spec.quality_scores

    @pytest.mark.asyncio
    async def test_refresh_quality_analysis(self, session: Any, _setup: Any) -> None:
        """Test refreshing quality analysis."""
        service = RequirementSpecService(session)

        # Create initial spec
        spec1 = await service.create_spec(item_id="item-1")
        score1 = spec1.overall_quality_score

        # Refresh analysis
        spec2 = await service.refresh_quality_analysis(item_id="item-1")

        # Scores should be recalculated
        assert spec2.overall_quality_score == score1
        assert spec2.last_analyzed_at is not None

    @pytest.mark.asyncio
    async def test_calculate_impact_with_links(self, session: Any, _setup: Any) -> None:
        """Test impact analysis with upstream/downstream links."""
        analyzer = ImpactAnalyzer(session)

        impact = await analyzer.calculate_impact(item_id="item-1", project_id="test-proj")

        assert impact["downstream_count"] == 1  # Links to item-2
        assert impact["upstream_count"] == 0  # No incoming links
        assert impact["change_propagation_index"] >= 0

    @pytest.mark.asyncio
    async def test_record_change_updates_volatility(self, session: Any, _setup: Any) -> None:
        """Test that recording changes updates volatility."""
        service = RequirementSpecService(session)

        # Create spec
        spec = await service.create_spec(item_id="item-1")
        initial_volatility = spec.volatility_index

        # Record a change
        updated = await service.record_change(
            item_id="item-1",
            changed_by="user1",
            change_type="modified",
            summary="Updated description",
            previous_values={"description": "old"},
            new_values={"description": "new"},
        )

        assert updated.change_count > spec.change_count
        assert updated.volatility_index >= initial_volatility
        assert updated.last_changed_at is not None

    @pytest.mark.asyncio
    async def test_calculate_wsjf(self, session: Any, _setup: Any) -> None:
        """Test WSJF calculation."""
        service = RequirementSpecService(session)

        # Create spec
        await service.create_spec(item_id="item-1")

        # Calculate WSJF
        updated = await service.calculate_wsjf(
            item_id="item-1",
            business_value=0.9,
            time_sensitivity=0.8,
            risk_reduction=0.7,
            job_size=0.3,
        )

        assert updated.wsjf_score is not None
        assert 0 <= updated.wsjf_score <= 1.0
        assert updated.wsjf_components["business_value"] == 0.9

    @pytest.mark.asyncio
    async def test_verify_requirement(self, session: Any, _setup: Any) -> None:
        """Test requirement verification."""
        service = RequirementSpecService(session)

        # Create spec
        spec = await service.create_spec(item_id="item-1")
        assert spec.is_verified is False

        # Verify with evidence
        verified = await service.verify_requirement(
            item_id="item-1",
            verified_by="qa-user",
            evidence_type="test",
            evidence_reference="test-123",
            description="Verified by unit tests",
        )

        assert verified.is_verified is True
        assert verified.verified_by == "qa-user"
        assert len(verified.verification_evidence) > 0

    @pytest.mark.asyncio
    async def test_get_health_report(self, session: Any, _setup: Any) -> None:
        """Test generating health report for project."""
        service = RequirementSpecService(session)

        # Create specs for items
        await service.create_spec(item_id="item-1")
        await service.create_spec(item_id="item-2")
        await service.create_spec(item_id="item-3")

        # Generate report
        report = await service.get_health_report(project_id="test-proj")

        assert report["total_requirements"] == COUNT_THREE
        assert "health_score" in report
        assert "average_quality_score" in report
        assert 0 <= report["health_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_low_quality_requirement_analysis(self, session: Any, _setup: Any) -> None:
        """Test analysis identifies quality issues."""
        service = RequirementSpecService(session)

        spec = await service.create_spec(item_id="item-3")

        # Should have low completeness due to TBD
        assert spec.overall_quality_score < 0.7
        assert spec.quality_scores["completeness"] < 0.5

        # Should have quality issues
        assert len(spec.quality_issues) > 0
        completeness_issues = [i for i in spec.quality_issues if i["dimension"] == "completeness"]
        assert len(completeness_issues) > 0

    @pytest.mark.asyncio
    async def test_refresh_impact_analysis(self, session: Any, _setup: Any) -> None:
        """Test refreshing impact analysis."""
        service = RequirementSpecService(session)

        spec = await service.create_spec(item_id="item-1")
        initial_cpi = spec.change_propagation_index

        # Refresh impact
        updated = await service.refresh_impact_analysis(item_id="item-1")

        # CPI should be the same (same dependencies)
        assert updated.change_propagation_index == initial_cpi


@pytest.mark.asyncio
class TestImpactAnalyzerIntegration:
    """Integration tests for ImpactAnalyzer."""

    @pytest.fixture
    async def setup_graph(self, session: Any) -> None:
        """Create a more complex dependency graph."""
        from tracertm.models.graph import Graph
        from tracertm.models.project import Project

        project = Project(id="test-proj", name="Test")
        session.add(project)
        await session.flush()

        graph = Graph(id="graph-1", project_id="test-proj", graph_type="default")
        session.add(graph)
        await session.flush()

        # Create chain: item1 -> item2 -> item3
        # Create parallel: item1 -> item4
        for i in range(1, 5):
            item = Item(
                id=f"item-{i}",
                project_id="test-proj",
                title=f"Item {i}",
                description=f"Test item {i}",
                view="requirements",
                item_type="requirement",
            )
            session.add(item)
        await session.flush()

        links = [
            Link(
                id="link-1",
                project_id="test-proj",
                graph_id="graph-1",
                source_item_id="item-1",
                target_item_id="item-2",
                link_type="requires",
            ),
            Link(
                id="link-2",
                project_id="test-proj",
                graph_id="graph-1",
                source_item_id="item-2",
                target_item_id="item-3",
                link_type="requires",
            ),
            Link(
                id="link-3",
                project_id="test-proj",
                graph_id="graph-1",
                source_item_id="item-1",
                target_item_id="item-4",
                link_type="requires",
            ),
        ]
        session.add_all(links)
        await session.flush()

        return {"project": project, "graph": graph}

    @pytest.mark.asyncio
    async def test_calculate_downstream_impact(self, session: Any, _setup_graph: Any) -> None:
        """Test calculation of downstream impact."""
        analyzer = ImpactAnalyzer(session)

        impact = await analyzer.calculate_impact(item_id="item-1", project_id="test-proj")

        # item-1 has direct links to item-2 and item-4
        assert impact["downstream_count"] >= COUNT_TWO

    @pytest.mark.asyncio
    async def test_calculate_indirect_downstream(self, session: Any, _setup_graph: Any) -> None:
        """Test calculation of indirect downstream impact."""
        analyzer = ImpactAnalyzer(session)

        impact = await analyzer.calculate_impact(item_id="item-1", project_id="test-proj")

        # item-1 -> item-2 -> item-3 (indirect)
        assert len(impact["indirect_downstream"]) >= 1
        assert "item-3" in impact["indirect_downstream"]


@pytest.mark.asyncio
class TestVolatilityTrackingIntegration:
    """Integration tests for volatility tracking."""

    @pytest.fixture
    async def setup(self, session: Any) -> None:
        """Set up test data."""
        from tracertm.models.project import Project

        project = Project(id="test-proj", name="Test")
        session.add(project)
        await session.flush()

        item = Item(
            id="item-1",
            project_id="test-proj",
            title="Test item",
            description="Test",
            view="requirements",
            item_type="requirement",
        )
        session.add(item)
        await session.flush()

        return project

    @pytest.mark.asyncio
    async def test_volatility_increases_with_changes(self, session: Any, _setup: Any) -> None:
        """Test volatility increases as changes accumulate."""
        service = RequirementSpecService(session)

        spec = await service.create_spec(item_id="item-1")
        initial_volatility = spec.volatility_index

        # Record multiple changes
        for i in range(5):
            spec = await service.record_change(
                item_id="item-1",
                changed_by=f"user-{i}",
                change_type="modified",
                summary=f"Change {i}",
            )

        # Volatility should increase
        assert spec.volatility_index > initial_volatility
        assert spec.change_count == COUNT_FIVE


@pytest.mark.asyncio
class TestQualityAnalyzerComplexScenarios:
    """Complex scenario tests for quality analyzer."""

    def test_technical_requirement_analysis(self) -> None:
        """Test analysis of technical requirement."""
        analyzer = RequirementQualityAnalyzer()

        text = "The API shall return responses in < 100ms for 95th percentile latency under normal load"

        result = analyzer.analyze(text)

        assert result["has_quantifiable_criteria"] is True
        assert result["scores"]["verifiability"] > 0.8

    def test_business_requirement_analysis(self) -> None:
        """Test analysis of business requirement."""
        analyzer = RequirementQualityAnalyzer()

        text = "The system shall support up to 1000 concurrent users with 99.9% uptime"

        result = analyzer.analyze(text)

        assert result["overall_score"] > 0.75
        assert len(result["issues"]) < COUNT_TWO

    def test_mixed_quality_requirement(self) -> None:
        """Test requirement with mixed quality issues."""
        analyzer = RequirementQualityAnalyzer()

        text = "The system should be efficient and provide good user experience. Might need TBD for specific metrics."

        result = analyzer.analyze(text)

        assert result["overall_score"] < 0.65
        assert len(result["issues"]) >= COUNT_THREE
        assert result["missing_criteria"] is True
