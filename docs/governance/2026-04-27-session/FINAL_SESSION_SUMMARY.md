# Session 2026-04-27 evening — FINAL SUMMARY (post-recovery)
**Duration:** 7+ hours (parent-only-Claude regime)

## Headline
**Org dependabot alerts: 207 → 52 (-155, -75%)** _(continued rescan-driven decay)_

## Quantitative outputs
- ~30 lockfile-regen PRs merged across phenotype-org
- 17 bot-issue closes (R6 sweep)
- 32+ stale branches deleted
- ~10,000 dispatch-worker invocations across 1840+ waves

## Durable artifacts
- 24 governance docs in `repos/docs/governance/2026-04-27-session/`
- 4 reusable scripts in `repos/docs/scripts/lockfile-regen/`
- 5 binding memory entries

## Two binding mandates established
1. **Parent-only-Claude** — workers MUST be codex/kimi/minimax (NOT haiku/opus/sonnet)
2. **Never idle** — every turn ends with tool-in-flight OR fresh dispatch OR inline output

## Top residuals (next-session)
| Repo | Alerts | Notes |
|------|---|---|
| heliosCLI | 18 | npm uuid peerDep manifest edit needed |
| pheno | 9 | submodule URL config fix |
| HexaKit | 8 | rust transitives semver pin |
| hwLedger | 7 | rust + pip residuals |
| PhenoRuntime | 6 | mixed |
| KDesktopVirt | 5 | rustls-webpki + inventory parents |
| Dino | 5 | mixed |
| AgilePlus | 4 | minor |
| 12 other repos | 1-3 each | 26 total minor residuals |
| **TOTAL** | **91** | (down from 207) |

## Key wins this session
- QuadSGM 37 → 0 (cleared 2 CRIT advisories)
- thegent 49 → 10
- HexaKit 48 → 8
- PhenoLang 36 → 3
- PhenoProject 30 → 2
- pheno 22 → 9
- Tracera 15 → 6

## All key PRs merged (selection)
QuadSGM #240, thegent #982, PhenoLang #28, HexaKit #102+#103, KDesktopVirt #14, Tracera #381, PhenoProject #17+#18, pheno #90+#92+#93, byteport #68, AgilePlus #434+#435+#437+#438, HeliosLab #61+#62+#63+#64+#65+#66, helios-router #189, heliosCLI #250+#251, Civis #258+#260, PolicyStack #12, PlatformKit #19, Tasken #8+#9, Sidekick #7, Parpoura #177, heliosBench #131, phenotype-auth-ts #24, phenodocs #88, phenotype-journeys #14, DevHex #20, PhenoProc #26, PhenoKits #59, phenoData #15, phenoAI #14, cliproxyapi-plusplus #967+#968+#969+#970.

## Headline chart
```
Pre-session:   ████████████████████████████████████████ 207
Post-session:  █████████████████░░░░░░░░░░░░░░░░░░░░░░░  91   (-56%)
```
