# Phase 2: Resources – Planning Document

## Overview

Phase 2 adds **read-only MCP resources** that expose TraceRTM project state as structured data. Resources allow LLM clients to query project context without invoking tools.

**Status:** Planning (not implemented)

## Resource Categories

### 1. Current Project Context (2 resources)

#### tracertm://current-project
**Purpose:** Get metadata about the currently selected project.

**Output Schema:**
```json
{
  "project_id": "uuid",
  "name": "string",
  "description": "string",
  "created_at": "ISO8601",
  "item_count": "integer",
  "link_count": "integer",
  "views": ["FEATURE", "CODE", "TEST", ...],
  "status": "active|archived"
}
```

**Use Case:** LLM needs to know which project is active and basic stats.

#### tracertm://current-project/config
**Purpose:** Get project-specific configuration (views, link types, metadata schema).

**Output Schema:**
```json
{
  "project_id": "uuid",
  "views": ["FEATURE", "CODE", "TEST", "DESIGN", "API", "DOC"],
  "link_types": ["implements", "validates", "documents", "depends_on", ...],
  "item_types": ["requirement", "feature", "task", "bug", ...],
  "statuses": ["todo", "in_progress", "done", "blocked"],
  "priorities": ["low", "medium", "high", "critical"],
  "metadata_schema": {...}
}
```

**Use Case:** LLM needs to understand valid values for creating/updating items.

### 2. Project Summary & Overview (3 resources)

#### tracertm://project/{id}/summary
**Purpose:** High-level project overview (counts, status distribution, health).

**Output Schema:**
```json
{
  "project_id": "uuid",
  "name": "string",
  "total_items": "integer",
  "total_links": "integer",
  "items_by_view": {"FEATURE": 10, "CODE": 8, ...},
  "items_by_status": {"todo": 5, "in_progress": 3, "done": 10},
  "coverage_percentage": "float",
  "complexity_score": "float",
  "health_status": "healthy|warning|critical",
  "last_updated": "ISO8601"
}
```

**Use Case:** LLM gets a quick snapshot of project health.

#### tracertm://project/{id}/views
**Purpose:** Detailed breakdown by view (items per view, status distribution).

**Output Schema:**
```json
{
  "project_id": "uuid",
  "views": [
    {
      "name": "FEATURE",
      "total_items": 10,
      "by_status": {"todo": 2, "in_progress": 3, "done": 5},
      "by_priority": {"low": 1, "medium": 5, "high": 4},
      "sample_items": [{"id": "...", "title": "...", "status": "..."}]
    }
  ]
}
```

**Use Case:** LLM understands work distribution across views.

#### tracertm://project/{id}/activity-log
**Purpose:** Recent changes (items created/updated, links added, status changes).

**Output Schema:**
```json
{
  "project_id": "uuid",
  "events": [
    {
      "timestamp": "ISO8601",
      "event_type": "item_created|item_updated|link_created|status_changed",
      "actor": "string",
      "item_id": "uuid",
      "item_title": "string",
      "details": {...}
    }
  ],
  "total_events": "integer",
  "time_range": {"start": "ISO8601", "end": "ISO8601"}
}
```

**Use Case:** LLM understands recent activity and can reference recent changes.

### 3. Traceability & Coverage (3 resources)

#### tracertm://project/{id}/trace-matrix
**Purpose:** Traceability matrix (rows=source view, cols=target view, cells=link counts).

**Output Schema:**
```json
{
  "project_id": "uuid",
  "source_view": "FEATURE",
  "target_view": "CODE",
  "rows": [{"id": "...", "title": "...", "view": "FEATURE"}],
  "columns": [{"id": "...", "title": "...", "view": "CODE"}],
  "matrix": [[1, 0, 1], [0, 1, 0], ...],
  "coverage_percentage": "float",
  "total_links": "integer",
  "gaps": [{"source_id": "...", "source_title": "...", "target_view": "CODE"}]
}
```

**Use Case:** LLM sees traceability coverage and identifies gaps.

#### tracertm://project/{id}/gaps/{from_view}-to-{to_view}
**Purpose:** Items in from_view with no links to to_view.

**Output Schema:**
```json
{
  "project_id": "uuid",
  "from_view": "FEATURE",
  "to_view": "CODE",
  "gap_count": "integer",
  "coverage_percentage": "float",
  "gaps": [
    {
      "item_id": "uuid",
      "item_title": "string",
      "item_status": "string",
      "priority": "string",
      "owner": "string"
    }
  ]
}
```

**Use Case:** LLM identifies what needs to be traced.

