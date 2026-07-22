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

The current manifest covers 57 frontend paths exactly; the rich API inventory
contains 94. **46 paths are currently unclassified**, including agent status and
task routes, AuthKit lifecycle routes, component/library/token operations,
equivalence mutations, events, journeys, Codex review, execution artifacts, and
search indexing. These must be classified before enabling those UI surfaces.

The existing 16-family capability manifest already has semantic buckets for
most of these paths (authentication, agents, journeys, concepts/libraries/
equivalences, search, executions/Codex, notifications/settings). The 46-path
count is therefore an **exact-template coverage gap**, not 46 new product
domains. The next matrix pass must expand those existing buckets to concrete
templates and leave only genuinely unmapped paths as `unavailable`.

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
