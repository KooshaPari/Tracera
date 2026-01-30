# Phase 3 MCP Tools - Quick Reference

## New Tools Added: 55

### Priority 1: Critical Infrastructure (18 tools)

**Authentication (3)**
- `auth_login(authkit_domain, client_id, scopes, connect_endpoint)` - Device flow auth
- `auth_status()` - Check token status
- `auth_logout()` - Clear token

**Configuration (6)**
- `config_init(database_url)` - Init config with DB URL
- `config_show()` - Display all config (masked)
- `config_set(key, value)` - Set value
- `config_get(key)` - Get value
- `config_unset(key)` - Clear value
- `config_list()` - List all

**Database (6)**
- `db_init(database_url?)` - Init database
- `db_status()` - Check health
- `db_migrate()` - Create tables
- `db_rollback(confirm=True)` - Drop tables (DESTRUCTIVE)
- `db_reset(confirm=True)` - Drop & recreate (DESTRUCTIVE)

### Priority 2: Core Features (18 tools)

**Design Integration (6)**
- `design_init(figma_token, figma_file_id)` - Init Figma
- `design_link(component_name, figma_url)` - Link component
- `design_sync()` - Sync from Figma
- `design_generate(component_pattern?)` - Generate stories
- `design_status()` - Show status
- `design_list()` - List components

**Data Ingestion (4)**
- `ingest_directory(directory_path, project_name?, recursive=True)` - Dir ingestion
- `ingest_markdown(file_path, project_name?)` - MD ingestion
- `ingest_yaml(file_path, project_name?)` - YAML ingestion
- `ingest_file(file_path, file_type, project_name?)` - Generic ingestion

**Migration (1)**
- `migrate_project(source_path, project_name?, backup_existing=True)` - Project migration

**Link Analysis (3)**
- `link_detect_missing(project_id?)` - Find missing links
- `link_detect_orphans(project_id?)` - Find orphaned items
- `link_auto_link(project_id?, threshold=0.8)` - Auto-link via similarity

### Priority 3: Optional Features (19 tools)

**View Management (5)**
- `view_list()` - List views
- `view_switch(view_name)` - Switch view
- `view_current()` - Get current view
- `view_stats()` - View stats
- `view_show(view_name, project_id?)` - Show view

**History (3)**
- `history_show(project_id?, limit=10)` - Change history
- `history_version(item_id)` - Version history
- `history_rollback(item_id, version, confirm=True)` - Rollback (DESTRUCTIVE)

**Agents (5)**
- `agent_list(project_id?)` - List agents
- `agent_activity(agent_id?)` - Activity log
- `agent_metrics(agent_id?)` - Performance metrics
- `agent_workload(agent_id?)` - Workload status
- `agent_health(agent_id?)` - Health check

**State (2)**
- `state_show()` - Show system state
- `state_get(key)` - Get state value

**Other (2)**
- `drill_item(item_id, depth=2, project_id?)` - Drill into item
- `dashboard_show(project_id?)` - Show dashboard

## Tool Files

```
src/tracertm/mcp/tools/
├── auth_config_db.py (18 tools) - auth, config, db
├── design_ingest_migration.py (18 tools) - design, ingest, migration, links
└── optional_features.py (19 tools) - views, history, agents, state, drill, dashboard
```

## Standard Response Format

All tools return:
```python
{
    "ok": True/False,
    "action": "tool_name",
    "data": { /* result */ },      # if ok=True
    "error": "message",             # if ok=False
    "error_code": "CODE",          # if ok=False
    "actor": {                      # always present if context available
        "client_id": "...",
        "sub": "...",
        "email": "..."
    }
}
```

## Common Parameters

- `ctx: Context` - MCP context (always first parameter)
- `project_id: str?` - Falls back to current_project_id from config
- `confirm: bool` - Required for destructive operations
- `trace_dir: str?` - Falls back to current directory

## Error Codes

- `ERROR` - Generic error
- `NO_PROJECT` - No project selected
- `NO_DATABASE_URL` - DB URL not configured
- `AUTH_ERROR` - Authentication failed
- `INVALID_AUTH_RESPONSE` - Bad auth response
- `DEVICE_CODE_EXPIRED` - Auth device code expired
- `ACCESS_DENIED` - User denied auth
- `CONFIRMATION_REQUIRED` - Destructive op needs confirm=True
- `MIGRATION_FAILED` - Migration error
- And more specific codes per tool

## Usage Examples

### Authentication Flow
```python
# 1. Login
auth_login(
    authkit_domain="https://your-app.authkit.app",
    client_id="your_client_id",
    scopes="profile email"
)

# 2. Check status
auth_status()  # Returns {"authenticated": True, ...}

# 3. Logout
auth_logout()
```

