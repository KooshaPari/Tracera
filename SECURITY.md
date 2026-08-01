# Security Policy

## Threat model (high level)

- [TRAC-API-001] API token forgery and replay: mitigate with JWT validation, claim checks, expiration checks, and signature/audience/issuer enforcement when env vars are configured.
- [TRAC-API-002] Unauthorized access and privilege escalation: enforce `ApiAuthzMiddleware` plus route scope requirements.
- [TRAC-API-003] Input abuse/malformed requests: reduce by strict request shape checks and typed request models.
- [TRAC-ENV-001] Secret leakage: prevent through environment-only secrets and policy for local defaults.

## Supported Versions

Tracera is in active development. Security fixes are applied to `main` first, and
then to active releases where applicable.

## Reporting a Vulnerability

Do not report suspected security vulnerabilities in public issue threads, discussion
posts, chat channels, or social media. Use private channels only.

### Private disclosure channels (in priority order)

1. GitHub Security Advisory (`Security` tab → `Report a vulnerability`).
2. Contact via repository security or owner contact (`CODEOWNERS` / repo metadata).
3. Direct private message to a maintainer.

### Required report contents

- Component, endpoint, workflow, or config path.
- Proof-of-concept steps.
- Expected/observed impact.
- Affected version/commit/environment.
- Impacted runtime context and mitigations, if known.

## Runtime controls

The Rust server defaults to loopback (`127.0.0.1:8080`). A non-loopback bind is
rejected unless `TRACERA_PUBLIC_BIND_MODE=authenticated-proxy` is explicitly
set. With that deployment mode, the service must be placed behind an
authenticated TLS reverse proxy before exposure; this proxy acknowledgement is
deployment policy, not Rust-layer authentication. The Rust HTTP layer also caps
request bodies at 8 MiB and adds `nosniff`, `DENY`, and `no-referrer` response
headers. The body cap bounds parser memory use without changing JSON contracts.

- All non-probe API requests go through `ApiAuthzMiddleware` in
  `src/tracertm/api/main.py`.
- Authentication and claim validation are centralized in `src/tracertm/api/deps.py`.
- Scope-aware authorization policy is defined in `src/tracertm/api/middleware/authz.py`.
- Route coverage, controls, and traceability evidence are documented under
  `docs/governance/policy/`.

## Input-validation policy

- JWT parsing (`Authorization` header) and bound checks are enforced in
  `src/tracertm/api/deps.py`.
- Route claim validation checks required claims (`sub`, `exp`) and optional
  `iss`/`aud` formatting.
- Request-shape validation is enforced in `ApiAuthzMiddleware`:
  - path length ceiling
  - query-length ceiling
  - control character filtering in request target
  - request payload hard size cap.
- Missing constraints in router models are tracked in
  `docs/governance/policy/coverage_matrix_self_application.md`.

## Secrets-via-environment policy

Secrets must be provided through environment variables and never checked into source:

- `TRACERA_JWT_SECRET`
- `TRACERA_JWT_PUBLIC_KEY`
- `TRACERA_JWT_AUDIENCE`
- `TRACERA_JWT_ISSUER`
- `TRACERA_DB_DSN` and any service credentials

Set `TRACERA_JWT_SECRET` and related verification knobs in production before
exposing authentication-bound endpoints.

## Rate-limiting plan

Current controls: middleware hard limits for request shape/size and header validation.

Planned phased rollout:

1. Per-route request limit counters and burst caps (in-memory start, then shared store).
2. Emit `Retry-After`, `X-RateLimit-Limit`, and `X-RateLimit-Remaining` headers.
3. Add CI contract tests for 429 behavior and abuse-scenario coverage.
4. Integrate service-level abuse dashboards for incident response.

## Coordinated disclosure timeline

- Acknowledgement within 5 business days.
- Initial severity/scope update by day 10.
- Fix or accepted-risk decision by day 90.
- Public advisory timing coordinated with reporter.
- If delayed, provide explicit revised timeline and rationale.
