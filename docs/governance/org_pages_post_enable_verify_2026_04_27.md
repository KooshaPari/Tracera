# GitHub Pages Post-Enable Verification — 2026-04-27

**Status:** Builds NOT yet live (GH Pages 404/301; CF 530). Deployments pending or failed.

## Summary

Five repos enabled GitHub Pages today (FocalPoint, PolicyStack, Tokn, KDesktopVirt, HeliosLab). Verification 2+ hours later shows:
- All GitHub Pages URLs return **404 or 301** (not 200)
- All Cloudflare subdomains return **530** (Bad Gateway — upstream not available)
- **HeliosLab** is the only exception: Pages config shows `status: "built"` with `gh-pages` branch source (legacy mode, pre-existing)

## Per-Domain Status

### FocalPoint
- **CF Status**: 530 (Bad Gateway)
- **GH Status**: 404 Not Found
- **Pages Config**: `status: null`, `build_type: "workflow"`, source: `main:/`
- **Issue**: Build type set to workflow, but no Pages deployment workflow has run yet
- **Category**: GH-BUILD-PENDING

### PolicyStack
- **CF Status**: 530 (Bad Gateway)
- **GH Status**: 404 Not Found
- **Pages Config**: `status: null`, `build_type: "workflow"`, source: `main:/`
- **Workflow File**: `pages-deploy.yml` exists
- **Issue**: Build workflow may not have triggered; no recent run detected
- **Category**: GH-BUILD-PENDING

### Tokn
- **CF Status**: 530 (Bad Gateway)
- **GH Status**: 404 Not Found
- **Pages Config**: `status: null`, `build_type: "workflow"`, source: `main:/`
- **Workflow File**: MISSING (no `pages-deploy.yml`)
- **Issue**: No Pages deployment workflow configured; manual trigger or workflow file needed
- **Category**: GH-MISSING-WORKFLOW

### KDesktopVirt
- **CF Status**: 530 (Bad Gateway)
- **GH Status**: 404 Not Found
- **Pages Config**: `status: null`, `build_type: "workflow"`, source: `main:/`
- **Workflow File**: `pages-deploy.yml` exists
- **Issue**: Build workflow may not have triggered; no recent run detected
- **Category**: GH-BUILD-PENDING

### HeliosLab
- **CF Status**: 530 (Bad Gateway)
- **GH Status**: 301 Redirect (to root)
- **Pages Config**: `status: "built"`, `build_type: "legacy"`, source: `gh-pages:/`
- **Issue**: Pages already configured on pre-existing `gh-pages` branch; not a fresh enable today
- **Category**: PRE-EXISTING-BUILD (not part of today's 5)

## Root Causes

1. **Workflow Trigger Not Fired**: Pages settings point to `main` branch, `build_type: "workflow"`, but no GitHub Actions Pages deployment workflow has been invoked. GitHub Pages "workflow" build type requires a manual trigger or push event to fire a workflow.

2. **Missing Workflow File (Tokn)**: Tokn does not have a Pages deployment workflow at all.

3. **Cloudflare DNS Routing**: All CF subdomains return 530 because GitHub Pages origins (which should be behind the CF proxy) are returning 404/301. CF cannot proxy a failed upstream.

## Next Steps

### For Each Repo (except HeliosLab)

1. **Ensure Pages deployment workflow exists**: Copy `pages-deploy.yml` from PolicyStack or KDesktopVirt to Tokn.
2. **Trigger workflow manually**: Push a commit to `main` or manually trigger the workflow via `gh workflow run`.
3. **Wait for build**: GitHub Pages build should show `status: "built"` within 2-5 minutes.
4. **Verify GH origin**: Confirm `https://kooshapari.github.io/<repo>` returns 200.
5. **CF automatic proxy**: Once GH origin is 200, CF will proxy it and subdomains will return 200.

### Timeline Expectation

- Workflow trigger: <1 min (manual)
- Build completion: 2-5 min
- CF cache invalidation: ~2 min
- Total to live: ~5-10 min per repo

## Deployment Branch Policy Note

All 5 repos have environment protection rules with `custom_branch_policies: true` (i.e., deployments restricted to specific branches). Verify the GitHub Pages environment allows deployments from `main` (or the source branch configured in Pages settings).

## HeliosLab Clarification

HeliosLab was NOT part of today's fresh enable — it has a pre-existing `gh-pages` branch and Pages was already configured in legacy mode. The "301 Redirect" GH Pages response may be working (redirecting to the versioned or real index), but CF cannot reach it because downstream docs build may be incomplete. Check HeliosLab `docs/.vitepress/config.ts` for build output path.
