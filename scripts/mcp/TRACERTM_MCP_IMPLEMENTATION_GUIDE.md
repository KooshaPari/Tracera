# TraceRTM MCP Server – Implementation Guide

## Overview

The TraceRTM MCP server (`tracertm-mcp`) is a FastMCP 3.0.0b1 implementation that exposes TraceRTM's project/requirements/traceability model as a set of MCP tools, resources, and prompts.

**Current Status:** Phase 1 complete – 21 tools fully implemented and tested.

## Architecture

### Core Components

1. **ConfigManager** – Manages database_url, current_project_id, and project-specific config
2. **DatabaseConnection** – Sync SQLAlchemy engine for project/item/link CRUD
3. **Services** – Async services for traceability, impact analysis, cycle detection, etc.
4. **Models** – Project, Item, Link, Event (SQLAlchemy ORM)

### Tool Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Projects | 4 | Create, list, select, snapshot projects |
| Items | 7 | Full CRUD + query + summarize |
| Links | 3 | Create, list, show traceability |
| Traceability | 5 | Gaps, matrix, impact analysis, health |
| Graph | 2 | Cycle detection, shortest path |

## Running the Server

### Direct Execution
```bash
python -m tracertm.mcp
```

### Via FastMCP CLI
```bash
fastmcp run src/tracertm/mcp/server.py
```

### Configuration
Requires `rtm config init` to set database_url:
```bash
rtm config init --database-url "sqlite:///tracertm.db"
```

## Tool Usage Patterns

### Pattern 1: Project-scoped operations
Most tools require a current project (set via `select_project`):
```
1. list_projects()
2. select_project(project_id)
3. create_item(...) – uses current project
```

### Pattern 2: Analysis workflows
Traceability tools use async services:
```
1. project_health() – get overview
2. find_gaps(from_view, to_view) – identify missing links
3. analyze_impact(item_id) – understand downstream effects
```

### Pattern 3: Graph queries
Graph tools find paths and cycles:
```
1. detect_cycles() – find circular dependencies
2. shortest_path(source_id, target_id) – find connection
```

## Next Phases

### Phase 2: Resources
- `tracertm://current-project` – current project metadata
- `tracertm://project/{id}/summary` – project overview
- `tracertm://project/{id}/trace-matrix` – traceability matrix
- `tracertm://project/{id}/gaps/{from}-to-{to}` – gap report
- `tracertm://project/{id}/activity-log` – recent changes

### Phase 3: Prompts
- `tracertm.plan_iteration` – iteration planning
- `tracertm.groom_backlog` – backlog prioritization
- `tracertm.analyze_risk` – risk assessment
- `tracertm.implement_feature_with_traceability` – guided feature implementation

### Phase 4: Production Features
- Authentication & authorization
- Caching & performance optimization
- Advanced filtering & search
- Webhook support
- Rate limiting

## Testing

Core unit tests pass (config, DB models):
```bash
pytest tests/unit/test_config_manager.py tests/unit/test_database_models.py -v
```

MCP-specific tests (Phase 2) will cover tool invocation with temp SQLite DB.

## References

- **Design:** `scripts/mcp/TRACE_RTM_MCP_DESIGN.md`
- **Tools Summary:** `scripts/mcp/TRACERTM_MCP_TOOLS_SUMMARY.md`
- **TraceRTM PRD:** `docs/PRD.md`
- **Architecture:** `docs/architecture.md`
