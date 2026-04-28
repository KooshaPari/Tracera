# TraceRTM Unified Local Storage Architecture

## Overview

This document defines the hybrid SQLite + Markdown local storage system for TraceRTM clients (CLI, TUI, Desktop). The design prioritizes:

1. **Machine parseability** - SQLite for queries, relationships, sync state
2. **Human/LLM parseability** - Markdown files for readable artifacts
3. **Offline-first** - Work locally, sync when connected
4. **Portability** - No vendor lock-in, standard formats

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      TraceRTM Client                            │
│  (CLI / TUI / Desktop)                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐     ┌─────────────────┐                   │
│  │  Local Storage  │     │   API Client    │                   │
│  │    Manager      │────▶│   (httpx/reqwest)│                   │
│  └────────┬────────┘     └────────┬────────┘                   │
│           │                       │                             │
│           ▼                       ▼                             │
│  ┌─────────────────────────────────────────┐                   │
│  │           Sync Engine                    │                   │
│  │  - Conflict resolution (vector clocks)  │                   │
│  │  - Retry queue                          │                   │
│  │  - Delta sync                           │                   │
│  └─────────────────────────────────────────┘                   │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────┐
│  │                   Storage Layer                              │
│  │                                                              │
│  │  ┌──────────────────┐    ┌──────────────────────────────┐   │
│  │  │     SQLite       │    │      Markdown Files          │   │
│  │  │  (tracertm.db)   │    │   (.tracertm/projects/)      │   │
│  │  │                  │    │                              │   │
│  │  │  - Relationships │    │  project-name/               │   │
│  │  │  - Sync metadata │    │  ├── README.md               │   │
│  │  │  - Search index  │    │  ├── epics/                  │   │
│  │  │  - Change queue  │    │  │   ├── EPIC-001.md         │   │
│  │  │  - Conflict log  │    │  │   └── EPIC-002.md         │   │
│  │  │                  │    │  ├── stories/                │   │
│  │  └──────────────────┘    │  │   ├── STORY-001.md        │   │
│  │                          │  │   └── STORY-002.md        │   │
│  │                          │  ├── tests/                  │   │
│  │                          │  │   └── TEST-001.md         │   │
│  │                          │  └── .meta/                  │   │
│  │                          │      └── links.yaml          │   │
│  │                          └──────────────────────────────┘   │
│  └─────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend API                                  │
│               (GCP Cloud Run / Self-hosted)                     │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  PostgreSQL │  │    Neo4j    │  │    Redis    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## Storage Components

### 1. SQLite Database (`~/.tracertm/tracertm.db`)

The SQLite database handles structured data and relationships:

```sql
-- Core tables (same as desktop app)
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    synced_at TEXT,
    remote_id TEXT,           -- Server-side ID
    version INTEGER DEFAULT 1,
    is_deleted INTEGER DEFAULT 0
);

CREATE TABLE items (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    item_type TEXT NOT NULL,  -- epic, story, test, task, etc.
    external_id TEXT,         -- EPIC-001, STORY-002, etc.
    title TEXT NOT NULL,
    content_hash TEXT,        -- Hash of markdown content
    status TEXT NOT NULL,
    priority TEXT,
    owner TEXT,
    parent_id TEXT,
    version INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    synced_at TEXT,
    remote_id TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (parent_id) REFERENCES items(id)
);

CREATE TABLE links (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    link_type TEXT NOT NULL,  -- implements, tests, blocks, etc.
    metadata TEXT,            -- JSON for additional data
    created_at TEXT NOT NULL,
    synced_at TEXT,
    remote_id TEXT,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (source_id) REFERENCES items(id),
    FOREIGN KEY (target_id) REFERENCES items(id)
);

-- Sync management
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- project, item, link
    entity_id TEXT NOT NULL,
    operation TEXT NOT NULL,    -- create, update, delete
    payload TEXT NOT NULL,      -- JSON of changes
    created_at TEXT NOT NULL,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    UNIQUE(entity_type, entity_id, operation)
);

CREATE TABLE sync_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Full-text search
CREATE VIRTUAL TABLE items_fts USING fts5(
    title, content, external_id,
    content='items',
    content_rowid='rowid'
);
```

