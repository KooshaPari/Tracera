# External Integrations Implementation Plan - TraceRTM

## Executive Summary

This document provides a comprehensive implementation plan for adding three critical external integrations to TraceRTM:

1. **GitHub Integration** - Link commits, pull requests, and branches to requirements and features
2. **GitHub Projects Integration** - Two-way sync with GitHub Project boards
3. **Linear Integration** - Two-way sync with Linear issues

The plan follows a phased approach with production-ready patterns, comprehensive security considerations, and conflict resolution strategies. Total estimated effort: **8-12 weeks** for full implementation with testing and documentation.

### Key Objectives

- Enable bidirectional traceability between TraceRTM items and external platforms
- Maintain data consistency across systems with intelligent conflict resolution
- Provide real-time synchronization through webhooks with polling fallback
- Ensure secure credential storage and authentication
- Support both OAuth and personal access token (PAT) authentication methods
- Create intuitive UI for setup, configuration, and monitoring

---

## Part 1: Authentication Architecture

### 1.1 Authentication Approaches Analysis

#### Option A: OAuth 2.0 Apps (Recommended for GitHub/Linear)

**Advantages:**
- No need for users to share personal credentials
- Fine-grained permission scoping
- Easy permission revocation
- Support for organization-level integrations
- Better audit trails

**Disadvantages:**
- Requires registering apps with each platform
- More complex setup process
- Needs callback URL for OAuth flow

**Use Case:** Primary approach for GitHub and Linear - provides enterprise-grade security.

#### Option B: Personal Access Tokens (PAT)

**Advantages:**
- Simple setup - users generate tokens in their account
- No OAuth callback infrastructure needed
- Works for both GitHub and Linear
- User maintains full control

**Disadvantages:**
- Users share long-lived credentials
- Harder to rotate securely
- Less granular permission scoping

**Use Case:** Secondary option for users who prefer simplicity or have OAuth restrictions.

#### Option C: GitHub Apps

**Advantages:**
- Can be installed at organization level
- Supports webhook events automatically
- Better for organization-wide deployments
- Can request only needed permissions

**Disadvantages:**
- More complex setup
- Requires app approval process
- Higher learning curve

**Use Case:** Recommended for enterprise deployments and organization-wide features.

### 1.2 Recommended Authentication Strategy

**Primary Flow:**
1. OAuth 2.0 for GitHub (with GitHub Apps alternative)
2. OAuth 2.0 for Linear
3. PAT as fallback/alternative option

**Storage Security:**
- Encrypt credentials using industry-standard encryption (AES-256)
- Store encrypted credentials in database with distinct encryption keys
- Implement credential rotation with grace periods
- Use environment variables for encryption master key
- Implement secure deletion on integration removal

---

## Part 2: Data Models

### 2.1 New Database Models

#### Integration Credential Model

```python
# src/tracertm/models/integration_credential.py

class IntegrationProvider(str, Enum):
    """Supported external integration providers."""
    GITHUB = "github"
    GITHUB_PROJECTS = "github_projects"
    LINEAR = "linear"

class CredentialType(str, Enum):
    """Type of credential stored."""
    OAUTH_TOKEN = "oauth_token"
    PAT = "personal_access_token"
    GITHUB_APP_INSTALLATION = "github_app_installation"

class IntegrationCredential(Base, TimestampMixin):
    """Secure storage of external integration credentials."""

    __tablename__ = "integration_credentials"

    id: str = UUID primary key
    project_id: str = FK to projects

    # Credential metadata
    provider: IntegrationProvider
    credential_type: CredentialType
    user_id: str (who setup this integration)

    # Authentication details
    encrypted_token: str (AES-256 encrypted)
    token_expires_at: Optional[datetime]
    refresh_token: Optional[str] (encrypted)

    # OAuth scope tracking
    scopes: list[str] (JSON)

    # Credential metadata for provider-specific info
    provider_metadata: dict (JSON)
        - For GitHub: installation_id, app_id, user_login, org_login
        - For Linear: team_id, workspace_id

    # Status tracking
    status: "active" | "expired" | "revoked" | "invalid"
    last_validated_at: Optional[datetime]
    validation_error: Optional[str]

    # Rotation tracking
    created_by_user_id: str
    rotated_at: Optional[datetime]
    rotation_required_at: Optional[datetime]

    version: int (optimistic locking)
    __table_args__ = (
        Index("ix_integration_credentials_project_provider", "project_id", "provider"),
        Index("ix_integration_credentials_status", "status"),
        Index("ix_integration_credentials_expires", "token_expires_at"),
    )
```

#### Integration Mapping Model

```python
# src/tracertm/models/integration_mapping.py

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

class IntegrationMapping(Base, TimestampMixin):
    """Maps TraceRTM items to external system identifiers."""

    __tablename__ = "integration_mappings"

    id: str = UUID primary key
    project_id: str = FK to projects
    integration_credential_id: str = FK to integration_credentials

    # TraceRTM side
    tracertm_item_id: str = FK to items
    tracertm_item_type: str ("requirement", "feature", "epic", "test")

    # External side
    external_system: str (github_issue, github_pr, linear_issue, etc.)
    external_id: str (e.g., "octocat/repo#123" for GitHub)
    external_url: str

    # Mapping metadata
    mapping_metadata: dict (JSON)
        - For GitHub Issues: repo, issue_number, labels
        - For GitHub PRs: repo, pr_number, branch
        - For Linear: team_key, issue_id

    # Sync configuration
    direction: MappingDirection
    status: MappingStatus
    auto_sync: bool (default: true)

    # Sync tracking
    last_sync_at: Optional[datetime]
    last_sync_direction: Optional[str]
    sync_error_message: Optional[str]
    consecutive_failures: int

    # Conflict tracking
    last_conflict_at: Optional[datetime]
    conflict_resolution_strategy: str ("manual" | "tracertm_wins" | "external_wins")

    version: int
    __table_args__ = (
        Index("ix_integration_mappings_credential", "integration_credential_id"),
        Index("ix_integration_mappings_item", "tracertm_item_id"),
        Index("ix_integration_mappings_external", "external_id"),
        Index("ix_integration_mappings_status", "status"),
    )
```

#### Integration Sync Queue Model

```python
# src/tracertm/models/integration_sync_queue.py

class SyncEvent(str, Enum):
    """Types of sync events."""
    ITEM_CREATED = "item_created"
    ITEM_UPDATED = "item_updated"
    ITEM_DELETED = "item_deleted"
    STATUS_CHANGED = "status_changed"
    LINKED = "linked"
    UNLINKED = "unlinked"

class SyncDirection(str, Enum):
    """Direction of sync."""
    PUSH = "push"  # TraceRTM -> External
    PULL = "pull"  # External -> TraceRTM

class SyncPriority(str, Enum):
    """Priority of sync event."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class IntegrationSyncQueue(Base, TimestampMixin):
    """Queue for pending sync operations."""

    __tablename__ = "integration_sync_queue"

    id: str = UUID primary key
    integration_credential_id: str = FK to integration_credentials
    mapping_id: str = FK to integration_mappings

    # Event details
    event_type: SyncEvent
    direction: SyncDirection
    priority: SyncPriority

    # Payload
    payload: dict (JSON) - The data to sync

    # Processing state
    status: "pending" | "processing" | "completed" | "failed" | "retried"
    attempts: int
    max_attempts: int = 3
    next_retry_at: Optional[datetime]

    # Error tracking
    error_message: Optional[str]
    error_code: Optional[str]

    # Idempotency
    idempotency_key: Optional[str]

    # Processing tracking
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    processing_time_ms: Optional[int]

    __table_args__ = (
        Index("ix_sync_queue_credential_status", "integration_credential_id", "status"),
        Index("ix_sync_queue_mapping", "mapping_id"),
        Index("ix_sync_queue_priority_status", "priority", "status"),
        Index("ix_sync_queue_retry", "status", "next_retry_at"),
    )
```

#### Integration Sync Log Model

