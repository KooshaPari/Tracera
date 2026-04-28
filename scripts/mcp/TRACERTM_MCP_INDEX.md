# TraceRTM MCP Server – Documentation Index

## Quick Links

### Getting Started
- **[TRACERTM_MCP_IMPLEMENTATION_GUIDE.md](TRACERTM_MCP_IMPLEMENTATION_GUIDE.md)** – How to run the server, architecture overview, next phases
- **[PHASE_1_COMPLETION_SUMMARY.md](PHASE_1_COMPLETION_SUMMARY.md)** – What was delivered, tool inventory, key decisions

### Reference
- **[TRACERTM_MCP_TOOL_REFERENCE.md](TRACERTM_MCP_TOOL_REFERENCE.md)** – Complete tool signatures and descriptions
- **[TRACERTM_MCP_TOOLS_SUMMARY.md](TRACERTM_MCP_TOOLS_SUMMARY.md)** – Tools by category with quick reference

### Implementation
- **`src/tracertm/mcp/server.py`** – Unified MCP server (FastMCP) with registered tools/resources
- **[TRACE_RTM_MCP_DESIGN.md](TRACE_RTM_MCP_DESIGN.md)** – Original design document (phases 1–4)

## Tool Categories (21 Total)

### Projects (4)
- create_project
- list_projects
- select_project
- snapshot_project

### Items (7)
- create_item
- get_item
- update_item
- delete_item
- query_items
- summarize_view
- bulk_update_items

### Links (3)
- create_link
- list_links
- show_links

### Traceability (5)
- find_gaps
- get_trace_matrix
- analyze_impact
- analyze_reverse_impact
- project_health

### Graph (2)
- detect_cycles
- shortest_path

## Architecture

```
MCP Client (Claude Desktop / droid)
    ↓
tracertm-mcp (FastMCP 3.0.0b1)
    ├─ Sync tools (CRUD) → DatabaseConnection → SQLAlchemy
    └─ Async tools (Analysis) → get_session → Services
        ├─ TraceabilityService
        ├─ ImpactAnalysisService
        ├─ CycleDetectionService
        ├─ ShortestPathService
        └─ PerformanceService
```

## Status

✅ **Phase 1 (Tools):** Complete – 21 tools, all tested  
⏳ **Phase 2 (Resources):** Planned  
⏳ **Phase 3 (Prompts):** Planned  
⏳ **Phase 4 (Production):** Planned

## Running

```bash
python -m tracertm.mcp
```

Then configure in your MCP host (Claude Desktop, droid, etc.) to point to this server.

## Testing

```bash
pytest tests/unit/test_config_manager.py tests/unit/test_database_models.py -v
```

All 12 core tests pass. MCP-specific tests (Phase 2).

## Questions?

See the implementation guide or tool reference for details on any specific tool.
