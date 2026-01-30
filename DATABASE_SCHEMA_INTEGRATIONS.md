# External Integrations - Database Schema

## Overview

This document defines all database tables required for external integrations support.

## Table Definitions

### 1. integration_credentials

Stores encrypted credentials for external system authentication.

```sql
CREATE TABLE integration_credentials (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,

    -- Provider and type
    provider VARCHAR(50) NOT NULL,  -- 'github', 'linear'
    credential_type VARCHAR(50) NOT NULL,  -- 'oauth_token', 'personal_access_token', 'github_app'

    -- Authentication
    encrypted_token VARCHAR(1024) NOT NULL,  -- AES-256-GCM encrypted
    token_expires_at DATETIME NULL,
    refresh_token VARCHAR(512) NULL,  -- For OAuth refresh tokens

    -- Scope tracking
    scopes JSON NOT NULL DEFAULT '[]',

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active',  -- 'active', 'expired', 'revoked', 'invalid'

    -- Validation
    last_validated_at DATETIME NULL,
    validation_error VARCHAR(1000) NULL,

    -- Provider metadata
    provider_metadata JSON NOT NULL DEFAULT '{}',
    -- GitHub: { "user_login": "octocat", "org_login": "github", "installation_id": "123" }
    -- Linear: { "team_id": "...", "workspace_id": "..." }

    -- Rotation tracking
    created_by_user_id VARCHAR(36),
    rotated_at DATETIME NULL,
    rotation_required_at DATETIME NULL,

    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Versioning
    version INT NOT NULL DEFAULT 1,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,

    INDEX idx_project_provider (project_id, provider),
    INDEX idx_status (status),
    INDEX idx_expires_at (token_expires_at)
);
```

**Python Model:**

```python
class IntegrationCredential(Base, TimestampMixin):
    __tablename__ = "integration_credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))

    provider: Mapped[str] = mapped_column(String(50))
    credential_type: Mapped[str] = mapped_column(String(50))

    encrypted_token: Mapped[str] = mapped_column(String(1024))
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    refresh_token: Mapped[Optional[str]] = mapped_column(String(512))

    scopes: Mapped[list[str]] = mapped_column(JSONType, default=list)

    status: Mapped[str] = mapped_column(String(50), default="active")

    last_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    validation_error: Mapped[Optional[str]] = mapped_column(String(1000))

    provider_metadata: Mapped[dict] = mapped_column(JSONType, default=dict)

    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36))
    rotated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rotation_required_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    version: Mapped[int] = mapped_column(Integer, default=1)
```

---

### 2. integration_mappings

Maps TraceRTM items to external system items.

```sql
CREATE TABLE integration_mappings (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    integration_credential_id VARCHAR(36) NOT NULL,

    -- TraceRTM side
    tracertm_item_id VARCHAR(255) NOT NULL,
    tracertm_item_type VARCHAR(50) NOT NULL,  -- 'requirement', 'feature', 'epic', 'test'

    -- External side
    external_system VARCHAR(100) NOT NULL,  -- 'github_issue', 'github_pr', 'linear_issue'
    external_id VARCHAR(500) NOT NULL,  -- "octocat/repo#42" or "LINEAR-123"
    external_url VARCHAR(2000) NOT NULL,

    -- Mapping metadata
    mapping_metadata JSON NOT NULL DEFAULT '{}',
    -- GitHub Issues: { "repo": "owner/repo", "issue_number": 42, "labels": ["bug"] }
    -- GitHub PRs: { "repo": "owner/repo", "pr_number": 42, "branch": "feature-123" }
    -- Linear: { "team_key": "ACME", "issue_id": "....", "status": "Todo" }

    -- Sync configuration
    direction VARCHAR(50) NOT NULL DEFAULT 'bidirectional',  -- 'bidirectional', 'tracertm_to_external', 'external_to_tracertm'
    status VARCHAR(50) NOT NULL DEFAULT 'active',  -- 'active', 'paused', 'sync_error'
    auto_sync BOOLEAN NOT NULL DEFAULT TRUE,

    -- Sync tracking
    last_sync_at DATETIME NULL,
    last_sync_direction VARCHAR(50) NULL,  -- 'push', 'pull'
    sync_error_message VARCHAR(1000) NULL,
    consecutive_failures INT NOT NULL DEFAULT 0,

    -- Conflict tracking
    last_conflict_at DATETIME NULL,
    conflict_resolution_strategy VARCHAR(50) NOT NULL DEFAULT 'manual',
    -- 'manual', 'tracertm_wins', 'external_wins', 'last_write_wins'

    -- Field-specific conflict strategies (JSON)
    field_resolution_rules JSON NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Versioning
    version INT NOT NULL DEFAULT 1,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (integration_credential_id) REFERENCES integration_credentials(id) ON DELETE CASCADE,
    FOREIGN KEY (tracertm_item_id) REFERENCES items(id) ON DELETE CASCADE,

    UNIQUE KEY uc_mapping (project_id, external_id),
    INDEX idx_credential (integration_credential_id),
    INDEX idx_item (tracertm_item_id),
    INDEX idx_external_id (external_id),
    INDEX idx_status (status),
    INDEX idx_last_sync (last_sync_at)
);
```

