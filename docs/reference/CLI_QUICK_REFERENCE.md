# TraceRTM CLI Quick Reference

## Getting Started

```bash
# Check version
rtm --version

# Get help
rtm --help
rtm <command> --help

# Enable debug mode
rtm --debug <command>
```

## Project Management

```bash
# Initialize new project
rtm init --name "My Project" --description "Project description"

# List all projects
rtm project list

# Switch project
rtm project switch <project-name>

# Show project state
rtm state

# Multi-project dashboard
rtm dashboard dashboard
```

## Creating Items

```bash
# Quick create (MVP shortcuts)
rtm create epic "Epic Title" --description "Details" --status todo --priority high
rtm create story "Story Title" --description "Details" --status in_progress
rtm create task "Task Title" --status todo

# Full create with view
rtm item create "Title" --view FEATURE --type epic --description "Details" --status todo --priority high

# Valid item types per view:
# FEATURE: epic, feature, story, task, bug
# CODE: class, function, module, package
# TEST: test_suite, test_case, test_step
# API: endpoint, service, schema
# DATABASE: table, column, query, migration
```

## Listing and Viewing Items

```bash
# List all items
rtm list

# List with filters
rtm list --type epic --status todo --priority high --limit 20

# Show item details (use UUID from list output)
rtm show <item-uuid>

# Query with structured filters
rtm query --type story --status in_progress
rtm query --priority high --view FEATURE
```

## Creating Links

```bash
# Create link between items
rtm link create <source-uuid> <target-uuid> --type <link-type>

# Example
rtm link create 47108a77-199e-40f6-a5ba-a22f7e33d919 97440b2a-035f-48c2-901f-47c879f48b53 --type parent_of

# Valid link types:
# implements, tests, designs, depends_on, blocks
# related_to, parent_of, child_of, tested_by
# implemented_by, decomposes_to, decomposed_from

# Show links for an item
rtm link show <item-uuid>

# List all links
rtm link list
```

## Visualizing Relationships

```bash
# Show ASCII graph
rtm link graph <item-uuid>

# Show traceability matrix
rtm link matrix

# Detect issues
rtm link detect-cycles
rtm link detect-orphans
rtm link detect-missing
```

## Searching

```bash
# Full-text search
rtm search "keyword"

# Examples
rtm search "login"
rtm search "authentication"

# Drill down hierarchy
rtm drill <item-uuid>
```

## Updating Items

```bash
# Update item status
rtm item update-status <item-uuid> --status done

# Update item (full)
rtm item update <item-uuid> --title "New Title" --description "New description"

# Bulk update
rtm item bulk-update --status in_progress --new-status done
rtm item bulk-update-preview  # Preview before applying
```

## Progress Tracking

```bash
# Show progress
rtm progress show <item-uuid>

# Show blocked items
rtm progress blocked

# Show stalled items
rtm progress stalled

# Show velocity
rtm progress velocity

# Generate report
rtm progress report --start-date 2026-01-01 --end-date 2026-01-31
```

## Views

```bash
# List available views
rtm view list

# Switch view
rtm view switch FEATURE

# Show current view
rtm view current

# View statistics
rtm view stats
```

**Available Views**:
- `FEATURE` - Features, epics, stories
- `CODE` - Source code files
- `WIREFRAME` - UI/UX designs
- `API` - API endpoints
- `TEST` - Test cases
- `DATABASE` - Database schemas
- `ROADMAP` - Milestones
- `PROGRESS` - Progress tracking

## Exporting and Importing

```bash
# Export project
rtm export --format json --output backup.json

# Export entire project
rtm project export <project-name> --output project-backup.json

# Import from various formats
rtm import json --file data.json
rtm import yaml --file data.yaml
rtm import jira --file jira-export.json
rtm import github --file github-export.json
```

## Backup and Restore

```bash
# Create backup
rtm backup backup --output backup.json.gz

# Restore backup
rtm backup restore --file backup.json.gz
```

## Sync Operations

```bash
# Full sync
rtm sync sync

# Push local changes
rtm sync push

# Pull remote changes
rtm sync pull

# Check sync status
rtm sync status

# List conflicts
rtm sync conflicts

# Resolve conflict
rtm sync resolve <conflict-id> --strategy local|remote|manual
```

## File Ingestion

```bash
# Ingest directory
rtm ingest directory ./docs

# Ingest specific files
rtm ingest markdown file.md
rtm ingest mdx component.mdx
rtm ingest yaml config.yaml

# Auto-detect format
rtm ingest file document.md
```

## Agent Management

```bash
# List agents
rtm agents list

# Show agent activity
rtm agents activity

# Show metrics
rtm agents metrics

# Show workload
rtm agents workload

# Check health
rtm agents health
```

## Database Operations

```bash
# Initialize database
rtm db init

# Check status
rtm db status

# Run migrations
rtm db migrate

# Reset database
rtm db reset
```

## Configuration

