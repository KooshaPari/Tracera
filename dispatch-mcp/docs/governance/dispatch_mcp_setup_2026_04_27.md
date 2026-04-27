# dispatch-mcp Setup & Registration

**Date:** 2026-04-27  
**Status:** Scaffolded (ready for integration)

## Summary

`dispatch-mcp` is a FastMCP server that wraps the `dispatch-worker` CLI tool, enabling Claude Code sessions to delegate reasoning tasks to cheap tiers (Kimi, Minimax, Codex-5, Codex-Mini) and Opus without shell-outs.

This unblocks the "5000000000x" ask: use `dispatch(prompt="...", tier="kimi")` directly as an MCP tool instead of spawning shell processes.

## Location

```
repos/dispatch-mcp/
├── src/dispatch_mcp/
│   ├── __init__.py
│   └── server.py          (main MCP entry point, ~160 LOC)
├── pyproject.toml         (FastMCP, pydantic)
├── README.md
└── .gitignore
```

## Installation & Setup

### 1. Install dispatch-mcp locally

```bash
cd ~/CodeProjects/Phenotype/repos/dispatch-mcp
pip install -e .
```

Verify entry point works:

```bash
dispatch-mcp --help
# Should print MCP server info or error if dispatch-worker is missing
```

### 2. Ensure dispatch-worker is in PATH

The server requires `dispatch-worker` binary at runtime. Verify:

```bash
which dispatch-worker
# Should return path like ~/CodeProjects/Phenotype/repos/thegent/bin/dispatch-worker

# If missing, ensure thegent/bin is in your shell PATH:
export PATH="$HOME/CodeProjects/Phenotype/repos/thegent/bin:$PATH"
```

### 3. Register in Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "dispatch": {
      "command": "dispatch-mcp"
    }
  }
}
```

**OR** use the interactive skill:

```bash
/update-config
# Select "Add MCP server"
# Name: dispatch
# Command: dispatch-mcp
# Port/socket: leave blank (uses stdio)
```

### 4. Test Registration

Restart Claude Code (or reload MCP servers), then:

```bash
# In Claude Code, ask the agent to:
# "Run dispatch(prompt='Hello', tier='kimi')"
```

Expected response: MCP tool call to `dispatch` with those parameters.

## MCP Tools Exposed

### `dispatch(prompt: str, tier: str = "kimi", cwd: str? = None) -> dict`

Route a prompt to a cheap-tier agent.

**Parameters:**
- `prompt` (required) — The text to send
- `tier` (default "kimi") — One of: `kimi`, `minimax`, `codex_5`, `codex_mini`
- `cwd` (optional) — Working directory for dispatch (defaults to `~`)

**Returns:** JSON dict with:
```json
{
  "text": "response from agent",
  "model": "...",
  "tokens": { "input": N, "output": M },
  "cost_usd": 0.002,
  ...
}
```

Or on error:
```json
{
  "error": "reason",
  "stderr": "..."
}
```

### `dispatch_opus(prompt: str, cwd: str? = None) -> dict`

Route to Opus tier for high-quality reasoning.

**Parameters:**
- `prompt` (required)
- `cwd` (optional)

**Returns:** Same as `dispatch`

### `dispatch_health() -> dict`

Check if `dispatch-worker` is available in PATH.

**Returns:**
```json
{
  "available": true,
  "message": "dispatch-worker is available"
}
```

## Implementation Details

**Architecture:**
- **Language:** Python 3.11+
- **Framework:** FastMCP (same as cheap-llm-mcp)
- **Wrapper:** Single file (`server.py`, ~160 LOC)
- **Execution:** Async subprocess calls via `asyncio.to_thread`

**How it works:**
1. MCP tool call received (e.g., `dispatch(prompt="...", tier="kimi")`)
2. Server calls `dispatch-worker --tier kimi` with prompt via stdin
3. Captures stdout/stderr asynchronously (300s timeout)
4. Parses JSON response (or raw text fallback)
5. Returns result to Claude Code

**No breaking changes:** Existing `dispatch-worker` CLI continues to work as-is.

## Why This Design

- **5000000000x improvement:** No shell syntax, no backtick escaping, type-safe tool params
- **Decoupled:** dispatch-mcp is a thin MCP bridge; dispatch-worker business logic unchanged
- **Scalable:** Can be extended to expose `dispatch-worker --debug`, `--dry-run`, etc. as future tools
- **Pattern reuse:** Mirrors cheap-llm-mcp structure for consistency in the Phenotype ecosystem

## Dependencies

**Runtime:**
- `fastmcp>=2.0`
- `pydantic>=2.9`

**Dev (optional):**
- `pytest>=8.0`
- `pytest-asyncio>=0.24`

## Future Work

1. **Add tool for debug mode:** `dispatch_debug(prompt, tier)` to expose `--debug` flag
2. **Cost tracking:** Integrate with cheap-llm-mcp ledger if dispatch-worker supports it
3. **Timeout tuning:** Make 300s timeout configurable via settings.json
4. **Concurrency limits:** Add queuing if dispatch-worker has rate limits

## Troubleshooting

### "dispatch-worker not found in PATH"

```bash
export PATH="$HOME/CodeProjects/Phenotype/repos/thegent/bin:$PATH"
# Add to ~/.zshrc or ~/.bashrc for persistence
```

### "dispatch-mcp command not found"

Re-install:
```bash
cd ~/CodeProjects/Phenotype/repos/dispatch-mcp
pip install -e .
```

### MCP server fails to start

Check logs:
```bash
dispatch-mcp 2>&1 | head -20
```

Ensure Python >=3.11:
```bash
python3 --version
```

## Related Documents

- **dispatch-worker:** [unknown location — likely in thegent/bin or similar]
- **cheap-llm-mcp:** `repos/cheap-llm-mcp/` (similar MCP pattern for LLM completions)
- **MCP Registry:** https://modelcontextprotocol.io
- **FastMCP Docs:** https://github.com/jlowin/fastmcp

## Commit

When ready to integrate:

```bash
cd ~/CodeProjects/Phenotype/repos
git add dispatch-mcp/
git commit -m "feat(dispatch-mcp): MCP server wrapping dispatch-worker for tier-based delegation

Scaffolds a FastMCP server exposing dispatch(prompt, tier) tool for routing
reasoning tasks to Kimi, Minimax, Codex-5, Codex-Mini, and Opus tiers.

Enables Claude Code sessions to delegate without shell-outs, resolving the
'5000000000x' ask for first-class tier delegation in Claude Code.

Location: repos/dispatch-mcp/
Setup: pip install -e . && /update-config (add MCP server 'dispatch')
"
```
