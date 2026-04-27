# dispatch-mcp

MCP bridge that lets Claude Code delegate sub-work through local OmniRoute.

## Current Local Path

Claude Code has two OmniRoute paths on this machine:

1. Primary Claude Code transport through OmniRoute's Anthropic-compatible
   gateway.
2. The `dispatch` MCP bridge for explicit side-task delegation from a normal
   Claude Code session.

OmniRoute itself documents Claude Code support through the dashboard CLI Tools
page. The installed OmniRoute app writes this shape into
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

Use `ANTHROPIC_AUTH_TOKEN`, not `ANTHROPIC_API_KEY`, for this path. Claude Code
prefixes `ANTHROPIC_AUTH_TOKEN` with `Bearer` for the `Authorization` header.

For one-off launches without changing global settings, export the same values
in the shell:

```bash
cd ~/CodeProjects/Phenotype/repos
ANTHROPIC_BASE_URL=http://localhost:20128/v1 \
ANTHROPIC_AUTH_TOKEN=your-omniroute-api-key \
ANTHROPIC_MODEL=Worker \
claude --permission-mode auto --dangerously-skip-permissions --resume
```

The MCP delegation path is also configured from `~/.claude/settings.json`:

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

That means the simple MCP-backed launch path is also just normal Claude Code:

```bash
cd ~/CodeProjects/Phenotype/repos
claude --permission-mode auto --dangerously-skip-permissions --resume
```

Inside Claude, use the `dispatch` MCP tools for OmniRoute-backed worker calls.
This is useful when the primary session should stay on a Claude subscription or
when you want typed, explicit fan-out to OmniRoute combos.

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

OmniRoute supports Claude Code as a first-class CLI integration. Prefer the
dashboard one-click setup at `http://localhost:20128/dashboard/cli-tools` so the
real API key is written safely and the base URL/model env vars are consistent.

If a direct launch returns a malformed-response error, check these first:

- `ANTHROPIC_BASE_URL` includes `/v1`
- `ANTHROPIC_AUTH_TOKEN` is set to an OmniRoute endpoint API key
- `ANTHROPIC_MODEL` or `--model` names an exposed OmniRoute model/combo
- OmniRoute is running and `curl -s http://localhost:20128/v1/models` works

## Development

```bash
python3 -m py_compile server.py src/dispatch_mcp/server.py
```

## Related

- `~/.config/omniroute/` — local OmniRoute state and call logs
- `cheap-llm-mcp` — MCP server for cheap model completions
- MCP Registry: [model-context-protocol.io](https://model-context-protocol.io)
