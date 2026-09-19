# Environments: triggers, gating, and DNS

One rule drives everything here: **a push to `main` is never a production
deploy.** Production moves only on a release tag, and every environment has its
own hostname so a URL always identifies which system you are talking to.

## The model

| Environment | Trigger                                                              | GitHub environment                                                  | Approval           | Purpose                                            |
| ----------- | -------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------ | -------------------------------------------------- |
| `preview`   | `pull_request` against `main` (`deploy-vercel`, `deploy-cloudflare`) | `vercel-preview` / `cloudflare-preview`                             | none               | Per-PR build, reaches a non-production backend     |
| `dev`       | push to `main`; nightly `schedule`                                   | `vercel-dev` / `render-dev` / `cloudflare-dev`                      | none               | Continuous delivery and the nightly validation run |
| `prod`      | push of a `v*` tag; `workflow_dispatch` with `environment: prod`     | `vercel-production` / `render-production` / `cloudflare-production` | required reviewers | Public production                                  |

`workflow_dispatch` takes an explicit `environment` input (`dev`, `preview`,
`prod`) defaulting to `dev`, so a manual run never lands in production by
accident.

`deploy-render`, `deploy-vercel` and `deploy-cloudflare` each derive that
environment in a single `plan` job from the event and pass it on, rather than
re-deriving it per step. `deploy-full-stack` has no `plan` job of its own; it
forwards its `environment` input to the three workflows it calls, so a dispatch
asking for `prod` reaches the backend and frontend as `prod` instead of falling
through to `dev`:

| Event                                      | Derived environment     |
| ------------------------------------------ | ----------------------- |
| `pull_request`                             | `preview`               |
| ref starts with `refs/tags/`               | `prod`                  |
| `workflow_dispatch`                        | the `environment` input |
| anything else (push to `main`, `schedule`) | `dev`                   |

## DNS and hostnames

Each environment owns a distinct hostname. Verified against the live services;
re-verify before relying on any of it.

| Environment       | Frontend                                                           | API                                       | Edge worker                                             |
| ----------------- | ------------------------------------------------------------------ | ----------------------------------------- | ------------------------------------------------------- |
| `prod`            | `https://tracera.pheno.studio` (Cloudflare Access)                 | `https://tracera.pheno.studio/api`        | `https://tracera-edge.pheno.studio` (not attached, 530) |
| `prod` (fallback) | `https://tracera-kappa.vercel.app` (Vercel production alias, stub) | `https://tracera-server.onrender.com`     | `https://tracera-edge.kooshapari.workers.dev`           |
| `dev`             | per-deploy Vercel URL, behind Vercel Authentication                | `https://tracera-server-dev.onrender.com` | `https://tracera-edge-dev.kooshapari.workers.dev`       |
| `preview`         | per-deploy Vercel URL, behind Vercel Authentication                | same as `dev` (no separate service)       | `https://tracera-edge-preview.kooshapari.workers.dev`   |

Three corrections to what this table used to say, each observed rather than
assumed:

- **`tracera-kappa.vercel.app` is the Vercel _production_ alias, not dev.** The
  deploy log says so directly: `To deploy to production (tracera-kappa.vercel.app),
run 'vercel --prod'`. A push to `main` deploys a _preview_, so this alias keeps
  serving the last production deployment until a `v*` tag is pushed.
- **It served a placeholder, not the app.** The body was the tracked repo-root
  `public/index.html` ("Frontend scaffolding coming soon."), 157 bytes. That file
  has been **deleted**: it was the fallback Vercel serves when a deployment has no
  build output, so a broken frontend build answered 200 with a convincing page
  instead of failing. The real SPA builds to `frontend/dist`, matching
  `vercel.json`'s `outputDirectory` and vite's `outDir`. Verify by body,
  never by status alone - and note that a deployment with no output now returns
  an error rather than a placeholder.
- **Worker hosts are `<worker>.<account-subdomain>.workers.dev`.** The subdomain
  is per account (`kooshapari` here) and cannot be assumed away: a host built as
  `tracera-edge-dev.workers.dev` does not resolve at all.

Notes that matter when debugging a hostname:

- **`tracera.pheno.studio` is behind Cloudflare Access.** An unauthenticated
  request gets `302` to a `*.cloudflareaccess.com` login, not a `200` and not a
  `401`. Automated checks must not treat production as reachable; CI instead
  smokes `dev`, where routes answer normally (public liveness routes `200`,
  guarded routes `401`/`403`).
- **`tracera.pheno.studio/api` is the canonical production API**, served through
  a Cloudflare Tunnel to the operator's box rather than by a hosting provider.
  The Render service `tracera-server` is the documented fallback, used when that
  box is down for a long stretch. See the header of `render.yaml`.
- **`api.pheno.studio` is not Tracera.** It serves the AgilePlus home page. It
  was previously wired into `TRACERA_API_BASE`, which is why the parity smoke
  spent its life reporting `404` on every route. Do not point anything here.
