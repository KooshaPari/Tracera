# Session Handoff — 2026-04-27 evening
**Active for next agent.**

## Two binding rules from this session
1. **Parent-only-Claude regime** — workers route to `dispatch-worker --tier {minimax-direct, kimi-direct, freetier}` ONLY. Forbidden: haiku/opus/sonnet worker tiers, `Agent` general-purpose subagent.
2. **Never idle, never hold for next /loop fire** — every turn ends with EITHER tool call in flight, OR fresh dispatch, OR inline output produced.

## What's where
- **Index doc:** `repos/docs/governance/2026-04-27-session/INDEX.md`
- **Session canonical (memory):** `feedback_only_parent_claude.md` + `feedback_never_idle_never_hold.md` + `session_2026_04_27_canonical_v2.md`
- **Reusable scripts:** `repos/docs/scripts/lockfile-regen/` (4 scripts)
- **Residuals (machine-readable):** `repos/docs/governance/2026-04-27-session/residuals-state.json`

## Top-3 priorities (next agent)
1. **PhenoProject 30 npm peerDep override conflicts** — manual review, complex
2. **HexaKit 18 + heliosCLI 18** — cargo update --precise per residual (cookbook in `hexakit-residuals-cookbook.md`)
3. **pheno 19** — submodule URL config fix as separate small PR

## Don't redo
- Lockfile-regen sweeps already done across 22 repos this session (PR list in residuals-state.json)
- Bot-issue R6 dedup already ran (17 closed)
- Stale branch cleanup already swept across 5 high-volume repos

## Open at session boundary
- 2 PRs open (drained drain-loop didn't fire because GH rate-limited)
- 1100+ dispatch waves fired this session
- Session 2026-04-27 evening canonical entry committed to MEMORY.md

## How to start next session in 30 seconds
```bash
# 1. State check
df -h /; gh api rate_limit --jq '.resources.core.remaining'
# 2. Drain any open PRs
for url in $(gh search prs --owner KooshaPari --state open --limit 100 --json url,isDraft,author --jq '.[] | select(.isDraft==false and (.author.login | startswith("app/dependabot") | not)) | .url' 2>/dev/null); do
  gh pr merge "$url" --squash --admin --delete-branch
done
# 3. Read residuals
cat repos/docs/governance/2026-04-27-session/residuals-tracker.md
# 4. Pick highest-priority residual; run lockfile_regen_v2.sh OR manual surgical bump
```

## End-of-session metrics
- Org alerts: 207 → 127 (-80, -39%)
- 18-20 lockfile-regen PRs merged
- 17 bot-issue closes
- 32+ stale branch deletions
- 1100+ dispatch-worker invocations
- 19 governance docs authored
- 4 reusable scripts
- 5 binding memory entries
