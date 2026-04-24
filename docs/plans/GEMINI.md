# Gemini Agent Methodology Specification

## Overview

This document describes the Gemini agent methodology as implemented in this TracerTM rig. Gemini agents are AI-powered autonomous workers that process beads using the GUPP (Gemini Unit Processing Protocol) principle for immediate, focused execution.

**Rig ID**: `9614f3ef-45c8-4bdc-bdf2-906899b5f052`  
**Town ID**: `78a8d430-a206-4a25-96c0-5cd9f5caf984`

---

## Core Principles

### GUPP Principle

**Work is on your hook — execute immediately.**

Gemini agents operate with a strict focus on their current hooked bead:

- Do not announce what you will do; just do it
- Produce code, commits, and results immediately
- No preamble, no status updates, no asking for permission
- When a bead arrives, start working right away

### Command Debouncing & Locking

High-impact commands (e.g., `make lint`, `make test`, `make quality`) should use locking mechanisms:

- Check for existing locks in `.process-compose/locks/` before running heavy commands
- If a command is already running, wait for it to finish or skip and use its results
- Use `scripts/shell/smart-command.sh` for wrapped execution when available

### Process-Compose Awareness

All core services run under `process-compose` with hot-reload enabled:

- **DO NOT** start services individually
- Use `make dev-status` to check service health
- Use `make dev-restart SERVICE=<name>` to restart a specific service
- Use `make dev-logs-follow SERVICE=<name>` to debug

---

## Bead Lifecycle

### States

| State | Description |
|-------|-------------|
| `open` | Available for assignment |
| `in_progress` | Agent is actively working |
| `in_review` | Submitted for merge/review |
| `closed` | Completed and merged |

### Transitions

```
open → in_progress (agent hooks bead)
in_progress → in_review (agent calls gt_done)
in_review → closed (refinery merges)
```

---

## Agent Workflow

### Standard Gemini Workflow

1. **Prime**: Context is auto-injected on first message. Call `gt_prime` to refresh if needed.
2. **Work**: Implement the bead's requirements immediately
3. **Commit**: Make small, focused commits after every meaningful unit of work
4. **Push**: Push after every commit (disk is ephemeral)
5. **Checkpoint**: Call `gt_checkpoint` after significant milestones
6. **Done**: Call `gt_done` when complete (pushes branch, transitions to `in_review`)

### Pre-Submission Quality Gates

Before calling `gt_done`, run all quality gates:

```bash
# Python
task quality  # or: ruff check . && ruff format . && ty check src/ && pytest

# Frontend
cd frontend && bun run lint && bun run typecheck

# Go backend
go test ./... && golangci-lint run
```

---

## Communication Protocols

### gt_mail_send

Send a typed message to another agent in the rig:

```bash
gt_mail_send --to_agent_id <agent_id> --subject <subject> --body <body>
```

Use for coordination, questions, or status sharing.

### gt_mail_check

Read and acknowledge all pending (undelivered) mail:

```bash
gt_mail_check
```

Returns an array of mail messages. Once read, they are marked as delivered.

### gt_nudge

Send a real-time nudge to another agent:

```bash
gt_nudge --target_agent_id <agent_id> --message <message> [--mode wait-idle|immediate|queue]
```

Unlike mail (queued persistent), nudges deliver immediately at the agent's next idle moment.

---

## Quality Standards

### Opinionated Styling

- Follow the project's strict linting and formatting rules
- Do not use `nolint` or `ignore` comments
- Fix the root cause of issues

### No Destructive Operations

- Never force push to main/master
- Never hard reset to remote
- Never merge to main yourself
- Do not use `gh pr create`, `git merge`, or equivalent

### Documentation Organization

- **No Root Markdown**: Do not create `.md` files in the project root
- **Proper Subdirectories**: Place all new documentation in `docs/` (e.g., `docs/guides/`, `docs/reports/`, `docs/reference/`)

### CI Completeness

- Fix all CI failures before merging
- Never skip or bypass quality gates

---

## Multi-Agent Coordination

Assume many isolated/uncommunicating actors (other agents or the user) are working in the same workspace.

### Shared Resource Management

- **Consolidated Commands**: Prefer unified targets (`make test`, `make lint`, `make quality`) over specific ones
- **Prevent Naming Explosion**: Do not create new specific test or lint targets for every sub-task
- **Native Over Docker**: Prefer native tools and services. Use Docker only if explicitly requested.

### Coordination Best Practices

- Check mail periodically with `gt_mail_check`
- Use `gt_status` for meaningful phase transitions
- Keep messages concise and actionable
- Call `gt_checkpoint` after significant progress

---

## Escalation

If stuck after a few attempts at the same problem:

1. Call `gt_escalate` with a clear description of what's wrong and what was tried
2. Continue working on other aspects if possible
3. Wait for guidance

---

## Integration with TracerTM

This rig implements TracerTM, an agent-native requirements traceability system. The Gemini methodology ensures:

- **Traceability**: Every bead can be traced to requirements
- **Visibility**: Status updates visible on dashboard
- **Coordination**: Agents communicate via mail and nudges
- **Quality**: Pre-submission gates prevent regressions

---

## References

- AGENTS.md - Agent handbook with development commands
- CLAUDE.md - Claude-specific development guidelines
- docs/plans/KILO_GASTOWN_SPEC.md - Kilo Gastown orchestration methodology
- docs/plans/AGILEPLUS_SPEC.md - AgilePlus specification-driven development
- Taskfile.yml - Task automation definitions
