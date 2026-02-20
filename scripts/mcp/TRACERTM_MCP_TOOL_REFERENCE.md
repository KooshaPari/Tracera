# TraceRTM MCP – Complete Tool Reference

## Projects (4 tools)

### create_project
```
create_project(name: str, description?: str) → {project_id, name, description}
```
Creates a new project and sets it as current.

### list_projects
```
list_projects() → {projects: [{id, name, description, created_at}]}
```
Lists all projects in the database.

### select_project
```
select_project(project_id: str) → {project_id, name}
```
Sets the current project for subsequent operations.

### snapshot_project
```
snapshot_project(project_id: str, label: str) → {snapshot_id, created_at}
```
Creates a lightweight snapshot record (YAML file).

## Items (7 tools)

### create_item
```
create_item(title, view, item_type, description?, status='todo', priority='medium', owner?, parent_id?, metadata?) → {id, project_id, title, view, item_type, status, priority, owner, parent_id}
```

### get_item
```
get_item(item_id: str) → {id, project_id, title, description, view, item_type, status, priority, owner, parent_id, version, created_at, updated_at, metadata}
```

### update_item
```
update_item(item_id, title?, description?, status?, priority?, owner?, metadata?) → {id, project_id, title, view, item_type, status, priority, owner, version}
```
Optimistic locking via SQLAlchemy version.

### delete_item
```
delete_item(item_id: str) → {id, deleted_at}
```
Soft-delete (sets deleted_at).

### query_items
```
query_items(view?, item_type?, status?, owner?, limit=50) → {project_id, filters, items}
```

### summarize_view
```
summarize_view(view: str) → {project_id, view, total_items, counts_by_status, sample_items}
```

### bulk_update_items
```
bulk_update_items(view?, status?, new_status) → {project_id, updated_count, new_status}
```

## Links (3 tools)

### create_link
```
create_link(source_id, target_id, link_type, metadata?) → {id, project_id, source_id, target_id, link_type, metadata}
```

### list_links
```
list_links(item_id?, link_type?, limit=50) → {project_id, count, links}
```

### show_links
```
show_links(item_id, view?) → {item, outgoing, incoming}
```

## Traceability (5 tools)

### find_gaps
```
find_gaps(from_view, to_view) → {project_id, from_view, to_view, coverage_percentage, gaps, link_count}
```

### get_trace_matrix
```
get_trace_matrix(source_view?, target_view?) → {project_id, rows, columns, matrix, coverage, total_links}
```

### analyze_impact
```
analyze_impact(item_id, max_depth=5, link_types?) → {root_item_id, root_item_title, total_affected, max_depth_reached, affected_by_depth, affected_by_view, affected_items, critical_paths}
```

### analyze_reverse_impact
```
analyze_reverse_impact(item_id, max_depth=5) → {root_item_id, root_item_title, total_affected, max_depth_reached, affected_by_depth, affected_by_view, affected_items, critical_paths}
```

### project_health
```
project_health() → {project_id, item_count, link_count, density, complexity, views, statuses}
```

## Graph (2 tools)

### detect_cycles
```
detect_cycles() → {project_id, has_cycles, cycle_count, severity, affected_items, cycles}
```

### shortest_path
```
shortest_path(source_id, target_id) → {source_id, target_id, path, distance, link_types, exists}
```

