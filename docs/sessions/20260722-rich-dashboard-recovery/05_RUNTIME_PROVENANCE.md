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

