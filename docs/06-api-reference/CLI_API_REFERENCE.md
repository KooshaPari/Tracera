# TraceRTM CLI API Reference

**Version**: 1.0  
**Last Updated**: 2025-01-27

---

## 📖 Table of Contents

1. [Command Overview](#command-overview)
2. [Global Options](#global-options)
3. [Command Groups](#command-groups)
4. [Individual Commands](#individual-commands)
5. [Return Codes](#return-codes)
6. [Error Messages](#error-messages)

---

## 1. Command Overview

TraceRTM CLI provides a comprehensive set of commands organized into logical groups:

- **Configuration**: `rtm config`
- **Projects**: `rtm project`
- **Items**: `rtm item`
- **Links**: `rtm link`
- **Views**: `rtm view`
- **Database**: `rtm db`
- **Backup**: `rtm backup`
- **Benchmark**: `rtm benchmark`
- **Agents**: `rtm droid`, `rtm cursor`

---

## 2. Global Options

All commands support these global options:

### `--version, -v`

Show version and exit.

**Usage**:
```bash
rtm --version
```

**Output**:
```
TraceRTM version 0.1.0
```

### `--debug`

Enable debug mode with full stack traces.

**Usage**:
```bash
rtm --debug item list
```

### `--help, -h`

Show help message for command or subcommand.

**Usage**:
```bash
rtm --help
rtm item --help
rtm item create --help
```

---

## 3. Command Groups

### `rtm config`

Configuration management commands.

**Subcommands**:
- `init`: Initialize configuration
- `show`: Show current configuration
- `set`: Set configuration value

### `rtm project`

Project management commands.

**Subcommands**:
- `init`: Initialize new project
- `list`: List all projects
- `switch`: Switch to different project

### `rtm item`

Item management commands.

**Subcommands**:
- `create`: Create new item
- `list`: List items
- `show`: Show item details
- `update`: Update item
- `delete`: Delete item
- `bulk-update`: Bulk update items

### `rtm link`

Link management commands.

**Subcommands**:
- `create`: Create link
- `list`: List links

### `rtm view`

View management commands.

**Subcommands**:
- `list`: List all views
- `switch`: Switch view
- `current`: Show current view
- `stats`: Show view statistics

### `rtm db`

Database operations.

**Subcommands**:
- `status`: Check database status
- `migrate`: Run migrations
- `rollback`: Rollback database

### `rtm backup`

Backup and restore.

**Subcommands**:
- `backup`: Create backup
- `restore`: Restore from backup

### `rtm benchmark`

Performance benchmarking.

**Subcommands**:
- `views`: Benchmark views
- `refresh`: Benchmark refresh
- `report`: Generate report

### `rtm droid`

Droid agent interactions.

**Subcommands**:
- `check`: Check installation
- `exec`: Execute droid

### `rtm cursor`

Cursor agent interactions.

**Subcommands**:
- `check`: Check installation
- `run`: Run cursor-agent

---

## 4. Individual Commands

### `rtm config init`

Initialize TraceRTM configuration.

**Syntax**:
```bash
rtm config init --database-url <url>
```

**Options**:
- `--database-url, -d` (required): Database URL (PostgreSQL or SQLite)

**Examples**:
```bash
rtm config init --database-url sqlite:///tracertm.db
rtm config init -d postgresql://user:pass@localhost/tracertm
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm config show`

Show current configuration.

**Syntax**:
```bash
rtm config show
```

**Options**: None

**Output**: Table showing all configuration values

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm config set`

Set a configuration value.

**Syntax**:
```bash
rtm config set <key> <value>
```

**Arguments**:
- `key` (required): Configuration key
- `value` (required): Configuration value

**Examples**:
```bash
rtm config set current_project_id proj-123
rtm config set database_url sqlite:///new.db
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm project init`

Initialize a new project.

**Syntax**:
```bash
rtm project init <name> [OPTIONS]
```

**Arguments**:
- `name` (required): Project name

**Options**:
- `--description, -d`: Project description
- `--database-url`: Database URL (default: SQLite in project directory)

**Examples**:
```bash
rtm project init "My Project"
rtm project init "My Project" --description "Project description"
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm project list`

List all projects.

**Syntax**:
```bash
rtm project list
```

**Options**: None

**Output**: Table of all projects

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm project switch`

Switch to a different project.

**Syntax**:
```bash
rtm project switch <name>
```

**Arguments**:
- `name` (required): Project name

**Examples**:
```bash
rtm project switch "My Project"
```

**Return Codes**:
- `0`: Success
- `1`: Error (project not found)

---

### `rtm item create`

Create a new item.

**Syntax**:
```bash
rtm item create <title> [OPTIONS]
```

**Arguments**:
- `title` (required): Item title

**Options**:
- `--view, -v` (required): View (FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS)
- `--type, -t` (required): Item type (view-specific)
- `--description, -d`: Item description
- `--status, -s`: Item status (default: "todo")
- `--parent, -p`: Parent item ID
- `--metadata, -m`: Metadata as JSON

**Examples**:
```bash
rtm item create "User Login" --view FEATURE --type feature
rtm item create "auth.py" --view CODE --type file --description "Authentication module"
```

**Return Codes**:
- `0`: Success
- `1`: Error (validation, missing config, etc.)

---

### `rtm item list`

List items in current project.

**Syntax**:
```bash
rtm item list [OPTIONS]
```

**Options**:
- `--view, -v`: Filter by view
- `--type, -t`: Filter by type
- `--status, -s`: Filter by status
- `--limit, -l`: Maximum items to show (default: 50)

**Examples**:
```bash
rtm item list
rtm item list --view FEATURE --status todo
rtm item list --limit 100
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm item show`

Show detailed information about an item.

**Syntax**:
```bash
rtm item show <item_id>
```

**Arguments**:
- `item_id` (required): Item ID (partial ID accepted)

**Options**:
- `--metadata, -m`: Show metadata

**Examples**:
```bash
rtm item show abc123
rtm item show abc123 --metadata
```

**Return Codes**:
- `0`: Success
- `1`: Error (item not found)

---

### `rtm item update`

Update an existing item.

**Syntax**:
```bash
rtm item update <item_id> [OPTIONS]
```

**Arguments**:
- `item_id` (required): Item ID

**Options**:
- `--title`: New title
- `--description, -d`: New description
- `--status, -s`: New status
- `--metadata, -m`: Metadata as JSON

**Examples**:
```bash
rtm item update abc123 --status in_progress
rtm item update abc123 --title "New Title" --description "New description"
```

**Return Codes**:
- `0`: Success
- `1`: Error (item not found, conflict, etc.)

---

### `rtm item delete`

Delete an item (soft delete).

**Syntax**:
```bash
rtm item delete <item_id> [OPTIONS]
```

**Arguments**:
- `item_id` (required): Item ID

**Options**:
- `--force, -f`: Force delete without confirmation

**Examples**:
```bash
rtm item delete abc123
rtm item delete abc123 --force
```

**Return Codes**:
- `0`: Success
- `1`: Error (item not found)

---

### `rtm item bulk-update`

Bulk update multiple items.

**Syntax**:
```bash
rtm item bulk-update [OPTIONS]
```

**Options**:
- `--view, -v`: Filter by view
- `--status, -s`: Filter by current status
- `--new-status` (required): New status to set
- `--force, -f`: Force update without confirmation

**Examples**:
```bash
rtm item bulk-update --view FEATURE --status todo --new-status in_progress
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm link create`

Create a link between items.

**Syntax**:
```bash
rtm link create [OPTIONS]
```

**Options**:
- `--source` (required): Source item ID
- `--target` (required): Target item ID
- `--type` (required): Link type
- `--metadata, -m`: Metadata as JSON

**Examples**:
```bash
rtm link create --source abc123 --target def456 --type implements
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm link list`

List links in current project.

**Syntax**:
```bash
rtm link list [OPTIONS]
```

**Options**:
- `--source`: Filter by source item ID
- `--target`: Filter by target item ID
- `--type`: Filter by link type

**Examples**:
```bash
rtm link list
rtm link list --source abc123
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm view list`

List all available views.

**Syntax**:
```bash
rtm view list
```

**Options**: None

**Output**: Table of all views with descriptions

**Return Codes**:
- `0`: Success

---

### `rtm view switch`

Switch to a different view.

**Syntax**:
```bash
rtm view switch <view_name>
```

**Arguments**:
- `view_name` (required): View name (FEATURE, CODE, etc.)

**Examples**:
```bash
rtm view switch FEATURE
rtm view switch CODE
```

**Return Codes**:
- `0`: Success
- `1`: Error (invalid view)

---

### `rtm view current`

Show current view.

**Syntax**:
```bash
rtm view current
```

**Options**: None

**Return Codes**:
- `0`: Success

---

### `rtm view stats`

Show view statistics.

**Syntax**:
```bash
rtm view stats [OPTIONS]
```

**Options**:
- `--view, -v`: Show stats for specific view

**Examples**:
```bash
rtm view stats
rtm view stats --view FEATURE
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm db status`

Check database health status.

**Syntax**:
```bash
rtm db status
```

**Options**: None

**Output**: Table showing database status

**Return Codes**:
- `0`: Success (connected)
- `1`: Error (not configured, connection failed)

---

### `rtm db migrate`

Run database migrations (create tables).

**Syntax**:
```bash
rtm db migrate
```

**Options**: None

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm db rollback`

Rollback database (drop all tables).

**Syntax**:
```bash
rtm db rollback [OPTIONS]
```

**Options**:
- `--confirm`: Confirm rollback (required)

**Examples**:
```bash
rtm db rollback --confirm
```

**Return Codes**:
- `0`: Success
- `1`: Error (not confirmed, not configured)

---

### `rtm backup backup`

Create project backup.

**Syntax**:
```bash
rtm backup backup [OPTIONS]
```

**Options**:
- `--output, -o`: Output file path
- `--compress/--no-compress`: Compress backup (default: compress)
- `--project-id`: Project ID to backup

**Examples**:
```bash
rtm backup backup
rtm backup backup --output my_backup.json --no-compress
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm backup restore`

Restore from backup.

**Syntax**:
```bash
rtm backup restore <backup_file> [OPTIONS]
```

**Arguments**:
- `backup_file` (required): Backup file path

**Options**:
- `--force, -f`: Force restore without confirmation

**Examples**:
```bash
rtm backup restore backup.json --force
```

**Return Codes**:
- `0`: Success
- `1`: Error (file not found, invalid format, etc.)

---

### `rtm benchmark views`

Benchmark view performance.

**Syntax**:
```bash
rtm benchmark views
```

**Options**: None

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm benchmark refresh`

Benchmark refresh operations.

**Syntax**:
```bash
rtm benchmark refresh
```

**Options**: None

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm benchmark report`

Generate performance report.

**Syntax**:
```bash
rtm benchmark report
```

**Options**: None

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm droid check`

Check if droid is installed.

**Syntax**:
```bash
rtm droid check
```

**Options**: None

**Return Codes**:
- `0`: Success (installed)
- `1`: Error (not installed)

---

### `rtm droid exec`

Execute droid command.

**Syntax**:
```bash
rtm droid exec [ARGS...]
```

**Arguments**: Passed directly to droid

**Return Codes**: Same as droid command

---

### `rtm cursor check`

Check if cursor-agent is installed.

**Syntax**:
```bash
rtm cursor check
```

**Options**: None

**Return Codes**:
- `0`: Success (installed)
- `1`: Error (not installed)

---

### `rtm cursor run`

Run cursor-agent.

**Syntax**:
```bash
rtm cursor run [ARGS...]
```

**Arguments**: Passed directly to cursor-agent

**Return Codes**: Same as cursor-agent command

---

### `rtm query`

Query items with structured filter criteria (FR29, FR21, FR49).

**Syntax**:
```bash
rtm query [OPTIONS]
```

**Options**:
- `--filter, -f`: Filter criteria (e.g., `status=todo,view=FEATURE`)
- `--view, -v`: Filter by view
- `--status, -s`: Filter by status
- `--priority`: Filter by priority
- `--owner, -o`: Filter by owner
- `--type, -t`: Filter by item type
- `--related-to`: Query items related to item ID (FR21)
- `--link-type`: Filter by link type when using `--related-to`
- `--all-projects`: Query across all projects (FR49)
- `--limit, -l`: Maximum results to show (default: 50)
- `--json`: Output as JSON (FR32)

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

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm saved-queries`

Manage saved queries for reuse (FR65).

**Subcommands**:
- `save`: Save a query
- `list`: List all saved queries
- `run`: Run a saved query
- `delete`: Delete a saved query

#### `rtm saved-queries save`

Save a query for reuse.

**Syntax**:
```bash
rtm saved-queries save <name> [OPTIONS]
```

**Arguments**:
- `name` (required): Query name

**Options**:
- `--query, -q`: Query string
- `--filter, -f`: Filter criteria
- `--view, -v`: View filter
- `--status, -s`: Status filter

**Examples**:
```bash
rtm saved-queries save "my-todos" --filter status=todo
rtm saved-queries save "high-priority" --priority high --view FEATURE
```

**Return Codes**:
- `0`: Success
- `1`: Error

#### `rtm saved-queries list`

List all saved queries.

**Syntax**:
```bash
rtm saved-queries list
```

**Return Codes**:
- `0`: Success

#### `rtm saved-queries run`

Run a saved query.

**Syntax**:
```bash
rtm saved-queries run <name>
```

**Arguments**:
- `name` (required): Query name to run

**Examples**:
```bash
rtm saved-queries run "my-todos"
```

**Return Codes**:
- `0`: Success
- `1`: Error (query not found)

#### `rtm saved-queries delete`

Delete a saved query.

**Syntax**:
```bash
rtm saved-queries delete <name>
```

**Arguments**:
- `name` (required): Query name to delete

**Examples**:
```bash
rtm saved-queries delete "my-todos"
```

**Return Codes**:
- `0`: Success
- `1`: Error (query not found)

---

### `rtm link detect-cycles`

Detect cycles in dependency graph (FR22).

**Syntax**:
```bash
rtm link detect-cycles
```

**Options**: None

**Output**: Lists all cycles found in `depends_on` relationships

**Examples**:
```bash
rtm link detect-cycles
```

**Return Codes**:
- `0`: Success (cycles found or none found)
- `1`: Error

---

### `rtm link auto-link`

Automatically create links from commit messages (FR18).

**Syntax**:
```bash
rtm link auto-link [OPTIONS]
```

**Options**:
- `--commit-message, -m`: Commit message to parse
- `--file, -f`: File containing commit messages (one per line)

**Examples**:
```bash
rtm link auto-link --commit-message "Implements STORY-123"
rtm link auto-link --file commits.txt
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm dashboard`

Show multi-project dashboard with status of all projects (FR50).

**Syntax**:
```bash
rtm dashboard
```

**Options**: None

**Output**: Table showing all projects with item counts, agent counts, status breakdowns, and current project marker

**Examples**:
```bash
rtm dashboard
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm project export`

Export entire project for backup/sharing (FR53).

**Syntax**:
```bash
rtm project export [OPTIONS]
```

**Options**:
- `--output, -o`: Output file path
- `--format`: Export format (json, yaml, markdown, csv)
- `--compress`: Compress output

**Examples**:
```bash
rtm project export --output project-backup.json
rtm project export --format yaml --output project.yaml
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm project import`

Import entire project from backup (FR53).

**Syntax**:
```bash
rtm project import <file> [OPTIONS]
```

**Arguments**:
- `file` (required): Project file to import

**Options**:
- `--force, -f`: Force import without confirmation

**Examples**:
```bash
rtm project import project-backup.json
rtm project import project.yaml --force
```

**Return Codes**:
- `0`: Success
- `1`: Error (file not found, invalid format, etc.)

---

### `rtm history`

Show history of changes for an item (FR55).

**Syntax**:
```bash
rtm history <item_id> [OPTIONS]
```

**Arguments**:
- `item_id` (required): Item ID to show history for

**Options**:
- `--limit, -l`: Maximum history entries (default: 20)
- `--at`: Query item state at specific date (FR56, FR59)

**Examples**:
```bash
rtm history ITEM-001
rtm history ITEM-001 --limit 50
rtm history ITEM-001 --at "2025-01-15"
rtm history ITEM-001 --at "2025-01-15T10:30:00"
```

**Return Codes**:
- `0`: Success
- `1`: Error (item not found)

---

### `rtm history version`

Show version information for an item.

**Syntax**:
```bash
rtm history version <item_id> [OPTIONS]
```

**Arguments**:
- `item_id` (required): Item ID

**Options**:
- `--version, -v`: Specific version to show

**Examples**:
```bash
rtm history version ITEM-001
rtm history version ITEM-001 --version 3
```

**Return Codes**:
- `0`: Success
- `1`: Error (item not found)

---

### `rtm history rollback`

Rollback an item to a previous version (FR57).

**Syntax**:
```bash
rtm history rollback <item_id> [OPTIONS]
```

**Arguments**:
- `item_id` (required): Item ID to rollback

**Options**:
- `--version, -v` (required): Version to rollback to
- `--confirm`: Skip confirmation prompt

**Examples**:
```bash
rtm history rollback ITEM-001 --version 3
rtm history rollback ITEM-001 --version 2 --confirm
```

**Return Codes**:
- `0`: Success
- `1`: Error (item not found, no history, etc.)

---

### `rtm search`

Full-text search across all items (FR60-FR67).

**Syntax**:
```bash
rtm search <query> [OPTIONS]
```

**Arguments**:
- `query` (required): Search query (searches title and description)

**Options**:
- `--view, -v`: Filter by view
- `--status, -s`: Filter by status (FR61)
- `--type, -t`: Filter by type (FR62)
- `--owner, -o`: Filter by owner (FR63)
- `--created-after`: Filter by creation date (FR64)
- `--created-before`: Filter by creation date (FR64)
- `--updated-after`: Filter by update date (FR64)
- `--updated-before`: Filter by update date (FR64)
- `--fuzzy`: Enable fuzzy matching (FR66)
- `--limit, -l`: Maximum results (default: 50)

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

# Combine filters (FR67)
rtm search "feature" --status blocked --owner agent-12
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm progress show`

Show progress information (FR68, FR69).

**Syntax**:
```bash
rtm progress show [OPTIONS]
```

**Options**:
- `--item, -i`: Show progress for specific item
- `--view, -v`: Show progress for view (FR69)

**Examples**:
```bash
rtm progress show
rtm progress show --item ITEM-001
rtm progress show --view FEATURE
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm progress blocked`

Show items that are blocking others (FR70).

**Syntax**:
```bash
rtm progress blocked [OPTIONS]
```

**Options**:
- `--limit, -l`: Maximum items to show (default: 50)

**Examples**:
```bash
rtm progress blocked
rtm progress blocked --limit 100
```

**Return Codes**:
- `0`: Success

---

### `rtm progress stalled`

Show items with no progress (stalled items) (FR71).

**Syntax**:
```bash
rtm progress stalled [OPTIONS]
```

**Options**:
- `--days, -d`: Days without update to consider stalled (default: 7)
- `--limit, -l`: Maximum items to show (default: 50)

**Examples**:
```bash
rtm progress stalled
rtm progress stalled --days 14
```

**Return Codes**:
- `0`: Success

---

### `rtm progress velocity`

Show velocity metrics (items completed per time period) (FR73).

**Syntax**:
```bash
rtm progress velocity [OPTIONS]
```

**Options**:
- `--days, -d`: Time period in days (default: 7)

**Examples**:
```bash
rtm progress velocity
rtm progress velocity --days 30
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm progress report`

Generate progress report for time period (FR72).

**Syntax**:
```bash
rtm progress report [OPTIONS]
```

**Options**:
- `--days, -d`: Report period in days (default: 30)
- `--json`: Output as JSON

**Examples**:
```bash
rtm progress report
rtm progress report --days 7
rtm progress report --days 30 --json
```

**Return Codes**:
- `0`: Success
- `1`: Error

---

### `rtm import json`

Import items from JSON file (FR78).

**Syntax**:
```bash
rtm import json <file> [OPTIONS]
```

**Arguments**:
- `file` (required): JSON file to import

**Options**:
- `--project, -p`: Target project name
- `--validate-only`: Only validate, don't import (FR82)

**Examples**:
```bash
rtm import json backup.json
rtm import json backup.json --project my-project
rtm import json backup.json --validate-only
```

**Return Codes**:
- `0`: Success
- `1`: Error (file not found, invalid format, validation failed)

---

### `rtm import yaml`

Import items from YAML file (FR79).

**Syntax**:
```bash
rtm import yaml <file> [OPTIONS]
```

**Arguments**:
- `file` (required): YAML file to import

**Options**:
- `--project, -p`: Target project name
- `--validate-only`: Only validate, don't import (FR82)

**Examples**:
```bash
rtm import yaml backup.yaml
rtm import yaml backup.yaml --project my-project
rtm import yaml backup.yaml --validate-only
```

**Return Codes**:
- `0`: Success
- `1`: Error (file not found, invalid format, validation failed)

---

### `rtm import jira`

Import from Jira export format (FR80).

**Syntax**:
```bash
rtm import jira <file> [OPTIONS]
```

**Arguments**:
- `file` (required): Jira export JSON file

**Options**:
- `--project, -p`: Target project name
- `--validate-only`: Only validate, don't import (FR82)

**Examples**:
```bash
rtm import jira jira-export.json
rtm import jira jira-export.json --project imported-project
rtm import jira jira-export.json --validate-only
```

**Return Codes**:
- `0`: Success
- `1`: Error (file not found, invalid format, validation failed)

---

### `rtm import github`

Import from GitHub Projects export format (FR81).

**Syntax**:
```bash
rtm import github <file> [OPTIONS]
```

**Arguments**:
- `file` (required): GitHub export JSON file

**Options**:
- `--project, -p`: Target project name
- `--validate-only`: Only validate, don't import (FR82)

**Examples**:
```bash
rtm import github github-export.json
rtm import github github-export.json --project imported-project
rtm import github github-export.json --validate-only
```

**Return Codes**:
- `0`: Success
- `1`: Error (file not found, invalid format, validation failed)

---

## 5. Return Codes

### Success Codes

- `0`: Command executed successfully

### Error Codes

- `1`: General error (validation, configuration, database, etc.)
- `2`: Invalid arguments or options

### Common Error Scenarios

| Error | Code | Description |
|-------|------|-------------|
| No database configured | 1 | Run `rtm config init` first |
| No current project | 1 | Run `rtm project init` or `rtm project switch` |
| Item not found | 1 | Item ID doesn't exist |
| Invalid view | 1 | View name not recognized |
| Invalid type | 1 | Item type not valid for view |
| Invalid JSON | 1 | Metadata JSON is malformed |
| File not found | 1 | Backup file doesn't exist |
| Database error | 1 | Connection or query failed |

---

## 6. Error Messages

### Configuration Errors

**"No database configured"**
- **Cause**: Database URL not set
- **Solution**: Run `rtm config init --database-url <url>`

**"No current project"**
- **Cause**: No project selected
- **Solution**: Run `rtm project init` or `rtm project switch`

### Validation Errors

**"Invalid view: {view}"**
- **Cause**: View name not recognized
- **Solution**: Use valid view: FEATURE, CODE, WIREFRAME, API, TEST, DATABASE, ROADMAP, PROGRESS

**"Invalid type '{type}' for view {view}"**
- **Cause**: Item type not valid for specified view
- **Solution**: Use valid type for view (see command help)

**"Invalid JSON metadata: {error}"**
- **Cause**: Metadata JSON is malformed
- **Solution**: Provide valid JSON: `--metadata '{"key": "value"}'`

### Not Found Errors

**"Item not found: {id}"**
- **Cause**: Item ID doesn't exist
- **Solution**: Check item exists with `rtm item list`

**"Project '{name}' not found"**
- **Cause**: Project name doesn't exist
- **Solution**: List projects with `rtm project list`

**"Backup file not found: {path}"**
- **Cause**: Backup file path doesn't exist
- **Solution**: Check file path and permissions

### Database Errors

**"Database check failed: {error}"**
- **Cause**: Database connection or query failed
- **Solution**: Check database URL and connectivity

**"Migration failed: {error}"**
- **Cause**: Database migration error
- **Solution**: Check database permissions and schema

---

## 📚 Related Documentation

- **CLI User Guide**: `docs/04-guides/CLI_USER_GUIDE.md`
- **CLI Tutorial**: `docs/01-getting-started/CLI_TUTORIAL.md`
- **CLI Examples**: `docs/05-research/rtm-deep-dives/RTM_MULTI_VIEW_CLI_EXAMPLES.md`

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
