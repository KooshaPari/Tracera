# GEMINI.md - Development Guidelines for TracerTM

## Project Overview

TracerTM is an agent-native, multi-view requirements traceability and project management system. It provides defense-in-depth project governance, linking requirements to code, tests, and deployments across multiple architectural lenses.

## Key Files

- `README.md` - Project overview and usage
- `AGENTS.md` - Kilo Gastown integration and agent handbook
- `pyproject.toml` - Python package config, pytest/ruff settings
- `Taskfile.yml` - Task automation
- `src/tracertm/` - Python services & CLI
- `frontend/` - React/TypeScript SPA

## Development Commands

```bash
# Python (Primary)
task install        # Install dependencies (or: uv sync)
pytest              # Run tests (or: task test)
pytest -m unit      # Unit tests only
pytest -m integration  # Integration tests
ruff check . && ruff format .  # Lint & format
ty check src/       # Type checking
task quality        # Full quality gates

# Frontend
cd frontend
bun run dev         # Start dev server
bun run build       # Production build
bun run lint        # ESLint
bun run typecheck   # TypeScript check
bun test            # Vitest tests

# Go Backend
go test ./...
go build ./...
golangci-lint run

# All Services
task dev:tui        # Start all services with interactive TUI
task dev            # Standard dev mode
```

## Architecture Principles

- **Multi-Service Architecture** - Go backend, Python services, React frontend
- **Observability-First** - Prometheus, Loki, Jaeger integration
- **Agent-Native** - Built-in support for AI-assisted analysis
- **Defense in Depth** - Multiple quality gates and governance layers

## Kilo Gastown Integration

This repository is a **rig** in Kilo Gastown.

- **Rig ID**: `9614f3ef-45c8-4bdc-bdf2-906899b5f052`
- **Town**: `78a8d430-a206-4a25-96c0-5cd9f5caf984`
- **Worktree Branch**: `convoy/methodology-trace/a8883763/head`

### Work Delegation

Use `gt_sling` and `gt_sling_batch` for delegating work to other agents:

```bash
gt_sling <bead_id> <agent_id>  # Delegate single bead
gt_sling_batch <bead_ids> <agent_id>  # Delegate multiple beads
```

## Agent Behavior Guidelines

When working in this repository as a Gemini agent:

1. **GUPP Principle**: Work is on your hook — execute immediately
2. **Commit Frequently**: Push after every meaningful unit of work
3. **Checkpoint**: Call gt_checkpoint after significant milestones
4. **No Destructive Ops**: Never force push, hard reset, or merge to main
5. **Pre-Submission Gates**: Run `task quality` before considering work complete

## Communication

- Check mail periodically with gt_mail_check
- Use gt_mail_send for coordination with other agents
- Keep messages concise and actionable
- Use gt_status for meaningful phase transitions

## Quality Standards

- **Opinionated Quality**: Follow the strict styling and linting rules
- **Fix Properly**: Do not use `nolint` or `ignore` comments
- **Preserve Coverage**: Ensure all changes maintain or improve existing test coverage
- **CI Completeness**: Fix all CI failures before merging
