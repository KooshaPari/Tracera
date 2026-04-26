# Scope Expansion Policy

**Status**: ACTIVE | **Owner**: orchestration | **Date**: 2026-04-26

## Rule

When the agent appears out of tasks or hits a blocker on the current scope, **expand the scope before going idle**. Idle (no agents in flight, no pending work) is a policy violation when adjacent valuable work exists.

**≥5 ACTIVE FLOOR (mandatory, 2026-04-26 user clarification):** Always hold **>5 active background agents**, even if some tasks block on user/external action. Fill blocker-vacated slots with other relevant work from the expansion ladder. If >5 agents are needed and tasks are independent, **parallelize aggressively** — there is no upper cap when work decomposes cleanly. The floor is not just for "loop ticks" — it applies anytime there is in-flight work to dispatch.

## Triggers

- A subagent reports "no further action" / "nothing to fix"
- A PR is blocked on external action (review, billing, network)
- Disk/billing/permission constraint stops one workstream

## Expansion ladder (apply in order)

1. **Adjacent files/repos**: same audit pattern, next repo or sub-tree
2. **Inverse audit**: if confirming X, also enumerate where X is missing
3. **Tier-down**: tier-1 → tier-2 → tier-3 repos for the same check
4. **Cross-cutting concerns**: if fixing repo X surfaces a generalizable pattern, audit org-wide
5. **Backlog cross-pollination**: revisit memory `Tasks pending`, `Open follow-ups`, governance docs from prior sessions
6. **Truth-state recheck**: re-verify earlier session claims (audit drift goes ~30-50%/week)
7. **Memory consolidation**: if everything is verified, harden a memory rule from observed patterns

## Anti-patterns

- Halting because "the task as defined is done" while related work obviously remains
- Reporting "nothing to do" when memory has explicit pending tasks
- Idle ScheduleWakeup chains without dispatching meaningful work in between

## How to apply

When a subagent finishes with "skipped" / "no action" / "blocked":
- Re-read the originating memory or governance doc for adjacent items
- Dispatch the next-tier or next-pattern audit
- Only stop the loop (omit ScheduleWakeup) if the *entire org* is verified clean AND no pending memory tasks remain.

## Companion memory

Add: `feedback_scope_expansion.md` — "When blocked or out of tasks, expand scope before going idle."
