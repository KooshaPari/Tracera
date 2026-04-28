# TraceRTM Project-Local Storage Architecture

## Overview

TraceRTM uses a **two-tier storage model**:

1. **Project-local `.trace/`** - Markdown files in the project repository (version-controlled)
2. **Global `~/.tracertm/`** - SQLite index for fast queries (auto-managed)

This design ensures:
- Requirements live WITH the code (git-versioned)
- LLM agents can read/write directly to `.trace/` files
- Fast queries via SQLite index (auto-synced from `.trace/`)
- Multi-project dashboard via global index

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Project Repository                                  │
│                                                                              │
│  my-project/                                                                 │
│  ├── src/                           # Source code                            │
│  ├── tests/                         # Test code                              │
│  ├── .trace/                        # ← TraceRTM requirements (git-tracked)  │
│  │   ├── project.yaml               # Project metadata                       │
│  │   ├── epics/                                                              │
│  │   │   ├── EPIC-001.md            # Epic with YAML frontmatter            │
│  │   │   └── EPIC-002.md                                                     │
│  │   ├── stories/                                                            │
│  │   │   ├── STORY-001.md                                                    │
│  │   │   └── STORY-002.md                                                    │
│  │   ├── tests/                                                              │
│  │   │   └── TEST-001.md                                                     │
│  │   ├── tasks/                                                              │
│  │   ├── docs/                      # Project documentation                  │
│  │   └── .meta/                                                              │
│  │       ├── links.yaml             # Traceability matrix                    │
│  │       ├── agents.yaml            # Agent configurations                   │
│  │       └── sync.yaml              # Sync state (gitignored)                │
│  └── .gitignore                     # Includes .trace/.meta/sync.yaml        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Auto-sync (file watcher)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Global Index (~/.tracertm/)                          │
│                                                                              │
│  ~/.tracertm/                                                                │
│  ├── config.yaml                    # Global TraceRTM config                 │
│  ├── tracertm.db                    # SQLite index (all projects)            │
│  │   ├── projects                   # Project registry                       │
│  │   │   - id, name, path, last_indexed                                      │
│  │   ├── items                      # Indexed items (from all .trace/)       │
│  │   │   - id, project_id, type, title, content_hash, ...                   │
│  │   ├── links                      # Indexed links                          │
│  │   ├── items_fts                  # Full-text search                       │
│  │   └── sync_queue                 # Remote API sync queue                  │
│  └── auth.json                      # API authentication tokens              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ API Sync (when online)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Backend API                                        │
│                     (GCP Cloud Run / Self-hosted)                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Project-Local `.trace/` Structure

```
.trace/
├── project.yaml              # Project metadata
├── epics/
│   ├── EPIC-001.md
│   └── EPIC-002.md
├── stories/
│   ├── STORY-001.md
│   └── STORY-002.md
├── wireframes/               # Design wireframes with Figma integration
│   ├── WF-001.md
│   └── WF-002.md
├── tests/
│   └── TEST-001.md
├── tasks/
│   └── TASK-001.md
├── docs/
│   ├── architecture.md
│   └── api-design.md
├── changes/                  # RFC-style change proposals (like openspec)
│   └── add-auth-system/
│       ├── proposal.md
│       ├── tasks.md
│       └── specs/
│           └── auth/
│               └── spec.md
└── .meta/
    ├── links.yaml            # Traceability links
    ├── agents.yaml           # Agent configurations
    └── sync.yaml             # Sync state (gitignored)
```

### project.yaml

```yaml
# .trace/project.yaml
name: my-awesome-project
description: A project to build awesome things
version: 1.0.0

# Auto-generated counters for external IDs
counters:
  epic: 2      # Next: EPIC-003
  story: 5     # Next: STORY-006
  test: 3      # Next: TEST-004
  task: 10     # Next: TASK-011
  wireframe: 1 # Next: WF-002

# Project-level settings
settings:
  default_priority: medium
  default_status: todo
  auto_link_commits: true

# Team/ownership
team:
  - name: Alice
    role: pm
    email: alice@example.com
  - name: Bob
    role: dev
    email: bob@example.com

# Integration hooks
hooks:
  on_item_create: []
  on_item_update: []
  on_link_create: []
```

### Item Markdown Format

```markdown
---
# .trace/epics/EPIC-001.md
id: "550e8400-e29b-41d4-a716-446655440000"
type: epic
status: in_progress
priority: high
owner: "@alice"
created: 2024-01-15T10:30:00Z
updated: 2024-01-20T14:22:00Z
version: 3
tags:
  - authentication
  - security
  - mvp
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

## History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3 | 2024-01-20 | @dev | Added OAuth requirements |
| 2 | 2024-01-18 | @pm | Updated acceptance criteria |
| 1 | 2024-01-15 | @pm | Initial creation |
```

