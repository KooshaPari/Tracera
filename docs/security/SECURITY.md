# Tracera API Security Policy

## Threat model

| Area | Threat | Control |
|---|---|---|
| Authn/Authz | Stolen or forged bearer tokens | JWT validation with required claims and optional signature/audience/issuer checks |
| Privilege misuse | Scope or method mismatch on route | `ApiAuthzMiddleware` route-by-route scope matrix |
| Input abuse | Oversize path/query/body or control-character injection | middleware hard limits + schema-level constraints |
| Secret exposure | Inlined credentials in code/PR | environment-driven configuration and policy above |

## Secrets via environment

- `TRACERA_JWT_SECRET` must be set for production signature verification.
- `TRACERA_JWT_AUDIENCE`, `TRACERA_JWT_ISSUER` should be set to force claim binding.
- `TRACERA_JWT_PUBLIC_KEY` can be used for asymmetric verification paths.
- DB and service credentials must be injected at runtime only.

## Input validation checklist

- Token header parsing rejects malformed `Authorization` values.
- Token claim validation enforces `sub` and `exp` presence and type.
- Optional `iss`/`aud` claims are type-checked and bounded.
- Request target validation limits path/query length and strips control characters from
  request targets.
- Request body size cap is enforced via `Content-Length`.
- Router schemas use `pydantic` constraints on body, path, and query parameters.

## Runtime authn/authz middleware check

`src/tracertm/api/main.py` mounts middleware in this order:

1. Logging middleware
2. Request-id middleware
3. `ApiAuthzMiddleware`

`ApiAuthzMiddleware` currently:

- marks `/health`, `/ready`, `/docs`, `/redoc`, `/openapi.json` as public,
- requires bearer auth on all other routes,
- resolves token scope policy via:
  - HTTP method baseline scope (`read`/`write`/`delete`),
  - path-prefix policy (`/api/v1/traceability`, `/api/v1/evidence`, etc.),
- returns `401`/`403` with non-sensitive `detail` only.

## Rate-limiting plan

### Phase 1 (current)
- Request shape guardrails: path/query size limits and request body cap.

### Phase 2
- Per-route fixed-window counters (in-memory), then shared Redis adapter for
  horizontal scale.
- `429` enforcement with `Retry-After` and rate-limit headers.

### Phase 3
- Abuse simulation tests in API contract suite (burst, replay, and malformed body cases).

## Cross-link

- Security policy: [`../../SECURITY.md`](../../SECURITY.md)
- Governance matrix + endpoint traceability: [`../../docs/governance/policy/endpoint_traceability_map.md`](../../docs/governance/policy/endpoint_traceability_map.md)
- Self-application coverage: [`../../docs/governance/policy/coverage_matrix_self_application.md`](../../docs/governance/policy/coverage_matrix_self_application.md)

