# dispatch-mcp

MCP server wrapping `dispatch-worker` for tier-based agent delegation in Claude Code.

## Overview

`dispatch-mcp` exposes MCP tools that route prompts to agent tiers without shell-outs:

- `dispatch(prompt, tier="kimi")` — Route to cheap tiers (Kimi, Minimax, Codex-5, Codex-Mini)
- `dispatch_opus(prompt)` — Route to high-tier Opus for complex reasoning
- `dispatch_health()` — Verify `dispatch-worker` availability

## Installation

1. **Install dependencies:**
   ```bash
   cd ~/CodeProjects/Phenotype/repos/dispatch-mcp
   pip install -e .
   ```

2. **Verify dispatch-worker is accessible:**
   ```bash
   dispatch-worker --help
   # or verify path:
   which dispatch-worker
   ```

## Registration in Claude Code

Add to `~/.claude/settings.json` (or project `.claude/settings.json`):

```json
{
  "mcpServers": {
    "dispatch": {
      "command": "dispatch-mcp"
    }
  }
}
```

Or use the update-config skill:

```bash
/update-config

# Then select:
# - "Add MCP server"
# - Name: dispatch
# - Command: dispatch-mcp
```

## Usage in Claude Code

Once registered, use the `dispatch` tool directly:

```
Summarize the following code using dispatch(prompt="...", tier="kimi")
```

Tools available:

| Tool | Params | Purpose |
|------|--------|---------|
| `dispatch` | `prompt`, `tier="kimi"` (or minimax/codex_5/codex_mini), `cwd?` | Route to cheap tier |
| `dispatch_opus` | `prompt`, `cwd?` | Route to Opus (high-quality reasoning) |
| `dispatch_health` | none | Verify dispatch-worker is available |

## Environment

- **Requires:** `dispatch-worker` binary in PATH
- **Python:** ≥3.11
- **FastMCP:** ≥2.0

## Development

```bash
# Run tests
pytest

# Format code
ruff format src/

# Lint
ruff check src/
```

## Architecture

The server is a single-file FastMCP wrapper (~160 LOC) that:

1. Receives MCP tool calls with `prompt` and `tier` parameters
2. Shells out to `dispatch-worker --tier <tier>` via `subprocess.run` in a thread
3. Parses JSON response (or raw text fallback)
4. Returns result to Claude Code

All actual model routing and tier logic lives in `dispatch-worker` binary; this server is just the MCP bridge.

## Related

- `cheap-llm-mcp` — Similar MCP server for Minimax/Kimi/Fireworks completions
- `dispatch-worker` — The underlying CLI tool being wrapped (install from `thegent/bin/`)
- MCP Registry: [model-context-protocol.io](https://modelcontextprotocol.io)
