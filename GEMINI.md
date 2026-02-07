# Gemini Actor Governance

This document defines the rules and best practices for Gemini agents (and other high-capacity LLM actors) operating in this shared workspace.

## Multi-Actor Coordination

To prevent conflicts between multiple root agents, subagents, and human users, follow these rules:

1.  **Command Debouncing**: Use the `Makefile` or `Taskfile.yml` targets for high-impact tasks (linting, testing, validation). These are wrapped in `smart-command.sh` which uses lock files in `.process-compose/locks/`.
    *   `make lint` / `task lint`
    *   `make test` / `task test`
    *   `make quality` / `task quality`
    *   `make validate` / `task validate`

2.  **Shared Service Management**:
    *   **NEVER** force-kill processes (e.g., `pkill`, `killall`) unless absolutely necessary.
    *   **Always** check `process-compose` status first: `make dev-status`.
    *   **Assume** services are on hot-reload. Restarts should be done via `make dev-restart SERVICE=name`.
    *   Infrastructure services (Postgres, Redis, NATS, Neo4j) are shared. Do not stop them unless you are the only actor.

3.  **Resource Awareness**:
    *   Be mindful of CPU and Memory usage when running parallel tasks.
    *   Limit concurrent subagents to 50 (system-wide limit).

4.  **Logging**:
    *   Logs are consolidated in `.process-compose/process-compose.log`.
    *   Read specific service logs using `process-compose process logs <name> --port 18080`.

## Documentation First

*   **Documentation Organization**: Follow the strict structure defined in `AGENTS.md`.
*   **No Code in Plans**: Planner personas (Architect, PM, etc.) must NEVER write implementation code.
*   **DAG-based Planning**: Use phased WBS and Directed Acyclic Graphs for complex implementation plans.

## Quality Standards

*   **Opinionated Quality**: Follow the strict styling and linting rules.
*   **Fix Properly**: Do not use `nolint` or `ignore` comments. Extract helper functions or constants instead.
*   **Preserve Coverage**: Ensure all changes maintain or improve existing test coverage.

## See Also

*   `CLAUDE.md`: General context management and delegation strategy.
*   `AGENTS.md`: Detailed documentation organization and linting governance.
*   `SHARED_ACTOR_GOVERNANCE.md`: Master coordination rules for all actors.
