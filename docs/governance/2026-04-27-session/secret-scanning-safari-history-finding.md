# Secret-scanning hits — Safari browser history export committed (2026-04-27)

## TL;DR — privacy concern, not credential leak

Both `thegent` (56 alerts) and `AgilePlus` (54 alerts) have nearly-identical secret-scanning distributions because both repos contain a committed Safari browser history export at:

```
data/safari/Safari Export 2026-02-19/History.json
```

The "secrets" GitHub flags are URL parameters from visited sites (e.g., `?key=AIza...&access_token=ya29...`) — **not real exploitable Phenotype credentials**, but **browsing-behavior privacy leak**.

## Alert distribution (identical between repos)

| Secret type | thegent | AgilePlus | Likely source |
|------------|---------|-----------|---------------|
| github_oauth_access_token | 17 | 16 | URL params from GH OAuth flows visited |
| google_api_key | 16 | 16 | URL params (Google Maps/Search/etc.) |
| google_oauth_access_token | 14 | 14 | OAuth callback URLs in browsing |
| openrouter_api_key | 2 | 1 | API testing? |
| aws_temporary_access_key_id | 2 | 2 | AWS console URLs |
| adobe_short_lived_access_token | 2 | 2 | |
| workos_staging_api_key | 1 | 1 | |
| mongodb_atlas_db_uri_with_credentials | 1 | 1 | |
| highnote_sk_test_key | 1 | 1 | |

## What's NOT Safari history (real credentials in repo)

- **AgilePlus alert #1**: `apps/byteport/backend/.env:40` — Highnote `sk_test_*` key (test/sandbox tier — low blast radius but should rotate)
- **AgilePlus alert #2**: same `.env` file — WorkOS staging API key
- **AgilePlus alert #3**: `docs/research/gemini_export.html` — Google API key in saved Gemini chat export

These three need: (a) rotate the keys (test keys can still leak business structure), (b) remove the files from the repo, (c) add `.env` and `*_export.html` to `.gitignore`.

## Recommended actions (USER DECISION REQUIRED)

**Option A — Privacy-first (recommended):**
1. Remove `data/safari/Safari Export 2026-02-19/` from both repos via history-rewrite (BFG / git filter-repo).
2. Force-push (destructive — needs your approval).
3. Add `data/safari/` to `.gitignore` in both repos.
4. After history rewrite, dismiss all 110 alerts as `false_positive` (URL params not exploitable Phenotype creds).
5. Audit thegent for any other Safari/Chrome/Firefox export files.

**Option B — Dismiss-only (risk: history persists publicly):**
1. Just dismiss the 110 alerts as `false_positive` with comment "browser history URL params, not Phenotype credentials".
2. The committed file remains in git history — anyone cloning sees your browsing.

**Option C — Investigate first:**
1. Audit `apps/byteport/backend/.env:40` (AgilePlus alert #1) — is that a real Phenotype/AWS/Google credential? If yes, **rotate immediately** before anything else.

## NOT autonomously actioned

This finding requires human decision because:
- History rewrites are destructive
- The `.env:40` alert may be a real credential needing rotation
- Privacy implications go beyond automated alert hygiene

## Detection commands used

```bash
# Distribution check (revealed identical pattern)
gh api /repos/KooshaPari/thegent/secret-scanning/alerts?state=open --paginate --jq '.[].secret_type' | sort | uniq -c
gh api /repos/KooshaPari/AgilePlus/secret-scanning/alerts?state=open --paginate --jq '.[].secret_type' | sort | uniq -c

# Location sample (revealed Safari history)
gh api /repos/KooshaPari/thegent/secret-scanning/alerts/56/locations --jq '.[0].details.path'
# → "data/safari/Safari Export 2026-02-19/History.json"
```
