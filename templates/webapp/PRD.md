# PRD — template-domain-webapp

## Overview
template-domain-webapp is a project scaffolding template for domain-driven web applications in the Phenotype ecosystem. It provides a production-ready starter with hexagonal architecture, a typed API layer, frontend/backend separation, authentication stubs, and CI configuration baked in.

## Epics

### E1 — Project Structure
**E1.1** Hexagonal architecture layout: `src/domain/`, `src/application/`, `src/adapters/`, `src/ports/`.
**E1.2** API layer with typed route definitions and request/response schemas.
**E1.3** Frontend scaffold: component library (Radix/shadcn), router, dark-mode-first design.
**E1.4** Configuration management: typed config via `config-ts` or equivalent.

### E2 — Auth Stub
**E2.1** Authentication port and stub adapter (session or JWT-based).
**E2.2** Route guards for protected pages/endpoints.
**E2.3** Placeholder for OAuth/OIDC integration.

### E3 — Developer Experience
**E3.1** One-command local start: `task dev` brings up API and frontend with hot reload.
**E3.2** Pre-configured linting, formatting, and type checking.
**E3.3** Test scaffold with example unit and integration tests.

### E4 — CI/CD
**E4.1** GitHub Actions workflow: lint, test, build on PR.
**E4.2** Docker Compose for local dependencies (DB, cache).
**E4.3** Environment config template (`.env.example`).

## Acceptance Criteria
- `task scaffold` runs in under 60 seconds and produces a working app skeleton.
- All placeholder files have clear `TODO` markers with the exact change required.
- Generated project passes lint and type check with zero errors before any user modification.
