# Tracera API Security Policy

This repository uses bearer-token auth with scoped authorization, route-level input
validation, and CI hardening controls.

## Scope

- `src/tracertm/api/main.py`
- `src/tracertm/api/deps.py`
- `src/tracertm/api/middleware/authz.py`
- API workflow / release workflows

## Security notes

- Authentication is now validated in middleware (`ApiAuthzMiddleware`) for all
  non-probe requests.
- JWT input checks include header format, token size, required claims (`sub`, `exp`),
  and token expiry tolerance.
- Scope checks are enforced via normalized token scopes when scope requirements are
  declared for the route.
- Signature verification defaults to permissive mode when `TRACERA_JWT_SECRET` is not
  set and must be enabled in production.

## Runtime threat model (summary)

| Threat | Control |
|---|---|
| Replay/tampered tokens | Enforce expiry and signature/audience/issuer validation via env config |
| Missing/forged auth headers | Middleware rejects malformed or missing Bearer tokens |
| Privilege escalation by route | Per-prefix scope requirements in middleware |
| Unbounded/unvalidated payloads | Expand Pydantic constraints on all router inputs |

## Secrets policy (environment variables)

- `TRACERA_JWT_SECRET`, `TRACERA_JWT_PUBLIC_KEY`, `TRACERA_JWT_AUDIENCE`,
  `TRACERA_JWT_ISSUER`
- DB/queue/service credentials in CI and host process environment

## Rate-limiting plan

Implement in phases:

1. Add sliding-window limiter middleware (in-memory first, Redis in production).
2. Apply per-route defaults (read/write/ingest tiers).
3. Emit `Retry-After`, `X-RateLimit-*` headers.
4. Add CI contract tests that verify 429 behavior for burst abuse.

## Governance linkage

- Security control mapping: [`docs/governance/policy/endpoint_traceability_map.md`](docs/governance/policy/endpoint_traceability_map.md)
- Coverage matrix: [`docs/governance/policy/coverage_matrix_self_application.md`](docs/governance/policy/coverage_matrix_self_application.md)
- ADR index: [`docs/governance/policy/adr_index.md`](docs/governance/policy/adr_index.md)
