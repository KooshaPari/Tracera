# ADR: Parent-Only-Claude Regime + Never-Idle Mandate
**Date:** 2026-04-27
**Status:** Active
**Authority:** User mandate (verbatim quote): *"from now on you are the only allowed claude model, all else must be codex/mini/kimi"* + *"no idling, call agents plz never hold for next loop"*

## Decision
1. **Parent /loop agent is the ONLY Claude.** Any sub-work delegated MUST route to a non-Claude tier:
   - `dispatch-worker --tier {minimax-direct, kimi-direct, freetier}` for one-shot text tasks
   - `codex exec` (when creds configured) for code-execution tasks
   - Forbidden: `Agent` tool with `subagent_type: general-purpose` (defaults to Claude)
   - Forbidden: dispatch-worker tiers `haiku`, `opus`, `worker`, `main` (when they route to Claude)
2. **Parent must never voluntarily idle.** Each turn must end with EITHER (a) a tool call still in flight, OR (b) freshly-dispatched non-Claude workers, OR (c) inline output produced by parent. ScheduleWakeup is a safety net, not a pause.

## Rationale
- **Capacity pool:** Parent + every Claude subagent share the same ~6hr session budget. Routing workers to non-Claude tiers eliminates the contention pattern that hit "monthly limit" 3× this session.
- **Cost:** Free-tier minimax-2.5 + kimi-via-gpt-oss-120b = $0/call. Sub-second latency. 100+ wave dispatches feasible per hour.
- **Throughput:** Parent inline lockfile-regen + bash one-liners outperformed claude-subagent dispatch for mechanical tasks (1500+ worker dispatches this session).

## Anti-Patterns (forbidden)
- Calling `Agent` tool with general-purpose claude subagent for any work that fits dispatch-worker.
- Ending a turn with "holding for wakeup" or "stopping here for this iteration."
- Defaulting to `haiku` worker tier (was previously cheap-LLM default — now superseded).

## Required Memory References
- `feedback_only_parent_claude.md`
- `feedback_no_claude_subagents.md` (user-authored complement)
- `feedback_never_idle_never_hold.md`
- `feedback_session_budget_correction.md`

## Consequences
- Mass-dispatch playbooks (`dispatch-worker` waves) become primary leverage.
- Inline parent work for git/PR ops.
- Memory + governance docs become primary ROI artifacts when GH API is rate-limited.
- Branch cleanup, lockfile-regen, admin-merge are parent-direct, not subagent-delegated.
