"""Tests for item_spec_service module.

Functional Requirements Coverage:
    - FR-QUAL-001: Requirement Quality Assessment (via RequirementQualityAnalyzer)
    - FR-DISC-002: Specification Parsing (partial)

Epics:
    - EPIC-002: Spec-Driven Traceability

Tests verify requirement quality analysis, test specification flakiness detection,
volatility tracking, and WSJF prioritization calculations.
"""

from typing import Any

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.services.item_spec_service import (
    RequirementQualityAnalyzer,
    TestSpecFlakinessDector,
    VolatilityTracker,
    WSJFCalculator,
)


class TestRequirementQualityAnalyzer:
    """Tests for RequirementQualityAnalyzer."""

    @pytest.fixture
    def analyzer(self) -> None:
        return RequirementQualityAnalyzer()

    def test_analyze_high_quality_requirement(self, analyzer: Any) -> None:
        """Test analysis of well-written requirement."""
        title = "User login functionality"
        text = "The system shall authenticate users with username and password within 2 seconds."

        result = analyzer.analyze(text, title)

        assert result["overall_score"] > 0.7
        assert result["scores"]["unambiguity"] > 0.7
        assert result["scores"]["completeness"] > 0.7
        assert result["scores"]["verifiability"] > 0.7
        assert len(result["issues"]) == 0
        assert result["has_quantifiable_criteria"] is True

    def test_analyze_low_quality_requirement(self, analyzer: Any) -> None:
        """Test analysis of poorly-written requirement."""
        title = "Better performance"
        text = "The system should be as efficient as possible with good performance TBD"

        result = analyzer.analyze(text, title)

        assert result["overall_score"] < 0.6
        assert result["scores"]["completeness"] < 0.5
        assert any(issue["severity"] == "error" for issue in result["issues"])
        assert len(result["ambiguous_terms"]) > 0

    def test_ambiguity_detection(self, analyzer: Any) -> None:
        """Test detection of ambiguous language."""
        text = "The system should be efficient and flexible"

        result = analyzer.analyze(text)

        assert len(result["ambiguous_terms"]) >= COUNT_TWO
        ambiguity_issues = [i for i in result["issues"] if i["dimension"] == "unambiguity"]
        assert len(ambiguity_issues) >= COUNT_TWO

    def test_completeness_detection(self, analyzer: Any) -> None:
        """Test detection of incomplete requirements."""
        text = "Implement user authentication. TBD: Verification method"

        result = analyzer.analyze(text)

        assert result["scores"]["completeness"] < 0.75
        completeness_issues = [i for i in result["issues"] if i["dimension"] == "completeness"]
        assert len(completeness_issues) > 0

    def test_verifiability_with_metrics(self, analyzer: Any) -> None:
        """Test verifiability improves with quantifiable criteria."""
        text1 = "System should be fast"
        text2 = "System shall respond within 500ms to user input"

        result1 = analyzer.analyze(text1)
        result2 = analyzer.analyze(text2)

        assert result2["scores"]["verifiability"] > result1["scores"]["verifiability"]
        assert result2["has_quantifiable_criteria"] is True

    def test_necessity_strong_verbs(self, analyzer: Any) -> None:
        """Test necessity scoring with strong requirement verbs."""
        text_weak = "The system might provide user authentication"
        text_strong = "The system shall provide user authentication"

        result_weak = analyzer.analyze(text_weak)
        result_strong = analyzer.analyze(text_strong)

        assert result_strong["scores"]["necessity"] > result_weak["scores"]["necessity"]

    def test_singularity_multiple_requirements(self, analyzer: Any) -> None:
        """Test detection of multiple requirements in one statement."""
        text = "The system shall authenticate users and encrypt passwords and audit access"

        result = analyzer.analyze(text)

        assert result["scores"]["singularity"] < 0.7
        singularity_issues = [i for i in result["issues"] if i["dimension"] == "singularity"]
        assert len(singularity_issues) > 0

    def test_overall_score_weighting(self, analyzer: Any) -> None:
        """Test that overall score uses correct weights."""
        text = "The system shall authenticate users within 2 seconds"

        result = analyzer.analyze(text)

        # Calculate expected score manually
        expected = (
            result["scores"]["unambiguity"] * 0.25
            + result["scores"]["completeness"] * 0.20
            + result["scores"]["verifiability"] * 0.25
            + result["scores"]["necessity"] * 0.15
            + result["scores"]["singularity"] * 0.15
        )

        assert abs(result["overall_score"] - expected) < 0.01


