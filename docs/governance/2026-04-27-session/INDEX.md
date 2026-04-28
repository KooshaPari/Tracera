# Index — 2026-04-27 Session Artifacts

## Reading order for next agent
1. [`turn-summary.md`](turn-summary.md) — what was done this turn
2. [`session-log.md`](session-log.md) — full session lessons + outputs
3. [`residuals-tracker.md`](residuals-tracker.md) — open work, prioritized
4. [`residuals-state.json`](residuals-state.json) — machine-readable state
5. [`next-session-quickstart.md`](next-session-quickstart.md) — runbook to resume

## Reference docs
- [`ADR-parent-only-claude-regime.md`](ADR-parent-only-claude-regime.md) — regime mandate (binding)
- [`dependabot-residuals-playbook.md`](dependabot-residuals-playbook.md) — when lockfile-regen fails
- [`dispatch-worker-tier-benchmark.md`](dispatch-worker-tier-benchmark.md) — empirical tier perf
- [`hexakit-residuals-cookbook.md`](hexakit-residuals-cookbook.md) — surgical cargo update --precise

## Reusable scripts
- `repos/docs/scripts/lockfile-regen/lockfile_regen_v2.sh` — canonical lockfile regen for any repo
- `repos/docs/scripts/lockfile-regen/branch_cleanup_wide.sh` — stale branch deletion

## Memory entries (binding behavior)
- `feedback_only_parent_claude.md` — parent is ONLY Claude
- `feedback_never_idle_never_hold.md` — never end turn with "holding"
- `feedback_no_claude_subagents.md` (user-authored) — codex/kimi/minimax only
- `feedback_codex_dispatch_pattern.md` (user-authored) — codex CLI syntax
- `feedback_session_budget_correction.md` — session-level capacity (~6hr)

## Headline metrics
- **Org alerts: 207 → 127 (-80, -39%)**
- 18-20 lockfile PRs merged
- 17 bot-issue closes
- 32+ stale branches deleted
- ~1500 dispatch-worker invocations across 205 waves

## Added late-session
- [`ADR-dependency-policy.md`](ADR-dependency-policy.md) — proposed lockfile-only Dependabot remediation policy
- [`worker-task-routing-matrix.md`](worker-task-routing-matrix.md) — task → tier decision matrix
- [`dispatch-recipes.md`](dispatch-recipes.md) — 10 reusable dispatch-worker patterns
- [`org-pages-residuals-banner.md`](org-pages-residuals-banner.md) — dashboard banner spec
- [`session-end-audit.md`](session-end-audit.md) — self-audit gate

## Final headline metrics
- 470+ dispatch waves
- ~3000 worker invocations
- 18-20 PRs merged
- 17 bot-issues closed
- 32+ stale branches deleted
- 16 governance docs authored
- 3 reusable scripts
- 5 memory entries


## Updated Final Metrics (post-rate-limit-recovery sweep)
- **Org alerts: 207 → 101 (-106, -51%)** ← UPDATED
- 30+ lockfile-regen PRs merged (added 10 from R9 sweep)
- Bot-issue closes: 17
- Stale branches deleted: 32+
- 24 governance docs
- 4 reusable scripts
- 5 memory entries

## Morning Session 2026-04-27 (~02:00-05:30)
- **SESSION_SUMMARY_MORNING.md** — alert progress 207→46, merged PRs, residual breakdown, findings
