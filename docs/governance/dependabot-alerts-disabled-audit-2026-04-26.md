# Dependabot Alerts Disabled Audit — 2026-04-26

**Method:** API-only (`gh api repos/<r>/vulnerability-alerts -i`). 204 = enabled, 404 = disabled. KooshaPari is a user account (not org); used `users/KooshaPari/repos` paginated.

## Summary

- **Total repos scanned:** 130 (all visibilities, including forks/archived)
- **Enabled (204):** 73
- **Disabled (404):** 57
  - Archived: 48 (intentionally inert — see `reference_archived_repos_locked.md`)
  - Non-archived: 9 (all forks, but recently active with real code)

No 403s observed; the tier-3 harvest "403 on dependabot/alerts" likely conflated 404 (alerts disabled) with 403 (auth/scope). Current `gh` token surfaces them as 404.

## Tier Breakdown (Disabled)

| Tier | Bucket | Count | Action |
|------|--------|-------|--------|
| T-archived | Archived repos | 48 | **Skip.** Inert per policy. |
| T-fork-active | Non-archived forks, pushed ≤2d | 9 | **Recommend enable** if we maintain divergent code. |
| T-1/T-2 canonical | Non-archived non-fork | 0 | n/a — all canonical Tier-1/2 already enabled. |

## Top-5 to Enable (non-archived, recently pushed, real code)

| name | last_push | language | criticality | recommendation |
|------|-----------|----------|-------------|----------------|
| HeliosLab | 2026-04-26 | TypeScript | T-2 (Helios family, tracked in memory) | **Enable** — active divergence, JS deps |
| helios-cli | 2026-04-26 | Rust | T-2 (Helios family) | **Enable** — Cargo.toml, active integration work |
| phenotype-ops-mcp | 2026-04-26 | Go | T-2 (Phenotype org) | **Enable** — go.mod, mcp surface |
| MCPForge | 2026-04-26 | Go | T-3 | Enable — go.mod, recently pushed |
| phenotype-omlx | 2026-04-25 | Python | T-3 | Enable — pip deps, ML surface |

Remaining 4 non-archived forks (DINOForge-UnityDoorstop, Planify, portage, vibeproxy) — judgment call; enable only if we ship from the fork.

**No auto-enable performed.** Data: `/tmp/all_status.txt`.
