# Coverage Matrix (Self-Application)

| Concern | Evidence |
|---|---|
| Authn / authz middleware | [`src/tracertm/api/middleware/authz.py`](../..//src/tracertm/api/middleware/authz.py) |
| Token claim validation | [`src/tracertm/api/deps.py`](../../src/tracertm/api/deps.py) |
| Endpoint inventory | [`docs/FEATURE_INVENTORY.md`](../../docs/FEATURE_INVENTORY.md) |
| Endpoint map | [`endpoint_traceability_map.md`](endpoint_traceability_map.md) |
| Quickstart coverage | [`../../docs/quickstart.md`](../../docs/quickstart.md) |
| API reference coverage | [`../../docs/API_REFERENCE.md`](../../docs/API_REFERENCE.md) |
| Security policy | [`../../SECURITY.md`](../../SECURITY.md), [`../../docs/security/SECURITY.md`](../../docs/security/SECURITY.md) |

## Gaps and next steps

- Mounting coverage: several endpoints are currently unmounted and need explicit
  product decision before the next audit cycle.
- Endpoint-level API tests: most routes need direct coverage additions.
- Scope matrix for authz checks should be converted from placeholder scopes to
decision-backed permissions.
