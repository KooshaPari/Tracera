# TraceRTM MCP Server Quickstart

**Version**: 1.0
**Created**: 2026-01-29

Get started with TraceRTM's MCP (Model Context Protocol) server in 5 minutes.

---

## Table of Contents

1. [Installation](#installation)
2. [Starting the Server](#starting-the-server)
3. [Authentication Setup](#authentication-setup)
4. [First API Call](#first-api-call)
5. [Claude Desktop Integration](#claude-desktop-integration)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.10+
- Bun (package manager)
- PostgreSQL (for production)
- SQLite (local development)

### Step 1: Clone and Setup

```bash
# Clone repository
git clone https://github.com/atoms-tech/trace-rtm.git
cd trace-rtm

# Install dependencies
bun install

# Install Python dependencies
pip install -e .

# Or with Poetry
poetry install
```

### Step 2: Database Setup

```bash
# Initialize database
alembic upgrade head

# Or use SQLite for local testing
export TRACERTM_DATABASE_URL=sqlite:///~/.tracertm/tracertm.db
```

---

## Starting the Server

### Option 1: Standalone MCP Server (Development)

```bash
# Start with development auth (no production credentials required)
export TRACERTM_MCP_AUTH_MODE=static
export TRACERTM_MCP_DEV_API_KEYS="dev-key-1,dev-key-2"
export TRACERTM_MCP_DEV_SCOPES="read:*,write:*,analyze:*"

python -m tracertm.mcp.server
```

Expected output:
```
[TRACERTM_MCP][INFO] Starting MCP server on stdio
[TRACERTM_MCP][INFO] Auth mode: static
[TRACERTM_MCP][INFO] Tools registered: 50
[TRACERTM_MCP][INFO] Ready for connections
```

### Option 2: Via CLI Command

```bash
rtm mcp start --dev
```

### Option 3: Via Docker

```bash
docker build -t tracertm-mcp .
docker run -e TRACERTM_MCP_AUTH_MODE=static \
           -e TRACERTM_MCP_DEV_API_KEYS="dev-key-1" \
           tracertm-mcp
```

### Option 4: Claude Desktop Integration

See [Claude Desktop Integration](#claude-desktop-integration) section below.

---

## Authentication Setup

### Development Mode (Quickest Start)

```bash
# No configuration needed - use dev keys
export TRACERTM_MCP_AUTH_MODE=static
export TRACERTM_MCP_DEV_API_KEYS="dev-key-1"

# Start server
python -m tracertm.mcp.server

# In another terminal, make requests
curl -H "Authorization: Bearer dev-key-1" \
     http://localhost:4000/mcp/list_projects
```

### Production Mode (WorkOS AuthKit)

#### Step 1: Get WorkOS Credentials

1. Go to [WorkOS Dashboard](https://dashboard.workos.com)
2. Create organization
3. Get `Client ID` and `API Key`
4. Configure redirect URIs

#### Step 2: Set Environment Variables

```bash
# .env file or shell environment
export TRACERTM_MCP_AUTH_MODE=oauth
export TRACERTM_MCP_AUTHKIT_DOMAIN=https://your-domain.workos.com
export TRACERTM_MCP_BASE_URL=https://mcp.your-domain.com
export TRACERTM_MCP_REQUIRED_SCOPES="read:projects,write:items,analyze:trace"

# Database
export TRACERTM_DATABASE_URL=postgresql://user:pass@localhost/tracertm
```

#### Step 3: Test Connection

```bash
python -m tracertm.mcp.server
# Should start without errors
```

### Generating Tokens (For Testing)

#### WorkOS Device Flow

```bash
# Login via CLI device flow
rtm auth login

# Follow browser prompt to authorize
# Token automatically stored in ~/.tracertm/tokens.json

# Verify login
rtm auth status
```

#### Static Dev Keys

```bash
# Use dev key directly
BEARER_TOKEN="dev-key-1"

# Pass to MCP server (see examples below)
```

---

## First API Call

### Via curl

```bash
# 1. Start server (from section above)
# 2. In another terminal:

curl -H "Authorization: Bearer dev-key-1" \
     -H "Content-Type: application/json" \
     http://localhost:4000/mcp \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/list_projects"
     }'
```

Expected response:
```json
{
  "ok": true,
  "data": [],
  "meta": {
    "count": 0,
    "timestamp": "2026-01-29T10:30:45Z"
  }
}
```

### Via Python

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:4000/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list_projects"
            },
            headers={"Authorization": "Bearer dev-key-1"}
        )
        print(response.json())

asyncio.run(main())
```

### Via JavaScript/TypeScript

```typescript
import fetch from 'node-fetch';

async function main() {
  const response = await fetch('http://localhost:4000/mcp', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer dev-key-1',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/list_projects'
    })
  });

  const data = await response.json();
  console.log(data);
}

main();
```

---

## Claude Desktop Integration

### Step 1: Get API Key

```bash
# Generate or get your WorkOS API key
export WORKOS_API_KEY=sk_live_xxx

# Or use dev key for testing
export WORKOS_API_KEY=dev-key-1
```

### Step 2: Update Claude Desktop Config

#### macOS

```bash
# Edit Claude Desktop config
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Linux

```bash
code ~/.config/Claude/claude_desktop_config.json
```

#### Windows

```bash
code %APPDATA%\Claude\claude_desktop_config.json
```

### Step 3: Add TraceRTM MCP Server

```json
{
  "mcpServers": {
    "tracertm": {
      "command": "python",
      "args": ["-m", "tracertm.mcp.server"],
      "env": {
        "TRACERTM_MCP_AUTH_MODE": "static",
        "TRACERTM_MCP_DEV_API_KEYS": "dev-key-1",
        "TRACERTM_MCP_DEV_SCOPES": "read:*,write:*,analyze:*",
        "TRACERTM_DATABASE_URL": "sqlite://~/.tracertm/tracertm.db"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. Chat with Claude about your TraceRTM projects

### Step 5: Try It Out

```
User: Create a new project called "Safety System"

Claude: I'll create a new project for you using the TraceRTM MCP server.
[Uses create_project tool]
✓ Project created with ID: proj-xxx
```

---

## Common Workflows

### Workflow 1: Create a Project and Add Requirements

```bash
#!/bin/bash

API_KEY="dev-key-1"
BASE_URL="http://localhost:4000/mcp"

# Create project
PROJECT_ID=$(curl -s -H "Authorization: Bearer $API_KEY" -X POST $BASE_URL/create_project \
  -d '{"name": "Acme Safety"}' | jq -r .data.id)

echo "Created project: $PROJECT_ID"

# Create requirement
REQ_ID=$(curl -s -H "Authorization: Bearer $API_KEY" -X POST $BASE_URL/create_item \
  -d "{\"project_id\": \"$PROJECT_ID\", \"name\": \"System Shutdown\", \"item_type\": \"requirement\"}" \
  | jq -r .data.id)

echo "Created requirement: $REQ_ID"

# Create feature
FEAT_ID=$(curl -s -H "Authorization: Bearer $API_KEY" -X POST $BASE_URL/create_item \
  -d "{\"project_id\": \"$PROJECT_ID\", \"name\": \"Emergency Stop\", \"item_type\": \"feature\"}" \
  | jq -r .data.id)

echo "Created feature: $FEAT_ID"

# Link them
curl -s -H "Authorization: Bearer $API_KEY" -X POST $BASE_URL/create_link \
  -d "{\"source_item_id\": \"$REQ_ID\", \"target_item_id\": \"$FEAT_ID\", \"link_type\": \"traces_to\"}"

echo "Created traceability link"
```

### Workflow 2: Gap Analysis

```bash
# Find uncovered requirements
curl -s -H "Authorization: Bearer dev-key-1" \
     http://localhost:4000/mcp/trace_gap_analysis \
     -d '{
       "project_id": "proj-123",
       "source_view": "requirements",
       "target_view": "features"
     }' | jq .
```

### Workflow 3: Import Existing Project

```bash
# Import from YAML
curl -s -H "Authorization: Bearer dev-key-1" \
     http://localhost:4000/mcp/import_project \
     -d '{
       "name": "Imported Project",
       "source_file": "/path/to/project.yaml"
     }' | jq .