```python
# src/tracertm/models/integration_sync_log.py

class IntegrationSyncLog(Base):
    """Audit log for all sync operations."""

    __tablename__ = "integration_sync_logs"

    id: str = UUID primary key
    sync_queue_id: str = FK to integration_sync_queue
    mapping_id: str = FK to integration_mappings

    # Operation details
    operation: str (create, update, delete, link, unlink)
    direction: SyncDirection

    # Source and target
    source_system: str
    source_id: str
    target_system: str
    target_id: str

    # Changes
    changes: dict (JSON)
        - before: dict of previous values
        - after: dict of new values
        - fields_changed: list of field names

    # Result
    success: bool
    error_message: Optional[str]

    # Metadata
    sync_metadata: dict (JSON)
        - triggered_by: "webhook" | "polling" | "manual"
        - user_id: Optional[str] (if manual)
        - conflict_detected: bool
        - conflict_resolution_used: Optional[str]

    created_at: datetime
    __table_args__ = (
        Index("ix_sync_log_mapping", "mapping_id"),
        Index("ix_sync_log_queue", "sync_queue_id"),
        Index("ix_sync_log_success", "success"),
        Index("ix_sync_log_created", "created_at"),
    )
```

### 2.2 Extended Webhook Integration Model

Update existing `WebhookIntegration` model to support external integration webhooks:

```python
# Extend WebhookIntegration in src/tracertm/models/webhook_integration.py

class ExternalWebhookEventType(str, Enum):
    """Events from external systems."""
    GITHUB_PUSH = "github_push"
    GITHUB_PULL_REQUEST = "github_pull_request"
    GITHUB_ISSUES = "github_issues"
    GITHUB_PROJECTS = "github_projects"
    LINEAR_ISSUE_UPDATED = "linear_issue_updated"
    LINEAR_PROJECT_UPDATED = "linear_project_updated"
    # ... others

# Add to WebhookIntegration fields:
external_event_types: Optional[list[ExternalWebhookEventType]]
github_webhook_id: Optional[str]  # GitHub webhook ID for cleanup
linear_webhook_id: Optional[str]   # Linear webhook ID for cleanup
```

---

## Part 3: Data Sync Strategies

### 3.1 Real-Time Webhook-Based Sync

#### GitHub Webhooks

**Setup Flow:**
1. User authorizes TraceRTM via OAuth or provides PAT
2. System registers webhook for subscribed events
3. GitHub sends events to TraceRTM webhook endpoint
4. TraceRTM processes and queues sync operations

**Subscribed Events:**
```yaml
GitHub Events:
  Push:
    - Triggered when code is pushed
    - Creates/updates commit-linked items
    - Fields: commit SHA, branch, author, message

  Pull Request:
    - opened, synchronize, closed, reopened
    - Links PR to requirements/features via mapping
    - Syncs PR status to mapped external system

  Issues:
    - opened, edited, closed, reopened, labeled
    - Creates/updates mappings for issue tracking

  Projects (v2):
    - item_added, item_updated, item_removed
    - Syncs project board changes
```

**Webhook Signature Verification:**
```python
# Use HMAC-SHA256 for GitHub webhooks
# Header: X-Hub-Signature-256: sha256=<signature>

import hmac
import hashlib

def verify_github_webhook(payload_bytes: bytes, secret: str, signature_header: str) -> bool:
    """Verify GitHub webhook signature."""
    computed_signature = "sha256=" + hmac.new(
        secret.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_signature, signature_header)
```

#### Linear Webhooks

**Setup Flow:**
Similar to GitHub but simpler - Linear webhooks require:
1. API key authentication
2. Webhook URL registration in Linear workspace
3. Event subscriptions

**Subscribed Events:**
```yaml
Linear Events:
  Issue:
    - created, updated, removed
    - Syncs issue state, assignee, priority

  Comment:
    - created, updated, removed
    - For future: sync comments as notes

  Project:
    - updated (for shared projects)
    - Syncs project status
```

**Signature Verification:**
```python
# Linear uses HMAC-SHA256 with header "Linear-Signature"

def verify_linear_webhook(payload_bytes: bytes, secret: str, signature_header: str) -> bool:
    """Verify Linear webhook signature."""
    computed_signature = hmac.new(
        secret.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_signature, signature_header)
```

### 3.2 Polling Fallback Strategy

For missed webhooks or initial sync:

```python
# src/tracertm/services/integration_polling_service.py

class IntegrationPollingService:
    """Periodically poll external systems for changes."""

    async def poll_github_repositories(self, credential: IntegrationCredential):
        """
        Poll GitHub for:
        - New/updated commits
        - PR changes
        - Issue status changes
        """
        pass

    async def poll_linear_workspace(self, credential: IntegrationCredential):
        """
        Poll Linear workspace for:
        - New/updated issues
        - Status changes
        - Assignment changes
        """
        pass

    # Run on schedule (every 5-15 minutes)
    # Only check items modified since last poll
    # Use cursor-based pagination for efficiency
```

**Polling Configuration:**
- Interval: 5 minutes for high-priority workspaces, 15 minutes for others
- Track last poll timestamp per integration
- Use cursor-based pagination to avoid redundant checks
- Implement exponential backoff for failed polls

### 3.3 Conflict Resolution Strategy

**Conflict Detection:**

```python
# src/tracertm/services/integration_conflict_service.py

class ConflictDetectionStrategy:
    """Detect and resolve sync conflicts."""

    async def detect_conflict(
        self,
        mapping: IntegrationMapping,
        tracertm_state: dict,
        external_state: dict
    ) -> Optional[SyncConflict]:
        """
        Detect if states diverged.

        Conflict scenarios:
        1. Both systems modified same field independently
        2. Delete vs. Update conflict
        3. Status progression conflict (incompatible workflows)
        """
        pass
```

**Conflict Resolution Strategies:**

1. **Last-Writer-Wins (Default for non-critical fields)**
   - Check modification timestamps
   - Accept changes from system with newer timestamp
   - Log conflict for user review

2. **TraceRTM Priority (Configuration Option)**
   - TraceRTM state always wins
   - Useful for requirements management focus
   - External system state is overwritten

3. **External System Priority (Configuration Option)**
   - External state always wins
   - Useful for GitHub/Linear as source of truth
   - TraceRTM state is updated

4. **Manual Resolution (Default for critical fields)**
   - Flag conflict for user review
   - Block sync until user chooses winner
   - Log detailed conflict information

**Configuration:**

```python
# In IntegrationMapping

conflict_resolution_strategy: str = Field(
    default="manual",
    description="Strategy for resolving conflicts",
    enum=["manual", "tracertm_wins", "external_wins", "last_write_wins"]
)

# Per-field resolution rules
field_resolution_rules: dict = Field(
    default={},
    description="Per-field resolution strategies"
    example={
        "status": "external_wins",  # Always trust external status
        "description": "last_write_wins",
        "priority": "tracertm_wins"  # Prioritize tracer requirements
    }
)
```

---

## Part 4: API Endpoint Design

### 4.1 Integration Credential Endpoints

```
POST   /api/v1/projects/{project_id}/integrations/credentials
       Create new integration credential (OAuth redirect or PAT)

GET    /api/v1/projects/{project_id}/integrations/credentials
       List all credentials for project

GET    /api/v1/projects/{project_id}/integrations/credentials/{credential_id}
       Get specific credential (metadata only, not token)

PUT    /api/v1/projects/{project_id}/integrations/credentials/{credential_id}
       Update credential (rotate token, change scopes)

DELETE /api/v1/projects/{project_id}/integrations/credentials/{credential_id}
       Revoke credential

POST   /api/v1/projects/{project_id}/integrations/credentials/{credential_id}/validate
       Test credential validity

POST   /api/v1/projects/{project_id}/integrations/oauth/callback
       OAuth callback handler (GitHub, Linear)

POST   /api/v1/projects/{project_id}/integrations/oauth/{provider}/start
       Initiate OAuth flow
```

### 4.2 Integration Mapping Endpoints

```
POST   /api/v1/projects/{project_id}/integrations/mappings
       Create mapping between TraceRTM item and external item

GET    /api/v1/projects/{project_id}/integrations/mappings
       List all mappings (with filtering options)

GET    /api/v1/projects/{project_id}/integrations/mappings/{mapping_id}
       Get specific mapping

PUT    /api/v1/projects/{project_id}/integrations/mappings/{mapping_id}
       Update mapping (direction, strategy, sync settings)

DELETE /api/v1/projects/{project_id}/integrations/mappings/{mapping_id}
       Remove mapping

GET    /api/v1/projects/{project_id}/integrations/mappings/search
       Search for mappings (query by external ID, item ID, etc.)

POST   /api/v1/projects/{project_id}/integrations/mappings/{mapping_id}/sync
       Trigger manual sync for specific mapping
```

