# TraceRTM MCP Server

The TraceRTM MCP (Model Context Protocol) Server enables AI assistants like Claude to interact with your traceability data through a standardized protocol.

## Quick Start

### Installation

```bash
# Install with MCP support
pip install tracertm

# Or install in development mode
pip install -e ".[dev]"
```

### Running the Server

```bash
# Using the CLI entry point
tracertm-mcp

# Or using Python module
python -m tracertm.mcp

# Or via the rtm CLI
rtm mcp start
```

## Claude Desktop Integration

### Automatic Configuration

Get the configuration for Claude Desktop:

```bash
rtm mcp config
```

This will display the JSON configuration you need to add to your Claude Desktop config file.

### Manual Configuration

Add the following to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tracertm": {
      "command": "tracertm-mcp",
      "env": {
        "TRACERTM_MCP_AUTH_MODE": "static",
        "TRACERTM_MCP_DEV_API_KEYS": "dev-key-1"
      }
    }
  }
}
```

Alternatively, use Python module invocation:

```json
{
  "mcpServers": {
    "tracertm": {
      "command": "python",
      "args": ["-m", "tracertm.mcp"],
      "env": {
        "TRACERTM_MCP_AUTH_MODE": "static",
        "TRACERTM_MCP_DEV_API_KEYS": "dev-key-1"
      }
    }
  }
}
```

After adding the configuration, restart Claude Desktop.

## Available Tools

### Core Operations

| Tool | Description |
|------|-------------|
| `project_manage` | Create, list, select, snapshot projects |
| `item_manage` | CRUD operations for items |
| `link_manage` | Create and query traceability links |

### Analysis Tools

| Tool | Description |
|------|-------------|
| `trace_analyze` | Gap analysis, impact analysis, traceability matrix |
| `graph_analyze` | Cycle detection, shortest path |
| `quality_analyze` | Requirement quality analysis |
| `spec_manage` | ADRs, contracts, features, scenarios |

### Streaming & Pagination

| Tool | Description |
|------|-------------|
| `stream_impact_analysis` | Impact analysis with progress updates |
| `get_matrix_page` | Paginated traceability matrix |
| `get_items_page` | Paginated items list |
| `get_links_page` | Paginated links list |

### Configuration & System

| Tool | Description |
|------|-------------|
| `config_manage` | Configuration operations |
| `sync_manage` | Offline sync operations |
| `db_manage` | Database operations |
| `backup_manage` | Backup and restore |

For a complete tool reference, see [MCP Tool Reference](../scripts/mcp/TRACERTM_MCP_TOOL_REFERENCE.md).

## Available Resources

Resources provide read-only access to data:

| Resource | Description |
|----------|-------------|
| `tracertm://projects` | List all projects |
| `tracertm://project/{id}` | Project details with counts |
| `tracertm://items/{project_id}` | Items in project (max 100) |
| `tracertm://links/{project_id}` | Links in project (max 100) |
| `tracertm://matrix/{project_id}` | Traceability matrix summary |
| `tracertm://health/{project_id}` | Project health metrics |
| `tracertm://views/traceability/{project_id}` | Traceability tree view |
| `tracertm://views/impact/{project_id}` | High-impact items view |
| `tracertm://views/coverage/{project_id}` | Coverage analysis view |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRACERTM_MCP_AUTH_MODE` | Authentication mode (`disabled`, `static`, `jwt`) | `disabled` |
| `TRACERTM_MCP_DEV_API_KEYS` | Comma-separated API keys for static auth | - |
| `TRACERTM_MCP_VERBOSE_LOGGING` | Enable verbose logging | `false` |
| `TRACERTM_MCP_RATE_LIMIT_PER_MIN` | Rate limit per minute | `60` |
| `TRACERTM_MCP_RATE_LIMIT_PER_HOUR` | Rate limit per hour | `1000` |
| `TRACERTM_MCP_NAMESPACE` | Tool namespace prefix | - |
| `TRACERTM_MCP_RESOURCES_AS_TOOLS` | Expose resources as tools | `false` |
| `TRACERTM_MCP_PROMPTS_AS_TOOLS` | Expose prompts as tools | `false` |

## Development

### Running in Development Mode

```bash
# With verbose logging
rtm mcp start --dev

# Or set environment variable
TRACERTM_MCP_VERBOSE_LOGGING=true tracertm-mcp
```

### Listing Tools

```bash
rtm mcp tools
rtm mcp tools --verbose
rtm mcp tools --category project
```

### Listing Resources

```bash
rtm mcp resources
rtm mcp resources --verbose
```

### Testing

```bash
# Run MCP tests
pytest tests/mcp/ -v

# Run with coverage
pytest tests/mcp/ --cov=src/tracertm/mcp
```

## Architecture

```
src/tracertm/mcp/
├── __init__.py          # Package entry point with run_server()
├── __main__.py          # python -m tracertm.mcp entry point
├── core.py              # FastMCP server builder
├── server.py            # Server instance and module registration
├── auth.py              # Authentication provider
├── middleware.py        # Rate limiting, logging middleware
├── tools/
│   ├── __init__.py      # Tool module loader
│   ├── core_tools.py    # Core CRUD tools
│   ├── param.py         # Unified parameterized tools
│   ├── streaming.py     # Streaming and pagination tools
│   ├── specifications.py# ADR, contract, feature tools
│   └── ...
├── resources/
│   ├── __init__.py
│   ├── bmm.py           # BMM workflow resources
│   └── tracertm.py      # Core data resources
└── prompts/
    └── bmm.py           # BMM workflow prompts
```

## Troubleshooting

### Server won't start

1. Check FastMCP is installed: `pip show fastmcp`
2. Check Python version: `python --version` (requires 3.12+)
3. Run with verbose logging to see errors

### Claude Desktop doesn't connect

1. Verify config file location and syntax
2. Restart Claude Desktop after config changes
3. Check the server is accessible: `tracertm-mcp --help`

### Tools not appearing

1. List tools to verify: `rtm mcp tools`
2. Check for import errors in verbose mode
3. Ensure database is initialized: `rtm db init`

## Version History

- **0.2.0**: Added CLI entry points, streaming tools, MCP resources
- **0.1.0**: Initial MCP server with core tools