**Python Model:**

```python
class IntegrationMapping(Base, TimestampMixin):
    __tablename__ = "integration_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    integration_credential_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_credentials.id")
    )

    tracertm_item_id: Mapped[str] = mapped_column(String(255), ForeignKey("items.id"))
    tracertm_item_type: Mapped[str] = mapped_column(String(50))

    external_system: Mapped[str] = mapped_column(String(100))
    external_id: Mapped[str] = mapped_column(String(500))
    external_url: Mapped[str] = mapped_column(String(2000))

    mapping_metadata: Mapped[dict] = mapped_column(JSONType, default=dict)

    direction: Mapped[str] = mapped_column(String(50), default="bidirectional")
    status: Mapped[str] = mapped_column(String(50), default="active")
    auto_sync: Mapped[bool] = mapped_column(Boolean, default=True)

    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_sync_direction: Mapped[Optional[str]] = mapped_column(String(50))
    sync_error_message: Mapped[Optional[str]] = mapped_column(String(1000))
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0)

    last_conflict_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    conflict_resolution_strategy: Mapped[str] = mapped_column(String(50), default="manual")
    field_resolution_rules: Mapped[dict] = mapped_column(JSONType, default=dict)

    version: Mapped[int] = mapped_column(Integer, default=1)
```

---

### 3. integration_sync_queue

Queue of pending synchronization operations.

```sql
CREATE TABLE integration_sync_queue (
    id VARCHAR(36) PRIMARY KEY,
    integration_credential_id VARCHAR(36) NOT NULL,
    mapping_id VARCHAR(36) NOT NULL,

    -- Event details
    event_type VARCHAR(50) NOT NULL,  -- 'item_created', 'item_updated', 'status_changed', 'linked', 'unlinked'
    direction VARCHAR(50) NOT NULL,  -- 'push', 'pull'
    priority VARCHAR(50) NOT NULL DEFAULT 'normal',  -- 'low', 'normal', 'high', 'critical'

    -- Payload (data to sync)
    payload JSON NOT NULL,

    -- Processing state
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed', 'retried'
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 3,
    next_retry_at DATETIME NULL,

    -- Error tracking
    error_message VARCHAR(2000) NULL,
    error_code VARCHAR(100) NULL,

    -- Idempotency (prevent duplicate processing)
    idempotency_key VARCHAR(255) NULL,

    -- Processing tracking
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    processing_time_ms INT NULL,

    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (integration_credential_id) REFERENCES integration_credentials(id) ON DELETE CASCADE,
    FOREIGN KEY (mapping_id) REFERENCES integration_mappings(id) ON DELETE CASCADE,

    UNIQUE KEY uc_idempotency (mapping_id, idempotency_key),
    INDEX idx_credential_status (integration_credential_id, status),
    INDEX idx_mapping (mapping_id),
    INDEX idx_priority_status (priority, status),
    INDEX idx_retry (status, next_retry_at),
    INDEX idx_created_at (created_at)
);
```

**Python Model:**

```python
class IntegrationSyncQueue(Base, TimestampMixin):
    __tablename__ = "integration_sync_queue"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    integration_credential_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_credentials.id")
    )
    mapping_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_mappings.id")
    )

    event_type: Mapped[str] = mapped_column(String(50))
    direction: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(50), default="normal")

    payload: Mapped[dict] = mapped_column(JSONType)

    status: Mapped[str] = mapped_column(String(50), default="pending")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    error_message: Mapped[Optional[str]] = mapped_column(String(2000))
    error_code: Mapped[Optional[str]] = mapped_column(String(100))

    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255))

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
```

---

### 4. integration_sync_logs

Audit log of all sync operations.