```

---

## Troubleshooting

### Issue: "Authorization: Unauthorized"

**Cause**: Missing or invalid token

**Solution**:
```bash
# Check token is valid
curl -H "Authorization: Bearer dev-key-1" \
     http://localhost:4000/mcp/list_projects

# Verify TRACERTM_MCP_DEV_API_KEYS is set
echo $TRACERTM_MCP_DEV_API_KEYS
```

### Issue: "Database connection error"

**Cause**: Database not configured or initialized

**Solution**:
```bash
# For SQLite (development)
export TRACERTM_DATABASE_URL=sqlite://~/.tracertm/tracertm.db

# For PostgreSQL
export TRACERTM_DATABASE_URL=postgresql://user:pass@localhost/tracertm
alembic upgrade head

# Verify connection
python -c "from tracertm.config import database; database.test_connection()"
```

### Issue: "Tool not found" error

**Cause**: MCP server didn't register tools

**Solution**:
```bash
# Check server logs
python -m tracertm.mcp.server 2>&1 | grep -i "tool"

# Verify tools module imports
python -c "from tracertm.mcp.server import mcp; print([t.name for t in mcp._tools.values()])"
```

### Issue: Claude Desktop shows "MCP Server Error"

**Cause**: Config path or Python environment issues

**Solution**:
1. Check `claude_desktop_config.json` syntax with `jq`
2. Verify Python is in PATH: `which python`
3. Check permissions: `ls -la ~/Library/Application\ Support/Claude/`
4. Use absolute paths in config

### Issue: Port 8000 already in use

**Cause**: Another service using port 8000

**Solution**:
```bash
# Use different port
export TRACERTM_MCP_PORT=8001
python -m tracertm.mcp.server

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

