# Dependency audit — 2026-07-19

OSV Scanner scanned `Cargo.lock`, `frontend/bun.lock`, `uv.lock`, and
`sidecar/go/go.mod`.

## Findings

- Initial scan: 13 known vulnerabilities across 7 packages
- After removing the unused Electron-builder/Squirrel packaging surface,
  refreshing Vite to 8.1.5, and raising the Go sidecar baseline to 1.23, the
  current scan reports 4 known Python tooling vulnerabilities; npm and Go are
  clean.
- 0 critical, 8 high, 4 medium, 1 unknown
- All reported entries have an available fixed version

The findings are not silently treated as runtime-server vulnerabilities: the
Python lockfile is historical/benchmark tooling, while the npm and Go entries
are adjacent build/sidecar surfaces. They still require remediation before a
production publish. The current release remains gated on dependency review.

## Remediation queue

| Surface | Package(s) | Fixed version(s) | Action |
|---|---|---|---|
| Go sidecar | `stdlib` 1.22.99 | 1.23.10 | Resolved by raising module/CI toolchain baseline to Go 1.23 |
| Python tooling | `mcp`, `ray`, `setuptools`, `torch` | 1.28.1, 2.56.0, 83.0.0, 2.13.0 | Upgrade in the benchmark environment and re-lock |
| Frontend lockfile | none | — | Resolved by removing unused Electron-builder packaging |

The inventory is generated from the command below and must be refreshed after
each dependency update:

```sh
osv-scanner scan source -r .
```
