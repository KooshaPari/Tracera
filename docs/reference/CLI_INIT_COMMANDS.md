# TraceRTM Init Commands

This document describes the new project-local `.trace/` initialization and management commands.

## Overview

TraceRTM now supports **project-local storage** in addition to the global `~/.tracertm/` directory. This enables:

- Requirements stored WITH the code (git-versioned)
- Direct file access for LLM agents
- Fast queries via SQLite index
- Multi-project dashboard

## Architecture

```
Project Repository                      Global Index (~/.tracertm/)
├── src/                               ├── config.yaml
├── tests/                             ├── tracertm.db (SQLite)
├── .trace/                            │   ├── projects (registry)
│   ├── project.yaml                   │   ├── items (indexed)
│   ├── epics/                         │   ├── links (indexed)
│   ├── stories/                       │   └── items_fts (search)
│   ├── tests/                         └── auth.json
│   ├── tasks/
│   ├── docs/
│   └── .meta/
│       ├── links.yaml
│       ├── agents.yaml
│       └── sync.yaml (gitignored)
└── .gitignore
```

## Commands

### `rtm init`

Initialize a new `.trace/` directory structure in the current or specified directory.

**Usage:**
```bash
rtm init [OPTIONS]
```

**Options:**
- `--name NAME, -n NAME` - Project name (defaults to directory name)
- `--path PATH, -p PATH` - Path to create .trace/ (defaults to current directory)
- `--description DESC, -d DESC` - Project description

**Examples:**

```bash
# Initialize in current directory
rtm init

# Initialize with custom name
rtm init --name my-project

# Initialize in specific directory
rtm init --path /path/to/project --name my-project

# Initialize with description
rtm init --name my-project --description "My awesome project"
```

**What it does:**

1. Creates `.trace/` directory structure:
   ```
   .trace/
   ├── project.yaml              # Project metadata and counters
   ├── epics/                    # Epic markdown files
   ├── stories/                  # Story markdown files
   ├── tests/                    # Test markdown files
   ├── tasks/                    # Task markdown files
   ├── docs/                     # Project documentation
   └── .meta/
       ├── links.yaml            # Traceability links
       ├── agents.yaml           # Agent configurations
       └── sync.yaml             # Sync state (gitignored)
   ```

2. Creates `project.yaml` with:
   - Project name and description
   - Auto-increment counters for external IDs (EPIC-001, STORY-001, etc.)
   - Default settings
   - Team members (empty initially)
   - Hooks for automation

3. Adds `.trace/.meta/sync.yaml` to `.gitignore` (if git repo)

4. Registers project in global `~/.tracertm/tracertm.db`

5. Sets as current project

**Output:**
```
Initializing TraceRTM project: my-project

✓ Created .trace/ directory structure

.trace/
├── project.yaml
├── epics/ (0 files)
├── stories/ (0 files)
├── tests/ (0 files)
├── tasks/ (0 files)
├── docs/ (0 files)
└── .meta/
    ├── links.yaml
    ├── agents.yaml
    └── sync.yaml (gitignored)

✓ Added .trace/.meta/sync.yaml to .gitignore
✓ Registered project in /Users/you/.tracertm/tracertm.db
Project ID: 24f2ba95-ac74-4019-aee6-21729c07afed

╭──────────────────────────────── Success ─────────────────────────────────╮
│ ✓ Project 'my-project' initialized successfully!                         │
│                                                                          │
│ Local: /path/to/project/.trace                                           │
│ Global DB: /Users/you/.tracertm/tracertm.db                              │
│                                                                          │
│ Next steps:                                                              │
│   • Create items: rtm create epic "My Epic"                              │
│   • List items: rtm list                                                 │
│   • Index changes: rtm index                                             │
╰──────────────────────────────────────────────────────────────────────────╯
```

### `rtm register`

Register an existing `.trace/` directory (e.g., after `git clone`) in the global database.

**Usage:**
```bash
rtm register [OPTIONS]
```

**Options:**
- `--path PATH, -p PATH` - Path containing .trace/ (defaults to current directory)

**Examples:**

```bash
# Register in current directory
rtm register

# Register in specific directory
rtm register --path /path/to/cloned/project
```

**What it does:**

