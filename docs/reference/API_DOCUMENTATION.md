# TraceRTM API Documentation

## Overview

TraceRTM is a comprehensive traceability management system for tracking relationships between requirements, code, and tests.

---

## Core Services

### ProjectRepository
Manages project CRUD operations.

```python
# Create project
project = await project_repo.create(
    name="My Project",
    description="Project description"
)

# Get project
project = await project_repo.get_by_id(project_id)

# Update project
updated = await project_repo.update(
    project_id=project_id,
    name="Updated Name"
)

# List all projects
projects = await project_repo.get_all()
```

### ItemRepository
Manages item CRUD with optimistic locking.

```python
# Create item
item = await item_repo.create(
    project_id=project_id,
    title="Feature Title",
    view="FEATURE",
    item_type="feature",
    status="todo",
    description="Optional description"
)

# Get item
item = await item_repo.get_by_id(item_id)

# Update item (with optimistic locking)
updated = await item_repo.update(
    item_id=item_id,
    expected_version=item.version,
    status="in_progress"
)

# Query items
items = await item_repo.query(
    project_id=project_id,
    filters={"status": "todo"}
)

# Get items by view
features = await item_repo.get_by_view(
    project_id=project_id,
    view="FEATURE"
)
```

### LinkRepository
Manages traceability links between items.

```python
# Create link
link = await link_repo.create(
    project_id=project_id,
    source_item_id=feature_id,
    target_item_id=code_id,
    link_type="implements"
)

# Get links for item
links = await link_repo.get_links_for_item(item_id)

# Get links by source
outgoing = await link_repo.get_by_source(item_id)

# Get links by target
incoming = await link_repo.get_by_target(item_id)
```

### TraceabilityService
Generates traceability matrices and impact analysis.

```python
# Generate matrix
matrix = await traceability.generate_matrix(
    project_id=project_id,
    source_view="FEATURE",
    target_view="CODE"
)

# Analyze impact
impact = await traceability.analyze_impact(item_id)
```

### ExportService
Exports project data in multiple formats.

```python
# Export to JSON
json_data = await export_service.export_to_json(project_id)

# Export to CSV
csv_data = await export_service.export_to_csv(project_id)

# Export to Markdown
md_data = await export_service.export_to_markdown(project_id)

# Export traceability matrix
matrix_csv = await export_service.export_traceability_matrix(
    project_id=project_id,
    source_view="FEATURE",
    target_view="CODE"
)
```

### ImportService
Imports project data from external sources.

```python
# Import from JSON
result = await import_service.import_from_json(json_data)

# Validate import data
errors = await import_service.validate_import_data(json_data)
```

### PerformanceService
Analyzes and optimizes performance.

```python
# Analyze performance
analysis = await perf_service.analyze_query_performance(project_id)

# Get project statistics
stats = await perf_service.get_project_statistics(project_id)

# Get recommendations
recommendations = await perf_service.recommend_optimizations(project_id)
```

---

## Data Models

### Project
```python
{
    "id": "project-1",
    "name": "My Project",
    "description": "Project description",
    "created_at": "2025-11-21T00:00:00",
    "updated_at": "2025-11-21T00:00:00"
}
```

### Item
```python
{
    "id": "item-1",
    "project_id": "project-1",
    "title": "Feature Title",
    "view": "FEATURE",
    "type": "feature",
    "status": "todo",
    "description": "Optional description",
    "version": 1,
    "created_at": "2025-11-21T00:00:00",
    "updated_at": "2025-11-21T00:00:00"
}
```

### Link
```python
{
    "id": "link-1",
    "project_id": "project-1",
    "source_item_id": "item-1",
    "target_item_id": "item-2",
    "link_type": "implements",
    "created_at": "2025-11-21T00:00:00"
}
```

---

## Error Handling

All services use consistent error handling:

```python
try:
    result = await service.operation()
except ValueError as e:
    # Validation error
    print(f"Validation error: {e}")
except Exception as e:
    # Other errors
    print(f"Error: {e}")
```

---

## Best Practices

1. **Always use optimistic locking** when updating items
2. **Validate data** before importing
3. **Use transactions** for multi-step operations
4. **Monitor performance** for large projects
5. **Export regularly** for backup purposes