### 4.3 External System Discovery Endpoints

```
GET    /api/v1/projects/{project_id}/integrations/github/repos
       List available GitHub repos for authenticated user

GET    /api/v1/projects/{project_id}/integrations/github/repos/{owner}/{repo}/issues
       List GitHub issues for searching/mapping

GET    /api/v1/projects/{project_id}/integrations/github/repos/{owner}/{repo}/pulls
       List GitHub PRs

GET    /api/v1/projects/{project_id}/integrations/linear/issues
       List Linear issues in workspace

GET    /api/v1/projects/{project_id}/integrations/linear/teams
       List Linear teams for organization selection
```

### 4.4 Sync Control Endpoints

```
GET    /api/v1/projects/{project_id}/integrations/sync-status
       Get overall sync status and statistics

GET    /api/v1/projects/{project_id}/integrations/sync-queue
       Get pending sync operations

POST   /api/v1/projects/{project_id}/integrations/sync-queue/{queue_id}/retry
       Retry failed sync operation

DELETE /api/v1/projects/{project_id}/integrations/sync-queue/{queue_id}
       Cancel pending sync operation

GET    /api/v1/projects/{project_id}/integrations/sync-logs
       Get paginated sync operation logs

POST   /api/v1/projects/{project_id}/integrations/conflicts
       List detected conflicts

POST   /api/v1/projects/{project_id}/integrations/conflicts/{conflict_id}/resolve
       Manually resolve conflict
```

### 4.5 Webhook Endpoint

```
POST   /api/v1/webhooks/github
       Receive GitHub webhook events
       Header: X-Hub-Signature-256

POST   /api/v1/webhooks/linear
       Receive Linear webhook events
       Header: Linear-Signature
```

### 4.6 Request/Response Examples

#### Create Integration Credential (OAuth)

```json
POST /api/v1/projects/proj-123/integrations/credentials

{
  "provider": "github",
  "credential_type": "oauth_token",
  "oauth_code": "gho_16C7e42F292c6912E7...",
  "redirect_uri": "https://tracertm.com/integrations/callback"
}

Response 201:
{
  "id": "cred-123",
  "project_id": "proj-123",
  "provider": "github",
  "credential_type": "oauth_token",
  "status": "active",
  "scopes": ["repo", "read:org", "read:user"],
  "provider_metadata": {
    "user_login": "octocat",
    "org_login": "github",
    "installation_id": "12345"
  },
  "last_validated_at": "2025-01-27T10:00:00Z",
  "created_at": "2025-01-27T10:00:00Z"
}
```

#### Create Mapping

```json
POST /api/v1/projects/proj-123/integrations/mappings

{
  "tracertm_item_id": "item-456",
  "credential_id": "cred-123",
  "external_system": "github_issue",
  "external_id": "octocat/repo#42",
  "direction": "bidirectional",
  "conflict_resolution_strategy": "manual",
  "field_resolution_rules": {
    "status": "external_wins",
    "priority": "tracertm_wins"
  }
}

Response 201:
{
  "id": "map-789",
  "tracertm_item_id": "item-456",
  "external_id": "octocat/repo#42",
  "external_url": "https://github.com/octocat/repo/issues/42",
  "status": "active",
  "direction": "bidirectional",
  "last_sync_at": null,
  "created_at": "2025-01-27T10:00:00Z"
}
```

#### Webhook Event (GitHub)

```json
POST /api/v1/webhooks/github

Headers:
  X-GitHub-Event: pull_request
  X-Hub-Signature-256: sha256=abc123def456...

{
  "action": "opened",
  "pull_request": {
    "id": 1,
    "number": 42,
    "title": "Implement new feature",
    "body": "Closes #10",
    "state": "open",
    "head": {
      "ref": "feature-branch",
      "sha": "abc123..."
    },
    "user": {
      "login": "octocat"
    }
  },
  "repository": {
    "full_name": "octocat/repo"
  }
}

Response 200:
{
  "success": true,
  "processed_mappings": 1,
  "synced_items": ["item-456"]
}
```

---

## Part 5: Data Models - Detailed Schema

### 5.1 Pydantic Schemas

#### Integration Credential Schemas

```python
# src/tracertm/schemas/integration.py

from datetime import datetime
from typing import Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl

class IntegrationProvider(str, Enum):
    GITHUB = "github"
    GITHUB_PROJECTS = "github_projects"
    LINEAR = "linear"

class CredentialType(str, Enum):
    OAUTH_TOKEN = "oauth_token"
    PAT = "personal_access_token"
    GITHUB_APP = "github_app"

class CredentialStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"

# OAuth Request/Response

class OAuthStartRequest(BaseModel):
    """Request to start OAuth flow."""
    provider: IntegrationProvider
    scopes: Optional[list[str]] = None

class OAuthCallbackRequest(BaseModel):
    """Receive OAuth callback."""
    code: str
    state: str
    error: Optional[str] = None

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

class IntegrationCredentialResponse(BaseModel):
    """Credential response (no token included)."""
    id: str
    project_id: str
    provider: IntegrationProvider
    credential_type: CredentialType
    status: CredentialStatus
    scopes: list[str]
    provider_metadata: dict[str, Any]
    last_validated_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}

class IntegrationCredentialList(BaseModel):
    """List of credentials."""
    credentials: list[IntegrationCredentialResponse]
    total: int

# Mapping Schemas

class MappingDirection(str, Enum):
    BIDIRECTIONAL = "bidirectional"
    TRACERTM_TO_EXTERNAL = "tracertm_to_external"
    EXTERNAL_TO_TRACERTM = "external_to_tracertm"

class ConflictResolutionStrategy(str, Enum):
    MANUAL = "manual"
    TRACERTM_WINS = "tracertm_wins"
    EXTERNAL_WINS = "external_wins"
    LAST_WRITE_WINS = "last_write_wins"

class IntegrationMappingCreate(BaseModel):
    """Create a new mapping."""
    credential_id: str
    tracertm_item_id: str
    external_system: str  # "github_issue", "github_pr", "linear_issue"
    external_id: str
    direction: MappingDirection = MappingDirection.BIDIRECTIONAL
    auto_sync: bool = True
    conflict_resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MANUAL
    field_resolution_rules: Optional[dict[str, str]] = None

class IntegrationMappingResponse(BaseModel):
    """Mapping response."""
    id: str
    project_id: str
    credential_id: str
    tracertm_item_id: str
    external_system: str
    external_id: str
    external_url: str
    direction: MappingDirection
    status: str
    auto_sync: bool
    last_sync_at: Optional[datetime]
    sync_error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

class IntegrationMappingUpdate(BaseModel):
    """Update mapping."""
    direction: Optional[MappingDirection] = None
    auto_sync: Optional[bool] = None
    conflict_resolution_strategy: Optional[ConflictResolutionStrategy] = None
    field_resolution_rules: Optional[dict[str, str]] = None

# Sync Status

class SyncQueueItem(BaseModel):
    """Item in sync queue."""
    id: str
    mapping_id: str
    event_type: str
    direction: str
    status: str
    attempts: int
    max_attempts: int
    error_message: Optional[str]
    created_at: datetime

class SyncStatus(BaseModel):
    """Overall sync status."""
    total_mappings: int
    synced_mappings: int
    pending_syncs: int
    failed_syncs: int
    queue: list[SyncQueueItem]
    last_poll_at: Optional[datetime]

# Conflict Resolution

class SyncConflict(BaseModel):
    """Detected sync conflict."""
    id: str
    mapping_id: str
    field: str
    tracertm_value: Any
    external_value: Any
    conflict_detected_at: datetime

class ConflictResolution(BaseModel):
    """Resolve conflict."""
    conflict_id: str
    resolution: str  # "tracertm_value" or "external_value"
    notes: Optional[str] = None
```

---

## Part 6: Backend Implementation Structure

### 6.1 Repository Layer

