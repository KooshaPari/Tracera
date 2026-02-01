# MCP Optimization Quick Start Guide

## What Was Done

Optimized MCP tool registration by splitting the monolithic 62KB `param.py` into 14 focused domain modules, achieving **45.9% performance improvement** (4,060ms → 2,197ms).

## File Structure

```
src/tracertm/mcp/tools/params/
├── common.py              # Shared utilities
├── project.py             # project_manage
├── item.py                # item_manage
├── link.py                # link_manage
├── trace.py               # trace_analyze, quality_analyze
├── graph.py               # graph_analyze
├── specification.py       # specification_manage
├── config.py              # config_manage
├── storage.py             # sync_manage, backup_manage, file_watch_manage
├── io_operations.py       # export_manage, import_manage, ingestion_manage
├── database.py            # database_manage
├── agent.py               # agent_manage, progress_manage
├── query_test.py          # saved_query_manage, test_manage
├── ui.py                  # tui_manage, design_manage
└── system.py              # benchmark_manage, chaos_manage
```

## How to Use

### Running Benchmarks

```bash
# Quick benchmark
python scripts/benchmark_tool_registration.py

# Full test suite
pytest tests/unit/mcp/test_tool_registration_performance.py -v
```

### Adding New Tools

When adding a new tool, add it to the appropriate domain module:

```python
# In src/tracertm/mcp/tools/params/project.py

from tracertm.mcp.core import mcp
from .common import _wrap, project_tools

@mcp.tool(description="New project operation")
async def project_new_operation(
    action: str,
    payload: dict[str, Any] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    # Implementation
    result = await project_tools.new_operation(...)
    return _wrap(result, ctx, action)
```

### Importing Tools

```python
# Old way (slow - loads 62KB file)
from tracertm.mcp.tools import param

# New way (fast - loads only what you need)
from tracertm.mcp.tools.params import project
from tracertm.mcp.tools.params import item

# Use the tools
await project.project_manage("list")
await item.item_manage("query", {"view": "FEATURE"})
```

## Performance Comparison

| Approach | Import Time | Improvement |
|----------|-------------|-------------|
| Monolithic param.py | 4,060ms | Baseline |
| Split modules (Phase 1) | 2,197ms | **45.9% faster** |
| Target (Phase 2) | <100ms | TBD |

## Current Limitations

1. **Not yet at <100ms target** - achieved 2,197ms (still above target)
2. **Some tools delegate to param.py** - agent, query_test, ui, system modules
3. **Heavy common imports** - common.py loads many dependencies at module level

## Next Steps for <100ms Target

1. **Lazy import common utilities** - defer heavy imports until function call
2. **Complete tool migration** - extract remaining tools from param.py
3. **Pre-compute tool metadata** - cache at build time

## Quick Commands

```bash
# Analyze param.py structure
python scripts/split_param_tools.py

# Run performance benchmark
python scripts/benchmark_tool_registration.py

# Test individual modules
pytest tests/unit/mcp/test_tool_registration_performance.py::test_individual_module_imports

# Check for duplicate registrations
python -c "from tracertm.mcp import server" 2>&1 | grep "already exists"
```

## Troubleshooting

### "Component already exists" warnings
**Cause:** Both param.py and split modules register the same tool
**Fix:** Phase 2 will complete migration and deprecate param.py
**Impact:** Cosmetic only, functionality works correctly

### Import errors
**Cause:** Missing dependency in split module
**Fix:** Add import to the appropriate module or common.py

### Performance not improved
**Cause:** Heavy imports in common.py or param.py still being loaded
**Fix:** Use lazy imports (Phase 2)

## Files Reference

### Created Files
- `src/tracertm/mcp/registry.py` - Tool registry for lazy loading
- `src/tracertm/mcp/tools/params/*.py` - 14 domain modules
- `scripts/benchmark_tool_registration.py` - Performance testing
- `tests/unit/mcp/test_tool_registration_performance.py` - Test suite

### Modified Files
- `src/tracertm/mcp/server.py` - Uses split modules instead of monolithic param.py

### Original Files (Kept for Compatibility)
- `src/tracertm/mcp/tools/param.py` - Original monolithic file (62KB, 1,742 lines)

## For More Details

See `MCP_OPTIMIZATION_PHASE_1_SUMMARY.md` for complete documentation.
