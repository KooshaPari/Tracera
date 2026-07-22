# Runtime provenance and recovery map

This record keeps the approved rich dashboard lineage separate from deployable
runtime snapshots. It is based on Git objects, not the current working tree.

| Requirement | Provenance | Result |
|---|---|---|
| Rich frontend | `36b6055faeed18bc398e5fb99242f31dcdf3e6b0`, `origin/legacy/grapheon-wip-final-2026-07-17` | 1,180 web source files; latest descendant of the Jan/Feb rich UI line found |
| Matching gateway schema | `1052cf01e6f6a9449944deecc08a696020aa2f27`, `origin/airlock-recovery/main:docker-compose.yml` | `nginx`, `go-backend`, `python-backend`, `postgres`, `redis`, `nats` services |
| Gateway assets | Same `1052cf01` ref, `deploy/nginx/{nginx.conf,conf.d/*}` | Present; compatible service names and internal ports |
| Go build | Same ref, `backend/Dockerfile` | Present |
| Python application | Same ref, `src/tracertm/api/main.py`, `pyproject.toml` | Present |
| Python image recipe | No root `Dockerfile` in `1052cf01` | Missing in source; requires isolated overlay-only Dockerfile |

## Route-contract evidence

The approved rich frontend API modules contain **94 distinct `/api/v1` path
templates**. The materialized Python candidate `bf6cd11ad26e2942d6bcad7f91c0a76601468f09`
contains 28 direct FastAPI route decorators before router-prefix expansion. This
is evidence of a broad compatibility gap, not proof that every rich route is
unsupported; prefixes and Go-owned routes still require normalization. A live
bundle must publish a generated route matrix with `frontend-only`,
`python-owned`, `go-owned`, and `matched` classifications.

The current manifest now classifies all 94 rich frontend route templates exactly
across the existing capability families. Classification is not backend parity:
the Python-oracle families remain gated until an authoritative runtime source
tuple is recovered, and the unavailable telemetry/WebSocket family remains
explicitly unavailable.

The existing 16-family capability manifest already has semantic buckets for
most of these paths (authentication, agents, journeys, concepts/libraries/
equivalences, search, executions/Codex, notifications/settings). The prior
46-path count was an **exact-template coverage gap**, not 46 new product
domains. The expanded matrix resolves that bookkeeping gap while preserving
the separate runtime-ownership and availability gates.

## Oracle parity checkpoint (2026-07-22 14:35 UTC)

Static expansion of the materialized Python candidate yields 20 unique
`/api/v1` routes (37 decorator occurrences including duplicates and tests).
Only `/api/v1/auth/me` is an exact-template match with the rich frontend
inventory. This is a conservative comparison: parameter-name normalization and
gateway rewrites may produce additional semantic matches, but they are not
counted until an explicit route map proves them. The Python candidate therefore
cannot yet back the rich dashboard in production.

The reproducible comparison is now encoded in
`scripts/compare-rich-oracle-routes.py`; it emits the rich/oracle counts,
normalized candidate matches, and both directional gaps. Normalization collapses
parameter names only for comparison and never changes the promotion gate.

The comparator also extracts Axum route literals. Against the current native
server it reports 23 Rust routes and zero normalized rich-template matches;
this is expected for the current API shape and confirms that the rich surface
cannot be enabled by simply pointing its client at the Rust listener.

The same comparator, run against the isolated `routes.go` object from
`1052cf01e6f6a9449944deecc08a696020aa2f27`, reports 141 Echo registrations and
43 normalized rich-template candidates. The gateway exposes multiple methods
on 28 normalized paths. These are candidate overlaps only; handler behavior,
auth middleware, method contracts, and response schemas still require
endpoint-level verification before promotion.

The rich-client method extractor finds only five direct route/method pairs in
the current API modules; dynamic URL builders remain intentionally unresolved.
This is a lower bound, not a claim that the other rich routes are GET-only.
The comparator now emits this inventory so unresolved client contracts remain a
visible promotion blocker.

## Incompatible snapshots

- `origin/releases/stable`'s `ARCHIVE/DOCKER/docker-compose.yml` uses `backend`
  and `api`, not the gateway schema above; it cannot consume the rich overlay.
- `24edd746532f2284293222488256594886b42ddf` contains a root `Dockerfile`, but
  its Compose/frontend snapshot is the small Grapheon bootstrap and is not the
  approved rich dashboard runtime.
- `3423caf276aa55b925ab9e484af09e35e71ae934` contains the matching gateway,
  nginx assets, backend Dockerfile, and Python source, but no root Dockerfile.

## Disposable-only recovery rule

The missing Python image recipe must be supplied under
`deploy/oracle-isolated/python/Dockerfile` and selected by an overlay that
changes only `python-backend.build`. It must never be merged into the stable
source snapshot or used to alter Grapheon port `8080`. Materialized checkouts
must retain the exact ref/hash above and record checksums before any launch.

## Validation checkpoint (2026-07-22 14:25 UTC)

- Rich worktree `/private/tmp/tracera-rich-integrated-20260722` restored its
  frozen Bun lockfile and installed 533 packages with Bun 1.3.11.
- `bun run build` passed: 1,895 modules transformed; production bundle emitted
  to `frontend/dist`. Vite emitted only deprecation and chunk-size warnings.
- `scripts/validate-rich-route-matrix.mjs` reports 94 route templates, 57
  declared exact paths, and 46 unclassified exact paths when evaluated against
  the canonical manifest. This remains a fail-closed promotion gate.
- No runtime launch or public deployment was claimed: the rich worktree does
  not contain the canonical manifest, and the oracle source tuple is still
  incomplete.

## Deployment security checkpoint (2026-07-22 14:48 UTC)

- `scripts/verify-deployment-security.sh --mode private`: passed.
- `scripts/verify-deployment-manifests.sh`: passed in secret-free static mode.
- Public mode fails closed without a real `TRACERA_PUBLIC_HOSTNAME`; a
  placeholder hostname is rejected as well. No public deployment is implied
  by the private-mode pass.

## Rich UI static checkpoint (2026-07-22 14:56 UTC)

- A source scan found no production `<img>` element without an `alt` attribute;
  the only missing-alt matches are intentionally adversarial XSS test fixtures.
- Existing rich source contains dedicated accessibility and security test trees.
- A direct Vitest invocation could not complete in the isolated worktree because
  the package has no configured test script/dependency; no test pass is claimed.

The rich worktree now has a canonical Vitest harness. Current evidence:

- Security/input-validation: **40/40 passed**.
- Form accessibility: **20/20 passed** after selector/keyboard assertion fixes.
- Page accessibility: **20/20 passed**.
- Combined configured a11y/security command: **237/265 passed**; the remaining
  28 failures are concentrated in legacy `forms.test.tsx` fixtures that render
  non-labellable `<div>` controls, not production page components. They remain
  visible failures and are not suppressed.
