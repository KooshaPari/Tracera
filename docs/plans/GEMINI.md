# Gemini Methodology Specification for TracerTM

**Project**: TracerTM  
**Status**: Active  
**Last Updated**: 2026-04-01

---

## 1. Overview

Gemini is the agent-native development methodology implemented in the TracerTM ecosystem for Google Gemini-powered AI agents. It provides a structured framework for autonomous agent execution, multi-agent coordination, and specification-driven development that enables Gemini agents to operate effectively within the Kilo Gastown orchestration system.

In TracerTM, Gemini methodology defines how autonomous agents consume specifications, execute work items (beads), coordinate through the Gastown messaging system, and maintain traceability across the development workflow.

---

## 2. Core Principles

### 2.1 GUPP Principle

**G**et to **U**nique **P**olecat **P**rinciple: Work is on your hook — execute immediately.

- Do not announce what you will do; just do it
- Produce code, commits, and results directly
- Avoid preamble, status updates, or asking for permission
- Execute with confidence and correct on iteration

### 2.2 Agent Autonomy

Gemini agents operate with high autonomy:

- **Execute First**: Start implementation immediately upon receiving a bead
- **Own the Outcome**: See tasks through to completion or proper escalation
- **Proactive Coordination**: Use gt_mail_send and gt_nudge for timely communication
- **Self-Sufficient**: Attempt resolution before escalating

### 2.3 Specification-Driven Execution

Every bead links to a specification or follows established methodology:

- **Clear Ownership**: Each bead has a single assignee agent
- **Traceable Work**: All changes link back to bead and specification
- **Verifiable Outcomes**: Quality gates ensure fitness for merge
- **Audit Trail**: Checkpoints and commits provide recovery points

### 2.4 Human + AI Collaborative

Gemini methodology supports mixed human-AI development:

- Humans provide strategic direction through bead creation
- AI agents consume beads for autonomous execution
- Both can update bead status and progress
- Gastown orchestration provides coordination layer

---

## 3. Agent Roles

### 3.1 Polecat Agents

Polecats are the primary autonomous agents in Gastown:

- Execute hooked beads to completion
- Perform implementation, testing, and documentation
- Coordinate with other agents via messaging
- Escalate blockers via gt_escalate
- Push branches and call gt_done when complete

### 3.2 Refinery Agents

Refinery agents handle integration and review:

- Merge approved branches
- Validate quality gates
- Create pull requests
- Handle rework requests
- Close beads after successful merge

### 3.3 Coordinator Agents

Coordinators manage workflow orchestration:

- Dispatch beads to appropriate agents
- Monitor progress and status
- Resolve conflicts between agents
- Trigger phase transitions
- Manage convoy and methodology beads

---

## 4. Bead Lifecycle

### 4.1 Bead States

| State | Description |
|-------|-------------|
| `open` | Available for assignment |
| `in_progress` | Assigned and being worked |
| `in_review` | Submitted for review |
| `done` | Completed and merged |
| `blocked` | Waiting on dependency |
| `escalated` | Requires human intervention |

### 4.2 Bead Types

| Type | Purpose |
|------|---------|
| `issue` | Single task or bug fix |
| `convoy` | Multi-agent feature effort |
| `methodology` | Process/methodology specification |

### 4.3 Lifecycle Flow

```
open → in_progress → in_review → done
           ↓            ↓
       blocked     escalated
           ↓            ↓
       (resolve)   (human intervention)
```

### 4.4 Polecat Execution Flow

1. **Prime**: Call gt_prime for context injection and bead assignment
2. **Execute**: Implement bead requirements
3. **Commit**: Make focused commits with descriptive messages
4. **Push**: Push after every commit for crash recovery
5. **Checkpoint**: Call gt_checkpoint after significant milestones
6. **Quality**: Run `task quality` before considering complete
7. **Done**: Push branch and call gt_done

---

## 5. Communication Protocols

### 5.1 gt_mail_send

Send persistent messages to other agents:

```bash
gt_mail_send <to_agent_id> <subject> <body>
```

