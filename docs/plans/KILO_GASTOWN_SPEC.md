# Kilo Gastown Methodology Specification

## Overview

This document describes the Kilo Gastown agent orchestration methodology as implemented in this TracerTM rig.

**Rig ID**: `9614f3ef-45c8-4bdc-bdf2-906899b5f052`  
**Town ID**: `78a8d430-a206-4a25-96c0-5cd9f5caf984`

---

## Core Concepts

### Convoys

Convoys are collaborative work branches that group related feature work across multiple agents. They enable parallel development on shared objectives.

- **Naming**: `convoy/<feature>/<convoy_id>/head`
- **Tracking**: Each convoy has a dedicated worktree branch
- **Coordination**: Multiple agents can work on the same convoy simultaneously

### Beads

Beads are the fundamental work unit in Kilo Gastown.

| Type | Purpose |
|------|---------|
| `issue` | Task or feature work |
| `convoy` | Collaborative work branch tracker |

**Bead Lifecycle**:
1. `open` - Available for assignment
2. `in_progress` - Agent is actively working
3. `in_review` - Submitted for merge/review
4. `closed` - Completed and merged

### Agents

Agents are autonomous workers that process beads. Each agent has:

- A unique `agent_id`
- A role (e.g., `polecat`)
- A current hooked bead (work in progress)
- Mailbox for coordination messages

---

## Work Delegation

### gt_sling

Delegates a single bead to another agent:

```bash
gt_sling <bead_id> <agent_id>
```

### gt_sling_batch

Delegates multiple beads to another agent:

```bash
gt_sling_batch <bead_ids> <agent_id>
```

Example delegating 3 beads:
```bash
gt_sling_batch "bead1 bead2 bead3" target_agent_id
```

---

## Agent Coordination Tools

| Tool | Purpose |
|------|---------|
| `gt_prime` | Get full context: identity, hooked bead, mail, open beads |
| `gt_bead_status` | Inspect current state of any bead by ID |
| `gt_bead_close` | Close a bead when work is complete |
| `gt_done` | Signal completion, push branch, transition bead to `in_review` |
| `gt_mail_send` | Send a message to another agent |
| `gt_mail_check` | Check for pending coordination messages |
| `gt_escalate` | Create an escalation bead for blocked issues |
| `gt_checkpoint` | Write crash-recovery state |
| `gt_status` | Emit dashboard-visible status updates |
| `gt_nudge` | Send real-time nudge to another agent |

---

## Workflow

### Standard Agent Workflow

1. **Prime**: Call `gt_prime` at session start to get context
2. **Work**: Implement the hooked bead's requirements
3. **Commit**: Make small, focused commits frequently
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

### Escalation

If stuck after a few attempts at the same problem:
1. Call `gt_escalate` with description of issue and what was tried
2. Continue working on other aspects if possible
3. Wait for guidance

---

## Merge Modes

Agents do not merge their own branches. The Refinery system handles:
- Pull request creation
- Merge execution
- Branch cleanup after successful merge

**Important**: Do NOT use `gh pr create`, `git merge`, or equivalent commands.

---

## Best Practices

### Commits
- Commit after every meaningful unit of work
- Use descriptive commit messages
- Push after every commit (ephemeral disk)

### Status Updates
- Call `gt_status` at meaningful phase transitions
- Write for teammates, not log lines
- One or two sentences maximum

### Coordination
- Check mail periodically with `gt_mail_check`
- Use `gt_mail_send` for formal coordination messages
- Use `gt_nudge` for time-sensitive wake-ups

---

## Integration with TracerTM

This rig implements TracerTM, an agent-native requirements traceability system. The methodology ensures:

- **Traceability**: Every bead can be traced to requirements
- **Visibility**: Status updates visible on dashboard
- **Coordination**: Agents communicate via mail and nudges
- **Quality**: Pre-submission gates prevent regressions

---

## References

- AGENTS.md - Agent handbook with development commands
- docs/plans/ - Implementation plans and specifications
- Taskfile.yml - Task automation definitions
