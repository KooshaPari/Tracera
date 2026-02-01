# TraceRTM CLI - Complete Command Reference

**Version**: 0.1.0
**Total Commands**: 100+
**Command Groups**: 20

---

## Command Index

### Core Commands

```bash
rtm --version                    # Show version
rtm --help                       # Show help
rtm --debug <command>            # Enable debug mode
rtm --install-completion         # Install shell completion
rtm --show-completion            # Show completion script
```

### MVP Shortcuts (Top-Level)

```bash
rtm create <type> "<title>"      # Create requirement
rtm list                         # List requirements
rtm show <item-id>               # Show requirement details
rtm state                        # Show project state
rtm search "<query>"             # Full-text search
rtm drill <item-id>              # Drill down hierarchy
rtm query [filters]              # Structured query
rtm export [options]             # Export project data
rtm history <item-id>            # Show item history
rtm init [options]               # Initialize .trace/
rtm register [options]           # Register .trace/
rtm index [options]              # Re-index .trace/
```

### Help System

```bash
rtm help-cmd [topic]             # Show help for topic
rtm list-help-topics             # List all help topics
rtm search-help <query>          # Search help topics
```

---

## Command Groups

### 1. rtm config - Configuration Management

```bash
rtm config init                  # Initialize configuration
rtm config show                  # Show current configuration
rtm config set <key> <value>     # Set configuration value
rtm config get <key>             # Get configuration value
rtm config unset <key>           # Unset configuration value
rtm config list                  # List all configuration values
```

### 2. rtm project - Project Management

```bash
rtm project init [options]       # Initialize new project
rtm project list                 # List all projects
rtm project switch <name>        # Switch to project
rtm project export <name>        # Export entire project
rtm project import <file>        # Import project from backup
rtm project clone <name>         # Clone existing project
rtm project template [cmd]       # Manage project templates
```

### 3. rtm item - Item Management

```bash
rtm item create "<title>"        # Create new item
rtm item list [filters]          # List items
rtm item show <id>               # Show item details
rtm item update <id>             # Update existing item
rtm item delete <id>             # Delete item
rtm item undelete <id>           # Restore deleted item
rtm item bulk-update [filters]   # Bulk update items
rtm item update-status <id>      # Update item status
rtm item get-progress <id>       # Get progress for item
rtm item bulk-update-preview     # Preview bulk update
rtm item bulk-delete [filters]   # Bulk delete items
rtm item bulk-create --csv       # Bulk create from CSV
rtm item install-completion      # Install shell completion
rtm item show-completion         # Show completion script
rtm item list-aliases            # List command aliases
rtm item show-alias <alias>      # Show alias resolution
rtm item add-alias               # Add custom alias
rtm item remove-alias            # Remove custom alias
```

### 4. rtm link - Link Management

```bash
rtm link create <src> <tgt>      # Create link between items
rtm link list                    # List all links
rtm link show <id>               # Show links for item
rtm link detect-cycles           # Detect dependency cycles
rtm link detect-missing          # Detect missing dependencies
rtm link detect-orphans          # Detect orphaned items
rtm link impact <id>             # Analyze change impact
rtm link auto-link               # Auto-link from commits
rtm link delete <link-id>        # Delete traceability link
rtm link graph <id>              # Visualize as ASCII graph
rtm link matrix                  # Show traceability matrix
```

**Valid Link Types**:
- `implements`, `tests`, `designs`, `depends_on`, `blocks`
- `related_to`, `parent_of`, `child_of`, `tested_by`
- `implemented_by`, `decomposes_to`, `decomposed_from`

### 5. rtm view - View Management

```bash
rtm view list                    # List all available views
rtm view switch <view>           # Switch to specific view
rtm view current                 # Show current view
rtm view stats                   # Show statistics for all views
rtm view show <view>             # Show basic information about view
```

**Available Views**:
- `FEATURE` - Features, epics, and user stories
- `CODE` - Code files, classes, and functions
- `WIREFRAME` - UI screens, components, and buttons
- `API` - API endpoints and services
- `TEST` - Test suites and test cases
- `DATABASE` - Database tables, schemas, and queries
- `ROADMAP` - Future plans and milestones
- `PROGRESS` - Progress tracking and metrics

### 6. rtm sync - Sync Management

```bash
rtm sync sync                    # Full bidirectional sync
rtm sync status                  # Show current sync status
rtm sync push                    # Upload local changes only
rtm sync pull                    # Download remote changes only
rtm sync conflicts               # List all unresolved conflicts
rtm sync resolve <id>            # Resolve specific conflict
rtm sync queue                   # Show pending sync queue
rtm sync clear-queue             # Clear all pending changes
```

