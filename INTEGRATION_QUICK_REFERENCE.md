# External Integrations - Quick Reference Guide

## Overview

TraceRTM External Integrations connect requirements/features to external systems:
- **GitHub** (commits, PRs, issues)
- **GitHub Projects** (board sync)
- **Linear** (issue tracking)

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────┐
│                    External Systems                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │   GitHub     │ │    Linear    │ │ GitHub Proj  │    │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘    │
│         │                │                │             │
│  Webhooks (real-time) + Polling (fallback)              │
└─────────┼────────────────┼────────────────┼─────────────┘
          │                │                │
┌─────────▼────────────────▼────────────────▼─────────────┐
│           TraceRTM External Integration Layer            │
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Webhook Handlers  │  API Clients   │  Sync Queue │ │
│  └────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Sync Processor  │  Conflict Resolver  │  Encryptor│ │
│  └────────────────────────────────────────────────────┘ │
└─────────┬──────────────────────────────────────────────┬─┘
          │                                              │
┌─────────▼─────────────────────────────────────────────▼─┐
│                    TraceRTM Database                     │
│  ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Items     │ │Mappings  │ │ Sync Q   │ │ Logs     │ │
│  └───────────┘ └──────────┘ └──────────┘ └──────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Core Concepts

### Integration Credential
Encrypted OAuth token or PAT for accessing external system.

```python
IntegrationCredential:
  - id: unique ID
  - provider: "github" | "linear"
  - credential_type: "oauth_token" | "personal_access_token"
  - encrypted_token: encrypted credential
  - status: "active" | "expired" | "invalid"
  - scopes: ["repo", "read:org"]
```

### Integration Mapping
Links a TraceRTM item to an external system item.

```python
IntegrationMapping:
  - tracertm_item_id: "item-123"
  - external_id: "octocat/repo#42"
  - direction: "bidirectional" | "push_only" | "pull_only"
  - status: "active" | "sync_error"
  - conflict_resolution: "manual" | "tracertm_wins" | "external_wins"
```

### Sync Queue
Tracks pending synchronization operations.

```python
IntegrationSyncQueue:
  - mapping_id: link to mapping
  - event: "item_created" | "item_updated" | "status_changed"
  - direction: "push" | "pull"
  - status: "pending" | "processing" | "completed" | "failed"
  - retry_count: attempt counter
```

## Authentication Flow

### OAuth (Recommended)

```
1. User clicks "Connect GitHub"
   ↓
2. Generate PKCE pair (code_verifier, code_challenge)
3. Redirect to GitHub OAuth endpoint
   ↓
4. User authorizes in GitHub
   ↓
5. GitHub redirects back with auth code
   ↓
6. Exchange code + code_verifier for token
7. Store encrypted token in database
   ↓
8. User can now create mappings
```

### Personal Access Token (Fallback)

```
1. User generates PAT in their account settings
2. User pastes PAT into TraceRTM form
3. Validate by making test API call
4. Store encrypted token in database
```

## Sync Operations

### Real-Time Sync (Webhook)

```
External System Event
  ↓
GitHub/Linear sends webhook to TraceRTM endpoint
  ↓
Verify webhook signature
  ↓
Parse event payload
  ↓
Find mapping for item
  ↓
Queue sync operation
  ↓
Process immediately or batch
  ↓
Update TraceRTM item
  ↓
Handle conflicts if needed
  ↓
Log result
```

### Polling Sync (Fallback)

```
Every 5-15 minutes:
  ↓
For each credential with mappings:
  ↓
Query external API for changes since last poll
  ↓
Compare with cached state
  ↓
Queue sync operations for changed items
  ↓
Process queue
```

### Manual Sync

```
User clicks "Sync Now" on mapping
  ↓
Fetch current state from external system
  ↓
Compare with TraceRTM item
  ↓
Queue operation with HIGH priority
  ↓
Process immediately
```

## Conflict Resolution

### Conflict Scenarios

1. **Both Modified** - Same field changed in both systems
2. **Delete vs Update** - One deleted, other modified
3. **Status Conflict** - Incompatible workflow states

