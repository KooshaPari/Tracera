# Agent Integration Guide

**Version:** 1.0  
**Last Updated:** 2025-01-27

---

## Overview

This guide explains how to build AI agents that interact with TraceRTM using the Python API. It covers agent registration, CRUD operations, conflict detection, and best practices.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Agent Registration](#agent-registration)
3. [Basic Operations](#basic-operations)
4. [Advanced Features](#advanced-features)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
pip install tracertm
```

### Import Client

```python
from tracertm.api.client import TraceRTMClient

# Create client instance
client = TraceRTMClient()
```

---

## Agent Registration

### Register an Agent

```python
# Register agent with name and description
agent = client.register_agent(
    agent_name="my-agent",
    agent_description="My AI agent for feature development"
)

print(f"Agent ID: {agent['agent_id']}")
```

### Assign Agent to Projects

```python
# Assign agent to single project
client.assign_agent_to_projects(
    agent_name="my-agent",
    project_names=["My Project"]
)

# Assign agent to multiple projects
client.assign_agent_to_projects(
    agent_name="my-agent",
    project_names=["Project A", "Project B", "Project C"]
)
```

### Get Agent Projects

```python
# Get projects assigned to agent
projects = client.get_agent_projects("my-agent")
print(f"Assigned to: {projects}")
```

---

## Basic Operations

### Query Items

```python
# Query items with filters
items = client.query_items(
    project_id="proj-123",
    filters={"status": "todo", "view": "FEATURE"}
)

for item in items:
    print(f"{item['title']} - {item['status']}")
```

### Get Single Item

```python
# Get item by ID
item = client.get_item(
    project_id="proj-123",
    item_id="item-456"
)

print(f"Title: {item['title']}")
print(f"Status: {item['status']}")
print(f"Version: {item['version']}")
```

### Create Item

```python
# Create new item
item = client.create_item(
    project_id="proj-123",
    title="New Feature",
    view="FEATURE",
    item_type="feature",
    description="Feature description",
    status="todo",
    agent_id="my-agent"
)

print(f"Created item: {item['id']}")
```

### Update Item

```python
# Update item (with optimistic locking)
updated = client.update_item(
    project_id="proj-123",
    item_id="item-456",
    status="in_progress",
    agent_id="my-agent"
)

print(f"Updated to version: {updated['version']}")
```

### Delete Item

```python
# Delete item
client.delete_item(
    project_id="proj-123",
    item_id="item-456",
    agent_id="my-agent"
)
```

---

## Advanced Features

### Optimistic Locking

TraceRTM uses optimistic locking to prevent conflicts:

```python
# Get current item
item = client.get_item("proj-123", "item-456")
current_version = item['version']

# Update with version check
try:
    updated = client.update_item(
        project_id="proj-123",
        item_id="item-456",
        status="complete",
        expected_version=current_version,
        agent_id="my-agent"
    )
except ConflictError as e:
    # Handle conflict
    print(f"Conflict detected: {e}")
    # Re-fetch and retry
    item = client.get_item("proj-123", "item-456")
    # ... retry update
```

### Conflict Detection

```python
# Check for conflicts before update
item = client.get_item("proj-123", "item-456")

# Update with conflict detection
try:
    updated = client.update_item(
        project_id="proj-123",
        item_id="item-456",
        status="in_progress",
        agent_id="my-agent"
    )
except ConflictError:
    # Another agent modified this item
    print("Conflict: Item was modified by another agent")
    # Get latest version
    latest = client.get_item("proj-123", "item-456")
    # Decide how to resolve
```

### Structured Filters

```python
# Advanced filtering
items = client.query_items(
    project_id="proj-123",
    filters={
        "status": "todo",
        "view": "FEATURE",
        "priority": "high",
        "owner": "my-agent"
    }
)
```

### Export Project Data

```python
# Export project as JSON
data = client.export_project("proj-123")

# Save to file
import json
with open("export.json", "w") as f:
    json.dump(data, f, indent=2)
```

### Import Data

```python
# Import items from JSON
with open("import.json", "r") as f:
    data = json.load(f)

client.import_data(
    project_id="proj-123",
    data=data,
    agent_id="my-agent"
)
```

---

## Agent Activity Monitoring

### Get Agent Activity

```python
# Get activity for specific agent
activity = client.get_agent_activity(
    agent_name="my-agent",
    limit=50
)

for operation in activity:
    print(f"{operation['timestamp']}: {operation['operation']}")
```

### Get All Agents Activity

```python
# Get activity for all agents
all_activity = client.get_all_agents_activity(limit=100)

for operation in all_activity:
    print(f"{operation['agent_id']}: {operation['operation']}")
```

---

## Best Practices

### 1. Always Register Agents

```python
# Register before first use
agent = client.register_agent("my-agent", "Description")
```

### 2. Use Optimistic Locking

```python
# Always check version before update
item = client.get_item(project_id, item_id)
updated = client.update_item(
    project_id, item_id,
    expected_version=item['version'],
    agent_id=agent_id
)
```

### 3. Handle Conflicts Gracefully

```python
# Retry on conflict
max_retries = 3
for attempt in range(max_retries):
    try:
        item = client.get_item(project_id, item_id)
        updated = client.update_item(
            project_id, item_id,
            expected_version=item['version'],
            agent_id=agent_id
        )
        break
    except ConflictError:
        if attempt == max_retries - 1:
            raise
        time.sleep(0.1)  # Brief delay before retry
```

### 4. Log Operations

```python
# All operations are automatically logged
# Access via get_agent_activity()
activity = client.get_agent_activity("my-agent")
```

### 5. Batch Operations

```python
# For multiple updates, use batch operations
items_to_update = [
    {"id": "item-1", "status": "complete"},
    {"id": "item-2", "status": "complete"},
]

for item_data in items_to_update:
    client.update_item(
        project_id="proj-123",
        item_id=item_data["id"],
        status=item_data["status"],
        agent_id="my-agent"
    )
```

---

## Coordination Patterns

### Pattern 1: Work Assignment

```python
# Agent claims work
items = client.query_items(
    project_id="proj-123",
    filters={"status": "todo", "view": "FEATURE"}
)

# Claim first available item
if items:
    item = items[0]
    client.update_item(
        project_id="proj-123",
        item_id=item['id'],
        status="in_progress",
        owner="my-agent",
        agent_id="my-agent"
    )
```

### Pattern 2: Progress Updates

```python
# Update progress as work completes
client.update_item(
    project_id="proj-123",
    item_id="item-456",
    status="complete",
    agent_id="my-agent"
)
```

### Pattern 3: Conflict Resolution

```python
# Check for conflicts before critical operations
item = client.get_item("proj-123", "item-456")

if item['version'] > last_known_version:
    # Item was modified, handle conflict
    print("Conflict detected, resolving...")
    # Fetch latest and merge changes
    latest = client.get_item("proj-123", "item-456")
    # Apply agent's changes to latest version
```

---

## Troubleshooting

### Issue: "Agent not registered"

**Solution:**
```python
# Register agent first
client.register_agent("my-agent", "Description")
```

### Issue: "Conflict detected"

**Solution:**
```python
# Re-fetch item and retry
item = client.get_item(project_id, item_id)
# Update with latest version
client.update_item(
    project_id, item_id,
    expected_version=item['version'],
    agent_id=agent_id
)
```

### Issue: "Project not found"

**Solution:**
```python
# Verify project exists
projects = client.list_projects()
# Or create project via CLI: rtm project init "My Project"
```

---

## Complete Example

```python
from tracertm.api.client import TraceRTMClient
import time

# Initialize client
client = TraceRTMClient()

# Register agent
agent = client.register_agent(
    agent_name="feature-dev-agent",
    agent_description="Agent for developing features"
)

# Assign to project
client.assign_agent_to_projects(
    agent_name="feature-dev-agent",
    project_names=["My Project"]
)

# Get project ID
projects = client.list_projects()
project_id = projects[0]['id']

# Query todo items
items = client.query_items(
    project_id=project_id,
    filters={"status": "todo", "view": "FEATURE"}
)

# Work on first item
if items:
    item = items[0]
    
    # Claim item
    client.update_item(
        project_id=project_id,
        item_id=item['id'],
        status="in_progress",
        owner="feature-dev-agent",
        agent_id="feature-dev-agent"
    )
    
    # ... do work ...
    
    # Mark complete
    client.update_item(
        project_id=project_id,
        item_id=item['id'],
        status="complete",
        agent_id="feature-dev-agent"
    )

# Check activity
activity = client.get_agent_activity("feature-dev-agent")
print(f"Agent performed {len(activity)} operations")
```

---

## Summary

✅ **Agent registered and assigned**  
✅ **CRUD operations working**  
✅ **Optimistic locking implemented**  
✅ **Conflict detection active**  
✅ **Activity monitoring enabled**

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