#### tracertm://project/{id}/impact/{item_id}
**Purpose:** Impact analysis (downstream and upstream dependencies).

**Output Schema:**
```json
{
  "item_id": "uuid",
  "item_title": "string",
  "downstream": {
    "total_affected": "integer",
    "by_depth": {"1": 3, "2": 5, "3": 2},
    "by_view": {"CODE": 5, "TEST": 3, "DOC": 2},
    "critical_items": [{"id": "...", "title": "...", "view": "..."}]
  },
  "upstream": {
    "total_affected": "integer",
    "by_depth": {"1": 2, "2": 1},
    "by_view": {"FEATURE": 2, "DESIGN": 1},
    "critical_items": [...]
  }
}
```

**Use Case:** LLM understands change impact before making updates.

### 4. Graph Analysis (2 resources)

#### tracertm://project/{id}/cycles
**Purpose:** Detected dependency cycles.

**Output Schema:**
```json
{
  "project_id": "uuid",
  "has_cycles": "boolean",
  "cycle_count": "integer",
  "severity": "none|low|medium|high|critical",
  "affected_items": ["uuid", "uuid", ...],
  "cycles": [
    {
      "items": ["uuid", "uuid", "uuid"],
      "length": 3,
      "link_types": ["depends_on", "implements", "depends_on"]
    }
  ]
}
```

**Use Case:** LLM identifies circular dependencies to avoid.

#### tracertm://project/{id}/paths/{source_id}-to-{target_id}
**Purpose:** Shortest path between two items.

**Output Schema:**
```json
{
  "source_id": "uuid",
  "source_title": "string",
  "target_id": "uuid",
  "target_title": "string",
  "path_exists": "boolean",
  "distance": "integer",
  "path": [
    {"id": "uuid", "title": "string", "view": "string", "link_type": "string"}
  ],
  "link_types": ["implements", "depends_on", ...]
}
```

**Use Case:** LLM understands how items are connected.

## Implementation Notes

- **Caching:** Resources should be cached (5–15 min TTL) to avoid repeated DB queries
- **Filtering:** Resources accept optional query params (e.g., ?limit=50, ?days=7)
- **Async:** All resources use async services (get_session)
- **Error Handling:** Return 404 if project/item not found; 400 for invalid params

## User Stories

### US-2.1: View Current Project Context
**As an** LLM agent  
**I want to** query the current project metadata and config  
**So that** I can understand what project I'm working in and what values are valid.

**Acceptance Criteria:**
- tracertm://current-project returns project metadata
- tracertm://current-project/config returns valid views, link types, statuses, etc.
- Both resources are cached for performance

### US-2.2: Understand Project Health
**As an** LLM agent  
**I want to** see a summary of project health (item counts, coverage, status distribution)  
**So that** I can assess project state before making changes.

**Acceptance Criteria:**
- tracertm://project/{id}/summary returns high-level metrics
- tracertm://project/{id}/views returns per-view breakdown
- tracertm://project/{id}/activity-log shows recent changes

### US-2.3: Identify Traceability Gaps
**As an** LLM agent  
**I want to** see which items lack traceability to other views  
**So that** I can prioritize what needs to be traced.

**Acceptance Criteria:**
- tracertm://project/{id}/trace-matrix shows coverage
- tracertm://project/{id}/gaps/{from}-to-{to} lists gap items
- tracertm://project/{id}/impact/{item_id} shows change impact

### US-2.4: Detect Circular Dependencies
**As an** LLM agent  
**I want to** see if there are cycles in the dependency graph  
**So that** I can avoid creating circular dependencies.

**Acceptance Criteria:**
- tracertm://project/{id}/cycles returns cycle info
- tracertm://project/{id}/paths/{source}-to-{target} shows shortest path
- Both resources indicate severity/distance

## Feature Requirements

| Feature | Priority | Effort | Notes |
|---------|----------|--------|-------|
| Current project context | High | 1 day | Simple metadata queries |
| Project summary & views | High | 1 day | Aggregation queries |
| Activity log | Medium | 1 day | Event repository queries |
| Trace matrix | High | 2 days | Reuse existing service |
| Gap reports | High | 1 day | Filter matrix results |
| Impact analysis | Medium | 1 day | Reuse existing service |
| Cycle detection | Medium | 1 day | Reuse existing service |
| Path finding | Low | 1 day | Reuse existing service |
| **Total** | | **9 days** | |

## Success Criteria

- [ ] All 10 resources implemented and tested
- [ ] Resources cached with appropriate TTL
- [ ] LLM can query project state without invoking tools
- [ ] All resources return structured JSON with clear schemas
- [ ] Error handling for missing projects/items