Use for:
- Coordination requests
- Status updates
- Handoff notifications
- Blocker notifications

### 5.2 gt_nudge

Send real-time nudges for immediate attention:

```bash
gt_nudge <target_agent_id> <message> [--mode immediate|wait-idle|queue]
```

Use for:
- Time-sensitive coordination
- Wake-up requests
- Blocking issue notifications

### 5.3 gt_mail_check

Check for undelivered mail:

```bash
gt_mail_check
```

Returns pending messages addressed to the agent. Call periodically or when expecting coordination.

### 5.4 Communication Guidelines

- **Concise**: Keep messages actionable and brief
- **Complete**: Include all context needed for response
- **Timely**: Use nudges for urgent, gt_mail for persistent
- **Traceable**: Reference bead IDs in all communications

---

## 6. Quality Enforcement

### 6.1 Pre-Submission Gates

Before calling gt_done, run all quality gates:

```bash
task quality  # Full quality gates (ruff, mypy, pytest)
```

Gates include:
- `ruff check .` - Lint validation
- `ruff format --check .` - Code formatting
- `ty check src/` - Type annotation validation
- `pytest` - Test suite execution

### 6.2 Quality Standards

| Standard | Requirement |
|----------|-------------|
| **No Silencing** | Do not use `nolint` or `ignore` comments |
| **Opinionated Styling** | Follow project strict linting rules |
| **Coverage Preservation** | Maintain or improve test coverage |
| **CI Completeness** | All CI checks must pass |

### 6.3 Fix Properly

When quality gates fail:

1. Analyze the failure output
2. Fix the root cause
3. Re-run the failing gate
4. Repeat until all gates pass
5. If unresolvable after 2-3 attempts, escalate

---

## 7. Git Workflow

### 7.1 Branch Model

Worktrees provide isolated development branches:

- Each bead/convoy gets a dedicated worktree
- Branch naming follows: `convoy/<feature>/<convoy_id>/<agent>`
- Never modify files outside your worktree

### 7.2 Commit Strategy

**Commit Frequently** — after every meaningful unit of work:

- New function implementation
- Passing test or test fix
- Configuration change
- Documentation update

**Commit Message Format**:
```
<type>(<scope>): <subject>

<body>
```

Examples:
```
feat(auth): add OAuth2 callback handler

- Implement callback endpoint
- Add session management
- Wire up WebSocket auth events

Closes: bead/7304e5d6
```

### 7.3 Push Hygiene

- Push after every commit (container disk is ephemeral)
- Do not batch pushes
- Use descriptive commit messages referencing bead ID

### 7.4 Prohibited Operations

Never perform these operations:

- `git push --force`
- `git hard reset` to remote
- `git merge` to main/master
- `gh pr create` (refinery handles this)
- Destructive git operations

---

## 8. Gastown Integration

### 8.1 Rig Configuration

TracerTM is a **rig** in Kilo Gastown:

- **Rig ID**: `9614f3ef-45c8-4bdc-bdf2-906899b5f052`
- **Town**: `78a8d430-a206-4a25-96c0-5cd9f5caf984`
- **Worktree Branch**: Per-convoy feature branches

### 8.2 Work Delegation

Delegate beads to other agents:

```bash
gt_sling <bead_id> <agent_id>  # Single bead
gt_sling_batch <bead_ids> <agent_id>  # Multiple beads
```

### 8.3 Bead Management

| Operation | Command |
|-----------|---------|
| Get context | `gt_prime` |
| Check status | `gt_bead_status <bead_id>` |
| Close bead | `gt_bead_close <bead_id>` |
| Signal done | `gt_done --branch <name>` |
| Escalate | `gt_escalate <title> <body>` |
| Checkpoint | `gt_checkpoint <data>` |

### 8.4 Status Updates

Use gt_status for meaningful phase transitions:

```bash
gt_status "Installing dependencies and setting up project structure"
gt_status "Writing unit tests for API endpoints"
gt_status "Fixing lint errors before committing"
```

