# TraceRTM CLI User Guide

**Version**: 1.0  
**Last Updated**: 2025-01-27

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Command Reference](#command-reference)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## 1. Introduction

TraceRTM is an agent-native, multi-view requirements traceability system designed for managing complex software projects. The CLI (Command-Line Interface) is the primary way to interact with TraceRTM, providing powerful commands for managing projects, items, links, and views.

### Key Features

- **Multi-View System**: Switch between Feature, Code, Wireframe, API, Test, Database, and more views
- **Intelligent CRUD**: Create, read, update, and delete items across all views
- **Rich Terminal Output**: Beautiful tables, progress bars, and formatted output using Rich
- **Local-First**: Works offline with SQLite or PostgreSQL
- **Agent-Native**: Designed for AI agents to interact programmatically

---

## 2. Installation

### Prerequisites

- Python 3.12 or higher
- pip or uv package manager

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd trace

# Install in development mode
pip install -e .

# Or using uv
uv pip install -e .
```

### Verify Installation

```bash
# Check if rtm command is available
rtm --version

# Or if using tracertm entry point
tracertm --version
```

### Configuration

Before using TraceRTM, initialize configuration:

```bash
# Initialize with SQLite (default)
rtm config init --database-url sqlite:///tracertm.db

# Or with PostgreSQL
rtm config init --database-url postgresql://user:pass@localhost/tracertm
```

---

## 3. Quick Start

### Step 1: Initialize a Project

```bash
# Create a new project
rtm project init "My Project" --description "My first TraceRTM project"
```

### Step 2: Create Your First Item

```bash
# Create a feature item
rtm item create "User Authentication" \
  --view FEATURE \
  --type feature \
  --description "Implement user login and registration"
```

### Step 3: List Items

```bash
# List all items
rtm item list

# List items in a specific view
rtm item list --view FEATURE

# List items with a specific status
rtm item list --status todo
```

### Step 4: View Item Details

```bash
# Show item details (use partial ID)
rtm item show abc123

# Show with metadata
rtm item show abc123 --metadata
```

### Step 5: Create Links

```bash
# Link two items
rtm link create \
  --source abc123 \
  --target def456 \
  --type implements
```

---

## 4. Command Reference

### Global Options

All commands support these global options:

- `--version, -v`: Show version and exit
- `--debug`: Enable debug mode with full stack traces
- `--help, -h`: Show help message

### Command Groups

#### `rtm config` - Configuration Management

**Commands**:
- `init`: Initialize TraceRTM configuration
- `show`: Show current configuration
- `set`: Set a configuration value

**Examples**:
```bash
# Initialize config
rtm config init --database-url sqlite:///tracertm.db

# Show config
rtm config show

# Set config value
rtm config set current_project_id proj-123
```

#### `rtm project` - Project Management

**Commands**:
- `init`: Initialize a new project
- `list`: List all projects
- `switch`: Switch to a different project

**Examples**:
```bash
# Initialize project
rtm project init "My Project" --description "Project description"

# List projects
rtm project list

# Switch project
rtm project switch "My Project"
```

#### `rtm item` - Item Management

**Commands**:
- `create`: Create a new item
- `list`: List items
- `show`: Show item details
- `update`: Update an item
- `delete`: Delete an item
- `bulk-update`: Bulk update multiple items

**Examples**:
```bash
# Create item
rtm item create "Feature Title" --view FEATURE --type feature

# List items
rtm item list --view CODE --status in_progress

# Show item
rtm item show abc123

# Update item
rtm item update abc123 --status done --description "Updated description"

# Delete item
rtm item delete abc123

# Bulk update
rtm item bulk-update --view FEATURE --status todo --new-status in_progress
```

#### `rtm link` - Link Management

**Commands**:
- `create`: Create a link between items
- `list`: List links

**Examples**:
```bash
# Create link
rtm link create --source abc123 --target def456 --type implements

# List links
rtm link list --source abc123
```

#### `rtm view` - View Management

**Commands**:
- `list`: List all available views
- `switch`: Switch to a different view
- `current`: Show current view
- `stats`: Show view statistics

**Examples**:
```bash
# List views
rtm view list

# Switch view
rtm view switch FEATURE

# Show current view
rtm view current

# Show view statistics
rtm view stats
```

#### `rtm db` - Database Operations

**Commands**:
- `status`: Check database health status
- `migrate`: Run database migrations
- `rollback`: Rollback database (drop all tables)

**Examples**:
```bash
# Check database status
rtm db status

# Run migrations
rtm db migrate

# Rollback (requires --confirm)
rtm db rollback --confirm
```

#### `rtm backup` - Backup and Restore

**Commands**:
- `backup`: Create project backup
- `restore`: Restore from backup

**Examples**:
```bash
# Create backup
rtm backup --output backup.json --compress

# Restore backup
rtm backup restore backup.json --force
```

#### `rtm benchmark` - Performance Benchmarking

**Commands**:
- `views`: Benchmark view performance
- `refresh`: Benchmark refresh operations
- `report`: Generate performance report

**Examples**:
```bash
# Benchmark views
rtm benchmark views

# Generate report
rtm benchmark report
```

#### `rtm droid` - Droid Agent Interactions

**Commands**:
- `check`: Check if droid is installed
- `exec`: Execute droid command

**Examples**:
```bash
# Check installation
rtm droid check

# Execute droid
rtm droid exec --help
```

#### `rtm cursor` - Cursor Agent Interactions

**Commands**:
- `check`: Check if cursor-agent is installed
- `run`: Run cursor-agent

**Examples**:
```bash
# Check installation
rtm cursor check

# Run cursor-agent
rtm cursor run --help
```

#### `rtm query` - Query Items

**Commands**:
- `query`: Query items with structured filters (FR29, FR21, FR49)

**Examples**:
```bash
# Query by status
rtm query --filter status=todo

# Query by multiple criteria
rtm query --filter status=todo,view=FEATURE

# Query with flags
rtm query --status in_progress --view CODE

# Query by relationship (FR21)
rtm query --related-to ITEM-001 --link-type tests

# Cross-project query (FR49)
rtm query --all-projects --status todo

# JSON output
rtm query --filter status=todo --json
```

#### `rtm saved-queries` - Saved Queries

**Commands**:
- `save`: Save a query for reuse (FR65)
- `list`: List all saved queries
- `run`: Run a saved query
- `delete`: Delete a saved query

**Examples**:
```bash
# Save a query
rtm saved-queries save "my-todos" --filter status=todo

# List saved queries
rtm saved-queries list

# Run a saved query
rtm saved-queries run "my-todos"

# Delete a saved query
rtm saved-queries delete "my-todos"
```

#### `rtm link` - Enhanced Link Management

**Additional Commands**:
- `detect-cycles`: Detect cycles in dependency graph (FR22)
- `auto-link`: Automatically create links from commit messages (FR18)

**Examples**:
```bash
# Detect cycles
rtm link detect-cycles

# Auto-link from commit message
rtm link auto-link --commit-message "Implements STORY-123"
```

#### `rtm dashboard` - Multi-Project Dashboard

**Commands**:
- `dashboard`: Show multi-project dashboard (FR50)

**Examples**:
```bash
# Show dashboard
rtm dashboard
```

#### `rtm project` - Enhanced Project Management

**Additional Commands**:
- `export`: Export entire project (FR53)
- `import`: Import entire project (FR53)

**Examples**:
```bash
# Export project
rtm project export --output project-backup.json

# Import project
rtm project import project-backup.json
```

#### `rtm history` - History & Versioning

**Commands**:
- `history`: Show history of changes (FR55)
- `history version`: Show version information
- `history rollback`: Rollback to previous version (FR57)

**Examples**:
```bash
# Show history
rtm history ITEM-001

# Show history with limit
rtm history ITEM-001 --limit 50

# Query state at specific date (FR56, FR59)
rtm history ITEM-001 --at "2025-01-15"

# Show version info
rtm history version ITEM-001 --version 3

# Rollback to previous version
rtm history rollback ITEM-001 --version 3
```

#### `rtm search` - Enhanced Search

**Commands**:
- `search`: Full-text search with filters (FR60-FR67)

**Examples**:
```bash
# Basic search
rtm search "authentication"

# Search with filters
rtm search "login" --view FEATURE --status todo
rtm search "user" --owner alice --type feature
rtm search "test" --created-after "2025-01-01"

# Fuzzy matching
rtm search "auth" --fuzzy

# Combine filters
rtm search "feature" --status blocked --owner agent-12
```

#### `rtm progress` - Progress Tracking

**Commands**:
- `show`: Show progress information (FR68, FR69)
- `blocked`: Show blocked items (FR70)
- `stalled`: Show stalled items (FR71)
- `velocity`: Show velocity metrics (FR73)
- `report`: Generate progress report (FR72)

**Examples**:
```bash
# Show overall progress
rtm progress show

# Show item progress
rtm progress show --item ITEM-001

# Show view progress
rtm progress show --view FEATURE

# Show blocked items
rtm progress blocked

# Show stalled items
rtm progress stalled --days 14

# Show velocity
rtm progress velocity --days 30

# Generate report
rtm progress report --days 30 --json
```

#### `rtm import` - Data Import

**Commands**:
- `json`: Import from JSON (FR78)
- `yaml`: Import from YAML (FR79)
- `jira`: Import from Jira (FR80)
- `github`: Import from GitHub (FR81)

**Examples**:
```bash
# Import JSON
rtm import json backup.json --project my-project

# Import YAML
rtm import yaml backup.yaml --project my-project

# Import Jira
rtm import jira jira-export.json --project imported-project

# Import GitHub
rtm import github github-export.json --project imported-project

# Validate only
rtm import json backup.json --validate-only
```

---

## 5. Examples

### Example 1: Creating a Feature Hierarchy

```bash
# Create epic
rtm item create "User Management" --view FEATURE --type epic

# Create feature (note the ID from previous command)
rtm item create "User Authentication" \
  --view FEATURE \
  --type feature \
  --parent <epic-id>

# Create story
rtm item create "User Login" \
  --view FEATURE \
  --type story \
  --parent <feature-id> \
  --description "As a user, I want to login"
```

### Example 2: Linking Across Views

```bash
# Create feature
FEATURE_ID=$(rtm item create "Login Feature" --view FEATURE --type feature | grep "ID:" | cut -d' ' -f2)

# Create code file
CODE_ID=$(rtm item create "auth/login.py" --view CODE --type file | grep "ID:" | cut -d' ' -f2)

# Link feature to code
rtm link create --source $FEATURE_ID --target $CODE_ID --type implements
```

### Example 3: View Switching Workflow

```bash
# Start in feature view
rtm view switch FEATURE
rtm item list

# Switch to code view
rtm view switch CODE
rtm item list

# Switch to test view
rtm view switch TEST
rtm item list
```

### Example 4: Bulk Operations

```bash
# Update all todo items in FEATURE view to in_progress
rtm item bulk-update \
  --view FEATURE \
  --status todo \
  --new-status in_progress \
  --force
```

### Example 5: Backup and Restore

```bash
# Create backup
rtm backup --output my_backup.json.gz --compress

# Restore backup
rtm backup restore my_backup.json.gz --force
```

### Example 6: Querying Items

```bash
# Query by status
rtm query --filter status=todo

# Query with multiple filters
rtm query --filter status=todo,view=FEATURE

# Query by relationship
rtm query --related-to ITEM-001 --link-type tests

# Cross-project query
rtm query --all-projects --status todo
```

### Example 7: Saved Queries

```bash
# Save a query
rtm saved-queries save "my-todos" --filter status=todo

# Run saved query
rtm saved-queries run "my-todos"

# List all saved queries
rtm saved-queries list
```

### Example 8: Progress Tracking

```bash
# Show overall progress
rtm progress show

# Show blocked items
rtm progress blocked

# Show velocity
rtm progress velocity --days 30

# Generate report
rtm progress report --days 30
```

### Example 9: History & Rollback

```bash
# Show item history
rtm history ITEM-001

# Query state at specific date
rtm history ITEM-001 --at "2025-01-15"

# Rollback to previous version
rtm history rollback ITEM-001 --version 3
```

### Example 10: Importing Data

```bash
# Import from JSON
rtm import json backup.json --project my-project

# Import from Jira
rtm import jira jira-export.json --project imported-project

# Validate before importing
rtm import json backup.json --validate-only
```

### Example 11: Multi-Project Dashboard

```bash
# Show dashboard of all projects
rtm dashboard
```

### Example 12: Enhanced Search

```bash
# Search with filters
rtm search "authentication" --view FEATURE --status todo

# Fuzzy search
rtm search "auth" --fuzzy

# Search with date filters
rtm search "test" --created-after "2025-01-01"
```

---

## 6. Troubleshooting

### Issue: "No database configured"

**Solution**:
```bash
rtm config init --database-url sqlite:///tracertm.db
```

### Issue: "No current project"

**Solution**:
```bash
# List projects
rtm project list

# Switch to a project
rtm project switch "Project Name"
```

### Issue: "Item not found"

**Solution**:
- Use partial IDs (first 8 characters)
- Check item exists: `rtm item list`
- Verify you're in the correct project

### Issue: "Invalid view"

**Solution**:
- Valid views: FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS
- Use uppercase: `--view FEATURE` not `--view feature`

### Issue: Command not found

**Solution**:
- Verify installation: `rtm --version`
- Check PATH includes Python scripts directory
- Reinstall: `pip install -e .`

---

## 7. FAQ

### Q: Can I use both `rtm` and `tracertm` commands?

**A**: Yes, both entry points are available. `rtm` is shorter, `tracertm` matches the package name.

### Q: How do I export data?

**A**: Use the backup command:
```bash
rtm backup --output export.json
```

### Q: Can I use this with multiple projects?

**A**: Yes, create multiple projects and switch between them:
```bash
rtm project init "Project 1"
rtm project init "Project 2"
rtm project switch "Project 1"
```

### Q: How do I delete everything?

**A**: Use database rollback (destructive):
```bash
rtm db rollback --confirm
```

### Q: Can I script these commands?

**A**: Yes, all commands are designed to be scriptable. Use `--force` flags to avoid prompts.

### Q: How do I get help for a specific command?

**A**: Use `--help`:
```bash
rtm item --help
rtm item create --help
```

---

## 📚 Additional Resources

- **CLI API Reference**: See `docs/06-api-reference/CLI_API_REFERENCE.md`
- **CLI Tutorial**: See `docs/01-getting-started/CLI_TUTORIAL.md`
- **CLI Examples**: See `docs/05-research/rtm-deep-dives/RTM_MULTI_VIEW_CLI_EXAMPLES.md`
- **Architecture**: See `docs/05-research/rtm-deep-dives/RTM_FINAL_ARCHITECTURE_SUMMARY.md`

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
