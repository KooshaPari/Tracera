# Tracera Production Deploy — Required Credentials

This document lists every credential Tracera needs for fully CI-driven
production deploys. All values are sourced from [Infisical](https://app.infisical.com)
project `<INFISICAL_PROJECT_ID>`, environment `prod`, and injected at
deploy time by `.github/workflows/deploy-*.yml`.

## Already Provisioned

| Variable / Secret         | Where stored         | Notes                                |
| ------------------------- | -------------------- | ------------------------------------ |
| `CLOUDFLARE_ACCOUNT_ID`   | GitHub repo secret   | (numeric account ID)                 |
| `WORKOS_CLIENT_ID`        | GitHub repo secret   | (WorkOS project client id)           |
| `WORKOS_API_KEY`          | GitHub repo secret   | test key, ok for staging             |
| `TRACERA_API_BASE`        | GitHub repo variable | `https://tracera.pheno.studio/api`   |
| `INFISICAL_PROJECT_ID`    | GitHub repo variable | (UUID)                               |
| `CF_ACCESS_CLIENT_ID`     | GitHub repo secret   | set by `setup-cloudflare-access.yml` |
| `CF_ACCESS_CLIENT_SECRET` | GitHub repo secret   | set by `setup-cloudflare-access.yml` |

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

| Scope   | Permission                      |
| ------- | ------------------------------- |
| Account | Workers Scripts: Edit           |
| Account | Workers KV Storage: Edit        |
| Account | Workers R2 Storage: Edit        |
| Account | Account Settings: Read          |
| Account | Workers Tail: Read              |
| Account | Access: Apps and Policies: Edit |
| Account | Access: Service Tokens: Edit    |

Set **Account Resources** to _Include → Specific account → your CF account ID_.

To unblock `tracera.pheno.studio` for CI and smoke checks, dispatch
**Setup Cloudflare Access (tracera.pheno.studio)** after the token above has
Zero Trust permissions. That workflow creates a `tracera-ci-smoke` service token,
attaches a Service Auth policy to the Access app, and stores
`CF_ACCESS_CLIENT_ID` / `CF_ACCESS_CLIENT_SECRET` in repo secrets.

```bash
gh secret set CLOUDFLARE_API_TOKEN --repo <REDACTED>/Tracera --body "<new_cf_token>"
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
gh secret set INFISICAL_TOKEN --repo <REDACTED>/Tracera --body "stk_..."
```

### 3. `VERCEL_TOKEN` (GitHub repo secret)

The token stored under this name is currently a token from a different
service. Vercel uses `vercel_…` tokens. Create one at
<https://vercel.com/account/tokens> and set:

```bash
gh secret set VERCEL_TOKEN --repo <REDACTED>/Tracera --body "vercel_..."
```

## Backend (self-hosted)

The Rust API is not deployed by CI. It runs on the operator's machine and is
exposed through a Cloudflare Tunnel. See `deploy/selfhost/README.md` for the
runbook and required environment variables (`CF_TUNNEL_TOKEN`,
`TRACERA_PUBLIC_HOSTNAME`, `TRACERA_AUTH_TOKEN`, and related settings).

CI still builds and publishes the container image (`build-push-image.yml`) to
GHCR for manual pull on the operator box.

## Graceful-Skip Behavior

`deploy-cloudflare.yml` validates token scope _before_ attempting any deploy.
If permissions are insufficient, the workflow:

1. Exits **0** (success) instead of failing the run
2. Prints the exact dashboard URL and permission list to add
3. Emits `skipped` status to make the absence of a deploy obvious
4. Does NOT block other workflows (Vercel, lint, test, coverage, etc.)

## Verifying Everything End-to-End

After replacing the tokens above:

```bash
# 1. Unblock Cloudflare Access for prod smoke + CI
gh workflow run "Setup Cloudflare Access (tracera.pheno.studio)" --repo <REDACTED>/Tracera --ref main \
  -f operator_email=you@example.com

# 2. Trigger deploys (no force needed - on main they run automatically)
gh workflow run "Deploy Cloudflare Worker (tracera-edge)" --repo <REDACTED>/Tracera --ref main
gh workflow run "Deploy Tracera to Vercel"            --repo <REDACTED>/Tracera --ref main

# 2. Watch
gh run list --repo <REDACTED>/Tracera --workflow "Deploy Cloudflare Worker (tracera-edge)" --limit 3

# 3. Verify live
# api.pheno.studio is NOT Tracera: it serves AgilePlus, so a 200 there says
# nothing about this project. Hosts per docs/04-guides/ENVIRONMENTS.md.
curl https://api.tracera.pheno.studio/healthz              # self-hosted API -> 200 {"status":"ok"}
curl -o /dev/null -w "%{http_code}\n" https://tracera.pheno.studio   # behind Cloudflare Access -> 302
curl https://tracera-kappa.vercel.app                   # dev frontend -> 200
```

## Cost Summary

| Service                                | Tier   | Cost          |
| -------------------------------------- | ------ | ------------- |
| Cloudflare Workers + KV + R2           | Free   | $0            |
| Vercel                                 | Free   | $0            |
| Self-hosted backend (operator machine) | —      | $0 marginal   |
| Domain `pheno.studio`                  | Annual | ~$10/yr       |
| **Total**                              |        | **~$10/year** |

## Files Referenced

- `.github/workflows/setup-cloudflare-access.yml` — Access service token + policy
- `.github/workflows/deploy-cloudflare.yml` — graceful-skip CF Worker deploy
- `.github/workflows/deploy-full-stack.yml` — orchestrator (frontend + edge)
- `.github/workflows/deploy-vercel.yml` — Vercel deploy
- `.github/workflows/build-push-image.yml` — GHCR image build
- `deploy/selfhost/README.md` — self-hosted backend runbook
- `wrangler.toml` — Cloudflare Worker config
- `vercel.json` — Vercel SPA config
- `Dockerfile.rust` — Backend container build
