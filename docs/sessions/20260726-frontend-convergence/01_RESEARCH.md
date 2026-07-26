# Research

## Variant inventory

| Variant | Evidence | Decision |
|---|---|---|
| Rich historical dashboard | `95334238c`, ~1,181 frontend source files, 117 API paths | Canonical target |
| Minimal main dashboard | `e939246e6`, 12 web source files | Preserve as rollback only |
| Desktop shell | `frontend/apps/desktop`, Electrobun | Keep shell; point at converged local web |
| Hosted Pages/Vercel | deployment-only artifacts | Never default for installed app |

## Runtime mismatch

The rich client defaults to `http://localhost:4000` in
`frontend/apps/web/src/api/client-core.ts`. The local stack is exposed at
`127.0.0.1:18081` (frontend proxy) and Rust directly at `127.0.0.1:8080`.
The convergence patch must use an explicit local default and retain hosted URLs
only as opt-in environment overrides.

## API evidence

The rich UI requires Projects, Items, Links, Graph, Agents, Events, Matrix,
Impact, Reports, Settings and related `/api/v1/*` routes. The current Rust route
registry does not provide all of these. Mock tests are useful for UI quality but
do not establish live compatibility.

