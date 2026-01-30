"""Pydantic schemas for external integrations."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


# ==================== ENUMS ====================


class IntegrationProvider(str, Enum):
    """Supported external integration providers."""

    GITHUB = "github"
    GITHUB_PROJECTS = "github_projects"
    LINEAR = "linear"


class CredentialType(str, Enum):
    """Type of credential stored."""

    OAUTH_TOKEN = "oauth_token"
    PAT = "personal_access_token"
    GITHUB_APP = "github_app"


class CredentialStatus(str, Enum):
    """Status of a credential."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"


class MappingDirection(str, Enum):
    """Sync direction for mappings."""

    BIDIRECTIONAL = "bidirectional"
    TRACERTM_TO_EXTERNAL = "tracertm_to_external"
    EXTERNAL_TO_TRACERTM = "external_to_tracertm"


class MappingStatus(str, Enum):
    """Status of a mapping."""

    ACTIVE = "active"
    PAUSED = "paused"
    SYNC_ERROR = "sync_error"


class ConflictResolutionStrategy(str, Enum):
    """Conflict resolution strategy."""

    MANUAL = "manual"
    TRACERTM_WINS = "tracertm_wins"
    EXTERNAL_WINS = "external_wins"
    LAST_WRITE_WINS = "last_write_wins"


class SyncEventType(str, Enum):
    """Types of sync events."""

    ITEM_CREATED = "item_created"
    ITEM_UPDATED = "item_updated"
    ITEM_DELETED = "item_deleted"
    STATUS_CHANGED = "status_changed"
    LINKED = "linked"
    UNLINKED = "unlinked"


class SyncDirection(str, Enum):
    """Direction of sync."""

    PUSH = "push"
    PULL = "pull"


class SyncQueueStatus(str, Enum):
    """Status of sync queue item."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRIED = "retried"


class ConflictResolutionStatus(str, Enum):
    """Status of conflict resolution."""

    PENDING = "pending"
    RESOLVED = "resolved"
    IGNORED = "ignored"


# ==================== OAUTH SCHEMAS ====================


class OAuthStartRequest(BaseModel):
    """Request to start OAuth flow."""

    provider: IntegrationProvider
    scopes: Optional[list[str]] = None


class OAuthStartResponse(BaseModel):
    """Response with OAuth redirect URL."""

    oauth_url: str
    state: str


class OAuthCallbackRequest(BaseModel):
    """Receive OAuth callback."""

    code: str
    state: str
    error: Optional[str] = None
    error_description: Optional[str] = None


# ==================== CREDENTIAL SCHEMAS ====================


class IntegrationCredentialCreate(BaseModel):
    """Create credential via OAuth or PAT."""

    provider: IntegrationProvider
    credential_type: CredentialType = CredentialType.OAUTH_TOKEN

    # For OAuth flow
    oauth_code: Optional[str] = None
    oauth_state: Optional[str] = None

    # For PAT
    token: Optional[str] = None
    scopes: Optional[list[str]] = None

    # Metadata
    provider_metadata: Optional[dict[str, Any]] = None


class IntegrationCredentialUpdate(BaseModel):
    """Update credential."""

    scopes: Optional[list[str]] = None
    provider_metadata: Optional[dict[str, Any]] = None


class IntegrationCredentialResponse(BaseModel):
    """Credential response (no token included)."""

    id: str
    project_id: Optional[str] = None
    provider: IntegrationProvider
    credential_type: CredentialType
    status: CredentialStatus
    scopes: list[str]
    provider_metadata: dict[str, Any]
    provider_user_id: Optional[str] = None
    last_validated_at: Optional[datetime] = None
    validation_error: Optional[str] = None
    token_expires_at: Optional[datetime] = None
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
    message: Optional[str] = None
    user_info: Optional[dict[str, Any]] = None
    scopes: Optional[list[str]] = None


# ==================== MAPPING SCHEMAS ====================


class IntegrationMappingCreate(BaseModel):
    """Create a new mapping."""

    credential_id: str
    tracertm_item_id: str
    external_system: str = Field(
        description="Type of external item: github_issue, github_pr, linear_issue, etc."
    )
    external_id: str = Field(description="External system ID like 'owner/repo#42' or 'LINEAR-123'")
    external_url: Optional[str] = None
    mapping_metadata: Optional[dict[str, Any]] = None
    direction: MappingDirection = MappingDirection.BIDIRECTIONAL
    auto_sync: bool = True
    conflict_resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MANUAL
    field_resolution_rules: Optional[dict[str, str]] = None


class IntegrationMappingUpdate(BaseModel):
    """Update mapping."""

    direction: Optional[MappingDirection] = None
    auto_sync: Optional[bool] = None
    status: Optional[MappingStatus] = None
    conflict_resolution_strategy: Optional[ConflictResolutionStrategy] = None
    field_resolution_rules: Optional[dict[str, str]] = None
    mapping_metadata: Optional[dict[str, Any]] = None


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
    mapping_metadata: dict[str, Any]
    direction: MappingDirection
    status: MappingStatus
    auto_sync: bool
    conflict_resolution_strategy: ConflictResolutionStrategy
    last_sync_at: Optional[datetime] = None
    last_sync_direction: Optional[str] = None
    sync_error_message: Optional[str] = None
    consecutive_failures: int = 0
    last_conflict_at: Optional[datetime] = None
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
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    next_retry_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncQueueList(BaseModel):
    """List of sync queue items."""

    items: list[SyncQueueItemResponse]
    total: int


class TriggerSyncRequest(BaseModel):
    """Request to trigger manual sync."""

    direction: Optional[SyncDirection] = None
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
    last_sync_at: Optional[datetime] = None
    last_poll_at: Optional[datetime] = None


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
    sync_queue_id: Optional[str] = None
    operation: str
    direction: SyncDirection
    source_system: str
    source_id: str
    target_system: str
    target_id: str
    changes: dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    sync_metadata: dict[str, Any]
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
    tracertm_value: Optional[str] = None
    external_value: Optional[str] = None
    resolution_status: ConflictResolutionStatus
    resolved_value: Optional[str] = None
    resolution_strategy_used: Optional[str] = None
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SyncConflictList(BaseModel):
    """List of conflicts."""

    conflicts: list[SyncConflictResponse]
    total: int


class ConflictResolutionRequest(BaseModel):
    """Resolve conflict."""

    resolution: str = Field(description="Value to use: 'tracertm' or 'external' or actual value")
    notes: Optional[str] = None


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
    system: Optional[str] = None  # github_issues, github_prs, linear_issues
    limit: int = 20


class GitHubRepo(BaseModel):
    """GitHub repository info."""

    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    private: bool
    default_branch: str


class GitHubIssue(BaseModel):
    """GitHub issue info."""

    id: int
    number: int
    title: str
    body: Optional[str] = None
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
    body: Optional[str] = None
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
    description: Optional[str] = None
    state: str
    url: str
    priority: int
    assignee: Optional[str] = None
    team_key: str
    created_at: datetime
    updated_at: datetime


class LinearTeam(BaseModel):
    """Linear team info."""

    id: str
    name: str
    key: str
    description: Optional[str] = None


class ExternalItemSearchResponse(BaseModel):
    """External item search results."""

    items: list[dict[str, Any]]
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
