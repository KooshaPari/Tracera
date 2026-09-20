# Environments: triggers, gating, and DNS

One rule drives everything here: **a push to `main` is never a production
deploy.** Production moves only on a release tag, and every environment has its
own hostname so a URL always identifies which system you are talking to.

## The model

| Environment | Trigger                                                              | GitHub environment                            | Approval           | Purpose                                            |
| ----------- | -------------------------------------------------------------------- | --------------------------------------------- | ------------------ | -------------------------------------------------- |
| `preview`   | `pull_request` against `main` (`deploy-vercel`, `deploy-cloudflare`) | `vercel-preview` / `cloudflare-preview`       | none               | Per-PR build, reaches a non-production backend     |
| `dev`       | push to `main`; nightly `schedule`                                   | `vercel-dev` / `cloudflare-dev`               | none               | Continuous delivery and the nightly validation run |
| `prod`      | push of a `v*` tag; `workflow_dispatch` with `environment: prod`     | `vercel-production` / `cloudflare-production` | required reviewers | Public production                                  |

`workflow_dispatch` takes an explicit `environment` input (`dev`, `preview`,
`prod`) defaulting to `dev`, so a manual run never lands in production by
accident.

`deploy-vercel` and `deploy-cloudflare` each derive that environment in a single
`plan` job from the event and pass it on, rather than re-deriving it per step.
`deploy-full-stack` has no `plan` job of its own; it forwards its `environment`
input to the frontend and edge workflows it calls, so a dispatch asking for
`prod` reaches those surfaces as `prod` instead of falling through to `dev`:

| Event                                      | Derived environment     |
| ------------------------------------------ | ----------------------- |
| `pull_request`                             | `preview`               |
| ref starts with `refs/tags/`               | `prod`                  |
| `workflow_dispatch`                        | the `environment` input |
| anything else (push to `main`, `schedule`) | `dev`                   |

## DNS and hostnames

Each environment owns a distinct hostname. Verified against the live services;
re-verify before relying on any of it.

| Environment          | Frontend                                            | API                                                   | Edge worker                                             |
| -------------------- | --------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------- |
| `prod`               | `https://tracera.pheno.studio` (Cloudflare Access)  | `https://tracera.pheno.studio/api`                    | `https://tracera-edge.pheno.studio` (not attached, 530) |
| `prod` (fleet nodes) | —                                                   | any enrolled node's tunnel/origin                     | `GET /fleet/nodes` on the edge worker lists them        |
| `dev`                | per-deploy Vercel URL, behind Vercel Authentication | `https://tracera.pheno.studio/api` (shared self-host) | `https://tracera-edge-dev.kooshapari.workers.dev`       |
| `preview`            | per-deploy Vercel URL, behind Vercel Authentication | same as `dev` (no separate service)                   | `https://tracera-edge-preview.kooshapari.workers.dev`   |

## Fleet compute nodes

Beyond the managed tiers, any bare-metal box or VPS slice can enroll as a
compute node (see `docs/04-guides/LOCAL-IAC.md`). The node daemon polls the
edge worker for desired state and converges via docker compose; CI publishes
new images to every enrolled node in the `publish-fleet-state` job of
`deploy-full-stack.yml`. This gives trivial compute (homelab, cheap VPS)
the same "push to main and it deploys" ergonomics as the managed tiers.

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
  a Cloudflare Tunnel to the operator's box. See `deploy/selfhost/README.md` and
  `.cloudflared/config.yml`.
- **`api.tracera.pheno.studio` is the alternate API hostname** on the same
  tunnel. Use it for `/healthz` and other root-level server routes; the
  path-prefixed `tracera.pheno.studio/api/*` ingress does not expose them.
- **`api.pheno.studio` is not Tracera.** It serves the AgilePlus home page. It
  was previously wired into `TRACERA_API_BASE`, which is why the parity smoke
  spent its life reporting `404` on every route. Do not point anything here.

## Backend deployment

The Rust backend is **self-hosted** on the operator's machine and published
through a Cloudflare Tunnel (with optional Tailscale for private access). CI
builds and pushes the `tracera-server` container image to GHCR via
`build-push-image.yml`; pulling and restarting that image on the operator box is
a manual step documented in `deploy/selfhost/README.md`.

There is no hosted dev API: `dev` and `preview` frontends talk to the same
self-hosted backend unless overridden locally (for example
`frontend/apps/web/.env.local` with `VITE_API_URL=http://localhost:8080`).

## Vercel Functions (Render replacement)

Render is dead; the Vercel deployment serves same-origin API stubs from
`api/` at the repo root so the frontend does not 404 on `/api/v1/*`. Each
file is a one-route TypeScript function under `nodejs20.x`, returning a
valid envelope (empty list, `{status:"ok"}`, or `501 "graph-stub"`). The
shape and status codes mirror the `501`/`{items:[]}` set that the Rust
backend returned when Render was alive, so the frontend contract is
unchanged.

