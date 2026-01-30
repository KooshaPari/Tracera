# TraceRTM MCP Auth

## Environment variables

Required for AuthKit verification:
- `TRACERTM_MCP_AUTHKIT_DOMAIN` (or `WORKOS_AUTHKIT_DOMAIN`)
- `TRACERTM_MCP_BASE_URL` (public MCP server URL)

Optional:
- `TRACERTM_MCP_REQUIRED_SCOPES` (space or comma separated)
- `TRACERTM_MCP_DEV_API_KEYS` (comma-separated dev tokens)
- `TRACERTM_MCP_DEV_SCOPES` (scopes for dev tokens)
- `TRACERTM_MCP_AUTH_MODE=disabled` (turn off auth)

## CLI device login

```
rtm auth login --authkit-domain https://your-app.authkit.app
```

Tokens are stored in `~/.tracertm/config.yaml` as `api_token`.