- `tracera-server-dev.onrender.com` returns `404` on `/healthz`: the service is
  defined in `render.yaml` but has never been created. Two things blocked it, and
  both are now fixed in the repo:
  1. The blueprint's image reference carried a redacted org name, so it resolved
     to no image at all. A blueprint sync therefore could not create the dev
     service, and would equally have tried to repoint the working production
     fallback at that dead path.
  2. The GHCR package was never actually made public. `build-push-image.yml`
     called `/orgs/<owner>/packages/...` for a repository owned by a _user_, so
     the flip 404'd on every run and the image stayed private.

  `tracera-server-dev` **serves** (`srv-damigk5bedkc73bspbm0`, created by the
  Bootstrap Render dev service workflow, recorded as the `RENDER_SERVICE_ID_DEV`
  repository variable), and `/healthz` returns 200. The remaining cause was **not**
  (2) below: the private-package theory was wrong, because the working production
  fallback pulls the same private image. Every deploy was instead rejected
  (`update_failed` after about five seconds) because the create payload was
  schema-invalid. The numbered items below are kept as history:
  the GHCR package is private, so Render cannot pull it. The bootstrap run shows
  this as `attempt N: …/healthz -> 000` and warns that the registry credential
  (`image.ownerId` in `render.yaml`) must be configured. Either configure that
  credential, or flip the package once at
  `https://github.com/users/KooshaPari/packages/container/tracera-server/settings`.

  Note that `build-push-image.yml` cannot flip it: `GITHUB_TOKEN` has no authority
  over package visibility for a user-owned package and both endpoints 404. Set a
  `GHCR_ADMIN_TOKEN` secret (a PAT with package admin) and the step will do it.

  `TRACERA_API_BASE_DEV` now points at the dev service, so `dev` and `preview`
  no longer fall back to `TRACERA_API_BASE`.

- **Render no longer depends on Infisical.** `deploy-render.yml` and
  `render-bootstrap.yml` now read the repository's own `RENDER_API_KEY` secret
  first and keep Infisical only as a fallback, so the two facts below are
  background rather than blockers. They were confirmed against the live Infisical
  project from a logged-in CLI session:
  1. `INFISICAL_TOKEN` **has been fixed** - it used to hold an Infisical
     Universal Auth Client ID, not a
     service token, which the CLI rejected as `403 The provided access token is
malformed` (see `DEPLOY_CREDENTIALS.md`). It now carries a read-scoped service
     token (`st.…`, one-year expiry) created for CI, and it authenticates: a dry run
     of `render-bootstrap.yml` reaches the missing-secret check below instead of
     failing auth. Store it with `gh secret set -f <file>`; piping on Windows appends
     CRLF and Infisical then rejects the value as malformed.
  2. **The project does not contain the deploy secrets at all.** Project
     `8efe392e-…` (`INFISICAL_PROJECT_ID`) holds AI-tooling values -
     `OPENAI_API_KEY`, `LANGFUSE_*`, `LANGSMITH_*`, `NIAH_*`, `HARBOR_*`,
     `MERGIFY_*`, `PORTAGE_ROOT`, plus Apple signing certs and `SONAR_TOKEN` in
     `prod`. It has **no `RENDER_API_KEY`, no `RENDER_SERVICE_ID`, no
     `CLOUDFLARE_API_TOKEN`, and no `WORKOS_*`** in `dev`, `prod` or `staging`.

  So fixing the token alone is not enough: `deploy-render` and the bootstrap
  would still find nothing to pull. Either add the deploy secrets to
  `8efe392e-…` under `dev` and `prod`, or point `INFISICAL_PROJECT_ID` at the
  project that actually holds them. The keys these workflows read are:

  | Key                                             | Read by                                          |
  | ----------------------------------------------- | ------------------------------------------------ |
  | `RENDER_API_KEY`, `RENDER_SERVICE_ID`           | `deploy-render.yml`, `render-bootstrap.yml`      |
  | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | `deploy-cloudflare.yml` (secrets, not Infisical) |
  | `WORKOS_CLIENT_ID`, `WORKOS_API_KEY`            | WorkOS integration                               |

  Until then every `deploy-render` run skips and reports success, carrying an
  `::error title='Render deploy skipped'` annotation that says so.

## Repository variables

| Variable               | Used for                                                                                    | Current value                             |
| ---------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------- |
| `TRACERA_API_BASE`     | production API base, baked into the frontend build and used by the parity smokes            | `https://tracera-server.onrender.com`     |
| `TRACERA_API_BASE_DEV` | overrides the API base for `dev` and `preview`; falls back to `TRACERA_API_BASE` when unset | `https://tracera-server-dev.onrender.com` |

Set `TRACERA_API_BASE` to `https://tracera.pheno.studio` once Cloudflare Access
is fronting a build that should be smoked without a service token, otherwise CI
keeps addressing the fallback host.

## What checks each environment

- `deploy-pages.yml` builds the Pages site against `TRACERA_API_BASE` and then
  asserts the deployed artifact still points at `EXPECTED_API_ORIGIN`, so a
  frontend can never silently drift onto a stale API.
- `frontend-contract-checks.yml` runs the parity smokes against
  `vars.TRACERA_API_BASE`. Those smokes treat `401`/`403` as "route present but
  guarded" and fail on `404`/`5xx`, so they catch a misaligned deployment without
  pretending an unauthenticated client can reach guarded routes.
- `nightly.yml` builds the server and smokes it on loopback. It is the scheduled
  `dev` validation: it never touches `prod`.

## Fleet-wide monitors

These run regardless of which environment was deployed and exist to catch the
thing the per-environment checks above cannot: a deployed surface that quietly
stops serving. The `Render` free tier sleeps a service after ~15 minutes of no
traffic and a cold start can take 30+ seconds; nothing in the deploy workflows
notices a service that wakes up broken or never wakes up at all.

- `live-service-smoke.yml` — daily at 06:37 UTC, plus on demand with a `target`
  input (`all`, `prod`, `dev`, `frontend`). Pings `tracera-server.onrender.com`,
  `tracera-server-dev.onrender.com`, and the `tracera-kappa.vercel.app` alias.
  Uses `curl --max-time 60` so a cold sleep doesn't trip the run, then reads
  the body: `/healthz` must report `"status":"ok"`, and the Vercel alias must
  serve the SPA rather than the retired `scaffolding coming soon` placeholder.
  Pairs with `deploy-vercel.yml`'s body-as-content verify step so a broken
  preview can't pass locally and a broken prod can't pass here.