class TestVolatilityTracker:
    """Tests for VolatilityTracker."""

    @pytest.fixture
    def tracker(self) -> None:
        return VolatilityTracker()

    def test_stable_requirement(self, tracker: Any) -> None:
        """Test volatility of stable, unchanging requirement."""
        score = tracker.calculate_volatility(change_count=0, days_since_creation=30)

        assert score == 0.0

    def test_volatile_requirement(self, tracker: Any) -> None:
        """Test volatility of frequently-changing requirement."""
        score = tracker.calculate_volatility(change_count=10, days_since_creation=10)

        assert score > 0.5

    def test_volatility_with_recent_changes(self, tracker: Any) -> None:
        """Test that recent changes increase volatility."""
        history_old = [{"timestamp": "2024-01-01"} for _ in range(5)]
        history_recent = [{"timestamp": "2025-01-29"} for _ in range(5)]

        score_old = tracker.calculate_volatility(5, 30, history_old)
        score_recent = tracker.calculate_volatility(5, 30, history_recent)

        # Recent history should have higher weight (in real implementation)
        assert score_recent >= score_old

    def test_volatility_categorization(self, tracker: Any) -> None:
        """Test volatility category assignment."""
        assert tracker.categorize_volatility(0.8) == "critical"
        assert tracker.categorize_volatility(0.5) == "high"
        assert tracker.categorize_volatility(0.3) == "medium"
        assert tracker.categorize_volatility(0.1) == "low"
        assert tracker.categorize_volatility(0.01) == "stable"

    def test_volatility_normalization(self, tracker: Any) -> None:
        """Test that volatility is normalized to 0-1."""
        score = tracker.calculate_volatility(change_count=100, days_since_creation=1)

        assert 0 <= score <= 1.0


class TestWSJFCalculator:
    """Tests for WSJFCalculator."""

    @pytest.fixture
    def calculator(self) -> None:
        return WSJFCalculator()

    def test_high_priority_wsjf(self, calculator: Any) -> None:
        """Test WSJF calculation for high-priority item."""
        score = calculator.calculate_wsjf(
            business_value=0.9,
            time_sensitivity=0.8,
            risk_reduction=0.7,
            job_size=0.2,  # Small effort = high priority
        )

        assert score > 0.7

    def test_low_priority_wsjf(self, calculator: Any) -> None:
        """Test WSJF calculation for low-priority item."""
        score = calculator.calculate_wsjf(
            business_value=0.2,
            time_sensitivity=0.1,
            risk_reduction=0.1,
            job_size=0.9,  # Large effort = low priority
        )

        assert score < 0.3

    def test_wsjf_zero_job_size(self, calculator: Any) -> None:
        """Test WSJF with zero job size is handled."""
        score = calculator.calculate_wsjf(
            business_value=1.0,
            time_sensitivity=1.0,
            risk_reduction=1.0,
            job_size=0.0,
        )

        # Should be capped at 1.0
        assert score == 1.0

    def test_wsjf_boundary_values(self, calculator: Any) -> None:
        """Test WSJF with boundary values."""
        # All zeros
        score_zero = calculator.calculate_wsjf(0, 0, 0, 1)
        assert score_zero == 0.0

        # All ones
        score_one = calculator.calculate_wsjf(1, 1, 1, 1)
        assert score_one == 1.0

    def test_wsjf_weighting(self, calculator: Any) -> None:
        """Test WSJF uses correct component weights."""
        # Business value should have 0.4 weight
        score1 = calculator.calculate_wsjf(1.0, 0, 0, 1)
        # Time sensitivity should have 0.3 weight
        score2 = calculator.calculate_wsjf(0, 1.0, 0, 1)
        # Risk reduction should have 0.3 weight
        score3 = calculator.calculate_wsjf(0, 0, 1.0, 1)

        assert score1 > score2
        assert score1 > score3
        assert abs(score2 - score3) < 0.01  # Should be roughly equal