### links.yaml

```yaml
# .trace/.meta/links.yaml
links:
  - source: EPIC-001
    target: STORY-001
    type: implements
    created: 2024-01-15T10:30:00Z

  - source: STORY-001
    target: TEST-001
    type: tested_by
    created: 2024-01-16T09:00:00Z

  - source: STORY-002
    target: STORY-001
    type: depends_on
    created: 2024-01-17T11:00:00Z
```

## CLI Commands

### Initialize Project

```bash
# In a project directory
rtm init

# Creates .trace/ structure:
# .trace/
# ├── project.yaml
# ├── epics/
# ├── stories/
# ├── tests/
# ├── tasks/
# ├── docs/
# └── .meta/
#     ├── links.yaml
#     └── agents.yaml

# Also adds to .gitignore:
# .trace/.meta/sync.yaml
```

### Register Existing Project

```bash
# If .trace/ already exists (from git clone)
rtm register

# Indexes .trace/ into ~/.tracertm/tracertm.db
```

### Create Items

```bash
# Creates .trace/epics/EPIC-003.md
rtm create epic "User Authentication"

# Creates .trace/stories/STORY-006.md
rtm create story "Login Page" --parent EPIC-003

# Creates .trace/tests/TEST-004.md
rtm create test "Login Tests" --covers STORY-006
```

### List/Query Items

```bash
# Fast query from SQLite index
rtm list --type epic --status in_progress

# Full-text search
rtm search "authentication"

# Traceability
rtm link graph EPIC-001
```

### Sync Commands

```bash
# Index .trace/ → SQLite (auto-runs on changes)
rtm index

# Sync SQLite → Remote API
rtm sync push

# Sync Remote API → SQLite → .trace/
rtm sync pull

# Full bidirectional sync
rtm sync
```

## File Watcher (Auto-Index)

When running `rtm watch` or using the TUI/Desktop app, TraceRTM watches `.trace/` for changes:

```python
# Pseudocode
watch(".trace/**/*.md", ".trace/**/*.yaml")
on_change:
    parse_file(changed_path)
    update_sqlite_index(parsed_data)
    if auto_sync_enabled:
        queue_for_remote_sync(changed_data)
```

## Sync Flow

### Local Edit → Global Index → Remote

```
1. User edits .trace/epics/EPIC-001.md
2. File watcher detects change
3. Parser extracts frontmatter + content
4. SQLite index updated (items table)
5. Change queued for remote sync
6. On next sync: uploaded to API
```

### Remote Change → Global Index → Local

```
1. rtm sync pull
2. API returns changes since last_sync
3. Changes written to SQLite index
4. For each changed item:
   - Generate markdown with frontmatter
   - Write to .trace/{type}s/{external_id}.md
5. Update sync timestamps
```

### Conflict Resolution

When both local and remote changed:

```
1. Detect conflict (different content_hash + remote version > local)
2. Based on strategy:
   - last_write_wins: Use newer timestamp
   - local_wins: Keep local, mark remote as overwritten
   - remote_wins: Accept remote, backup local
   - manual: Create .trace/{type}s/{id}.conflict.md for review
```

## Integration with Agents

LLM agents can directly read/write `.trace/` files:

```python
# Agent reading requirements
with open(".trace/epics/EPIC-001.md") as f:
    content = f.read()
    # Parse YAML frontmatter
    # Understand requirements
    # Generate code

# Agent creating a task
task_content = '''---
id: "new-uuid"
type: task
status: todo
priority: high
owner: "@agent"
created: 2024-01-20T15:00:00Z
---

# Implement login form validation

## Description
Add client-side validation to the login form...
'''
with open(".trace/tasks/TASK-011.md", "w") as f:
    f.write(task_content)

# TraceRTM file watcher auto-indexes the new task
```

## Git Integration

### Recommended .gitignore

```gitignore
# TraceRTM sync state (local only)
.trace/.meta/sync.yaml

# Optional: ignore agent-generated tasks
# .trace/tasks/*.agent.md
```

### Commit Hooks

```bash
# pre-commit: Validate .trace/ files
rtm validate

# post-commit: Auto-link commit to items
rtm link commit HEAD
```

## Migration from Old Structure

If you have `~/.tracertm/projects/` with markdown files:

```bash
# Export project to repo-local .trace/
rtm migrate --project my-project --to ./

# This creates:
# ./.trace/ with all items from ~/.tracertm/projects/my-project/
```

## Benefits

1. **Version Control**: Requirements tracked with code
2. **Agent-Friendly**: Direct file access for LLM agents
3. **Fast Queries**: SQLite index for complex queries
4. **Offline-First**: Works without network
5. **Multi-Project**: Global index supports dashboard views
6. **Standard Formats**: Markdown + YAML, no lock-in