### Configuration
```python
# 1. Initialize
config_init(database_url="sqlite:///tracertm.db")

# 2. View config
config_show()  # DB URL masked, token hidden

# 3. Update value
config_set("current_project_id", "proj-123")

# 4. List all
config_list()
```

### Database
```python
# 1. Initialize
db_init()

# 2. Check health
db_status()  # Shows tables, pool size, version

# 3. Run migrations
db_migrate()  # Creates tables

# 4. Reset (careful!)
db_reset(confirm=True)  # Requires confirmation
```

### Data Ingestion
```python
# 1. Directory ingestion
ingest_directory(
    directory_path="/path/to/items",
    project_name="my_project",
    recursive=True
)

# 2. Markdown ingestion
ingest_markdown(
    file_path="/path/to/items.md",
    project_name="my_project"
)

# 3. Generic file
ingest_file(
    file_path="/path/to/data.json",
    file_type="json",
    project_name="my_project"
)
```

### Link Analysis
```python
# 1. Find missing links
link_detect_missing(project_id="proj-123")

# 2. Find orphans
link_detect_orphans(project_id="proj-123")

# 3. Auto-link
link_auto_link(project_id="proj-123", threshold=0.8)
```

### Design Integration
```python
# 1. Initialize
design_init(
    figma_token="token_here",
    figma_file_id="file_id_here"
)

# 2. Link component
design_link(
    component_name="Button",
    figma_url="https://figma.com/..."
)

# 3. List links
design_list()

# 4. Check status
design_status()
```

### Views
```python
# 1. List available views
view_list()  # Returns {views: [...]}

# 2. Switch view
view_switch(view_name="graph")

# 3. Get current
view_current()  # Returns {current_view: "graph"}

# 4. Show view
view_show(view_name="matrix", project_id="proj-123")
```

### System State
```python
# 1. Show state
state_show()  # Returns config state

# 2. Get specific value
state_get(key="current_project_id")
```

## Important Notes

1. **Context Required**: All tools accept `ctx: Context` as first parameter
   - Enables actor extraction for audit trails
   - Can be None (graceful fallback)

2. **Project Selection**: Most tools use config's current_project_id
   - Explicit project_id parameter overrides

3. **Sensitive Data Masking**:
   - Database URLs: password masked (shows host/db only)
   - Auth tokens: shown as `***`
   - Never stored in logs

4. **Confirmation Requirements**:
   - `db_rollback(confirm=True)` - Must explicitly confirm
   - `db_reset(confirm=True)` - Must explicitly confirm
   - `history_rollback(..., confirm=True)` - Must explicitly confirm
   - Prevents accidental data loss

5. **Async-Ready**:
   - Design sync, ingestion operations designed for background tasks
   - Return immediately with "pending" status
   - Can be integrated with job queue system

## CLI Command Mapping

Each CLI command has a corresponding MCP tool:

| CLI Command | MCP Tool |
|---|---|
| `rtm auth login` | `auth_login` |
| `rtm auth status` | `auth_status` |
| `rtm auth logout` | `auth_logout` |
| `rtm config init` | `config_init` |
| `rtm config show` | `config_show` |
| `rtm config set` | `config_set` |
| `rtm config get` | `config_get` |
| `rtm config unset` | `config_unset` |
| `rtm config list` | `config_list` |
| `rtm db init` | `db_init` |
| `rtm db status` | `db_status` |
| `rtm db migrate` | `db_migrate` |
| `rtm db rollback` | `db_rollback` |
| `rtm db reset` | `db_reset` |
| `rtm design init` | `design_init` |
| `rtm design link` | `design_link` |
| `rtm design sync` | `design_sync` |
| `rtm design generate` | `design_generate` |
| `rtm design status` | `design_status` |
| `rtm design list` | `design_list` |
| (and 40+ more) | |

## Testing MCP Tools

### Via Claude MCP Client
```bash
# Start server
python -m tracertm.mcp.server

# In another terminal, call a tool
# (depends on client library)
```

### Via Python Tests
```python
# Import mcp instance
from tracertm.mcp.core import mcp

# Get all registered tools
tools = mcp.list_tools()
for tool in tools:
    print(tool.name, tool.description)
```

## Troubleshooting

**Tool not found**: Check that module is imported in `__init__.py`

**Context errors**: Pass `None` for ctx if not available (all tools handle this)

**Database errors**: Run `db_init` and `db_migrate` first

**Auth errors**: Check WORKOS_CLIENT_ID and WORKOS_AUTHKIT_DOMAIN env vars

**Confirmation required**: Add `confirm=True` to destructive operations

---

**Total Tools**: 80 (25 existing + 55 new)
**Phases Completed**: 3/4
**Next Phase**: Phase 4 - Testing & Documentation
