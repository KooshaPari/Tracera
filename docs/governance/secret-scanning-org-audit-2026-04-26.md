# Secret Scanning Audit — KooshaPari Active Repos (2026-04-26)

**Method:** API-only inventory via `gh api repos/<r>/secret-scanning/alerts?state=open --paginate`. No clones. 403/404 silenced. Inventory only — no closure or rotation.

**Scope:** 82 active (non-archived) repos in `KooshaPari` namespace.

**Result:** 4 repos with open alerts, 61 total open secret-scanning alerts. All `publicly_leaked=true`, all `validity=unknown` (GitHub could not validate live), all `push_protection_bypassed=false`.

## Per-Repo Summary

| Repo | Open Alerts | Top Secret Types | Oldest Alert | Active? |
|---|---|---|---|---|
| AgilePlus | 54 | google_api_key (16), github_oauth_access_token (16), google_oauth_access_token (14), aws_temporary_access_key_id (2), adobe_short_lived_access_token (2), workos_staging_api_key (1), mongodb_atlas_db_uri_with_credentials (1), openrouter_api_key (1), highnote_sk_test_key (1) | 2026-03-29T08:33:35Z | unknown (validity unverified) |
| heliosApp | 3 | google_api_key (3) | 2026-03-02T01:06:09Z | unknown |
| PhenoKits | 3 | google_oauth_client_id (2), google_oauth_client_secret (1) | 2026-04-23T05:37:15Z | unknown |
| FocalPoint | 1 | stripe_api_key (1) | 2026-04-24T23:10:34Z | unknown |

All 78 other active repos: 0 open alerts (or secret-scanning disabled — silenced per task constraints).

## Top Secret Types (org-wide, 61 alerts)

| Count | Secret Type |
|---|---|
| 19 | google_api_key |
| 16 | github_oauth_access_token |
| 14 | google_oauth_access_token |
| 2 | google_oauth_client_id |
| 2 | aws_temporary_access_key_id |
| 2 | adobe_short_lived_access_token |
| 1 each | workos_staging_api_key, stripe_api_key, openrouter_api_key, mongodb_atlas_db_uri_with_credentials, highnote_sk_test_key, google_oauth_client_secret |

## Source Location Notes

- **AgilePlus (54)** — All originate from browser history/research artifacts checked into the repo:
  - `data/safari/Safari Export 2026-02-19/History.json`
  - `docs/research/gemini_export.html`
  These are tokens captured in URLs the user visited (not product credentials). Still publicly leaked and individually rotatable.
- **heliosApp (3)** — google_api_key triplet from 2026-03-02 (oldest in inventory).
- **PhenoKits (3)** — google OAuth client_id + client_secret from 2026-04-23.
- **FocalPoint (1)** — stripe_api_key from 2026-04-24.

## Validity & Exposure

- `validity=unknown` for 61/61 — GitHub partner-validator did not return active/inactive. Manual verification required to determine if any are still live.
- `publicly_leaked=true` for 61/61 — all reside in public-repo blob history.
- `push_protection_bypassed=false` for 61/61 — none were pushed past an active push-protection block (most predate enablement, or repos lacked push-protection at commit time).

## Immediate-Action Items (User Decision Required)

**Treat all 61 as potentially-live until manually verified, given `validity=unknown`.**

1. **High-impact, individually verify and rotate:**
   - AgilePlus #15, #22 — `aws_temporary_access_key_id` (cloud creds)
   - AgilePlus #23 — `mongodb_atlas_db_uri_with_credentials` (DB URI with password)
   - AgilePlus #21 — `openrouter_api_key`
   - AgilePlus #2 — `workos_staging_api_key`
   - AgilePlus #1 — `highnote_sk_test_key` (test key — verify scope)
   - FocalPoint #1 — `stripe_api_key`
   - PhenoKits #1 — `google_oauth_client_secret`
2. **Bulk-revoke + reissue** the 49 google_*/github_oauth_access_token entries in AgilePlus + heliosApp:
   - Google: rotate via Google Cloud Console (API & Services → Credentials).
   - GitHub: revoke via [github.com/settings/tokens](https://github.com/settings/tokens) (OAuth tab).
3. **AgilePlus history export hygiene** — purge `data/safari/` and `docs/research/gemini_export.html` from git history (BFG / git-filter-repo) and add `.gitignore` rules to prevent re-commit. Most alerts will auto-close once the offending blobs leave reachable history.
4. **Enable push-protection** on all 4 affected repos if not already enabled (none were caught by it).

## Constraints Honored

- API-only, no clones.
- 403/404 (secret-scanning disabled) silenced.
- No alerts closed, no secrets rotated by this audit — user action required.
