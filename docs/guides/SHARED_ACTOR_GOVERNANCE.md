# Shared Actor Governance Guide

This guide establishes the rules for multiple agents (Claude, Gemini, etc.) and users working simultaneously in the TraceRTM workspace.

## Core Principles

1.  **Shared Process Awareness**: `process-compose` is the source of truth for running services.
2.  **Command Debouncing**: High-impact commands (lint, test, quality) are locked to prevent redundant execution.
3.  **Graceful Interaction**: Use `process-compose` CLI/API for service management instead of raw scripts.

## How to Coordinate

### 1. Check Before You Run
Before running a heavy command like `make test` or `make lint`, check if another actor is already running it:
- Check for locks in `.process-compose/locks/`.
- Use `make dev-status` to see if services are healthy.
- If a lock exists, **WAIT** or **SKIP**.

### 2. Use Consolidated Targets
Avoid "naming explosion" in the `Makefile`. Use these primary entries:
- `make lint`: Runs naming guards, Go, Python, and Frontend linters with debouncing.
- `make test`: Runs Go, Python, and TypeScript tests with debouncing.
- `make quality`: Runs the full quality suite (static checks + tests).

### 3. Service Management
Services use "Check-Before-Start" logic in their underlying scripts (e.g., `postgres-if-not-running.sh`).
- **Restarting**: Use `make dev-restart SERVICE=<name>` if a service needs a kick.
- **Logs**: Use `make dev-logs-follow SERVICE=<name>` to monitor a specific service.
- **Don't kill manually**: Avoid `pkill` or manual `kill -9` unless `process-compose` fails to manage the process.

## Implementation Details

### Command Locking (`scripts/shell/smart-command.sh`)
High-impact `Makefile` targets wrap their logic in this script:
```bash
./smart-command.sh <command_key> <real_command> [required_services...]
```
- It creates a lock file in `.process-compose/locks/`.
- It verifies required services are up in `process-compose`.
- It handles PID tracking and cleanup.

### Governance Documentation
- `CLAUDE.md`: Updated with coordination rules.
- `AGENTS.md`: Updated with coordination rules.
- `docs/reference/GEMINI.md`: Mirror rules for Gemini.