---

## Environment Variables Reference

### Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `TRACERTM_MCP_AUTH_MODE` | `oauth` | `oauth`, `static`, or `disabled` |
| `TRACERTM_MCP_AUTHKIT_DOMAIN` | None | WorkOS domain for OAuth |
| `TRACERTM_MCP_BASE_URL` | None | Base URL for audience validation |
| `TRACERTM_MCP_DEV_API_KEYS` | None | Comma-separated dev keys |
| `TRACERTM_MCP_DEV_SCOPES` | None | Default scopes for dev keys |
| `TRACERTM_MCP_REQUIRED_SCOPES` | None | Required scopes for all requests |

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `TRACERTM_MCP_PORT` | `8000` | Server port |
| `TRACERTM_MCP_HOST` | `0.0.0.0` | Server host |
| `TRACERTM_MCP_LOG_LEVEL` | `INFO` | Logging level |

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `TRACERTM_DATABASE_URL` | SQLite | Database connection string |

---

## Next Steps

1. **Explore Tools**: Read [MCP_TOOL_REFERENCE.md](./MCP_TOOL_REFERENCE.md) for complete tool catalog
2. **Learn Auth Flows**: See [AUTH_FLOWS.md](./AUTH_FLOWS.md) for detailed auth patterns
3. **Integration Guide**: Check [MCP_CLI_CONSOLIDATION_SPEC.md](./MCP_CLI_CONSOLIDATION_SPEC.md) for architecture
4. **Run Tests**: `bun run test:mcp` to validate setup

---

## Support

- **Issues**: GitHub Issues (with MCP tag)
- **Docs**: `/docs` directory
- **Examples**: `/examples/mcp/` directory
- **API Reference**: [MCP_TOOL_REFERENCE.md](./MCP_TOOL_REFERENCE.md)
