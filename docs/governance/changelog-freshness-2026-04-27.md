# CHANGELOG Freshness Audit — 2026-04-27

API-only audit of `KooshaPari/*` non-archived repos (n=82). Method: GitHub Contents API for `CHANGELOG.md` + `/releases/latest`; substring-match latest tag against first 2KB of CHANGELOG.

## Counts

| Category | Count | Definition |
|---|---:|---|
| MISSING | 30 | No `CHANGELOG.md` (Contents API 404) |
| STUB | 1 | Present but <200 bytes |
| NO_RELEASE_PRESENT | 34 | CHANGELOG present, no GitHub Release exists (cannot verify staleness) |
| STALE | 10 | Release exists, tag string absent from CHANGELOG head |
| CURRENT | 7 | Latest tag found in CHANGELOG head |

## Top-10 Stale (release exists, tag missing from CHANGELOG)

| Repo | Latest Tag | CHANGELOG size |
|---|---|---:|
| Dino | v0.23.0 | 145,987 |
| AgilePlus | v0.2.1 | 135,270 |
| vibeproxy | v1.5.0 | 49,144 |
| thegent | v0.1.2 | 3,683 |
| Tracera | v2.0.1 | 2,810 |
| helios-cli | v0.2.0 | 1,836 |
| HeliosLab | v0.2.2 | 774 |
| cliproxyapi-plusplus | v0.2.0 | 612 |
| PhenoKits | v0.1.1 | 452 |
| hwLedger | v0.1.0-alpha | 451 |

STUB: `phenoDesign` (185 B). CURRENT: agentapi-plusplus, FocalPoint, heliosApp, heliosCLI, phenoShared, PolicyStack, Tokn.

## Recommendation

Adopt **`git-cliff` (cliff.toml) + release-please** org-wide:

1. **Per-repo `cliff.toml`** generates Keep-a-Changelog from Conventional Commits; bind into release workflow so `CHANGELOG.md` is regenerated alongside the tag (closes the 10 stale + prevents recurrence on the 7 current).
2. **For the 34 NO_RELEASE_PRESENT repos**, gate first release behind `git cliff --bump --unreleased` to bootstrap version + entry atomically.
3. **For 30 MISSING + 1 STUB**, scaffold via shared `phenotype-infra` template (cliff.toml + GH Action) — same template already used by FocalPoint/heliosApp (CURRENT).
4. Hook into existing `task quality` so a tag without matching CHANGELOG entry fails locally before push.

Coverage today: 8.5% current / 86% gap. Target post-rollout: 100% auto-maintained.
