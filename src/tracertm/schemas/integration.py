"""Pydantic schemas for external integrations."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

# ==================== ENUMS ====================


class IntegrationProvider(StrEnum):
    """Supported external integration providers."""

    GITHUB = "github"
    GITHUB_PROJECTS = "github_projects"
    LINEAR = "linear"


class CredentialType(StrEnum):
    """Type of credential stored."""

    OAUTH_TOKEN = "oauth_token"
    PAT = "personal_access_token"
    GITHUB_APP = "github_app"


class CredentialStatus(StrEnum):
    """Status of a credential."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"


class MappingDirection(StrEnum):
    """Sync direction for mappings."""

    BIDIRECTIONAL = "bidirectional"
    TRACERTM_TO_EXTERNAL = "tracertm_to_external"
    EXTERNAL_TO_TRACERTM = "external_to_tracertm"


class MappingStatus(StrEnum):
    """Status of a mapping."""

    ACTIVE = "active"
    PAUSED = "paused"
    SYNC_ERROR = "sync_error"


class ConflictResolutionStrategy(StrEnum):
    """Conflict resolution strategy."""

    MANUAL = "manual"
    TRACERTM_WINS = "tracertm_wins"
    EXTERNAL_WINS = "external_wins"
    LAST_WRITE_WINS = "last_write_wins"


class SyncEventType(StrEnum):
    """Types of sync events."""

    ITEM_CREATED = "item_created"
    ITEM_UPDATED = "item_updated"
    ITEM_DELETED = "item_deleted"
    STATUS_CHANGED = "status_changed"
    LINKED = "linked"
    UNLINKED = "unlinked"


class SyncDirection(StrEnum):
    """Direction of sync."""

    PUSH = "push"
    PULL = "pull"