```python
# src/tracertm/repositories/integration_credential_repository.py

class IntegrationCredentialRepository(BaseRepository):
    """Repository for integration credentials."""

    async def create(self, project_id: str, credential_data: dict) -> IntegrationCredential:
        """Create new credential with encryption."""
        pass

    async def get_by_id(self, credential_id: str) -> Optional[IntegrationCredential]:
        """Get credential by ID."""
        pass

    async def get_by_project_and_provider(
        self,
        project_id: str,
        provider: str
    ) -> list[IntegrationCredential]:
        """Get all credentials for provider."""
        pass

    async def update_token(self, credential_id: str, new_token: str):
        """Update encrypted token."""
        pass

    async def validate_credential(self, credential_id: str) -> bool:
        """Validate credential is still valid."""
        pass

    async def revoke(self, credential_id: str):
        """Revoke credential."""
        pass

# src/tracertm/repositories/integration_mapping_repository.py

class IntegrationMappingRepository(BaseRepository):
    """Repository for item-to-external mappings."""

    async def create(self, mapping_data: dict) -> IntegrationMapping:
        """Create mapping."""
        pass

    async def get_by_tracertm_item(self, item_id: str) -> list[IntegrationMapping]:
        """Get all mappings for TraceRTM item."""
        pass

    async def get_by_external_id(self, external_id: str) -> Optional[IntegrationMapping]:
        """Find mapping by external ID."""
        pass

    async def list_by_credential(self, credential_id: str) -> list[IntegrationMapping]:
        """Get all mappings for credential."""
        pass

    async def update_sync_status(
        self,
        mapping_id: str,
        success: bool,
        error: Optional[str] = None
    ):
        """Update last sync status."""
        pass

# src/tracertm/repositories/integration_sync_queue_repository.py

class IntegrationSyncQueueRepository(BaseRepository):
    """Repository for sync queue."""

    async def enqueue(self, sync_event: dict) -> IntegrationSyncQueue:
        """Add item to sync queue."""
        pass

    async def get_pending(self, limit: int = 100) -> list[IntegrationSyncQueue]:
        """Get pending items."""
        pass

    async def get_retryable(self) -> list[IntegrationSyncQueue]:
        """Get items ready for retry."""
        pass

    async def mark_processing(self, queue_id: str):
        """Mark as processing."""
        pass

    async def mark_completed(self, queue_id: str, processing_time_ms: int):
        """Mark as completed."""
        pass

    async def mark_failed(self, queue_id: str, error: str):
        """Mark as failed with error."""
        pass

    async def reschedule_retry(self, queue_id: str, delay_seconds: int):
        """Schedule retry."""
        pass
```

### 6.2 Service Layer

```python
# src/tracertm/services/external_integration_service.py

class ExternalIntegrationService:
    """Orchestrate external integrations."""

    def __init__(
        self,
        credential_repo: IntegrationCredentialRepository,
        mapping_repo: IntegrationMappingRepository,
        sync_queue_repo: IntegrationSyncQueueRepository,
        github_client: GitHubClient,
        linear_client: LinearClient,
        encryption_service: EncryptionService,
    ):
        self.credential_repo = credential_repo
        self.mapping_repo = mapping_repo
        self.sync_queue_repo = sync_queue_repo
        self.github = github_client
        self.linear = linear_client
        self.encryption = encryption_service

    async def create_credential(
        self,
        project_id: str,
        provider: str,
        oauth_code: Optional[str] = None,
        token: Optional[str] = None
    ) -> IntegrationCredential:
        """Create new credential."""
        pass

    async def validate_credential(self, credential_id: str) -> bool:
        """Test credential validity."""
        pass

    async def create_mapping(
        self,
        mapping_data: IntegrationMappingCreate
    ) -> IntegrationMapping:
        """Create item mapping."""
        pass

    async def sync_mapping(self, mapping_id: str) -> SyncResult:
        """Trigger manual sync."""
        pass

# src/tracertm/services/github_integration_service.py

class GitHubIntegrationService:
    """GitHub-specific integration logic."""

    async def get_repositories(self, credential: IntegrationCredential) -> list[dict]:
        """List available repositories."""
        pass

    async def get_issues(
        self,
        credential: IntegrationCredential,
        repo: str
    ) -> list[dict]:
        """List issues in repository."""
        pass

    async def get_pull_requests(
        self,
        credential: IntegrationCredential,
        repo: str
    ) -> list[dict]:
        """List pull requests."""
        pass

    async def sync_item_to_github(
        self,
        mapping: IntegrationMapping,
        item: Item,
        credential: IntegrationCredential
    ) -> SyncResult:
        """Sync TraceRTM item to GitHub issue/PR."""
        pass

    async def sync_github_to_item(
        self,
        mapping: IntegrationMapping,
        github_item: dict,
        credential: IntegrationCredential
    ) -> SyncResult:
        """Sync GitHub issue/PR to TraceRTM item."""
        pass

    async def register_webhook(
        self,
        credential: IntegrationCredential,
        repo: str
    ) -> str:
        """Register webhook with GitHub."""
        pass

# src/tracertm/services/linear_integration_service.py

class LinearIntegrationService:
    """Linear-specific integration logic."""

    async def get_issues(
        self,
        credential: IntegrationCredential
    ) -> list[dict]:
        """List issues in workspace."""
        pass

    async def sync_item_to_linear(
        self,
        mapping: IntegrationMapping,
        item: Item,
        credential: IntegrationCredential
    ) -> SyncResult:
        """Sync TraceRTM item to Linear issue."""
        pass

    async def sync_linear_to_item(
        self,
        mapping: IntegrationMapping,
        linear_issue: dict,
        credential: IntegrationCredential
    ) -> SyncResult:
        """Sync Linear issue to TraceRTM item."""
        pass

# src/tracertm/services/integration_sync_processor_service.py

class IntegrationSyncProcessorService:
    """Process queued sync operations."""

    async def process_queue(self) -> ProcessingStats:
        """Process all pending sync items."""
        pass

    async def process_item(self, queue_item: IntegrationSyncQueue) -> bool:
        """Process single sync item."""
        pass

    async def handle_conflict(
        self,
        mapping: IntegrationMapping,
        conflict: SyncConflict
    ) -> bool:
        """Handle detected conflict."""
        pass

# src/tracertm/services/encryption_service.py

class EncryptionService:
    """Encrypt/decrypt sensitive data."""

    def encrypt_token(self, token: str) -> str:
        """Encrypt credential token."""
        pass

    def decrypt_token(self, encrypted: str) -> str:
        """Decrypt credential token."""
        pass
```

### 6.3 Client Layers

```python
# src/tracertm/clients/github_client.py

class GitHubClient:
    """GitHub API client with rate limiting and error handling."""

    def __init__(self, token: str, app_id: Optional[str] = None):
        self.token = token
        self.app_id = app_id
        self.session = None
        self.rate_limiter = RateLimiter(requests_per_hour=5000)

    async def get_user(self) -> dict:
        """Get authenticated user info."""
        pass

    async def list_repos(self, org: Optional[str] = None) -> list[dict]:
        """List repositories."""
        pass

    async def get_issue(self, owner: str, repo: str, number: int) -> dict:
        """Get issue."""
        pass

    async def update_issue(
        self,
        owner: str,
        repo: str,
        number: int,
        updates: dict
    ) -> dict:
        """Update issue."""
        pass

    async def get_pull(self, owner: str, repo: str, number: int) -> dict:
        """Get pull request."""
        pass

    async def register_webhook(
        self,
        owner: str,
        repo: str,
        webhook_url: str,
        events: list[str]
    ) -> str:
        """Register webhook (returns webhook ID)."""
        pass

    async def delete_webhook(
        self,
        owner: str,
        repo: str,
        webhook_id: str
    ):
        """Delete webhook."""
        pass

# src/tracertm/clients/linear_client.py

class LinearClient:
    """Linear API client using GraphQL."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rate_limiter = RateLimiter(requests_per_second=10)

    async def get_workspace(self) -> dict:
        """Get workspace info."""
        pass

    async def list_issues(self, team_id: Optional[str] = None) -> list[dict]:
        """List issues."""
        pass

    async def get_issue(self, issue_id: str) -> dict:
        """Get issue."""
        pass

    async def update_issue(self, issue_id: str, updates: dict) -> dict:
        """Update issue."""
        pass

    async def create_issue(self, team_id: str, issue_data: dict) -> dict:
        """Create issue."""
        pass

    async def register_webhook(self, webhook_url: str) -> str:
        """Register webhook (returns webhook ID)."""
        pass
```

### 6.4 Webhook Handlers

