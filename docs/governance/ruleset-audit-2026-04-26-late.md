# Branch Protection Ruleset Audit — KooshaPari Org (API-only)

**Date:** 2026-04-26 (late)
**Method:** `gh api` only — no clones, no mutations.
**Scope:** 82 active (non-archived) repos under user `KooshaPari`.

## Headline Numbers

- **82** active repos audited.
- **68** repos: NO ruleset (open-merge — relies on local hooks for guardrails).
- **14** repos: at least one ruleset present.
- **7** repos: ruleset enforces `pull_request.required_approving_review_count >= 1` ("review-blocked").
- **1** repo (phenoShared): review_count=0 in API but blocks admin-merge due to **User-scoped bypass** instead of `RepositoryRole:always` (anomaly — see below).

## Review-Blocked Repos (review_count=1)

| Repo | Ruleset | Extra Rules | Bypass |
|---|---|---|---|
| AgilePlus | Main Governance Baseline | deletion, non-FF, PR | RepositoryRole:always |
| BytePort | Main | deletion, non-FF, PR | RepositoryRole:always |
| cliproxyapi-plusplus | Main | + code_quality, copilot_code_review | RepositoryRole:always |
| helios-cli | Main | + code_quality, copilot_code_review | RepositoryRole:always |
| heliosApp | Main Governance Baseline | + required_status_checks | RepositoryRole:always |
| heliosCLI | Main | + code_quality | RepositoryRole:always |
| thegent | Main | deletion, non-FF, PR | RepositoryRole:always |

All 7 have `RepositoryRole:always` bypass — admin/`gh pr merge --admin` should succeed. If billing-blocked CI is also `required_status_checks` (heliosApp), strip that requirement first.

## phenoShared Anomaly

`phenoShared` ruleset id `14279307` uses `bypass_actors=[User:always]` (User-scoped) rather than RepositoryRole. This is the root cause of the previously-observed "review-required-blocked" pattern. **Fix:** swap bypass actor to RepositoryRole=Maintain/Admin, OR add the operating user explicitly.

## Other Active-but-Not-Review-Blocked

`agent-devops-setups`, `agentapi-plusplus`, `HeliosLab`, `Tracera` — rulesets present, review_count=0; cosmetic only.

`heliosBench`, `portage` — empty/null rulesets returned; likely created blank.

## Suggested Next Steps

1. **phenoShared:** PATCH ruleset 14279307 — change bypass to `{actor_type: RepositoryRole, actor_id: 5, bypass_mode: always}` (Admin role).
2. **heliosApp:** drop `required_status_checks` rule (billing-blocked CI cannot satisfy).
3. **Review-blocked 7:** confirm `gh pr merge --admin` works; if not, audit token scope (`admin:repo`).
4. **68 ruleset-less repos:** acceptable per "local hooks compensate" policy (ref: `reference_billing_blocked_rules.md`); no action.
5. **heliosBench/portage:** delete empty rulesets to reduce noise.

## Raw Data

`/tmp/ruleset_audit/results.tsv` (82 rows; regenerate via inventory script in this audit).
