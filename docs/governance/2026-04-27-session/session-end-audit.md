# Session-End Audit Checklist (durable artifact)

For any /loop session approaching close, run through this:

## State checks
- [ ] `df -h /` — disk free ≥30Gi (else trigger target-pruner)
- [ ] `gh api rate_limit --jq .resources.core.remaining` — record remaining
- [ ] `ps aux | grep dispatch-worker | grep -v grep | wc -l` — record active workers
- [ ] Active background jobs (TaskList) — record any unfinished work

## Org snapshot (if GH API available)
- [ ] Top-10 repo alert ranking — saved to `residuals-state.json`
- [ ] Open non-draft non-dependabot PR count — should be 0 or noted
- [ ] Recent merged PRs (last 4hrs) — saved to session log
- [ ] Stale branch count by repo — recorded

## Memory hygiene
- [ ] New memory entries this session — listed in turn-summary.md
- [ ] MEMORY.md index updated to point at new entries
- [ ] Any superseded memory entries — annotate as deprecated, don't delete

## Governance docs hygiene
- [ ] All session-specific docs in `repos/docs/governance/<date>-session/`
- [ ] INDEX.md updated to point at all docs
- [ ] residuals-state.json regenerated for next agent
- [ ] next-session-quickstart.md current

## Worker fleet hygiene
- [ ] /tmp/wave* cleaned to last 30 dirs
- [ ] /tmp/* clones removed
- [ ] No orphan dispatch-worker processes (check ps)

## Standing items to flag
- [ ] User-decisions still pending (PRs, manifest edits, security reviews)
- [ ] Cron jobs scheduled (if recurring work)
- [ ] ScheduleWakeup armed (if dynamic wake needed)

## Hand-off
- [ ] turn-summary.md written with concrete metrics
- [ ] retrospective.md updated with lessons learned
- [ ] residuals-tracker.md updated with priorities

This checklist is a self-audit gate — running through it ensures no work falls through the cracks at session boundary.
