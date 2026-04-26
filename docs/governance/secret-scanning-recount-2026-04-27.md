# Secret-Scanning Re-Audit — 2026-04-27

API-only inventory across 4 leaked-secret repos. No code changes; rotation
remains a user action.

## Counts (open / resolved)

| Repo       | Open (now) | Open (prior) | Delta | Resolved |
|------------|------------|--------------|-------|----------|
| AgilePlus  | 54         | 54           | 0     | 0        |
| heliosApp  | 3          | 3            | 0     | 0        |
| PhenoKits  | 3          | 3            | 0     | 0        |
| FocalPoint | 1          | 1            | 0     | 0        |
| **TOTAL**  | **61**     | **61**       | **0** | **0**    |

## Validity=active (rotation-required)

None. The `validity=active` filter returned zero alerts across all four repos.
Either GitHub has not validated any of these alerts as live, or all leaked
secrets are inactive/expired. This is **not** a guarantee they are revoked —
GitHub validity checks only cover supported provider tokens (GitHub PATs,
AWS, Stripe, etc.) and report `unknown` for unsupported types.

## Delta vs prior audit

Zero movement. No alerts dismissed, resolved, or rotated since prior audit.
User action still pending on all 61 alerts.

## Next steps (user)

1. Triage AgilePlus 54-alert backlog (largest concentration).
2. Rotate any tokens whose `secret_type` is provider-validated.
3. Dismiss alerts only after revocation, not before.
