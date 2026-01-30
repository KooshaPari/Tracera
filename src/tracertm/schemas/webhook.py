"""
Pydantic schemas for Webhook Integrations.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class WebhookCreate(BaseModel):
    """Schema for creating a webhook integration."""

    name: str = Field(..., min_length=1, max_length=255, description="Webhook name")
    description: Optional[str] = Field(default=None, description="Description")
    provider: str = Field(
        default="custom",
        description="Provider: github_actions, gitlab_ci, jenkins, azure_devops, circleci, travis_ci, custom",
    )
    enabled_events: Optional[list[str]] = Field(
        default=None,
        description="List of enabled event types",
    )
    event_filters: Optional[dict[str, Any]] = Field(
        default=None,
        description="Event filtering rules",
    )
    callback_url: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="URL to send callbacks to",
    )
    callback_headers: Optional[dict[str, str]] = Field(
        default=None,
        description="Headers to include in callbacks",
    )
    default_suite_id: Optional[str] = Field(
        default=None,
        description="Default test suite ID for results",
    )
    rate_limit_per_minute: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="Maximum requests per minute",
    )
    auto_create_run: bool = Field(
        default=True,
        description="Auto-create test run if not specified",
    )
    auto_complete_run: bool = Field(
        default=True,
        description="Auto-complete run when bulk results indicate complete",
    )
    verify_signatures: bool = Field(
        default=True,
        description="Require HMAC signature verification",
    )
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Extensible metadata",
    )


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook integration."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled_events: Optional[list[str]] = None
    event_filters: Optional[dict[str, Any]] = None
    callback_url: Optional[str] = Field(default=None, max_length=1000)
    callback_headers: Optional[dict[str, str]] = None
    default_suite_id: Optional[str] = None
    rate_limit_per_minute: Optional[int] = Field(default=None, ge=1, le=1000)
    auto_create_run: Optional[bool] = None
    auto_complete_run: Optional[bool] = None
    verify_signatures: Optional[bool] = None
    metadata: Optional[dict[str, Any]] = None


class WebhookResponse(BaseModel):
    """Schema for webhook integration response."""

    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    provider: str
    status: str
    webhook_secret: str
    api_key: Optional[str] = None
    enabled_events: Optional[list[str]] = None
    event_filters: Optional[dict[str, Any]] = None
    callback_url: Optional[str] = None
    callback_headers: Optional[dict[str, str]] = None
    default_suite_id: Optional[str] = None
    rate_limit_per_minute: int
    auto_create_run: bool
    auto_complete_run: bool
    verify_signatures: bool
    # Statistics
    total_requests: int
    successful_requests: int
    failed_requests: int
    last_request_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    last_error_message: Optional[str] = None
    webhook_metadata: Optional[dict[str, Any]] = None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WebhookListResponse(BaseModel):
    """Schema for paginated webhook list."""

    webhooks: list[WebhookResponse]
    total: int
    skip: int
    limit: int


class WebhookStatusUpdate(BaseModel):
    """Schema for updating webhook status."""

    status: str = Field(
        ...,
        description="New status: active, paused, disabled",
    )


class WebhookLogResponse(BaseModel):
    """Schema for webhook log response."""

    id: str
    webhook_id: str
    request_id: str
    event_type: Optional[str] = None
    http_method: str
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    request_headers: Optional[dict[str, Any]] = None
    request_body_preview: Optional[str] = None
    payload_size_bytes: Optional[int] = None
    success: bool
    status_code: int
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
    test_run_id: Optional[str] = None
    results_submitted: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WebhookLogsResponse(BaseModel):
    """Schema for paginated webhook logs."""

    logs: list[WebhookLogResponse]
    total: int
    skip: int
    limit: int


class WebhookStats(BaseModel):
    """Schema for webhook statistics."""

    project_id: str
    total: int
    by_status: dict[str, int]
    by_provider: dict[str, int]
    total_requests: int
    successful_requests: int
    failed_requests: int


# Inbound webhook payload schemas
class InboundWebhookPayload(BaseModel):
    """Schema for inbound webhook payload."""

    action: str = Field(
        ...,
        description="Action: create_run, start_run, submit_result, bulk_results, complete_run",
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO8601 timestamp",
    )
    payload: Optional[dict[str, Any]] = Field(
        default=None,
        description="Action-specific payload",
    )


class CreateRunPayload(BaseModel):
    """Payload for create_run action."""

    name: Optional[str] = None
    description: Optional[str] = None
    suite_id: Optional[str] = None
    environment: Optional[str] = None
    build_number: Optional[str] = None
    build_url: Optional[str] = None
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
    initiated_by: Optional[str] = None
    external_run_id: Optional[str] = None


class StartRunPayload(BaseModel):
    """Payload for start_run action."""

    run_id: str
    executed_by: Optional[str] = None


class SubmitResultPayload(BaseModel):
    """Payload for submit_result action."""

    run_id: Optional[str] = None
    test_case_id: str
    status: str = Field(default="passed")
    executed_by: Optional[str] = None
    actual_result: Optional[str] = None
    failure_reason: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    duration_seconds: Optional[float] = None
    screenshots: Optional[list[str]] = None
    logs_url: Optional[str] = None
    notes: Optional[str] = None
    is_flaky: bool = False
    # Optional for auto-create
    build_number: Optional[str] = None
    branch: Optional[str] = None
    commit_sha: Optional[str] = None


class BulkResultItem(BaseModel):
    """Single result item in bulk submission."""

    test_case_id: str
    status: str = Field(default="passed")
    executed_by: Optional[str] = None
    actual_result: Optional[str] = None
    failure_reason: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    is_flaky: bool = False


class BulkResultsPayload(BaseModel):
    """Payload for bulk_results action."""

    run_id: Optional[str] = None
    results: list[BulkResultItem]
    complete: bool = Field(
        default=False,
        description="Auto-complete run after submitting results",
    )
    # Optional for auto-create
    build_number: Optional[str] = None
    branch: Optional[str] = None
    commit_sha: Optional[str] = None


class CompleteRunPayload(BaseModel):
    """Payload for complete_run action."""

    run_id: str
    failure_summary: Optional[str] = None
    notes: Optional[str] = None


class InboundWebhookResponse(BaseModel):
    """Schema for inbound webhook response."""

    success: bool
    message: str
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
