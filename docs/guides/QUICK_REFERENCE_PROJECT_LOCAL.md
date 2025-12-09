# Quick Reference: Project-Local Item Commands

## Overview

Item commands now support project-local `.trace/` directories with automatic detection.

## Basic Usage

### Auto-Detect Project (Recommended)

Navigate to your project directory and run commands:

```bash
cd /path/to/my-project
rtm item create "Feature Name" --view FEATURE --type epic
rtm item list --type epic
rtm item update EPIC-001 --status in_progress
rtm item delete EPIC-001
```

The CLI will automatically:
1. Look for `.trace/` in current directory
2. Walk up parent directories to find `.trace/`
3. Fall back to global storage if not found

### Explicit Project Path

Specify project explicitly with `--project`:

```bash
rtm item create "Feature" --view FEATURE --type epic --project /path/to/project
rtm item list --project /path/to/project
rtm item update EPIC-001 --status done --project /path/to/project
```

## Directory Structure

When you create items, they're stored in `.trace/`:

```
my-project/
├── src/
├── tests/
└── .trace/
    ├── project.yaml          # Auto-updated counters
    ├── epics/
    │   ├── EPIC-001.md
    │   └── EPIC-002.md
    ├── stories/
    │   └── STORY-001.md
    ├── tests/
    │   └── TEST-001.md
    ├── tasks/
    │   └── TASK-001.md
    └── .meta/
        ├── links.yaml        # Traceability links
        └── sync.yaml         # Sync state (gitignored)
```

## External ID Counters

Counters in `project.yaml` auto-increment:

```yaml
name: my-awesome-project
description: A project to build awesome things
version: 1.0.0

counters:
  epic: 2      # Next: EPIC-003
  story: 5     # Next: STORY-006
  test: 3      # Next: TEST-004
  task: 10     # Next: TASK-011
```

## Markdown Format

Items are stored as markdown with YAML frontmatter:

```markdown
---
id: "550e8400-e29b-41d4-a716-446655440000"
external_id: EPIC-001
type: epic
status: in_progress
priority: high
owner: "@alice"
parent: null
version: 2
created: 2024-01-15T10:30:00Z
updated: 2024-01-20T14:22:00Z
tags:
  - authentication
  - security
links:
  - type: implements
    target: STORY-001
---

# User Authentication

## Description

Implement a complete user authentication system...
```

## Command Examples

### Create Items

```bash
# Epic
rtm item create "User Authentication" \
  --view FEATURE \
  --type epic \
  --priority high \
  --owner alice

# Story under epic
rtm item create "Login Page" \
  --view FEATURE \
  --type story \
  --parent EPIC-001 \
  --description "Create login UI with email/password"

# Test for story
rtm item create "Login Tests" \
  --view TEST \
  --type test \
  --parent STORY-001
```

### Update Items

```bash
# Change status
rtm item update EPIC-001 --status in_progress

# Update multiple fields
rtm item update EPIC-001 \
  --title "User Auth System" \
  --priority high \
  --owner bob

# Add metadata
rtm item update EPIC-001 \
  --metadata '{"sprint": 3, "estimate": "5 days"}'
```

### List Items

```bash
# List all epics
rtm item list --type epic

# Filter by status
rtm item list --type story --status in_progress

# Limit results
rtm item list --limit 10

# JSON output
rtm item list --type epic --json
```

### Delete Items

```bash
# With confirmation
rtm item delete EPIC-001

# Force delete (no prompt)
rtm item delete EPIC-001 --force
```

## Output Examples

### Create Output

```
✓ Created EPIC-003: User Authentication
  File: .trace/epics/EPIC-003.md
  Project: my-awesome-project
  Indexed: ~/.tracertm/tracertm.db
```

### Update Output

```
✓ Updated EPIC-003: User Authentication
  Version: 2
  Markdown updated in .trace/epics/EPIC-003.md
```

### Delete Output

```
✓ Deleted EPIC-003
  Markdown file removed: .trace/epics/EPIC-003.md
  SQLite index updated
```

### List Output

```
Items in my-awesome-project (3)
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┓
┃ External  ┃ Title               ┃ Type ┃ Status      ┃ Priority ┃ Owner ┃
┃ ID        ┃                     ┃      ┃             ┃          ┃       ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━┩
│ EPIC-001  │ User Authentication │ epic │ in_progress │ high     │ alice │
│ EPIC-002  │ Payment System      │ epic │ todo        │ medium   │ bob   │
│ EPIC-003  │ Admin Dashboard     │ epic │ done        │ low      │       │
└───────────┴─────────────────────┴──────┴─────────────┴──────────┴───────┘
```

## Fallback Behavior

If not in a project directory:

```bash
$ rtm item create "Test" --view FEATURE --type epic

[yellow]Not in a project directory. Using global storage.[/yellow]
✓ Item created successfully!
  ID: abc123def456
  External ID: EPIC-001
  Markdown: ~/.tracertm/projects/my-project/epics/EPIC-001.md
```

## Git Integration

Add to `.gitignore`:

```gitignore
# TraceRTM sync state (local only)
.trace/.meta/sync.yaml
```

Commit everything else:

```bash
git add .trace/
git commit -m "Add EPIC-001: User Authentication"
```

## Common Workflows

### Start New Feature

```bash
# Create epic
rtm item create "User Profile" --view FEATURE --type epic

# Create stories
rtm item create "Profile View" --view FEATURE --type story --parent EPIC-001
rtm item create "Edit Profile" --view FEATURE --type story --parent EPIC-001

# Create tests
rtm item create "Profile Tests" --view TEST --type test --parent STORY-001
```

### Update Sprint Status

```bash
# Mark story in progress
rtm item update STORY-001 --status in_progress

# Complete story
rtm item update STORY-001 --status done

# List remaining work
rtm item list --type story --status todo
```

### Search Across Projects

```bash
# Use global search (queries SQLite index)
rtm search "authentication"

# List from specific project
rtm item list --project /path/to/project1
rtm item list --project /path/to/project2
```

## Troubleshooting

### "Not in a TraceRTM project"

Run `rtm init` to create `.trace/` structure:

```bash
cd /path/to/my-project
rtm init
```

### Counter Out of Sync

Manually edit `project.yaml`:

```yaml
counters:
  epic: 5  # Set to highest existing + 1
```

### Item Not Found

Verify item exists in SQLite:

```bash
rtm item list --type epic
```

Re-index if needed:

```bash
rtm index
```

## Advanced Usage

### Metadata

Store custom fields:

```bash
rtm item create "Feature" --view FEATURE --type epic \
  --metadata '{
    "sprint": 3,
    "estimate": "5 days",
    "labels": ["mvp", "critical"]
  }'
```

### Links

Links are stored in `.meta/links.yaml`:

```yaml
links:
  - source: EPIC-001
    target: STORY-001
    type: implements
    created: 2024-01-15T10:30:00Z
```

### Local-Only Mode

Prevent sync to remote:

```bash
rtm item create "Feature" --view FEATURE --type epic --local
```

## See Also

- [PROJECT_LOCAL_STORAGE.md](docs/PROJECT_LOCAL_STORAGE.md) - Architecture details
- [ITEM_COMMAND_UPDATE_SUMMARY.md](ITEM_COMMAND_UPDATE_SUMMARY.md) - Implementation details
