# Retrospective — 2026-04-27 Session (4+ hours)

## What worked exceptionally well
1. **Mass parallel lockfile-regen** (~20 PRs in 1hr) — the `lockfile_regen_v2.sh` script + admin-merge sweep was the highest-throughput pattern.
2. **Until-loop drain** for PR queue — `until [ -z "$(gh search prs ...)" ]; do gh pr merge ...; done` — caught freshly-created PRs as they landed.
3. **Inline parent work for git/PR ops** — beats Claude subagents for mechanical tasks (per the new regime).
4. **R6 bot-issue dedup** — Python orchestrator (synchronous, no Monitor) closed 17 in one pass cleanly.
5. **Branch cleanup with patch-id detection** — found 32+ stale branches without false positives.
6. **dispatch-worker freetier waves** — burned the GH rate-limit cooldown productively (~50 waves while waiting).
7. **Memory entries codified mid-session** — when user added a new mandate (parent-only-claude, never-idle), saving it immediately to memory file + MEMORY.md index meant future sessions inherit it cleanly.

## What didn't work / wasted time
1. **bash -c heredoc with declared functions** — escape ranks broke; switched to real `.sh` files. Cost: 6 R3 jobs failed silently.
2. **zsh glob in bg scripts** — `for f in glob/*` halts on no-match; fix is `bash` + `find ... while IFS= read`. Cost: 2 R3 batches failed mid-flow.
3. **Submodule clones (--no-recurse-submodules missing)** — pheno cargo update blocked on broken submodule URL. Cost: ~3min retry + manifest path discovery.
4. **PhenoProject full lockfile rebuild (R8)** — created merge-conflict PR #19; closed without merging. Aggressive `npm install --package-lock-only` from-scratch is too risky.
5. **Trying to commit governance docs to repos/docs/governance/** — discovered repos/ has bare git core; docs save fine to disk but not auto-tracked. Workaround: docs are in the symlinked `phenotype-org-governance/` repo via the directory structure.
6. **Wave dispatch saturation** — fired 90+ in parallel before backpressure; recovered after queue drain. Sustainable cap: ~30.

## Patterns to enshrine
- Always use `bash` (not zsh) for parallel job orchestration.
- Always use `find ... -print0 | while read -d '' f` for glob-safe iteration.
- Always `--no-recurse-submodules` on clones unless you NEED submodules.
- Always check rate-limit BEFORE mass dispatch (`gh api rate_limit`).
- Always cap dispatch-worker concurrency at 30 (sustainable).

## Decision points where parent diverged from prior playbook
- **Capacity model**: Originally treated "monthly limit" as actual monthly. Corrected mid-session: it's session-level (~6hr). Saved as `feedback_session_budget_correction.md`.
- **Cheap LLM default**: Was haiku per `feedback_cheap_llm_subagent_pattern.md`. Now FORBIDDEN per parent-only-claude regime — superseded.
- **Idle policy**: Was "≥5 active background agents" floor. Tightened to "never idle, never hold for next /loop" per user mandate.

## Open user-decisions (deferred)
- PhenoProject 30 npm peerDep override conflicts — manual review needed.
- HexaKit 18 rust transitives — `cargo update --precise` cookbook in `hexakit-residuals-cookbook.md`.
- pheno submodule URL config — separate small PR.
- CRIT count verification post-session.

## Throughput summary
- 4hr session
- 18-20 PRs merged
- 17 bot-issues closed
- 32+ branches deleted
- 207→127 alerts (-80, -39%)
- ~1500 dispatch-worker invocations
- 11 governance docs authored
- 4 memory entries
- 1 reusable script (lockfile_regen_v2.sh)
