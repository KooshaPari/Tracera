# TraceRTM User Guide

## Getting Started

### Installation

```bash
pip install tracertm
```

### Quick Start

```python
from tracertm import TraceRTM

# Initialize
trace = TraceRTM()

# Create project
project = trace.create_project("My Project", "Project description")

# Create items
feature = trace.create_item(
    project_id=project.id,
    title="User Authentication",
    view="FEATURE",
    item_type="feature"
)

code = trace.create_item(
    project_id=project.id,
    title="auth.py",
    view="CODE",
    item_type="file"
)

# Create link
trace.create_link(
    project_id=project.id,
    source_id=feature.id,
    target_id=code.id,
    link_type="implements"
)

# Generate matrix
matrix = trace.generate_matrix(project.id, "FEATURE", "CODE")
print(f"Coverage: {matrix.coverage_percentage}%")
```

---

## Common Workflows

### 1. Create a Traceability Project

```python
# Create project
project = trace.create_project(
    name="E-Commerce Platform",
    description="Traceability for e-commerce system"
)

# Create items for each view
requirements = trace.create_item(
    project_id=project.id,
    title="User Registration",
    view="REQUIREMENT",
    item_type="requirement"
)

design = trace.create_item(
    project_id=project.id,
    title="Auth Service Design",
    view="DESIGN",
    item_type="design"
)

implementation = trace.create_item(
    project_id=project.id,
    title="auth_service.py",
    view="CODE",
    item_type="file"
)

test = trace.create_item(
    project_id=project.id,
    title="test_auth.py",
    view="TEST",
    item_type="test"
)

# Link them
trace.create_link(project.id, requirements.id, design.id, "designed_by")
trace.create_link(project.id, design.id, implementation.id, "implemented_by")
trace.create_link(project.id, implementation.id, test.id, "tested_by")
```

### 2. Generate Traceability Matrix

```python
# Generate matrix
matrix = trace.generate_matrix(
    project_id=project.id,
    source_view="REQUIREMENT",
    target_view="CODE"
)

# Check coverage
print(f"Coverage: {matrix.coverage_percentage}%")
print(f"Gaps: {matrix.gaps}")

# Export matrix
csv_data = trace.export_matrix_to_csv(matrix)
```

### 3. Analyze Impact

```python
# Analyze impact of changing a requirement
impact = trace.analyze_impact(requirement_id)

print(f"Direct impact: {len(impact.directly_affected)} items")
print(f"Indirect impact: {len(impact.indirectly_affected)} items")
```

### 4. Export and Import

```python
# Export project
json_data = trace.export_to_json(project.id)

# Save to file
with open("project.json", "w") as f:
    f.write(json_data)

# Import project
with open("project.json", "r") as f:
    imported = trace.import_from_json(f.read())
```

### 5. Bulk Operations

```python
# Update multiple items
updated = trace.bulk_update(
    project_id=project.id,
    filters={"status": "todo"},
    updates={"status": "in_progress"}
)

print(f"Updated {len(updated)} items")
```

---

## Tips and Tricks

### Use Views Effectively
- **REQUIREMENT**: High-level requirements
- **DESIGN**: Design documents and specifications
- **CODE**: Source code files
- **TEST**: Test cases and test files
- **FEATURE**: Feature descriptions

### Link Types
- `implements`: Code implements requirement
- `tests`: Test covers code
- `depends_on`: Item depends on another
- `relates_to`: General relationship
- `designed_by`: Design for requirement

### Performance Tips
1. Use filters when querying large projects
2. Export regularly for backup
3. Monitor project statistics
4. Archive completed items
5. Use bulk operations for large updates

### Best Practices
1. Keep item titles descriptive
2. Use consistent naming conventions
3. Link items as you create them
4. Review coverage regularly
5. Document link types used

