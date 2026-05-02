# CLAUDE.md — dispatch-mcp

Extends parent governance. See:
- **Global baseline:** `~/.claude/CLAUDE.md`
- **Phenotype root:** `/Users/kooshapari/CodeProjects/Phenotype/repos/CLAUDE.md`

## Project Overview

- **Name:** dispatch-mcp
- **Description:** MCP-based dispatch/orchestration tools for Phenotype org
- **Location:** repos/dispatch-mcp
- **Language Stack:** Python (pip)
- **Status:** Active development

## Quality Checks

```bash
pytest
ruff check .
ruff format .
```

## AgilePlus Mandate

All work MUST be tracked in AgilePlus:
- CLI: `cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>`
- Check for existing specs before implementing
- Create spec for new work: `agileplus specify --title "<feature>" --description "<desc>"`
- No code without corresponding AgilePlus spec
