"""Pandera schemas for DataFrame validation.

Provides type-safe DataFrame schemas for data validation at boundaries.
"""

import pandera as pa  # type: ignore[possibly-unknown-member]  # pandera type stubs incomplete
from pandera.typing import DataFrame, Series  # type: ignore[possibly-missing-import]  # pandera.typing stubs incomplete


class RequirementSchema(pa.DataFrameModel):
    """Schema for requirement data."""

    id: Series[int] = pa.Field(gt=0, description="Unique requirement ID")
    name: Series[str] = pa.Field(min_length=1, description="Requirement name")
    description: Series[str] = pa.Field(description="Requirement description")
    status: Series[str] = pa.Field(
        isin=["draft", "active", "deprecated", "archived"],
        description="Requirement status",
    )
    priority: Series[int] = pa.Field(ge=1, le=5, description="Priority level (1-5)")
    created_at: Series[object] = pa.Field(description="Creation timestamp")
    updated_at: Series[object] = pa.Field(description="Last update timestamp")

    class Config:
        """Pandera config."""

        strict = True
        coerce = True


class TraceabilityLinkSchema(pa.DataFrameModel):
    """Schema for traceability links."""

    id: Series[int] = pa.Field(gt=0, description="Unique link ID")
    source_id: Series[int] = pa.Field(gt=0, description="Source requirement ID")
    target_id: Series[int] = pa.Field(gt=0, description="Target requirement ID")
    link_type: Series[str] = pa.Field(
        isin=["implements", "tests", "depends_on", "related_to"],
        description="Type of link",
    )
    strength: Series[float] = pa.Field(ge=0.0, le=1.0, description="Link strength")

    class Config:
        """Pandera config."""

        strict = True
        coerce = True


class ProjectMetricsSchema(pa.DataFrameModel):
    """Schema for project metrics."""

    project_id: Series[int] = pa.Field(gt=0, description="Project ID")
    total_requirements: Series[int] = pa.Field(ge=0, description="Total requirements")
    implemented: Series[int] = pa.Field(ge=0, description="Implemented count")
    tested: Series[int] = pa.Field(ge=0, description="Tested count")
    coverage: Series[float] = pa.Field(ge=0.0, le=100.0, description="Coverage %")
    timestamp: Series[object] = pa.Field(description="Metric timestamp")

    class Config:
        """Pandera config."""

        strict = True
        coerce = True


def validate_requirements(df: DataFrame) -> DataFrame[RequirementSchema]:
    """Validate requirements DataFrame."""
    return RequirementSchema.validate(df, lazy=True)


def validate_traceability_links(df: DataFrame) -> DataFrame[TraceabilityLinkSchema]:
    """Validate traceability links DataFrame."""
    return TraceabilityLinkSchema.validate(df, lazy=True)


def validate_project_metrics(df: DataFrame) -> DataFrame[ProjectMetricsSchema]:
    """Validate project metrics DataFrame."""
    return ProjectMetricsSchema.validate(df, lazy=True)
