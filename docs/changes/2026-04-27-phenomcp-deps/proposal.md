# PhenoMCP Dependabot Alerts — Scope & Verification (2026-04-27)

## Context

The 2026-04-26 evening push wave referenced PhenoMCP follow-up in
`docs/governance/user_decisions_runbook_2026_04_26.md` (item #10) as
"MEDIUM — 2 informational Dependabot advisories on PR #12 baseline".
W-96 cargo-deny snapshot did not include them, suggesting non-Rust
ecosystem (npm / GitHub Actions / pip).

## Live Verification (2026-04-27)

Source of truth: `gh api /repos/KooshaPari/PhenoMCP/dependabot/alerts`

| State          | Count |
|----------------|-------|
| open           | 0     |
| dismissed      | 0     |
| auto_dismissed | 0     |
| fixed          | 0     |
| **total**      | **0** |

Repository security state:
- `archived: false`
- `disabled: false`
- `dependabot_security_updates: enabled`
- `vulnerability-alerts` endpoint: enabled (no body)

## Resolution Path Already Taken

Alerts referenced in the runbook were GitHub Actions ecosystem bumps
that merged the same day as PRs:

| PR  | Bump                                  | State  |
|-----|---------------------------------------|--------|
| #7  | actions/upload-artifact 4 → 7         | MERGED |
| #8  | github/codeql-action 3 → 4            | MERGED |
| #9  | ossf/scorecard-action 2.4.2 → 2.4.3   | MERGED |
| #10 | actions/checkout 4 → 6                | MERGED |

These four merges cleared the dependabot queue. The "2 informational"
count in the runbook predates PRs #7–#10 landing.

## Categorization

| Bucket              | Count | Action       |
|---------------------|-------|--------------|
| AUTO-MERGE-READY    | 0     | n/a          |
| DEAD-DEP-CANDIDATE  | 0     | n/a          |
| NEEDS-REVIEW        | 0     | n/a          |

## Recommendation

**No-op.** Close runbook item #10. PhenoMCP has zero open Dependabot
alerts as of 2026-04-27. Re-verify on next push wave; if alerts
re-appear, file a fresh proposal at that time.

## Re-verification Command

```bash
gh api /repos/KooshaPari/PhenoMCP/dependabot/alerts \
  --jq '[.[] | select(.state=="open")] | length'
```