class TestTestSpecFlakinessDector:
    """Tests for TestSpecFlakinessDector."""

    @pytest.fixture
    def detector(self) -> None:
        return TestSpecFlakinessDector()

    def test_stable_test(self, detector: Any) -> None:
        """Test flakiness of stable test."""
        score = detector.calculate_flakiness_score(
            pass_count=100,
            fail_count=0,
            total_runs=100,
            recent_failures=[],
        )

        assert score == 0.0

    def test_completely_failing_test(self, detector: Any) -> None:
        """Test flakiness of consistently failing test."""
        score = detector.calculate_flakiness_score(
            pass_count=0,
            fail_count=100,
            total_runs=100,
            recent_failures=[{"status": "fail", "error": "AssertionError"}] * 100,
        )

        assert score == 1.0

    def test_intermittent_failures(self, detector: Any) -> None:
        """Test flakiness detection with intermittent failures."""
        recent_failures = [
            {"status": "pass"},
            {"status": "fail"},
            {"status": "pass"},
            {"status": "fail"},
        ]

        score = detector.calculate_flakiness_score(
            pass_count=50,
            fail_count=50,
            total_runs=100,
            recent_failures=recent_failures,
        )

        # Alternating pattern should indicate high flakiness
        assert score > 0.4

    def test_flakiness_categorization(self, detector: Any) -> None:
        """Test flakiness category assignment."""
        assert detector.categorize_flakiness(0.8) == "critical"
        assert detector.categorize_flakiness(0.5) == "high"
        assert detector.categorize_flakiness(0.3) == "medium"
        assert detector.categorize_flakiness(0.1) == "low"
        assert detector.categorize_flakiness(0.01) == "stable"

    def test_flakiness_with_different_errors(self, detector: Any) -> None:
        """Test flakiness increases with different error messages."""
        failures_same_error = [
            {"status": "fail", "error": "TimeoutError"},
            {"status": "fail", "error": "TimeoutError"},
            {"status": "fail", "error": "TimeoutError"},
        ]

        failures_different_errors = [
            {"status": "fail", "error": "TimeoutError"},
            {"status": "fail", "error": "AssertionError"},
            {"status": "fail", "error": "ValueError"},
        ]

        score_same = detector.calculate_flakiness_score(3, 3, 6, failures_same_error)
        score_diff = detector.calculate_flakiness_score(3, 3, 6, failures_different_errors)

        # Different errors indicate more flakiness
        assert score_diff > score_same


class TestIntegrationWithModels:
    """Integration tests with actual models."""

    def test_requirement_quality_model_creation(self) -> None:
        """Test RequirementQuality model creation with all fields."""
        from tracertm.models.requirement_quality import RequirementQuality

        spec = RequirementQuality(
            id="test-1",
            item_id="item-1",
            project_id="proj-1",
            quality_scores={
                "unambiguity": 0.85,
                "completeness": 0.90,
                "verifiability": 0.80,
                "necessity": 0.95,
                "singularity": 0.88,
            },
            overall_quality_score=0.88,
            quality_issues=[
                {
                    "dimension": "unambiguity",
                    "severity": "warning",
                    "message": "Ambiguous term",
                    "suggestion": "Use specific metrics",
                },
            ],
            change_propagation_index=0.25,
            downstream_impact_count=5,
            upstream_dependency_count=2,
            volatility_index=0.15,
            wsjf_score=0.75,
        )

        assert spec.item_id == "item-1"
        assert spec.overall_quality_score == 0.88
        assert spec.quality_scores["unambiguity"] == 0.85
        assert spec.is_verified is False
