---
description: Start and sanity-check TraceRTM MCP server modes.
---

# tracertm-mcp

Use this when configuring or validating MCP access for agents.

## Commands

```pwsh
cd E:/Dev/Tracera
tracertm-mcp            # stdio mode
# or
rtm mcp start --dev
```

HTTP mode requires gateway/API running:

```pwsh
rtm mcp tools   # after server is running
```

## Checks

- Confirm MCP config references only project-appropriate server names (`tracertm-stdio`, `tracertm-http`) from `.claude/mcp-servers.json`.
- Ensure auth mode and tokens are only injected via environment variables (`.env`) and not committed.
