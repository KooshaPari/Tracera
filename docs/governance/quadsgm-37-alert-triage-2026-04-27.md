# QuadSGM Dependabot Alert Triage — 2026-04-27

**Repo:** KooshaPari/QuadSGM (Python/HTML, created 2026-02-23, pushed 2026-04-25, NOT archived, NOT july-2025-redeye)
**Alerts open:** 37 (all `pip` ecosystem, all in `uv.lock`)
**Open Dependabot PRs:** 0 (security updates appear unconfigured or auto-dismissed)

## Severity Distribution

| Severity | Count |
|----------|-------|
| Critical | 2 |
| High     | 9 |
| Medium   | 17 |
| Low      | 9 |

## Top-5 Packages by Alert Count

| Package | Alerts | Worst Severity | Patched Version |
|---------|--------|----------------|-----------------|
| aiohttp | 10 | medium | latest 3.x |
| fastmcp | 4 | **critical** | 3.2.0 |
| authlib | 3 | **critical** | 1.6.9 |
| GitPython | 2 | high | 3.1.47 |
| cryptography | 2 | medium | latest |

## The 2 CRITICAL Alerts

1. **fastmcp** GHSA-vv7q-7jx5-f767 — FastMCP OpenAPI Provider SSRF & Path Traversal — fix `>=3.2.0`
2. **authlib** GHSA-wvwj-cvrp-7pv5 — JWS JWK Header Injection (signature bypass) — fix `>=1.6.9`

## Pyproject Constraints (all loose lower bounds — lockfile-regen safe)

```
fastmcp>=0.2.0  / fastmcp>=0.3.0   (duplicate entry — cleanup opportunity)
aiohttp>=3.9.0
langchain>=0.1.0, langchain-openai>=0.0.5
```

No upper-bound pins → `uv lock --upgrade` will resolve all CRIT/HIGH to patched.

## Decision: **LOCKFILE-REGEN**

All 37 alerts target a single `uv.lock`. Pyproject constraints permit upgrades. Single command remediation:

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/QuadSGM-wtrees/dep-lockfile-regen
uv lock --upgrade
git commit -am "chore(deps): regenerate uv.lock to clear 37 dependabot alerts (incl 2 CRIT)"
```

Expected effect:
- Closes 36/37 alerts (CRIT fastmcp + authlib, all HIGH except `lupa`, all MEDIUM/LOW)
- **Residual blocker:** `lupa` GHSA-69v7-xpr6-6gjm has no patched version published → document as suppressed-pending-upstream

## Recommended Next Action

1. Add QuadSGM to lockfile-regen batch (this commit creates the batch file).
2. Dispatch worktree subagent: `uv lock --upgrade` + verify alert closure post-push.
3. Open follow-up issue for `lupa` upstream tracking.
4. Clean up duplicate `fastmcp` constraint in `pyproject.toml` (`>=0.2.0` and `>=0.3.0` both present).
5. Enable Dependabot security updates so future regressions auto-PR (currently 0 open Dependabot PRs despite 37 alerts — config gap).
