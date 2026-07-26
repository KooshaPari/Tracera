# Parity Matrix and Acceptance Gates

| Gate | Required evidence | Status |
|---|---|---|
| Source selection | Build from `95334238c` or a descendant containing its full route/view tree | pending |
| API origin | Production default resolves to `http://127.0.0.1:18081/`; no implicit Pages/Vercel URL | pending |
| Contract parity | Every rich client route has a typed Rust route or an explicit, tested server adapter | pending |
| Live CRUD | Projects, Items, Links create/read/update/delete against local server | pending |
| SPA delivery | Local compose image serves the rich `dist` output at port 18081 | pending |
| Desktop | Electrobun window opens local rich SPA and tray reports the same origin | pending |
| Regression | Existing minimal app remains recoverable until all gates are green | required |
| Verification | Focused tests, build, HTTP smoke, and installed-app smoke all pass | pending |

100% acceptance means every row is green with live evidence. Mock-only Vitest,
source counts, or a successful Vite build cannot satisfy API or desktop gates.

