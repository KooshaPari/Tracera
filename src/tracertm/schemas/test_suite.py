"""
Pydantic schemas for Test Suite API.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TestSuiteTestCaseCreate(BaseModel):
    """Schema for adding a test case to a suite."""

    test_case_id: str
    order_index: int = 0
    is_mandatory: bool = True
    skip_reason: Optional[str] = None
    custom_parameters: Optional[dict[str, Any]] = None


class TestSuiteTestCaseResponse(BaseModel):
    """Response schema for suite test case association."""

    id: str
    suite_id: str
    test_case_id: str
    order_index: int
    is_mandatory: bool
    skip_reason: Optional[str]
    custom_parameters: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestSuiteCreate(BaseModel):
    """Schema for creating a test suite."""

    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    objective: Optional[str] = Field(None, max_length=2000)
    parent_id: Optional[str] = None
    order_index: int = 0
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[list[str]] = None
    is_parallel_execution: bool = False
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    required_environment: Optional[str] = Field(None, max_length=255)
    environment_variables: Optional[dict[str, str]] = None
    setup_instructions: Optional[str] = None
    teardown_instructions: Optional[str] = None
    owner: Optional[str] = Field(None, max_length=255)
    responsible_team: Optional[str] = Field(None, max_length=255)
    metadata: Optional[dict[str, Any]] = None


class TestSuiteUpdate(BaseModel):
    """Schema for updating a test suite."""

    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    objective: Optional[str] = Field(None, max_length=2000)
    parent_id: Optional[str] = None
    order_index: Optional[int] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[list[str]] = None
    is_parallel_execution: Optional[bool] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    required_environment: Optional[str] = Field(None, max_length=255)
    environment_variables: Optional[dict[str, str]] = None
    setup_instructions: Optional[str] = None
    teardown_instructions: Optional[str] = None
    owner: Optional[str] = Field(None, max_length=255)
    responsible_team: Optional[str] = Field(None, max_length=255)
    metadata: Optional[dict[str, Any]] = None


class TestSuiteResponse(BaseModel):
    """Response schema for a test suite."""

    id: str
    suite_number: str
    project_id: str
    name: str
    description: Optional[str]
    objective: Optional[str]
    status: str
    parent_id: Optional[str]
    order_index: int
    category: Optional[str]
    tags: Optional[list[str]]
    is_parallel_execution: bool
    estimated_duration_minutes: Optional[int]
    required_environment: Optional[str]
    environment_variables: Optional[dict[str, str]]
    setup_instructions: Optional[str]
    teardown_instructions: Optional[str]
    owner: Optional[str]
    responsible_team: Optional[str]
    total_test_cases: int
    automated_count: int
    last_run_at: Optional[datetime]
    last_run_result: Optional[str]
    pass_rate: Optional[float]
    metadata: Optional[dict[str, Any]]
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestSuiteListResponse(BaseModel):
    """Response schema for listing test suites."""

    test_suites: list[TestSuiteResponse]
    total: int


class TestSuiteStatusTransition(BaseModel):
    """Schema for transitioning suite status."""

    new_status: str = Field(..., pattern="^(draft|active|deprecated|archived)$")
    reason: Optional[str] = None


class TestSuiteActivityResponse(BaseModel):
    """Response schema for suite activity log entry."""

    id: str
    suite_id: str
    activity_type: str
    from_value: Optional[str]
    to_value: Optional[str]
    description: Optional[str]
    performed_by: Optional[str]
    metadata: Optional[dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}


class TestSuiteActivitiesResponse(BaseModel):
    """Response schema for suite activities list."""

    suite_id: str
    activities: list[TestSuiteActivityResponse]


class TestSuiteStats(BaseModel):
    """Statistics for test suites in a project."""

    project_id: str
    total: int
    by_status: dict[str, int]
    by_category: dict[str, int]
    total_test_cases: int
    automated_test_cases: int
