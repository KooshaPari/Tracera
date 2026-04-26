# Dependabot Org Recount — 2026-04-27 (late)

**Method:** API-only via `gh api repos/<r>/dependabot/alerts?state=open`. Scope: top 50 active non-archived KooshaPari repos by `pushed`. 49/50 returned data; 1 (`vibeproxy`) has Dependabot disabled.

## Org-wide open severity totals

| Severity | Count |
|----------|-------|
| Critical | **4** |
| High     | **94** |
| Medium   | 149 |
| Low      | 55 |
| **Total**| **302** |

Critical alerts located in: `PhenoLang` (2), `heliosCLI` (1), `pheno` (1).

## Top-10 repos by critical+high

| Rank | Repo | Crit+High |
|------|------|-----------|
| 1 | thegent | 25 |
| 2 | heliosCLI | 23 |
| 3 | PhenoProject | 15 |
| 4 | PhenoLang | 10 |
| 5 | pheno | 7 |
| 6 | agentapi-plusplus | 6 |
| 7 | Tracera | 5 |
| 8 | hwLedger | 3 |
| 9 | PlatformKit | 1 |
| 10 | phenotype-ops-mcp | 1 |

## Deltas vs previous CodeQL audit (W-93 cargo-deny snapshot, 205 alerts org-wide)

- Total open alerts **302** (this scan, 49 repos) vs prior W-93 governance loop ~205. **+97** delta — plausibly explained by Dependabot picking up new advisories post-merge waves (lockfile commits unblocked re-scan) rather than fresh introductions.
- **Criticals: 4** — small but non-zero. PhenoLang gained a critical pair (W-93 had it under "residual"); heliosCLI + pheno each show one new critical worth surfacing.
- High concentration unchanged: thegent + heliosCLI continue to dominate (48/94 highs = 51%).
- BytePort (16 total) and PhenoRuntime (6) appear higher than W-93 expectations — recent dep additions likely.

## Action items

1. Triage 4 criticals immediately (`PhenoLang` x2, `heliosCLI`, `pheno`).
2. thegent + heliosCLI need a focused dep-bump wave; combined 76 medium+ alerts.
3. Enable Dependabot on `vibeproxy` or document exemption.

Source data: `/tmp/depcount/all.txt` (50 repos, parallel API pull, <60s wall clock).