| Route surface                                   | Source                                                                                                                                   | Returns today                                                |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `/health`, `/healthz`, `/ready`, `/readyz`      | `api/{health,healthz,ready,readyz}.ts`                                                                                                   | `200 {"status":"ok"\|"ready"}`                               |
| `/api/v1/health`                                | `api/v1/health.ts`                                                                                                                       | `200 {"status":"ok"}`                                        |
| `/api/v1/csrf-token`                            | `api/v1/csrf-token.ts`                                                                                                                   | `200 {"csrf_token":"...stub...","header":"x-csrf-token"}`    |
| `/api/v1/dashboard/summary`                     | `api/v1/dashboard/summary.ts`                                                                                                            | `200 {"total_artifacts":0,"coverage_ratio":0,"open_gaps":0}` |
| `/api/v1/projects`, `/projects/{id}`            | `api/v1/projects/index.ts`, `api/v1/projects/[id].ts`                                                                                    | `200 {total:0, projects:[]}` (GET) / `501` (write)           |
| `/api/v1/items`, `/items/{id}`                  | `api/v1/items/{index,[id],summary,bulk-update}.ts`                                                                                       | `200 {total:0, items:[]}` (GET) / `501` (write)              |
| `/api/v1/items/pivot-targets/{id}`              | `api/v1/items/pivot-targets/[item_id].ts`                                                                                                | `501 pivot-stub`                                             |
| `/api/v1/links`, `/links/{id}`                  | `api/v1/links/{index,[id]}.ts`                                                                                                           | `200 []` (GET) / `501` (write)                               |
| `/api/v1/graph/**`                              | `api/v1/graph/{ancestors/[id],descendants/[id],path,paths,full,cycles,topo-sort,orphans,impact/[id],dependencies/[id],traverse/[id]}.ts` | `501 graph-stub`                                             |
| `/api/v1/search/**`                             | `api/v1/search/{index,index/[id],suggest,stats,reindex,batch-index}.ts`                                                                  | `501 search-stub` (only `/health` returns 200)               |
| `/api/v1/auth/{me,login,logout,refresh,verify}` | `api/v1/auth/*.ts`                                                                                                                       | `200 {status:"ok"}` (logout) / `501` (others)                |
| `/api/v1/import`, `/projects/{id}/import`       | `api/v1/import.ts`, `api/v1/projects/[id]/import.ts`                                                                                     | `501 import-stub`                                            |
| `/api/v1/projects/{id}/export`                  | `api/v1/projects/[id]/export.ts`                                                                                                         | `501 export-stub`                                            |

The functions are configured via `vercel.json`'s `functions.api/**/*.ts`
block (`maxDuration: 10s`; the official Node.js runtime is auto-detected
when `runtime` is unset, and the Vercel CLI rejects `runtime: "nodejs20.x"`
because that field is for community runtimes that need a `name@version`).
`@vercel/node` is a root-level devDep declared in `package.json`;
`tsconfig.json` is the build root for typechecking the functions in
isolation, scoped to `api/**/*.ts` only so it never collides with the
Vite app's TS project.

When the Cloudflare Tunnel to the local Rust backend is restored, swap
`VITE_API_URL=/api` in `.env.production` back to
`https://tracera.pheno.studio/api` and the Functions fall out of the
path; Render never comes back.

A path-segment constraint that bit once and is worth recording: Vercel
treats every dynamic `[param]` directly under the same directory as a
named parameter, and two different names collide. So `items/[id].ts` and
`items/[item_id]/pivot.ts` cannot coexist (the Vercel build fails with
"Two or more files have conflicting paths or names"). The current tree
uses the same `[id]` name everywhere it appears in the same directory
level; per-resource sub-actions live under a sibling `[id]/` directory
rather than under a differently-named dynamic segment.

## Repository variables

| Variable               | Used for                                                                                    | Current value                      |
| ---------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------- |
| `TRACERA_API_BASE`     | production API base, baked into the frontend build and used by the parity smokes            | `https://tracera.pheno.studio/api` |
| `TRACERA_API_BASE_DEV` | overrides the API base for `dev` and `preview`; falls back to `TRACERA_API_BASE` when unset | `https://tracera.pheno.studio/api` |

Set these in GitHub repository variables so deploy workflows and contract checks
point at the self-hosted tunnel rather than a retired third-party host.

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
stops serving.

- `live-service-smoke.yml` — daily at 06:37 UTC, plus on demand with a `target`
  input (`all`, `prod`, `dev`, `frontend`). Pings `api.tracera.pheno.studio`
  and the `tracera-kappa.vercel.app` alias. Uses `curl --max-time 60` and reads
  the body: `/healthz` must report `"status":"ok"`, and the Vercel alias must
  serve the SPA rather than the retired `scaffolding coming soon` placeholder.
  Pairs with `deploy-vercel.yml`'s body-as-content verify step so a broken
  preview can't pass locally and a broken prod can't pass here.