```python
# src/tracertm/handlers/external_webhook_handler.py

class ExternalWebhookHandler:
    """Handle webhooks from external systems."""

    async def handle_github_webhook(
        self,
        event_type: str,
        payload: dict,
        signature: str
    ) -> WebhookResponse:
        """Handle GitHub webhook."""
        pass

    async def handle_linear_webhook(
        self,
        event_type: str,
        payload: dict,
        signature: str
    ) -> WebhookResponse:
        """Handle Linear webhook."""
        pass

    async def process_github_push(self, payload: dict):
        """Process GitHub push event."""
        pass

    async def process_github_pr(self, payload: dict):
        """Process GitHub PR event."""
        pass

    async def process_linear_issue(self, payload: dict):
        """Process Linear issue update."""
        pass
```

---

## Part 7: Frontend Implementation Structure

### 7.1 Frontend File Structure

```
frontend/apps/web/src/
├── pages/
│   └── projects/
│       └── integrations/
│           ├── IntegrationsPage.tsx          # Main page
│           ├── CredentialsView.tsx           # Credential management
│           ├── MappingsView.tsx              # Mapping management
│           ├── SyncStatusView.tsx            # Real-time sync status
│           └── ConflictResolver.tsx          # Conflict UI
│
├── components/
│   └── integrations/
│       ├── GitHubAuthButton.tsx              # OAuth flow button
│       ├── LinearAuthButton.tsx
│       ├── CredentialForm.tsx                # Create/edit credentials
│       ├── MappingForm.tsx                   # Create/edit mappings
│       ├── ExternalItemSearch.tsx            # Search GitHub/Linear items
│       ├── SyncQueueMonitor.tsx              # Queue monitoring
│       ├── ConflictCard.tsx                  # Single conflict display
│       └── IntegrationSettings.tsx           # Integration settings
│
├── hooks/
│   ├── useIntegrations.ts                    # Main integration hook
│   ├── useExternalItems.ts                   # Search external items
│   ├── useSyncStatus.ts                      # Real-time sync status
│   └── useConflictResolution.ts              # Conflict handling
│
├── services/
│   └── api/
│       └── integrationClient.ts              # API client
│
└── types/
    └── integration.ts                        # TypeScript types
```

### 7.2 Key Components

#### Integration Setup Flow

```tsx
// frontend/apps/web/src/pages/projects/integrations/IntegrationsPage.tsx

export function IntegrationsPage() {
  const [credentials, setCredentials] = useState<IntegrationCredential[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <ProviderCards
        onSelect={(provider) => setSelectedProvider(provider)}
      />

      {selectedProvider && (
        <AuthenticationFlow provider={selectedProvider} />
      )}

      <CredentialsView
        credentials={credentials}
        onRefresh={() => fetchCredentials()}
      />

      <MappingsView />

      <SyncStatusDashboard />
    </div>
  );
}
```

#### OAuth Flow

```tsx
// frontend/apps/web/src/components/integrations/GitHubAuthButton.tsx

export function GitHubAuthButton() {
  const navigate = useNavigate();

  const handleOAuthStart = async () => {
    const response = await integrationClient.startOAuth({
      provider: "github",
      scopes: ["repo", "read:org"]
    });

    // Redirect to GitHub
    window.location.href = response.oauth_url;
  };

  return (
    <button
      onClick={handleOAuthStart}
      className="flex items-center gap-2"
    >
      <GitHubIcon />
      Connect GitHub
    </button>
  );
}

// OAuth callback handler
export function OAuthCallback() {
  const { projectId } = useParams();
  const { code, state } = useSearchParams();

  useEffect(() => {
    (async () => {
      const credential = await integrationClient.completeOAuth({
        projectId,
        code,
        state
      });

      toast.success("GitHub connected successfully");
      navigate(`/projects/${projectId}/integrations`);
    })();
  }, []);

  return <LoadingSpinner />;
}
```

#### Mapping Interface

```tsx
// frontend/apps/web/src/components/integrations/MappingForm.tsx

export function MappingForm({
  itemId,
  onMappingCreated
}: {
  itemId: string;
  onMappingCreated: (mapping: IntegrationMapping) => void;
}) {
  const [credential, setCredential] = useState<IntegrationCredential | null>(null);
  const [externalItems, setExternalItems] = useState<ExternalItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<ExternalItem | null>(null);
  const [direction, setDirection] = useState<MappingDirection>("bidirectional");

  const handleSearch = async (query: string) => {
    if (!credential) return;

    const items = await integrationClient.searchExternalItems({
      credentialId: credential.id,
      query,
      system: credential.provider
    });

    setExternalItems(items);
  };

  const handleCreate = async () => {
    if (!credential || !selectedItem) return;

    const mapping = await integrationClient.createMapping({
      tracertm_item_id: itemId,
      credential_id: credential.id,
      external_system: getExternalSystem(credential.provider, selectedItem),
      external_id: selectedItem.id,
      direction
    });

    onMappingCreated(mapping);
    toast.success("Mapping created");
  };

  return (
    <form className="space-y-4">
      <CredentialSelect
        value={credential}
        onChange={setCredential}
      />

      <ExternalItemSearch
        credential={credential}
        onSearch={handleSearch}
        items={externalItems}
        selectedItem={selectedItem}
        onSelect={setSelectedItem}
      />

      <SyncDirectionSelect
        value={direction}
        onChange={setDirection}
      />

      <button
        type="button"
        onClick={handleCreate}
        disabled={!credential || !selectedItem}
      >
        Create Mapping
      </button>
    </form>
  );
}
```

#### Sync Status Monitor

```tsx
// frontend/apps/web/src/components/integrations/SyncQueueMonitor.tsx

export function SyncQueueMonitor() {
  const { projectId } = useParams();
  const { data: syncStatus, refetch } = useSyncStatus(projectId);

  useEffect(() => {
    const interval = setInterval(() => {
      refetch();
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (!syncStatus) return null;

  return (
    <div className="border rounded-lg p-4">
      <h3 className="font-semibold mb-4">Sync Status</h3>

      <div className="grid grid-cols-4 gap-4 mb-4">
        <StatCard
          label="Total Mappings"
          value={syncStatus.total_mappings}
        />
        <StatCard
          label="Synced"
          value={syncStatus.synced_mappings}
          variant="success"
        />
        <StatCard
          label="Pending"
          value={syncStatus.pending_syncs}
          variant="info"
        />
        <StatCard
          label="Failed"
          value={syncStatus.failed_syncs}
          variant="error"
        />
      </div>

      <SyncQueueTable queue={syncStatus.queue} />
    </div>
  );
}
```

#### Conflict Resolution UI

```tsx
// frontend/apps/web/src/components/integrations/ConflictResolver.tsx

export function ConflictResolver({
  conflict,
  onResolved
}: {
  conflict: SyncConflict;
  onResolved: (resolution: "tracertm" | "external") => void;
}) {
  return (
    <div className="border-l-4 border-amber-500 p-4 bg-amber-50">
      <h4 className="font-semibold text-amber-900 mb-3">
        Sync Conflict Detected
      </h4>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600 mb-2">TraceRTM Value</p>
          <ValueDisplay value={conflict.tracertm_value} />
        </div>

        <div>
          <p className="text-sm text-gray-600 mb-2">External Value</p>
          <ValueDisplay value={conflict.external_value} />
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => onResolved("tracertm")}
          className="btn btn-sm btn-primary"
        >
          Use TraceRTM Value
        </button>

        <button
          onClick={() => onResolved("external")}
          className="btn btn-sm btn-secondary"
        >
          Use External Value
        </button>
      </div>
    </div>
  );
}
```

### 7.3 React Hooks for Integration Management

