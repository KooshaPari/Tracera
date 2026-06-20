"""Pydantic schemas for Webhook Integrations."""

from datetime import datetime

from pydantic import BaseModel, Field


class WebhookCreate(BaseModel):
    """Schema for creating a webhook integration."""

    name: str = Field(..., min_length=1, max_length=255, description="Webhook name")
    description: str | None = Field(default=None, description="Description")
    provider: str = Field(
        default="custom",
        description="Provider: github_actions, gitlab_ci, jenkins, azure_devops, circleci, travis_ci, custom",
    )
    enabled_events: list[str] | None = Field(
        default=None,
        description="List of enabled event types",
    )
    event_filters: dict[str, object] | None = Field(
        default=None,
        description="Event filtering rules",
    )
    callback_url: str | None = Field(
        default=None,
        max_length=1000,
        description="URL to send callbacks to",
    )
    callback_headers: dict[str, str] | None = Field(
        default=None,
        description="Headers to include in callbacks",
    )
    default_suite_id: str | None = Field(
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
    metadata: dict[str, object] | None = Field(
        default=None,
        description="Extensible metadata",
    )


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook integration."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    enabled_events: list[str] | None = None
    event_filters: dict[str, object] | None = None
    callback_url: str | None = Field(default=None, max_length=1000)
    callback_headers: dict[str, str] | None = None
    default_suite_id: str | None = None
    rate_limit_per_minute: int | None = Field(default=None, ge=1, le=1000)
    auto_create_run: bool | None = None
    auto_complete_run: bool | None = None
    verify_signatures: bool | None = None
    metadata: dict[str, object] | None = None


class WebhookResponse(BaseModel):
    """Schema for webhook integration response."""

    id: str
    project_id: str
    name: str
    description: str | None = None
    provider: str
    status: str
    webhook_secret: str
    api_key: str | None = None
    enabled_events: list[str] | None = None
    event_filters: dict[str, object] | None = None
    callback_url: str | None = None
    callback_headers: dict[str, str] | None = None
    default_suite_id: str | None = None
    rate_limit_per_minute: int
    auto_create_run: bool
    auto_complete_run: bool
    verify_signatures: bool
    # Statistics
    total_requests: int
    successful_requests: int
    failed_requests: int
    last_request_at: datetime | None = None
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None
    last_error_message: str | None = None
    webhook_metadata: dict[str, object] | None = None
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
    event_type: str | None = None
    http_method: str
    source_ip: str | None = None
    user_agent: str | None = None
    request_headers: dict[str, object] | None = None
    request_body_preview: str | None = None
    payload_size_bytes: int | None = None
    success: bool
    status_code: int
    error_message: str | None = None
    processing_time_ms: int | None = None
    test_run_id: str | None = None
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
    timestamp: str | None = Field(
        default=None,
        description="ISO8601 timestamp",
    )
    payload: dict[str, object] | None = Field(
        default=None,
        description="Action-specific payload",
    )


class CreateRunPayload(BaseModel):
    """Payload for create_run action."""

    name: str | None = None
    description: str | None = None
    suite_id: str | None = None
    environment: str | None = None
    build_number: str | None = None
    build_url: str | None = None
    branch: str | None = None
    commit_sha: str | None = None
    initiated_by: str | None = None
    external_run_id: str | None = None


class StartRunPayload(BaseModel):
    """Payload for start_run action."""

    run_id: str
    executed_by: str | None = None


class SubmitResultPayload(BaseModel):
    """Payload for submit_result action."""

    run_id: str | None = None
    test_case_id: str
    status: str = Field(default="passed")
    executed_by: str | None = None
    actual_result: str | None = None
    failure_reason: str | None = None
    error_message: str | None = None
    stack_trace: str | None = None
    duration_seconds: float | None = None
    screenshots: list[str] | None = None
    logs_url: str | None = None
    notes: str | None = None
    is_flaky: bool = False
    # Optional for auto-create
    build_number: str | None = None
    branch: str | None = None
    commit_sha: str | None = None


class BulkResultItem(BaseModel):
    """Single result item in bulk submission."""

    test_case_id: str
    status: str = Field(default="passed")
    executed_by: str | None = None
    actual_result: str | None = None
    failure_reason: str | None = None
    error_message: str | None = None
    duration_seconds: float | None = None
    is_flaky: bool = False


class BulkResultsPayload(BaseModel):
    """Payload for bulk_results action."""

    run_id: str | None = None
    results: list[BulkResultItem]
    complete: bool = Field(
        default=False,
        description="Auto-complete run after submitting results",
    )
    # Optional for auto-create
    build_number: str | None = None
    branch: str | None = None
    commit_sha: str | None = None


class CompleteRunPayload(BaseModel):
    """Payload for complete_run action."""

    run_id: str
    failure_summary: str | None = None
    notes: str | None = None


class InboundWebhookResponse(BaseModel):
    """Schema for inbound webhook response."""

    success: bool
    message: str
    data: dict[str, object] | None = None
    error: str | None = None
    rate_limit_remaining: int | None = None
