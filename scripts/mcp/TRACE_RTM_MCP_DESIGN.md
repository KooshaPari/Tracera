# TraceRTM MCP Server - Design Document

## 1. Executive Summary

This document defines the **TraceRTM MCP Server**, an MCP-native interface for TraceRTM, the agent-native requirements traceability and multi-view project management system described in the PRD, architecture, and UX docs.

The goal is to expose TraceRTM's project model (projects, items, views, links, traceability, progress) as a **typed, toolable API** to LLM-based agents and UIs via the **Model Context Protocol (MCP)** using **FastMCP 3.0.0b1**.

The TraceRTM MCP Server becomes the primary way agents:
- Discover and select projects
- Inspect, create, and update items across views (FEATURE, CODE, TEST, etc.)
- Create and traverse links for end-to-end traceability
- Compute project health, coverage, and risk
- Run higher-level workflows for planning and execution

BMM and other workflow systems are treated as **clients** of this MCP server, not the core identity.

---

## 2. System Context & Roles

**Server:** `tracertm-mcp`
- Implemented with FastMCP 3.0.0b1
- Runs alongside the `tracertm` Python package and database
- Exposes tools/resources/prompts

**Clients:**
- LLM hosts (Claude Desktop, droid/auggie, custom MCP clients)
- Higher-level orchestrators (e.g., BMM workflows) that call TraceRTM MCP tools

**Underlying System:**
- TraceRTM core engine (Python 3.12+, PostgreSQL/SQLite)
- CLI (`rtm`) and Python API (`from tracertm import TraceRTM`)

---

## 3. Server Surface: Tools (Active Operations)

All tools are exposed via `@mcp.tool` with Pydantic-validated input/output schemas and structured JSON results.

### 3.1 Project Tools

- `create_project`
  - Input: `{ name: str, description?: str }`
  - Output: `{ project_id: str, name: str, description: str }`

- `list_projects`
  - Input: `{}`
  - Output: `{ projects: [{ id: str, name: str, status: str }] }`

- `select_project`
  - Input: `{ project_id: str }`
  - Effect: Updates server-side "current project" context for this client/session.
  - Output: `{ project_id: str, name: str }`

- `snapshot_project`
  - Input: `{ project_id: str, label: str }`
  - Output: `{ snapshot_id: str, created_at: str }`

### 3.2 Item & View Tools

- `create_item`
  - Input: `{ project_id: str, title: str, view: str, item_type: str, status?: str, metadata?: dict }`
  - Output: `{ item_id: str, project_id: str, view: str, item_type: str, status: str }`

- `update_item_status`
  - Input: `{ project_id: str, item_id: str, status: str }`
  - Output: `{ item_id: str, status: str }`

- `query_items`
  - Input: `{ project_id: str, filters?: { view?: str, status?: str, tags?: [str], text?: str } }`
  - Output: `{ items: [... minimal item summaries ...] }`

- `summarize_view`
  - Input: `{ project_id: str, view: str }`
  - Output: `{ view: str, counts_by_status: dict, key_items: [..], gaps: [..] }`

### 3.3 Links & Traceability Tools

- `create_link`
  - Input: `{ project_id: str, source_id: str, target_id: str, link_type: str }`
  - Output: `{ link_id: str }`

- `get_trace_chain`
  - Input: `{ project_id: str, item_id: str, direction: "forward"|"backward"|"both", max_depth?: int }`
  - Output: `{ nodes: [...], edges: [...] }`

- `find_gaps`
  - Input: `{ project_id: str, from_view: str, to_view: str }`
  - Output: `{ missing_links: [{ from_id: str, reason: str }] }`

### 3.4 Project Health & Planning Tools

- `project_health`
  - Input: `{ project_id: str }`
  - Output: `{ status: str, coverage_metrics: dict, risks: [str], suggestions: [str] }`

- `plan_release`
  - Input: `{ project_id: str, scope_filter?: { views?: [str], statuses?: [str] } }`
  - Output: `{ plan_id: str, items: [...], dependencies: [...], summary: str }`

---

## 4. Server Surface: Resources (Read-Only Context)

Resources expose frequently accessed, read-only views optimized for agents.

- `tracertm://current-project`
  - Returns current project metadata and high-level stats.

- `tracertm://project/{id}/summary`
  - Aggregate counts by view/status, last activity, and open risks.

- `tracertm://project/{id}/trace-matrix`
  - Lightweight structured representation of requirement→design→code→test mapping.

- `tracertm://project/{id}/gaps/{from_view}-to-{to_view}`
  - Precomputed gap reports for key view pairs (e.g., REQUIREMENT→TEST).

- `tracertm://project/{id}/activity-log`
  - Recent changes (items created/updated, links created, snapshots).

All resources are suitable for FastMCP 3.0.0b1 response caching.

---

## 5. Server Surface: Prompts (Canonical Conversations)

Prompts are reusable prompt templates that use TraceRTM data to drive higher-level reasoning.

Examples:

- `tracertm.plan_iteration`
  - Input: `{ project_id: str, iteration_length_days?: int }`
  - Uses project summary + gaps to propose an iteration plan.

- `tracertm.groom_backlog`
  - Helps clean up and prioritize open items in FEATURE/REQUIREMENT views.

- `tracertm.analyze_risk`
  - Generates a human-readable and structured risk report based on trace matrix and gaps.

- `tracertm.implement_feature_with_traceability`
  - For a given feature item, guides the creation of design/code/test items and links.

---

## 6. Data, State, and Storage

- Primary truth remains in TraceRTM's database (projects, items, links, etc.).
- MCP server uses FastMCP 3.0.0b1 storage layer for:
  - Caching expensive derived views (trace matrix, gap reports)
  - Storing MCP-level metadata (plans, snapshots, per-client state)
  - Securely storing any access tokens (for future remote deployments)

---

## 7. Security & Auth

Initial local usage:
- Run `tracertm-mcp` locally via stdio, no auth, trusted single-user environment.

Future remote/multi-tenant:
- Use FastMCP 3.0.0b1 OAuth proxy for authentication.
- Restrict tool surface by tags for untrusted clients.

---

## 8. Implementation Phases

1. **Phase 1: Core MCP Server Skeleton**
   - Use unified server in `src/tracertm/mcp/server.py` (FastMCP 3.x)
   - Implement minimal tools: `list_projects`, `select_project`, `create_item`, `create_link`

2. **Phase 2: Traceability & Health**
   - Implement `get_trace_chain`, `find_gaps`, `project_health`
   - Add core resources: `current-project`, `summary`, `trace-matrix`

3. **Phase 3: Prompts & Workflows**
   - Add prompts for planning, backlog grooming, risk analysis
   - Integrate with BMM or other orchestrators as MCP clients

4. **Phase 4: Production Features**
   - Enable caching, storage-backed state, and optional OAuth
   - Add observability (logging, metrics middleware)