```typescript
// frontend/apps/web/src/hooks/useIntegrations.ts

export function useIntegrations(projectId: string) {
  const queryClient = useQueryClient();

  const credentials = useQuery({
    queryKey: ["integrations", projectId, "credentials"],
    queryFn: () => integrationClient.listCredentials(projectId),
    staleTime: 5 * 60 * 1000
  });

  const createCredential = useMutation({
    mutationFn: (data: IntegrationCredentialCreate) =>
      integrationClient.createCredential(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["integrations", projectId, "credentials"]
      });
    }
  });

  const validateCredential = useMutation({
    mutationFn: (credentialId: string) =>
      integrationClient.validateCredential(projectId, credentialId)
  });

  const deleteCredential = useMutation({
    mutationFn: (credentialId: string) =>
      integrationClient.deleteCredential(projectId, credentialId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["integrations", projectId, "credentials"]
      });
    }
  });

  return {
    credentials,
    createCredential,
    validateCredential,
    deleteCredential
  };
}

// frontend/apps/web/src/hooks/useSyncStatus.ts

export function useSyncStatus(projectId: string) {
  return useQuery({
    queryKey: ["integrations", projectId, "sync-status"],
    queryFn: () => integrationClient.getSyncStatus(projectId),
    staleTime: 0, // Always fresh
    refetchInterval: 5000 // Auto-refetch every 5 seconds
  });
}

// frontend/apps/web/src/hooks/useExternalItems.ts

export function useExternalItems(
  credentialId: string,
  query: string,
  system: string
) {
  return useQuery({
    queryKey: ["external-items", credentialId, system, query],
    queryFn: () =>
      integrationClient.searchExternalItems({
        credentialId,
        query,
        system
      }),
    enabled: !!query && query.length > 2,
    staleTime: 2 * 60 * 1000
  });
}
```

---

## Part 8: Security Considerations

### 8.1 Credential Storage

