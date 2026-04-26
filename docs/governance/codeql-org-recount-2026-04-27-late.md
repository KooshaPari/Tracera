# CodeQL Org-Wide Alert Recount — 2026-04-27 (late)

**Method:** API-only via `gh api repos/KooshaPari/<r>/code-scanning/alerts?state=open` across 82 non-archived repos, parallelized.

## Org Totals (open alerts)

| Severity | Current | Prior   | Delta  |
|----------|--------:|--------:|-------:|
| Critical |      23 |      56 |    -33 |
| High     |     798 |   1,006 |   -208 |
| Medium   |   1,674 |   1,797 |   -123 |
| Low      |     138 |     142 |     -4 |
| None/null|     264 |     222 |    +42 |
| **Total**|**2,897**|**3,223**| **-326** |

Critical+High dropped 241 (1,062 → 821, -22.7%). Total -10.1%. The "none/null" rise (+42) reflects new alerts without a `security_severity_level` (e.g., quality rules) — not regressions on severity-rated findings.

## Top-10 Repos by Critical+High

| Rank | Repo                  | Crit+High | Total |
|-----:|-----------------------|----------:|------:|
| 1 | thegent                  | 288 | 383 |
| 2 | cliproxyapi-plusplus     |  55 | 406 |
| 3 | Tokn                     |  26 | 107 |
| 4 | PolicyStack              |  21 | 107 |
| 5 | agentapi-plusplus        |  20 |  92 |
| 6 | Stashly                  |  17 |  83 |
| 7 | Dino                     |  17 |  21 |
| 8 | Tasken                   |  16 |  75 |
| 9 | Planify                  |  16 | 117 |
|10 | PhenoProc                |  15 |  25 |

## Notes

- 82 repos scanned; per-repo TSV cached at `/tmp/codeql_recount/summary.tsv`.
- `thegent` remains primary High concentration (275 high / 13 critical).
- `cliproxyapi-plusplus` carries the largest unrated bucket (222 none/null) — expected from quality rules; security severity load is moderate.
