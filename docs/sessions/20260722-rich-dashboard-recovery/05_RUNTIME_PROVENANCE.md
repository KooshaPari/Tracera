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

The approved rich WIP then fixed the underlying shared UI primitive defect:
`@tracertm/ui` `Input` and `Button` now render semantic native elements with
forwarded refs and correct default button behavior. The formerly failing legacy
forms fixture suite passes **19/19**, and the rich production build still passes
(1,895 modules). The change is preserved on
`wip/20260722T1522-18c4a5ddffb51138` pending promotion review.

Post-repair aggregate rerun reports **253/265 passed**. The two previously
unloadable DOMPurify suites are now executable and pass **79/79** after adding
the declared test dependency. The remaining 12 failures are isolated to
`command-palette.test.tsx` missing local test bindings (`container`, `user`,
and query destructuring); they are not hidden by the runner.

Those command-palette fixtures are now repaired (valid listbox ownership,
keyboard close behavior, and local query/user bindings). The configured
aggregate now passes **344/344 tests across 12 files**. Axe still emits a
non-fatal jsdom canvas diagnostic, but no test is suppressed or marked passing
by configuration.

## Synchronized release checkpoint (2026-07-22 23:44 UTC)

- Canonical checkout is clean at `9a875ff54`.
- Capability manifest validation passes (16 capability families).
- Deployment-manifest and Kubernetes security checks pass in secret-free static
  mode.
- Durable rich WIP refs `95334238c` (a11y fixtures) and `3f5eebe52`
  (DOMPurify dependency) are present on origin; the rich build and aggregate
  test run pass independently. These refs remain promotion candidates, not a
  claim that the canonical checkout contains the rich frontend.

## Promotion order and no-go gates

Promotion must preserve rich base `36b6055fa` and apply the reviewed WIP line in
order: websocket lifecycle `0590fa178`, route validator `e1cf3e49f`, semantic
UI primitives `384ab0c1b`, Vitest harness/security `98cec6b0e` and `3f5eebe52`,
then a11y fixture repair `95334238c`. Before merge or launch, all of these must
be true: rich build passes; the 344-test aggregate passes; route ownership has
an authoritative backend owner; public security mode passes with a real
hostname; and the complete oracle source tuple is checksummed. Any missing
condition is an explicit no-go.

## Overlay validation checkpoint (2026-07-23 00:04 UTC)

The disposable Python Dockerfile is context-compatible with the oracle source:
the pinned `1052cf01` object contains `pyproject.toml`, `README.md`, `src`,
`alembic`, and `config`, which are exactly the files it copies. The standalone
materialized checkout still fails `scripts/validate-oracle-compose.py
--http-only` because it lacks root Compose/nginx assets; those are supplied by
the isolated overlay and must not be inferred from the source ref. No container
launch was attempted.

The new `scripts/verify-oracle-provenance.py` gate checks the tuple directly
from Git objects. It fails for both candidate refs tested: `1052cf01` and
`3423caf2` contain Compose, backend Dockerfile, Python metadata, and nginx, but
both lack the required root `Dockerfile`. This is machine-verified evidence
that neither ref is launch-complete without the isolated overlay recipe.

## Overlay gate repair checkpoint (2026-07-23 00:28 UTC)

The safety validator now accepts an explicit Compose project root and gateway
config. This is required because the isolated override lives under
`deploy/oracle-isolated/` while its build context is the repository root.
Validated command (read-only, no container launch):

```text
INFO: build contexts checked: 1
INFO: host ports: 18000, 18081, 18080, 15432, 16379, 14222
INFO: fixed container_name values: none
OK: oracle checkout passes Compose safety gate
```

## Route comparator repair checkpoint (2026-07-23 00:35 UTC)

The route comparator was corrected to avoid double-prefixing Python routers
that already declare `/api/v1`, and to preserve brace/template parameters in
frontend route extraction. Against materialized rich ref `36b6055fa` and
oracle ref `1052cf01` it now reports 104 rich routes, 71 oracle routes, 9
normalized rich/oracle matches, and 141 Go gateway registrations with 44
normalized rich/gateway matches. These are candidate overlaps only; method,
schema, and authorization parity remain unproven.

### Endpoint contract triage

The only rich route with an explicit frontend method in the normalized overlap
set is `POST /api/v1/agent/sessions`. The Python oracle implements that route
with a `201` `AgentSessionResponse`; the Go gateway has no corresponding
registration. It is therefore **missing from Go**, not safe to route through
the Go service. The remaining eight overlap entries lack an extracted
frontend method in the current API inventory and remain **unclassified** until
request/response schemas and auth guards are inspected directly.

### Authentication overlap audit (2026-07-23 00:38 UTC)

Direct source inspection confirms the shared auth routes are not equivalent by
route presence alone. The Go gateway registers `POST /auth/logout`, `GET
/auth/me`, `POST /auth/refresh`, and AuthKit authorize/callback/refresh only
when the auth provider and AuthKit configuration are available. The Python
oracle protects `/auth/me` and `/auth/logout` with `auth_guard`, while refresh
and AuthKit handlers have separate token/cookie behavior. Rich calls all of
these routes, including cookie credentials. Classification remains **partial**
until response schemas, cookie attributes, and provider-disabled behavior are
tested end to end; route presence is not promotion evidence.
