"""DataFrame schema validation tests using Pandera.

Tests for:
- RequirementSchema
- TraceabilityLinkSchema
- ProjectMetricsSchema
"""

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR

pd = pytest.importorskip("pandas")

try:
    from pandera import ValidationError

    from tracertm.schemas import (
        validate_project_metrics,
        validate_requirements,
        validate_traceability_links,
    )

    HAS_PANDERA = True
except (ImportError, ModuleNotFoundError):
    HAS_PANDERA = False

    # Define mock for testing purposes
    class ValidationError(Exception):
        pass


# ============================================================================
# REQUIREMENT SCHEMA VALIDATION TESTS
# ============================================================================


@pytest.mark.skipif(not HAS_PANDERA, reason="pandera not installed")
class TestRequirementSchemaValidation:
    """Test RequirementSchema validation."""

    def test_valid_requirement_dataframe(self) -> None:
        """Test that valid requirement data passes validation."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Req1", "Req2", "Req3"],
            "description": ["Desc1", "Desc2", "Desc3"],
            "status": ["draft", "active", "deprecated"],
            "priority": [1, 2, 5],
            "created_at": pd.date_range("2024-01-01", periods=3),
            "updated_at": pd.date_range("2024-01-01", periods=3),
        })
        result = validate_requirements(df)
        assert len(result) == COUNT_THREE

    def test_requirement_id_positive_constraint(self) -> None:
        """Test that requirement IDs must be positive (gt=0)."""
        df = pd.DataFrame({
            "id": [0, 1, 2],  # 0 violates gt=0
            "name": ["Req1", "Req2", "Req3"],
            "description": ["Desc1", "Desc2", "Desc3"],
            "status": ["draft", "active", "deprecated"],
            "priority": [1, 2, 5],
            "created_at": pd.date_range("2024-01-01", periods=3),
            "updated_at": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_requirements(df)

    def test_requirement_id_negative_invalid(self) -> None:
        """Test that negative IDs are invalid."""
        df = pd.DataFrame({
            "id": [-1, 1, 2],
            "name": ["Req1", "Req2", "Req3"],
            "description": ["Desc1", "Desc2", "Desc3"],
            "status": ["draft", "active", "deprecated"],
            "priority": [1, 2, 5],
            "created_at": pd.date_range("2024-01-01", periods=3),
            "updated_at": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_requirements(df)

    def test_requirement_name_min_length(self) -> None:
        """Test that requirement names cannot be empty (min_length=1)."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["", "Req2", "Req3"],  # Empty string violates min_length=1
            "description": ["Desc1", "Desc2", "Desc3"],
            "status": ["draft", "active", "deprecated"],
            "priority": [1, 2, 5],
            "created_at": pd.date_range("2024-01-01", periods=3),
            "updated_at": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_requirements(df)

    def test_requirement_status_enum_constraint(self) -> None:
        """Test that status must be one of the allowed values."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Req1", "Req2", "Req3"],
            "description": ["Desc1", "Desc2", "Desc3"],
            "status": ["draft", "active", "invalid_status"],  # Invalid status
            "priority": [1, 2, 5],
            "created_at": pd.date_range("2024-01-01", periods=3),
            "updated_at": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_requirements(df)

    def test_requirement_status_all_valid_values(self) -> None:
        """Test all valid status values."""
        statuses = ["draft", "active", "deprecated", "archived"]
        df = pd.DataFrame({
            "id": list(range(1, len(statuses) + 1)),
            "name": [f"Req{i}" for i in range(len(statuses))],
            "description": ["Desc"] * len(statuses),
            "status": statuses,
            "priority": [1] * len(statuses),
            "created_at": pd.date_range("2024-01-01", periods=len(statuses)),
            "updated_at": pd.date_range("2024-01-01", periods=len(statuses)),
        })
        result = validate_requirements(df)
        assert len(result) == len(statuses)

    def test_requirement_priority_range_1_to_5(self) -> None:
        """Test that priority must be in range 1-5 (ge=1, le=5)."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Req1", "Req2", "Req3"],
            "description": ["Desc1", "Desc2", "Desc3"],
            "status": ["draft", "active", "deprecated"],
            "priority": [1, 3, 6],  # 6 violates le=5
            "created_at": pd.date_range("2024-01-01", periods=3),
            "updated_at": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_requirements(df)

    def test_requirement_priority_below_minimum(self) -> None:
        """Test that priority below 1 is invalid."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Req1", "Req2", "Req3"],
            "description": ["Desc1", "Desc2", "Desc3"],
            "status": ["draft", "active", "deprecated"],
            "priority": [0, 2, 5],  # 0 violates ge=1
            "created_at": pd.date_range("2024-01-01", periods=3),
            "updated_at": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_requirements(df)

    def test_requirement_priority_boundaries(self) -> None:
        """Test priority boundary values."""
        df = pd.DataFrame({
            "id": [1, 2],
            "name": ["Req1", "Req2"],
            "description": ["Desc1", "Desc2"],
            "status": ["draft", "active"],
            "priority": [1, 5],  # Boundaries
            "created_at": pd.date_range("2024-01-01", periods=2),
            "updated_at": pd.date_range("2024-01-01", periods=2),
        })
        result = validate_requirements(df)
        assert len(result) == COUNT_TWO


# ============================================================================
# TRACEABILITY LINK SCHEMA VALIDATION TESTS
# ============================================================================


@pytest.mark.skipif(not HAS_PANDERA, reason="pandera not installed")
class TestTraceabilityLinkSchemaValidation:
    """Test TraceabilityLinkSchema validation."""

    def test_valid_traceability_link_dataframe(self) -> None:
        """Test that valid link data passes validation."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "source_id": [1, 2, 3],
            "target_id": [2, 3, 4],
            "link_type": ["implements", "tests", "depends_on"],
            "strength": [0.8, 0.9, 0.7],
        })
        result = validate_traceability_links(df)
        assert len(result) == COUNT_THREE

    def test_link_id_positive_constraint(self) -> None:
        """Test that link IDs must be positive."""
        df = pd.DataFrame({
            "id": [0, 1, 2],  # 0 violates gt=0
            "source_id": [1, 2, 3],
            "target_id": [2, 3, 4],
            "link_type": ["implements", "tests", "depends_on"],
            "strength": [0.8, 0.9, 0.7],
        })
        with pytest.raises(ValidationError):
            validate_traceability_links(df)

    def test_link_source_id_positive_constraint(self) -> None:
        """Test that source_id must be positive."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "source_id": [0, 2, 3],  # 0 violates gt=0
            "target_id": [2, 3, 4],
            "link_type": ["implements", "tests", "depends_on"],
            "strength": [0.8, 0.9, 0.7],
        })
        with pytest.raises(ValidationError):
            validate_traceability_links(df)

    def test_link_target_id_positive_constraint(self) -> None:
        """Test that target_id must be positive."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "source_id": [1, 2, 3],
            "target_id": [0, 3, 4],  # 0 violates gt=0
            "link_type": ["implements", "tests", "depends_on"],
            "strength": [0.8, 0.9, 0.7],
        })
        with pytest.raises(ValidationError):
            validate_traceability_links(df)

    def test_link_type_enum_constraint(self) -> None:
        """Test that link_type must be one of allowed values."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "source_id": [1, 2, 3],
            "target_id": [2, 3, 4],
            "link_type": ["implements", "tests", "invalid_type"],  # Invalid type
            "strength": [0.8, 0.9, 0.7],
        })
        with pytest.raises(ValidationError):
            validate_traceability_links(df)

    def test_link_type_all_valid_values(self) -> None:
        """Test all valid link types."""
        types = ["implements", "tests", "depends_on", "related_to"]
        df = pd.DataFrame({
            "id": list(range(1, len(types) + 1)),
            "source_id": list(range(1, len(types) + 1)),
            "target_id": list(range(2, len(types) + 2)),
            "link_type": types,
            "strength": [0.8] * len(types),
        })
        result = validate_traceability_links(df)
        assert len(result) == len(types)

    def test_link_strength_range_0_to_1(self) -> None:
        """Test that strength must be in range 0.0-1.0."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "source_id": [1, 2, 3],
            "target_id": [2, 3, 4],
            "link_type": ["implements", "tests", "depends_on"],
            "strength": [0.0, 0.5, 1.5],  # 1.5 violates le=1.0
        })
        with pytest.raises(ValidationError):
            validate_traceability_links(df)

    def test_link_strength_negative_invalid(self) -> None:
        """Test that negative strength is invalid."""
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "source_id": [1, 2, 3],
            "target_id": [2, 3, 4],
            "link_type": ["implements", "tests", "depends_on"],
            "strength": [-0.1, 0.5, 0.8],  # -0.1 violates ge=0.0
        })
        with pytest.raises(ValidationError):
            validate_traceability_links(df)

    def test_link_strength_boundaries(self) -> None:
        """Test strength boundary values."""
        df = pd.DataFrame({
            "id": [1, 2],
            "source_id": [1, 2],
            "target_id": [2, 3],
            "link_type": ["implements", "tests"],
            "strength": [0.0, 1.0],  # Boundaries
        })
        result = validate_traceability_links(df)
        assert len(result) == COUNT_TWO