### Resolution Strategies

| Strategy | Behavior | Best For |
|----------|----------|----------|
| Manual | Block sync, flag for user | Critical fields |
| Last-Write-Wins | Accept newer timestamp | Comments, descriptions |
| TraceRTM Wins | Always use TraceRTM value | Requirements-driven |
| External Wins | Always use external value | GitHub/Linear source of truth |

**Configuration:**
```python
# Global default
conflict_resolution_strategy: "manual"

# Per-field override
field_resolution_rules: {
    "status": "external_wins",      # GitHub status is truth
    "priority": "tracertm_wins",    # Keep TraceRTM priority
    "description": "last_write_wins" # Latest update wins
}
```

## API Quick Reference

### Credentials

```
POST   /api/v1/projects/{project_id}/integrations/credentials
       Create credential

GET    /api/v1/projects/{project_id}/integrations/credentials
       List all credentials

DELETE /api/v1/projects/{project_id}/integrations/credentials/{id}
       Delete/revoke credential

POST   /api/v1/projects/{project_id}/integrations/oauth/{provider}/start
       Start OAuth flow → returns oauth_url

POST   /api/v1/projects/{project_id}/integrations/oauth/callback
       Handle OAuth redirect → creates credential
```

### Mappings

```
POST   /api/v1/projects/{project_id}/integrations/mappings
       Create mapping

GET    /api/v1/projects/{project_id}/integrations/mappings
       List all mappings

PUT    /api/v1/projects/{project_id}/integrations/mappings/{id}
       Update mapping (direction, conflict strategy)

DELETE /api/v1/projects/{project_id}/integrations/mappings/{id}
       Delete mapping

POST   /api/v1/projects/{project_id}/integrations/mappings/{id}/sync
       Trigger manual sync
```

### Sync Status

```
GET    /api/v1/projects/{project_id}/integrations/sync-status
       Get overall status

GET    /api/v1/projects/{project_id}/integrations/sync-queue
       List pending syncs

GET    /api/v1/projects/{project_id}/integrations/sync-logs
       Get sync history

POST   /api/v1/projects/{project_id}/integrations/conflicts
       List conflicts

POST   /api/v1/projects/{project_id}/integrations/conflicts/{id}/resolve
       Resolve conflict
```

## Webhook Events

### GitHub Webhooks

```
Events to subscribe:
- push: New commits
- pull_request: PR created/updated/closed
- issues: Issues created/updated/closed
- projects_v2_item: Project board changes
```

### Linear Webhooks

```
Events to subscribe:
- Issue.created: New issue
- Issue.updated: Issue status/fields changed
- Issue.removed: Issue deleted
```

## Error Handling

### Retry Strategy

```
Attempt 1: Immediate
Attempt 2: Wait 60s  (60 × 2^0)
Attempt 3: Wait 120s (60 × 2^1)
Attempt 4: Wait 240s (60 × 2^2)
Max: 3600s (1 hour)
```

### Common Errors

| Error | Cause | Action |
|-------|-------|--------|
| `CredentialValidationError` | Token expired/revoked | User must refresh credential |
| `ExternalSystemError` | API down or network issue | Auto-retry with backoff |
| `RateLimitExceeded` | Too many API calls | Wait and retry (exponential) |
| `SyncConflictError` | Unresolvable conflict | Flag for manual resolution |
| `MappingNotFound` | Mapping deleted | Cancel sync operation |

## Rate Limits

| Provider | Limit | TraceRTM Handling |
|----------|-------|-------------------|
| GitHub REST | 5,000/hour | Batch operations, respect headers |
| GitHub GraphQL | 15,000/hour | Use for bulk operations |
| Linear | 10/second | Queue operations, respect headers |
| TraceRTM Sync | 10,000/hour | Prioritize, batch syncs |

## Data Flow Examples

### Example 1: Create GitHub Issue from TraceRTM

