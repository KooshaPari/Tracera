# dispatch-mcp Setup & Registration

**Date:** 2026-04-27  
**Status:** Integrated locally through Claude Code settings

## Summary

`dispatch-mcp` is a FastMCP server that lets Claude Code sessions delegate
reasoning tasks through the local OmniRoute endpoint at
`http://localhost:20128/v1`.

This unblocks the "5000000000x" ask: launch Claude normally, then use typed MCP
tools such as `dispatch_worker` or `dispatch_main` instead of ad hoc shelling to
model CLIs.

OmniRoute also supports Claude Code as a primary Anthropic-compatible transport.
The dispatch bridge is therefore an optional delegation layer, not the only
supported Claude Code integration.

## Location

```
repos/dispatch-mcp/
├── server.py              (live OmniRoute MCP entry point)
├── src/dispatch_mcp/
│   ├── __init__.py
│   └── server.py          (older dispatch-worker package entry point)
├── pyproject.toml         (FastMCP, pydantic)
├── README.md
└── .gitignore
```

## Installation & Setup

### 1. Verify OmniRoute is running

```bash
curl -s http://localhost:20128/v1/models
```

Expected model IDs include `Worker`, `Main`, `FreeTier`, and `Codeman`.

### 2. Configure direct Claude Code transport when desired

The OmniRoute dashboard exposes a CLI Tools page for one-click Claude Code
configuration. The installed route writes these environment values into
`~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128/v1",
    "ANTHROPIC_AUTH_TOKEN": "your-omniroute-api-key",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "cc/claude-opus-4-6",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "cc/claude-sonnet-4-6",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "cc/claude-haiku-4-5-20251001"
  }
}
```

For temporary shell-only routing:

```bash
cd ~/CodeProjects/Phenotype/repos
ANTHROPIC_BASE_URL=http://localhost:20128/v1 \
ANTHROPIC_AUTH_TOKEN=your-omniroute-api-key \
ANTHROPIC_MODEL=Worker \
claude --permission-mode auto --dangerously-skip-permissions --resume
```

Use `ANTHROPIC_AUTH_TOKEN` for OmniRoute endpoint keys. `ANTHROPIC_API_KEY`
sends an `X-Api-Key` header and is not the dashboard-generated Claude Code path.

### 3. Verify MCP dispatch registration

`~/.claude/settings.json` should contain:

```json
{
  "mcpServers": {
    "dispatch": {
      "command": "python3",
      "args": [
        "/Users/kooshapari/CodeProjects/Phenotype/repos/dispatch-mcp/server.py"
      ],
      "env": {
        "OMNIROUTE_URL": "http://localhost:20128/v1"
      }
    }
  }
}
```

### 4. Launch Claude Code for MCP delegation

Use the normal Claude Code session path:

```bash
cd ~/CodeProjects/Phenotype/repos
claude --permission-mode auto --dangerously-skip-permissions --resume
```

### 5. Test dispatch

Ask Claude to call `dispatch_health`, then route a tiny worker prompt through
`dispatch_worker`.

If direct Claude Code transport fails with a malformed-response error, first
verify the base URL includes `/v1`, `ANTHROPIC_AUTH_TOKEN` is set to a real
OmniRoute endpoint key, and the selected model/combo appears in `/v1/models`.

## MCP Tools Exposed

### `dispatch_worker(prompt: str, cwd: str? = None, max_tokens: int = 4096) -> str`

Route to OmniRoute `Worker`.

### `dispatch_main(prompt: str, cwd: str? = None, max_tokens: int = 4096) -> str`

Route to OmniRoute `Main`.

### `dispatch_codeman(prompt: str, cwd: str? = None, max_tokens: int = 4096) -> str`

Route to OmniRoute `Codeman`.

### `dispatch_freetier(prompt: str, cwd: str? = None, max_tokens: int = 4096) -> str`

Route to OmniRoute `FreeTier`.

### `dispatch_custom(prompt: str, model: str, cwd: str? = None, max_tokens: int = 4096) -> str`

Route to any OmniRoute model ID.

### `dispatch_health() -> dict`

Check whether OmniRoute is reachable.

**Returns:**
```json
{
  "OK: OmniRoute reachable at http://localhost:20128/v1, 200 models exposed."
}
```

## Implementation Details

**Architecture:**
- **Language:** Python 3.11+
- **Framework:** FastMCP (same as cheap-llm-mcp)
- **Wrapper:** Root `server.py`
- **Execution:** HTTP POST to OmniRoute `/chat/completions`

**How it works:**
1. MCP tool call received, such as `dispatch_worker(prompt="...")`.
2. Server posts an OpenAI-compatible chat completion request to OmniRoute.
3. OmniRoute resolves the requested combo or model ID.
4. Server returns assistant text plus the routed model ID.

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
3. **Direct transport smoke:** Add a redacted helper that validates Claude Code
   direct routing without logging endpoint keys
4. **Timeout tuning:** Make 300s timeout configurable via settings.json
5. **Concurrency limits:** Add queuing if dispatch-worker has rate limits

## Troubleshooting

### "OmniRoute unreachable"

```bash
curl -s http://localhost:20128/v1/models
```

Start OmniRoute before launching Claude Code if the endpoint is down.

### MCP server fails to start

Check logs:
```bash
python3 --version
python3 -m py_compile server.py
```

## Related Documents

- **OmniRoute state:** `~/.config/omniroute/`
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