```bash
# Show config
rtm config show

# Set value
rtm config set key value

# Get value
rtm config get key

# List all
rtm config list
```

## TUI Applications

```bash
# Launch dashboard
rtm tui dashboard

# Launch item browser
rtm tui browser

# Launch graph viewer
rtm tui graph

# List available TUIs
rtm tui list
```

## Advanced Features

### Saved Queries

```bash
# Save a query
rtm saved-queries save "my-query" --type story --status todo

# List saved queries
rtm saved-queries list

# Run saved query
rtm saved-queries run "my-query"
```

### Bulk Operations

```bash
# Bulk create from CSV
rtm item bulk-create --csv items.csv

# Bulk update with preview
rtm item bulk-update-preview --status todo --new-status in_progress

# Bulk delete
rtm item bulk-delete --status cancelled
```

### Impact Analysis

```bash
# Analyze impact of changing an item
rtm link impact <item-uuid>
```

### Auto-linking

```bash
# Auto-link from commit messages
rtm link auto-link --commit-sha abc123
```

## Common Workflows

### Create Complete Feature

```bash
# 1. Initialize project
rtm init --name "Feature Project"

# 2. Create epic
rtm create epic "User Management" --priority high

# 3. Create stories (get epic UUID from list)
rtm list --type epic
rtm create story "Login Form" --priority high
rtm create story "Registration" --priority medium

# 4. Link stories to epic (get UUIDs from list)
rtm list
rtm link create <epic-uuid> <story1-uuid> --type parent_of
rtm link create <epic-uuid> <story2-uuid> --type parent_of

# 5. Visualize
rtm link graph <epic-uuid>

# 6. Track progress
rtm progress show <epic-uuid>
```

### Import and Analyze

```bash
# 1. Import data
rtm import jira --file jira-export.json

# 2. Search for items
rtm search "important keyword"

# 3. Query specific types
rtm query --type bug --priority critical

# 4. Detect issues
rtm link detect-orphans
rtm link detect-cycles

# 5. Generate report
rtm progress report --output report.html
```

### Multi-Project Management

```bash
# 1. View all projects
rtm project list

# 2. Show dashboard
rtm dashboard dashboard

# 3. Switch project
rtm project switch "Project A"

# 4. Work on items
rtm list --status in_progress

# 5. Switch back
rtm project switch "Project B"
```

## Tips and Tricks

### Output Formats

```bash
# Most commands support JSON output
rtm list --format json
rtm query --type story --format json | jq '.items[].title'

# Table output (default)
rtm list
rtm link list
```

### Filtering

```bash
# Combine multiple filters
rtm query --type story --status todo --priority high --owner "alice"

# Use limit for large result sets
rtm list --limit 100
```

### Using UUIDs vs External IDs

```bash
# ⚠️ Currently, most commands require full UUIDs
# Get UUIDs from rtm list output

# This works:
rtm show 47108a77-199e-40f6-a5ba-a22f7e33d919

# This doesn't work yet:
# rtm show EPIC-001  (coming soon)
```

### Shell Completion

```bash
# Install completion
rtm --install-completion

# Show completion script
rtm --show-completion
```

### Getting Help

```bash
# General help
rtm --help

# Command-specific help
rtm item --help
rtm link create --help

# Search help topics
rtm search-help "query"

# List all help topics
rtm list-help-topics
```

## Keyboard Shortcuts (TUI)

When in TUI mode:
- `q` - Quit
- `?` - Help
- `↑/↓` - Navigate
- `Enter` - Select
- `Tab` - Switch panels
- `/` - Search

## Common Errors and Solutions

### FTS5 Database Error

```
sqlite3.OperationalError: invalid fts5 file format
```

**Solution**: Operations complete successfully, ignore the warning.

### Item Not Found with External ID

```
✗ Item not found: EPIC-001
```

**Solution**: Use full UUID from `rtm list` output instead.

### No Current Project

```
✗ Error: No current project set
```

**Solution**: Run `rtm init` or `rtm project switch <name>`

### Invalid Link Type

```
✗ Error: Invalid link type: parent_child
```

**Solution**: Use `parent_of` instead. See valid types above.

## Environment Variables

```bash
# Set database path
export TRACERTM_DB_PATH=~/.tracertm/custom.db

# Set project path
export TRACERTM_PROJECT_PATH=/path/to/project

# Enable debug mode
export TRACERTM_DEBUG=1
```

## Configuration File

Location: `~/.tracertm/config.yaml`

```yaml
database:
  path: ~/.tracertm/tracertm.db

project:
  default: "my-project"

output:
  format: json
  color: true
```

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Usage error (wrong arguments)

## Support

- Documentation: `rtm help-cmd <topic>`
- Search help: `rtm search-help <query>`
- Debug mode: `rtm --debug <command>`
- Issue tracker: Check project repository

---

**Version**: TraceRTM 0.1.0
**Last Updated**: 2026-01-22