```
1. User creates mapping:
   TraceRTM Item #123 ↔ github/repo#42

2. User updates item in TraceRTM:
   Title: "Add authentication"

3. Sync processor detects change:
   event_type: "item_updated"
   direction: "push"

4. Queue sync operation:
   UPDATE github/repo#42
   title: "Add authentication"

5. GitHub API call:
   PATCH /repos/owner/repo/issues/42
   { "title": "Add authentication" }

6. GitHub responds 200:
   Issue updated

7. Log success:
   mapping_id, sync_timestamp, direction, changes
```

### Example 2: Detect and Resolve Conflict

```
1. GitHub PR #42 status → "merged"
   Linear #456 status → "in progress"
   (Mapped together, both changed independently)

2. Conflict detected:
   field: "status"
   tracertm_value: "in progress"
   external_value: "merged"

3. Check conflict_resolution_strategy:
   status: "external_wins"

4. Resolve automatically:
   Update TraceRTM item status → "merged"
   Log: conflict_resolution_used: "external_wins"

5. If strategy was "manual":
   Flag in UI
   Wait for user decision
   Apply when user chooses winner
```

## Security Checklist

- [ ] Encryption: AES-256-GCM for all tokens
- [ ] OAuth: PKCE flow with state validation
- [ ] Webhooks: HMAC-SHA256 signature verification
- [ ] Rate Limiting: Per-credential rate limiters
- [ ] Input Validation: All external IDs sanitized
- [ ] Encryption Key: Stored in environment, rotated annually
- [ ] Audit Log: All operations logged with timestamps
- [ ] Credential Rotation: Support for token refresh
- [ ] Permission Scoping: Minimal OAuth scopes requested
- [ ] Revocation: Support for credential revocation

## Monitoring Checklist

- [ ] Sync success rate tracked
- [ ] Error rate by type monitored
- [ ] Webhook delivery failures alerted
- [ ] Rate limit hits logged
- [ ] Credential validity checked regularly
- [ ] Sync queue backlog monitored
- [ ] Conflict rate tracked
- [ ] Sync latency measured
- [ ] User adoption metrics collected
- [ ] Dashboards created for ops team

## Testing Checklist

- [ ] Unit tests for encryption/decryption
- [ ] Unit tests for conflict detection
- [ ] Unit tests for retry logic
- [ ] Integration tests for GitHub sync
- [ ] Integration tests for Linear sync
- [ ] E2E tests for OAuth flow
- [ ] E2E tests for full sync cycle
- [ ] Mock external APIs for testing
- [ ] Performance tests for sync processor
- [ ] Security tests (HMAC verification, etc)

## Deployment Checklist

- [ ] Database migrations tested
- [ ] Encryption key configured
- [ ] OAuth apps registered with GitHub/Linear
- [ ] Webhook URLs configured
- [ ] SSL certificates valid
- [ ] Rate limits configured
- [ ] Monitoring/alerting enabled
- [ ] Rollback procedure documented
- [ ] Feature flag created (canary deploy)
- [ ] On-call team trained

## Common Scenarios

### Scenario: User wants to stop syncing

```
1. User deletes mapping
2. IntegrationMapping record removed
3. Pending sync operations cancelled
4. No more changes synced between systems
5. Data remains as-is (no cleanup)
```

### Scenario: Credential expires

```
1. Webhook fails with 401 Unauthorized
2. System marks credential as "invalid"
3. Sync processor stops processing for this credential
4. User notified: "Please refresh GitHub credential"
5. User clicks refresh → OAuth flow
6. Syncing resumes
```

### Scenario: Too many conflicts

```
1. Conflicts detected on mapping
2. Sync paused (manual resolution required)
3. User views conflict in UI
4. User chooses winner
5. Sync resumes
6. Both systems now consistent
```

### Scenario: Rate limit hit

```
1. GitHub API returns 429 (rate limited)
2. System extracts retry-after header (3600s)
3. Sync operation requeued with backoff
4. User notified: "Syncing paused due to rate limit"
5. Automatic retry after 1 hour
6. Resume normal operation
```

