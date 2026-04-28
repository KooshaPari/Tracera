# Phenotype Org Session 2026-04-27 — parent-only-Claude regime

## Context shift mid-session
At ~3 hours in, user mandated **parent agent is the ONLY Claude allowed**. All subagents/workers must route to codex/kimi/minimax/freetier (NOT haiku/opus/sonnet). Then user mandated **never idle, never hold for next /loop fire**.

## Operating model adopted
1. Parent (this Opus 4.7 1M ctx) is the only Claude.
2. All delegated work routes through `dispatch-worker` shell wrapper to OmniRoute (`http://localhost:20128/v1`).
3. Working tiers: `minimax-direct` (M2.7-highspeed), `kimi-direct` (kmc/kimi-k2.5 → routes to gpt-oss-120b free), `freetier` (gemini-3-flash → routes to minimax 2.5 free).
4. Broken tiers this session: `codex-mini` (no openai creds), `gemini` (model 404).
5. Inline parent work: small lockfile regens, admin-merges, branch deletes via `gh api`/git CLI.
6. Reusable scripts: `/tmp/lockfile_regen.sh` + `/tmp/branch_cleanup_wide.sh` (committed to `repos/docs/scripts/lockfile-regen/`).

## Throughput delivered
- **18-20 lockfile-regen PRs merged** across HexaKit, QuadSGM (CRIT-2 cleared), KDesktopVirt, Tracera, PhenoLang (-36→3), thegent (-49→10), byteport, HeliosLab×2, heliosCLI×2, Civis, PolicyStack, PlatformKit, AgilePlus, Sidekick, Tasken, PhenoProject, pheno×2, Parpoura, heliosBench, phenotype-auth-ts, phenotype-ops-mcp.
- **17 bot-issue closes** (R6 sweep): 8 agentapi-plusplus + 9 helios-cli.
- **32+ stale branch deletions**: cliproxyapi 6, HexaKit 2, heliosCLI 5, AgilePlus 9, thegent 10.
- **Dependabot alerts org-wide: 207 → 127 (-80, -39%)**.

## Worker dispatch volume
- 130+ waves of 5-21 freetier/minimax/kimi workers each.
- Estimated 1500+ dispatch-worker invocations.
- All sub-second per call; aggregate cost ~$0 (free tiers + low-cost minimax).

## Operational lessons captured to memory
- `feedback_only_parent_claude.md` — parent-only-Claude rule
- `feedback_never_idle_never_hold.md` — never-idle rule + rate-limit cooldown pattern
- `feedback_session_budget_correction.md` — correction to "monthly limit" interpretation (it's session-level)
- `feedback_codex_dispatch_pattern.md` — codex-cli dispatch syntax (added by user)
- `feedback_no_claude_subagents.md` — user-authored complement to parent-only rule

## Failure modes observed
1. zsh `for f in glob/*` halts on no-match → switched to `bash` + `find ... while IFS= read`
2. `bash -c '$(declare -f fn); fn args'` heredoc escape breakage → fixed with real `.sh` files
3. Submodule URLs broken in some clones → `--no-recurse-submodules` flag
4. GitHub API 5000-req/hr ceiling hit at ~125 PRs into session → pivot to dispatch-only mode for ~40min cooldown
5. Process saturation at 92+ dispatch-worker processes → backpressure throttling needed (cap ~30)

## Residuals (manifest-bound, lockfile-regen alone won't help)
- **PhenoProject 30** (npm — multiple peerDep override conflicts during audit-fix)
- **pheno 19** (rust submodule URL block)
- **HexaKit 18** (rust transitives at semver pin)
- **heliosCLI 18** (npm peer-dep conflicts on uuid)
- **hwLedger 7**, **PhenoRuntime 6**, **KDesktopVirt 5**, **Dino 5** — small residuals

## Next-session recommendations
1. Targeted `cargo update --precise <crate>@<ver>` for HexaKit/heliosCLI Rust transitives.
2. Manual peerDep override resolution in PhenoProject.
3. pheno submodule URL config fix (separate PR).
4. Scope check: many lockfile-regens caught CRIT advisories (fastmcp SSRF, authlib JWS bypass) — verify CRIT count is now 0 across org.