```sql
CREATE TABLE integration_sync_logs (
    id VARCHAR(36) PRIMARY KEY,
    sync_queue_id VARCHAR(36) NULL,
    mapping_id VARCHAR(36) NOT NULL,

    -- Operation details
    operation VARCHAR(50) NOT NULL,  -- 'create', 'update', 'delete', 'link', 'unlink'
    direction VARCHAR(50) NOT NULL,  -- 'push', 'pull'

    -- Source and target
    source_system VARCHAR(100) NOT NULL,  -- 'tracertm' or external system name
    source_id VARCHAR(255) NOT NULL,
    target_system VARCHAR(100) NOT NULL,
    target_id VARCHAR(255) NOT NULL,

    -- Changes (what was synced)
    changes JSON NOT NULL DEFAULT '{}',
    -- {
    --   "before": { "status": "todo", "priority": "high" },
    --   "after": { "status": "in_progress", "priority": "high" },
    --   "fields_changed": ["status"]
    -- }

    -- Result
    success BOOLEAN NOT NULL,
    error_message VARCHAR(2000) NULL,

    -- Metadata
    sync_metadata JSON NOT NULL DEFAULT '{}',
    -- {
    --   "triggered_by": "webhook" | "polling" | "manual",
    --   "user_id": "...",
    --   "conflict_detected": true,
    --   "conflict_resolution_used": "external_wins"
    -- }

    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sync_queue_id) REFERENCES integration_sync_queue(id) ON DELETE SET NULL,
    FOREIGN KEY (mapping_id) REFERENCES integration_mappings(id) ON DELETE CASCADE,

    INDEX idx_mapping (mapping_id),
    INDEX idx_queue (sync_queue_id),
    INDEX idx_success (success),
    INDEX idx_created_at (created_at),
    INDEX idx_operation (operation)
);
```

**Python Model:**

```python
class IntegrationSyncLog(Base):
    __tablename__ = "integration_sync_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sync_queue_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("integration_sync_queue.id")
    )
    mapping_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_mappings.id")
    )

    operation: Mapped[str] = mapped_column(String(50))
    direction: Mapped[str] = mapped_column(String(50))

    source_system: Mapped[str] = mapped_column(String(100))
    source_id: Mapped[str] = mapped_column(String(255))
    target_system: Mapped[str] = mapped_column(String(100))
    target_id: Mapped[str] = mapped_column(String(255))

    changes: Mapped[dict] = mapped_column(JSONType, default=dict)

    success: Mapped[bool] = mapped_column(Boolean)
    error_message: Mapped[Optional[str]] = mapped_column(String(2000))

    sync_metadata: Mapped[dict] = mapped_column(JSONType, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
```

---

### 5. integration_conflicts

Detected sync conflicts awaiting resolution.

```sql
CREATE TABLE integration_conflicts (
    id VARCHAR(36) PRIMARY KEY,
    mapping_id VARCHAR(36) NOT NULL,

    -- Conflict details
    field VARCHAR(100) NOT NULL,
    tracertm_value TEXT NULL,
    external_value TEXT NULL,

    -- Resolution
    resolution_status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- 'pending', 'resolved', 'ignored'
    resolved_value TEXT NULL,
    resolution_strategy_used VARCHAR(50) NULL,

    -- Timestamps
    detected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,

    FOREIGN KEY (mapping_id) REFERENCES integration_mappings(id) ON DELETE CASCADE,

    INDEX idx_mapping (mapping_id),
    INDEX idx_status (resolution_status),
    INDEX idx_detected_at (detected_at)
);
```

**Python Model:**

```python
class IntegrationConflict(Base):
    __tablename__ = "integration_conflicts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    mapping_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_mappings.id")
    )

    field: Mapped[str] = mapped_column(String(100))
    tracertm_value: Mapped[Optional[str]] = mapped_column(Text)
    external_value: Mapped[Optional[str]] = mapped_column(Text)

    resolution_status: Mapped[str] = mapped_column(String(50), default="pending")
    resolved_value: Mapped[Optional[str]] = mapped_column(Text)
    resolution_strategy_used: Mapped[Optional[str]] = mapped_column(String(50))

    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
```

---

### 6. integration_rate_limits

Track rate limit usage per credential.

```sql
CREATE TABLE integration_rate_limits (
    id VARCHAR(36) PRIMARY KEY,
    integration_credential_id VARCHAR(36) NOT NULL,

    -- Provider rate limit info
    provider VARCHAR(50) NOT NULL,
    api_endpoint VARCHAR(255) NOT NULL,

    -- Current usage in window
    requests_used INT NOT NULL DEFAULT 0,
    requests_limit INT NOT NULL,

    -- Window management
    window_start_at DATETIME NOT NULL,
    window_end_at DATETIME NOT NULL,

    -- Backoff info
    is_rate_limited BOOLEAN NOT NULL DEFAULT FALSE,
    backoff_until DATETIME NULL,

    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (integration_credential_id) REFERENCES integration_credentials(id) ON DELETE CASCADE,

    UNIQUE KEY uc_credential_endpoint (integration_credential_id, api_endpoint),
    INDEX idx_backoff_until (backoff_until)
);
```

