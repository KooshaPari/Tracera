# Helios Family CodeQL/Scanning Triage — 2026-04-27

API-only inventory (no dismissals). Source: `gh api .../code-scanning/alerts?state=open --paginate`.

## Pre-flight

| Repo | Archived | Analysis Available |
|------|----------|-------------------|
| heliosApp | false | yes (Scorecard) |
| helios-cli | false | **no analysis (404)** |
| heliosCLI | false | yes (Trivy only) |

## Per-repo Critical+High Counts

| Repo | Critical | High | Medium | Low | Total Open | Tool(s) |
|------|---------:|-----:|-------:|----:|-----------:|---------|
| heliosApp | 1 | 19 | — | — | 86 (all sev) | Scorecard |
| helios-cli | — | — | — | — | 0 | none |
| heliosCLI | 0 | 0 | 3 | 8 | 11 | Trivy |

**No CodeQL alerts exist on any helios-family repo.** All open alerts are Scorecard (heliosApp) or Trivy (heliosCLI).

## heliosApp — Top Rule Clusters (crit+high = 20)

| Rule | Count | Severity | Notes |
|------|------:|----------|-------|
| `TokenPermissionsID` | 16 | high | Workflow files missing top-level `permissions:` block |
| `DangerousWorkflowID` | 1 | **critical** | `.github/workflows/stage-gates.yml` |
| `BranchProtectionID` | 1 | high | repo-level (no file) |
| `CodeReviewID` | 1 | high | repo-level (no file) |
| `MaintainedID` | 1 | high | repo-level (no file) |

## Vendor vs Real Split

- **Real (workflow hardening):** 17/20 in `.github/workflows/*` — all owned by KooshaPari, no vendored upstream.
- **Repo-level policy:** 3/20 (no file path) — branch protection / code review / maintenance signals.
- **Vendored `codex-rs/`:** 0. helios-cli (the codex-fork tier-1 candidate) has **no scanning analysis configured at all** — no upstream-vendor noise to filter.

## False-Positive / Low-Value Candidates

- `MaintainedID` (1) — Scorecard heuristic; repo is active (commits today). Safe noise.
- `BranchProtectionID` / `CodeReviewID` (2) — billing-blocked rulesets context (per memory `reference_billing_blocked_rules`); these reflect ruleset removal 2026-04-25, not real regressions. Re-enable post-billing.
- `TokenPermissionsID` cluster (16) — all real, mechanically fixable by adding `permissions: contents: read` top-level to each workflow. Single-PR fix.

## Recommended Action (not executed)

1. heliosApp: one PR adding default-minimal `permissions:` to 16 workflows + audit `stage-gates.yml` for the critical `DangerousWorkflowID` (likely `pull_request_target` + checkout of PR head).
2. helios-cli: enable CodeQL or document why excluded; currently zero coverage.
3. heliosCLI: 11 Trivy alerts (low/med) — separate dependency-update sweep, not in helios-family scope here.

## Tool/Stat Caveats

- Scorecard != CodeQL; original task framed as "CodeQL" but actual scanner deployment is Scorecard for heliosApp. Title preserved per request; classification corrected here.
- helios-cli `admin:repo_hook` warning surfaced; alert API still returned 404 (no setup), not auth failure for the data path.
