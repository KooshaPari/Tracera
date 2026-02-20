# Quick Start for Agents

## Before You Start

1. **Read AGENTS.md** - Understand autonomous operation expectations
2. **Read CLAUDE.md** - Understand the development workflow
3. **Review Session Docs** - Check `docs/sessions/20251115-stdio-mcp-server/`

## Key Commands

```bash
# Activate environment
source .venv/bin/activate

# Run tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov

# Check code quality
uv run ruff check .
uv run mypy .

# Format code
uv run ruff format .

# Start server
uv run python server.py
```

## Critical Rules

1. **Modularity**: Keep all files ≤350 lines (500 hard limit)
2. **Autonomy**: Proceed without asking unless blocked by secrets/ambiguity
3. **Research**: Always research before implementing
4. **Testing**: Write tests as you code
5. **Aggressiveness**: No backwards compatibility, full refactoring when needed

## Project Structure

```
stdio-mcp-server/
├── server.py              # FastMCP entry point
├── tools/                 # Tool implementations
├── services/              # Business logic
├── infrastructure/        # Adapters
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Development Loop

1. **Review** - Understand the task
2. **Research** - Check codebase and external docs
3. **Plan** - Create a short plan
4. **Execute** - Implement in small increments
5. **Test** - Run tests after each change
6. **Polish** - Clean up and optimize
7. **Repeat** - Loop until complete

## When to Ask

Only ask when:
- Missing credentials/secrets
- Genuine product ambiguity
- Destructive operations needed

Otherwise, proceed autonomously!

## References

- AGENTS.md - Full agent guidelines
- CLAUDE.md - Full Claude guide
- docs/sessions/20251115-stdio-mcp-server/ - Session documentation
- README_STDIO_MCP_SERVER.md - Project overview

