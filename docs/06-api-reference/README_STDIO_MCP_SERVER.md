# Stdio MCP Server with FastMCP

A production-grade Model Context Protocol (MCP) server built with FastMCP 2.13 that replicates and extends Claude Code's task tool with advanced features for batch execution, DAG-based planning, and async/sync execution modes.

## Features

### Core Task Tool
- Identical replication of Claude Code's task tool
- Task creation, status tracking, hierarchical organization
- Full task lifecycle management

### Batch Execution
- Execute multiple tasks in batch mode
- Parallel execution of independent tasks
- Sequential execution with dependency resolution
- Comprehensive error handling

### DAG-Based Planning
- Directed acyclic graph construction
- Topological sorting for execution order
- Cycle detection and prevention
- Critical path analysis

### Async/Sync Execution
- Async-first implementation for concurrent execution
- Sync mode for sequential workflows
- Graceful fallback mechanisms
- Hybrid execution support

### Mid-Execution Interaction
- Bidirectional communication between parent and child tasks
- Status checking during execution
- Message passing and state synchronization
- Designed for massive distributed task coordination

## Quick Start

### Prerequisites
- Python 3.12+
- uv package manager

### Installation

```bash
# Clone and navigate to project
cd stdio-mcp-server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
```

### Running the Server

```bash
# Start stdio MCP server
uv run python server.py

# Or with environment variables
FASTMCP_DEBUG=1 uv run python server.py
```

### Testing

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov

# Run specific test suite
uv run pytest tests/unit/ -v
```

## Architecture

See `docs/sessions/20251115-stdio-mcp-server/04_IMPLEMENTATION_STRATEGY.md` for detailed architecture.

## Documentation

- `AGENTS.md` - Agent automation guidelines
- `CLAUDE.md` - Claude AI agent guide
- `docs/sessions/20251115-stdio-mcp-server/` - Session documentation

## Development

Follow the guidelines in `AGENTS.md` and `CLAUDE.md` for autonomous development.

### Key Principles

- **Modularity**: All modules ≤350 lines (500 hard limit)
- **Autonomy**: Agents operate independently with minimal human intervention
- **Quality**: Full test coverage, type safety, comprehensive logging
- **Aggressiveness**: No backwards compatibility shims, full refactoring when needed

## License

MIT