### 7. rtm dashboard - Multi-Project Dashboard

```bash
rtm dashboard dashboard          # Show multi-project dashboard
```

### 8. rtm db - Database Operations

```bash
rtm db init                      # Initialize database
rtm db status                    # Check database health status
rtm db migrate                   # Run database migrations
rtm db rollback                  # Rollback database (drop all tables)
rtm db reset                     # Reset database (drop and recreate)
```

### 9. rtm backup - Backup and Restore

```bash
rtm backup backup [options]      # Backup project data to file
rtm backup restore <file>        # Restore project data from backup
```

### 10. rtm ingest - File Ingestion

```bash
rtm ingest directory <path>      # Ingest all files in directory
rtm ingest md <file>             # Ingest Markdown (alias)
rtm ingest markdown <file>       # Ingest Markdown file
rtm ingest mdx <file>            # Ingest MDX file
rtm ingest yaml <file>           # Ingest YAML file
rtm ingest file <file>           # Auto-detect and ingest file
```

### 11. rtm progress - Progress Tracking

```bash
rtm progress show <id>           # Show progress information
rtm progress track               # Track progress over time
rtm progress blocked             # Show items blocking others
rtm progress stalled             # Show items with no progress
rtm progress velocity            # Show velocity metrics
rtm progress report [options]    # Generate progress report
```

### 12. rtm saved-queries - Saved Query Management

```bash
rtm saved-queries save           # Save a query
rtm saved-queries list           # List saved queries
rtm saved-queries run            # Run saved query
rtm saved-queries delete         # Delete saved query
```

### 13. rtm import - Import Data

```bash
rtm import json <file>           # Import items from JSON
rtm import yaml <file>           # Import items from YAML
rtm import jira <file>           # Import from Jira export
rtm import github <file>         # Import from GitHub Projects export
```

### 14. rtm agents - Agent Management

```bash
rtm agents list                  # List all registered agents
rtm agents activity              # Show agent activity history
rtm agents metrics               # Show agent performance metrics
rtm agents workload              # Show agent workload
rtm agents health                # Check agent health status
```

### 15. rtm chaos - Chaos Mode Operations

```bash
rtm chaos explode <file>         # Explode file into multiple items
rtm chaos crash                  # Track scope crash
rtm chaos zombies                # Detect and cleanup zombie items
rtm chaos snapshot               # Create temporal snapshot
rtm chaos enable                 # Enable chaos mode
rtm chaos disable                # Disable chaos mode
```

### 16. rtm tui - Terminal UI Applications

```bash
rtm tui dashboard                # Launch main dashboard TUI
rtm tui browser                  # Launch item browser TUI
rtm tui graph                    # Launch graph visualization TUI
rtm tui list                     # List available TUI applications
```

### 17. rtm benchmark - Performance Benchmarking

```bash
rtm benchmark views              # Benchmark all materialized views
rtm benchmark refresh            # Benchmark refresh operations
rtm benchmark report             # Generate comprehensive report
```

### 18. rtm migrate - Migration Tools

```bash
rtm migrate [commands]           # Migration from old storage to .trace/
```

### 19. rtm watch - File Watching

```bash
rtm watch [options]              # Watch .trace/ directory for changes
```

### 20. rtm design - Design Integration

```bash
rtm design [commands]            # Design integration (Storybook + Figma)
```

### 21. rtm test - Unified Test Runner

```bash
rtm test test [options]          # Run tests across all languages
```

---

## Command Options

### Global Options (Available on All Commands)

```bash
--help                           # Show help and exit
--version / -v                   # Show version and exit
--debug                          # Enable debug mode with full stack traces
--install-completion             # Install completion for current shell
--show-completion                # Show completion for current shell
```

### Common Item Options

```bash
--view <view>                    # Specify view (FEATURE, CODE, etc.)
--type <type>                    # Specify item type (epic, story, task, etc.)
--status <status>                # Specify status (todo, in_progress, done, etc.)
--priority <priority>            # Specify priority (low, medium, high, critical)
--owner <owner>                  # Specify owner
--description <text>             # Add description
--metadata <json>                # Add metadata as JSON
```

### Common Query Options

