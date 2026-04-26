# Org Pages Enablement — 2026-04-27

## Summary

Enabled GitHub Pages (workflow source, `main` branch) on three product repos
that already had `actions/deploy-pages@v4` workflows committed but no Pages
origin. Source script: `scripts/enable_org_pages_2026_04_26.sh` (commit
`353f2d777b`).

## Per-Repo Results

| Repo | API Status | html_url | build_type | source |
|------|------------|----------|------------|--------|
| FocalPoint | 201 Created | https://kooshapari.github.io/FocalPoint/ | workflow | main:/ |
| PolicyStack | 201 Created | https://kooshapari.github.io/PolicyStack/ | workflow | main:/ |
| Tokn | 201 Created | https://kooshapari.github.io/Tokn/ | workflow | main:/ |

All three returned non-error JSON with `https_enforced: true`, `public: true`,
and `build_type: workflow`. No 422 ("already enabled") responses — these were
fresh enablements.

## Cloudflare Subdomain State (post-enable)

| Subdomain | Status |
|-----------|--------|
| https://focalpoint.kooshapari.com | HTTP/2 530 (expected, first build pending) |
| https://policystack.kooshapari.com | HTTP/2 530 (expected, first build pending) |
| https://tokn.kooshapari.com | HTTP/2 530 (expected, first build pending) |

The 530 response chain (CF -> origin) will clear once:

1. The Pages workflow completes its first build on `main` (~2-5 min wall clock).
2. GitHub provisions the Pages origin and serves a 200 from
   `kooshapari.github.io/<repo>/`.
3. Cloudflare's proxied CNAME resolves the new origin.

## What The User Should Expect

- First build kicks off automatically when the next push to `main` triggers the
  workflow, OR can be triggered manually via `gh workflow run` per repo.
- Wall-clock to live: ~2-5 minutes per repo after the workflow run starts.
- If subdomain CNAME is set in repo Pages settings (custom domain), CF must
  match `kooshapari.github.io` as the proxied target with SSL/TLS = Full.
- Verify cleared state: `curl -sI https://<subdomain>.kooshapari.com` returns
  HTTP/2 200 (not 530).

## Remaining Cohort

Per `org_pages_status_2026_04_26_late.md`:

- **HeliosLab** — uses `peaceiris/actions-gh-pages` (gh-pages branch flow);
  needs migration to `actions/deploy-pages` OR enable with `gh-pages` source.
- **KDesktopVirt** — scaffold committed 2026-04-26; ready to enable once that
  commit lands on `origin/main`.

## Related

- Audit source: `org_pages_status_2026_04_26_late.md` (commit `d954227f6d`).
- Enablement script: `scripts/enable_org_pages_2026_04_26.sh`.
- Cloudflare proxy fix cohort (Tracera, heliosApp) — separate workstream; not
  covered here.
