# Tracera Dependabot Vulnerability Sweep — 2026-04-26

## Summary

Tracera repository scan completed on 2026-04-26. Total: **28 open Dependabot alerts** across 5 severity tiers.

| Severity | Count | Packages |
|----------|-------|----------|
| Critical | 2 | libxmljs2 |
| High | 11 | GitPython, PyJWT, chromedriver, docker, grunt, ray |
| Medium | 14 | Mako, authlib, chromedriver, esbuild, docker, grunt, pip, pytest, python-dotenv, python-multipart, srvx |
| Low | 1 | Pygments |

## Critical Alerts (Action Required)

### libxmljs2 (2 alerts)
- **GHSA-78h3-pg4x-j8cv** — No patched version available; node dependency
- **GHSA-mjr4-7xg5-pfvh** — No patched version available; node dependency

**Status:** Requires manual review. Check if libxmljs2 is actively maintained or if replacement library is needed.

## High-Severity Alerts (Action Required)

| Package | Count | GHSAs | Fix |
|---------|-------|-------|-----|
| GitPython | 2 | GHSA-x2qx-6953-8485, GHSA-rpm5-65cw-6hj4 | 3.1.47 |
| PyJWT | 1 | GHSA-752w-5fwx-jx9f | 2.12.0 |
| ray | 1 | GHSA-mw35-8rx3-xf9r | 2.55.0 |
| grunt | 2 | GHSA-rm36-94g8-835r, GHSA-m5pj-vjjf-4m3h | 1.5.3, 1.3.0 |
| chromedriver | 2 | GHSA-jh5w-6964-x5cf (×2) | 2.25.2 |
| docker | 3 | GHSA-x744-4wpc-v9h2 (×3) | No patch available |

**Status:** Most have patch versions available. Await Dependabot PRs or apply manually.

## Medium & Low Alerts

14 medium + 1 low severity. Patch versions exist for all medium-severity items (python-dotenv, pytest, Mako, authlib, esbuild, srvx). Docker also has medium-severity duplicate (no patch).

## Ecosystem Breakdown

- **Python (pip)**: 17 alerts (GitPython, ray, PyJWT, python-dotenv, authlib, Mako, python-multipart, pytest, Pygments)
- **Node.js (npm)**: 9 alerts (libxmljs2 critical, esbuild, grunt, chromedriver)
- **Go (mod)**: 2 alerts (docker/docker high + medium duplicates)

## PR Status

**Existing Dependabot PRs:** 0 open

No pull requests have been auto-opened by Dependabot. This may indicate:
1. Dependabot is not enabled for all package managers
2. Alerts are newly discovered or in manual review queue

## Next Steps

1. **Enable Dependabot for all ecosystems** if not already done (Settings → Code security → Dependabot).
2. **libxmljs2 critical alerts:** Evaluate if replacement is possible (e.g., xmljs, xml2js alternatives).
3. **docker/docker high severity:** Check if Tracera's docker usage can be upgraded or if workarounds exist.
4. **Other high/medium:** Merge Dependabot PRs as they arrive (expected within 24–48 hours of scan).
5. **Schedule weekly triage:** Set a reminder to review new alerts as they surface.

## Scan Details

- **Repository:** KooshaPari/Tracera
- **Scan Date:** 2026-04-26
- **Filter:** state=open, all severity levels
- **Tool:** GitHub Dependabot API