```bash
--type <type>                    # Filter by type
--status <status>                # Filter by status
--priority <priority>            # Filter by priority
--owner <owner>                  # Filter by owner
--view <view>                    # Filter by view
--limit <number>                 # Limit results
--offset <number>                # Offset for pagination
--format <format>                # Output format (json, table)
```

### Common Link Options

```bash
--type <link-type>               # Specify link type (required for create)
--metadata <json>                # Add metadata as JSON
--max-depth <number>             # Maximum depth for graph traversal
```

### Common Export Options

```bash
--format <format>                # Export format (json, yaml, csv, html)
--output <file>                  # Output file path
--pretty                         # Pretty-print output
--include-links                  # Include links in export
--include-metadata               # Include metadata in export
```

---

## Output Formats

Most commands support multiple output formats:

```bash
--format json                    # JSON output (machine-readable)
--format table                   # Table output (human-readable, default)
--format yaml                    # YAML output
--format csv                     # CSV output (for bulk operations)
--format html                    # HTML output (for reports)
```

---

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Usage error (wrong arguments/options)

---

## Environment Variables

```bash
TRACERTM_DB_PATH                 # Override database path
TRACERTM_PROJECT_PATH            # Override project path
TRACERTM_DEBUG                   # Enable debug mode (1 or 0)
TRACERTM_CONFIG_PATH             # Override config file path
```

---

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

sync:
  auto: false
  interval: 300
```

---

## Common Workflows

### 1. Initialize and Create Basic Structure

```bash
# Initialize project
rtm init --name "My Project"

# Create epic
rtm create epic "User Management"

# Create stories
rtm create story "Login Page"
rtm create story "Registration"

# List to get UUIDs
rtm list
```

### 2. Create Links and Visualize

```bash
# Create link (use UUIDs from list)
rtm link create <epic-uuid> <story-uuid> --type parent_of

# Show links
rtm link show <epic-uuid>

# Visualize graph
rtm link graph <epic-uuid>

# Show matrix
rtm link matrix
```

### 3. Search and Query

```bash
# Full-text search
rtm search "authentication"

# Structured query
rtm query --type story --status todo --priority high

# Show project state
rtm state
```

### 4. Export and Backup

```bash
# Export to JSON
rtm export --format json --output backup.json

# Create compressed backup
rtm backup backup --output backup.json.gz

# Export entire project
rtm project export "My Project" --output project-backup.json
```

### 5. Import Data

```bash
# Import from JSON
rtm import json --file data.json

# Import from Jira
rtm import jira --file jira-export.json

# Import from GitHub
rtm import github --file github-export.json
```

### 6. Track Progress

```bash
# Show progress for item
rtm progress show <item-uuid>

# Show blocked items
rtm progress blocked

# Show velocity
rtm progress velocity

# Generate report
rtm progress report --output report.html
```

### 7. Multi-Project Management

```bash
# List all projects
rtm project list

# Show dashboard
rtm dashboard dashboard

# Switch project
rtm project switch "Other Project"
```

### 8. TUI Applications

```bash
# Launch dashboard
rtm tui dashboard

# Launch item browser
rtm tui browser

# Launch graph viewer
rtm tui graph
```

---

## Tips

1. **Use Tab Completion**: Install shell completion for faster command entry
   ```bash
   rtm --install-completion
   ```

2. **Use JSON for Scripting**: Most commands support JSON output
   ```bash
   rtm list --format json | jq '.items[].title'
   ```

3. **Get Help Anytime**: Use `--help` on any command
   ```bash
   rtm link create --help
   ```

4. **Use Debug Mode**: For detailed error information
   ```bash
   rtm --debug create epic "Test"
   ```

5. **Save Complex Queries**: Use saved queries for repeated operations
   ```bash
   rtm saved-queries save "my-todos" --status todo --owner me
   rtm saved-queries run "my-todos"
   ```

---

## Quick Reference Card

### Most Common Commands

```bash
rtm init                         # Start new project
rtm create <type> "<title>"      # Create item
rtm list                         # List items
rtm link create <src> <tgt> -t X # Link items
rtm search "<keyword>"           # Search
rtm state                        # Show state
rtm export --format json         # Export
```

### Get Help

```bash
rtm --help                       # All commands
rtm <cmd> --help                 # Specific command
rtm help-cmd <topic>             # Help topic
```

### Keyboard Shortcuts (TUI)

```
q       - Quit
?       - Help
↑/↓     - Navigate
Enter   - Select
Tab     - Switch panels
/       - Search
```

---

**Total Commands**: 100+
**Last Updated**: 2026-01-22
**Version**: TraceRTM 0.1.0
