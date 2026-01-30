# Phase 3: Capability Parity Audit

## Executive Summary

This audit identifies capability gaps between CLI commands and MCP tools to achieve feature parity. Current state:
- **CLI Commands**: 23 major command groups (agents, auth, backup, benchmark, chaos, config, dashboard, db, design, drill, export, history, import_cmd, ingest, item, link, migrate, progress, project, query, saved_queries, search, state, test, tui, view, watch)
- **MCP Tools**: 25 tools across 8 modules
- **Target**: 100% feature parity with consistent behavior

## Part 1: MCP Tools Inventory

### Current MCP Tools (25 total)

**Legacy TraceRTM Module (21 tools)**
- Projects (4): create_project, list_projects, select_project, snapshot_project
- Items (7): create_item, get_item, update_item, delete_item, query_items, summarize_view, bulk_update_items
- Links (3): create_link, list_links, show_links
- Traceability (5): find_gaps, get_trace_matrix, analyze_impact, analyze_reverse_impact, project_health
- Graph (2): detect_cycles, shortest_path

**Specifications Module (2 tools)**
- create_specification, update_specification

**BMM Workflows Module (2 tools)**
- run_workflow, run_phase

**Param Module (1 tool)**
- get_status

**Undocumented**
- init_project (in param.py)

## Part 2: CLI Commands Inventory

### Organized by Domain

**Authentication (auth)**
- login, status, logout

**Project Management (project)**
- init, list, switch, export, import, clone, template

**Item Operations (item)**
- create, list, show, update, delete, undelete, bulk-update

**Link Operations (link)**
- create, list, show, delete, detect-cycles, detect-missing, detect-orphans, impact, auto-link, graph

**Traceability & Queries (search, query, saved_queries)**
- search, query, save [query], list [queries], run [query], delete [query]

**Import/Export (import_cmd, export)**
- import {json, yaml, jira, github}, export

**Data Ingestion (ingest)**
- directory, markdown, mdx, yaml, file

**Configuration (config)**
- init, show, set, get, unset, list

**Database (db)**
- init, status, migrate, rollback, reset

**Design Integration (design)**
- init, link, sync, generate, status, list, export

**Testing (test)**
- test, list, python, go, e2e

**Monitoring & Progress (progress, benchmark, chaos)**
- show, track, blocked, stalled, velocity, report
- views, refresh, report
- explode, crash, zombies, snapshot, enable, disable

**Agents (agents)**
- list, activity, metrics, workload, health

**System (history, migrate, state, tui, view, watch, dashboard, drill)**
- history operations: show, version, rollback
- migrate: migrate_project
- state: show_state
- tui: dashboard, browser, graph, list
- view: list, switch, current, stats, show
- watch: watch
- dashboard: dashboard
- drill: drill

## Part 3: Gap Analysis

### CLI-Only Features (Need MCP Tools)

1. **Authentication (auth)** - No MCP equivalent
   - login, status, logout → MCP: auth_login, auth_status, auth_logout
   - Status: CRITICAL - Authentication is fundamental

2. **Configuration Management (config)** - No MCP equivalent
   - init, show, set, get, unset, list → MCP: config_init, config_show, config_set, config_get, config_unset, config_list
   - Status: IMPORTANT - Required for system setup

3. **Database Management (db)** - No MCP equivalent
   - init, status, migrate, rollback, reset → MCP: db_init, db_status, db_migrate, db_rollback, db_reset
   - Status: IMPORTANT - Critical infrastructure

4. **Design Integration (design)** - No MCP equivalent
   - init, link, sync, generate, status, list, export → MCP: design_init, design_link, design_sync, design_generate, design_status, design_list
   - Status: IMPORTANT - Feature parity for integrations

5. **Ingestion Commands (ingest)** - Partial MCP coverage
   - directory, markdown, mdx, yaml, file → MCP: ingest_* (need all)
   - Status: IMPORTANT - Data pipeline

6. **Migration (migrate)** - No MCP equivalent
   - migrate_project → MCP: migrate_project
   - Status: IMPORTANT - Data migration

