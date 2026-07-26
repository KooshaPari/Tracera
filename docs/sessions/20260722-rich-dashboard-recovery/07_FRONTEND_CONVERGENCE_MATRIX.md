# Frontend convergence matrix

Audit date: 2026-07-26 00:45 UTC

This inventory separates the Grapheon shell from the canonical rich Tracera
dashboard. It is a merge plan, not permission to delete either tree.

## Implementations found

| Surface | Location | Shape | API posture | Decision |
|---|---|---|---|---|
| Canonical rich dashboard candidate | `Tracera` history around `95334238c` (2026-07-22) | 1,181 frontend source files; 117 distinct `/api/v1` paths | Broad typed client; requires Rust route parity | Source of truth for product UX, pending live contract gate |
| Current Tracera installed web | `Tracera/frontend/apps/web/src` | 12 source files; Dashboard, TraceViewer, CoverageMatrix, TopNav | `traceraClient.js` targets coverage, impact, governance, confidence, blast-radius, trace forward/reverse | Release shell; keep as fallback until rich parity is green |
| Grapheon web | `Grapheon/frontend/apps/web/src` | 1 Dashboard component (204 JSX lines) plus 340 CSS lines | Direct fetches; health plus sprints/teams/coverage paths | Mine for useful status/empty/error presentation; do not promote as canonical |
| Grapheon desktop | `Grapheon/frontend/apps/desktop/src` | Thin Electrobun wrapper | Defaults to GitHub Pages; explicit local origin work is required | Converge with Tracera desktop origin policy |
| Tracera desktop | `Tracera/frontend/apps/desktop/src` | Native shell with local-origin resolver and sidecar lifecycle | Defaults to `http://127.0.0.1:8080` | Canonical desktop behavior |

## Semantic comparison

| Capability | Grapheon | Canonical rich candidate | Current Rust server | Merge action |
|---|---|---|---|---|
| Health/backend status | Health card and API base display | Operational dashboard/status surfaces | `/health`, `/ready`, `/evidence/health` | Keep Grapheon health-card copy; bind only to live health endpoints |
| Sprints/teams | Direct `/sdlc-pm/sprints`, `/org-intel/teams` fetches | Rich organization/project views | No matching Rust routes | Represent as typed adapters; do not silently show empty fake data |
| Coverage | `/api/v1/coverage-matrix` fetch | Coverage matrix plus governance views | Route exists only for method-compatible contract; verify schema | Reuse rich matrix; add contract fixture and live test |
| Evidence/trace | Minimal dashboard has none | Trace viewer, evidence graph, forward/reverse impact | `/evidence` and evidence health are live | Wire evidence first; gate graph/impact on typed routes |
| Loading/error/empty states | Grapheon has readable explicit states | Rich candidate has reusable async/client state | Server errors need normalized envelope | Extract state primitives from both into canonical components |
| API origin | `localhost:8080` in web; Pages default in desktop | Vite/API client had historical `localhost:4000` drift | Local launchd server at `127.0.0.1:8080` | One resolver: explicit env override, otherwise local 8080 |

## Mergeable improvements

1. Port Grapheon's health card, backend badge, API-base disclosure, and
   degraded-state copy into the canonical Dashboard without preserving direct
   untyped fetches.
2. Define typed `Project`, `Item`, and `Link` contracts before enabling the rich
   CRUD views; add Rust routes and integration fixtures together.
3. Reuse the rich candidate's navigation/layout and trace/coverage surfaces;
   use current Rust `/evidence` as the first real data source.
4. Add a single origin resolver shared by web and desktop. Default must be
   `http://127.0.0.1:8080`; hosted Pages is an explicit deployment override only.
5. Add browser smoke assertions that fail if the renderer navigates to
   `github.io` without an explicit hosted mode.

## Non-mergeable / reject

- Do not copy Grapheon's GitHub Pages default into any installed app.
- Do not treat `/sdlc-pm/*`, `/org-intel/*`, or absent rich CRUD routes as live
  merely because the UI renders an empty array.
- Do not delete the historical rich candidate or the current release shell
  until API parity and installed-app smoke gates pass.

## Promotion gates

```text
typed contracts -> Rust routes -> live integration tests
                         |
                         v
rich dashboard build -> local desktop smoke -> install/open -> release
```

Evidence required for promotion: endpoint/schema matrix, live local-server
responses, frontend build/test output, and installed-app origin log showing
`127.0.0.1:8080`.
