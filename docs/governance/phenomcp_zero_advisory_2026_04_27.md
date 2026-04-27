# PhenoMCP Zero-Advisory State (2026-04-27)

## cargo-deny Verification

**Status:** PASS (`advisories ok`)

- **Active Suppresses (3):** All LOW severity rustls-webpki advisories (RUSTSEC-2026-0098, -0099, -0104)
- **Reason:** Transitive via rustls. Fix pending in rustls-webpki 0.104.0 (alpha.7 as of 2026-04-20; stable ETA May–June 2026)
- **Re-evaluation Date:** 2026-06-01
- **Commit:** 40c7ab9 (chore: suppress 3 rustls-webpki LOW advisories pending stable 0.104.0)

**Warnings:** 3 "advisory-not-detected" — these are harmless; suppressions pre-emptively defined for the three advisories, but they're not in the current dependency closure yet (upstream hasn't reached that version).

## Dependabot Alerts

**Status:** ZERO OPEN ALERTS

- Verified via `gh api repos/KooshaPari/PhenoMCP/dependabot/alerts --paginate`
- No high/critical issues, no medium/low issues outstanding
- All previously dismissed or resolved

## Timeline

| Date | Event |
|------|-------|
| 2026-04-27 | Zero-advisory state verified; doc created |
| 2026-06-01 | Re-evaluate rustls-webpki 0.104.0 stable release; update or remove suppresses |

## Dismissal History

None in this cycle. Repository maintains zero-alert state proactively via deny.toml suppresses aligned with upstream release cadence.
