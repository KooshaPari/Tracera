# Tracera Production Deploy — Required Credentials

This document lists every credential Tracera needs for fully CI-driven
production deploys. All values are sourced from [Infisical](https://app.infisical.com)
project `<INFISICAL_PROJECT_ID>`, environment `prod`, and injected at
deploy time by `.github/workflows/deploy-*.yml`.

## Already Provisioned

| Variable / Secret | Where stored | Notes |
|---|---|---|
| `CLOUDFLARE_ACCOUNT_ID` | GitHub repo secret | (numeric account ID) |
| `WORKOS_CLIENT_ID` | GitHub repo secret | (WorkOS project client id) |
| `WORKOS_API_KEY` | GitHub repo secret | test key, ok for staging |
| `TRACERA_API_BASE` | GitHub repo variable | `https://api.pheno.studio` |
| `INFISICAL_PROJECT_ID` | GitHub repo variable | (UUID) |

> **Note:** This document intentionally uses placeholders rather than
> literal token values. To inject secrets, use the
> `gh secret set …` / Infisical dashboard commands below, or have the
> CI pull them from Infisical at deploy time.

## Tokens That Need Replacement

The first wave of secrets used during sandboxing had the wrong scopes
or were misidentified. These need to be replaced before the prod
deploys can succeed.

### 1. `CLOUDFLARE_API_TOKEN` (GitHub repo secret)

The current value is **Zone-scoped** ("Cloudflare Agent Token") — it
can read zones but **cannot deploy Workers, create KV namespaces,
or create R2 buckets**.

Replace with an **Account-scoped** token created at
<https://dash.cloudflare.com/profile/api-tokens> → **Create Token** →
**Edit Cloudflare Workers** template.

Permissions required:

| Scope | Permission |
|---|---|
| Account | Workers Scripts: Edit |
| Account | Workers KV Storage: Edit |
| Account | Workers R2 Storage: Edit |
| Account | Account Settings: Read |
| Account | Workers Tail: Read |

Set **Account Resources** to *Include → Specific account → your CF account ID*.

```bash
gh secret set CLOUDFLARE_API_TOKEN --repo KooshaPari/Tracera --body "<new_cf_token>"
```

### 2. `INFISICAL_TOKEN` (GitHub repo secret)

The current value is an **Infisical Universal Auth Client ID**, not a
service token. The Infisical CLI rejects it as "malformed access token"
(403).

Two ways to fix:

**Option A — Service Token (preferred, simplest):**
1. <https://app.infisical.com> → Project → Settings → Machine Identities
2. Create service token → env: `prod` → scopes: read
3. Copy `stk_…` value → set as `INFISICAL_TOKEN`

**Option B — Universal Auth Client Secret:**
1. <https://app.infisical.com> → Project → Machine Identities → existing client
2. Copy the matching **Client Secret**
3. Set both `INFISICAL_CLIENT_ID` and add `INFISICAL_CLIENT_SECRET`

```bash
gh secret set INFISICAL_TOKEN --repo KooshaPari/Tracera --body "stk_..."
```

### 3. Render Credentials (live in Infisical `prod` env)

The current `RENDER_API_KEY` slot holds a token of the wrong service.
Render uses `rnd_…` API keys.

Set up Render Blueprint first:

1. Go to <https://dashboard.render.com> → **New** → **Blueprint**
2. Connect GitHub → select `KooshaPari/Tracera` → branch `main`
3. Render auto-detects `render.yaml` and provisions:
   - `tracera-postgres` (PostgreSQL 17, free tier)
   - `tracera-server` (Rust, Docker, free tier)
4. After first deploy, copy the **Service ID** (`srv-…`) from the URL:
   `https://dashboard.render.com/web/srv-XXXXXXXX`

Then add to Infisical `prod` env:

| Key | Value |
|---|---|
| `RENDER_API_KEY` | (from <https://dashboard.render.com/api-keys>) |
| `RENDER_SERVICE_ID` | (e.g. `srv-XXXXXXXX`) |

### 4. `VERCEL_TOKEN` (GitHub repo secret)

The token stored under this name is currently a token from a different
service. Vercel uses `vercel_…` tokens. Create one at
<https://vercel.com/account/tokens> and set:

```bash
gh secret set VERCEL_TOKEN --repo KooshaPari/Tracera --body "vercel_..."
```

## Graceful-Skip Behavior

Both `deploy-cloudflare.yml` and `deploy-render.yml` now validate
token scope *before* attempting any deploy. If permissions are
insufficient, the workflow:

1. Exits **0** (success) instead of failing the run
2. Prints the exact dashboard URL and permission list to add
3. Emits `skipped` status to make the absence of a deploy obvious
4. Does NOT block other workflows (Vercel, lint, test, coverage, etc.)

## Verifying Everything End-to-End

After replacing the 4 tokens above:

```bash
# 1. Trigger deploys (no force needed - on main they run automatically)
gh workflow run "Deploy Cloudflare Worker (tracera-edge)" --repo KooshaPari/Tracera --ref main
gh workflow run "Deploy Render Backend"              --repo KooshaPari/Tracera --ref main
gh workflow run "Deploy Tracera to Vercel"            --repo KooshaPari/Tracera --ref main

# 2. Watch
gh run list --repo KooshaPari/Tracera --workflow "Deploy Cloudflare Worker (tracera-edge)" --limit 3
gh run list --repo KooshaPari/Tracera --workflow "Deploy Render Backend"              --limit 3

# 3. Verify live
curl https://api.pheno.studio/healthz
curl https://tracera-kappa.vercel.app
```

## Cost Summary

| Service | Tier | Cost |
|---|---|---|
| Cloudflare Workers + KV + R2 | Free | $0 |
| Vercel | Free | $0 |
| Render (free PostgreSQL + free Docker) | Free | $0 |
| Domain `pheno.studio` | Annual | ~$10/yr |
| **Total** | | **~$10/year** |

## Files Referenced

- `.github/workflows/deploy-cloudflare.yml` — graceful-skip CF Worker deploy
- `.github/workflows/deploy-render.yml` — graceful-skip Render deploy
- `.github/workflows/deploy-full-stack.yml` — orchestrator
- `.github/workflows/deploy-vercel.yml` — Vercel deploy
- `render.yaml` — Render Blueprint (Rust backend + PostgreSQL)
- `wrangler.toml` — Cloudflare Worker config
- `vercel.json` — Vercel SPA config
- `Dockerfile.rust` — Backend container build