7. **Link Analysis (link)** - Partial MCP coverage
   - detect-missing, detect-orphans, auto-link, graph → MCP: link_detect_missing, link_detect_orphans, link_auto_link, link_graph
   - Status: IMPORTANT - Advanced traceability

8. **State Management (state)** - No MCP equivalent
   - show_state → MCP: get_state (or show_state)
   - Status: OPTIONAL - Debug/monitoring

9. **View Management (view)** - No MCP equivalent
   - list, switch, current, stats, show → MCP: view_list, view_switch, view_current, view_stats, view_show
   - Status: OPTIONAL - View switching

10. **History & Rollback (history)** - Partial MCP coverage
    - show, version, rollback_item → MCP: history_show, history_version, history_rollback
    - Status: OPTIONAL - Audit/recovery

11. **TUI Commands (tui)** - No MCP equivalent
    - dashboard, browser, graph, list → MCP tools NOT APPLICABLE (TUI-specific)
    - Status: N/A - Terminal UI commands

12. **Drill Command (drill)** - No MCP equivalent
    - drill → MCP: drill_item
    - Status: OPTIONAL - Visualization

13. **Dashboard Command (dashboard)** - No MCP equivalent
    - dashboard → MCP: dashboard_show or launch_dashboard
    - Status: OPTIONAL - UI command

14. **Agents (agents)** - Partial MCP coverage
    - list, activity, metrics, workload, health → MCP: agent_list, agent_activity, agent_metrics, agent_workload, agent_health
    - Status: OPTIONAL - Agent monitoring

15. **Performance Tools (benchmark, chaos)** - No MCP equivalent
    - benchmark_views, benchmark_refresh, performance_report
    - chaos_explode, crash, zombies, snapshot, enable, disable
    - Status: OPTIONAL - Testing/QA tools

### MCP-Only Features (Need CLI Commands)

1. **init_project** - Exists in MCP (param.py) but may lack CLI command
   - Status: Check if `project init` covers this

2. **run_workflow, run_phase** - BMM Workflow tools
   - Status: Check if these need CLI equivalents

3. **create_specification, update_specification** - Specs module
   - Status: May already have CLI support via item or design commands

## Part 4: Implementation Plan

### Priority 1: CRITICAL (Block Release)
1. Auth tools: auth_login, auth_status, auth_logout
2. Config tools: config_init, config_show, config_set, config_get, config_unset, config_list
3. DB tools: db_init, db_status, db_migrate, db_rollback, db_reset

### Priority 2: IMPORTANT (Core Features)
1. Design tools: design_init, design_link, design_sync, design_generate, design_status
2. Ingest tools: ingest_directory, ingest_markdown, ingest_mdx, ingest_yaml, ingest_file
3. Link analysis: link_detect_missing, link_detect_orphans, link_auto_link
4. Migration: migrate_project (ensure exists)

### Priority 3: OPTIONAL (Enhanced Features)
1. View management: view_list, view_switch, view_current, view_stats
2. History: history_show, history_version, history_rollback
3. Agents: agent_list, agent_activity, agent_metrics, agent_workload
4. State: get_state, show_state
5. Drill: drill_item

### Priority 4: TESTING/QA (May Skip for MVP)
1. Benchmark tools (performance testing)
2. Chaos tools (failure injection)
3. TUI commands (not applicable to MCP)

## Part 5: Response Format Standardization

### Current MCP Response Format
```python
{
    "ok": True,
    "action": "action_name",
    "data": result_data,
    "actor": actor_info
}
```

### CLI Response Format
- Typically returns structured data via click output
- Should map to MCP format

### Standardization Rules
1. All MCP responses use the 5-field format above
2. All CLI commands use consistent error handling
3. Validation errors are consistent (Zod-like schemas)
4. Timestamps use ISO 8601 format
5. IDs are strings (UUIDs or external IDs)

## Part 6: Next Steps

1. ✓ Complete this audit (DONE)
2. Implement Priority 1 tools (auth, config, db)
3. Implement Priority 2 tools (design, ingest, link, migrate)
4. Add missing CLI commands for MCP-only features
5. Test capability parity
6. Document all tools
7. Update version to reflect parity achievement
