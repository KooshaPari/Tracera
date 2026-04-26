# Scorecard PinnedDependenciesID — Org Sweep (2026-04-27)

**Scope:** API-only audit of all 82 non-archived KooshaPari repos via
`gh api .../code-scanning/alerts?state=open` filtered on
`rule.id == "PinnedDependenciesID"`.

## Headline numbers

- **Total open alerts:** 1,442
- **Affected repos:** 48 / 82 (58.5%)
- **Distribution:** 50+ alerts: 13 repos · 10–49: 18 · 1–9: 17 · 0: 34
- **Concentration:** top 10 repos = 791 alerts (54.9% of total)

## Top 10 by alert count

| Rank | Repo | Alerts |
|------|------|-------:|
| 1 | cliproxyapi-plusplus | 126 |
| 2 | Planify | 94 |
| 3 | Dino | 88 |
| 4 | PolicyStack | 83 |
| 5 | Tokn | 76 |
| 6 | FocalPoint | 74 |
| 7 | heliosApp | 64 |
| 8 | Stashly | 61 |
| 8 | argis-extensions | 61 |
| 8 | agentapi-plusplus | 61 |

Sampled paths (top-5) confirm alerts are concentrated in `.github/workflows/*.yml`
(security-guard, sast, quality-gate, traceability, build-lint, asset-pipeline).
No `action.yml`/composite hits in samples — pure workflow `uses:` unpinned tags.

## SHA-pinned reference pattern

No third-party SHA-pinned action found in scanned zero-alert repos (zero counts
are mostly "no workflows" or "code-scanning disabled", not "already pinned").
Only internal reusable callout SHA-pin observed:
`AgilePlus/.github/workflows/alert-sync-issues.yml`
→ `uses: KooshaPari/phenoShared/.github/workflows/reusable/alert-sync-issues.yml@5e6c1f05...`

**Implication:** there is no in-org canonical pattern to copy; the standard
`step-security/secure-repo` pin-bot or a `pin-github-action` codemod is the
correct one-shot remediation tool.

## 1-PR-per-repo strategy

Single PR per repo running `step-security/secure-repo` (or
`mheap/pin-github-action`) over `.github/workflows/*.yml` to convert
`uses: org/action@vN` → `uses: org/action@<40-char-sha>  # vN`.

## Suggested 3-PR test batch

Pick mid-volume + structurally diverse to validate:

1. **FocalPoint** (74) — Rust workspace, multi-workflow
2. **PolicyStack** (83) — quality-gate-heavy, recent v0.1.0 release
3. **agentapi-plusplus** (61) — fork of upstream, pin discipline matters most

If all three merge clean and Scorecard recounts to ~0 PinnedDeps for those
repos, scale to remaining 45 affected repos in a single dispatch wave.

## Next batch after test (top concentration)

cliproxyapi-plusplus, Planify, Dino, Tokn, heliosApp, Stashly,
argis-extensions, Tasken, nanovms, vibeproxy → ~700 alerts cleared.

**Source data:** `/tmp/pinned_counts.txt` (82 lines, format `<count> <repo>`).
