# TraceRTM MCP Server – Tools Summary

**Server:** `tracertm-mcp` (FastMCP 3.0.0b1)  
**Location:** `src/tracertm/mcp/server.py`  
**Status:** Complete tools section (Phase 1)

## Tools by Category

### 1. Project Management (4 tools)
- **create_project**(name, description?) → {project_id, name, description}
- **list_projects**() → {projects: [{id, name, description, created_at}]}
- **select_project**(project_id) → {project_id, name}
- **snapshot_project**(project_id, label) → {snapshot_id, created_at}

### 2. Item Operations (7 tools)
- **create_item**(title, view, item_type, description?, status='todo', priority='medium', owner?, parent_id?, metadata?) → {id, project_id, title, view, item_type, status, priority, owner, parent_id}
- **get_item**(item_id) → {id, project_id, title, description, view, item_type, status, priority, owner, parent_id, version, created_at, updated_at, metadata}
- **update_item**(item_id, title?, description?, status?, priority?, owner?, metadata?) → {id, project_id, title, view, item_type, status, priority, owner, version}
- **delete_item**(item_id) → {id, deleted_at}
- **query_items**(view?, item_type?, status?, owner?, limit=50) → {project_id, filters, items: [...]}
- **summarize_view**(view) → {project_id, view, total_items, counts_by_status, sample_items}
- **bulk_update_items**(view?, status?, new_status) → {project_id, updated_count, new_status}

### 3. Link Operations (3 tools)
- **create_link**(source_id, target_id, link_type, metadata?) → {id, project_id, source_id, target_id, link_type, metadata}
- **list_links**(item_id?, link_type?, limit=50) → {project_id, count, links: [...]}
- **show_links**(item_id, view?) → {item: {...}, outgoing: [...], incoming: [...]}

### 4. Traceability & Analysis (5 tools)
- **find_gaps**(from_view, to_view) → {project_id, from_view, to_view, coverage_percentage, gaps, link_count}
- **get_trace_matrix**(source_view?, target_view?) → {project_id, rows, columns, matrix, coverage, total_links}
- **analyze_impact**(item_id, max_depth=5, link_types?) → {root_item_id, root_item_title, total_affected, max_depth_reached, affected_by_depth, affected_by_view, affected_items, critical_paths}
- **analyze_reverse_impact**(item_id, max_depth=5) → {root_item_id, root_item_title, total_affected, max_depth_reached, affected_by_depth, affected_by_view, affected_items, critical_paths}
- **project_health**() → {project_id, item_count, link_count, density, complexity, views, statuses}

### 5. Graph Analysis (2 tools)
- **detect_cycles**() → {project_id, has_cycles, cycle_count, severity, affected_items, cycles}
- **shortest_path**(source_id, target_id) → {source_id, target_id, path, distance, link_types, exists}

## Implementation Notes

- **Sync vs. Async:** Project/item/link tools use sync SQLAlchemy (DatabaseConnection); analysis tools use async (get_session).
- **Current Project:** Most tools require a current project (set via select_project or CLI config).
- **Error Handling:** All tools raise ToolError with clear messages on validation failures.
- **Logging:** All tool calls logged via LoggingMiddleware.

## Next Phases

- **Phase 2:** Resources (tracertm://current-project, .../summary, .../trace-matrix, .../gaps, .../activity-log)
- **Phase 3:** Prompts (plan_iteration, groom_backlog, analyze_risk, implement_feature_with_traceability)
- **Phase 4:** Production features (auth, caching, storage, advanced filtering)