1. Reads `project.yaml` from existing `.trace/` directory
2. Registers project in global `~/.tracertm/tracertm.db`
3. Indexes all items from `.trace/` into SQLite:
   - Parses all markdown files in epics/, stories/, tests/, tasks/
   - Extracts frontmatter and content
   - Creates database records
   - Indexes links from `.meta/links.yaml`
4. Updates `.meta/sync.yaml` with last_indexed timestamp
5. Sets as current project

**Output:**
```
Registering TraceRTM project: my-project

✓ Registered project in /Users/you/.tracertm/tracertm.db
Project ID: f8724a51-50be-408d-98ac-eff094ccaabf

✓ Indexed items:
  • Epics: 5
  • Stories: 23
  • Tests: 12
  • Tasks: 8
  • Links: 45

╭──────────────────────────────── Success ─────────────────────────────────╮
│ ✓ Project 'my-project' registered successfully!                          │
│                                                                          │
│ Local: /path/to/project/.trace                                           │
│ Global DB: /Users/you/.tracertm/tracertm.db                              │
│ Indexed: 48 items                                                        │
│                                                                          │
│ Next steps:                                                              │
│   • List items: rtm list                                                 │
│   • Create items: rtm create epic "My Epic"                              │
│   • Re-index: rtm index                                                  │
╰──────────────────────────────────────────────────────────────────────────╯
```

### `rtm index`

Re-index `.trace/` directory into SQLite database.

**Usage:**
```bash
rtm index [OPTIONS]
```

**Options:**
- `--path PATH, -p PATH` - Path containing .trace/ (defaults to current directory)
- `--full` - Force full re-index vs incremental

**Examples:**

```bash
# Incremental index (default)
rtm index

# Full re-index
rtm index --full

# Index specific directory
rtm index --path /path/to/project
```

**What it does:**

1. Reads all markdown files from `.trace/` directories
2. Parses frontmatter and content
3. Updates or creates database records
4. Updates full-text search index
5. Indexes links from `.meta/links.yaml`
6. Updates `.meta/sync.yaml` with timestamp

**Incremental vs Full:**
- **Incremental** (default): Only processes files changed since last index
- **Full** (`--full`): Re-processes all files regardless of timestamps

**Output:**
```
Indexing .trace/ directory (incremental)...

✓ Indexed items:
  • Epics: 5
  • Stories: 23
  • Tests: 12
  • Tasks: 8
  • Links: 45

✓ Index complete for project 'my-project'
```

### `rtm project list`

List all projects with local paths and indexed times (updated).

**Usage:**
```bash
rtm project list [OPTIONS]
```

**Options:**
- `--sync-status` - Show sync status for projects
- `--paths / --no-paths` - Show/hide local .trace/ paths (default: show)

**Examples:**

```bash
# List all projects with local paths
rtm project list

# Hide local paths
rtm project list --no-paths

# Show sync status
rtm project list --sync-status
```

**Output:**
```
                                    Projects
┏━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ ID       ┃ Name       ┃ Description  ┃ Local Path    ┃ Items ┃ Last Indexed  ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━┩
│ 24f2ba95 │ project-1  │ First proj   │ /path/to/p1   │    48 │ 2025-11-30    │
│          │            │              │               │       │ 06:28         │
│ f8724a51 │ project-2  │ Second proj  │ /path/to/p2   │    23 │ 2025-11-30    │
│          │            │              │               │       │ 06:29         │
│ a1b2c3d4 │ global-prj │ Global only  │ Global only   │     5 │ Never         │
└──────────┴────────────┴──────────────┴───────────────┴───────┴───────────────┘

Current project: project-1
Global database: /Users/you/.tracertm/tracertm.db
```

## Workflow Examples

### Starting a New Project

```bash
# 1. Create project directory
mkdir my-awesome-project
cd my-awesome-project

# 2. Initialize git (optional but recommended)
git init

# 3. Initialize TraceRTM
rtm init --name my-awesome-project --description "My awesome project"

# 4. Create first epic
rtm create epic "User Authentication System"

# 5. Create stories
rtm create story "Login Page" --parent EPIC-001
rtm create story "OAuth Integration" --parent EPIC-001

# 6. List items
rtm list

# 7. Commit to git
git add .trace/
git commit -m "Initial TraceRTM structure"
```

### Cloning an Existing Project

