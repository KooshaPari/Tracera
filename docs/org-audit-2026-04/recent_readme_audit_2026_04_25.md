# RECENT-tier README Freshness Audit — 2026-04-25

**Scope:** 25 most-active Phenotype-org repos (by 28-day commit count) sampled
from the canonical working tree at `/Users/kooshapari/CodeProjects/Phenotype/repos`.

**Method:** Read first ~80 lines of each `README.md` and the last 6 commits.
Score reflects whether the README accurately represents current state today
(2026-04-26): claims of shipped features, install/setup commands, and status
banners.

> Note: The named ledger `MASTER_AUDIT_LEDGER_2026_04_25.md` was not present
> on disk; the RECENT cohort here was derived from `git log --since=28d`
> commit-count ranking (top 25). All repos in the cohort had ≥18 commits in
> the last 28 days.

## Score legend

| Score | Meaning |
|-------|---------|
| GREEN  | README matches current state; setup commands plausibly run |
| YELLOW | Minor drift: stale status line, missing license/CHANGELOG ref, TODO leak, narrow gap |
| RED    | Misleading: wrong project README, claims unfinished features as shipped, broken install |

## Counts

- GREEN: 14
- YELLOW: 8
- RED:    3

## Findings

| Repo | Score | Top issue | Suggested fix |
|------|-------|-----------|---------------|
| pheno | YELLOW | README is "repos shelf" doc — pheno is now a Rust workspace (~170k LOC, 70 crates) per memory + recent commits adopting `phenotype-migrations`; README doesn't mention crates | Replace shelf text with crate inventory + workspace quickstart |
| FocalPoint | GREEN | Status banner explicitly admits "Compilation broken (2026-04-23)" + lists honest gaps; recent commits show v0.0.12 release continuing | Keep; maybe move banner into a STATUS.md once green |
| phenotype-omlx | YELLOW | Upstream-fork README; install path `brew tap jundot/omlx` is upstream, not the Phenotype fork; no mention of fork divergence (hwLedger JSON-RPC shim, StatusKit fixes) | Add "Phenotype fork" preamble + `KooshaPari/phenotype-omlx` install paths |
| hwLedger | GREEN | Status banner ("pre-alpha, P0"), DMG-blocked note, devtools crate name fixed in last commit (PR #36) | Keep |
| Dino | YELLOW | Lists "M14 Done" + "20/20 CI Workflows" but recent commits are exclusively Dependabot bumps; "Current test count: 1,017+" stated twice with mismatched 1,269+ above | Reconcile test count (1017 vs 1269); add real progress entry post-M14 |
| AgilePlus | RED | **README is the wrong document — shows "repos shelf" content for the AgilePlus project repo**; no mention of `agileplus` CLI, kitty-specs, or any AgilePlus feature | Replace entire README with AgilePlus product overview + CLI quickstart |
| heliosApp | GREEN | Version 2026.03A.0 matches recent v2026.05B.0 release commit (close); "TODO: add desktop shell screenshot" leak | Bump version line; remove TODO or move to issue |
| phench | YELLOW | "Status: maintenance" but 83 commits in 28d (mostly governance/dependabot); CLI examples (`phench benchmark run`) unverified | Verify CLI commands exist; clarify "maintenance" vs governance churn |
| artifacts | GREEN | Stub README, "Status: Maintenance" matches doc-only commits | Keep, but expand purpose |
| thegent | GREEN | Recent commit "bridge Python thegent CLI and Rust thegent-dispatch surfaces" matches README scope | Keep |
| PhenoObservability | YELLOW | "Status: maintenance" but 56 commits in 28d incl. feat work on async_instrumented; crate table real | Status downgrade is wrong → "active" |
| heliosCLI | GREEN | Architecture section accurate; PR #237 fixed crate count drift; v0.2.1 release noted in log | Keep |
| KDesktopVirt | GREEN | README explicitly disambiguates from KVirtualStage and corrects prior archive notice (PR #7); v0.2.1 release matches | Keep |
| phenoShared | GREEN | Crate table updated (PR #104), Phase 1 imports (PR #102) reflected | Keep |
| PhenoProc | YELLOW | "Status: maintenance" claimed; SPEC.md/AGENTS.md referenced but `cat SPEC.md` quickstart unverified; pheno-contracts crate moved to phenoShared (per recent commit `feat(contracts): import phenotype-contracts crate from PhenoProc`) but README still claims phenoShared inherits — actually crate is now gone from PhenoProc | Note that contracts crate was extracted; update crate list |
| PhenoSpecs | YELLOW | `spec-links check`, `spec-new create` CLI commands referenced but no install instructions; registry.yaml referenced — not verified | Add install path or strike commands |
| phenotype-infra | GREEN | "Operational status (2026-04-24)" banner is current; runbook references concrete | Keep |
| phenotype-journeys | GREEN | Status implicit from Quickstart; "Planned consumers" honestly labeled "Planned" | Keep |
| PhenoKits | YELLOW | "Status: maintenance" but 30 commits in 28d incl. Phase 1 forced-adoption sweep | Reclassify status |
| BytePort | RED | README is unmigrated student-project narrative ("GPT YAP BELOW (outdated)"); ASCII art, broken Quickstart ("spin build up"), `localhost:5180, ILOVEKUSHPAPI` credentials in markdown; recent SBOM/dep commits indicate active maintenance | Full rewrite: drop "GPT YAP" section, modernize quickstart, scrub embedded credential string |
| agentapi-plusplus | GREEN | PR #465 "correct API routes and required flags per user-story audit" indicates README was fact-checked recently | Keep |
| DataKit | GREEN | Status "Active", license + bindings accurate, Python primary surface flagged honestly | Keep |
| Eidolon | GREEN | "Active Development" + WIP markers honest; KVirtualStage merge note current | Keep |
| cliproxyapi-plusplus | YELLOW | Self-reference loop: "This is the Plus version of [cliproxyapi-plusplus](.../cliproxyapi-plusplus)"; should reference upstream `router-for-me/CLIProxyAPI` | Fix upstream link |
| GDK | RED | Reads as marketing copy: "🚀 FINALIZED FOR UNSUPERVISED ENTERPRISE AND PRODUCTION USAGE", quality scores ("0.96") in README, demo gifs likely missing; recent commits are baseline ci/license/cargo-deny adoption — i.e. genuinely early; "Production Ready" badge contradicts | Strip marketing emoji block, replace with real status (early/exploratory) |

## Top 5 RED / RED-leaning

1. **AgilePlus** — wrong README entirely (org shelf doc).
2. **BytePort** — outdated narrative + embedded plaintext credential string.
3. **GDK** — "Enterprise Production Ready" claims contradicted by current commit pattern.
4. **PhenoObservability** — status="maintenance" claim is materially wrong (active feat work).
5. **PhenoKits** — status="maintenance" claim wrong (Phase 1 adoption sweep in flight).

## Recommended next actions

- Open one PR per RED repo with corrected README (AgilePlus, BytePort, GDK).
- Status-banner sweep across YELLOW repos: enforce status taxonomy (active / maintenance / archived) and verify against `git log --since=28d` automatically.
- Add a CI check that fails when README "Status: maintenance" coincides with ≥20 substantive commits in the prior 28 days.