Write for teammates watching the dashboard — not log lines.

---

## 9. Convoy Model

### 9.1 Convoy Overview

Convoys organize multi-agent feature development:

- **Convoy ID**: Links related beads
- **Feature Branch**: Shared branch for convoy
- **Parallel Execution**: Multiple agents work simultaneously
- **Coordination**: Coordinator dispatches beads to agents

### 9.2 Convoy Lifecycle

1. **Creation**: Coordinator creates convoy bead
2. **Dispatch**: Beads dispatched to polecat agents
3. **Execution**: Agents work in parallel worktrees
4. **Integration**: Refinery merges feature branch
5. **Completion**: Convoy closed after all beads done

### 9.3 Example Convoy Structure

```
Convoy: methodology-trace/a8883763
├── Bead 7304e5d6: Add GEMINI.md (Pike)
├── Bead db2fc1df: Add AgilePlus spec (另一Agent)
└── Feature Branch: convoy/methodology-trace/a8883763/head
```

---

## 10. Methodology Documents

### 10.1 GEMINI.md

This document — core methodology for Gemini agents in TracerTM.

### 10.2 AGILEPLUS_SPEC.md

Specification-driven development methodology — [`AGILEPLUS_SPEC.md`](./AGILEPLUS_SPEC.md)

### 10.3 KILO_GASTOWN_SPEC.md

Kilo Gastown orchestration system — [`KILO_GASTOWN_SPEC.md`](./KILO_GASTOWN_SPEC.md)

### 10.4 BMM Methodology

Scale-adaptive planning from `.archive/.bmad/bmm/docs/`

### 10.5 Other Agent Methodologies

| Agent | Methodology File |
|-------|------------------|
| Claude | `claude.md` |
| Codex | `.archive/.bmad/docs/codex-instructions.md` |
| Cursor | `.archive/.bmad/docs/cursor-instructions.md` |

---

## 11. Best Practices

### 11.1 Execution

- **Start Immediately**: Do not wait or ask — execute
- **Deliver Results**: Focus on producing code, not discussing
- **Iterate**: Fix issues quickly and push
- **Escalate When Stuck**: After 2-3 failed attempts, escalate

### 11.2 Coordination

- **Check Mail**: Periodically call gt_mail_check
- **Send Updates**: Notify relevant agents of progress
- **Reference Beads**: Always include bead IDs in communication
- **Be Concise**: Actionable messages, not essays

### 11.3 Quality

- **Run Gates**: Execute `task quality` before gt_done
- **Fix Root Cause**: Do not silence or ignore issues
- **Preserve Coverage**: Don't reduce test coverage
- **Commit Clean**: Lint and format before commit

### 11.4 Documentation

- **No Root MDs**: Do not create `.md` files in project root
- **Proper Locations**: Use `docs/` subdirectories
- **Link Specifications**: Reference related specs
- **Keep Updated**: Reflect actual implementation

---

## 12. Troubleshooting

### 12.1 Stuck Agent

If no progress for extended period:

1. Call `gt_mail_check` for coordination messages
2. Use `gt_nudge` to wake if waiting on response
3. If truly blocked, call `gt_escalate` with context
4. Include what was tried and what's blocking

### 12.2 Rework Request

If refinery returns changes:

1. Review feedback carefully
2. Implement fixes on same branch
3. Re-run quality gates
4. Push and call `gt_done` again

### 12.3 Container Restart

If container restarts:

1. Call `gt_prime` to re-establish context
2. Review checkpoint data if available
3. Continue from last checkpoint
4. Push any unpushed commits

---

## 13. Reference

- **Kilo Gastown**: Agent orchestration platform
- **TracerTM**: Requirements traceability system
- **AgilePlus**: Specification-driven development
- **Bead IDs**: Format `8-hexdigits-8-hexdigits-8-hexdigits-8-hexdigits`
- **Convoy IDs**: Format `8-hexdigits-4-hexdigits-4-hexdigits-4-hexdigits-12-hexdigits`

---

**End of Specification**