### 2. Markdown Files (`~/.tracertm/projects/<name>/`)

Human-readable artifacts with YAML frontmatter:

```
.tracertm/
└── projects/
    └── my-project/
        ├── README.md           # Project overview
        ├── epics/
        │   ├── EPIC-001.md
        │   └── EPIC-002.md
        ├── stories/
        │   ├── STORY-001.md
        │   └── STORY-002.md
        ├── tests/
        │   └── TEST-001.md
        ├── tasks/
        │   └── TASK-001.md
        └── .meta/
            ├── links.yaml      # Traceability links
            ├── agents.yaml     # Agent configurations
            └── config.yaml     # Project settings
```

#### Item Markdown Format

```markdown
---
id: "550e8400-e29b-41d4-a716-446655440000"
external_id: "EPIC-001"
type: epic
status: in_progress
priority: high
owner: "@team-lead"
parent: null
version: 3
created: 2024-01-15T10:30:00Z
updated: 2024-01-20T14:22:00Z
tags:
  - authentication
  - security
  - mvp
links:
  - type: implements
    target: "STORY-001"
  - type: implements
    target: "STORY-002"
---

# User Authentication System

## Description

Implement a complete user authentication system supporting OAuth2, JWT tokens,
and session management.

## Acceptance Criteria

- [ ] Users can sign up with email/password
- [ ] OAuth2 integration with Google, GitHub
- [ ] JWT token refresh mechanism
- [ ] Session timeout after 24 hours
- [x] Password reset flow

## Notes

This epic covers all authentication-related functionality for the MVP release.

### Technical Considerations

- Use bcrypt for password hashing
- Store refresh tokens in Redis
- Implement rate limiting on auth endpoints

## History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3 | 2024-01-20 | @dev | Added OAuth requirements |
| 2 | 2024-01-18 | @pm | Updated acceptance criteria |
| 1 | 2024-01-15 | @pm | Initial creation |
```

#### Links YAML Format (`.meta/links.yaml`)

```yaml
# Traceability links for the project
# Format optimized for both machine parsing and human readability

links:
  - id: "link-001"
    source: "EPIC-001"
    target: "STORY-001"
    type: implements
    created: 2024-01-15T10:30:00Z

  - id: "link-002"
    source: "STORY-001"
    target: "TEST-001"
    type: tested_by
    created: 2024-01-16T09:00:00Z

  - id: "link-003"
    source: "STORY-002"
    target: "STORY-001"
    type: depends_on
    created: 2024-01-17T11:00:00Z

# Link types:
# - implements: Epic → Story, Story → Task
# - tested_by: Story/Task → Test
# - depends_on: Any → Any
# - blocks: Any → Any
# - relates_to: Any → Any
```

## Sync Engine

### Sync Flow

```
1. Local Change Detection
   └─▶ Hash markdown content
   └─▶ Compare with stored content_hash
   └─▶ Queue changes in sync_queue

2. Sync Trigger (manual or periodic)
   └─▶ Check network connectivity
   └─▶ Authenticate with API

3. Upload Phase
   └─▶ Process sync_queue in order
   └─▶ Send changes to /api/sync/upload
   └─▶ Mark successful items as synced

4. Download Phase
   └─▶ GET /api/sync/changes?since={last_sync}
   └─▶ Merge remote changes

5. Conflict Resolution
   └─▶ Compare versions
   └─▶ Apply resolution strategy
   └─▶ Create conflict backup if needed
```

### Conflict Resolution Strategies

```python
class ConflictStrategy(Enum):
    LAST_WRITE_WINS = "last_write_wins"      # Default: newest version wins
    LOCAL_WINS = "local_wins"                 # Prefer local changes
    REMOTE_WINS = "remote_wins"               # Prefer server changes
    MANUAL = "manual"                         # Create conflict file for review

# Vector clock for ordering
{
    "client_id": "cli-abc123",
    "version": 5,
    "timestamp": "2024-01-20T14:22:00Z",
    "parent_version": 4
}
```

