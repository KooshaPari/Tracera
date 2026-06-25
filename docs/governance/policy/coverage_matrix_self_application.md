# Coverage Matrix (Self-Application)

## Evidence index

| Control | Evidence |
|---|---|
| Authn/Authz middleware mounted for API | [`src/tracertm/api/main.py`](../../src/tracertm/api/main.py) |
| JWT header/claim validation | [`src/tracertm/api/deps.py`](../../src/tracertm/api/deps.py) |
| Middleware input-shape validation | [`src/tracertm/api/middleware/authz.py`](../../src/tracertm/api/middleware/authz.py) |
| Endpoint inventory + mount map | [`docs/FEATURE_INVENTORY.md`](../../docs/FEATURE_INVENTORY.md), [`endpoint_traceability_map.md`](endpoint_traceability_map.md) |
| API reference stub | [`../../docs/API_REFERENCE.md`](../../docs/API_REFERENCE.md) |
| Runtime security policy | [`../../SECURITY.md`](../../SECURITY.md), [`../../docs/security/SECURITY.md`](../../docs/security/SECURITY.md) |
| Governance ADR list | [`policy/adr_index.md`](adr_index.md) |
| Quickstart for security verification | [`../../docs/quickstart.md`](../../docs/quickstart.md) |

## FR → endpoint → test coverage (self-check)

| FR family | Coverage status |
|---|---|
| API + health probes | `Partial` |
| Auth `/api/v1/auth/me` | `Missing` |
| Traceability / impact / blast-radius surface | `Partial` |
| Evidence / SDLC / Org-intel / Governance endpoints | `Partial` |
| Ingest / comments endpoints | `Missing` |

## Remediation notes

- Unmounted routes are intentionally non-covered for runtime integration tests until routers
  are mounted in `src/tracertm/api/main.py` or explicitly de-scoped in the audit artifact.
- All listed controls are aligned to the traceability table and updated together in future audit drops.