**Python Model:**

```python
class IntegrationRateLimit(Base, TimestampMixin):
    __tablename__ = "integration_rate_limits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    integration_credential_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_credentials.id")
    )

    provider: Mapped[str] = mapped_column(String(50))
    api_endpoint: Mapped[str] = mapped_column(String(255))

    requests_used: Mapped[int] = mapped_column(Integer, default=0)
    requests_limit: Mapped[int] = mapped_column(Integer)

    window_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    is_rate_limited: Mapped[bool] = mapped_column(Boolean, default=False)
    backoff_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
```

---

## Alembic Migration

```python
# alembic/versions/008_add_external_integrations.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    """Add external integrations tables."""

    # integration_credentials
    op.create_table(
        'integration_credentials',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('credential_type', sa.String(50), nullable=False),
        sa.Column('encrypted_token', sa.String(1024), nullable=False),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refresh_token', sa.String(512), nullable=True),
        sa.Column('scopes', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('last_validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('validation_error', sa.String(1000), nullable=True),
        sa.Column('provider_metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_by_user_id', sa.String(36), nullable=True),
        sa.Column('rotated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rotation_required_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_project_provider', 'integration_credentials', ['project_id', 'provider'])
    op.create_index('idx_status', 'integration_credentials', ['status'])
    op.create_index('idx_expires_at', 'integration_credentials', ['token_expires_at'])

    # integration_mappings
    op.create_table(
        'integration_mappings',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('integration_credential_id', sa.String(36), nullable=False),
        sa.Column('tracertm_item_id', sa.String(255), nullable=False),
        sa.Column('tracertm_item_type', sa.String(50), nullable=False),
        sa.Column('external_system', sa.String(100), nullable=False),
        sa.Column('external_id', sa.String(500), nullable=False),
        sa.Column('external_url', sa.String(2000), nullable=False),
        sa.Column('mapping_metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('direction', sa.String(50), nullable=False, server_default='bidirectional'),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('auto_sync', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync_direction', sa.String(50), nullable=True),
        sa.Column('sync_error_message', sa.String(1000), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_conflict_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('conflict_resolution_strategy', sa.String(50), nullable=False, server_default='manual'),
        sa.Column('field_resolution_rules', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['integration_credential_id'], ['integration_credentials.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tracertm_item_id'], ['items.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_unique_constraint('uc_mapping', 'integration_mappings', ['project_id', 'external_id'])
    op.create_index('idx_credential', 'integration_mappings', ['integration_credential_id'])
    op.create_index('idx_item', 'integration_mappings', ['tracertm_item_id'])
    op.create_index('idx_external_id', 'integration_mappings', ['external_id'])
    op.create_index('idx_status', 'integration_mappings', ['status'])
    op.create_index('idx_last_sync', 'integration_mappings', ['last_sync_at'])

    # integration_sync_queue
    op.create_table(
        'integration_sync_queue',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('integration_credential_id', sa.String(36), nullable=False),
        sa.Column('mapping_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('direction', sa.String(50), nullable=False),
        sa.Column('priority', sa.String(50), nullable=False, server_default='normal'),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(2000), nullable=True),
        sa.Column('error_code', sa.String(100), nullable=True),
        sa.Column('idempotency_key', sa.String(255), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['integration_credential_id'], ['integration_credentials.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mapping_id'], ['integration_mappings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_unique_constraint('uc_idempotency', 'integration_sync_queue', ['mapping_id', 'idempotency_key'])
    op.create_index('idx_credential_status', 'integration_sync_queue', ['integration_credential_id', 'status'])
    op.create_index('idx_mapping', 'integration_sync_queue', ['mapping_id'])
    op.create_index('idx_priority_status', 'integration_sync_queue', ['priority', 'status'])
    op.create_index('idx_retry', 'integration_sync_queue', ['status', 'next_retry_at'])
    op.create_index('idx_created_at', 'integration_sync_queue', ['created_at'])

    # integration_sync_logs
    op.create_table(
        'integration_sync_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('sync_queue_id', sa.String(36), nullable=True),
        sa.Column('mapping_id', sa.String(36), nullable=False),
        sa.Column('operation', sa.String(50), nullable=False),
        sa.Column('direction', sa.String(50), nullable=False),
        sa.Column('source_system', sa.String(100), nullable=False),
        sa.Column('source_id', sa.String(255), nullable=False),
        sa.Column('target_system', sa.String(100), nullable=False),
        sa.Column('target_id', sa.String(255), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.String(2000), nullable=True),
        sa.Column('sync_metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['sync_queue_id'], ['integration_sync_queue.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['mapping_id'], ['integration_mappings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_mapping', 'integration_sync_logs', ['mapping_id'])
    op.create_index('idx_queue', 'integration_sync_logs', ['sync_queue_id'])
    op.create_index('idx_success', 'integration_sync_logs', ['success'])
    op.create_index('idx_created_at', 'integration_sync_logs', ['created_at'])
    op.create_index('idx_operation', 'integration_sync_logs', ['operation'])

    # integration_conflicts
    op.create_table(
        'integration_conflicts',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('mapping_id', sa.String(36), nullable=False),
        sa.Column('field', sa.String(100), nullable=False),
        sa.Column('tracertm_value', sa.Text(), nullable=True),
        sa.Column('external_value', sa.Text(), nullable=True),
        sa.Column('resolution_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('resolved_value', sa.Text(), nullable=True),
        sa.Column('resolution_strategy_used', sa.String(50), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['mapping_id'], ['integration_mappings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_index('idx_mapping', 'integration_conflicts', ['mapping_id'])
    op.create_index('idx_status', 'integration_conflicts', ['resolution_status'])
    op.create_index('idx_detected_at', 'integration_conflicts', ['detected_at'])

    # integration_rate_limits
    op.create_table(
        'integration_rate_limits',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('integration_credential_id', sa.String(36), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('api_endpoint', sa.String(255), nullable=False),
        sa.Column('requests_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('requests_limit', sa.Integer(), nullable=False),
        sa.Column('window_start_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('window_end_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_rate_limited', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('backoff_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['integration_credential_id'], ['integration_credentials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB'
    )
    op.create_unique_constraint('uc_credential_endpoint', 'integration_rate_limits', ['integration_credential_id', 'api_endpoint'])
    op.create_index('idx_backoff_until', 'integration_rate_limits', ['backoff_until'])

def downgrade():
    """Remove external integrations tables."""
    op.drop_table('integration_rate_limits')
    op.drop_table('integration_conflicts')
    op.drop_table('integration_sync_logs')
    op.drop_table('integration_sync_queue')
    op.drop_table('integration_mappings')
    op.drop_table('integration_credentials')
```