```bash
# 1. Clone repository
git clone https://github.com/user/project.git
cd project

# 2. Register .trace/ directory
rtm register

# 3. Verify items were indexed
rtm project list

# 4. Start working
rtm list --type epic
```

### Syncing Changes

```bash
# After editing .trace/ files manually or via LLM agents:

# 1. Re-index changes
rtm index

# 2. Verify updates
rtm project list

# 3. Commit changes
git add .trace/
git commit -m "Updated requirements"
```

## File Formats

### project.yaml

```yaml
name: my-awesome-project
description: A project to build awesome things
version: 1.0.0

# Auto-generated counters for external IDs
counters:
  epic: 2      # Next: EPIC-003
  story: 5     # Next: STORY-006
  test: 3      # Next: TEST-004
  task: 10     # Next: TASK-011

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
external_id: EPIC-001
type: epic
status: in_progress
priority: high
owner: "@alice"
parent: null
version: 3
created: 2024-01-15T10:30:00Z
updated: 2024-01-20T14:22:00Z
tags:
  - authentication
  - security
links:
  - type: implements
    target: STORY-001
---

# User Authentication System

## Description

Implement a complete user authentication system supporting OAuth2, JWT tokens,
and session management.

## Acceptance Criteria

- [ ] Users can sign up with email/password
- [ ] OAuth2 integration with Google, GitHub
- [ ] JWT token refresh mechanism
- [x] Password reset flow
```

### links.yaml

```yaml
# .trace/.meta/links.yaml
links:
  - id: "link-uuid-1"
    source: EPIC-001
    target: STORY-001
    type: implements
    created: 2024-01-15T10:30:00Z

  - id: "link-uuid-2"
    source: STORY-001
    target: TEST-001
    type: tested_by
    created: 2024-01-16T09:00:00Z
```

## Best Practices

### Git Integration

1. **Always commit .trace/ to version control:**
   ```bash
   git add .trace/
   git commit -m "Requirements updates"
   ```

2. **Gitignore sync state only:**
   ```gitignore
   # TraceRTM sync state (local only)
   .trace/.meta/sync.yaml
   ```

3. **Use pre-commit hooks:**
   ```bash
   # .git/hooks/pre-commit
   rtm index
   ```

### Team Collaboration

1. **After pulling changes:**
   ```bash
   git pull
   rtm index  # Re-index to update local database
   ```

2. **Before pushing:**
   ```bash
   rtm index  # Ensure all changes are indexed
   git add .trace/
   git commit -m "Updated requirements"
   git push
   ```

### LLM Agent Integration

Agents can directly read/write `.trace/` files:

```python
# Agent reading requirements
with open(".trace/epics/EPIC-001.md") as f:
    content = f.read()
    # Parse and generate code

# Agent creating a task
task_content = '''---
id: "new-uuid"
type: task
status: todo
---

# Implement login form validation
'''
with open(".trace/tasks/TASK-011.md", "w") as f:
    f.write(task_content)

# TraceRTM file watcher auto-indexes the new task
```

## Troubleshooting

### "No .trace/ directory found"

**Problem:** Running `rtm register` or `rtm index` in wrong directory.

**Solution:**
```bash
# Check if .trace/ exists
ls -la .trace/

# Or specify path explicitly
rtm register --path /path/to/project
```

### ".trace/ already exists"

**Problem:** Running `rtm init` when `.trace/` already exists.

**Solution:**
```bash
# Use rtm register instead
rtm register

# Or remove existing .trace/ first
rm -rf .trace/
rtm init
```

### "Project not found in database"

**Problem:** Running `rtm index` before registering project.

**Solution:**
```bash
rtm register  # Register first
rtm index     # Then index
```

### Items not appearing after index

**Problem:** Markdown files have invalid frontmatter.

**Solution:**
```bash
# Check frontmatter format
cat .trace/epics/EPIC-001.md

# Re-index with full mode
rtm index --full
```

## See Also

- [PROJECT_LOCAL_STORAGE.md](PROJECT_LOCAL_STORAGE.md) - Architecture overview
- [CLI_REFERENCE.md](CLI_REFERENCE.md) - Complete CLI reference
- [AGENT_INTEGRATION.md](AGENT_INTEGRATION.md) - LLM agent integration guide
