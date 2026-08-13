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
`frontend/apps/web/src/api/client-core.ts`. The approved local runtime is the
rich gateway at `127.0.0.1:18000`; it fronts the API and is the default origin
for the desktop/web build. Rust remains directly reachable at
`127.0.0.1:8080` for backend diagnostics. The bundled legacy stack on `18081`
is an explicit opt-in compatibility/latency-smoke surface, not the production
or rich-dashboard default. Hosted URLs remain opt-in environment overrides.

## API evidence

The rich UI requires Projects, Items, Links, Graph, Agents, Events, Matrix,
Impact, Reports, Settings and related `/api/v1/*` routes. The current Rust route
registry does not provide all of these. Mock tests are useful for UI quality but
do not establish live compatibility.