---

## Data Volume Considerations

### Expected Scale

```
For a project with:
- 1,000 items
- 100 GitHub repos
- 1 Linear workspace

Estimated records:
- Credentials: 1-3
- Mappings: ~1,000 (1 per item)
- Sync Queue: 10-100 (pending operations)
- Sync Logs: 1,000/day × 30 days = 30,000/month
- Conflicts: 10-50 per month
- Rate Limits: 5-10 (per API endpoint)
```

### Retention Policy

```python
# Archive old logs after 90 days
DELETE FROM integration_sync_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY)
AND success = TRUE;

# Keep failed syncs for 1 year
DELETE FROM integration_sync_logs
WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR)
AND success = FALSE;
```

---

## Performance Optimization

### Indexes Strategy

**Hot queries:**

```sql
-- Finding mappings by item
SELECT * FROM integration_mappings
WHERE tracertm_item_id = ? AND project_id = ?;
-- Uses: idx_item

-- Finding pending syncs
SELECT * FROM integration_sync_queue
WHERE status = 'pending' AND priority IN ('high', 'critical')
ORDER BY created_at ASC
LIMIT 100;
-- Uses: idx_priority_status

-- Sync logs for audit
SELECT * FROM integration_sync_logs
WHERE mapping_id = ?
ORDER BY created_at DESC;
-- Uses: idx_mapping

-- Rate limit checks
SELECT * FROM integration_rate_limits
WHERE integration_credential_id = ?
AND api_endpoint = ?;
-- Uses: uc_credential_endpoint
```

### Partitioning (Future)

For large-scale deployments, consider partitioning:

```sql
-- Partition integration_sync_logs by month
ALTER TABLE integration_sync_logs
PARTITION BY RANGE (MONTH(created_at)) (
    PARTITION p202501 VALUES LESS THAN (202502),
    PARTITION p202502 VALUES LESS THAN (202503),
    ...
);
```

