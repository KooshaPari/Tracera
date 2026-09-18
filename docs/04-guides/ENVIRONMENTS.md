# Environments: triggers, gating, and DNS

One rule drives everything here: **a push to `main` is never a production
deploy.** Production moves only on a release tag, and every environment has its
own hostname so a URL always identifies which system you are talking to.

## The model

| Environment | Trigger | GitHub environment | Approval | Purpose |
| --- | --- | --- | --- | --- |
| `preview` | `pull_request` against `main` | `vercel-preview` / `render-preview` / `cloudflare-preview` | none | Per-PR build, reaches a non-production backend |
| `dev` | push to `main`; nightly `schedule` | `vercel-dev` / `render-dev` / `cloudflare-dev` | none | Continuous delivery and the nightly validation run |
| `prod` | push of a `v*` tag; `workflow_dispatch` with `environment: prod` | `vercel-production` / `render-production` / `cloudflare-production` | required reviewers | Public production |

`workflow_dispatch` takes an explicit `environment` input (`dev`, `preview`,
`prod`) defaulting to `dev`, so a manual run never lands in production by
accident.

Each deploy workflow derives that environment in a single `plan` job from the
event and passes it on, rather than re-deriving it per step:

| Event | Derived environment |
| --- | --- |
| `pull_request` | `preview` |
| ref starts with `refs/tags/` | `prod` |
| `workflow_dispatch` | the `environment` input |
| anything else (push to `main`, `schedule`) | `dev` |

## DNS and hostnames

Each environment owns a distinct hostname. Verified against the live services;
re-verify before relying on any of it.

| Environment | Frontend | API | Edge worker |
| --- | --- | --- | --- |
| `prod` | `https://tracera.pheno.studio` | `https://tracera.pheno.studio/api` | `https://tracera-edge.pheno.studio` |
| `prod` (fallback) | — | `https://tracera-server.onrender.com` | — |
| `dev` | `https://tracera-kappa.vercel.app` | `https://tracera-server-dev.onrender.com` | worker deployed with dev vars |
| `preview` | Vercel-generated URL per PR | same as `dev` | not deployed |

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
- `tracera-server-dev.onrender.com` currently returns `404` on `/healthz`: the
  `tracera-server-dev` service in `render.yaml` is defined but not deployed.
  `dev` deployments are blocked on that service existing, not on this repo.

## Repository variables

| Variable | Used for | Current value |
| --- | --- | --- |
| `TRACERA_API_BASE` | production API base, baked into the frontend build and used by the parity smokes | `https://tracera-server.onrender.com` |
| `TRACERA_API_BASE_DEV` | overrides the API base for `dev` and `preview`; falls back to `TRACERA_API_BASE` when unset | unset |

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
