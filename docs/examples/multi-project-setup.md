# Example Project: Multi-Project Setup

**Project Type:** Multi-Project (3 projects, shared agents)  
**Complexity:** Medium-High  
**Estimated Time:** 6-8 hours

---

## Overview

This example demonstrates managing multiple projects within a single TraceRTM instance, with shared AI agents working across projects. Shows multi-project coordination and dashboard usage.

---

## Setup

```bash
# Initialize configuration
rtm config init --database-url postgresql://user:pass@localhost/tracertm

# Create database
rtm db migrate
```

---

## Project 1: Web Application

```bash
# Create first project
rtm project init "Web Application" --description "Customer-facing web app"
WEB_PROJECT=$(rtm project list | grep "Web Application" | awk '{print $1}')

# Switch to web project
rtm project switch "Web Application"

# Create features
rtm item create "User Authentication" --view FEATURE --type feature
rtm item create "Product Catalog" --view FEATURE --type feature
rtm item create "Shopping Cart" --view FEATURE --type feature

# Create code files
rtm item create "src/auth/login.py" --view CODE --type file
rtm item create "src/products/catalog.py" --view CODE --type file
```

---

## Project 2: Mobile App

```bash
# Create second project
rtm project init "Mobile App" --description "iOS/Android mobile application"
rtm project switch "Mobile App"

# Create features
rtm item create "Mobile Login" --view FEATURE --type feature
rtm item create "Product Browsing" --view FEATURE --type feature
rtm item create "Push Notifications" --view FEATURE --type feature

# Create code files
rtm item create "ios/AuthViewController.swift" --view CODE --type file
rtm item create "android/AuthActivity.kt" --view CODE --type file
```

---

## Project 3: Backend API

```bash
# Create third project
rtm project init "Backend API" --description "RESTful API service"
rtm project switch "Backend API"

# Create features
rtm item create "API Authentication" --view FEATURE --type feature
rtm item create "Product API" --view FEATURE --type feature
rtm item create "Order API" --view FEATURE --type feature

# Create API endpoints
rtm item create "POST /api/v1/auth/login" --view API --type endpoint
rtm item create "GET /api/v1/products" --view API --type endpoint
```

---

## Multi-Project Dashboard

```bash
# View all projects at once
rtm dashboard
```

**Output shows:**
- All 3 projects
- Item counts per project
- Agent assignments
- Status breakdowns
- Current active project marker

---

## Cross-Project Queries

```bash
# Query items across all projects
rtm query --all-projects --status todo

# Search across all projects
rtm search "authentication"  # Searches all projects

# Find items by relationship across projects
rtm query --all-projects --related-to <item-id>
```

---

## Agent Assignment

### Register Agents

```python
from tracertm.api.client import TraceRTMClient

# Create client
client = TraceRTMClient()

# Register agents
agent1 = client.register_agent("web-dev-agent", "Web development agent")
agent2 = client.register_agent("mobile-dev-agent", "Mobile development agent")
agent3 = client.register_agent("api-dev-agent", "API development agent")
```

### Assign Agents to Projects

```python
# Assign agents to projects
client.assign_agent_to_projects("web-dev-agent", ["Web Application"])
client.assign_agent_to_projects("mobile-dev-agent", ["Mobile App"])
client.assign_agent_to_projects("api-dev-agent", ["Backend API"])

# Assign agent to multiple projects
client.assign_agent_to_projects("web-dev-agent", ["Web Application", "Backend API"])
```

### View Agent Activity

```python
# Get agent activity
activity = client.get_agent_activity("web-dev-agent")

# Get all agents activity
all_activity = client.get_all_agents_activity()
```

---

## Project Switching

```bash
# List all projects
rtm project list

# Switch between projects
rtm project switch "Web Application"
rtm item list  # Shows web app items

rtm project switch "Mobile App"
rtm item list  # Shows mobile app items

rtm project switch "Backend API"
rtm item list  # Shows API items
```

---

## Project Export/Import

```bash
# Export individual projects
rtm project switch "Web Application"
rtm project export --output web-app.json

rtm project switch "Mobile App"
rtm project export --output mobile-app.json

rtm project switch "Backend API"
rtm project export --output backend-api.json

# Import projects
rtm project import web-app.json
rtm project import mobile-app.json
```

---

## Cross-Project Progress Tracking

```bash
# Show progress for current project
rtm progress show

# Switch projects and check progress
rtm project switch "Web Application"
rtm progress show

rtm project switch "Mobile App"
rtm progress show
```

---

## Cross-Project Search

```bash
# Search across all projects
rtm search "authentication"  # Finds in all projects

# Search in specific project
rtm project switch "Web Application"
rtm search "authentication"  # Only in web app
```

---

## Agent Coordination

### Python API Example

```python
from tracertm.api.client import TraceRTMClient

client = TraceRTMClient()

# Agent 1: Working on Web Application
client.update_item(
    item_id="web-feature-1",
    status="in_progress",
    agent_id="web-dev-agent"
)

# Agent 2: Working on Mobile App
client.update_item(
    item_id="mobile-feature-1",
    status="in_progress",
    agent_id="mobile-dev-agent"
)

# Check for conflicts
activity = client.get_all_agents_activity()
# Shows all agent operations across all projects
```

---

## Multi-Project Dashboard Usage

```bash
# View dashboard
rtm dashboard

# Output:
# ┌─────────────────┬───────┬────────┬─────────────────────────┬─────────┐
# │ Project         │ Items │ Agents │ Status                  │ Current │
# ├─────────────────┼───────┼────────┼─────────────────────────┼─────────┤
# │ Web Application │ 45    │ 2      │ todo: 20, in_progress: │ ✓       │
# │ Mobile App      │ 32    │ 1      │ todo: 15, complete: 17 │         │
# │ Backend API     │ 28    │ 1      │ todo: 10, blocked: 5   │         │
# └─────────────────┴───────┴────────┴─────────────────────────┴─────────┘
```

---

## Best Practices

### 1. Project Naming

Use clear, descriptive names:
- ✅ "Web Application"
- ✅ "Mobile App iOS"
- ✅ "Backend API Service"
- ❌ "Project 1"
- ❌ "App"

### 2. Agent Assignment

Assign agents to specific projects:
- Web development agent → Web Application
- Mobile development agent → Mobile App
- API development agent → Backend API

### 3. Cross-Project Queries

Use `--all-projects` flag sparingly:
- Good for: Finding duplicates, shared patterns
- Avoid: Regular day-to-day queries (use project switching)

### 4. Project Isolation

Keep projects logically separate:
- Each project has its own items
- Links typically within project
- Cross-project links for shared components

---

## Summary

This multi-project setup demonstrates:
- ✅ Managing 3+ projects in one instance
- ✅ Project switching and isolation
- ✅ Multi-project dashboard
- ✅ Cross-project queries
- ✅ Agent assignment across projects
- ✅ Project export/import
- ✅ Coordinated agent work

**Total Projects:** 3  
**Total Items:** 100+ across all projects  
**Agents:** 3 shared agents  
**Complexity:** Medium-High

---

**Last Updated**: 2025-01-27  
**Version**: 1.0