## API Endpoints for Sync

The backend needs these endpoints:

```
POST /api/sync/upload
  Body: { changes: [...], client_id: string, last_sync: timestamp }
  Response: { applied: [...], conflicts: [...], server_time: timestamp }

GET /api/sync/changes
  Params: since=timestamp, project_id=optional
  Response: { changes: [...], server_time: timestamp }

POST /api/sync/resolve
  Body: { conflict_id: string, resolution: "local" | "remote" | "merged", merged_content?: string }
  Response: { resolved: true }

GET /api/sync/status
  Response: { last_sync: timestamp, pending_changes: number, online: boolean }
```

## Directory Structure for Clients

### Python (CLI/TUI)

```
src/tracertm/
├── storage/
│   ├── __init__.py
│   ├── local_storage.py      # SQLite + Markdown manager
│   ├── markdown_parser.py    # Parse/write markdown with frontmatter
│   ├── sync_engine.py        # Sync logic
│   └── conflict_resolver.py  # Conflict handling
├── api/
│   ├── __init__.py
│   ├── client.py             # HTTP client (httpx)
│   └── models.py             # API request/response types
```

### Rust (Desktop/Tauri)

```
src-tauri/src/
├── storage/
│   ├── mod.rs
│   ├── local_storage.rs      # SQLite + Markdown manager
│   ├── markdown.rs           # Parse/write markdown
│   ├── sync.rs               # Sync engine
│   └── conflict.rs           # Conflict resolution
├── api/
│   ├── mod.rs
│   ├── client.rs             # HTTP client (reqwest)
│   └── models.rs             # API types
```

## Implementation Priority

### Phase 1: Local Storage (Week 1-2)
1. SQLite schema for CLI/TUI (reuse from desktop)
2. Markdown file format implementation
3. Bidirectional sync between SQLite ↔ Markdown
4. Local CRUD operations

### Phase 2: Sync Engine (Week 3-4)
1. Change detection and queueing
2. API client implementation
3. Upload/download sync
4. Basic conflict resolution (last-write-wins)

### Phase 3: Advanced Features (Week 5-6)
1. Vector clocks for ordering
2. Manual conflict resolution UI
3. Offline queue persistence
4. Real-time sync via WebSocket (optional)

## Configuration

```yaml
# ~/.tracertm/config.yaml
storage:
  base_dir: ~/.tracertm
  database: tracertm.db
  markdown_enabled: true

sync:
  enabled: true
  api_url: https://api.tracertm.io
  interval_seconds: 300  # 5 minutes
  conflict_strategy: last_write_wins
  retry_max: 3

auth:
  token_path: ~/.tracertm/auth.json
  # Token refresh handled automatically
```

## Benefits of This Architecture

1. **LLM Agent Friendly**: Markdown files can be read/written by AI agents directly
2. **Human Readable**: Engineers can view/edit requirements in their editor
3. **Git Compatible**: Markdown files can be version controlled
4. **Offline First**: Full functionality without network
5. **Fast Queries**: SQLite for complex queries and relationships
6. **Portable**: Standard formats, no vendor lock-in
7. **Sync Resilient**: Queue-based sync handles network issues gracefully

## Migration from Current Implementation

### CLI (Python)
- Current: SQLAlchemy with direct DB access
- Migration: Add `LocalStorageManager` wrapper that:
  1. Uses existing SQLite operations
  2. Generates/parses Markdown on save/load
  3. Adds sync queue population

### Desktop (Tauri)
- Current: SQLite + JSON store sync
- Migration:
  1. Add Markdown file generation
  2. Replace JSON store with YAML config
  3. Update sync to use new endpoints

### TUI (Python/Textual)
- Current: Direct database access
- Migration: Use same `LocalStorageManager` as CLI
