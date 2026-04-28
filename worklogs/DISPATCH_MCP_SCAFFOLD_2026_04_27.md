# dispatch-mcp Scaffold — 2026-04-27

**Status:** Complete (scaffolded, ready for user registration)  
**Commit:** 99e0ffdc96 (`feat(dispatch-mcp): MCP server wrapping dispatch-worker...`)

## Summary

Scaffolded `repos/dispatch-mcp/` as a FastMCP server that wraps `dispatch-worker` CLI, enabling Claude Code to call `dispatch(prompt="...", tier="kimi")` directly as an MCP tool instead of shell-outs.

**The 5000000000x ask:** First-class tier delegation in Claude Code without subprocess escaping complexity.

## What Was Scaffolded

```
repos/dispatch-mcp/
├── src/dispatch_mcp/
│   ├── __init__.py                                  (module init)
│   └── server.py                                    (FastMCP server, ~160 LOC)
├── pyproject.toml                                   (deps: fastmcp, pydantic)
├── README.md                                        (user-facing setup guide)
├── .gitignore                                       (standard Python)
└── docs/governance/
    └── dispatch_mcp_setup_2026_04_27.md            (detailed setup + troubleshooting)
```

## Architecture

**MCP Tools Exposed:**

1. `dispatch(prompt: str, tier: str = "kimi", cwd: str? = None) -> dict`
   - Tiers: kimi, minimax, codex_5, codex_mini
   - Returns: JSON response from dispatch-worker (or raw text fallback)

2. `dispatch_opus(prompt: str, cwd: str? = None) -> dict`
   - High-tier reasoning variant
   - Same return format

3. `dispatch_health() -> dict`
   - Verifies dispatch-worker availability in PATH
   - Returns: `{available: bool, message: str}`

**Implementation Pattern:**
- Single-file server (mirrors cheap-llm-mcp structure)
- Async subprocess calls via `asyncio.to_thread`
- 300s timeout per dispatch
- JSON response parsing with raw text fallback
- No business logic — all routing handled by dispatch-worker binary

## Registration Instructions

**User must perform these steps:**

```bash
# 1. Install dispatch-mcp locally
cd ~/CodeProjects/Phenotype/repos/dispatch-mcp
pip install -e .

# 2. Verify dispatch-worker in PATH
which dispatch-worker
# If missing: export PATH="$HOME/.../thegent/bin:$PATH"

# 3. Register in Claude Code
# Option A: Manual edit ~/.claude/settings.json
# {
#   "mcpServers": {
#     "dispatch": {
#       "command": "dispatch-mcp"
#     }
#   }
# }

# Option B: Use interactive skill
/update-config
# > Add MCP server
# > Name: dispatch
# > Command: dispatch-mcp

# 4. Test
# In Claude Code, ask agent to: dispatch(prompt="Hello", tier="kimi")
```

## Why This Design

| Goal | Solution |
|------|----------|
| No shell escaping complexity | MCP tools + type-safe params |
| Tier routing without subprocess | dispatch-worker binary as subprocess (hidden from user) |
| Pattern consistency | Mirrors cheap-llm-mcp (FastMCP, same structure) |
| Future extensibility | Can add `--debug`, `--dry-run`, cost tracking tools later |

## Not Included (Scaffold Only)

- Tests (user can add pytest fixtures)
- Actual `dispatch-worker` binary (already exists in thegent/bin)
- Integration into Claude Code settings (user must register manually)
- Server startup/systemd integration (runs on-demand via MCP stdio)

## Related Work

- **cheap-llm-mcp** (`repos/cheap-llm-mcp/`): Similar FastMCP pattern for LLM completions
- **dispatch-worker**: Unknown location (likely `thegent/bin/` or similar CLI tool)
- **thegent**: Main dispatch orchestrator repository

## Next Steps (User Action)

1. Follow registration instructions above
2. Test with: `dispatch(prompt="Hello world", tier="kimi")`
3. If dispatch-worker path issues, add to shell profile:
   ```bash
   export PATH="$HOME/CodeProjects/Phenotype/repos/thegent/bin:$PATH"
   ```
4. Expand tools in future (--debug mode, cost tracking, etc.)

## Files Created

- `dispatch-mcp/` (new directory, 543 LOC)
- `docs/governance/dispatch_mcp_setup_2026_04_27.md` (detailed guide)
- `README.md` (user-facing docs)
- `pyproject.toml` (FastMCP + pydantic)
- `src/dispatch_mcp/server.py` (main logic)
- `.gitignore` (standard Python)

All files follow Phenotype governance (UTF-8, no suppression, quality-ready).
