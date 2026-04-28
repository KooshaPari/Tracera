# TraceRTM Example Workflows

## Workflow 1: Complete Project Traceability

### Scenario
Track a feature from requirement through implementation to testing.

### Steps

```python
from tracertm import TraceRTM

trace = TraceRTM()

# 1. Create project
project = trace.create_project(
    "Payment System",
    "Traceability for payment processing"
)

# 2. Create requirement
req = trace.create_item(
    project_id=project.id,
    title="Process Credit Card Payments",
    view="REQUIREMENT",
    item_type="requirement",
    status="approved"
)

# 3. Create design
design = trace.create_item(
    project_id=project.id,
    title="Payment Service Architecture",
    view="DESIGN",
    item_type="design",
    status="completed"
)

# 4. Create implementation
code = trace.create_item(
    project_id=project.id,
    title="payment_service.py",
    view="CODE",
    item_type="file",
    status="in_progress"
)

# 5. Create test
test = trace.create_item(
    project_id=project.id,
    title="test_payment_service.py",
    view="TEST",
    item_type="test",
    status="in_progress"
)

# 6. Link them
trace.create_link(project.id, req.id, design.id, "designed_by")
trace.create_link(project.id, design.id, code.id, "implemented_by")
trace.create_link(project.id, code.id, test.id, "tested_by")

# 7. Generate matrix
matrix = trace.generate_matrix(
    project.id,
    "REQUIREMENT",
    "TEST"
)

print(f"Coverage: {matrix.coverage_percentage}%")
```

---

## Workflow 2: Impact Analysis

### Scenario
Analyze impact of changing a requirement.

### Steps

```python
# Get the requirement
requirement = trace.get_item(req.id)

# Analyze impact
impact = trace.analyze_impact(requirement.id)

print(f"Direct impact: {len(impact.directly_affected)} items")
print(f"Indirect impact: {len(impact.indirectly_affected)} items")

# Update requirement
trace.update_item(
    item_id=requirement.id,
    expected_version=requirement.version,
    title="Process Credit Card and PayPal Payments"
)

# Notify affected items
for item_id in impact.directly_affected:
    item = trace.get_item(item_id)
    print(f"Affected: {item.title}")
```

---

## Workflow 3: Bulk Update with Preview

### Scenario
Update multiple items and preview changes before committing.

### Steps

```python
# Preview bulk update
preview = trace.preview_bulk_update(
    project_id=project.id,
    filters={"status": "todo"},
    updates={"status": "in_progress"}
)

print(f"Will update {preview.total_count} items")
print(f"Sample: {preview.sample_items}")

# Check for warnings
if preview.has_warnings():
    print("Warnings:")
    for warning in preview.warnings:
        print(f"  - {warning}")
else:
    # Execute update
    updated = trace.execute_bulk_update(
        project_id=project.id,
        filters={"status": "todo"},
        updates={"status": "in_progress"}
    )
    print(f"Updated {len(updated)} items")
```

---

## Workflow 4: Export and Backup

### Scenario
Export project for backup and sharing.

### Steps

```python
# Export to JSON
json_data = trace.export_to_json(project.id)

# Save to file
with open("project_backup.json", "w") as f:
    f.write(json_data)

# Export to CSV
csv_data = trace.export_to_csv(project.id)

with open("items.csv", "w") as f:
    f.write(csv_data)

# Export traceability matrix
matrix_csv = trace.export_traceability_matrix(
    project.id,
    "REQUIREMENT",
    "CODE"
)

with open("traceability_matrix.csv", "w") as f:
    f.write(matrix_csv)

# Export to Markdown report
md_data = trace.export_to_markdown(project.id)

with open("project_report.md", "w") as f:
    f.write(md_data)
```

---

## Workflow 5: Import and Merge

### Scenario
Import project from external source and merge with existing.

### Steps

```python
# Read import file
with open("external_project.json", "r") as f:
    json_data = f.read()

# Validate import data
errors = trace.validate_import_data(json_data)

if errors:
    print("Import errors:")
    for error in errors:
        print(f"  - {error}")
else:
    # Import project
    result = trace.import_from_json(json_data)
    
    print(f"Imported {result['items_imported']} items")
    print(f"Imported {result['links_imported']} links")
```

---

## Workflow 6: Performance Analysis

### Scenario
Analyze project performance and get optimization recommendations.

### Steps

```python
# Get project statistics
stats = trace.get_project_statistics(project.id)

print(f"Items: {stats['item_count']}")
print(f"Links: {stats['link_count']}")
print(f"Complexity: {stats['complexity']}")

# Get recommendations
recommendations = trace.recommend_optimizations(project.id)

print("Optimization recommendations:")
for rec in recommendations:
    print(f"  - {rec}")
```

---

## Workflow 7: Audit Trail

### Scenario
Review audit trail for compliance and debugging.

### Steps

```python
# Get audit trail for project
trail = trace.get_audit_trail(project.id)

print("Recent events:")
for event in trail[:10]:
    print(f"  {event.timestamp}: {event.event_type} - {event.description}")

# Get history for specific item
item_history = trace.get_item_history(item.id)

print(f"Item {item.title} has {len(item_history)} events")

# Replay events to reconstruct state
state = trace.replay_events(item.id)

print(f"Item state: {state}")
```

---

## Workflow 8: Multi-Agent Coordination

### Scenario
Coordinate multiple agents working on same project.

### Steps

```python
# Register agents
agent1 = trace.register_agent(
    project_id=project.id,
    name="Requirements Agent",
    agent_type="requirements"
)

agent2 = trace.register_agent(
    project_id=project.id,
    name="Implementation Agent",
    agent_type="implementation"
)

# Detect conflicts
conflicts = trace.detect_conflicts(project.id)

if conflicts:
    print("Conflicts detected:")
    for conflict in conflicts:
        print(f"  {conflict.description}")
        
        # Resolve conflict
        resolution = trace.resolve_conflict(
            project.id,
            conflict,
            strategy="last_write_wins"
        )
        print(f"  Resolved: {resolution.winner_agent_id} wins")
```

