# dispatch-mcp

MCP bridge that lets Claude Code delegate sub-work through local OmniRoute.

## Current Local Path

Claude Code is already configured to start this MCP server from `~/.claude/settings.json`:

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

That means the simple launch path is just normal Claude Code:

```bash
cd ~/CodeProjects/Phenotype/repos
claude --permission-mode auto --dangerously-skip-permissions --resume
```

Inside Claude, use the `dispatch` MCP tools for OmniRoute-backed worker calls.
This keeps Claude Code's own primary Anthropic transport unchanged while
delegating side tasks through OmniRoute.

## OmniRoute Health

Check that OmniRoute is listening:

```bash
curl -s http://localhost:20128/v1/models
```

Expected exposed combo models include:

- `Worker`
- `Main`
- `FreeTier`
- `Codeman`

If the endpoint is down, start OmniRoute before launching Claude Code.

## Tools

The live root server exposes tier and direct-model tools:

| Tool | Purpose |
| --- | --- |
| `dispatch_worker` | Cheap volume worker tier through OmniRoute `Worker` |
| `dispatch_main` | Balanced tier through OmniRoute `Main` |
| `dispatch_codeman` | Code-oriented tier through OmniRoute `Codeman` |
| `dispatch_freetier` | Free-model-only tier through OmniRoute `FreeTier` |
| `dispatch_custom` | Direct OmniRoute model ID |
| `dispatch_health` | OmniRoute reachability check |

The installable package entry point under `src/dispatch_mcp/server.py` is the
older `dispatch-worker` bridge. Prefer the live root `server.py` path above for
the current OmniRoute setup.

## Direct Claude Transport

Do not rely on this as the default path right now:

```bash
ANTHROPIC_BASE_URL=http://localhost:20128 ANTHROPIC_API_KEY=local claude --model Worker
```

Claude Code reaches the local service, but current responses are OpenAI-style
and Claude reports a malformed Anthropic response. Use the MCP dispatch bridge
until OmniRoute has a Claude/Anthropic-compatible transport mode for primary
Claude Code sessions.

## Development

```bash
python3 -m py_compile server.py src/dispatch_mcp/server.py
```

## Related

- `~/.config/omniroute/` — local OmniRoute state and call logs
- `cheap-llm-mcp` — MCP server for cheap model completions
- MCP Registry: [model-context-protocol.io](https://model-context-protocol.io)