**Encryption Requirements:**
- Use AES-256-GCM for encryption
- Generate random IV for each encryption
- Store IV with ciphertext (IV doesn't need to be secret)
- Use KMS (Key Management Service) for master key in production
- Rotate keys annually

**Implementation:**

```python
# src/tracertm/services/encryption_service.py

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os

class EncryptionService:
    """AES-256-GCM encryption for credentials."""

    def __init__(self, master_key_env: str = "ENCRYPTION_MASTER_KEY"):
        self.master_key = os.getenv(master_key_env)
        if not self.master_key:
            raise ValueError(f"{master_key_env} not set")

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext token."""
        iv = os.urandom(12)  # 96-bit IV recommended for GCM
        cipher = AESGCM(self.master_key.encode())
        ciphertext = cipher.encrypt(iv, plaintext.encode(), None)

        # Return base64(IV + ciphertext)
        return base64.b64encode(iv + ciphertext).decode()

    def decrypt(self, encrypted: str) -> str:
        """Decrypt encrypted token."""
        data = base64.b64decode(encrypted)
        iv = data[:12]
        ciphertext = data[12:]

        cipher = AESGCM(self.master_key.encode())
        plaintext = cipher.decrypt(iv, ciphertext, None)

        return plaintext.decode()
```

### 8.2 API Security

**Rate Limiting:**

```python
# src/tracertm/middleware/rate_limiter.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to integration endpoints
app.state.limiter = limiter

@app.post("/api/v1/integrations/oauth/callback")
@limiter.limit("10/minute")
async def oauth_callback(request: Request):
    """Limit OAuth callback attempts."""
    pass

@app.get("/api/v1/integrations/sync-logs")
@limiter.limit("30/minute")
async def get_sync_logs(project_id: str):
    """Limit log retrieval."""
    pass
```

**Input Validation:**

```python
# Validate all external IDs and URLs

from pydantic import BaseModel, HttpUrl, validator

class IntegrationMappingCreate(BaseModel):
    external_id: str = Field(..., max_length=500)
    external_url: HttpUrl

    @validator('external_id')
    def validate_external_id(cls, v):
        # Reject suspicious patterns
        if len(v) > 500:
            raise ValueError("ID too long")
        if not re.match(r'^[a-zA-Z0-9/_#-]+$', v):
            raise ValueError("Invalid ID format")
        return v
```

### 8.3 OAuth Security

**PKCE Flow (for public/browser clients):**

```python
# src/tracertm/handlers/oauth_handler.py

import secrets
import hashlib
import base64

class OAuthHandler:
    """Handle OAuth flows securely."""

    def generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code_verifier and code_challenge."""
        # Generate random 43-128 character string
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')

        # Generate SHA256 hash
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')

        return code_verifier, code_challenge

    async def start_oauth_flow(self, provider: str) -> dict:
        """Initiate OAuth with PKCE."""
        code_verifier, code_challenge = self.generate_pkce_pair()

        # Store in session/Redis with TTL
        state = secrets.token_urlsafe(32)
        await self.session_store.set(
            f"oauth_state:{state}",
            {
                "code_verifier": code_verifier,
                "created_at": datetime.utcnow().isoformat()
            },
            ex=600  # 10 minute expiry
        )

        oauth_url = self.build_oauth_url(
            provider=provider,
            code_challenge=code_challenge,
            state=state
        )

        return {"oauth_url": oauth_url, "state": state}

    async def complete_oauth_flow(
        self,
        provider: str,
        code: str,
        state: str
    ) -> str:
        """Complete OAuth and exchange for token."""
        # Retrieve code_verifier from session
        session_data = await self.session_store.get(f"oauth_state:{state}")
        if not session_data:
            raise ValueError("Invalid or expired state")

        code_verifier = session_data["code_verifier"]

        # Exchange code for token using PKCE
        token = await self.exchange_code_for_token(
            provider=provider,
            code=code,
            code_verifier=code_verifier
        )

        # Clean up session
        await self.session_store.delete(f"oauth_state:{state}")

        return token
```

### 8.4 Webhook Security

**Signature Verification:**

```python
# src/tracertm/middleware/webhook_verification.py

import hmac
import hashlib

class WebhookVerificationMiddleware:
    """Verify webhook signatures."""

    async def verify_github_signature(
        self,
        payload: bytes,
        signature_header: str,
        secret: str
    ) -> bool:
        """Verify GitHub webhook signature."""
        computed = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison
        return hmac.compare_digest(computed, signature_header)

    async def verify_linear_signature(
        self,
        payload: bytes,
        signature_header: str,
        secret: str
    ) -> bool:
        """Verify Linear webhook signature."""
        computed = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed, signature_header)
```

### 8.5 Permission Scopes

**GitHub OAuth Scopes:**

```python
class GitHubScopes:
    """Required OAuth scopes for GitHub."""

    # Read access
    READ_REPO = "public_repo"  # Read public repos
    READ_PRIVATE_REPO = "repo"  # Read private repos
    READ_ORG = "read:org"  # Read organization
    READ_USER = "read:user"  # Read user profile

    # Write access (if syncing back)
    WRITE_ISSUES = "repo"  # Required for issue updates

    # Webhook
    ADMIN_REPO_HOOK = "admin:repo_hook"  # Register webhooks

    # Recommended minimal scopes
    MINIMAL = ["repo", "read:org"]
```

**Linear API Permissions:**
- Team access (read/write issues)
- Workspace access (limited to authenticated team)
- No scopes needed - all scopes are granted to the API key

---

## Part 9: Rate Limiting and Error Handling

### 9.1 Rate Limiting Strategy

```python
# src/tracertm/services/rate_limiter_service.py

class ExternalIntegrationRateLimiter:
    """Rate limiting for external API calls."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def check_limit(
        self,
        credential_id: str,
        provider: str,
        calls_made: int
    ) -> RateLimitStatus:
        """
        Check if credential has exceeded rate limit.

        Limits:
        - GitHub: 5,000 requests/hour (primary), 15,000/hour (GraphQL)
        - Linear: 10 requests/second
        - TraceRTM: Batch sync operations
        """

        key = f"rate_limit:{credential_id}:{provider}"

        # Check current usage
        current = await self.redis.incr(key)

        if current == 1:
            # First request, set expiry
            await self.redis.expire(key, 3600)  # 1 hour

        # Get limits based on provider
        limits = {
            "github": 5000,
            "linear": 600,  # 10/second * 60
        }

        limit = limits.get(provider, 1000)

        if current >= limit:
            remaining = 0
            reset_at = await self.redis.ttl(key)
        else:
            remaining = limit - current
            reset_at = await self.redis.ttl(key)

        return RateLimitStatus(
            limit=limit,
            used=current,
            remaining=remaining,
            reset_at=reset_at
        )

    async def wait_if_needed(
        self,
        credential_id: str,
        provider: str
    ):
        """Wait if approaching rate limit."""
        status = await self.check_limit(credential_id, provider, 0)

        # If > 80% used, back off
        usage_percent = (status.used / status.limit) * 100

        if usage_percent > 80:
            wait_time = min(5, (usage_percent - 80) / 20)  # 0-5 second wait
            await asyncio.sleep(wait_time)
```

### 9.2 Error Handling

```python
# src/tracertm/exceptions/integration_exceptions.py

class IntegrationException(Exception):
    """Base integration exception."""
    pass

class CredentialValidationError(IntegrationException):
    """Credential is invalid or expired."""
    pass

class ExternalSystemError(IntegrationException):
    """Error communicating with external system."""
    pass

class SyncConflictError(IntegrationException):
    """Unresolvable sync conflict."""
    pass

class MappingNotFoundError(IntegrationException):
    """Mapping doesn't exist."""
    pass

class RateLimitExceededError(IntegrationException):
    """Rate limit exceeded."""
    pass

# src/tracertm/handlers/integration_error_handler.py

class IntegrationErrorHandler:
    """Handle integration errors gracefully."""

    async def handle_sync_failure(
        self,
        queue_item: IntegrationSyncQueue,
        error: Exception
    ):
        """Handle sync operation failure."""

        # Categorize error
        if isinstance(error, CredentialValidationError):
            # Alert user: credential expired/revoked
            await self.notify_user(
                queue_item.mapping_id,
                "Your integration credential has expired. Please refresh it."
            )
            # Mark credential invalid
            await self.credential_repo.mark_invalid(
                queue_item.integration_credential_id
            )

        elif isinstance(error, RateLimitExceededError):
            # Exponential backoff retry
            backoff = min(2 ** queue_item.attempts, 3600)  # Max 1 hour
            await self.sync_queue_repo.reschedule_retry(
                queue_item.id,
                backoff
            )

        elif isinstance(error, ExternalSystemError):
            # Transient error - retry with backoff
            if queue_item.attempts < queue_item.max_attempts:
                backoff = 60 * (2 ** queue_item.attempts)
                await self.sync_queue_repo.reschedule_retry(
                    queue_item.id,
                    backoff
                )
            else:
                # Max retries exceeded
                await self.notify_user(
                    queue_item.mapping_id,
                    f"Sync failed after {queue_item.max_attempts} retries"
                )

        elif isinstance(error, SyncConflictError):
            # Flag for manual resolution
            await self.create_conflict_record(queue_item, error)

        # Log error
        logger.error(f"Sync failed: {error}", exc_info=True)
```

### 9.3 Retry Strategy

**Exponential Backoff with Jitter:**

```python
def calculate_backoff(attempt: int, base: int = 60, max_wait: int = 3600) -> int:
    """Calculate backoff with jitter."""
    # Exponential backoff: base * 2^attempt
    backoff = base * (2 ** attempt)

    # Cap at max_wait
    backoff = min(backoff, max_wait)

    # Add random jitter (±10%)
    jitter = backoff * 0.1 * random.uniform(-1, 1)

    return int(backoff + jitter)

# Example:
# Attempt 0: ~60s
# Attempt 1: ~120s
# Attempt 2: ~240s
# Max: ~3600s (1 hour)
```

---

## Part 10: Implementation Phases

### Phase 1: Foundation & Authentication (Weeks 1-2)

**Deliverables:**
- Integration credential model and encryption service
- OAuth infrastructure (state management, PKCE)
- GitHub OAuth app registration
- Linear API key support
- Credential repository and service
- Basic credential validation

**Tasks:**
1. Create integration models and migrations
2. Implement encryption service
3. Set up OAuth flow handlers
4. Create credential management API endpoints
5. Build credential UI (auth buttons, form)
6. Write integration tests for auth flows
7. Security audit of auth implementation

**Estimated: 40 hours**

### Phase 2: Core Sync Infrastructure (Weeks 3-4)

**Deliverables:**
- Integration mapping model
- Sync queue infrastructure
- Webhook event handlers
- Basic GitHub/Linear API clients
- Sync processor service
- Sync logging and monitoring

**Tasks:**
1. Create mapping model and repository
2. Implement sync queue and processor
3. Build webhook signature verification
4. Create GitHub API client with error handling
5. Create Linear API client with error handling
6. Implement basic sync logic (pull direction)
7. Add sync queue monitoring UI
8. Write sync service tests

**Estimated: 50 hours**

### Phase 3: Bidirectional Sync & Conflict Resolution (Weeks 5-6)

**Deliverables:**
- Bidirectional sync implementation
- Conflict detection and resolution
- Conflict resolution UI
- Sync statistics and diagnostics
- Rate limiting and backoff strategies

**Tasks:**
1. Implement item-to-GitHub sync (issues, PRs)
2. Implement item-to-Linear sync
3. Build conflict detection logic
4. Implement conflict resolution strategies
5. Create conflict resolution UI
6. Add rate limiting to sync processor
7. Implement retry logic with exponential backoff
8. Add comprehensive logging and diagnostics

**Estimated: 45 hours**

### Phase 4: GitHub Projects Integration (Weeks 7-8)

**Deliverables:**
- GitHub Projects v2 sync
- Project board mapping
- Status synchronization
- Column/field mapping

**Tasks:**
1. Research GitHub Projects API
2. Build project item sync logic
3. Implement project board column mapping
4. Create GitHub Projects UI components
5. Add project sync to queue processor
6. Write project sync tests

**Estimated: 35 hours**

### Phase 5: Polish, Testing & Documentation (Weeks 9-10)

**Deliverables:**
- Comprehensive test coverage
- E2E tests
- Documentation
- Performance optimization
- Security hardening

**Tasks:**
1. Write integration tests for all sync scenarios
2. E2E tests for complete flows
3. Performance testing and optimization
4. Security penetration testing
5. Create user documentation
6. Create API documentation
7. Create troubleshooting guide

**Estimated: 40 hours**

### Phase 6: Deployment & Monitoring (Weeks 11-12)

**Deliverables:**
- Production deployment
- Monitoring and alerting
- Rollback plan
- Post-launch support

**Tasks:**
1. Set up production credential encryption
2. Configure monitoring/alerting
3. Deploy to staging
4. Perform production dry-run
5. Deploy to production (canary)
6. Monitor error rates and sync latency
7. Gather user feedback

**Estimated: 30 hours**

**Total: ~240 hours (8-12 weeks with 20-30 hours/week)**

---

## Part 11: File Organization & Structure

### 11.1 New Backend Files to Create

**Models:**
- `/src/tracertm/models/integration_credential.py`
- `/src/tracertm/models/integration_mapping.py`
- `/src/tracertm/models/integration_sync_queue.py`
- `/src/tracertm/models/integration_sync_log.py`

**Repositories:**
- `/src/tracertm/repositories/integration_credential_repository.py`
- `/src/tracertm/repositories/integration_mapping_repository.py`
- `/src/tracertm/repositories/integration_sync_queue_repository.py`

**Services:**
- `/src/tracertm/services/external_integration_service.py`
- `/src/tracertm/services/github_integration_service.py`
- `/src/tracertm/services/linear_integration_service.py`
- `/src/tracertm/services/integration_sync_processor_service.py`
- `/src/tracertm/services/integration_polling_service.py`
- `/src/tracertm/services/integration_conflict_service.py`
- `/src/tracertm/services/encryption_service.py`

**Clients:**
- `/src/tracertm/clients/github_client.py`
- `/src/tracertm/clients/linear_client.py`

**Handlers:**
- `/src/tracertm/handlers/external_webhook_handler.py`
- `/src/tracertm/handlers/oauth_handler.py`
- `/src/tracertm/handlers/integration_error_handler.py`

**Middleware:**
- `/src/tracertm/middleware/webhook_verification.py`
- `/src/tracertm/middleware/integration_rate_limiter.py`

**Schemas:**
- `/src/tracertm/schemas/integration.py` (new file with all schemas)

**API Routes:**
- Add to `/src/tracertm/api/main.py` or create `/src/tracertm/api/routers/integrations.py`

### 11.2 New Frontend Files to Create

**Pages:**
- `/frontend/apps/web/src/pages/projects/integrations/IntegrationsPage.tsx`
- `/frontend/apps/web/src/pages/projects/integrations/OAuthCallbackPage.tsx`

**Components:**
- `/frontend/apps/web/src/components/integrations/GitHubAuthButton.tsx`
- `/frontend/apps/web/src/components/integrations/LinearAuthButton.tsx`
- `/frontend/apps/web/src/components/integrations/CredentialForm.tsx`
- `/frontend/apps/web/src/components/integrations/CredentialsView.tsx`
- `/frontend/apps/web/src/components/integrations/MappingForm.tsx`
- `/frontend/apps/web/src/components/integrations/MappingsView.tsx`
- `/frontend/apps/web/src/components/integrations/ExternalItemSearch.tsx`
- `/frontend/apps/web/src/components/integrations/SyncQueueMonitor.tsx`
- `/frontend/apps/web/src/components/integrations/ConflictResolver.tsx`
- `/frontend/apps/web/src/components/integrations/SyncStatusDashboard.tsx`

**Hooks:**
- `/frontend/apps/web/src/hooks/useIntegrations.ts`
- `/frontend/apps/web/src/hooks/useExternalItems.ts`
- `/frontend/apps/web/src/hooks/useSyncStatus.ts`
- `/frontend/apps/web/src/hooks/useConflictResolution.ts`

**Services:**
- `/frontend/apps/web/src/services/api/integrationClient.ts`

**Types:**
- `/frontend/apps/web/src/types/integration.ts`

### 11.3 Configuration & Environment

**New Environment Variables:**

```bash
# Encryption
ENCRYPTION_MASTER_KEY=<128-bit key in base64>

# GitHub OAuth App
GITHUB_OAUTH_CLIENT_ID=<your app id>
GITHUB_OAUTH_CLIENT_SECRET=<your app secret>
GITHUB_OAUTH_REDIRECT_URI=https://tracertm.com/integrations/callback

# Linear Integration
LINEAR_API_KEY=<org api key>

# External URLs
EXTERNAL_WEBHOOK_URL=https://tracertm.com/api/v1/webhooks

# Sync Configuration
SYNC_POLL_INTERVAL_SECONDS=300
SYNC_BATCH_SIZE=10
SYNC_MAX_RETRIES=3
SYNC_TIMEOUT_SECONDS=30
```

**Update Configuration Models:**

```python
# src/tracertm/config/schema.py

class IntegrationConfig(BaseSettings):
    """Integration configuration."""

    encryption_master_key: str

    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str

    linear_api_key: str

    external_webhook_url: str

    # Sync settings
    sync_poll_interval: int = 300
    sync_batch_size: int = 10
    sync_max_retries: int = 3
    sync_timeout: int = 30
```

---

## Part 12: Testing Strategy

### 12.1 Unit Tests

```python
# tests/unit/test_integration_credential_repository.py

class TestIntegrationCredentialRepository:
    """Test credential repository."""

    async def test_create_credential(self):
        """Test creating credential."""
        pass

    async def test_encrypt_decrypt_token(self):
        """Test token encryption/decryption."""
        pass

    async def test_validate_credential(self):
        """Test credential validation."""
        pass

# tests/unit/test_sync_processor.py

class TestIntegrationSyncProcessor:
    """Test sync processor."""

    async def test_process_item_created_event(self):
        """Test processing item creation."""
        pass

    async def test_conflict_detection(self):
        """Test conflict detection."""
        pass

    async def test_retry_logic(self):
        """Test retry with exponential backoff."""
        pass

# tests/unit/test_github_client.py

class TestGitHubClient:
    """Test GitHub API client."""

    async def test_list_repos(self):
        """Test listing repositories."""
        pass

    async def test_rate_limiting(self):
        """Test rate limit handling."""
        pass

    async def test_webhook_registration(self):
        """Test webhook registration."""
        pass
```

### 12.2 Integration Tests

```python
# tests/integration/test_github_sync.py

class TestGitHubSync:
    """Test GitHub synchronization."""

    async def test_sync_issue_to_tracertm_item(self):
        """Test syncing GitHub issue to TraceRTM."""
        pass

    async def test_sync_tracertm_to_github_issue(self):
        """Test syncing TraceRTM item to GitHub issue."""
        pass

    async def test_bidirectional_sync(self):
        """Test bidirectional sync."""
        pass

# tests/integration/test_linear_sync.py

class TestLinearSync:
    """Test Linear synchronization."""

    async def test_sync_linear_issue_to_tracertm(self):
        """Test syncing Linear issue to TraceRTM."""
        pass
```

### 12.3 E2E Tests

```typescript
// frontend/apps/web/e2e/integrations.spec.ts

test.describe("External Integrations", () => {
  test("should connect GitHub via OAuth", async ({ page }) => {
    // Navigate to integrations page
    // Click GitHub button
    // Verify OAuth redirect
    // Complete OAuth flow
    // Verify credential created
  });

  test("should create mapping and sync", async ({ page }) => {
    // Set up mapping between item and GitHub issue
    // Trigger manual sync
    // Verify data synced
  });

  test("should resolve conflicts", async ({ page }) => {
    // Create conflicting changes in both systems
    // Verify conflict detected
    // Resolve conflict
    // Verify correct value synced
  });
});
```

---

## Part 13: Success Metrics & Monitoring

### 13.1 Key Metrics

```python
# src/tracertm/services/integration_metrics_service.py

class IntegrationMetricsService:
    """Track integration metrics for monitoring."""

    async def record_sync_event(
        self,
        mapping_id: str,
        success: bool,
        duration_ms: float,
        direction: str
    ):
        """Record sync event metric."""
        pass

    async def get_sync_statistics(
        self,
        project_id: str,
        time_range: str = "24h"
    ) -> dict:
        """
        Get sync statistics:
        - Total syncs: successful, failed, retried
        - Average sync time
        - Error rate by type
        - Mapping health
        - Rate limit hits
        """
        pass
```

**Key Metrics to Track:**
- Sync success rate (target: > 99%)
- Average sync latency (target: < 5s for push, < 30s for poll)
- Error rate by type
- Credential validity rate
- Conflict detection rate
- Rate limit hit frequency
- User adoption (% of projects with mappings)

### 13.2 Monitoring & Alerting

```yaml
# Alerts to configure

Alerts:
  SyncFailureRate:
    condition: error_rate > 5% in 10 minutes
    severity: critical
    action: page on-call

  CredentialExpired:
    condition: credential_status == "expired"
    severity: warning
    action: notify user, disable integration

  RateLimitExceeded:
    condition: rate_limit_hits > threshold
    severity: info
    action: log, increase backoff

  WebhookFailures:
    condition: webhook_delivery_failures > 10 in 1 hour
    severity: warning
    action: investigate webhook endpoint health

  SyncQueueBacklog:
    condition: queue_size > 1000
    severity: warning
    action: scale sync processor

  HighConflictRate:
    condition: conflicts_per_hour > 100
    severity: info
    action: notify users, investigate sync logic
```

---

## Part 14: Migration & Rollback Strategy

### 14.1 Phased Rollout

**Phase 1: Internal Beta (Week 11)**
- Deploy to staging
- Enable for internal team only
- Manual testing
- Performance validation

**Phase 2: Early Access (Week 12)**
- Deploy to production (feature flag)
- Enable for beta users (opt-in)
- Monitor error rates
- Gather feedback

**Phase 3: General Availability**
- Remove feature flag
- Enable for all users
- Full monitoring active
- Documentation published

### 14.2 Rollback Plan

```python
# Rollback triggers

ROLLBACK_TRIGGERS = {
    "error_rate_exceeds_10_percent": {
        "window": "1 hour",
        "action": "disable_new_mappings"
    },
    "sync_failure_rate_exceeds_50_percent": {
        "window": "15 minutes",
        "action": "pause_sync_processor"
    },
    "data_corruption_detected": {
        "window": "immediate",
        "action": "stop_bidirectional_sync"
    },
    "credential_leak_detected": {
        "window": "immediate",
        "action": "revoke_all_credentials"
    }
}
```

---

## Summary

This comprehensive implementation plan provides:

1. **Authentication Architecture** - OAuth 2.0 and PAT support with security best practices
2. **Data Models** - Production-ready schemas with encryption, versioning, and audit trails
3. **Sync Strategies** - Real-time webhooks with polling fallback and intelligent conflict resolution
4. **API Design** - RESTful endpoints for all integration operations
5. **Frontend UI** - Complete components for setup, mapping, and monitoring
6. **Security** - AES-256 encryption, PKCE OAuth, webhook signature verification
7. **Error Handling** - Comprehensive retry logic, rate limiting, and error categorization
8. **Testing Strategy** - Unit, integration, and E2E test coverage
9. **Monitoring** - Metrics, alerts, and dashboards for operational visibility
10. **Phased Approach** - 12-week implementation roadmap with clear milestones

The plan balances production-readiness with pragmatic implementation, leveraging existing TraceRTM patterns (webhooks, repository pattern, async architecture) while introducing enterprise-grade external integration capabilities.

