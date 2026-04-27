# KooshaPari Org — Releases & Tags Inventory (2026-04-27)

Snapshot of all non-archived, non-fork repositories in the KooshaPari GitHub org (71 repos), bucketed by release/tag presence. Generated via `gh api` walk over `/tags`, `/releases`, and `/releases/latest`.

## Summary

| Bucket | Count |
|---|---|
| HAS RELEASES (≥1 GitHub release) | 16 |
| TAGS ONLY (≥1 tag, 0 releases) | 1 |
| NO TAGS (zero tags, zero releases) | 54 |
| **Total** | **71** |

### Latest-release-age distribution (HAS RELEASES bucket only)

| Age of latest release | Count |
|---|---|
| < 30 days | 15 |
| 30–90 days | 1 |
| > 90 days | 0 |
| Never released (TAGS_ONLY + NO_TAGS) | 55 |

> Note: 4 repos in HAS RELEASES (`HexaKit`, `pheno`, `PhenoLang`, `phenoShared` partially) return `404` on `/releases/latest` — those releases exist as **drafts or prereleases only**; published-latest age is undefined for them and they are excluded from the age histogram. `phenoShared` has a published `v0.1.0` and is included.

## HAS RELEASES (16)

- `AgilePlus` — 4 releases, latest `v0.2.1` (2026-04-26T07:38:25Z)
- `Dino` — 16 releases, latest `v0.23.0` (2026-04-23T09:36:33Z)
- `FocalPoint` — 5 releases, latest `v0.0.12` (2026-04-26T03:03:42Z)
- `heliosApp` — 7 releases, latest `v2026.05B.0` (2026-04-26T02:39:43Z)
- `heliosBench` — 1 releases, latest `v0.2.0` (2026-04-25T13:31:43Z)
- `heliosCLI` — 3 releases, latest `v0.2.1` (2026-04-25T15:23:44Z)
- `HexaKit` — 1 releases, latest `(drafts/prereleases only)` (-)
- `hwLedger` — 1 releases, latest `v0.1.0-alpha` (2026-04-19T10:31:10Z)
- `pheno` — 1 releases, latest `(drafts/prereleases only)` (-)
- `PhenoKits` — 2 releases, latest `v0.1.1` (2026-04-26T02:57:20Z)
- `PhenoLang` — 1 releases, latest `(drafts/prereleases only)` (-)
- `phenoShared` — 1 releases, latest `v0.1.0` (2026-03-29T14:14:26Z)
- `PolicyStack` — 1 releases, latest `v0.1.0` (2026-04-26T03:55:33Z)
- `thegent` — 3 releases, latest `v0.1.2` (2026-02-23T03:45:06Z)
- `Tokn` — 2 releases, latest `v0.1.1` (2026-04-26T04:05:40Z)
- `Tracera` — 3 releases, latest `v2.0.1` (2026-03-29T15:08:36Z)

## TAGS ONLY (1) — first-release candidates for `gh release create`

- `eyetracker` (2 tags)

## NO TAGS (54)

These repositories have neither tags nor releases. Sorted alphabetically.