# ============================================================================
# PROJECT METRICS SCHEMA VALIDATION TESTS
# ============================================================================


@pytest.mark.skipif(not HAS_PANDERA, reason="pandera not installed")
class TestProjectMetricsSchemaValidation:
    """Test ProjectMetricsSchema validation."""

    def test_valid_project_metrics_dataframe(self) -> None:
        """Test that valid metrics data passes validation."""
        df = pd.DataFrame({
            "project_id": [1, 2, 3],
            "total_requirements": [10, 20, 30],
            "implemented": [8, 15, 25],
            "tested": [7, 12, 20],
            "coverage": [70.0, 75.0, 80.0],
            "timestamp": pd.date_range("2024-01-01", periods=3),
        })
        result = validate_project_metrics(df)
        assert len(result) == COUNT_THREE

    def test_metrics_project_id_positive_constraint(self) -> None:
        """Test that project_id must be positive."""
        df = pd.DataFrame({
            "project_id": [0, 1, 2],  # 0 violates gt=0
            "total_requirements": [10, 20, 30],
            "implemented": [8, 15, 25],
            "tested": [7, 12, 20],
            "coverage": [70.0, 75.0, 80.0],
            "timestamp": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_project_metrics(df)

    def test_metrics_total_requirements_non_negative(self) -> None:
        """Test that total_requirements must be non-negative."""
        df = pd.DataFrame({
            "project_id": [1, 2, 3],
            "total_requirements": [-1, 20, 30],  # -1 violates ge=0
            "implemented": [8, 15, 25],
            "tested": [7, 12, 20],
            "coverage": [70.0, 75.0, 80.0],
            "timestamp": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_project_metrics(df)

    def test_metrics_implemented_non_negative(self) -> None:
        """Test that implemented must be non-negative."""
        df = pd.DataFrame({
            "project_id": [1, 2, 3],
            "total_requirements": [10, 20, 30],
            "implemented": [-1, 15, 25],  # -1 violates ge=0
            "tested": [7, 12, 20],
            "coverage": [70.0, 75.0, 80.0],
            "timestamp": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_project_metrics(df)

    def test_metrics_tested_non_negative(self) -> None:
        """Test that tested must be non-negative."""
        df = pd.DataFrame({
            "project_id": [1, 2, 3],
            "total_requirements": [10, 20, 30],
            "implemented": [8, 15, 25],
            "tested": [-1, 12, 20],  # -1 violates ge=0
            "coverage": [70.0, 75.0, 80.0],
            "timestamp": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_project_metrics(df)

    def test_metrics_coverage_range_0_to_100(self) -> None:
        """Test that coverage must be in range 0.0-100.0."""
        df = pd.DataFrame({
            "project_id": [1, 2, 3],
            "total_requirements": [10, 20, 30],
            "implemented": [8, 15, 25],
            "tested": [7, 12, 20],
            "coverage": [0.0, 50.0, 100.5],  # 100.5 violates le=100.0
            "timestamp": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_project_metrics(df)

    def test_metrics_coverage_negative_invalid(self) -> None:
        """Test that negative coverage is invalid."""
        df = pd.DataFrame({
            "project_id": [1, 2, 3],
            "total_requirements": [10, 20, 30],
            "implemented": [8, 15, 25],
            "tested": [7, 12, 20],
            "coverage": [-0.1, 50.0, 80.0],  # -0.1 violates ge=0.0
            "timestamp": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_project_metrics(df)

    def test_metrics_coverage_boundaries(self) -> None:
        """Test coverage boundary values."""
        df = pd.DataFrame({
            "project_id": [1, 2],
            "total_requirements": [10, 20],
            "implemented": [0, 20],
            "tested": [0, 20],
            "coverage": [0.0, 100.0],  # Boundaries
            "timestamp": pd.date_range("2024-01-01", periods=2),
        })
        result = validate_project_metrics(df)
        assert len(result) == COUNT_TWO

    def test_metrics_coverage_zero_percent(self) -> None:
        """Test coverage at zero percent."""
        df = pd.DataFrame({
            "project_id": [1],
            "total_requirements": [10],
            "implemented": [0],
            "tested": [0],
            "coverage": [0.0],
        })
        result = validate_project_metrics(df)
        assert len(result) == 1
        assert result["coverage"].iloc[0] == 0.0

    def test_metrics_coverage_100_percent(self) -> None:
        """Test coverage at 100 percent."""
        df = pd.DataFrame({
            "project_id": [1],
            "total_requirements": [10],
            "implemented": [10],
            "tested": [10],
            "coverage": [100.0],
        })
        result = validate_project_metrics(df)
        assert len(result) == 1
        assert result["coverage"].iloc[0] == 100.0


# ============================================================================
# SCHEMA COERCION TESTS
# ============================================================================


@pytest.mark.skipif(not HAS_PANDERA, reason="pandera not installed")
class TestSchemaCoercion:
    """Test schema coercion with strict=True and coerce=True."""

    def test_requirement_coerces_to_correct_types(self) -> None:
        """Test that schema coerces data to correct types."""
        df = pd.DataFrame({
            "id": ["1", "2", "3"],  # String IDs
            "name": ["Req1", "Req2", "Req3"],
            "description": ["Desc1", "Desc2", "Desc3"],
            "status": ["draft", "active", "deprecated"],
            "priority": [1, 2, 5],
            "created_at": pd.date_range("2024-01-01", periods=3),
            "updated_at": pd.date_range("2024-01-01", periods=3),
        })
        result = validate_requirements(df)
        # Coercion should convert string IDs to int
        assert result["id"].dtype in {int, "int64"}

    def test_link_strength_type_coercion(self) -> None:
        """Test strength is numeric type."""
        df = pd.DataFrame({
            "id": [1, 2],
            "source_id": [1, 2],
            "target_id": [2, 3],
            "link_type": ["implements", "tests"],
            "strength": [0.8, 0.9],  # Float
        })
        result = validate_traceability_links(df)
        assert result["strength"].dtype in {float, "float64"}


# ============================================================================
# MISSING DATA AND NULL HANDLING TESTS
# ============================================================================


@pytest.mark.skipif(not HAS_PANDERA, reason="pandera not installed")
class TestMissingDataHandling:
    """Test handling of missing/null data."""

    def test_requirement_missing_required_column(self) -> None:
        """Test that missing required columns fails validation."""
        df = pd.DataFrame({
            # Missing 'id' column
            "name": ["Req1"],
            "description": ["Desc1"],
            "status": ["draft"],
            "priority": [1],
            "created_at": pd.date_range("2024-01-01", periods=1),
            "updated_at": pd.date_range("2024-01-01", periods=1),
        })
        with pytest.raises(ValidationError):
            validate_requirements(df)

    def test_requirement_null_in_required_field(self) -> None:
        """Test that nulls in required fields cause validation failure."""
        df = pd.DataFrame({
            "id": [1, None, 3],  # None violates NOT NULL
            "name": ["Req1", "Req2", "Req3"],
            "description": ["Desc1", "Desc2", "Desc3"],
            "status": ["draft", "active", "deprecated"],
            "priority": [1, 2, 5],
            "created_at": pd.date_range("2024-01-01", periods=3),
            "updated_at": pd.date_range("2024-01-01", periods=3),
        })
        with pytest.raises(ValidationError):
            validate_requirements(df)


# ============================================================================
# DATAFRAME SIZE AND SCALE TESTS
# ============================================================================


@pytest.mark.skipif(not HAS_PANDERA, reason="pandera not installed")
class TestDataFrameScale:
    """Test schema validation at scale."""

    def test_requirement_large_dataframe(self) -> None:
        """Test validation of large requirement dataset."""
        df = pd.DataFrame({
            "id": range(1, 1001),  # 1000 rows
            "name": [f"Req{i}" for i in range(1000)],
            "description": ["Desc"] * 1000,
            "status": ["draft"] * 1000,
            "priority": [1] * 1000,
            "created_at": pd.date_range("2024-01-01", periods=1000),
            "updated_at": pd.date_range("2024-01-01", periods=1000),
        })
        result = validate_requirements(df)
        assert len(result) == 1000

    def test_link_large_dataframe(self) -> None:
        """Test validation of large link dataset."""
        df = pd.DataFrame({
            "id": range(1, 501),
            "source_id": range(1, 501),
            "target_id": range(2, 502),
            "link_type": ["implements"] * 500,
            "strength": [0.8] * 500,
        })
        result = validate_traceability_links(df)
        assert len(result) == HTTP_INTERNAL_SERVER_ERROR

    def test_metrics_large_dataframe(self) -> None:
        """Test validation of large metrics dataset."""
        df = pd.DataFrame({
            "project_id": range(1, 101),
            "total_requirements": [10] * 100,
            "implemented": [8] * 100,
            "tested": [7] * 100,
            "coverage": [70.0] * 100,
            "timestamp": pd.date_range("2024-01-01", periods=100),
        })
        result = validate_project_metrics(df)
        assert len(result) == 100


# ============================================================================
# EMPTY DATAFRAME TESTS
# ============================================================================


@pytest.mark.skipif(not HAS_PANDERA, reason="pandera not installed")
class TestEmptyDataFrames:
    """Test schema validation with empty data."""

    def test_empty_requirement_dataframe(self) -> None:
        """Test validation of empty requirement dataframe."""
        df = pd.DataFrame({
            "id": pd.Series([], dtype="int64"),
            "name": pd.Series([], dtype="str"),
            "description": pd.Series([], dtype="str"),
            "status": pd.Series([], dtype="str"),
            "priority": pd.Series([], dtype="int64"),
            "created_at": pd.Series([], dtype="datetime64[ns]"),
            "updated_at": pd.Series([], dtype="datetime64[ns]"),
        })
        result = validate_requirements(df)
        assert len(result) == 0

    def test_empty_link_dataframe(self) -> None:
        """Test validation of empty link dataframe."""
        df = pd.DataFrame({
            "id": pd.Series([], dtype="int64"),
            "source_id": pd.Series([], dtype="int64"),
            "target_id": pd.Series([], dtype="int64"),
            "link_type": pd.Series([], dtype="str"),
            "strength": pd.Series([], dtype="float64"),
        })
        result = validate_traceability_links(df)
        assert len(result) == 0

    def test_empty_metrics_dataframe(self) -> None:
        """Test validation of empty metrics dataframe."""
        df = pd.DataFrame({
            "project_id": pd.Series([], dtype="int64"),
            "total_requirements": pd.Series([], dtype="int64"),
            "implemented": pd.Series([], dtype="int64"),
            "tested": pd.Series([], dtype="int64"),
            "coverage": pd.Series([], dtype="float64"),
            "timestamp": pd.Series([], dtype="datetime64[ns]"),
        })
        result = validate_project_metrics(df)
        assert len(result) == 0
