# Stale Draft PR Audit — 2026-04-27

**Scope:** All open draft PRs across `KooshaPari` org (102 non-archived repos; 63 archived pre-filtered out).

**Method:** API-only inventory via `gh api repos/KooshaPari/<repo>/pulls?state=open` filtered by `.draft==true`.

## Result

**Total open draft PRs: 0**

| Age bucket | Count |
|------------|-------|
| < 30 days  | 0 |
| 30-90 days (stale) | 0 |
| > 90 days (abandoned) | 0 |

## Cross-checks

- `gh search prs "user:KooshaPari is:pr is:open"` → 1 open PR, but `is:draft` filter → 0.
- Per-repo verified on high-traffic repos (cliproxyapi-plusplus, heliosApp, PhenoMCP, thegent, FocalPoint, AgilePlus): all 0 drafts.
- Archived repos excluded per pre-filter spec (63 archived skipped).

## Recommendation

**No action required.** No stale or abandoned draft PRs exist in the `KooshaPari` org. The org's PR hygiene is clean — the recent loop-wave activity merges drafts promptly rather than letting them accumulate.

Re-run cadence suggestion: monthly sweep (cheap; ~5min wall-clock for 100 repos).