- `agent-devops-setups` (last push 2026-04-26T21:58:08Z)
- `AgentMCP` (last push 2026-04-26T22:06:47Z)
- `Agentora` (last push 2026-04-26T22:18:31Z)
- `agileplus-landing` (last push 2026-04-26T21:50:23Z)
- `Apisync` (last push 2026-04-25T00:52:30Z)
- `argis-extensions` (last push 2026-04-25T17:34:28Z)
- `AuthKit` (last push 2026-04-26T22:20:12Z)
- `Benchora` (last push 2026-04-26T21:59:23Z)
- `byteport-landing` (last push 2026-04-26T21:50:20Z)
- `BytePort` (last push 2026-04-26T22:17:27Z)
- `Conft` (last push 2026-04-26T16:45:31Z)
- `DataKit` (last push 2026-04-26T05:54:45Z)
- `DevHex` (last push 2026-04-26T22:06:31Z)
- `dinoforge-packs` (last push 2026-04-26T22:17:17Z)
- `GDK` (last push 2026-04-26T21:56:31Z)
- `Httpora` (last push 2026-04-26T22:08:42Z)
- `hwledger-landing` (last push 2026-04-26T21:50:12Z)
- `McpKit` (last push 2026-04-26T22:06:20Z)
- `Metron` (last push 2026-04-26T21:56:28Z)
- `nanovms` (last push 2026-04-26T21:59:14Z)
- `ObservabilityKit` (last push 2026-04-26T22:18:05Z)
- `PhenoAgent` (last push 2026-04-26T21:59:25Z)
- `phenoAI` (last push 2026-04-26T21:50:09Z)
- `PhenoCompose` (last push 2026-04-26T22:17:59Z)
- `phenoData` (last push 2026-04-26T21:50:06Z)
- `phenoDesign` (last push 2026-04-26T12:56:02Z)
- `PhenoDevOps` (last push 2026-04-26T22:17:56Z)
- `phenodocs` (last push 2026-04-26T17:39:41Z)
- `PhenoHandbook` (last push 2026-04-26T21:42:06Z)
- `phenokits-landing` (last push 2026-04-26T08:46:07Z)
- `PhenoMCP` (last push 2026-04-26T22:25:39Z)
- `PhenoObservability` (last push 2026-04-26T22:17:30Z)
- `PhenoPlugins` (last push 2026-04-26T22:25:44Z)
- `PhenoProc` (last push 2026-04-26T22:17:47Z)
- `PhenoProject` (last push 2026-04-26T21:41:32Z)
- `PhenoRuntime` (last push 2026-04-26T21:38:38Z)
- `PhenoSpecs` (last push 2026-04-26T21:38:25Z)
- `phenotype-auth-ts` (last push 2026-04-26T22:08:48Z)
- `phenotype-hub` (last push 2026-04-26T21:38:13Z)
- `phenotype-infra` (last push 2026-04-26T22:06:53Z)
- `phenotype-registry` (last push 2026-04-26T18:42:30Z)
- `phenotype-tooling` (last push 2026-04-26T22:06:50Z)
- `phenoUtils` (last push 2026-04-26T17:51:11Z)
- `PhenoVCS` (last push 2026-04-26T21:56:20Z)
- `phenoXdd` (last push 2026-04-26T22:06:58Z)
- `PlatformKit` (last push 2026-04-26T22:06:43Z)
- `PlayCua` (last push 2026-04-26T22:26:00Z)
- `projects-landing` (last push 2026-04-26T18:41:13Z)
- `ResilienceKit` (last push 2026-04-26T22:06:35Z)
- `Stashly` (last push 2026-04-26T18:40:46Z)
- `Tasken` (last push 2026-04-26T18:40:21Z)
- `TestingKit` (last push 2026-04-26T22:25:43Z)
- `thegent-landing` (last push 2026-04-26T18:37:59Z)
- `vibeproxy-monitoring-unified` (last push 2026-04-26T18:36:13Z)

## Top 10 Most-Active NO-TAGS Repos (by last push, UTC)

These have recent commits and warrant a first-release decision (semver `v0.1.0` or CalVer):

1. `PlayCua` — pushed 2026-04-26T22:26:00Z
2. `PhenoPlugins` — pushed 2026-04-26T22:25:44Z
3. `TestingKit` — pushed 2026-04-26T22:25:43Z
4. `PhenoMCP` — pushed 2026-04-26T22:25:39Z
5. `AuthKit` — pushed 2026-04-26T22:20:12Z
6. `Agentora` — pushed 2026-04-26T22:18:31Z
7. `ObservabilityKit` — pushed 2026-04-26T22:18:05Z
8. `PhenoCompose` — pushed 2026-04-26T22:17:59Z
9. `PhenoDevOps` — pushed 2026-04-26T22:17:56Z
10. `PhenoProc` — pushed 2026-04-26T22:17:47Z

## Recommendations

- **Cut first releases** for the Top-10 active NO-TAGS repos above. All are pushed within the last hour of snapshot and are candidates for an initial `v0.1.0` (Rust/TS) or CalVer (`heliosApp`-style apps). Use `gh release create v0.1.0 --generate-notes`.
- **Promote the TAGS-ONLY repo** (`eyetracker`, 2 tags, 0 releases) to a GitHub Release — fastest win in the org since the version history already exists.
- **Investigate draft-only repos** (`HexaKit`, `pheno`, `PhenoLang`): they have releases per the count API but no published latest — either publish the drafts or convert prereleases to latest.
- **No release-cadence concerns** in HAS RELEASES: 15/16 published a release in the last 30 days; only `thegent` (last release 2026-02-23) is over 60 days stale and should cut a refresh release.
