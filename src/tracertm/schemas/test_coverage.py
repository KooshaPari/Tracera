"""
Pydantic schemas for Test Coverage.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TestCoverageCreate(BaseModel):
    """Schema for creating a test coverage mapping."""

    test_case_id: str = Field(..., description="ID of the test case")
    requirement_id: str = Field(..., description="ID of the requirement/item being covered")
    coverage_type: str = Field(
        default="direct",
        description="Type of coverage: direct, partial, indirect, regression",
    )
    coverage_percentage: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Coverage percentage for partial coverage",
    )
    rationale: Optional[str] = Field(default=None, description="Rationale for the mapping")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Extensible metadata")


class TestCoverageUpdate(BaseModel):
    """Schema for updating a test coverage mapping."""

    coverage_type: Optional[str] = None
    status: Optional[str] = None
    coverage_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    rationale: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class TestCoverageResponse(BaseModel):
    """Schema for test coverage response."""

    id: str
    project_id: str
    test_case_id: str
    requirement_id: str
    coverage_type: str
    status: str
    coverage_percentage: Optional[int] = None
    rationale: Optional[str] = None
    notes: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    last_test_result: Optional[str] = None
    last_tested_at: Optional[datetime] = None
    created_by: Optional[str] = None
    coverage_metadata: Optional[dict[str, Any]] = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestCoverageListResponse(BaseModel):
    """Schema for paginated test coverage list."""

    coverages: list[TestCoverageResponse]
    total: int
    skip: int
    limit: int


class TestCoverageVerify(BaseModel):
    """Schema for verifying a coverage mapping."""

    notes: Optional[str] = None


class CoverageActivityResponse(BaseModel):
    """Schema for coverage activity response."""

    id: str
    coverage_id: str
    activity_type: str
    from_value: Optional[str] = None
    to_value: Optional[str] = None
    description: Optional[str] = None
    performed_by: Optional[str] = None
    activity_metadata: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TraceabilityMatrixItem(BaseModel):
    """Schema for a single item in the traceability matrix."""

    requirement_id: str
    requirement_title: str
    requirement_view: str
    requirement_status: str
    is_covered: bool
    test_count: int
    test_cases: list[dict[str, Any]]
    overall_status: str


class TraceabilityMatrixResponse(BaseModel):
    """Schema for traceability matrix response."""

    project_id: str
    total_requirements: int
    covered_requirements: int
    uncovered_requirements: int
    coverage_percentage: float
    matrix: list[TraceabilityMatrixItem]


class CoverageGapItem(BaseModel):
    """Schema for a single coverage gap item."""

    requirement_id: str
    requirement_title: str
    requirement_view: str
    requirement_status: str
    priority: Optional[str] = None


class CoverageGapsResponse(BaseModel):
    """Schema for coverage gaps response."""

    project_id: str
    total_requirements: int
    uncovered_count: int
    coverage_percentage: float
    gaps: list[CoverageGapItem]


class TestCaseCoverageSummary(BaseModel):
    """Schema for test case coverage summary."""

    test_case_id: str
    total_requirements_covered: int
    coverage_types: dict[str, int]
    requirements: list[dict[str, Any]]


class CoverageStats(BaseModel):
    """Schema for coverage statistics."""

    project_id: str
    total_mappings: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    unique_test_cases: int
    unique_requirements: int