class SyncQueueStatus(StrEnum):
    """Status of sync queue item."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRIED = "retried"


class ConflictResolutionStatus(StrEnum):
    """Status of conflict resolution."""

    PENDING = "pending"
    RESOLVED = "resolved"
    IGNORED = "ignored"


# ==================== OAUTH SCHEMAS ====================


class OAuthStartRequest(BaseModel):
    """Request to start OAuth flow."""

    provider: IntegrationProvider
    scopes: list[str] | None = None


class OAuthStartResponse(BaseModel):
    """Response with OAuth redirect URL."""

    oauth_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    """Receive OAuth callback."""

    code: str
    state: str
    error: str | None = None
    error_description: str | None = None


# ==================== CREDENTIAL SCHEMAS ====================


class IntegrationCredentialCreate(BaseModel):
    """Create credential via OAuth or PAT."""

    provider: IntegrationProvider
    credential_type: CredentialType = CredentialType.OAUTH_TOKEN

    # For OAuth flow
    oauth_code: str | None = None
    oauth_state: str | None = None

    # For PAT
    token: str | None = None
    scopes: list[str] | None = None

    # Metadata
    provider_metadata: dict[str, object] | None = None


class IntegrationCredentialUpdate(BaseModel):
    """Update credential."""

    scopes: list[str] | None = None
    provider_metadata: dict[str, object] | None = None


class IntegrationCredentialResponse(BaseModel):
    """Credential response (no token included)."""

    id: str
    project_id: str | None = None
    provider: IntegrationProvider
    credential_type: CredentialType
    status: CredentialStatus
    scopes: list[str]
    provider_metadata: dict[str, object]
    provider_user_id: str | None = None
    last_validated_at: datetime | None = None
    validation_error: str | None = None
    token_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IntegrationCredentialList(BaseModel):
    """List of credentials."""

    credentials: list[IntegrationCredentialResponse]
    total: int


class CredentialValidationResult(BaseModel):
    """Result of credential validation."""

    valid: bool
    message: str | None = None
    user_info: dict[str, object] | None = None
    scopes: list[str] | None = None


# ==================== MAPPING SCHEMAS ====================


class IntegrationMappingCreate(BaseModel):
    """Create a new mapping."""

    credential_id: str
    tracertm_item_id: str
    external_system: str = Field(description="Type of external item: github_issue, github_pr, linear_issue, etc.")
    external_id: str = Field(description="External system ID like 'owner/repo#42' or 'LINEAR-123'")
    external_url: str | None = None
    mapping_metadata: dict[str, object] | None = None
    direction: MappingDirection = MappingDirection.BIDIRECTIONAL
    auto_sync: bool = True
    conflict_resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MANUAL
    field_resolution_rules: dict[str, str] | None = None


class IntegrationMappingUpdate(BaseModel):
    """Update mapping."""

    direction: MappingDirection | None = None
    auto_sync: bool | None = None
    status: MappingStatus | None = None
    conflict_resolution_strategy: ConflictResolutionStrategy | None = None
    field_resolution_rules: dict[str, str] | None = None
    mapping_metadata: dict[str, object] | None = None


class IntegrationMappingResponse(BaseModel):
    """Mapping response."""

    id: str
    project_id: str
    credential_id: str
    tracertm_item_id: str
    tracertm_item_type: str
    external_system: str
    external_id: str
    external_url: str
    mapping_metadata: dict[str, object]
    direction: MappingDirection
    status: MappingStatus
    auto_sync: bool
    conflict_resolution_strategy: ConflictResolutionStrategy
    last_sync_at: datetime | None = None
    last_sync_direction: str | None = None
    sync_error_message: str | None = None
    consecutive_failures: int = 0
    last_conflict_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IntegrationMappingList(BaseModel):
    """List of mappings."""

    mappings: list[IntegrationMappingResponse]
    total: int


# ==================== SYNC QUEUE SCHEMAS ====================


class SyncQueueItemResponse(BaseModel):
    """Item in sync queue."""

    id: str
    mapping_id: str
    event_type: SyncEventType
    direction: SyncDirection
    priority: str
    status: SyncQueueStatus
    attempts: int
    max_attempts: int
    error_message: str | None = None
    error_code: str | None = None
    next_retry_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    processing_time_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncQueueList(BaseModel):
    """List of sync queue items."""

    items: list[SyncQueueItemResponse]
    total: int


class TriggerSyncRequest(BaseModel):
    """Request to trigger manual sync."""

    direction: SyncDirection | None = None
    force: bool = False


class TriggerSyncResponse(BaseModel):
    """Response from manual sync trigger."""

    queue_id: str
    mapping_id: str
    status: str
    message: str


# ==================== SYNC STATUS SCHEMAS ====================


class SyncStatusSummary(BaseModel):
    """Overall sync status summary."""

    total_mappings: int
    active_mappings: int
    paused_mappings: int
    error_mappings: int
    pending_syncs: int
    processing_syncs: int
    failed_syncs: int
    last_sync_at: datetime | None = None
    last_poll_at: datetime | None = None


class SyncStatusResponse(BaseModel):
    """Detailed sync status response."""

    summary: SyncStatusSummary
    queue: list[SyncQueueItemResponse]
    recent_failures: list[SyncQueueItemResponse]


# ==================== SYNC LOG SCHEMAS ====================


class SyncLogResponse(BaseModel):
    """Sync log entry response."""

    id: str
    mapping_id: str
    sync_queue_id: str | None = None
    operation: str
    direction: SyncDirection
    source_system: str
    source_id: str
    target_system: str
    target_id: str
    changes: dict[str, object]
    success: bool
    error_message: str | None = None
    sync_metadata: dict[str, object]
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncLogList(BaseModel):
    """List of sync logs."""

    logs: list[SyncLogResponse]
    total: int


# ==================== CONFLICT SCHEMAS ====================


class SyncConflictResponse(BaseModel):
    """Detected sync conflict."""

    id: str
    mapping_id: str
    field: str
    tracertm_value: str | None = None
    external_value: str | None = None
    resolution_status: ConflictResolutionStatus
    resolved_value: str | None = None
    resolution_strategy_used: str | None = None
    detected_at: datetime
    resolved_at: datetime | None = None

    model_config = {"from_attributes": True}


class SyncConflictList(BaseModel):
    """List of conflicts."""

    conflicts: list[SyncConflictResponse]
    total: int


class ConflictResolutionRequest(BaseModel):
    """Resolve conflict."""

    resolution: str = Field(description="Value to use: 'tracertm' or 'external' or actual value")
    notes: str | None = None


class ConflictResolutionResponse(BaseModel):
    """Conflict resolution response."""

    conflict_id: str
    resolved: bool
    resolved_value: str
    strategy_used: str


# ==================== EXTERNAL ITEM SCHEMAS ====================


class ExternalItemSearchRequest(BaseModel):
    """Search for external items."""

    credential_id: str
    query: str
    system: str | None = None  # github_issues, github_prs, linear_issues
    limit: int = 20


class GitHubRepo(BaseModel):
    """GitHub repository info."""

    id: int
    name: str
    full_name: str
    description: str | None = None
    html_url: str
    private: bool
    default_branch: str


class GitHubIssue(BaseModel):
    """GitHub issue info."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: str
    html_url: str
    labels: list[str]
    assignees: list[str]
    created_at: datetime
    updated_at: datetime


class GitHubPullRequest(BaseModel):
    """GitHub pull request info."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: str
    html_url: str
    head_ref: str
    base_ref: str
    draft: bool
    merged: bool
    created_at: datetime
    updated_at: datetime


class LinearIssue(BaseModel):
    """Linear issue info."""

    id: str
    identifier: str  # e.g., "LINEAR-123"
    title: str
    description: str | None = None
    state: str
    url: str
    priority: int
    assignee: str | None = None
    team_key: str
    created_at: datetime
    updated_at: datetime


class LinearTeam(BaseModel):
    """Linear team info."""

    id: str
    name: str
    key: str
    description: str | None = None


class ExternalItemSearchResponse(BaseModel):
    """External item search results."""

    items: list[dict[str, object]]
    total: int
    system: str


# ==================== GITHUB REPOS/DISCOVERY ====================


class GitHubRepoList(BaseModel):
    """List of GitHub repositories."""

    repos: list[GitHubRepo]
    total: int


class LinearTeamList(BaseModel):
    """List of Linear teams."""

    teams: list[LinearTeam]
    total: int


# ==================== STATISTICS SCHEMAS ====================


class IntegrationStats(BaseModel):
    """Integration statistics for a project."""

    total_credentials: int
    active_credentials: int
    total_mappings: int
    active_mappings: int
    total_syncs_24h: int
    successful_syncs_24h: int
    failed_syncs_24h: int
    pending_conflicts: int
    by_provider: dict[str, int]
    by_external_system: dict[str, int]
