# CLI ↔ MCP Capability Matrix

This is a high-level mapping of CLI command groups to MCP tools.

## Core Project/Item/Link/Traceability

| CLI Group | CLI Commands (sample) | MCP (Legacy) | MCP (Parameterized) |
|---|---|---|---|
| project | init, list, switch, clone, export, import, template | create_project, list_projects, select_project, snapshot_project | project_manage(action=...) |
| item | create, list, show, update, delete, bulk-* | create_item, get_item, update_item, delete_item, query_items, summarize_view, bulk_update_items | item_manage(action=...) |
| link | create, list, show, graph, matrix, impact | create_link, list_links, show_links, get_trace_matrix, analyze_impact | link_manage(action=...) + trace_analyze(kind=...) |
| view | list, show, stats, switch | summarize_view (limited) | item_manage(action="summarize_view") |
| graph | detect-cycles, shortest_path | detect_cycles, shortest_path | graph_analyze(kind=...) |
| traceability | matrix, gaps, impact | get_trace_matrix, find_gaps, analyze_impact | trace_analyze(kind=...) |

## Specs & Quality

| CLI Group | CLI Commands | MCP (Legacy) | MCP (Parameterized) |
|---|---|---|---|
| specs | n/a | create_adr, list_adrs, create_contract, create_feature, create_scenario | spec_manage(kind, action, payload) |
| quality | n/a | analyze_quality | quality_analyze(payload) |

## CLI-only (not yet exposed via MCP)
- migrate, history, state, query, search, dashboard

## Newly Exposed via MCP (Parameterized)
| CLI Group | MCP (Parameterized) |
|---|---|
| config | config_manage(action=...) |
| sync | sync_manage(action=...) |
| backup | backup_manage(action=...) |
| export | export_manage(action=...) |
| import | import_manage(action=...) |
| ingest | ingest_manage(action=...) |
| watch | watch_manage(action=...) |
| db | db_manage(action=...) |
| agents | agents_manage(action=...) |
| progress | progress_manage(action=...) |
| saved-queries | saved_queries_manage(action=...) |
| test | test_manage(action=...) |
| tui | tui_manage(action=...) |
| benchmark | benchmark_manage(action=...) |
| chaos | chaos_manage(action=...) |
| design | design_manage(action=...) |

## Notes
- Legacy tools remain for compatibility; parameterized tools are recommended for agents.
- CLI-only tools may be added to MCP in future phases if needed.
